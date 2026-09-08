"""Citation counts from NIH iCite, keyed by PMID.

The paper database needs a way to cut ~10,000 query hits down to the papers
that the field actually reads. iCite (https://icite.od.nih.gov) is the NIH's
own citation index: no API key, up to a thousand PMIDs per request, and it
speaks PMIDs natively, which OpenAlex does not. ``citedByPmidCount`` is the
number of PubMed-indexed papers citing the record — smaller than a Google
Scholar count (no preprints, theses, or books) and therefore a conservative
filter, which is what we want.

Counts are a snapshot: they grow over time, and a 2026 paper has had no chance
to accrue any. Whatever threshold the caller sets is therefore also an implicit
recency filter, and the report says so.
"""

from __future__ import annotations

from typing import Any

from . import utils

ICITE = "https://icite.od.nih.gov/api/pubs"

# iCite allows 1000 ids per request; 250 keeps the URL short enough to cache
# cleanly and makes a partial failure cheap to retry.
BATCH = 250


def fetch(pmids: list[str]) -> dict[str, dict[str, Any]]:
    """PMID -> {citations, year, title, journal, doi} for the ids iCite knows.

    Missing PMIDs are simply absent from the result. Returns what it managed to
    fetch if a batch fails, so one bad request never aborts a run.
    """
    out: dict[str, dict[str, Any]] = {}
    unique = list(dict.fromkeys(str(p) for p in pmids))
    for i in range(0, len(unique), BATCH):
        chunk = unique[i : i + BATCH]
        try:
            data = utils.http_get_json(
                ICITE, {"pmids": ",".join(chunk), "legacy": "false"}, pause=0.2
            )
        except Exception:
            continue
        for rec in data.get("data") or []:
            pmid = str(rec.get("pmid") or rec.get("_id") or "")
            if not pmid:
                continue
            out[pmid] = {
                "citations": int(rec.get("citedByPmidCount") or 0),
                "year": rec.get("pubYear"),
                "title": rec.get("title"),
                "journal": rec.get("journalNameIso"),
                "doi": rec.get("doi"),
            }
    return out


def citation_counts(pmids: list[str]) -> dict[str, int]:
    """PMID -> citation count. PMIDs iCite does not know count as zero."""
    known = fetch(pmids)
    return {str(p): known.get(str(p), {}).get("citations", 0) for p in pmids}
