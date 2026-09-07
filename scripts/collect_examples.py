#!/usr/bin/env python3
"""Fetch representative images of popular tools, papers and products -> figures/examples/."""

from __future__ import annotations

from pedrad_ai import examples


def main() -> None:
    print("Fetching example images...")
    m = examples.fetch_all()
    ok = [e for e in m if e.get("file")]
    print(f"  {len(ok)}/{len(m)} images available")


if __name__ == "__main__":
    main()
