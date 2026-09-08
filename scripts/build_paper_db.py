#!/usr/bin/env python3
"""Build / update the pediatric radiology-AI paper database.

One row per paper: model name, modality, patient population, clinical problem,
a plain-language model description, journal, year, citations, DOI/link, and
whether the model is open-source, commercial, or unreleased.

The database is code, not a spreadsheet someone maintains. Candidates are the
pediatric radiology-AI PubMed query filtered to papers with at least
--min-citations citations in NIH iCite; each abstract is read once under a fixed
schema (pedrad_ai/extract.py); the row is stored with the hash of the text it
was read from, so a re-run only touches papers that are new or changed. Hand
corrections live in data/paper_db_overrides.json and are applied on export,
never baked into the stored row.

Two ways to fill in a row, both validated against the same schema:

  * the API path (needs ANTHROPIC_API_KEY) — the default, one structured-output
    call per abstract;
  * the worklist path (needs nothing) — --worklist dumps the outstanding papers
    with their abstracts to JSON, a person or a Claude Code session reads them
    and writes the rows back, and --ingest merges them.

Usage:
    python scripts/build_paper_db.py --dry-run          # how many are outstanding, and what it would cost
    python scripts/build_paper_db.py                    # API path: read up to --limit new papers
    python scripts/build_paper_db.py --all              # API path: read every outstanding paper
    python scripts/build_paper_db.py --worklist         # no API key: dump abstracts to read by hand
    python scripts/build_paper_db.py --ingest rows.json # merge hand-written rows back in
    python scripts/build_paper_db.py --min-citations 50 # raise the citation floor
    python scripts/build_paper_db.py --since 2023       # restrict the year window
    python scripts/build_paper_db.py --rebuild          # regenerate CSV/summary from the store, no API calls
    python scripts/build_paper_db.py --reextract        # re-read papers already in the store
    python scripts/build_paper_db.py --pmid 30153431    # one paper, for spot-checking

Outputs:
    data/processed/pedrad_paper_db.json          the store (every screened paper, with provenance)
    data/processed/pedrad_paper_db.csv           the table (included papers only)
    data/processed/pedrad_paper_db_summary.json  counts by year / modality / task / release
    data/processed/pedrad_paper_db_worklist.json papers waiting to be read (--worklist)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

from pedrad_ai import config, extract, paper_db, utils

# $ per million tokens, for the cost estimate only (Claude API list prices).
PRICES = {
    "claude-opus-5": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
}
# Measured shape of one extraction: a ~350-word abstract in, one JSON row out.
EST_INPUT_TOKENS = 1400
EST_OUTPUT_TOKENS = 600


def estimate_cost(n: int, model: str) -> str:
    price_in, price_out = PRICES.get(model, PRICES["claude-opus-5"])
    dollars = n * (EST_INPUT_TOKENS * price_in + EST_OUTPUT_TOKENS * price_out) / 1e6
    return f"~${dollars:,.2f}"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--limit", type=int, default=config.PAPER_DB_RUN_LIMIT,
                    help=f"max papers to read this run (default {config.PAPER_DB_RUN_LIMIT})")
    ap.add_argument("--all", action="store_true", help="no limit: read every outstanding paper")
    ap.add_argument("--since", type=int, default=config.PAPER_DB_START_YEAR, help="first publication year")
    ap.add_argument("--until", type=int, default=config.END_YEAR, help="last publication year")
    ap.add_argument("--min-citations", type=int, default=config.PAPER_DB_MIN_CITATIONS,
                    help=f"citation floor from NIH iCite (default {config.PAPER_DB_MIN_CITATIONS}; "
                         "0 keeps every paper the query returns)")
    ap.add_argument("--model", default=config.PAPER_DB_MODEL, help="extraction model")
    ap.add_argument("--effort", default=config.PAPER_DB_EFFORT,
                    choices=["low", "medium", "high", "xhigh", "max"], help="thinking effort")
    ap.add_argument("--workers", type=int, default=config.PAPER_DB_WORKERS, help="concurrent extractions")
    ap.add_argument("--reextract", action="store_true", help="re-read papers already in the store")
    ap.add_argument("--rebuild", action="store_true",
                    help="regenerate CSV and summary from the stored rows; makes no API calls")
    ap.add_argument("--dry-run", action="store_true", help="report what is outstanding, extract nothing")
    ap.add_argument("--pmid", action="append", default=[], help="extract specific PMID(s) only (repeatable)")
    ap.add_argument("--worklist", nargs="?", const=str(config.PAPER_DB_WORKLIST), default=None,
                    metavar="PATH",
                    help="write the outstanding papers and their abstracts to JSON for reading by "
                         "hand instead of calling the API, then stop")
    ap.add_argument("--ingest", metavar="PATH",
                    help="merge hand-written rows (the JSON produced by reading a worklist) into the store")
    ap.add_argument("--extractor", default="claude-code (manual)",
                    help="value recorded in extractor_model for --ingest rows")
    args = ap.parse_args()

    store = paper_db.load()
    overrides = paper_db.load_overrides()
    print(f"Store: {len(store['records'])} screened papers, "
          f"{sum(1 for r in store['records'].values() if r.get('include'))} in the database")
    if overrides:
        print(f"Overrides: {len(overrides)} hand-corrected papers")

    if args.rebuild:
        return _export(store, overrides)

    if args.ingest:
        return _ingest(store, overrides, Path(args.ingest), args.extractor)

    # ------------------------------------------------------------------ #
    # Which papers still need reading
    # ------------------------------------------------------------------ #
    if args.pmid:
        wanted = {p: {"year": None, "citations": None} for p in args.pmid}
        print(f"Candidates: {len(wanted)} PMID(s) given on the command line")
    else:
        print(f"Searching PubMed for candidates, {args.since}-{args.until}...")
        wanted = paper_db.candidates_with_citations(args.since, args.until, args.min_citations)
        print(f"Candidates: {len(wanted)} papers match the query with >= {args.min_citations} "
              f"citations in iCite")

    outstanding = [
        pmid for pmid in wanted
        if args.reextract or args.pmid or paper_db.needs_extraction(store, pmid)
    ]
    # Most-cited first: whatever the run reads, it reads the papers that matter
    # most to the field, and a capped run is a prefix of a full one.
    outstanding.sort(key=lambda p: (-(wanted[p]["citations"] or 0), -(wanted[p]["year"] or 0), p))
    print(f"Outstanding: {len(outstanding)} papers not yet read under prompt v{extract.PROMPT_VERSION}")

    todo = outstanding if (args.all or args.pmid) else outstanding[: args.limit]
    if args.dry_run:
        print(f"Would read {len(todo)} papers with {args.model} at effort={args.effort} "
              f"({estimate_cost(len(todo), args.model)})")
        return 0
    if not todo:
        print("Nothing to read; regenerating exports from the store.")
        return _export(store, overrides)

    if args.worklist:
        return _write_worklist(todo, wanted, Path(args.worklist))

    ok, why = extract.available()
    if not ok:
        print(f"Cannot extract: {why}")
        print("Keeping the existing database; regenerating exports from the store.")
        _export(store, overrides)
        return 0

    # ------------------------------------------------------------------ #
    # Read them
    # ------------------------------------------------------------------ #
    print(f"Fetching {len(todo)} PubMed records with abstracts...")
    articles = paper_db.fetch_articles(todo)
    for art in articles:
        art["citations"] = (wanted.get(art["pmid"]) or {}).get("citations")
    if not args.reextract and not args.pmid:
        # A record already read under the current prompt, from identical text,
        # needs no second read. The prompt check happened above; the text check
        # needs the article in hand, and catches the case where PubMed has since
        # attached an abstract to a record we read title-only.
        articles = [
            a for a in articles
            if paper_db.needs_extraction(store, a["pmid"]) or paper_db.stale_fingerprint(store, a)
        ]
    no_abstract = [a for a in articles if not (a.get("abstract") or "").strip()]
    if no_abstract:
        print(f"  {len(no_abstract)} of them have no abstract in PubMed (title-only records)")

    print(f"Reading {len(articles)} abstracts with {args.model} (effort={args.effort}, "
          f"{args.workers} at a time, {estimate_cost(len(articles), args.model)})...")

    usage = {"input": 0, "output": 0, "cached": 0}
    counters = {"included": 0, "excluded": 0, "errors": 0}

    def _on_result(idx: int, article: dict, extraction: dict) -> None:
        row = paper_db.build_row(article, extraction)
        store["records"][article["pmid"]] = row
        if extraction.get("error"):
            counters["errors"] += 1
        elif row.get("include"):
            counters["included"] += 1
        else:
            counters["excluded"] += 1
        u = extraction.get("usage") or {}
        usage["input"] += u.get("input_tokens", 0)
        usage["output"] += u.get("output_tokens", 0)
        usage["cached"] += u.get("cache_read_input_tokens", 0)
        done = counters["included"] + counters["excluded"] + counters["errors"]
        if done % 25 == 0 or done == len(articles):
            paper_db.save(store)  # checkpoint: an interrupted run resumes here
            print(f"  {done}/{len(articles)}  in:{counters['included']} out:{counters['excluded']} "
                  f"err:{counters['errors']}")

    try:
        extract.extract_many(
            articles, model=args.model, effort=args.effort, workers=args.workers, on_result=_on_result
        )
    except KeyboardInterrupt:
        print("\nInterrupted; saving what was read so far.")

    paper_db.save(store)
    print(f"Read {counters['included'] + counters['excluded'] + counters['errors']} papers: "
          f"{counters['included']} added, {counters['excluded']} screened out, {counters['errors']} failed")
    price_in, price_out = PRICES.get(args.model, PRICES["claude-opus-5"])
    spent = (usage["input"] * price_in + usage["output"] * price_out) / 1e6
    print(f"Tokens: {usage['input']:,} in ({usage['cached']:,} from cache), {usage['output']:,} out "
          f"(~${spent:,.2f})")
    return _export(store, overrides)


def _write_worklist(pmids: list[str], wanted: dict, path: Path) -> int:
    """Dump the outstanding papers, with abstracts, for reading without the API.

    The file is self-describing: it carries the same instructions and the same
    JSON schema the API path sends, so rows written from it are directly
    comparable with rows the model produced. Feed the result back with --ingest,
    which validates every row against that schema before storing it.
    """
    print(f"Fetching {len(pmids)} PubMed records with abstracts...")
    articles = paper_db.fetch_articles(pmids)
    by_pmid = {a["pmid"]: a for a in articles}
    papers = []
    for pmid in pmids:  # keep the most-cited-first order
        art = by_pmid.get(pmid)
        if art is None:
            continue
        doi = (art.get("doi") or "").strip()
        papers.append(
            {
                "pmid": pmid,
                "citations": (wanted.get(pmid) or {}).get("citations"),
                "year": art.get("year"),
                "title": art.get("title"),
                "journal": art.get("journal"),
                "doi": doi,
                "url": f"https://doi.org/{doi}" if doi else f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "authors": art.get("authors"),
                "publication_types": art.get("publication_types"),
                "mesh_terms": art.get("mesh_terms"),
                "abstract": art.get("abstract"),
            }
        )
    utils.save_json(
        {
            "generated_on": dt.date.today().isoformat(),
            "n_papers": len(papers),
            "prompt_version": extract.PROMPT_VERSION,
            "prompt_fingerprint": extract.prompt_fingerprint(),
            "instructions": extract.SYSTEM_PROMPT,
            "how_to_return": (
                "Write a JSON file mapping each PMID to an object with exactly the fields in "
                "'schema' below, then run: python scripts/build_paper_db.py --ingest <that file>. "
                "Every row is validated against the schema, so a wrong enum value or a missing "
                "field is rejected rather than silently stored."
            ),
            "schema": extract.PaperExtraction.model_json_schema(),
            "papers": papers,
        },
        path,
    )
    print(f"Wrote {len(papers)} papers to {path}")
    print("Read them, write the rows, then: "
          f"python scripts/build_paper_db.py --ingest <rows.json>")
    return 0


def _ingest(store: dict, overrides: dict, path: Path, extractor: str) -> int:
    """Merge hand-written rows into the store, validating each against the schema.

    Accepts either {"<pmid>": {...fields...}, ...} or a list of objects that
    each carry a "pmid". Rows that fail validation are reported and skipped;
    the rest are stored with the same provenance stamps the API path writes, so
    they are never re-read and the table cannot tell them apart except by
    ``extractor_model``.
    """
    from pedrad_ai import icite

    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = [{**fields, "pmid": str(pmid)} for pmid, fields in raw.items()
               if not str(pmid).startswith("_")]
    if not isinstance(raw, list):
        print(f"{path}: expected a JSON object keyed by PMID, or a list of rows")
        return 1

    valid: dict[str, Any] = {}
    for entry in raw:
        pmid = str(entry.get("pmid") or "")
        fields = {k: v for k, v in entry.items() if k != "pmid"}
        if not pmid:
            print("  skipped a row with no pmid")
            continue
        try:
            valid[pmid] = extract.PaperExtraction.model_validate(fields).model_dump()
        except Exception as exc:
            first = str(exc).splitlines()[1] if len(str(exc).splitlines()) > 1 else str(exc)
            print(f"  {pmid}: rejected — {first.strip()}")
    if not valid:
        print("No valid rows to ingest.")
        return 1

    print(f"Fetching {len(valid)} PubMed records to attach titles, DOIs and fingerprints...")
    articles = {a["pmid"]: a for a in paper_db.fetch_articles(list(valid))}
    citations = icite.citation_counts(list(valid))

    added = excluded = 0
    for pmid, fields in valid.items():
        article = articles.get(pmid)
        if article is None:
            print(f"  {pmid}: not in PubMed, skipped")
            continue
        extraction = {
            **fields,
            "extractor_model": extractor,
            "extractor_effort": "manual",
            "prompt_version": extract.PROMPT_VERSION,
            "prompt_fingerprint": extract.prompt_fingerprint(),
            "input_fingerprint": extract.input_fingerprint(article),
        }
        row = paper_db.build_row(article, extraction, citations=citations.get(pmid))
        store["records"][pmid] = row
        if row.get("include"):
            added += 1
        else:
            excluded += 1
    print(f"Ingested {added + excluded} rows: {added} added, {excluded} screened out")
    return _export(store, overrides)


def _export(store: dict, overrides: dict) -> int:
    """Write the CSV, the summary, and the markdown view from the stored rows."""
    json_path = paper_db.save(store)
    csv_path = paper_db.write_csv(store, overrides=overrides)
    summary = paper_db.summarize(store, overrides)
    utils.save_json(summary, config.PAPER_DB_SUMMARY)
    md_path = paper_db.write_markdown(store, overrides=overrides)

    print(f"\n{summary['n_included']} papers in the database "
          f"({summary['n_excluded']} screened out of {summary['n_candidates_screened']} read)")
    print(f"  named models: {summary['n_named_models']}   with a code URL: {summary['n_with_code_url']}")
    if summary["by_release_status"]:
        print("  release: " + ", ".join(f"{k} {v}" for k, v in summary["by_release_status"].items()))
    if summary["by_modality"]:
        print("  modality: " + ", ".join(f"{k} {v}" for k, v in list(summary["by_modality"].items())[:6]))
    print(f"Wrote {json_path.relative_to(config.REPO_ROOT)}, "
          f"{csv_path.relative_to(config.REPO_ROOT)}, "
          f"{config.PAPER_DB_SUMMARY.relative_to(config.REPO_ROOT)}, "
          f"{md_path.relative_to(config.REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
