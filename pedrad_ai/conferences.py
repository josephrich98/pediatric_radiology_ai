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


# DBLP drops connections to throttle bursts, so we make exactly ONE request per
# venue-year (no pagination) and pace generously. DBLP caps each response at 100
# hits but reports the true total, so one request yields a 100-paper sample for
# the on-topic *fraction* plus the venue's true paper count for that year.
DBLP_PAUSE = 2.0


def fetch_venue_titles(venue_key: str, year: int) -> tuple[list[str], int]:
    """Fetch a sample of paper titles for a DBLP venue stream in a given year.

    Returns ``(titles, reported_total)`` where ``titles`` is up to 100 papers
    (DBLP's per-response cap) and ``reported_total`` is the venue's true paper
    count that year. Fractions are estimated from the sample; totals are exact.
    """
    venue_short = venue_key.split("/")[-1]
    params = {
        "q": f"stream:streams/conf/{venue_short}: year:{year}:",
        "format": "xml",
        "h": 100,
        "c": 0,
    }
    try:
        # max_retries=1: if DBLP throttles (it drops connections), skip this
        # venue-year fast rather than stalling the whole run in backoff.
        xml = utils.http_get(DBLP_PUBL_API, params, pause=DBLP_PAUSE, max_retries=1)
        root = ET.fromstring(xml)
    except Exception:
        return [], 0
    titles: list[str] = []
    for hit in root.findall(".//hit"):
        title_el = hit.find(".//title")
        if title_el is not None and title_el.text:
            titles.append("".join(title_el.itertext()).strip())
    total_el = root.find(".//hits")
    reported_total = int(total_el.get("total", 0)) if total_el is not None else len(titles)
    return titles, reported_total


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
    start = start or config.START_YEAR
    end = end or config.END_YEAR
    rows: list[dict[str, Any]] = []
    for venue_name, venue_key in config.DBLP_VENUES.items():
        rows.extend(venue_topic_fractions(venue_name, venue_key, start, end))
    return rows
