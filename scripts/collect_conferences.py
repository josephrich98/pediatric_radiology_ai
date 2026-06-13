#!/usr/bin/env python3
"""Collect conference topic fractions (NeurIPS, MICCAI, CVPR, ISBI, ...).

Outputs:
    data/processed/conference_fractions.csv
    data/processed/conference_fractions.json
"""

from __future__ import annotations

import argparse

from pedrad_ai import conferences, config, utils


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", type=int, default=config.START_YEAR)
    ap.add_argument("--end", type=int, default=config.END_YEAR)
    args = ap.parse_args()

    print(f"Pulling DBLP venue titles {args.start}-{args.end} for {list(config.DBLP_VENUES)}...")
    rows = conferences.collect_all(args.start, args.end)
    utils.save_json(rows, config.PROCESSED_DIR / "conference_fractions.json")
    utils.save_csv(rows, config.PROCESSED_DIR / "conference_fractions.csv")

    # Quick console summary: latest-year radiology fraction at NeurIPS, AI
    # fraction at MICCAI.
    for venue in ("NeurIPS", "MICCAI"):
        venue_rows = [r for r in rows if r["venue"] == venue]
        if venue_rows:
            latest = max(venue_rows, key=lambda r: r["year"])
            print(
                f"  {venue} {latest['year']}: {latest['total_papers']} papers, "
                f"radiology≈{latest['radiology_fraction']:.1%}, AI≈{latest['ai_fraction']:.1%}"
            )


if __name__ == "__main__":
    main()
