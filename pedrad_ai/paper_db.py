"""The pediatric radiology-AI paper database: one structured row per paper.

The counting collectors say how much is being published; this module says what
was published. Each row names the model, the modality, the children it was
built for, the clinical problem it addresses, what it does in a few plain
sentences, and — the column clinical leadership asks about first — whether
anyone outside the authors' institution can actually use it.

How it stays reproducible and updatable
---------------------------------------
* **Candidates** come from one PubMed query (``config.PAPER_DB_QUERY``), year by
  year, filtered to those with at least ``PAPER_DB_MIN_CITATIONS`` citations in
  NIH iCite — so the corpus is defined by code, not by hand-picking.
* **Rows** are written either by :mod:`pedrad_ai.extract` (a Claude API call per
  abstract) or by hand through the worklist/ingest path, which validates against
  the same schema. Which one produced a row is recorded in ``extractor_model``.
* **Nothing is read twice.** Every row records the hash of the exact text the
  model saw plus the prompt/schema version. A paper is re-extracted only when
  it is new, when PubMed has changed the record (an abstract appears, a title is
  corrected), or when the schema or prompt version is bumped. So a run is
  incremental, an interrupted run resumes, and a fresh clone rebuilds the whole
  database from the committed JSON with no API calls.
* **Hand corrections survive.** ``data/paper_db_overrides.json`` maps a PMID to
  field values that are applied after extraction and recorded in
  ``overridden_fields``; re-extraction never clobbers them.
* **Deterministic output.** Rows are sorted by year then PMID and written with
  stable key order, so the committed JSON and CSV diff meaningfully.

The store keeps screened-out papers too (``include: false``), so a rejected
record costs one extraction, once, rather than one per refresh.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any, Iterable

from . import config, extract, icite, pubmed, utils

# Column order for the CSV / markdown table. The first block is the answer to
# "what is this paper about"; provenance trails at the end.
COLUMNS = [
    "model_name",
    "model_family",
    "modality",
    "body_region",
    "patient_population",
    "age_groups",
    "clinical_problem",
    "task",
    "model_description",
    "release_status",
    "release_evidence",
    "code_url",
    "journal",
    "year",
    "citations",
    "doi",
    "url",
    "title",
    "first_author",
    "study_design",
    "dataset_size",
    "data_source",
    "validation",
    "headline_result",
    "pmid",
    "confidence",
    "overridden_fields",
    "extractor_model",
    "prompt_version",
    "extracted_on",
]

# Fields a human may override in data/paper_db_overrides.json.
OVERRIDABLE = {
    c
    for c in COLUMNS
    if c
    not in {"pmid", "citations", "overridden_fields", "extractor_model", "prompt_version", "extracted_on"}
} | {"include", "exclusion_reason"}


# --------------------------------------------------------------------------- #
# Store
# --------------------------------------------------------------------------- #
def load(path: str | Path | None = None) -> dict[str, Any]:
    """Load the store, or an empty one. Records are keyed by PMID."""
    path = Path(path or config.PAPER_DB_JSON)
    if not path.exists():
        return {"schema_version": config.PAPER_DB_SCHEMA_VERSION, "updated": None, "records": {}}
    raw = utils.load_json(path)
    records = raw.get("records", [])
    if isinstance(records, list):
        records = {r["pmid"]: r for r in records if r.get("pmid")}
    return {
        "schema_version": raw.get("schema_version", 0),
        "updated": raw.get("updated"),
        "records": records,
    }


def save(store: dict[str, Any], path: str | Path | None = None) -> Path:
    """Write the store back, deterministically ordered."""
    path = Path(path or config.PAPER_DB_JSON)
    return utils.save_json(
        {
            "schema_version": config.PAPER_DB_SCHEMA_VERSION,
            "prompt_version": extract.PROMPT_VERSION,
            "updated": dt.date.today().isoformat(),
            "source_query": config.PAPER_DB_QUERY,
            "min_citations": config.PAPER_DB_MIN_CITATIONS,
            "start_year": config.PAPER_DB_START_YEAR,
            "n_records": len(store["records"]),
            "n_included": sum(1 for r in store["records"].values() if r.get("include")),
            "records": sorted_records(store),
        },
        path,
    )


def sorted_records(store: dict[str, Any]) -> list[dict[str, Any]]:
    """Records newest first, then by PMID — stable across runs."""
    return sorted(
        store["records"].values(),
        key=lambda r: (-(r.get("year") or 0), str(r.get("pmid"))),
    )


def presented(store: dict[str, Any], overrides: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Stored rows with hand corrections applied, newest first.

    Overrides are applied here rather than baked into the stored row, so the
    stored row always remains exactly what the extractor produced and deleting
    an entry from the overrides file reverts the table on the next rebuild.
    """
    overrides = load_overrides() if overrides is None else overrides
    out = []
    for rec in sorted_records(store):
        row = dict(rec)
        override = overrides.get(str(rec.get("pmid")))
        if override:
            applied = sorted(k for k in override if k in OVERRIDABLE)
            for key in applied:
                row[key] = override[key]
            row["overridden_fields"] = applied
        else:
            row["overridden_fields"] = []
        out.append(row)
    return out


def included(store: dict[str, Any], overrides: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return [r for r in presented(store, overrides) if r.get("include")]


def write_csv(
    store: dict[str, Any],
    path: str | Path | None = None,
    overrides: dict[str, dict[str, Any]] | None = None,
) -> Path:
    """Export the included rows as a flat table (lists joined with '; ').

    An empty database still gets its header row, so the columns are readable
    before the first extraction run.
    """
    path = Path(path or config.PAPER_DB_CSV)
    rows = []
    for rec in included(store, overrides):
        row = {}
        for col in COLUMNS:
            val = rec.get(col, "")
            row[col] = "; ".join(str(v) for v in val) if isinstance(val, list) else val
        rows.append(row)
    if not rows:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(",".join(COLUMNS) + "\n", encoding="utf-8")
        return path
    return utils.save_csv(rows, path, columns=COLUMNS)


# --------------------------------------------------------------------------- #
# Candidates
# --------------------------------------------------------------------------- #
def candidate_pmids(
    start_year: int | None = None, end_year: int | None = None, query: str | None = None
) -> dict[str, int]:
    """PMID -> year for every paper matching :data:`config.PAPER_DB_QUERY`.

    One ESearch per year, which caches cleanly and keeps the year facet (rather
    than "now") as the thing that dates a record. Note this is the strict,
    title/abstract-fielded query, not the broader counting query — see the note
    on ``PAPER_DB_QUERY`` in config.
    """
    query = query or config.PAPER_DB_QUERY
    start = start_year or config.PAPER_DB_START_YEAR
    end = end_year or config.END_YEAR
    out: dict[str, int] = {}
    for year in range(start, end + 1):
        for pmid in pubmed.pmids_for_year(query, year):
            out.setdefault(pmid, year)
    return out


def candidates_with_citations(
    start_year: int | None = None,
    end_year: int | None = None,
    min_citations: int | None = None,
    query: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Candidate PMIDs that clear the citation floor: pmid -> {year, citations}.

    The query returns roughly ten thousand records; most are never cited and
    reading them would cost far more than it is worth. Citation counts come
    from NIH iCite in batches, which is one request per 250 PMIDs.

    The floor doubles as a recency filter — the current year's papers have had
    no time to accrue citations — so callers that want the newest work should
    lower it deliberately rather than assume the table is complete.
    """
    min_citations = config.PAPER_DB_MIN_CITATIONS if min_citations is None else min_citations
    years = candidate_pmids(start_year, end_year, query)
    counts = icite.citation_counts(list(years)) if min_citations >= 0 else {}
    return {
        pmid: {"year": year, "citations": counts.get(pmid, 0)}
        for pmid, year in years.items()
        if counts.get(pmid, 0) >= min_citations
    }


def needs_extraction(store: dict[str, Any], pmid: str) -> bool:
    """True if this PMID has never been read, or was read under an old prompt.

    A record whose input fingerprint no longer matches (PubMed attached an
    abstract, say) is caught later, in :func:`stale_fingerprint`, once the
    article text is in hand.
    """
    rec = store["records"].get(pmid)
    if rec is None:
        return True
    if rec.get("error"):
        return True
    return rec.get("prompt_fingerprint") != extract.prompt_fingerprint()


def stale_fingerprint(store: dict[str, Any], article: dict[str, Any]) -> bool:
    """True if the record we hold was built from different text than we now have."""
    rec = store["records"].get(article["pmid"])
    if rec is None:
        return True
    return rec.get("input_fingerprint") != extract.input_fingerprint(article)


def fetch_articles(pmids: Iterable[str]) -> list[dict[str, Any]]:
    """PubMed records with abstracts, for the PMIDs that need reading."""
    pmids = list(pmids)
    if not pmids:
        return []
    return pubmed.article_details(pmids, with_abstract=True)


# --------------------------------------------------------------------------- #
# Row assembly
# --------------------------------------------------------------------------- #
_CODE_HOST_RE = re.compile(
    r"\b(?:https?://)?(?:www\.)?(" + "|".join(re.escape(h) for h in config.PAPER_DB_CODE_HOSTS) + r")/[\w\-./#?=&%~+]+",
    re.I,
)


def find_code_url(text: str) -> str:
    """First code-hosting URL in the text, normalized. Empty string if none.

    Abstracts that say "code is available at github.com/..." are the single
    most reliable open-source signal in the corpus, and a regex catches them
    more consistently than a model does.
    """
    match = _CODE_HOST_RE.search(text or "")
    if not match:
        return ""
    url = match.group(0).rstrip(").,;")
    return url if url.startswith("http") else f"https://{url}"


def _commercial_names() -> list[tuple[str, str]]:
    """(name, evidence) pairs for products we already know are commercial.

    Drawn from the curated pediatric-product list and the pediatric-named
    devices on the FDA AI list, so the database's release column agrees with
    the commercial-players analysis instead of re-deciding it per abstract.
    """
    names: list[tuple[str, str]] = []
    for prod in config.COMMERCIAL_PEDIATRIC:
        for part in re.split(r"[,/]", prod["product"]):
            part = part.strip()
            if len(part) >= 4:
                names.append((part, f"{prod['vendor']} {prod['product']} (curated commercial list)"))
        vendor = prod["vendor"].strip()
        if len(vendor) >= 4 and "/" not in vendor:
            names.append((vendor, f"{vendor} (curated commercial list)"))
    fda_path = config.PROCESSED_DIR / "fda_ai_devices.json"
    if fda_path.exists():
        try:
            fda = utils.load_json(fda_path)
        except Exception:
            fda = {}
        for dev in fda.get("pediatric_name_hits", []):
            name = re.sub(r"\s*\(.*?\)\s*", " ", dev.get("device", "")).strip()
            name = re.split(r"\s+-\s+|\s+v\d", name)[0].strip()
            if len(name) >= 4:
                names.append((name, f"FDA AI device list: {dev.get('device')} ({dev.get('company')})"))
    # Longest first so "EFAI Bonesuite Bone Age Pro" wins over "Bone Age".
    return sorted(set(names), key=lambda t: -len(t[0]))


_COMMERCIAL_CACHE: list[tuple[str, str]] | None = None


def match_commercial(*fields: str) -> tuple[str, str]:
    """(name, evidence) if any known commercial product is named in ``fields``."""
    global _COMMERCIAL_CACHE
    if _COMMERCIAL_CACHE is None:
        _COMMERCIAL_CACHE = _commercial_names()
    haystack = " ".join(f for f in fields if f)
    for name, evidence in _COMMERCIAL_CACHE:
        if re.search(rf"\b{re.escape(name)}\b", haystack, re.I):
            return name, evidence
    return "", ""


def load_overrides(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """Hand corrections, keyed by PMID. Missing file means none."""
    path = Path(path or config.PAPER_DB_OVERRIDES)
    if not path.exists():
        return {}
    raw = utils.load_json(path)
    return {str(k): v for k, v in raw.items() if isinstance(v, dict) and not k.startswith("_")}


def build_row(
    article: dict[str, Any], extraction: dict[str, Any], citations: int | None = None
) -> dict[str, Any]:
    """Merge a PubMed record and its extraction into one stored row.

    Hand overrides are *not* applied here — see :func:`presented`.
    """
    doi = (article.get("doi") or "").strip()
    row: dict[str, Any] = {
        "pmid": article["pmid"],
        "title": article.get("title", ""),
        "journal": article.get("journal", ""),
        "year": article.get("year"),
        "doi": doi,
        "url": f"https://doi.org/{doi}" if doi else f"https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/",
        "first_author": (article.get("authors") or [""])[0],
        "citations": article.get("citations") if citations is None else citations,
        "citations_as_of": dt.date.today().isoformat(),
        "extracted_on": dt.date.today().isoformat(),
    }

    if extraction.get("error"):
        row.update({"include": False, "error": extraction["error"]})
    else:
        row["include"] = bool(extraction.get("is_pediatric_radiology_ai"))
        for key in (
            "exclusion_reason", "model_name", "model_family", "modality", "body_region",
            "clinical_problem", "patient_population", "age_groups", "task",
            "model_description", "release_status", "release_evidence", "code_url",
            "dataset_size", "data_source", "validation", "headline_result",
            "study_design", "confidence",
        ):
            row[key] = extraction.get(key, "")
    for key in ("extractor_model", "extractor_effort", "prompt_version", "prompt_fingerprint", "input_fingerprint"):
        row[key] = extraction.get(key)

    if row.get("include"):
        _apply_release_evidence(row, article)
    return row


def _apply_release_evidence(row: dict[str, Any], article: dict[str, Any]) -> None:
    """Upgrade the release column from evidence the model can't be trusted to weigh.

    A repository URL in the abstract settles "open-source" outright, and a
    product we already track as commercial settles "commercial". Both only
    *upgrade* an unclear or unreleased verdict; an explicit call by the model is
    left alone.
    """
    text = " ".join([article.get("abstract") or "", row.get("code_url") or "", row.get("release_evidence") or ""])
    url = find_code_url(text)
    if url:
        row["code_url"] = row.get("code_url") or url
        if row.get("release_status") in ("unclear", "unreleased", "", None):
            row["release_status"] = "open-source"
            row["release_evidence"] = (row.get("release_evidence") or "").strip() or f"code URL in abstract: {url}"
        return

    name, evidence = match_commercial(row.get("model_name", ""), article.get("title", ""))
    if name and row.get("release_status") in ("unclear", "unreleased", "", None):
        row["release_status"] = "commercial"
        row["release_evidence"] = evidence


# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #
def summarize(store: dict[str, Any], overrides: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Counts the report and slides quote: by year, modality, task, release."""
    rows = included(store, overrides)

    def _tally(key: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for rec in rows:
            val = rec.get(key)
            for item in val if isinstance(val, list) else [val]:
                if item:
                    out[str(item)] = out.get(str(item), 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    named = [r for r in rows if (r.get("model_name") or "").strip()]
    return {
        "generated_on": dt.date.today().isoformat(),
        "source_query": config.PAPER_DB_QUERY,
        "years": [config.PAPER_DB_START_YEAR, config.END_YEAR],
        "min_citations": config.PAPER_DB_MIN_CITATIONS,
        "median_citations": (
            sorted(r.get("citations") or 0 for r in rows)[len(rows) // 2] if rows else 0
        ),
        "n_candidates_screened": len(store["records"]),
        "n_included": len(rows),
        "n_excluded": len(store["records"]) - len(rows),
        "n_named_models": len(named),
        "n_with_code_url": sum(1 for r in rows if (r.get("code_url") or "").strip()),
        "by_year": dict(sorted(_tally("year").items())),
        "by_modality": _tally("modality"),
        "by_task": _tally("task"),
        "by_release_status": _tally("release_status"),
        "by_age_group": _tally("age_groups"),
        "by_validation": _tally("validation"),
        "by_data_source": _tally("data_source"),
        "top_journals": dict(list(_tally("journal").items())[:20]),
    }


# --------------------------------------------------------------------------- #
# Markdown view
# --------------------------------------------------------------------------- #
def _md_cell(value: Any, limit: int = 0) -> str:
    """One table cell: lists joined, pipes escaped, optionally truncated."""
    if isinstance(value, list):
        value = "; ".join(str(v) for v in value)
    text = str(value or "").replace("|", "\\|").replace("\n", " ").strip()
    if limit and len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text or "—"


def write_markdown(
    store: dict[str, Any],
    path: str | Path | None = None,
    overrides: dict[str, dict[str, Any]] | None = None,
    named_only_limit: int = 120,
) -> Path:
    """A readable view of the database for the reports directory.

    The CSV is the database; this is the part a reader can skim — the counts,
    then the most recent papers that name a model, with the full table left to
    the CSV.
    """
    path = Path(path or config.REPORT_DIR / "04_paper_database.md")
    rows = included(store, overrides)
    summary = summarize(store, overrides)
    named = sorted(
        (r for r in rows if (r.get("model_name") or "").strip()),
        key=lambda r: (-(r.get("citations") or 0), -(r.get("year") or 0)),
    )[:named_only_limit]

    def _counts_table(title: str, tally: dict[str, int], header: str) -> list[str]:
        if not tally:
            return []
        out = [f"### {title}", "", f"| {header} | Papers |", "| --- | ---: |"]
        out += [f"| {_md_cell(k)} | {v} |" for k, v in tally.items()]
        return out + [""]

    lines = [
        "# Pediatric radiology AI: paper database",
        "",
        f"Generated {summary['generated_on']} from `data/processed/pedrad_paper_db.csv`.",
        "",
        f"{summary['n_included']} papers, {summary['n_named_models']} of which name a model or product, "
        f"screened from {summary['n_candidates_screened']} PubMed records matching the pediatric "
        f"radiology-AI query (title/abstract fielded) for {summary['years'][0]}-{summary['years'][1]} "
        f"({summary['n_excluded']} were screened out as adult-only, non-radiologic, or non-AI).",
        "",
        f"Candidates are limited to papers with at least {summary['min_citations']} citations in NIH "
        "iCite, which keeps the database to work the field has actually engaged with. That floor is "
        "also a recency filter: a paper published this year has had no time to accrue citations, so "
        "the last two years are under-represented here by construction and the trend figures, not "
        "this table, are the place to read growth.",
        "",
        "Each row is read from the paper's abstract under a fixed schema, so a field is blank when "
        "the abstract does not state it — most notably the release column, which abstracts are "
        "usually silent about. Read \"unclear\" as \"the paper does not say\", not as \"unavailable\". "
        "Hand corrections in `data/paper_db_overrides.json` take precedence over the extracted value "
        "and are flagged in the `overridden_fields` column of the CSV.",
        "",
        "## Counts",
        "",
    ]
    lines += _counts_table("Release status", summary["by_release_status"], "Status")
    lines += _counts_table("Modality", summary["by_modality"], "Modality")
    lines += _counts_table("Task", summary["by_task"], "Task")
    lines += _counts_table("Age group", summary["by_age_group"], "Age group")
    lines += _counts_table("Validation", summary["by_validation"], "Strongest validation claimed")
    lines += _counts_table("Papers per year", summary["by_year"], "Year")

    lines += [
        f"## Named models ({len(named)} most cited)",
        "",
        "| Model | Year | Cites | Modality | Population | Clinical problem | Release | Journal | Link |",
        "| --- | ---: | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for rec in named:
        lines.append(
            "| {model} | {year} | {cites} | {mod} | {pop} | {prob} | {rel} | {jrn} | [{lbl}]({url}) |".format(
                model=_md_cell(rec.get("model_name")),
                year=_md_cell(rec.get("year")),
                cites=_md_cell(rec.get("citations")),
                mod=_md_cell(rec.get("modality")),
                pop=_md_cell(rec.get("patient_population"), 70),
                prob=_md_cell(rec.get("clinical_problem"), 50),
                rel=_md_cell(rec.get("release_status")),
                jrn=_md_cell(rec.get("journal"), 32),
                lbl="doi" if rec.get("doi") else "pubmed",
                url=rec.get("url", ""),
            )
        )
    lines += [
        "",
        "The full table, including the model description, dataset size, validation and headline "
        "result for every paper, is `data/processed/pedrad_paper_db.csv`.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
