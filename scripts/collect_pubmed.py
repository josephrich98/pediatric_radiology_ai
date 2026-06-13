#!/usr/bin/env python3
"""Collect PubMed yearly counts and top articles, write to data/.

Usage:
    python scripts/collect_pubmed.py            # full pull (slow, ~hundreds of queries)
    python scripts/collect_pubmed.py --quick    # only the headline queries

Outputs:
    data/processed/pubmed_yearly_counts.json
    data/processed/pubmed_trends.csv
    data/processed/pubmed_summary.json
    data/raw/top_articles_<query>.json
"""

from __future__ import annotations

import argparse

from pedrad_ai import analysis, config, pubmed, utils


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true", help="headline queries only")
    ap.add_argument("--top", type=int, default=150, help="top articles per query")
    args = ap.parse_args()

    if args.quick:
        counts = {name: pubmed.yearly_counts(q) for name, q in config.QUERIES.items()}
    else:
        print("Pulling full yearly counts (queries x years)...")
        counts = pubmed.collect_all_yearly()

    utils.save_json(counts, config.PROCESSED_DIR / "pubmed_yearly_counts.json")
    analysis.write_trend_csv(counts, str(config.PROCESSED_DIR / "pubmed_trends.csv"))
    utils.save_json(analysis.summarize(counts), config.PROCESSED_DIR / "pubmed_summary.json")

    print("Computing RSNA-journal AI fraction...")
    rsna = pubmed.rsna_ai_fraction()
    utils.save_json(rsna, config.PROCESSED_DIR / "rsna_ai_fraction.json")

    for name in ("radiology_ai", "pediatric_radiology_ai"):
        print(f"Fetching top articles for {name}...")
        arts = pubmed.top_articles(config.QUERIES[name], retmax=args.top)
        utils.save_json(arts, config.RAW_DIR / f"top_articles_{name}.json")

    summary = analysis.summarize(counts)
    print("\nHeadline summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
