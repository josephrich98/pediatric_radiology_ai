"""Semantic Scholar collector: citation counts and most-influential papers.

Semantic Scholar's Graph API gives citation counts that PubMed lacks, which is
what we need to name the "biggest players" — the most-cited radiology AI papers
and, separately, the most-cited pediatric radiology AI papers. It also exposes a
relevance-ranked bulk search.

API docs: https://api.semanticscholar.org/api-docs/graph
The public (keyless) endpoint is heavily rate-limited; the collector paces
itself and caches aggressively. Set SEMANTIC_SCHOLAR_API_KEY to go faster.
"""

from __future__ import annotations

from typing import Any

from . import config, utils

SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"
BY_DOI = "https://api.semanticscholar.org/graph/v1/paper/DOI:"

PAPER_FIELDS = (
    "title,year,citationCount,influentialCitationCount,venue,externalIds,"
    "authors,fieldsOfStudy"
)


def _headers() -> dict[str, str]:
    if config.SEMANTIC_SCHOLAR_API_KEY:
        return {"x-api-key": config.SEMANTIC_SCHOLAR_API_KEY}
    return {}


def search_top_cited(query: str, limit: int = 100, min_year: int | None = None) -> list[dict[str, Any]]:
    """Return papers matching ``query``, ranked by citation count (descending).

    ``query`` is a plain keyword phrase (Semantic Scholar does not take boolean
    syntax). The endpoint returns relevance order; we re-sort by citationCount.
    """
    params: dict[str, Any] = {
        "query": query,
        "limit": min(limit, 100),
        "fields": PAPER_FIELDS,
    }
    if min_year:
        params["year"] = f"{min_year}-"
    try:
        data = utils.http_get_json(SEARCH, params, headers=_headers(), pause=1.1)
    except Exception:
        return []
    papers = data.get("data", []) or []
    cleaned = [_clean_paper(p) for p in papers]
    cleaned.sort(key=lambda r: r.get("citation_count", 0), reverse=True)
    return cleaned


def citations_for_doi(doi: str) -> dict[str, Any] | None:
    """Look up a single paper by DOI; returns None if not found."""
    if not doi:
        return None
    try:
        data = utils.http_get_json(
            BY_DOI + doi, {"fields": PAPER_FIELDS}, headers=_headers(), pause=1.1
        )
    except Exception:
        return None
    return _clean_paper(data)


_PREPRINT_VENUES = {"arxiv.org": "arXiv", "arxiv": "arXiv", "medrxiv": "medRxiv", "biorxiv": "bioRxiv",
                    "research square": "Research Square", "ssrn": "SSRN", "preprints.org": "Preprints.org"}


def _clean_paper(p: dict[str, Any]) -> dict[str, Any]:
    ext = p.get("externalIds") or {}
    venue = p.get("venue") or (p.get("journal") or {}).get("name") or ""
    low = venue.lower()
    pre = next((v for k, v in _PREPRINT_VENUES.items() if k in low), None)
    if not pre and not venue and ext.get("ArXiv") and not ext.get("DOI"):
        pre = "arXiv"
    authors = [a.get("name") for a in (p.get("authors") or []) if a.get("name")]
    doi = ext.get("DOI")
    if not doi and ext.get("ArXiv"):
        doi = f"10.48550/arxiv.{ext['ArXiv']}"
    return {
        "title": p.get("title"),
        "year": p.get("year"),
        "venue": venue or ("arXiv" if pre else None),
        "venue_label": pre if pre else venue,
        "is_preprint": bool(pre),
        "citation_count": p.get("citationCount") or 0,
        "influential_citation_count": p.get("influentialCitationCount") or 0,
        "fwci": None,
        "doi": doi,
        "arxiv_id": ext.get("ArXiv"),
        "pmid": ext.get("PubMed"),
        "s2_id": p.get("paperId"),
        "fields_of_study": p.get("fieldsOfStudy") or [],
        "authors": authors[:8],
        "first_author": authors[0].split()[-1] if authors else None,
        "n_authors": len(authors),
    }


# --------------------------------------------------------------------------- #
# Venue search (bulk endpoint)
# --------------------------------------------------------------------------- #
BULK = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"


def _truncated(data: dict[str, Any]) -> bool:
    """The bulk endpoint sometimes answers with a handful of rows and no
    continuation token although ``total`` is in the hundreds; treat that as a
    failed page."""
    rows = len(data.get("data") or [])
    total = int(data.get("total") or 0)
    return rows < min(total, 1000) and not data.get("token")


def _bulk_get(params: dict[str, Any]) -> dict[str, Any]:
    """One bulk-search page, re-fetched (bypassing the cache) when truncated;
    the best reply is written back to the cache."""
    import json as _json
    import urllib.parse as _up

    data = utils.http_get_json(BULK, params, headers=_headers(), pause=1.5, max_retries=4, timeout=90)
    best = data
    attempt = 0
    while _truncated(best) and attempt < 3:
        attempt += 1
        fresh = utils.http_get_json(BULK, params, headers=_headers(), use_cache=False, pause=2.0, max_retries=3, timeout=90)
        if len(fresh.get("data") or []) > len(best.get("data") or []):
            best = fresh
    if best is not data:
        url = BULK + "?" + _up.urlencode(params, doseq=True)
        utils._cache_path(url, None).write_text(_json.dumps(best), encoding="utf-8")
    return best
BULK_FIELDS = "title,year,venue,journal,citationCount,influentialCitationCount,externalIds,authors,publicationDate"


def venue_search(query: str, venue: str, start: int, end: int, max_pages: int = 3) -> list[dict[str, Any]]:
    """Works at ``venue`` (Semantic Scholar venue name / alias) matching ``query``.

    Uses the bulk endpoint, which takes boolean syntax (``|`` = OR, ``*`` =
    prefix, quotes = phrase) and a ``venue=`` filter; paged by continuation
    token, up to 1,000 works per page, sorted by citations. Returns [] on
    failure so one venue never aborts the run.
    """
    params: dict[str, Any] = {
        "query": query,
        "venue": venue,
        "year": f"{start}-{end}",
        "fields": BULK_FIELDS,
        "sort": "citationCount:desc",
    }
    out: list[dict[str, Any]] = []
    token: str | None = None
    for _ in range(max_pages):
        if token:
            params["token"] = token
        try:
            data = _bulk_get(params)
        except Exception:
            break
        out.extend(_clean_paper(p) for p in data.get("data", []) or [])
        token = data.get("token")
        if not token:
            break
    return out


def bulk_search(query: str, start: int, end: int, max_pages: int = 1) -> list[dict[str, Any]]:
    """Works matching ``query`` published ``start``..``end``, most cited first.

    One page is up to 1,000 works; for a most-cited table one page is enough.
    """
    params: dict[str, Any] = {"query": query, "year": f"{start}-{end}", "fields": BULK_FIELDS, "sort": "citationCount:desc"}
    out: list[dict[str, Any]] = []
    token: str | None = None
    for _ in range(max_pages):
        if token:
            params["token"] = token
        try:
            data = _bulk_get(params)
        except Exception as exc:
            print(f"    [warn] Semantic Scholar search failed ({exc}): {query[:50]!r}")
            break
        out.extend(_clean_paper(p) for p in data.get("data", []) or [])
        token = data.get("token")
        if not token:
            break
    return out


def union_search(queries: list[str], start: int, end: int, per_query: int = 200) -> list[dict[str, Any]]:
    """Run several searches, union by paper id, rank by citations.

    Same idea as ``openalex.top_cited_union``: a single ``radiology deep
    learning`` query misses landmark papers whose title never says radiology,
    so modality- and task-specific queries are unioned. Preprints are included
    (Semantic Scholar indexes arXiv, medRxiv, bioRxiv).
    """
    by_id: dict[str, dict[str, Any]] = {}
    for q in queries:
        for paper in bulk_search(q, start, end)[:per_query]:
            pid = paper.get("s2_id") or paper.get("title")
            if pid and pid not in by_id:
                by_id[pid] = paper
    out = list(by_id.values())
    out.sort(key=lambda r: r.get("citation_count", 0), reverse=True)
    return out
