#!/usr/bin/env python3
"""Measure the non-PubMed layers of the review search (Sections 4.4-4.5).

PubMed is counted by ``scripts/validate_search.py``. This script sizes the
preprint and conference layers, which live in OpenAlex and are therefore subject
to its free-tier budget (~1,000 credits/day, a search costing 10, reset at
midnight UTC). If the budget is spent the script says so and writes nothing,
rather than recording a zero that would look like an empty layer.

Usage:
    python scripts/measure_search_layers.py
"""
from __future__ import annotations

import argparse
import json

from pedrad_ai import config, openalex


def safe_count(label: str, query: str, start: int, end: int, types: str) -> int | None:
    try:
        n = openalex.count(query, start, end, types=types)
        print(f"  {label:<34} {n:>7}")
        return n
    except Exception as exc:  # noqa: BLE001 - any failure is "unmeasured", not zero
        print(f"  {label:<34} unmeasured ({exc})")
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", type=int, default=config.REVIEW_START_YEAR)
    ap.add_argument("--end", type=int, default=config.END_YEAR)
    args = ap.parse_args()

    translated = openalex.translate_pubmed_query(config.REVIEW_QUERY)
    print(f"Review search, non-PubMed layers, {args.start}-{args.end}\n")
    print("OpenAlex translation of REVIEW_QUERY:")
    print(f"  {translated[:300]}{'...' if len(translated) > 300 else ''}\n")

    out: dict = {
        "start": args.start,
        "end": args.end,
        "openalex_query": translated,
        "layers": {},
    }
    for label, types in [
        ("preprints", "preprint"),
        ("conference papers", "conference-paper"),
        ("journal articles", "article"),
    ]:
        out["layers"][label] = safe_count(label, translated, args.start, args.end, types)

    # The prespecified conference venues are searched by venue, not by keyword
    # sweep; this only reports the LNCS series, which is where MICCAI, IPMI and
    # the MICCAI workshops live. The rest are hand-searched via DBLP and PMLR.
    try:
        lncs = openalex.count(
            translated, args.start, args.end, types="article|book-chapter|conference-paper"
        )
        print(f"\n  {'LNCS-eligible (all types)':<34} {lncs:>7}")
        out["layers"]["lncs_eligible_all_types"] = lncs
    except Exception as exc:  # noqa: BLE001
        print(f"\n  {'LNCS-eligible (all types)':<34} unmeasured ({exc})")
        out["layers"]["lncs_eligible_all_types"] = None

    if all(v is None for v in out["layers"].values()):
        print("\nEvery layer is unmeasured — the OpenAlex budget is spent. "
              "Re-run after the midnight-UTC reset. Nothing written.")
        return

    path = config.PROCESSED_DIR / "search_layers.json"
    path.write_text(json.dumps(out, indent=2))
    print(f"\nwrote {path}")
    print("Note: these are pre-deduplication counts. Preprints are removed once "
          "their journal version appears; see paper_db.collect_candidates.")


if __name__ == "__main__":
    main()
