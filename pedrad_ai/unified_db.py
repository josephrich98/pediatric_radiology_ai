"""One table for every paper the project has touched.

``data/processed`` grew a paper record file per collection step: the screening
store (``pedrad_paper_db.json``), the Embase export (``embase_unique_rows.json``),
the per-venue tables (``conference_works.json``) and fourteen most-cited
leaderboards (``top_papers_*.json``). Each has its own columns and its own idea
of a key, so answering "do we have this paper, and in what capacity" meant
opening four files. This module folds all of them into a single flat CSV,
``data/processed/pediatric_radiology_ai.csv``, one row per paper, with a
``record_type`` column saying what the paper is to this project and a
``source_files`` column naming the files it came from.

Scope is papers: journal articles, conference papers and preprints. Repositories
(``github_repos.json``), FDA devices, newsletter stories and journal-level
impact are different entities and keep their own files.

Nothing here is a source of truth. The merged table is *generated* from the
files above on every run, so the store stays the store: ``corpus.py`` still owns
the PRISMA partition, ``paper_db.py`` still owns the corpus export, and this
module only reads what they wrote. Deleting the CSV costs nothing.

Deduplication is by PMID, then normalized DOI, then normalized title, in that
order, because the four sources key their records differently and the same paper
routinely appears in three of them — a MICCAI paper can be an arXiv preprint in
the store, a work in the venue table and a row on a leaderboard. When two source
rows are the same paper, the one from the higher-priority source supplies the
shared fields (the store outranks everything, because its fields were read from
the abstract rather than counted) and the other fills in what it left blank.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

from . import config, corpus, paper_db, utils

# Which source supplies a field when two rows are the same paper. The store is
# first because its rows carry the extraction; the leaderboards are last because
# they carry nothing the others do not, apart from citation counts.
PRIORITY = {"store": 0, "embase": 1, "conference_works": 2, "top_papers": 3}

COLUMNS = [
    # What this record is, and where it came from
    "record_id", "record_type", "publication_form", "scope",
    "source_files", "search_source", "in_corpus",
    # Bibliographic
    "title", "first_author", "year", "journal", "venue_label",
    "doi", "pmid", "arxiv_id", "url",
    "is_preprint", "publication_types", "language", "issn",
    # Screening
    "include", "exclusion_reason",
    # Extraction (populated for screened records only)
    "model_name", "model_family", "modality", "body_region", "patient_population",
    "age_groups", "clinical_problem", "task", "model_description",
    "release_status", "release_evidence", "code_url",
    "study_design", "dataset_size", "data_source", "validation", "headline_result",
    # Impact
    "citations", "citations_per_year", "rcr", "fwci", "impact", "impact_measure",
    "nih_percentile", "citation_percentile", "citations_source",
    # Extraction provenance
    "confidence", "overridden_fields", "extractor_model", "prompt_version", "extracted_on",
    # Venue-table and leaderboard extras
    "conference_venue", "pediatric_title", "top_lists",
]

# record_type, in the order the PRISMA flow produces them. The first four come
# from `corpus.partition`; the last three are records that were never screened,
# either because they are outside the review's scope (the venue tables and the
# general-radiology leaderboards) or because the search did not retrieve them.
RECORD_TYPES = (
    "corpus",                 # included primary study - the review corpus
    "non_primary",            # screened in, but a review / editorial / guideline
    "screened_out",           # read and excluded as not pediatric radiology AI
    "conference_proceeding",  # removed before screening by publication form
    "embase_not_retrieved",   # in the Embase export, never reached the store
    "venue_work",             # from a per-venue table, not part of the review
    "most_cited",             # from a most-cited leaderboard only
)

ARXIV_DOI = re.compile(r"^10\.48550/arxiv\.", re.I)
_PUNCT = re.compile(r"[^a-z0-9]+")

# Six of the eight venue tables are conferences; RSNA and SPR are the societies'
# journals standing in for meeting abstracts that are not indexed (see
# `config.CONFERENCE_WORKS`), so their works are journal articles.
JOURNAL_VENUES = {"RSNA", "SPR"}


# --------------------------------------------------------------------------- #
# Keys
# --------------------------------------------------------------------------- #
def norm_doi(doi: Any) -> str:
    """A DOI comparable across sources: bare, lowercase, no resolver prefix."""
    text = str(doi or "").strip().lower()
    text = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", text)
    return text.strip()


def norm_title(title: Any) -> str:
    """A title comparable across sources: lowercase, alphanumerics only.

    Short titles are rejected rather than matched: "Erratum" and "Editorial"
    would otherwise collapse dozens of unrelated records into one row.
    """
    text = _PUNCT.sub("", str(title or "").lower())
    return text if len(text) >= 20 else ""


def keys_of(row: dict[str, Any]) -> list[str]:
    """Every identifier a row can be matched on, most specific first."""
    out = []
    if row.get("pmid"):
        out.append(f"pmid:{row['pmid']}")
    doi = norm_doi(row.get("doi"))
    if doi:
        out.append(f"doi:{doi}")
    title = norm_title(row.get("title"))
    if title:
        out.append(f"title:{title}")
    return out


def publication_form(row: dict[str, Any]) -> str:
    """journal article / conference paper / preprint, from what the row says.

    An arXiv DOI settles "preprint" even when the source called the record a
    conference paper, because the arXiv version is what is actually indexed; the
    venue table's MICCAI rows are mostly author preprints of that kind.
    """
    if row.get("is_preprint") or ARXIV_DOI.match(norm_doi(row.get("doi"))):
        return "preprint"
    if row.get("record_type") == "conference_proceeding" or row.get("conference_venue"):
        return "conference paper"
    return "journal article"


# --------------------------------------------------------------------------- #
# Sources
# --------------------------------------------------------------------------- #
def _joined(value: Any) -> Any:
    return "; ".join(str(v) for v in value) if isinstance(value, list) else value


def from_store(store: dict[str, Any] | None = None,
               overrides: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """The screening store, one row per record, typed by the PRISMA partition.

    Read through ``paper_db.presented`` so hand corrections and the derived
    impact columns apply exactly as they do in the corpus CSV, and partitioned
    by ``corpus.partition`` so this table can never disagree with the manuscript
    about which records are the corpus.
    """
    store = paper_db.load() if store is None else store
    rows = paper_db.presented(store, overrides)
    part = corpus.partition(rows)
    typed: dict[int, str] = {}
    for name, bucket in (("conference_proceeding", part.conference),
                         ("screened_out", part.excluded),
                         ("non_primary", part.non_primary),
                         ("corpus", part.included)):
        for rec in bucket:
            typed[id(rec)] = name

    out = []
    for rec in rows:
        record_type = typed.get(id(rec), "screened_out")
        row = {col: _joined(rec.get(col)) for col in COLUMNS if col in rec}
        row.update(
            record_id=corpus.key(rec),
            record_type=record_type,
            scope="pediatric",
            source_files="pedrad_paper_db.json",
            search_source=rec.get("source") or "pubmed",
            in_corpus=record_type == "corpus",
            venue_label=rec.get("journal"),
            publication_types=_joined(corpus.publication_types(rec)),
        )
        row["publication_form"] = publication_form(row)
        out.append(row)
    return out


def from_embase(path: str | Path | None = None) -> list[dict[str, Any]]:
    """The Embase export. Rows the search already retrieved merge into the store
    row; the rest are the records only Embase has."""
    path = Path(path or config.PROCESSED_DIR / "embase_unique_rows.json")
    if not path.exists():
        return []
    out = []
    for rec in utils.load_json(path):
        pmid = str(rec.get("pmid") or rec.get("resolved_pmid") or "").strip()
        row = {
            "record_id": f"emb:{rec.get('pui')}" if rec.get("pui") else str(rec.get("id") or ""),
            "record_type": "embase_not_retrieved",
            "scope": "pediatric",
            "source_files": "embase_unique_rows.json",
            "search_source": "embase",
            "in_corpus": False,
            "title": rec.get("title") or rec.get("original_title"),
            "year": rec.get("year"),
            "journal": rec.get("journal"),
            "venue_label": rec.get("journal"),
            "doi": rec.get("doi"),
            "pmid": pmid,
            "is_preprint": bool(rec.get("is_preprint")),
            "publication_types": rec.get("embase_type"),
            "language": rec.get("language"),
            "issn": rec.get("issn"),
            "conference_venue": rec.get("conference_name") or "",
        }
        row["publication_form"] = publication_form(row)
        out.append(row)
    return out


def from_conference_works(path: str | Path | None = None) -> list[dict[str, Any]]:
    """The per-venue tables: radiology-AI works at the ML venues and in the
    society journals. Not part of the review corpus, so typed ``venue_work``.

    Only the works the collector kept are here. Each block stores its full count
    in ``n_works`` and ``by_year`` but caps ``works`` at the number the venue
    slide lists, so this contributes a few hundred rows against a few thousand
    counted works. The counts, not this table, are what the venue figures use.
    """
    path = Path(path or config.PROCESSED_DIR / "conference_works.json")
    if not path.exists():
        return []
    out = []
    for venue, block in utils.load_json(path).items():
        for work in block.get("works", []):
            row = {
                "record_id": "",
                "record_type": "venue_work",
                "scope": "pediatric" if work.get("pediatric") else "radiology_ai",
                "source_files": "conference_works.json",
                "search_source": "semantic_scholar",
                "in_corpus": False,
                "title": work.get("title"),
                "first_author": work.get("first_author"),
                "year": work.get("year"),
                "venue_label": work.get("venue_label") or block.get("full") or venue,
                "doi": work.get("doi"),
                "citations": work.get("citation_count"),
                "fwci": work.get("fwci"),
                "citation_percentile": work.get("citation_percentile"),
                "pediatric_title": bool(work.get("pediatric")),
                "conference_venue": "" if venue in JOURNAL_VENUES else venue,
            }
            if venue in JOURNAL_VENUES:
                row["journal"] = row["venue_label"]
            row["publication_form"] = publication_form(row)
            out.append(row)
    return out


def from_top_papers(directory: str | Path | None = None) -> list[dict[str, Any]]:
    """The most-cited leaderboards. Fourteen files with heavy overlap, so the
    lists a paper appears on are collected into one ``top_lists`` cell."""
    directory = Path(directory or config.PROCESSED_DIR)
    out = []
    for path in sorted(directory.glob("top_papers_*.json")):
        stem = path.stem[len("top_papers_"):]
        scope = "pediatric" if stem.startswith("pediatric_") else "radiology_ai"
        window = stem[len("pediatric_radiology_ai"):] if scope == "pediatric" else stem[len("radiology_ai"):]
        window = window.lstrip("_") or "all years"
        for work in utils.load_json(path):
            row = {
                "record_id": f"s2:{work['s2_id']}" if work.get("s2_id") else "",
                "record_type": "most_cited",
                "scope": scope,
                "source_files": path.name,
                "search_source": "semantic_scholar",
                "in_corpus": False,
                "title": work.get("title"),
                "first_author": work.get("first_author"),
                "year": work.get("year"),
                "venue_label": work.get("venue_label") or work.get("venue"),
                "journal": "" if work.get("is_preprint") else (work.get("venue") or ""),
                "doi": work.get("doi"),
                "pmid": str(work.get("pmid") or "").strip(),
                "arxiv_id": work.get("arxiv_id"),
                "is_preprint": bool(work.get("is_preprint")),
                "citations": work.get("citation_count"),
                "fwci": work.get("fwci"),
                "citation_percentile": work.get("citation_percentile"),
                "top_lists": f"{scope} {window}",
            }
            row["publication_form"] = publication_form(row)
            out.append(row)
    return out


# --------------------------------------------------------------------------- #
# Merge
# --------------------------------------------------------------------------- #
def _merge_into(target: dict[str, Any], incoming: dict[str, Any],
                target_rank: int, incoming_rank: int) -> int:
    """Fold ``incoming`` into ``target``; return the surviving priority rank.

    The higher-priority row keeps its values for every field it filled. The
    lower-priority row contributes only what the other left empty, plus the two
    accumulating columns — the source files a paper appears in, and the
    leaderboards it appears on — which are unions rather than overwrites.
    """
    first, second = ((target, incoming) if target_rank <= incoming_rank
                     else (incoming, target))
    kept = {col: (first.get(col) if first.get(col) not in (None, "", [])
                  else second.get(col)) for col in COLUMNS}
    # Two columns accumulate instead of being overwritten: which files hold this
    # paper, and which leaderboards it appears on.
    for col in ("source_files", "top_lists"):
        parts: list[str] = []
        for row in (first, second):
            for part in str(row.get(col) or "").split("; "):
                if part and part not in parts:
                    parts.append(part)
        kept[col] = "; ".join(parts)
    # `record_type` is a claim about the review, so it comes from the store when
    # the store has the record at all, whatever the other source called it.
    kept["record_type"] = first.get("record_type") or second.get("record_type")
    kept["in_corpus"] = kept["record_type"] == "corpus"
    target.clear()
    target.update(kept)
    return min(target_rank, incoming_rank)


def merge(sources: Iterable[tuple[str, list[dict[str, Any]]]]) -> list[dict[str, Any]]:
    """Dedupe rows across sources on PMID, then DOI, then normalized title.

    Store rows are exempt: they are appended one for one, never matched against
    each other. The store is already deduplicated on its own key, and its row
    count is the PRISMA denominator, so collapsing two of its records here — a
    preprint against its journal version, say, which share a title but not a
    DOI — would make this table disagree with ``review_stats.json`` about the
    size of the corpus. Records the store deliberately holds twice stay twice.
    """
    merged: list[dict[str, Any]] = []
    ranks: list[int] = []
    index: dict[str, int] = {}

    for name, rows in sources:
        rank = PRIORITY[name]
        for row in rows:
            hit = None if name == "store" else next(
                (index[k] for k in keys_of(row) if k in index), None)
            if hit is None:
                merged.append(dict(row))
                ranks.append(rank)
                hit = len(merged) - 1
            else:
                ranks[hit] = _merge_into(merged[hit], row, ranks[hit], rank)
            for key in keys_of(merged[hit]):
                index.setdefault(key, hit)

    for i, row in enumerate(merged):
        if not row.get("record_id"):
            row["record_id"] = f"row:{i:05d}"
        row["publication_form"] = publication_form(row)
    return merged


def build(store: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Every paper record the project holds, deduped, newest first."""
    store_rows = from_store(store)
    rows = merge([
        ("store", store_rows),
        ("embase", from_embase()),
        ("conference_works", from_conference_works()),
        ("top_papers", from_top_papers()),
    ])
    order = {name: i for i, name in enumerate(RECORD_TYPES)}
    return sorted(
        rows,
        key=lambda r: (order.get(r.get("record_type"), 99),
                       -(int(r["year"]) if str(r.get("year") or "").isdigit() else 0),
                       str(r.get("record_id"))),
    )


def write_csv(rows: list[dict[str, Any]] | None = None,
              path: str | Path | None = None) -> Path:
    """Write the merged table. Lists are joined with '; ' as elsewhere."""
    path = Path(path or config.UNIFIED_DB_CSV)
    rows = build() if rows is None else rows
    flat = [{col: _joined(row.get(col, "")) if row.get(col) is not None else ""
             for col in COLUMNS} for row in rows]
    if not flat:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(",".join(COLUMNS) + "\n", encoding="utf-8")
        return path
    return utils.save_csv(flat, path, columns=COLUMNS)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Counts by record type, publication form and source file, for the log."""
    def tally(key: str, split: bool = False) -> dict[str, int]:
        out: dict[str, int] = {}
        for row in rows:
            values = str(row.get(key) or "").split("; ") if split else [row.get(key) or ""]
            for value in values:
                if value:
                    out[value] = out.get(value, 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    return {
        "n_rows": len(rows),
        "by_record_type": tally("record_type"),
        "by_publication_form": tally("publication_form"),
        "by_scope": tally("scope"),
        "by_source_file": tally("source_files", split=True),
    }
