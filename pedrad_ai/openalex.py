"""OpenAlex collector: citation counts, most-cited papers, preprints, key-free.

OpenAlex (https://openalex.org) is an open index of scholarly works with
citation counts (``cited_by_count``), a field- and year-normalized citation
impact (``fwci``), generous rate limits, and no API key. It replaces Semantic
Scholar here, whose key-less endpoint is too heavily rate-limited to use
reliably. We use it for four things:

* the "biggest players" tables: works matching a topic, ranked by citations
  (per era and per year), with the FWCI shown next to the raw count so that a
  2025 paper can be compared with a 2023 one;
* preprints: PubMed does not index arXiv, so the count-based views (growth,
  modality x task, clinical problems) add an OpenAlex ``type:preprint`` layer
  built from the same PubMed queries, translated by
  :func:`translate_pubmed_query`;
* venue tables: the most-cited AI works in a journal set (RSNA journals,
  Pediatric Radiology) via ``primary_location.source.id``;
* DOI / title lookups for the papers behind trade-press stories.

API docs: https://docs.openalex.org/
Including a ``mailto`` puts requests in the faster, more reliable pool.
"""

from __future__ import annotations

import re
from typing import Any

from . import config, utils

WORKS = "https://api.openalex.org/works"

# Works of these types count as "papers" everywhere in the deck. OpenAlex
# merges a preprint with its published version when it can match them, so
# ``type:preprint`` is the set that never made it (yet) to a journal.
PAPER_TYPES = "article|preprint"
PREPRINT_TYPES = "preprint"

SELECT = (
    "id,doi,title,publication_year,type,cited_by_count,fwci,"
    "citation_normalized_percentile,primary_location,authorships"
)
# The paper database also needs the abstract and the publication date, which
# the leaderboard views do not.
SELECT_FULL = SELECT + ",abstract_inverted_index,publication_date,ids"


def _mailto() -> dict[str, str]:
    return {"mailto": config.CONTACT_EMAIL}


# OpenAlex allows 10 requests/s; one process at ~3/s with a patient retry
# schedule stays clear of 429s. Two collectors hitting it at once do not, and
# a swallowed 429 would silently become a zero count, so the count helpers
# raise after the retries and the collector script fails loudly instead.
_PAUSE = 0.35
_RETRIES = 8


def _get(url: str, params: dict[str, Any]) -> Any:
    """GET with a 429-aware schedule: OpenAlex also throttles per minute, so a
    rate-limit reply is followed by a long pause (10 s, 20 s, ...) rather than
    the short generic backoff in :mod:`utils`."""
    import time
    import urllib.error

    last: Exception | None = None
    for attempt in range(_RETRIES):
        try:
            return utils.http_get_json(url, params, pause=_PAUSE, max_retries=1)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code != 429 and not (500 <= exc.code < 600):
                raise
            time.sleep(10.0 * (attempt + 1))
        except Exception as exc:  # network blips
            last = exc
            time.sleep(5.0 * (attempt + 1))
    assert last is not None
    raise last


# --------------------------------------------------------------------------- #
# PubMed -> OpenAlex query translation
# --------------------------------------------------------------------------- #
# OpenAlex ``title_and_abstract.search`` accepts AND / OR / NOT, parentheses
# and quoted phrases, but no field tags, no MeSH and no wildcards (it stems
# instead). The mapping below expands the truncations whose Porter stem does
# not match the stem of the full word (``tomograph*`` vs ``tomography``);
# every other ``word*`` is simply un-starred, because the stemmer maps the
# stem and its inflections to the same token.
_STEM_MAP: dict[str, str] = {
    "radiograph*": "(radiograph OR radiographs OR radiographic OR radiography)",
    "tomograph*": "(tomography OR tomographic)",
    "ultrasonograph*": "(ultrasonography OR ultrasonographic)",
    "sonograph*": "(sonography OR sonographic)",
    "echocardiograph*": "(echocardiography OR echocardiographic)",
    "mammograph*": "(mammography OR mammographic OR mammogram OR mammograms)",
    "mammogra*": "(mammography OR mammographic OR mammogram OR mammograms)",
    "elastograph*": "(elastography OR elastographic)",
    "scintigraph*": "(scintigraphy OR scintigraphic)",
    "child*": "(child OR children OR childhood)",
    "adolescen*": "(adolescent OR adolescents OR adolescence)",
    "neonat*": "(neonatal OR neonate OR neonates OR neonatology)",
    "pediatric*": "(pediatric OR pediatrics)",
    "paediatric*": "(paediatric OR paediatrics)",
    "infant*": "(infant OR infants OR infancy)",
    "retina*": "(retina OR retinal)",
    "dermoscop*": "(dermoscopy OR dermoscopic)",
    "endoscop*": "(endoscopy OR endoscopic)",
    "colonoscop*": "(colonoscopy OR colonoscopic)",
    "microscop*": "(microscopy OR microscopic)",
    "histopatholog*": "(histopathology OR histopathological OR histopathologic)",
    "radiomic*": "(radiomics OR radiomic)",
    "volumetr*": "(volumetric OR volumetry)",
    "prognos*": "(prognosis OR prognostic)",
    "denois*": "(denoising OR denoise)",
    "accelerat*": "(accelerated OR acceleration)",
    "pretrain*": "(pretrained OR pretraining)",
    "fracture*": "(fracture OR fractures)",
    "protocol*": "(protocol OR protocols OR protocoling)",
    "measurement*": "(measurement OR measurements)",
    "reconstruct*": "(reconstruction OR reconstructed)",
    "imput*": "(imputation OR imputed)",
    "delineat*": "(delineation OR delineate)",
    "contour*": "(contour OR contouring OR contours)",
}
_MESH_MAP: dict[str, str] = {
    "tomography, x-ray computed": '"computed tomography"',
    "tomography, emission-computed": '"emission tomography"',
    "ultrasonography": "ultrasonography",
}


def translate_pubmed_query(q: str) -> str:
    """Rewrite a PubMed boolean query for ``title_and_abstract.search``.

    Field tags are dropped, MeSH headings become their plain phrase, and
    truncations are expanded (see ``_STEM_MAP``). Commas are removed because
    they separate filters in the OpenAlex URL syntax. The result is an
    approximation: it keeps the boolean structure and every literal term, but
    loses MeSH expansion, so preprint counts are indicative, not exact.
    """

    def _mesh(m: re.Match[str]) -> str:
        phrase = m.group(1).lower()
        return _MESH_MAP.get(phrase, f'"{phrase}"')

    s = re.sub(r'"([^"]+)"\[MeSH Terms\]', _mesh, q)
    s = re.sub(r"\[(tiab|ti|ta|pdat|mesh terms)\]", "", s, flags=re.I)
    for star, expansion in _STEM_MAP.items():
        s = re.sub(r"(?<![\w\"])" + re.escape(star) + r"(?![\w])", expansion, s, flags=re.I)
    s = re.sub(r"(\w+)\*", r"\1", s)  # any other truncation: bare stem
    s = s.replace(",", " ").replace("|", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


# --------------------------------------------------------------------------- #
# Counting (preprint layer)
# --------------------------------------------------------------------------- #
def count(query: str, start: int | None = None, end: int | None = None, types: str = PREPRINT_TYPES) -> int:
    """Number of works of ``types`` matching an OpenAlex search string."""
    filters = [f"title_and_abstract.search:{query}", f"type:{types}"]
    if start:
        filters.append(f"from_publication_date:{start}-01-01")
    if end:
        filters.append(f"to_publication_date:{end}-12-31")
    params = {"filter": ",".join(filters), "per_page": 1, **_mailto()}
    return int(_get(WORKS, params)["meta"]["count"])


def yearly_counts(query: str, types: str = PAPER_TYPES) -> dict[int, int]:
    """Publication counts per year for ``query`` (OpenAlex ``group_by``)."""
    # group_by results are paged by per_page too: per_page=1 would return only
    # the single largest year.
    params = {
        "filter": f"title_and_abstract.search:{query},type:{types}",
        "group_by": "publication_year",
        "per_page": 200,
        **_mailto(),
    }
    data = _get(WORKS, params)
    out: dict[int, int] = {}
    for g in data.get("group_by", []):
        key = g.get("key")
        if key and str(key).isdigit():
            yr = int(key)
            if config.START_YEAR <= yr <= config.END_YEAR:
                out[yr] = g.get("count", 0)
    return dict(sorted(out.items()))


def crosstab(
    base_query: str,
    rows: dict[str, str],
    cols: dict[str, str],
    start: int | None = None,
    end: int | None = None,
    types: str = PREPRINT_TYPES,
) -> dict[str, Any]:
    """Preprint counterpart of :func:`pubmed.crosstab` (same output shape).

    Every PubMed term group is translated with :func:`translate_pubmed_query`.
    """
    start = start or config.START_YEAR
    end = end or config.END_YEAR
    base = translate_pubmed_query(base_query)
    rq = {r: translate_pubmed_query(q) for r, q in rows.items()}
    cq = {c: translate_pubmed_query(q) for c, q in cols.items()}
    total = count(base, start, end, types)
    row_tot = {r: count(f"({base}) AND {q}", start, end, types) for r, q in rq.items()}
    col_tot = {c: count(f"({base}) AND {q}", start, end, types) for c, q in cq.items()}
    cells = {r: {c: count(f"({base}) AND {rq[r]} AND {cq[c]}", start, end, types) for c in cq} for r in rq}
    return {"years": [start, end], "total": total, "row_totals": row_tot, "col_totals": col_tot, "cells": cells}


def problem_counts(
    base_query: str,
    problems: dict[str, str],
    eras: list[tuple[str, int, int]] | None = None,
    types: str = PREPRINT_TYPES,
) -> dict[str, Any]:
    """Preprint counterpart of :func:`pubmed.problem_counts` (same shape)."""
    eras = eras or config.ERAS
    base = translate_pubmed_query(base_query)
    out: dict[str, Any] = {"eras": [{"label": lab, "start": a, "end": b} for lab, a, b in eras], "totals": {}, "counts": {}}
    for lab, a, b in eras:
        out["totals"][lab] = count(base, a, b, types)
    for name, q in problems.items():
        tq = translate_pubmed_query(q)
        out["counts"][name] = {lab: count(f"({base}) AND {tq}", a, b, types) for lab, a, b in eras}
    return out


# --------------------------------------------------------------------------- #
# Most-cited works
# --------------------------------------------------------------------------- #
def top_cited(
    query: str,
    per_page: int = 50,
    min_year: int | None = None,
    max_year: int | None = None,
    types: str = PAPER_TYPES,
    source_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return works matching ``query`` (title/abstract search), ranked by citations.

    ``query`` is a plain phrase (every word required; OpenAlex treats spaces as
    AND) or a boolean expression. ``types`` defaults to journal articles plus
    preprints. ``source_ids`` restricts to a venue set (OpenAlex source ids).
    Returns [] on failure so the pipeline keeps going.
    """
    filters = [f"title_and_abstract.search:{query}", f"type:{types}"]
    if min_year:
        filters.append(f"from_publication_date:{min_year}-01-01")
    if max_year:
        filters.append(f"to_publication_date:{max_year}-12-31")
    if source_ids:
        filters.append("primary_location.source.id:" + "|".join(s.rsplit("/", 1)[-1] for s in source_ids))
    params = {
        "filter": ",".join(filters),
        "sort": "cited_by_count:desc",
        "per_page": min(per_page, 200),
        "select": SELECT,
        **_mailto(),
    }
    try:
        data = _get(WORKS, params)
    except Exception as exc:
        print(f"    [warn] OpenAlex search failed ({exc}): {query[:60]!r}")
        return []
    return [_clean_work(w) for w in data.get("results", [])]


def top_cited_union(
    queries: list[str],
    per_query: int = 80,
    min_year: int | None = None,
    max_year: int | None = None,
    types: str = PAPER_TYPES,
) -> list[dict[str, Any]]:
    """Run several searches, union the results, dedupe, and rank by citations.

    A single query like ``radiology deep learning`` misses landmark papers whose
    title/abstract never use the literal word "radiology" (e.g. TotalSegmentator,
    whose title is only about CT segmentation). Running modality- and
    task-specific queries and unioning them recovers those papers. Deduped by
    OpenAlex work id.
    """
    by_id: dict[str, dict[str, Any]] = {}
    for q in queries:
        for paper in top_cited(q, per_page=per_query, min_year=min_year, max_year=max_year, types=types):
            wid = paper.get("openalex_id")
            if wid and wid not in by_id:
                by_id[wid] = paper
    out = list(by_id.values())
    out.sort(key=lambda r: r.get("citation_count", 0), reverse=True)
    return out


def abstract_text(work: dict[str, Any]) -> str:
    """Reconstruct an abstract from OpenAlex's inverted index.

    OpenAlex stores abstracts as ``{token: [positions]}`` for licensing reasons;
    inverting that back gives the running text. Returns "" when the work has no
    abstract, which is common for older preprints.
    """
    index = work.get("abstract_inverted_index")
    if not isinstance(index, dict) or not index:
        return ""
    positions: list[tuple[int, str]] = []
    for token, spots in index.items():
        for spot in spots or []:
            positions.append((spot, token))
    if not positions:
        return ""
    positions.sort()
    return " ".join(token for _, token in positions)


def search_all(
    query: str,
    min_year: int | None = None,
    max_year: int | None = None,
    types: str = PAPER_TYPES,
    max_results: int = 2000,
    budget_s: float = 240.0,
    extra_filters: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Every work matching ``query``, paged with a cursor, with abstracts.

    Used to harvest candidates for the paper database rather than to rank a
    leaderboard, so it pages rather than taking a top slice, and it asks for the
    fields an extraction needs.

    ``extra_filters`` are appended verbatim to the OpenAlex filter list, which
    is how the caller restricts to conference proceedings. ``budget_s`` is a
    wall-clock ceiling: OpenAlex throttles unpredictably and this is one
    collector among many, so when the budget runs out it returns what it has
    and says so rather than stalling the pipeline behind it.
    """
    import time as _time

    deadline = _time.monotonic() + budget_s
    filters = [f"title_and_abstract.search:{query}", f"type:{types}"]
    if min_year:
        filters.append(f"from_publication_date:{min_year}-01-01")
    if max_year:
        filters.append(f"to_publication_date:{max_year}-12-31")
    filters.extend(extra_filters or [])
    out: list[dict[str, Any]] = []
    cursor = "*"
    while cursor and len(out) < max_results:
        if _time.monotonic() > deadline:
            print(f"    [warn] OpenAlex budget spent; keeping {len(out)} works for this window")
            break
        params = {
            "filter": ",".join(filters),
            "per_page": 200,
            "cursor": cursor,
            "select": SELECT_FULL,
            **_mailto(),
        }
        try:
            data = utils.http_get_json(WORKS, params, pause=_PAUSE, max_retries=2)
        except Exception as exc:
            print(f"    [warn] OpenAlex page failed ({exc}); keeping {len(out)} works")
            break
        results = data.get("results") or []
        for w in results:
            out.append(_full_work(w))
        cursor = (data.get("meta") or {}).get("next_cursor")
        if not results:
            break
    return out[:max_results]


def _full_work(w: dict[str, Any]) -> dict[str, Any]:
    """:func:`_clean_work` plus the abstract, date and PubMed id."""
    work = _clean_work(w)
    work["abstract"] = abstract_text(w)
    work["publication_date"] = w.get("publication_date")
    work["pmid"] = _pmid_of(w)
    return work


def works_by_dois(dois: list[str], batch: int = 50) -> dict[str, dict[str, Any]]:
    """DOI (lowercased) -> work, fetched in batches.

    Used to attach field-weighted citation impact to records that came from
    PubMed, without one request per paper.
    """
    out: dict[str, dict[str, Any]] = {}
    clean = [d.strip().lower() for d in dois if d and d.strip()]
    for i in range(0, len(clean), batch):
        chunk = clean[i : i + batch]
        params = {
            "filter": "doi:" + "|".join(chunk),
            "per_page": len(chunk),
            "select": SELECT,
            **_mailto(),
        }
        try:
            data = _get(WORKS, params)
        except Exception:
            continue
        for w in data.get("results") or []:
            work = _clean_work(w)
            if work.get("doi"):
                out[work["doi"].lower()] = work
    return out


def _pmid_of(work: dict[str, Any]) -> str | None:
    """PubMed id from OpenAlex's ``ids`` block, when the work has one."""
    pm = (work.get("ids") or {}).get("pmid") or ""
    tail = str(pm).rstrip("/").rsplit("/", 1)[-1]
    return tail if tail.isdigit() else None


def work_by_doi(doi: str) -> dict[str, Any] | None:
    """One work by DOI (``None`` when unknown)."""
    doi = (doi or "").strip().lower().replace("https://doi.org/", "")
    if not doi:
        return None
    try:
        data = utils.http_get_json(f"{WORKS}/https://doi.org/{doi}", {"select": SELECT, **_mailto()}, pause=_PAUSE, max_retries=4)
    except Exception:
        return None
    return _clean_work(data) if data.get("id") else None


def work_by_title(title: str, year: int | None = None) -> dict[str, Any] | None:
    """Best title match (exact after normalization), or ``None``."""
    if not title:
        return None
    q = re.sub(r"[^\w\s]", " ", title)
    q = re.sub(r"\s+", " ", q).strip()[:200]
    filters = [f"title.search:{q}"]
    if year:
        filters.append(f"publication_year:{year - 1}-{year + 1}")
    params = {"filter": ",".join(filters), "per_page": 5, "select": SELECT, **_mailto()}
    try:
        data = _get(WORKS, params)
    except Exception:
        return None
    want = _norm(title)
    for w in data.get("results", []):
        if _norm(w.get("title") or "") == want:
            return _clean_work(w)
    res = data.get("results", [])
    return _clean_work(res[0]) if res and _norm(res[0].get("title") or "")[:40] == want[:40] else None


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# --------------------------------------------------------------------------- #
# Cleaning
# --------------------------------------------------------------------------- #
_PREPRINT_SERVERS = {
    "arxiv": "arXiv",
    "medrxiv": "medRxiv",
    "biorxiv": "bioRxiv",
    "research square": "Research Square",
    "ssrn": "SSRN",
    "preprints.org": "Preprints.org",
    "authorea": "Authorea",
    "techrxiv": "TechRxiv",
}


def venue_label(work: dict[str, Any]) -> str:
    """Short venue for tables: ``arXiv (preprint)``, journal or conference name."""
    name = work.get("venue") or ""
    if work.get("is_preprint"):
        low = name.lower()
        short = next((v for k, v in _PREPRINT_SERVERS.items() if k in low), name.split(" (")[0] or "preprint")
        return short
    return name


def _clean_work(w: dict[str, Any]) -> dict[str, Any]:
    doi = (w.get("doi") or "").replace("https://doi.org/", "") or None
    loc = w.get("primary_location") or {}
    host = loc.get("source") or {}
    authors = [(a.get("author") or {}).get("display_name") for a in (w.get("authorships") or [])]
    authors = [a for a in authors if a]
    wtype = w.get("type") or ""
    src_type = host.get("type") or ""
    is_preprint = wtype == "preprint" or src_type == "repository" or (loc.get("version") == "submittedVersion" and not host)
    kind = "preprint" if is_preprint else ("conference" if src_type == "conference" else ("journal" if src_type == "journal" else (src_type or "other")))
    pct = (w.get("citation_normalized_percentile") or {}).get("value")
    out = {
        "title": w.get("title"),
        "year": w.get("publication_year"),
        "venue": host.get("display_name") or loc.get("raw_source_name"),
        "venue_kind": kind,
        "is_preprint": bool(is_preprint),
        "type": wtype,
        "citation_count": w.get("cited_by_count", 0),
        "fwci": round(w["fwci"], 2) if isinstance(w.get("fwci"), (int, float)) else None,
        "citation_percentile": round(pct * 100, 1) if isinstance(pct, (int, float)) else None,
        "doi": doi,
        "openalex_id": w.get("id"),
        "authors": authors[:8],
        "first_author": (authors[0].split()[-1] if authors else None),
        "n_authors": len(authors),
    }
    out["venue_label"] = venue_label(out)
    return out
