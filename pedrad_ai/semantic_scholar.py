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


def _clean_paper(p: dict[str, Any]) -> dict[str, Any]:
    ext = p.get("externalIds") or {}
    return {
        "title": p.get("title"),
        "year": p.get("year"),
        "venue": p.get("venue"),
        "citation_count": p.get("citationCount") or 0,
        "influential_citation_count": p.get("influentialCitationCount") or 0,
        "doi": ext.get("DOI"),
        "pmid": ext.get("PubMed"),
        "fields_of_study": p.get("fieldsOfStudy") or [],
        "authors": [a.get("name") for a in (p.get("authors") or [])][:8],
    }
