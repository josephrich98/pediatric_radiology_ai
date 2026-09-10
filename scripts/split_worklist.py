#!/usr/bin/env python3
"""Split a paper-database worklist into batches for parallel reading.

``build_paper_db.py --worklist`` writes one large JSON carrying the prompt, the
schema and every outstanding paper. Reading several thousand abstracts in one
pass is impractical, so this splits the ``papers`` list into fixed-size batches,
each a standalone worklist with the same instructions and schema, so a batch is
readable on its own and rows written from any batch are directly comparable.

Rows come back as ``{"<pmid>": {…schema fields…}, …}``; merge them with
``--merge`` and feed the result to ``build_paper_db.py --ingest``.

Usage:
    python scripts/split_worklist.py data/processed/review_worklist.json --size 120
    python scripts/split_worklist.py --merge data/processed/review_rows
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def split(path: Path, size: int, out_dir: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    papers = data["papers"]
    out_dir.mkdir(parents=True, exist_ok=True)
    header = {k: v for k, v in data.items() if k != "papers"}
    n = 0
    for i in range(0, len(papers), size):
        batch = papers[i : i + size]
        n += 1
        payload = {**header, "batch": n, "n_papers": len(batch), "papers": batch}
        (out_dir / f"batch_{n:03d}.json").write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"{len(papers)} papers -> {n} batches of <= {size} in {out_dir}")
    # The schema and prompt are identical in every batch; write them once more
    # on their own so a reader can consult them without opening a batch.
    (out_dir / "_schema.json").write_text(
        json.dumps({"instructions": header.get("instructions"),
                    "schema": header.get("schema")}, indent=1), encoding="utf-8")
    print(f"wrote {out_dir / '_schema.json'}")


def merge(rows_dir: Path, out: Path) -> None:
    merged: dict[str, dict] = {}
    files = sorted(rows_dir.glob("rows_*.json"))
    collisions = 0
    for f in files:
        try:
            rows = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  [skip] {f.name}: invalid JSON ({exc})")
            continue
        if not isinstance(rows, dict):
            print(f"  [skip] {f.name}: expected an object keyed by PMID")
            continue
        for k, v in rows.items():
            if k in merged:
                collisions += 1
            merged[k] = v
        print(f"  {f.name}: {len(rows)} rows")
    out.write_text(json.dumps(merged, indent=1), encoding="utf-8")
    print(f"\n{len(merged)} unique rows from {len(files)} files"
          + (f" ({collisions} duplicate keys, last wins)" if collisions else ""))
    print(f"wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("worklist", nargs="?", help="worklist JSON to split")
    ap.add_argument("--size", type=int, default=120, help="papers per batch")
    ap.add_argument("--out-dir", default="data/processed/review_batches")
    ap.add_argument("--merge", metavar="ROWS_DIR",
                    help="merge rows_*.json in this directory instead of splitting")
    ap.add_argument("--merged-out", default="data/processed/review_rows_merged.json")
    args = ap.parse_args()

    if args.merge:
        merge(Path(args.merge), Path(args.merged_out))
        return
    if not args.worklist:
        ap.error("give a worklist to split, or --merge a rows directory")
    split(Path(args.worklist), args.size, Path(args.out_dir))


if __name__ == "__main__":
    main()
