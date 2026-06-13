"""Patent activity via the PatentsView API.

Patents are a useful, lagging signal of commercial interest: a company files
when it thinks something is worth protecting. PatentsView (USPTO-backed, free,
no key) lets us count granted patents per year whose title/abstract mention
radiology imaging together with AI terms.

API docs: https://search.patentsview.org/docs/

Note: as of 2024 the PatentsView search API requires a free API key sent in the
``X-Api-Key`` header (request one at https://patentsview.org/apis/keyrequest).
Set it via the ``PATENTSVIEW_API_KEY`` environment variable. Without a key the
endpoint returns 403 and the collector reports zero patents (the reports flag
this), so the rest of the pipeline still runs.

PatentsView indexes granted US patents, which undercount very recent years
because of the multi-year grant lag; the reports flag this explicitly.
"""

from __future__ import annotations

import os
from typing import Any

from . import config, utils

PATENTSVIEW_API_KEY = os.environ.get("PATENTSVIEW_API_KEY")

# The current PatentsView search API. If this host is unreachable in a given
# environment, the collector degrades to returning empty counts rather than
# failing the whole pipeline.
PATENTSVIEW_URL = "https://search.patentsview.org/api/v1/patent/"
LEGACY_URL = "https://api.patentsview.org/patents/query"

_AI_PATENT_TERMS = [
    "artificial intelligence", "machine learning", "deep learning",
    "neural network", "convolutional", "computer-aided diagnosis",
]
_RADIOLOGY_PATENT_TERMS = [
    "radiology", "radiograph", "medical imaging", "computed tomography",
    "magnetic resonance", "ultrasound", "mammograph", "x-ray",
]


def _text_or_group(field: str, terms: list[str]) -> dict[str, Any]:
    return {"_or": [{"_text_phrase": {field: t}} for t in terms]}


def count_patents(year: int, pediatric: bool = False) -> int:
    """Count granted patents for ``year`` matching radiology + AI terms.

    When ``pediatric`` is True, additionally require a pediatric term. Returns 0
    if the API is unreachable so the rest of the pipeline can proceed.
    """
    title_clause = {
        "_and": [
            _text_or_group("patent_title", _RADIOLOGY_PATENT_TERMS + ["imaging"]),
            _text_or_group("patent_abstract", _AI_PATENT_TERMS),
        ]
    }
    clauses: list[dict[str, Any]] = [
        title_clause,
        {"_gte": {"patent_date": f"{year}-01-01"}},
        {"_lte": {"patent_date": f"{year}-12-31"}},
    ]
    if pediatric:
        clauses.append(
            _text_or_group(
                "patent_abstract", ["pediatric", "paediatric", "child", "infant", "neonatal"]
            )
        )
    query = {"_and": clauses}
    payload = {
        "q": query,
        "f": ["patent_id"],
        "o": {"size": 1},
    }
    if not PATENTSVIEW_API_KEY:
        # No key -> the endpoint will 403; skip fast rather than retry-storm.
        return 0
    try:
        data = utils.http_post_json(
            PATENTSVIEW_URL,
            payload,
            headers={"X-Api-Key": PATENTSVIEW_API_KEY},
            pause=1.0,
            max_retries=2,
        )
    except Exception:
        return 0
    # The v1 API returns a total_hits field; fall back to counting returned ids.
    if isinstance(data, dict):
        if "total_hits" in data:
            return int(data["total_hits"])
        if "count" in data:
            return int(data["count"])
    return 0


def collect_yearly(pediatric: bool = False) -> dict[int, int]:
    """Per-year granted-patent counts across the configured year range."""
    return {yr: count_patents(yr, pediatric=pediatric) for yr in utils.years()}
