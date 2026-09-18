#!/usr/bin/env python3
"""Collect the FDA AI-enabled device list (Radiology panel) -> data/processed/fda_ai_devices.json."""

from __future__ import annotations

from pedrad_ai import config, fda_devices, utils


def main() -> None:
    import argparse

    # The spreadsheet is fetched with urllib directly, outside the HTTP cache, so
    # this script is already a refresh every time it runs and takes no --refresh
    # flag. The parser is here so `--help` prints help instead of re-downloading.
    argparse.ArgumentParser(
        description="Collect the FDA AI-enabled device list (Radiology panel). "
                    "Always downloads the current list; nothing is cached.",
    ).parse_args()
    print("FDA AI-enabled device list...")
    fda = fda_devices.collect()
    if not fda:
        print("  nothing collected (download failed); writing empty file")
    utils.save_json(fda, config.PROCESSED_DIR / "fda_ai_devices.json")
    if fda:
        print(f"  {fda['radiology_devices']} radiology devices of {fda['total_devices_all_panels']} total")
        for c in fda["top_companies"][:10]:
            print(f"  {c['devices']:>4}  {c['company']}")
        print(f"  pediatric-named devices: {len(fda['pediatric_name_hits'])}")


if __name__ == "__main__":
    main()
