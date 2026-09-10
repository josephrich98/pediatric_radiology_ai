#!/usr/bin/env python3
"""Journal-level view of the pediatric radiology-AI corpus.

Counts papers per journal per year (PubMed, strict pediatric query) and joins
each journal to an impact number (OpenAlex 2-year mean citedness, or a real JIF
from ``data/journal_impact_overrides.json``). Feeds the impact scatter figures.

    python scripts/collect_journals.py
"""

from __future__ import annotations

import argparse

from pedrad_ai import config, journals, utils


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", type=int, default=config.JOURNAL_START_YEAR)
    ap.add_argument("--end", type=int, default=config.JOURNAL_END_YEAR)
    ap.add_argument(
        "--impact-only",
        action="store_true",
        help="re-run only the impact lookup over the stored counts (no PubMed calls). "
        "Use it after the OpenAlex daily budget resets, or after editing "
        "data/journal_impact_overrides.json.",
    )
    args = ap.parse_args()

    if args.impact_only:
        print("Impact lookup only (stored counts) ...")
        data = journals.attach_impact(utils.load_json(config.JOURNAL_IMPACT_JSON))
    else:
        print(f"Journal counts {args.start}-{args.end} ...")
        data = journals.collect(start=args.start, end=args.end)
    utils.save_json(data, config.JOURNAL_IMPACT_JSON)
    print(f"  wrote {config.JOURNAL_IMPACT_JSON}")
    print(f"  {data['n_papers']} papers across {data['n_journals']} journals "
          f"({data.get('n_with_impact', 0)} with an impact number)")
    top = [j for j in data["journals"] if j["impact_factor"] is not None][:10]
    for j in top:
        print(f"    {j['total']:4d}  IF {j['impact_factor']:6.2f}  {j['journal']}")


if __name__ == "__main__":
    main()
