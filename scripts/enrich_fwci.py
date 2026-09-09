#!/usr/bin/env python3
"""Fill in the field-weighted citation impact (FWCI) from OpenAlex, by DOI.

The most-cited tables (``top_papers_*.json``) and the venue tables
(``conference_works.json``) come from Semantic Scholar, which has citation
counts but no year-normalized impact. OpenAlex computes an FWCI per work
(citations relative to the world average for the same field and year, 1 =
average), which is what lets a 2025 paper be read next to a 2023 one.

OpenAlex's free tier is a small daily budget (about 1,000 credits, reset at
midnight UTC); a search costs 10 credits but a ``filter=doi:a|b|...`` lookup
of up to 50 DOIs costs 1, so this script batches every DOI it needs into a
handful of requests. If the budget is exhausted it says when it resets and
exits non-zero without touching the files.

Usage:
    python scripts/enrich_fwci.py            # top 15 rows of every table
    python scripts/enrich_fwci.py --rows 25
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error

from pedrad_ai import config, openalex, utils

BATCH = 50


def _doi_key(d: str | None) -> str | None:
    d = (d or "").strip().lower().replace("https://doi.org/", "")
    return d or None


def collect_dois(rows: int) -> tuple[set[str], list[tuple[str, list[dict]]]]:
    targets: list[tuple[str, list[dict]]] = []
    dois: set[str] = set()
    for p in sorted(config.PROCESSED_DIR.glob("top_papers_*.json")):
        papers = utils.load_json(p)
        if isinstance(papers, list):
            targets.append((str(p), papers[:rows]))
            dois.update(k for k in (_doi_key(x.get("doi")) for x in papers[:rows]) if k)
    cw = config.PROCESSED_DIR / "conference_works.json"
    if cw.exists():
        works = utils.load_json(cw)
        for name, v in works.items():
            targets.append((f"{cw}::{name}", v.get("works", [])[:rows]))
            dois.update(k for k in (_doi_key(x.get("doi")) for x in v.get("works", [])[:rows]) if k)
    return dois, targets


def lookup(dois: list[str]) -> dict[str, dict]:
    """DOI -> {fwci, citation_count, citation_percentile} for up to 50 DOIs (1 credit)."""
    params = {
        "filter": "doi:" + "|".join(dois),
        "per_page": BATCH,
        "select": "id,doi,cited_by_count,fwci,citation_normalized_percentile",
        "mailto": config.CONTACT_EMAIL,
    }
    data = openalex._get(openalex.WORKS, params)
    out: dict[str, dict] = {}
    for w in data.get("results", []):
        k = _doi_key(w.get("doi"))
        if k:
            pct = (w.get("citation_normalized_percentile") or {}).get("value")
            out[k] = {
                "fwci": round(w["fwci"], 2) if isinstance(w.get("fwci"), (int, float)) else None,
                "citation_count_openalex": w.get("cited_by_count"),
                "citation_percentile": round(pct * 100, 1) if isinstance(pct, (int, float)) else None,
            }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rows", type=int, default=15, help="rows per table to enrich")
    args = ap.parse_args()

    dois, targets = collect_dois(args.rows)
    todo = sorted(dois)
    print(f"{len(todo)} DOIs across {len(targets)} tables -> {(len(todo) + BATCH - 1) // BATCH} OpenAlex requests")
    found: dict[str, dict] = {}
    for i in range(0, len(todo), BATCH):
        try:
            found.update(lookup(todo[i:i + BATCH]))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:300] if hasattr(exc, "read") else ""
            print(f"OpenAlex refused ({exc.code}): {body}")
            if exc.code == 429:
                try:
                    reset = json.loads(body).get("retryAfter")
                    print(f"Budget exhausted; resets in {reset} s (midnight UTC). Files left unchanged.")
                except Exception:
                    pass
            return 1
    print(f"  {len(found)} of {len(todo)} DOIs found in OpenAlex")

    for path, rows in targets:
        n = 0
        for r in rows:
            k = _doi_key(r.get("doi"))
            if k and k in found:
                r.update(found[k])
                n += 1
        if "::" in path:
            file, name = path.split("::", 1)
            works = utils.load_json(file)
            works[name]["works"][:len(rows)] = rows
            utils.save_json(works, file)
        else:
            papers = utils.load_json(path)
            papers[:len(rows)] = rows
            utils.save_json(papers, path)
        print(f"  {path.split('/')[-1]}: {n}/{len(rows)} rows enriched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
