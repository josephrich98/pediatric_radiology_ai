#!/usr/bin/env python3
"""Fold every paper record file in data/processed into one table.

Merges the screening store (``pedrad_paper_db.json``), the Embase export
(``embase_unique_rows.json``), the per-venue tables (``conference_works.json``)
and the most-cited leaderboards (``top_papers_*.json``) into
``data/processed/pediatric_radiology_ai.csv``: one row per paper, deduplicated on
PMID then DOI then title, with a ``record_type`` column saying what the paper is
to this project and a ``source_files`` column naming the files it came from.

Scope is papers - journal articles, conference papers and preprints. Repositories,
FDA devices, newsletter stories and journal impact are different entities and
keep their own files.

Reads only; it makes no network calls and writes nothing the other scripts read,
so it is safe to run at any point after the collectors.

    python scripts/export_unified_db.py
    python scripts/export_unified_db.py --out /tmp/papers.csv
"""

from __future__ import annotations

import argparse

from pedrad_ai import config, unified_db, utils


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None, help="write the CSV here instead")
    ap.add_argument("--no-summary", action="store_true",
                    help="skip the companion counts JSON")
    args = ap.parse_args()

    rows = unified_db.build()
    path = unified_db.write_csv(rows, args.out)
    summary = unified_db.summarize(rows)
    print(f"wrote {path}  ({summary['n_rows']} papers, {len(unified_db.COLUMNS)} columns)")

    if not args.no_summary and args.out is None:
        utils.save_json(summary, config.UNIFIED_DB_SUMMARY)
        print(f"  wrote {config.UNIFIED_DB_SUMMARY}")

    for title, key in (("record type", "by_record_type"),
                       ("publication form", "by_publication_form"),
                       ("source file", "by_source_file")):
        print(f"  by {title}:")
        for name, n in summary[key].items():
            print(f"    {n:6d}  {name}")


if __name__ == "__main__":
    main()
