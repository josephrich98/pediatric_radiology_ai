"""Conference collector: what fraction of ML / imaging venues is on-topic.

Two complementary questions:

* What fraction of a top ML venue (NeurIPS) deals with radiology / medical
  imaging? This proxies how much the broad AI community works on our domain.
* What fraction of an imaging venue (MICCAI, ISBI) or radiology forum deals with
  AI, and how much of that is pediatric?

Paper titles are pulled from DBLP, which has clean, free, per-venue listings
covering NeurIPS, CVPR, ICCV, MICCAI, and ISBI back many years. Titles are then
labelled with the keyword sets in :mod:`pedrad_ai.config`. Title-only labelling
is coarse, so the reports present these as lower bounds / indicative fractions.

DBLP API: https://dblp.org/faq/How+to+use+the+dblp+search+API.html
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any

from . import config, utils

DBLP_PUBL_API = "https://dblp.org/search/publ/api"


def _matches(title: str, keywords: list[str]) -> bool:
    """Whole-word / phrase match (case-insensitive) to avoid substring noise."""
    t = title.lower()
    for k in keywords:
        # \b around the phrase; keywords with hyphens still match on word edges.
        if re.search(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", t):
            return True
    return False


# DBLP caps each response at 100 hits and drops connections to throttle
# bursts, so we page through a venue-year in 100-hit requests, paced
# generously, up to DBLP_SAMPLE_TARGET titles. A dropped page ends the sample
# early rather than aborting; cached pages persist, so re-running the collector
# accumulates coverage. DBLP reports the true total on every page, so the
# venue's paper count is exact even when the sample is partial.
DBLP_PAUSE = 2.0
DBLP_PAGE = 100
DBLP_SAMPLE_TARGET = 500


def fetch_venue_titles(venue_key: str, year: int) -> tuple[list[str], int]:
    """Fetch a sample of paper titles for a DBLP venue stream in a given year.

    Returns ``(titles, reported_total)`` where ``titles`` is up to
    ``DBLP_SAMPLE_TARGET`` papers (paged 100 at a time) and ``reported_total``
    is the venue's true paper count that year. Fractions are estimated from
    the sample; totals are exact.
    """
    venue_short = venue_key.split("/")[-1]
    titles: list[str] = []
    reported_total = 0
    for first in range(0, DBLP_SAMPLE_TARGET, DBLP_PAGE):
        params = {
            "q": f"stream:streams/conf/{venue_short}: year:{year}:",
            "format": "xml",
            "h": DBLP_PAGE,
            "f": first,
            "c": 0,
        }
        try:
            xml = utils.http_get(DBLP_PUBL_API, params, pause=DBLP_PAUSE, max_retries=2)
            root = ET.fromstring(xml)
        except Exception:
            break
        page: list[str] = []
        for hit in root.findall(".//hit"):
            title_el = hit.find(".//title")
            if title_el is not None and title_el.text:
                page.append("".join(title_el.itertext()).strip())
        total_el = root.find(".//hits")
        if total_el is not None:
            reported_total = int(total_el.get("total", 0))
        titles.extend(page)
        if len(page) < DBLP_PAGE or len(titles) >= reported_total:
            break
    return titles, reported_total or len(titles)


def venue_topic_fractions(venue_name: str, venue_key: str, start: int, end: int) -> list[dict[str, Any]]:
    """Per-year counts of total / radiology / AI / pediatric papers for a venue.

    Returns a list of row dicts suitable for CSV, one per year.
    """
    rows: list[dict[str, Any]] = []
    for yr in range(start, end + 1):
        titles, reported_total = fetch_venue_titles(venue_key, yr)
        sampled = len(titles)
        if sampled == 0:
            continue
        n_rad = sum(_matches(t, config.RADIOLOGY_TITLE_KEYWORDS) for t in titles)
        n_ai = sum(_matches(t, config.AI_TITLE_KEYWORDS) for t in titles)
        n_ped = sum(_matches(t, config.PEDIATRIC_TITLE_KEYWORDS) for t in titles)
        rows.append(
            {
                "venue": venue_name,
                "year": yr,
                "total_papers": reported_total or sampled,
                "sampled_papers": sampled,
                "radiology_papers": n_rad,
                "ai_papers": n_ai,
                "pediatric_papers": n_ped,
                "radiology_fraction": round(n_rad / sampled, 4),
                "ai_fraction": round(n_ai / sampled, 4),
                "pediatric_fraction": round(n_ped / sampled, 4),
            }
        )
    return rows


def collect_all(start: int | None = None, end: int | None = None) -> list[dict[str, Any]]:
    """Radiology/AI fractions for the DBLP ML venues over the conference window."""
    start = start or config.CONF_START_YEAR
    end = end or config.CONF_END_YEAR
    rows: list[dict[str, Any]] = []
    for venue_name, venue_key in config.DBLP_VENUES.items():
        rows.extend(venue_topic_fractions(venue_name, venue_key, start, end))
    return rows


def collect_societies(start: int | None = None, end: int | None = None) -> list[dict[str, Any]]:
    """AI fraction of each radiology society's flagship journals, per year.

    RSNA / ACR / ECR / SPR meetings have no machine-readable program, so their
    engagement with AI is read from the AI share of their journals via PubMed.
    """
    from . import pubmed

    start = start or config.CONF_START_YEAR
    end = end or config.CONF_END_YEAR
    rows: list[dict[str, Any]] = []
    for society, journals in config.SOCIETY_JOURNALS.items():
        for r in pubmed.journal_ai_fraction(journals, start, end):
            rows.append(
                {
                    "society": society,
                    "journals": "; ".join(journals),
                    "year": r["year"],
                    "total_articles": r["total"],
                    "ai_articles": r["ai"],
                    "ai_fraction": r["ai_fraction"],
                }
            )
    return rows


# --------------------------------------------------------------------------- #
# Venue tables: the radiology-AI works that made it into each big venue
# --------------------------------------------------------------------------- #
def is_radiology_paper(title: str) -> bool:
    """Title carries a radiology / medical-imaging signal and no excluded domain."""
    t = title or ""
    return (bool(t) and not _matches(t, config.PAPER_EXCLUDE_DOMAIN) and _matches(t, config.PAPER_MEDICAL_SIGNAL)
            and _matches(t, config.PAPER_AI_SIGNAL))


def is_pediatric_title(title: str) -> bool:
    return _matches(title or "", config.PAPER_PEDIATRIC_SIGNAL)


def _venue_works_s2(spec: dict[str, Any], start: int, end: int) -> list[dict[str, Any]]:
    """Radiology-AI works at a venue. ML venues: radiology term query, title
    filter. Radiology journals: AI term query (radiology is implicit)."""
    from . import semantic_scholar

    if spec.get("query") == "ai":
        return semantic_scholar.venue_search(config.S2_AI_QUERY, spec["venue"], start, end)
    papers = semantic_scholar.venue_search(config.S2_RADIOLOGY_QUERY, spec["venue"], start, end)
    return [p for p in papers if is_radiology_paper(p.get("title") or "")]


def collect_venue_works(start: int | None = None, end: int | None = None, top_n: int = 40) -> dict[str, Any]:
    """Per venue: radiology-AI works over the window, ranked by citations.

    Semantic Scholar rows carry no FWCI; ``scripts/enrich_fwci.py`` fills it
    in afterwards from OpenAlex by DOI. Every row gets a ``pediatric`` flag
    from its title.
    """
    start = start or config.VENUE_WORKS_START
    end = end or config.END_YEAR
    out: dict[str, Any] = {}
    for name, spec in config.CONFERENCE_WORKS.items():
        print(f"  {name} ({spec['kind']})")
        works = _venue_works_s2(spec, start, end)
        works.sort(key=lambda w: w.get("citation_count", 0), reverse=True)
        by_year: dict[str, int] = {}
        for w in works:
            by_year[str(w.get("year"))] = by_year.get(str(w.get("year")), 0) + 1
        rows: list[dict[str, Any]] = []
        for w in works[:top_n]:
            row = {
                "title": w.get("title"),
                "year": w.get("year"),
                "citation_count": w.get("citation_count", 0),
                "fwci": w.get("fwci"),
                "doi": w.get("doi"),
                "venue_label": w.get("venue_label") or spec.get("venue") or name,
                "first_author": w.get("first_author") or ((w.get("authors") or [None])[0] or "").split()[-1:] or None,
                "pediatric": is_pediatric_title(w.get("title") or ""),
            }
            if isinstance(row["first_author"], list):
                row["first_author"] = row["first_author"][0] if row["first_author"] else None
            rows.append(row)
        out[name] = {
            "kind": spec["kind"],
            "full": spec.get("full", name),
            "note": spec.get("note"),
            "years": [start, end],
            "n_works": len(works),
            "n_pediatric": sum(1 for w in works if is_pediatric_title(w.get("title") or "")),
            "by_year": dict(sorted(by_year.items())),
            "works": rows,
        }
        print(f"    -> {len(works)} radiology-AI works, {out[name]['n_pediatric']} pediatric; top: {rows[0]['title'][:60] if rows else '-'}")
    return out
