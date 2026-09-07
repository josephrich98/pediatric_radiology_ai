#!/usr/bin/env python3
"""Refresh everything to today: clear the HTTP cache, re-collect, rebuild.

This is the one command behind both a manual refresh and the scheduled GitHub
Action (.github/workflows/refresh.yml).

Usage:
    python scripts/refresh.py                 # full refresh (30-60 min)
    python scripts/refresh.py --quick         # headline PubMed queries only
    python scripts/refresh.py --keep-cache    # re-run without re-fetching
    python scripts/refresh.py --no-slides     # skip build_slides + latexmk
    python scripts/refresh.py --skip conferences --skip patents
    python scripts/refresh.py --dry-run       # print the plan, touch nothing

Cache policy: the on-disk HTTP cache (data/raw/cache/) makes re-runs
reproducible but also freezes counts at the time of the first pull, so a
refresh deletes it. DBLP entries are kept by default because DBLP throttles
hard and a cold re-pull can lose venue-years; pass --drop-dblp-cache to
re-sample those too.

Every step is wrapped so one unreachable service never aborts the run; the
exit code is non-zero only when --strict is given and a step failed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
CACHE = REPO / "data" / "raw" / "cache"
LOGS = REPO / "data" / "logs"
SLIDES = REPO / "slides"

COLLECTORS = {
    "pubmed": "collect_pubmed.py",
    "landscape": "collect_landscape.py",
    "conferences": "collect_conferences.py",
    "patents": "collect_patents.py",
    "newsletters": "collect_newsletters.py",
    "fda": "collect_fda.py",
    "validation": "validate_queries.py",
    "examples": "collect_examples.py",
}


def clear_cache(keep_dblp: bool, dry_run: bool) -> tuple[int, int]:
    """Delete cached responses; optionally keep the DBLP ones. Returns (removed, kept)."""
    if not CACHE.exists():
        return 0, 0
    removed = kept = 0
    for f in CACHE.glob("*.cache"):
        if keep_dblp:
            try:
                head = f.read_bytes()[:4096]
            except OSError:
                head = b""
            if b"dblp" in head:
                kept += 1
                continue
        removed += 1
        if not dry_run:
            f.unlink()
    return removed, kept


def run_step(name: str, cmd: list[str], log: Path, dry_run: bool) -> tuple[bool, float]:
    print(f"\n=== {name}: {' '.join(cmd)}")
    if dry_run:
        return True, 0.0
    t0 = time.time()
    with log.open("w", encoding="utf-8") as fh:
        proc = subprocess.run(cmd, cwd=REPO, stdout=fh, stderr=subprocess.STDOUT)
    ok = proc.returncode == 0
    secs = time.time() - t0
    tail = log.read_text(encoding="utf-8", errors="replace").splitlines()[-3:]
    for line in tail:
        print(f"    {line}")
    print(f"    -> {'ok' if ok else f'FAILED (exit {proc.returncode})'} in {secs/60:.1f} min; log: {log.relative_to(REPO)}")
    return ok, secs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="headline PubMed queries only")
    ap.add_argument("--keep-cache", action="store_true", help="do not clear data/raw/cache/")
    ap.add_argument("--drop-dblp-cache", action="store_true", help="also clear cached DBLP responses")
    ap.add_argument("--no-slides", action="store_true", help="skip build_slides.py and latexmk")
    ap.add_argument("--skip", action="append", default=[], choices=sorted(COLLECTORS),
                    help="collector(s) to skip (repeatable)")
    ap.add_argument("--strict", action="store_true", help="exit non-zero if any step fails")
    ap.add_argument("--dry-run", action="store_true", help="print the plan without running anything")
    args = ap.parse_args()

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    LOGS.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    results: dict[str, bool] = {}
    t_start = time.time()

    print(f"Refresh started {dt.datetime.now():%Y-%m-%d %H:%M} (repo: {REPO})")
    if args.keep_cache:
        print("Cache: kept (--keep-cache)")
    else:
        removed, kept = clear_cache(keep_dblp=not args.drop_dblp_cache, dry_run=args.dry_run)
        print(f"Cache: {'would remove' if args.dry_run else 'removed'} {removed} entries, kept {kept} DBLP entries")

    for key, script in COLLECTORS.items():
        if key in args.skip:
            print(f"\n=== {key}: skipped")
            continue
        cmd = [py, str(SCRIPTS / script)]
        if key == "pubmed" and args.quick:
            cmd.append("--quick")
        results[key], _ = run_step(key, cmd, LOGS / f"refresh-{stamp}-{key}.log", args.dry_run)

    results["figures"], _ = run_step("figures", [py, str(SCRIPTS / "make_figures.py")],
                                     LOGS / f"refresh-{stamp}-figures.log", args.dry_run)
    results["reports"], _ = run_step("reports", [py, str(SCRIPTS / "build_reports.py")],
                                     LOGS / f"refresh-{stamp}-reports.log", args.dry_run)

    if not args.no_slides:
        results["slides"], _ = run_step("slides", [py, str(SCRIPTS / "build_slides.py")],
                                        LOGS / f"refresh-{stamp}-slides.log", args.dry_run)
        if shutil.which("latexmk"):
            results["pdf"], _ = run_step(
                "pdf",
                ["latexmk", "-pdf", "-interaction=nonstopmode", "-cd", str(SLIDES / "pedrad_ai_slides.tex")],
                LOGS / f"refresh-{stamp}-pdf.log", args.dry_run,
            )
        else:
            print("\n=== pdf: latexmk not found; slides/pedrad_ai_slides.tex written but not compiled")

    print(f"\nRefresh {'plan' if args.dry_run else 'finished'} in {(time.time() - t_start)/60:.1f} min")
    failed = [k for k, ok in results.items() if not ok]
    for k, ok in results.items():
        print(f"  {k:12s} {'ok' if ok else 'FAILED'}")
    if failed:
        print(f"Failed steps: {', '.join(failed)} (see data/logs/refresh-{stamp}-*.log)")
    print("Outputs: data/processed/, figures/, reports/, slides/")
    return 1 if (failed and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
