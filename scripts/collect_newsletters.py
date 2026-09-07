#!/usr/bin/env python3
"""Scan newsletter / trade-press archives for pediatric radiology AI news.

Usage:
    python scripts/collect_newsletters.py                 # every source
    python scripts/collect_newsletters.py --source "RSNA News" --source "The Imaging Wire"

Outputs:
    data/processed/newsletter_items.json      one row per pediatric-radiology-AI story
    data/processed/newsletter_items.csv       same, flat
    data/processed/newsletter_summary.json    per-source / per-year denominators + topics

Sources and vocabularies live in ``pedrad_ai/config.py`` (NEWSLETTER_SOURCES,
NEWS_*_PATTERNS). Archives are cached under data/raw/cache/, so a re-run only
fetches issues that did not exist last time.
"""

from __future__ import annotations

import argparse

from pedrad_ai import config, newsletters, utils


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", action="append", help="restrict to named source(s)")
    args = ap.parse_args()

    sources = config.NEWSLETTER_SOURCES
    if args.source:
        missing = [s for s in args.source if s not in sources]
        if missing:
            ap.error(f"unknown source(s): {missing}; known: {list(sources)}")
        sources = {k: v for k, v in sources.items() if k in args.source}

    print("Scanning newsletter archives...")
    items, summary = newsletters.collect(sources)

    utils.save_json(items, config.PROCESSED_DIR / "newsletter_items.json")
    utils.save_csv(
        [
            {**r, "topics": "; ".join(r["topics"]), "pediatric_terms": "; ".join(r["pediatric_terms"]),
             "ai_terms": "; ".join(r["ai_terms"]), "radiology_terms": "; ".join(r["radiology_terms"])}
            for r in items
        ],
        config.PROCESSED_DIR / "newsletter_items.csv",
        columns=["date", "source", "story", "issue_title", "url", "topics", "snippet",
                 "pediatric_terms", "ai_terms", "radiology_terms"],
    )
    utils.save_json(summary, config.PROCESSED_DIR / "newsletter_summary.json")

    print("\nPediatric radiology-AI stories by source:")
    for name, s in summary["sources"].items():
        print(
            f"  {name:20s} {s['pediatric_radiology_ai_stories']:4d} of {s['radiology_ai_stories']:5d} "
            f"radiology-AI stories  ({s['archive_from']} .. {s['archive_to']})"
        )
    print(f"  total: {summary['total_pediatric_radiology_ai_stories']}")


if __name__ == "__main__":
    main()
