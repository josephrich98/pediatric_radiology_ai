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

from . import config, extract, icite, openalex, pubmed, utils

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
    "citations_per_year",
    "rcr",
    "fwci",
    "nih_percentile",
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
    "record_id",
    "source",
    "is_preprint",
    "confidence",
    "overridden_fields",
    "extractor_model",
    "prompt_version",
    "extracted_on",
]

# Fields a human may override in data/paper_db_overrides.json.
# Fields a human may override in data/paper_db_overrides.json. The identifiers
# and the bibliometric measures are excluded: they come from an external index
# and a hand edit there would misrepresent the source rather than correct it.
_NOT_OVERRIDABLE = {
    "pmid", "record_id", "source", "is_preprint", "citations", "citations_per_year",
    "rcr", "fwci", "nih_percentile", "overridden_fields", "extractor_model",
    "prompt_version", "extracted_on",
}
OVERRIDABLE = {c for c in COLUMNS if c not in _NOT_OVERRIDABLE} | {"include", "exclusion_reason"}


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
        records = {record_key(r): r for r in records if record_key(r)}
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
            "min_citations_per_year": config.PAPER_DB_MIN_CITATIONS_PER_YEAR,
            "min_rcr": config.PAPER_DB_MIN_RCR,
            "start_year": config.PAPER_DB_START_YEAR,
            "n_records": len(store["records"]),
            "n_included": sum(1 for r in store["records"].values() if r.get("include")),
            "records": sorted_records(store),
        },
        path,
    )


def record_key(record: dict[str, Any]) -> str:
    """The store key for a row or a candidate.

    PubMed records are keyed by PMID, which is what the overrides file and every
    earlier version of this store used. Preprints that PubMed does not index get
    an OpenAlex-derived key instead, so the two sources can live in one table
    without colliding.
    """
    return str(record.get("record_id") or record.get("pmid") or "")


def sorted_records(store: dict[str, Any]) -> list[dict[str, Any]]:
    """Records newest first, then by key — stable across runs."""
    return sorted(
        store["records"].values(),
        key=lambda r: (-(r.get("year") or 0), record_key(r)),
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
        override = overrides.get(record_key(rec))
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


def passes_impact_floor(
    metrics: dict[str, Any],
    min_citations: int,
    min_citations_per_year: float = 0.0,
    min_rcr: float = 0.0,
) -> bool:
    """Whether a candidate clears any one of the impact floors.

    The floors are combined with OR on purpose. A raw citation count is the
    right filter for settled literature and the wrong one for the current year,
    where nothing has had time to be cited; a rate or a field-normalized ratio
    lets recent work in on its own terms. A floor of 0 disables that clause.
    """
    if min_citations and (metrics.get("citations") or 0) >= min_citations:
        return True
    if min_citations_per_year and (metrics.get("citations_per_year") or 0) >= min_citations_per_year:
        return True
    if min_rcr and (metrics.get("rcr") or 0) >= min_rcr:
        return True
    return not (min_citations or min_citations_per_year or min_rcr)


def collect_candidates(
    start_year: int | None = None,
    end_year: int | None = None,
    min_citations: int | None = None,
    min_citations_per_year: float | None = None,
    min_rcr: float | None = None,
    include_preprints: bool | None = None,
    include_conference: bool | None = None,
    query: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Candidates that clear an impact floor, keyed by :func:`record_key`.

    Two sources. PubMed via :func:`candidate_pmids`, scored with NIH iCite
    (citations, citations per year, relative citation ratio). OpenAlex
    ``type:preprint`` for the same query, scored with its own citation count and
    field-weighted citation impact, because PubMed does not index arXiv and
    indexes medRxiv and bioRxiv only partially — so a count-only view of the
    current year misses where much of the methods work first appears.

    Preprints already represented in the PubMed set (same PMID, DOI or title)
    are dropped, so a paper is not counted twice once it is published.
    """
    min_citations = config.PAPER_DB_MIN_CITATIONS if min_citations is None else min_citations
    min_citations_per_year = (
        config.PAPER_DB_MIN_CITATIONS_PER_YEAR
        if min_citations_per_year is None
        else min_citations_per_year
    )
    min_rcr = config.PAPER_DB_MIN_RCR if min_rcr is None else min_rcr
    include_preprints = (
        config.PAPER_DB_INCLUDE_PREPRINTS if include_preprints is None else include_preprints
    )
    include_conference = (
        config.PAPER_DB_INCLUDE_CONFERENCE if include_conference is None else include_conference
    )
    start = start_year or config.PAPER_DB_START_YEAR
    end = end_year or config.END_YEAR

    out: dict[str, dict[str, Any]] = {}
    years = candidate_pmids(start, end, query)
    met = icite.metrics(list(years))
    for pmid, year in years.items():
        m = met.get(pmid, {})
        if passes_impact_floor(m, min_citations, min_citations_per_year, min_rcr):
            out[pmid] = {
                "record_id": pmid, "pmid": pmid, "source": "pubmed", "is_preprint": False,
                "year": year, "citations": m.get("citations", 0),
                "citations_per_year": m.get("citations_per_year"),
                "rcr": m.get("rcr"), "nih_percentile": m.get("nih_percentile"),
            }

    # Each extra source is tagged with where it came from, because a work's own
    # metadata does not always say: OpenAlex files a MICCAI paper as an article
    # in a book series, and a preprint stream result is a preprint whether or
    # not its record admits it.
    extra: list[dict[str, Any]] = []
    if include_preprints:
        for work in preprint_candidates(start, end, query):
            extra.append({**work, "_origin": "preprint"})
    if include_conference:
        floor = min(x for x in (min_citations, int(min_citations_per_year)) if x > 0) \
            if (min_citations or min_citations_per_year) else 0
        for work in conference_candidates(start, end, min_cited=floor):
            extra.append({**work, "_origin": "conference"})

    if extra:
        seen_doi = {(r.get("doi") or "").lower() for r in out.values() if r.get("doi")}
        seen_title = {_norm_title(r.get("title")) for r in out.values() if r.get("title")}
        for work in extra:
            pmid = work.get("pmid")
            doi = (work.get("doi") or "").lower()
            title = _norm_title(work.get("title"))
            if (pmid and pmid in out) or (doi and doi in seen_doi) or (title and title in seen_title):
                continue
            m = {
                "citations": work.get("citation_count") or 0,
                "citations_per_year": _per_year(work),
                "rcr": None,
                "fwci": work.get("fwci"),
            }
            # A preprint has no RCR, so the RCR clause cannot admit it; the
            # count and rate clauses still apply.
            if not passes_impact_floor(m, min_citations, min_citations_per_year, 0.0):
                continue
            rid = "oa:" + str(work.get("openalex_id") or "").rsplit("/", 1)[-1]
            if not rid or rid == "oa:":
                continue
            out[rid] = {
                "record_id": rid, "pmid": pmid or "", "source": "openalex",
                "is_preprint": bool(work.get("is_preprint")) or work.get("_origin") == "preprint",
                "venue_kind": work.get("venue_kind"),
                "origin": work.get("_origin"),
                "year": work.get("year"), "citations": m["citations"],
                "citations_per_year": m["citations_per_year"], "rcr": None,
                "nih_percentile": None, "fwci": work.get("fwci"), "_work": work,
            }
            if doi:
                seen_doi.add(doi)
            if title:
                seen_title.add(title)
    return out


def conference_candidates(start: int, end: int, min_cited: int = 0) -> list[dict[str, Any]]:
    """Conference proceedings matching the database query.

    OpenAlex files a proceedings paper by *work* type — ``conference-paper`` —
    and not by venue: MICCAI, IPMI and MIDL live inside the Lecture Notes in
    Computer Science book series, NeurIPS and CVPR under their own sources, and
    ``primary_location.source.type:conference`` catches almost none of them
    while sweeping in a long tail of unrelated local proceedings. So the type is
    the filter, with a second pass over LNCS for volumes typed some other way.

    ``min_cited`` is pushed into the query rather than applied afterwards: the
    unfiltered type is a few thousand works a year, and every one of them is a
    page of a cursor walk. It is a floor on the raw count, which is a superset
    of what :func:`passes_impact_floor` admits, so nothing that would survive
    the floor is dropped here.

    Most conference records carry no abstract in OpenAlex. Those are still
    returned — the caller reports a record it cannot read rather than guessing
    at one.
    """
    extra = [f"cited_by_count:>{min_cited - 1}"] if min_cited > 0 else []
    works: list[dict[str, Any]] = []
    seen: set[str] = set()
    for label, filters, types in (
        ("conference papers", extra, "conference-paper"),
        ("Lecture Notes in Computer Science",
         [f"primary_location.source.id:{config.PAPER_DB_LNCS_SOURCE}", *extra],
         "article|book-chapter|conference-paper"),
    ):
        try:
            found = openalex.search_all(
                config.PAPER_DB_CONFERENCE_QUERY, min_year=start, max_year=end,
                types=types, extra_filters=filters,
                max_results=config.PAPER_DB_CONFERENCE_CAP, budget_s=240.0,
            )
        except Exception as exc:
            print(f"    [warn] conference search failed for {label} ({exc})")
            continue
        fresh = [w for w in found if (w.get("openalex_id") or "") not in seen]
        seen.update(w.get("openalex_id") or "" for w in found)
        print(f"    {label}: {len(found)} works ({len(fresh)} new)")
        works.extend(fresh)
    return works


def preprint_candidates(start: int, end: int, query: str | None = None) -> list[dict[str, Any]]:
    """Preprints matching the database query, one OpenAlex pass per year."""
    translated = openalex.translate_pubmed_query(query or config.PAPER_DB_QUERY)
    works: list[dict[str, Any]] = []
    for year in range(start, end + 1):
        try:
            works.extend(
                openalex.search_all(
                    translated, min_year=year, max_year=year,
                    types=openalex.PREPRINT_TYPES,
                    max_results=config.PAPER_DB_PREPRINT_CAP,
                )
            )
        except Exception as exc:
            print(f"    [warn] preprint search failed for {year} ({exc})")
    return works


def _per_year(work: dict[str, Any]) -> float | None:
    """Citations per year since publication, for an OpenAlex work."""
    year = work.get("year")
    if not year:
        return None
    elapsed = max(1.0, config.END_YEAR - int(year) + 1)
    return round((work.get("citation_count") or 0) / elapsed, 2)


def _norm_title(title: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (title or "").lower())


# Preprint servers whose records PubMed does index, through the NIH preprint
# pilot. A record reaching us via PubMed is still a preprint, and the release
# column should say so rather than calling it a journal article.
_PREPRINT_SERVERS = re.compile(r"\b(medrxiv|biorxiv|arxiv|research square|ssrn)\b", re.I)


def looks_like_preprint(record: dict[str, Any]) -> bool:
    """Whether a record is a preprint, from any of the signals available."""
    if record.get("is_preprint"):
        return True
    if any("preprint" in str(t).lower() for t in record.get("publication_types") or []):
        return True
    if (record.get("doi") or "").lower().startswith("10.1101/"):
        return True
    return bool(_PREPRINT_SERVERS.search(str(record.get("journal") or "")))


# Kept for callers written against the earlier single-floor signature.
def candidates_with_citations(
    start_year: int | None = None,
    end_year: int | None = None,
    min_citations: int | None = None,
    query: str | None = None,
) -> dict[str, dict[str, Any]]:
    """PubMed-only candidates above a raw citation floor."""
    return collect_candidates(
        start_year, end_year, min_citations,
        min_citations_per_year=0.0, min_rcr=0.0,
        include_preprints=False, include_conference=False, query=query,
    )


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


def fetch_articles(candidates: dict[str, dict[str, Any]] | Iterable[str]) -> list[dict[str, Any]]:
    """Records ready for extraction, from whichever source each came from.

    Accepts the candidate mapping from :func:`collect_candidates`, or a bare
    iterable of PMIDs for the ``--pmid`` spot-check path. PubMed records are
    fetched with EFetch; preprints are already in hand from the OpenAlex pass
    and only need reshaping into the same field names, so that
    :mod:`pedrad_ai.extract` sees one kind of input.
    """
    if not isinstance(candidates, dict):
        candidates = {str(p): {"record_id": str(p), "pmid": str(p), "source": "pubmed"}
                      for p in candidates}
    if not candidates:
        return []

    pubmed_ids = [c["pmid"] for c in candidates.values()
                  if c.get("source") != "openalex" and c.get("pmid")]
    fetched = (
        {a["pmid"]: a for a in pubmed.article_details(pubmed_ids, with_abstract=True)}
        if pubmed_ids
        else {}
    )

    out: list[dict[str, Any]] = []
    for rid, cand in candidates.items():
        if cand.get("source") == "openalex":
            work = cand.get("_work") or {}
            out.append(
                {
                    "record_id": rid,
                    "pmid": cand.get("pmid") or "",
                    "title": work.get("title") or "",
                    "journal": work.get("venue_label") or work.get("venue")
                    or ("conference proceedings" if cand.get("origin") == "conference" else "preprint"),
                    "year": work.get("year"),
                    "doi": work.get("doi"),
                    "authors": work.get("authors") or [],
                    "publication_types": [
                        "Conference Proceedings" if cand.get("origin") == "conference" else "Preprint"
                    ],
                    "mesh_terms": [],
                    "abstract": work.get("abstract") or "",
                }
            )
            continue
        article = fetched.get(cand.get("pmid") or rid)
        if article is not None:
            out.append({**article, "record_id": rid})
    return out


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
    article: dict[str, Any],
    extraction: dict[str, Any],
    citations: int | None = None,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge a source record and its extraction into one stored row.

    ``metrics`` is the candidate entry from :func:`collect_candidates`, carrying
    the bibliometrics and which source the record came from. Hand overrides are
    *not* applied here — see :func:`presented`.
    """
    metrics = metrics or {}
    doi = (article.get("doi") or "").strip()
    row: dict[str, Any] = {
        "pmid": article.get("pmid") or "",
        "record_id": article.get("record_id") or article.get("pmid") or "",
        "source": metrics.get("source", "pubmed"),
        "is_preprint": bool(metrics.get("is_preprint")) or looks_like_preprint(article),
        "title": article.get("title", ""),
        "journal": article.get("journal", ""),
        "year": article.get("year"),
        "doi": doi,
        "url": f"https://doi.org/{doi}" if doi else f"https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/",
        "first_author": (article.get("authors") or [""])[0],
        "citations": metrics.get("citations") if citations is None else citations,
        "citations_per_year": metrics.get("citations_per_year"),
        "rcr": metrics.get("rcr"),
        "fwci": metrics.get("fwci"),
        "nih_percentile": metrics.get("nih_percentile"),
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
    if row.get("is_preprint") and row.get("include") and row.get("release_status") == "unclear":
        # A preprint is by definition not a released product; saying "unclear"
        # about its release status would read as if the question were open.
        row["release_status"] = "unreleased"
        row["release_evidence"] = (row.get("release_evidence") or "").strip() or "preprint, not yet published"
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
# Metric refresh
# --------------------------------------------------------------------------- #
def refresh_metrics(store: dict[str, Any], with_fwci: bool = False) -> int:
    """Re-fetch the bibliometrics for every stored row, in place.

    Citations, citations per year and RCR all move over time, and a row read a
    year ago carries a stale snapshot. This updates them without re-reading a
    single abstract, so it is cheap and involves no model calls at all — the
    separation that makes the expensive half of the pipeline worth caching.
    Returns the number of rows updated.

    ``with_fwci`` adds OpenAlex's field-weighted citation impact by DOI. It is
    off by default because OpenAlex throttles aggressively and RCR already
    covers every PubMed row; preprints carry their FWCI from the search that
    found them, so nothing is lost by leaving it off.
    """
    records = store["records"]
    pmids = [r["pmid"] for r in records.values() if r.get("pmid")]
    met = icite.metrics(pmids) if pmids else {}

    by_doi: dict[str, dict[str, Any]] = {}
    if with_fwci:
        dois = [(r.get("doi") or "").strip() for r in records.values() if (r.get("doi") or "").strip()]
        try:
            by_doi = openalex.works_by_dois(dois)
        except Exception as exc:
            print(f"    [warn] OpenAlex impact lookup failed ({exc}); keeping stored values")

    updated = 0
    for rec in records.values():
        changed = False
        m = met.get(str(rec.get("pmid") or ""))
        if m:
            for key in ("citations", "citations_per_year", "rcr", "nih_percentile"):
                if rec.get(key) != m.get(key):
                    rec[key] = m.get(key)
                    changed = True
        work = by_doi.get((rec.get("doi") or "").strip().lower())
        if work and rec.get("fwci") != work.get("fwci"):
            rec["fwci"] = work.get("fwci")
            changed = True
        rec.setdefault("record_id", record_key(rec))
        rec.setdefault("source", "pubmed")
        was = rec.get("is_preprint")
        rec["is_preprint"] = looks_like_preprint(rec)
        if rec["is_preprint"] and rec.get("release_status") == "unclear":
            rec["release_status"] = "unreleased"
            rec["release_evidence"] = rec.get("release_evidence") or "preprint, not yet published"
        changed = changed or (was != rec["is_preprint"])
        if changed:
            rec["citations_as_of"] = dt.date.today().isoformat()
            updated += 1
    return updated


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
        "min_citations_per_year": config.PAPER_DB_MIN_CITATIONS_PER_YEAR,
        "min_rcr": config.PAPER_DB_MIN_RCR,
        "median_citations": (
            sorted(r.get("citations") or 0 for r in rows)[len(rows) // 2] if rows else 0
        ),
        "n_candidates_screened": len(store["records"]),
        "n_included": len(rows),
        "n_excluded": len(store["records"]) - len(rows),
        "n_named_models": len(named),
        "n_with_code_url": sum(1 for r in rows if (r.get("code_url") or "").strip()),
        "n_preprints": sum(1 for r in rows if r.get("is_preprint")),
        "n_with_rcr": sum(1 for r in rows if r.get("rcr") is not None),
        "median_rcr": (
            sorted(r["rcr"] for r in rows if r.get("rcr") is not None)[
                len([r for r in rows if r.get("rcr") is not None]) // 2
            ]
            if any(r.get("rcr") is not None for r in rows)
            else None
        ),
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


def _floor_sentence(summary: dict[str, Any]) -> str:
    """Describe the impact floors actually in force, in one sentence."""
    clauses = []
    if summary.get("min_citations"):
        clauses.append(f"at least {summary['min_citations']} citations in NIH iCite")
    if summary.get("min_citations_per_year"):
        clauses.append(f"at least {summary['min_citations_per_year']:g} citations per year")
    if summary.get("min_rcr"):
        clauses.append(f"a relative citation ratio of at least {summary['min_rcr']:g}")
    if not clauses:
        return "Every paper the query returns is a candidate; no impact floor is applied."
    return (
        "Candidates are papers meeting " + " or ".join(clauses) + ", which keeps the database to "
        "work the field has actually engaged with. A raw citation floor is also a recency filter — "
        "a paper published this year has had no time to accrue citations — which is why the rate and "
        "ratio clauses exist; even so the current year is thin by construction, and the trend "
        "figures, not this table, are the place to read growth."
    )


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
    recent = sorted(
        (r for r in rows if (r.get("year") or 0) >= config.END_YEAR - 2),
        key=lambda r: (-(r.get("citations_per_year") or 0), -(r.get("citations") or 0)),
    )[:40]

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
        _floor_sentence(summary),
        "",
        "Impact is reported four ways because no one measure works across the whole range. "
        "`citations` is the raw count and can only be compared within a year. `citations/yr` is that "
        "count divided by years since publication. `RCR` is iCite's relative citation ratio, where "
        "1.0 is the median NIH-funded paper of the same field and year, and is the column to use "
        "when comparing a 2016 paper with a 2024 one; it is undefined until a paper is about two "
        "years old. `fwci` is OpenAlex's field-weighted citation impact, on the same 1.0-is-average "
        "scale, and covers some of what RCR does not.",
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
        "| Model | Year | Cites | /yr | RCR | Modality | Population | Clinical problem | Release | Journal | Link |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for rec in named:
        lines.append(
            "| {model} | {year} | {cites} | {rate} | {rcr} | {mod} | {pop} | {prob} | {rel} | {jrn} | [{lbl}]({url}) |".format(
                model=_md_cell(rec.get("model_name")),
                year=_md_cell(rec.get("year")),
                cites=_md_cell(rec.get("citations")),
                rate=_md_cell(rec.get("citations_per_year")),
                rcr=_md_cell(rec.get("rcr") if rec.get("rcr") is not None else rec.get("fwci")),
                mod=_md_cell(rec.get("modality")),
                pop=_md_cell(rec.get("patient_population"), 70),
                prob=_md_cell(rec.get("clinical_problem"), 50),
                rel=_md_cell(rec.get("release_status")),
                jrn=_md_cell(rec.get("journal"), 32),
                lbl="doi" if rec.get("doi") else "pubmed",
                url=rec.get("url", ""),
            )
        )
    if recent:
        lines += [
            "",
            f"## Most-cited-per-year work from {config.END_YEAR - 2} onward ({len(recent)})",
            "",
            "Ranked by citations per year rather than raw count, because a paper from this year "
            "has had no time to accumulate one. `RCR` is iCite's relative citation ratio (1.0 is "
            "the median NIH-funded paper of the same field and year) and falls back to OpenAlex's "
            "field-weighted citation impact where iCite has not computed it, which is most of the "
            "last two years.",
            "",
            "| Title | Year | Cites | /yr | RCR/FWCI | Type | Clinical problem | Link |",
            "| --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
        ]
        for rec in recent:
            lines.append(
                "| {title} | {year} | {cites} | {rate} | {norm} | {kind} | {prob} | [{lbl}]({url}) |".format(
                    title=_md_cell(rec.get("model_name") or rec.get("title"), 64),
                    year=_md_cell(rec.get("year")),
                    cites=_md_cell(rec.get("citations")),
                    rate=_md_cell(rec.get("citations_per_year")),
                    norm=_md_cell(rec.get("rcr") if rec.get("rcr") is not None else rec.get("fwci")),
                    kind="preprint" if rec.get("is_preprint") else "journal",
                    prob=_md_cell(rec.get("clinical_problem"), 46),
                    lbl="doi" if rec.get("doi") else "link",
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
