"""Crossref collector: a second, broader publication-count signal.

Crossref indexes journal articles across publishers (not just MEDLINE), so it
cross-checks the PubMed trend and reaches venues PubMed misses. We use the
``works`` endpoint's ``total-results`` with date filters to get yearly counts
without downloading every record.

API docs: https://api.crossref.org/swagger-ui/index.html
"""

from __future__ import annotations

from typing import Any

from . import config, utils

WORKS = "https://api.crossref.org/works"

# Crossref does plain keyword matching, so the boolean PubMed strings are
# replaced with compact query phrases here.
CROSSREF_QUERIES: dict[str, str] = {
    "radiology_ai": "radiology artificial intelligence deep learning medical imaging",
    "pediatric_radiology_ai": "pediatric radiology artificial intelligence deep learning",
    "all_radiology": "radiology medical imaging",
    "pediatric_radiology": "pediatric radiology imaging",
}


def count_works(query: str, year: int) -> int:
    """Number of Crossref works matching ``query`` published in ``year``."""
    params = {
        "query": query,
        "filter": f"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31,type:journal-article",
        "rows": 0,
        "mailto": config.CONTACT_EMAIL,
    }
    try:
        data = utils.http_get_json(WORKS, params, pause=0.5)
    except Exception:
        return 0
    return int(data.get("message", {}).get("total-results", 0))


def yearly_counts(query_name: str) -> dict[int, int]:
    query = CROSSREF_QUERIES[query_name]
    return {yr: count_works(query, yr) for yr in utils.years()}


def collect_all_yearly() -> dict[str, dict[int, int]]:
    return {name: yearly_counts(name) for name in CROSSREF_QUERIES}
