"""OpenAlex collector: citation counts and most-cited papers, key-free.

OpenAlex (https://openalex.org) is an open index of scholarly works with
citation counts (``cited_by_count``), generous rate limits, and no API key. It
replaces Semantic Scholar here, whose key-less endpoint is too heavily
rate-limited to use reliably. We use it for two things:

* the "biggest players" tables: works matching a topic, ranked by citations;
* a cross-check on yearly publication counts (works ``group_by`` year).

API docs: https://docs.openalex.org/
Including a ``mailto`` puts requests in the faster, more reliable pool.
"""

from __future__ import annotations

from typing import Any

from . import config, utils

WORKS = "https://api.openalex.org/works"


def _mailto() -> dict[str, str]:
    return {"mailto": config.CONTACT_EMAIL}


def top_cited(query: str, per_page: int = 50, min_year: int | None = None) -> list[dict[str, Any]]:
    """Return works matching ``query`` (full-text search), ranked by citations.

    ``query`` is a plain phrase; every word is required (OpenAlex treats spaces
    in ``title_and_abstract.search`` as AND), which keeps results on-topic
    instead of surfacing unrelated high-citation papers. Results are sorted by
    ``cited_by_count`` descending. Returns [] on failure so the pipeline keeps
    going.
    """
    filters = [f"title_and_abstract.search:{query}", "type:article"]
    if min_year:
        filters.append(f"from_publication_date:{min_year}-01-01")
    params = {
        "filter": ",".join(filters),
        "sort": "cited_by_count:desc",
        "per_page": min(per_page, 200),
        **_mailto(),
    }
    try:
        data = utils.http_get_json(WORKS, params, pause=0.4)
    except Exception:
        return []
    return [_clean_work(w) for w in data.get("results", [])]


def yearly_counts(query: str) -> dict[int, int]:
    """Publication counts per year for ``query`` (OpenAlex ``group_by``)."""
    params = {
        "filter": f"title_and_abstract.search:{query},type:article",
        "group_by": "publication_year",
        "per_page": 1,
        **_mailto(),
    }
    try:
        data = utils.http_get_json(WORKS, params, pause=0.4)
    except Exception:
        return {}
    out: dict[int, int] = {}
    for g in data.get("group_by", []):
        key = g.get("key")
        if key and str(key).isdigit():
            yr = int(key)
            if config.START_YEAR <= yr <= config.END_YEAR:
                out[yr] = g.get("count", 0)
    return dict(sorted(out.items()))


def _clean_work(w: dict[str, Any]) -> dict[str, Any]:
    doi = (w.get("doi") or "").replace("https://doi.org/", "") or None
    host = (w.get("primary_location") or {}).get("source") or {}
    authors = [
        (a.get("author") or {}).get("display_name")
        for a in (w.get("authorships") or [])
    ]
    return {
        "title": w.get("title"),
        "year": w.get("publication_year"),
        "venue": host.get("display_name"),
        "citation_count": w.get("cited_by_count", 0),
        "doi": doi,
        "openalex_id": w.get("id"),
        "authors": [a for a in authors if a][:8],
    }
