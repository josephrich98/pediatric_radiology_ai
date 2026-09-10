#!/usr/bin/env python3
"""Validate the systematic-review search strategy.

Three checks, all reported into ``data/processed/search_validation.json``:

1. **Recall** — what fraction of ``config.REVIEW_GOLD_PAPERS`` the search
   retrieves. This is the number that matters for a review: a record the search
   never returns cannot be recovered at screening.
2. **Yield** — records identified per year, so the screening burden is known
   before the screen is run.
3. **Comparison** — the same recall and yield for the retired reading-list query
   (``config.PAPER_DB_QUERY``), so the change is auditable.

Usage:
    python scripts/validate_search.py
    python scripts/validate_search.py --start 2005 --end 2026
"""
from __future__ import annotations

import argparse
import json

from pedrad_ai import config, pubmed


def recall(query: str, gold: list[tuple[str, str]]) -> dict:
    """Fraction of ``gold`` DOIs the query retrieves from PubMed."""
    hits, misses, unindexed = [], [], []
    for doi, label in gold:
        pmid = pubmed.pmid_for_doi(doi)
        if not pmid:
            unindexed.append({"doi": doi, "label": label})
            continue
        found = pubmed.count_for_query(f"({query}) AND {pmid}[uid]") > 0
        (hits if found else misses).append({"doi": doi, "pmid": pmid, "label": label})
    n = len(hits) + len(misses)
    return {
        "n_testable": n,
        "n_retrieved": len(hits),
        "recall": round(len(hits) / n, 4) if n else None,
        "missed": misses,
        "not_pubmed_indexed": unindexed,
    }


def yearly(query: str, start: int, end: int) -> dict:
    """Records per year, plus the deduplicated range total.

    The per-year sum exceeds the range total: a record carrying an electronic
    and a print date in different years is counted once in each. The range
    figure is the one to quote.
    """
    per_year = {y: pubmed.count_for_query(f"({query}) AND {y}[pdat]") for y in range(start, end + 1)}
    return {
        "per_year": per_year,
        "sum_of_years": sum(per_year.values()),
        "range_total": pubmed.count_for_query(f"({query}) AND {start}:{end}[pdat]"),
        "with_abstract": pubmed.count_for_query(f"({query}) AND hasabstract AND {start}:{end}[pdat]"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", type=int, default=config.REVIEW_START_YEAR)
    ap.add_argument("--end", type=int, default=config.END_YEAR)
    ap.add_argument("--skip-comparison", action="store_true",
                    help="skip the retired reading-list query (halves the PubMed calls)")
    args = ap.parse_args()

    out: dict = {"start": args.start, "end": args.end, "queries": {}}

    print(f"Search validation, {args.start}-{args.end}\n")
    for name, query in [("review", config.REVIEW_QUERY),
                        ("paper_db_v0", config.PAPER_DB_QUERY)]:
        if name == "paper_db_v0" and args.skip_comparison:
            continue
        print(f"  {name}: counting ...", flush=True)
        y = yearly(query, args.start, args.end)
        print(f"  {name}: recall ...", flush=True)
        r = recall(query, config.REVIEW_GOLD_PAPERS)
        out["queries"][name] = {"query": query, "yield": y, "recall": r}
        print(f"    identified  {y['range_total']:>6}  "
              f"({y['with_abstract']} with abstract, "
              f"{100 * y['with_abstract'] / max(1, y['range_total']):.1f}%)")
        print(f"    recall      {r['n_retrieved']}/{r['n_testable']} "
              f"= {100 * (r['recall'] or 0):.1f}%")
        for m in r["missed"]:
            print(f"      MISSED: {m['label']}")
        print()

    path = config.PROCESSED_DIR / "search_validation.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
