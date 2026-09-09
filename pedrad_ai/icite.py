"""Citation counts and year-normalized impact from NIH iCite, keyed by PMID.

The paper database needs a way to cut ~10,000 query hits down to the papers
that the field actually reads. iCite (https://icite.od.nih.gov) is the NIH's
own citation index: no API key, up to a thousand PMIDs per request, and it
speaks PMIDs natively, which OpenAlex does not.

Three numbers are taken from it:

``citation_count``
    PubMed-indexed papers citing the record. Smaller than a Google Scholar
    count (no preprints, theses or books) and therefore a conservative filter.
``citations_per_year``
    The raw count divided by years since publication. Always computable, which
    matters for the current and previous year where a raw count is near zero by
    construction.
``relative_citation_ratio`` (RCR)
    iCite's field- and time-normalized measure: 1.0 is the median NIH-funded
    paper in the same field and year, 2.0 is twice that. This is the column to
    read when comparing a 2016 paper with a 2024 one. It is undefined for
    papers less than about two years old and for non-research articles, so it
    is often blank for the newest work — ``citations_per_year`` and OpenAlex's
    field-weighted citation impact cover that gap.

The legacy endpoint is used because it is the one that returns RCR and the NIH
percentile; the field names differ from the non-legacy form.
"""

from __future__ import annotations

from typing import Any

from . import utils

ICITE = "https://icite.od.nih.gov/api/pubs"

# iCite allows 1000 ids per request; 250 keeps the URL short enough to cache
# cleanly and makes a partial failure cheap to retry.
BATCH = 250


def _round(value: Any, digits: int = 2) -> float | None:
    return round(value, digits) if isinstance(value, (int, float)) else None


def fetch(pmids: list[str]) -> dict[str, dict[str, Any]]:
    """PMID -> impact metrics for the ids iCite knows.

    Missing PMIDs are simply absent from the result. Returns what it managed to
    fetch if a batch fails, so one bad request never aborts a run.
    """
    out: dict[str, dict[str, Any]] = {}
    unique = list(dict.fromkeys(str(p) for p in pmids))
    for i in range(0, len(unique), BATCH):
        chunk = unique[i : i + BATCH]
        try:
            data = utils.http_get_json(
                ICITE, {"pmids": ",".join(chunk), "legacy": "true"}, pause=0.2
            )
        except Exception:
            continue
        for rec in data.get("data") or []:
            pmid = str(rec.get("pmid") or rec.get("_id") or "")
            if not pmid:
                continue
            out[pmid] = {
                "citations": int(rec.get("citation_count") or 0),
                "citations_per_year": _round(rec.get("citations_per_year")),
                "rcr": _round(rec.get("relative_citation_ratio")),
                "nih_percentile": _round(rec.get("nih_percentile"), 1),
                "year": rec.get("year"),
                "title": rec.get("title"),
                "journal": rec.get("journal"),
                "doi": rec.get("doi"),
            }
    return out


def citation_counts(pmids: list[str]) -> dict[str, int]:
    """PMID -> citation count. PMIDs iCite does not know count as zero."""
    known = fetch(pmids)
    return {str(p): known.get(str(p), {}).get("citations", 0) for p in pmids}


def metrics(pmids: list[str]) -> dict[str, dict[str, Any]]:
    """PMID -> {citations, citations_per_year, rcr, nih_percentile}, zero-filled.

    Every requested PMID gets an entry so callers can filter without guarding
    for absence; the normalized measures stay ``None`` when iCite has not
    computed them (too recent, or not a research article).
    """
    known = fetch(pmids)
    return {
        str(p): {
            "citations": known.get(str(p), {}).get("citations", 0),
            "citations_per_year": known.get(str(p), {}).get("citations_per_year"),
            "rcr": known.get(str(p), {}).get("rcr"),
            "nih_percentile": known.get(str(p), {}).get("nih_percentile"),
        }
        for p in pmids
    }
