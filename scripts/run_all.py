#!/usr/bin/env python3
"""Run the full pipeline end to end: collect -> figures -> reports.

Usage:
    python scripts/run_all.py            # full run
    python scripts/run_all.py --quick    # headline PubMed queries only

Each collector is wrapped so a single network failure (e.g. a service blocked in
the current environment) does not abort the whole pipeline; the report builder
degrades gracefully when a data file is missing.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run(script: str, *args: str) -> None:
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    print(f"\n=== {' '.join(cmd[1:])} ===")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"  [warn] {script} exited with {exc.returncode}; continuing.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    pub_args = ["--quick"] if args.quick else []
    run("collect_pubmed.py", *pub_args)
    run("collect_landscape.py")
    run("collect_conferences.py")
    run("collect_patents.py")
    run("make_figures.py")
    run("build_reports.py")
    print("\nPipeline complete. See reports/ and figures/.")


if __name__ == "__main__":
    main()
