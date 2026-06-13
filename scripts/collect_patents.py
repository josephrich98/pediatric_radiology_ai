#!/usr/bin/env python3
"""Collect granted-patent counts for radiology AI (overall and pediatric).

Outputs:
    data/processed/patent_yearly_counts.json
"""

from __future__ import annotations

from pedrad_ai import config, patents, utils


def main() -> None:
    print("PatentsView: radiology-AI granted patents per year...")
    overall = patents.collect_yearly(pediatric=False)
    pediatric = patents.collect_yearly(pediatric=True)
    out = {"radiology_ai": overall, "pediatric_radiology_ai": pediatric}
    utils.save_json(out, config.PROCESSED_DIR / "patent_yearly_counts.json")
    total = sum(overall.values())
    if total == 0:
        print("  (no patents returned — PatentsView may be unreachable in this environment)")
    else:
        for yr in sorted(overall):
            print(f"  {yr}: {overall[yr]:>5} radiology-AI  /  {pediatric.get(yr,0):>3} pediatric")


if __name__ == "__main__":
    main()
