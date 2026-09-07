#!/usr/bin/env python3
"""Check the PubMed queries: recall on gold papers, strict-vs-broad, term audit.

Writes data/processed/query_validation.json, consumed by the methods slide.
"""

from __future__ import annotations

from pedrad_ai import config, utils, validation


def main() -> None:
    print("Validating PubMed queries...")
    out = validation.run()
    utils.save_json(out, config.PROCESSED_DIR / "query_validation.json")
    r = out["recall"]
    print(f"  recall {r['recall']} ({r['n_retrieved']}/{r['n_indexed']}); missed: {r['missed']}")
    print(f"  pediatric recall {r['pediatric_recall']}; missed: {r['pediatric_missed']}")
    for k, v in out["precision"]["series"].items():
        print(f"  {k}: broad {v['broad']}, strict {v['strict']}, strict share {v['strict_share_of_broad']}")


if __name__ == "__main__":
    main()
