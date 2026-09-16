#!/usr/bin/env python3
"""Count arXiv + medRxiv preprints for the count-based views.

PubMed indexes journals, not arXiv, and covers medRxiv only through the NIH
preprint pilot, so the growth curve, the modality x task tables and the
clinical-problem breakdown would miss much of the preprint-first part of the
field (foundation models, vision-language models, most of the ML-venue work
on arXiv; clinical validation studies posted to medRxiv ahead of peer review).
This script runs the same PubMed queries against the arXiv API (translated by
``arxiv.to_arxiv_query``) and against Europe PMC restricted to medRxiv
(translated by ``medrxiv.to_europepmc_query``), and stores the combined counts
in the same shapes as the PubMed files, so figures, slides and reports add the
two layers together. bioRxiv is not searched or counted: this preprint layer
is arXiv + medRxiv only.

Outputs:
    data/processed/preprint_counts.json
        {"source": "arXiv + medRxiv", "yearly": {query: {year: n}},
         "crosstab": {query: <pubmed.crosstab shape>},
         "problems": <pubmed.problem_counts shape>,
         "by_source": {"arXiv": {...same three keys...}, "medRxiv": {...}}}
        The top-level "yearly"/"crosstab"/"problems" are the arXiv+medRxiv sum
        (what ``analysis.add_preprints`` / ``merge_crosstab`` / ``merge_problems``
        consume); "by_source" keeps each source's own counts for reference.
        Double counting between the two servers is not a real concern: a
        preprint is posted to one server, not both.

About 400 requests to arXiv at 1.5 s each and a similar number to Europe PMC
at 1 s each on a cold cache (~15 minutes combined). arXiv responses are cached
under data/raw/cache/, so a re-run after a medRxiv-only change is fast.
"""

from __future__ import annotations

import argparse
import datetime as dt
from typing import Any

from pedrad_ai import arxiv, config, medrxiv, utils

SOURCES = {
    "arXiv": (arxiv, arxiv.to_arxiv_query),
    "medRxiv": (medrxiv, medrxiv.to_europepmc_query),
}


def _sum_yearly(a: dict[str, dict[str, int]], b: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for name in set(a) | set(b):
        ya, yb = a.get(name, {}), b.get(name, {})
        for yr in set(ya) | set(yb):
            out.setdefault(name, {})[yr] = int(ya.get(yr, 0)) + int(yb.get(yr, 0))
    return out


def _sum_crosstab(a: dict[str, Any] | None, b: dict[str, Any] | None) -> dict[str, Any] | None:
    if not a:
        return b
    if not b:
        return a
    return {
        "years": a["years"],
        "total": a["total"] + b.get("total", 0),
        "row_totals": {r: v + b.get("row_totals", {}).get(r, 0) for r, v in a["row_totals"].items()},
        "col_totals": {c: v + b.get("col_totals", {}).get(c, 0) for c, v in a["col_totals"].items()},
        "cells": {
            r: {c: v + b.get("cells", {}).get(r, {}).get(c, 0) for c, v in row.items()}
            for r, row in a["cells"].items()
        },
    }


def _sum_problems(a: dict[str, Any] | None, b: dict[str, Any] | None) -> dict[str, Any] | None:
    if not a or not a.get("counts"):
        return b
    if not b or not b.get("counts"):
        return a
    return {
        "eras": a["eras"],
        "totals": {e: v + b.get("totals", {}).get(e, 0) for e, v in a["totals"].items()},
        "counts": {
            p: {e: v + b["counts"].get(p, {}).get(e, 0) for e, v in eras.items()}
            for p, eras in a["counts"].items()
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true", help="yearly counts only (no crosstab / problems)")
    ap.add_argument("--source", choices=["arXiv", "medRxiv"], help="run only one source (for a fast top-up of the other)")
    args = ap.parse_args()

    sources = {args.source: SOURCES[args.source]} if args.source else SOURCES

    by_source: dict[str, dict[str, Any]] = {}
    for label, (mod, translate) in sources.items():
        print(f"{label} preprints: yearly counts per query...")
        src_out: dict[str, Any] = {"yearly": {}, "crosstab": {}, "problems": {}}
        for name, q in config.QUERIES.items():
            series = mod.yearly_counts(translate(q))
            src_out["yearly"][name] = {str(y): n for y, n in series.items()}
            print(f"  {name}: {series.get(config.END_YEAR - 1, 0):,} preprints in {config.END_YEAR - 1}")

        if not args.quick:
            print(f"{label} preprints: modality x task cross-tabulations...")
            for name in ("radiology_ai", "pediatric_radiology_ai"):
                src_out["crosstab"][name] = mod.crosstab(config.QUERIES[name], config.MODALITY_TERMS, config.TASK_TERMS)
                print(f"  {name}: {src_out['crosstab'][name]['total']:,} preprints total")
            print(f"{label} preprints: pediatric clinical problems per era...")
            src_out["problems"] = mod.problem_counts(config.QUERIES["pediatric_radiology_ai"], config.PEDIATRIC_PROBLEM_TERMS)
            print(f"  totals: {src_out['problems']['totals']}")

        by_source[label] = src_out

    # Load the previous file so a single-source rerun (--source) keeps the
    # other source's counts rather than dropping them.
    existing_by_source: dict[str, Any] = {}
    existing_path = config.PROCESSED_DIR / "preprint_counts.json"
    if args.source and existing_path.exists():
        try:
            existing_by_source = utils.load_json(existing_path).get("by_source", {})
        except Exception:
            existing_by_source = {}
    merged_by_source = {**existing_by_source, **by_source}

    combined_yearly: dict[str, dict[str, int]] = {}
    combined_crosstab: dict[str, Any] = {}
    combined_problems: dict[str, Any] | None = None
    labels = [lab for lab in ("arXiv", "medRxiv") if lab in merged_by_source]
    for label in labels:
        src = merged_by_source[label]
        combined_yearly = _sum_yearly(combined_yearly, src.get("yearly", {}))
        for name, ct in (src.get("crosstab") or {}).items():
            combined_crosstab[name] = _sum_crosstab(combined_crosstab.get(name), ct)
        combined_problems = _sum_problems(combined_problems, src.get("problems"))

    out = {
        "collected_on": dt.date.today().isoformat(),
        "source": "arXiv API (submittedDate by year) + Europe PMC (medRxiv, PUB_YEAR by year); bioRxiv not searched",
        "yearly": combined_yearly,
        "crosstab": combined_crosstab,
        "problems": combined_problems or {},
        "by_source": merged_by_source,
    }

    utils.save_json(out, config.PROCESSED_DIR / "preprint_counts.json")
    print("Wrote data/processed/preprint_counts.json")


if __name__ == "__main__":
    main()
