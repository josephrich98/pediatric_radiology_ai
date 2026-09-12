#!/usr/bin/env python3
"""Top up the review database: re-run the searches, screen whatever is new.

This is the narrow, monthly counterpart to ``scripts/refresh.py``. Refresh
re-collects every count-based view (PubMed trends, patents, conferences,
newsletters, FDA) and rebuilds every deliverable, and its paper-database step
runs the *reading-list* query with its impact floors. This script touches only
the systematic-review database: it re-runs ``config.REVIEW_QUERY`` over a recent
window, reads the abstracts that are new since the last run, recomputes the
PRISMA partition and the merged table, and redraws the review figures.

Sources, and what is deliberately absent:

* **PubMed** — ``config.REVIEW_QUERY``, one ESearch per year, no impact floor
  (eligibility is decided at screening, not by citations).
* **Preprints** — OpenAlex ``type:preprint`` for the translated query, which is
  where much of the methods work appears before PubMed sees it.
* **Conference papers** — OpenAlex ``type:conference-paper`` plus the LNCS pass.
  They are screened into the store and then partitioned out of the corpus by
  publication form, exactly as in a manual run.
* **Embase** is *not* re-run. It has no API and its export is a licensed,
  hand-driven download from embase.com (see ``scripts/embase_layer.py`` and
  ``reports/06_search_strategy.md`` section 4.3). The committed Embase records
  are reused as they stand; if the review is updated for a new submission, redo
  that export by hand and re-run ``embase_layer.py``.

The window matters. The store already holds every record the search returned
back to ``config.REVIEW_START_YEAR``, so a monthly run only needs to reach far
enough back to catch new indexing, not to re-search twenty years: ``--years-back
2`` (the default) searches the current and previous two calendar years. Pass
``--since 2005`` to redo the whole window, which is the right thing to do after
a change to ``REVIEW_QUERY``.

Cost. Screening is the only step that spends money: one structured-output call
per new abstract (~$0.01 with the default model), capped at ``--limit`` papers
per run. With no ``ANTHROPIC_API_KEY`` the run still re-searches and refreshes
the metrics, and ``--worklist`` writes the outstanding abstracts out for reading
without the API.

Usage:
    python scripts/update_database.py --dry-run     # what is new, and what it would cost
    python scripts/update_database.py               # last 3 calendar years, up to --limit papers
    python scripts/update_database.py --all         # read every outstanding paper
    python scripts/update_database.py --since 2005  # re-search the full review window
    python scripts/update_database.py --worklist    # no API key: dump abstracts to read by hand

Scheduling. ``.github/workflows/update_database.yml`` runs this monthly and
opens a pull request; it is disabled until the repository variable
``UPDATE_DATABASE_ENABLED`` is set to ``true``. To run it on this machine
instead, a crontab line does the same thing without GitHub:

    23 7 8 * * cd /path/to/pediatric_radiology_ai && \
      /path/to/python scripts/update_database.py >> data/logs/cron.log 2>&1

Every step is wrapped, so one unreachable service never aborts the run; the exit
code is non-zero only with --strict.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
LOGS = REPO / "data" / "logs"
STORE = REPO / "data" / "processed" / "pedrad_paper_db.json"

sys.path.insert(0, str(SCRIPTS))
from refresh import run_step  # noqa: E402  (same log format as the full refresh)

CACHE = REPO / "data" / "raw" / "cache"

# Cached responses that would hide a newly indexed paper: a PubMed ESearch
# result list, an OpenAlex page, an iCite metrics lookup. Everything else in the
# cache — above all the EFetch records of papers already read, which do not
# change — is kept, so this costs one re-search rather than a cold re-pull.
_STALE_MARKERS = (
    b"<eSearchResult",            # PubMed: the PMID list for a year
    b'"openalex"',                # OpenAlex: preprint / conference / FWCI lookups
    b"relative_citation_ratio",   # iCite: citations, citations/year, RCR
)


def clear_search_cache(dry_run: bool) -> tuple[int, int]:
    """Drop the cached searches and metric lookups; keep fetched records."""
    if not CACHE.exists():
        return 0, 0
    removed = kept = 0
    for f in CACHE.glob("*.cache"):
        try:
            head = f.read_bytes()[:4096]
        except OSError:
            head = b""
        if any(m in head for m in _STALE_MARKERS):
            removed += 1
            if not dry_run:
                f.unlink()
        else:
            kept += 1
    return removed, kept


def store_counts() -> dict[str, int]:
    """Header counts of the screening store: records, included, corpus."""
    try:
        head = json.loads(STORE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {k: head.get(k) or 0 for k in ("n_records", "n_included", "n_corpus")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--years-back", type=int, default=2,
                    help="search the current year and this many before it (default: 2)")
    ap.add_argument("--since", type=int, default=None,
                    help="first publication year to search (overrides --years-back); "
                         "use config.REVIEW_START_YEAR to redo the whole window")
    ap.add_argument("--limit", type=int, default=None,
                    help="max new abstracts to read this run (default: config.PAPER_DB_RUN_LIMIT)")
    ap.add_argument("--all", action="store_true", help="read every outstanding paper")
    ap.add_argument("--worklist", action="store_true",
                    help="write the outstanding papers out to be read without an API key")
    ap.add_argument("--no-metrics", action="store_true",
                    help="skip the citation/RCR/FWCI refresh over the stored rows")
    ap.add_argument("--no-fwci", action="store_true",
                    help="refresh metrics without the OpenAlex FWCI half (saves its daily budget)")
    ap.add_argument("--no-figures", action="store_true", help="skip make_review_figures.py")
    ap.add_argument("--keep-cache", action="store_true",
                    help="do not drop the cached searches first (a cached ESearch hides new records)")
    ap.add_argument("--summary", type=Path, default=None,
                    help="write a markdown summary here (default: data/logs/update-<stamp>.md)")
    ap.add_argument("--strict", action="store_true", help="exit non-zero if any step failed")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, touch nothing")
    args = ap.parse_args()

    from pedrad_ai import config  # after argparse so --help needs no import

    since = args.since if args.since is not None else config.END_YEAR - args.years_back
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    LOGS.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    results: dict[str, bool] = {}
    t_start = time.time()
    before = store_counts()

    print(f"Database update started {dt.datetime.now():%Y-%m-%d %H:%M} (repo: {REPO})")
    print(f"Search window: {since}-{config.END_YEAR}  (REVIEW_QUERY, no impact floor)")
    print(f"Store before: {before.get('n_records', 0)} screened, "
          f"{before.get('n_corpus', 0)} in the corpus")

    # A cached ESearch would return the PMID list as it stood at the last pull,
    # which is exactly the thing this run exists to look past.
    if args.keep_cache:
        print("Cache: kept (--keep-cache)")
    else:
        removed, kept = clear_search_cache(dry_run=args.dry_run)
        print(f"Cache: {'would remove' if args.dry_run else 'removed'} {removed} cached searches "
              f"and metric lookups, kept {kept} fetched records")

    # 1. Search + screen. --review swaps in REVIEW_QUERY and drops the impact
    #    floors; --order rate puts the recent years first, because a capped run
    #    ordered by raw citations would never reach the current year.
    cmd = [py, str(SCRIPTS / "build_paper_db.py"), "--review", "--since", str(since),
           "--order", "rate"]
    if args.all:
        cmd.append("--all")
    elif args.limit is not None:
        cmd += ["--limit", str(args.limit)]
    if args.worklist:
        cmd.append("--worklist")
    if args.dry_run:
        cmd.append("--dry-run")
    results["screen"], _ = run_step("screen", cmd, LOGS / f"update-{stamp}-screen.log", False)

    if args.dry_run:
        print("\nDry run: nothing was read, stored or exported.")
        return 0

    # 2. Citations, RCR and FWCI move for every stored row, not just the new
    #    ones, and the corpus ranks on them.
    if not args.no_metrics:
        cmd = [py, str(SCRIPTS / "build_paper_db.py"), "--refresh-metrics"]
        if args.no_fwci:
            cmd.append("--no-fwci")
        results["metrics"], _ = run_step("metrics", cmd, LOGS / f"update-{stamp}-metrics.log", False)

    # 3. Everything downstream of the store: the PRISMA partition and the
    #    manuscript's numbers, the merged paper table, the review figures.
    results["reviewstats"], _ = run_step("reviewstats", [py, str(SCRIPTS / "review_stats.py")],
                                         LOGS / f"update-{stamp}-reviewstats.log", False)
    results["unifieddb"], _ = run_step("unifieddb", [py, str(SCRIPTS / "export_unified_db.py")],
                                       LOGS / f"update-{stamp}-unifieddb.log", False)
    if not args.no_figures:
        results["reviewfigures"], _ = run_step(
            "reviewfigures", [py, str(SCRIPTS / "make_review_figures.py")],
            LOGS / f"update-{stamp}-reviewfigures.log", False)

    after = store_counts()
    delta = {k: (after.get(k, 0) - before.get(k, 0)) for k in after}
    failed = [k for k, ok in results.items() if not ok]

    lines = [
        f"Database update {stamp}",
        "",
        f"- Search window: {since}-{config.END_YEAR} (`REVIEW_QUERY`, PubMed + OpenAlex "
        "preprints + conference papers; Embase not re-run)",
        f"- Screened records: {before.get('n_records', 0)} -> {after.get('n_records', 0)} "
        f"({delta.get('n_records', 0):+d})",
        f"- Included (primary studies in the corpus): {before.get('n_corpus', 0)} -> "
        f"{after.get('n_corpus', 0)} ({delta.get('n_corpus', 0):+d})",
        f"- Steps: " + ", ".join(f"{k} {'ok' if ok else 'FAILED'}" for k, ok in results.items()),
    ]
    if failed:
        lines.append(f"- Failed steps: {', '.join(failed)} (see `data/logs/update-{stamp}-*.log`)")
    if delta.get("n_corpus", 0):
        lines += ["", "The corpus changed, so the numbers in `reports/05_review_manuscript.md` "
                      "are now behind `data/processed/review_stats.json`. Check them before "
                      "merging."]
        if args.no_figures:
            lines.append("The review figures were not redrawn: run "
                         "`python scripts/make_review_figures.py`.")
    summary = "\n".join(lines) + "\n"

    path = args.summary or (LOGS / f"update-{stamp}.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(summary, encoding="utf-8")

    print()
    print(summary)
    print(f"Finished in {(time.time() - t_start)/60:.1f} min; summary: {path}")
    return 1 if (failed and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
