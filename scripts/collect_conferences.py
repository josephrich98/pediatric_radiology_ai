#!/usr/bin/env python3
"""Collect conference / society engagement with the domain (2016-2026).

Two venue families:
  * ML / CV venues (CVPR, ICCV, NeurIPS, ICML, ICLR) via DBLP title sampling —
    reported as the *radiology / medical-imaging fraction* of each venue.
  * Radiology societies (RSNA, ACR, ECR, SPR) via the AI fraction of their
    flagship journals in PubMed — reported as the *AI fraction* of each society.

Outputs:
    data/processed/conference_ml_venues.csv / .json
    data/processed/conference_society_venues.csv / .json
"""

from __future__ import annotations

import argparse

from pedrad_ai import conferences, config, utils


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", type=int, default=config.CONF_START_YEAR)
    ap.add_argument("--end", type=int, default=config.CONF_END_YEAR)
    args = ap.parse_args()

    print(f"DBLP ML venues {args.start}-{args.end}: {list(config.DBLP_VENUES)}")
    ml_rows = conferences.collect_all(args.start, args.end)
    utils.save_json(ml_rows, config.PROCESSED_DIR / "conference_ml_venues.json")
    utils.save_csv(ml_rows, config.PROCESSED_DIR / "conference_ml_venues.csv")
    for venue in config.DBLP_VENUES:
        vr = [r for r in ml_rows if r["venue"] == venue]
        if vr:
            latest = max(vr, key=lambda r: r["year"])
            print(
                f"  {venue}: {len(vr)} yrs; {latest['year']} "
                f"radiology≈{latest['radiology_fraction']:.1%}"
            )

    print(f"\nRadiology societies {args.start}-{args.end}: {list(config.SOCIETY_JOURNALS)}")
    soc_rows = conferences.collect_societies(args.start, args.end)
    utils.save_json(soc_rows, config.PROCESSED_DIR / "conference_society_venues.json")
    utils.save_csv(soc_rows, config.PROCESSED_DIR / "conference_society_venues.csv")
    for society in config.SOCIETY_JOURNALS:
        sr = [r for r in soc_rows if r["society"] == society]
        if sr:
            latest = max(sr, key=lambda r: r["year"])
            print(
                f"  {society}: {latest['year']} AI≈{latest['ai_fraction']:.1%} "
                f"({latest['ai_articles']}/{latest['total_articles']})"
            )


if __name__ == "__main__":
    main()
