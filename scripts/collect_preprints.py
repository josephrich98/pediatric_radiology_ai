#!/usr/bin/env python3
"""Count arXiv preprints for the count-based views.

PubMed indexes journals, not arXiv, so the growth curve, the modality x task
tables and the clinical-problem breakdown would miss the preprint-first part
of the field (foundation models, vision-language models, most of the ML-venue
work). This script runs the same PubMed queries against the arXiv API
(translated by ``arxiv.to_arxiv_query``) and stores the counts in the same
shapes as the PubMed files, so figures, slides and reports add the two layers.

Outputs:
    data/processed/preprint_counts.json
        {"source": "arXiv", "yearly": {query: {year: n}},
         "crosstab": {query: <pubmed.crosstab shape>},
         "problems": <pubmed.problem_counts shape>}

About 400 requests at 1.5 s each on a cold cache (~10 minutes).
"""

from __future__ import annotations

import argparse
import datetime as dt

from pedrad_ai import arxiv, config, utils


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true", help="yearly counts only (no crosstab / problems)")
    args = ap.parse_args()

    out: dict = {"collected_on": dt.date.today().isoformat(), "source": "arXiv API (submittedDate by year)",
                 "yearly": {}, "crosstab": {}, "problems": {}}
    print("arXiv preprints: yearly counts per query...")
    for name, q in config.QUERIES.items():
        series = arxiv.yearly_counts(arxiv.to_arxiv_query(q))
        out["yearly"][name] = {str(y): n for y, n in series.items()}
        print(f"  {name}: {series.get(config.END_YEAR - 1, 0):,} preprints in {config.END_YEAR - 1}")

    if not args.quick:
        print("arXiv preprints: modality x task cross-tabulations...")
        for name in ("radiology_ai", "pediatric_radiology_ai"):
            out["crosstab"][name] = arxiv.crosstab(config.QUERIES[name], config.MODALITY_TERMS, config.TASK_TERMS)
            print(f"  {name}: {out['crosstab'][name]['total']:,} preprints total")
        print("arXiv preprints: pediatric clinical problems per era...")
        out["problems"] = arxiv.problem_counts(config.QUERIES["pediatric_radiology_ai"], config.PEDIATRIC_PROBLEM_TERMS)
        print(f"  totals: {out['problems']['totals']}")

    utils.save_json(out, config.PROCESSED_DIR / "preprint_counts.json")
    print("Wrote data/processed/preprint_counts.json")


if __name__ == "__main__":
    main()
