"""Which journals publish pediatric radiology AI, and how high-impact are they?

One row per journal: the number of pediatric radiology-AI papers it has
published (cumulative, by year) and a journal-level impact number for the x
axis of the scatter in ``figures/journal_impact*.png``.

Two halves:

1. **Counts.** Every PMID matching :data:`config.JOURNAL_QUERY` in each year
   is fetched from PubMed and its journal title and ISSNs are parsed. This uses
   its own EFetch parse rather than :func:`pubmed.article_details` because that
   one drops the ISSNs, and the ISSN is what joins a journal to its impact
   number.
2. **Impact.** Clarivate's Journal Impact Factor is licensed and has no free
   API. The default x value is therefore OpenAlex's ``2yr_mean_citedness`` for
   the journal — the same construction as the JIF (mean citations in the last
   two years) over OpenAlex's document set, so it runs lower than the published
   JIF while ranking journals about the same. It is looked up on the
   ``/sources`` endpoint by ISSN, 50 ISSNs per request, which costs one
   OpenAlex credit per request rather than the ten a search costs (see the
   budget note in :mod:`pedrad_ai.openalex`). Real JIFs pasted into
   ``data/journal_impact_overrides.json`` (keyed by ISSN-L or journal name)
   take precedence, and if any are present the figures relabel the axis.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any

from . import config, pubmed, utils

SOURCES = "https://api.openalex.org/sources"


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).strip()


# --------------------------------------------------------------------------- #
# 1. Counts
# --------------------------------------------------------------------------- #
def _parse_records(xml: str) -> list[dict[str, Any]]:
    """PMID, journal title, ISSNs and year from an EFetch reply."""
    root = ET.fromstring(xml)
    out: list[dict[str, Any]] = []
    for art in root.findall(".//PubmedArticle"):
        medline = art.find(".//MedlineCitation")
        article = medline.find("Article") if medline is not None else None
        if article is None:
            continue
        pmid_el = medline.find("PMID")
        journal = article.find("Journal")
        if journal is None:
            continue
        title_el = journal.find("Title")
        title = (title_el.text or "").strip() if title_el is not None else ""
        if not title:
            continue
        issns = [(e.text or "").strip() for e in journal.findall("ISSN")]
        # The linking ISSN lives on the MedlineJournalInfo, not the Journal.
        for e in medline.findall("MedlineJournalInfo/ISSNLinking"):
            if e.text:
                issns.append(e.text.strip())
        out.append(
            {
                "pmid": pmid_el.text if pmid_el is not None else None,
                "journal": title,
                "issns": [i for i in dict.fromkeys(issns) if i],
            }
        )
    return out


def _fetch_records(pmids: list[str]) -> list[dict[str, Any]]:
    pause = 0.12 if config.NCBI_API_KEY else 0.34
    out: list[dict[str, Any]] = []
    for i in range(0, len(pmids), 100):
        params = pubmed._base_params()
        params.update({"id": ",".join(pmids[i : i + 100]), "retmode": "xml"})
        try:
            xml = utils.http_get(pubmed.EFETCH, params, pause=pause)
        except Exception as exc:  # one bad batch must not lose the year
            print(f"    ! EFetch batch failed: {exc}")
            continue
        out.extend(_parse_records(xml))
    return out


def journal_counts(
    query: str | None = None, start: int | None = None, end: int | None = None
) -> dict[str, dict[str, Any]]:
    """``{normalized journal: {"journal", "issns", "counts": {year: n}}}``."""
    query = query or config.JOURNAL_QUERY
    start = start or config.JOURNAL_START_YEAR
    end = end or config.JOURNAL_END_YEAR
    journals: dict[str, dict[str, Any]] = {}
    for year in range(start, end + 1):
        pmids = pubmed.pmids_for_year(query, year)
        print(f"  {year}: {len(pmids)} papers")
        for rec in _fetch_records(pmids):
            title = rec["journal"]
            key = _norm(title)
            entry = journals.setdefault(key, {"journal": title, "issns": [], "counts": {}})
            entry["counts"][str(year)] = entry["counts"].get(str(year), 0) + 1
            for issn in rec["issns"]:
                if issn not in entry["issns"]:
                    entry["issns"].append(issn)
    return journals


# --------------------------------------------------------------------------- #
# 2. Impact
# --------------------------------------------------------------------------- #
def openalex_sources(issns: list[str]) -> dict[str, dict[str, Any]]:
    """``{issn: source}`` for every ISSN OpenAlex knows, 50 ISSNs per request.

    Degrades to ``{}`` on any failure (an exhausted OpenAlex budget included);
    the caller then plots only whatever the overrides file supplies.
    """
    found: dict[str, dict[str, Any]] = {}
    issns = [i for i in dict.fromkeys(issns) if i]
    for i in range(0, len(issns), 50):
        chunk = issns[i : i + 50]
        params = {
            "filter": "issn:" + "|".join(chunk),
            "select": "id,display_name,issn_l,issn,type,works_count,summary_stats",
            "per-page": 200,
            "mailto": config.CONTACT_EMAIL,
        }
        try:
            data = utils.http_get_json(SOURCES, params, pause=0.2)
        except Exception as exc:
            print(f"    ! OpenAlex sources lookup failed: {exc}")
            continue
        for src in data.get("results", []):
            for issn in src.get("issn") or []:
                found.setdefault(issn, src)
            if src.get("issn_l"):
                found.setdefault(src["issn_l"], src)
    return found


def _overrides() -> dict[str, float]:
    """Hand-supplied impact factors, keyed by ISSN or by normalized journal name."""
    path = config.JOURNAL_IMPACT_OVERRIDES
    if not path.exists():
        return {}
    raw = utils.load_json(path)
    out: dict[str, float] = {}
    for key, value in (raw or {}).items():
        if key.startswith("_") or value is None:
            continue
        out[key.strip()] = float(value)
        out[_norm(key)] = float(value)
    return out


def attach_impact(data: dict[str, Any], min_papers: int | None = None) -> dict[str, Any]:
    """Fill in ``impact_factor`` for every journal that the figures will plot.

    Only the journals above the plotting threshold are looked up. OpenAlex bills
    per request against a small daily budget, and the corpus has a thousand-journal
    tail of one-paper journals that no figure ever shows; asking about all of them
    costs twenty times as much and answers nothing.
    """
    rows = data["journals"]
    if min_papers is None:
        min_papers = min(config.JOURNAL_MIN_PAPERS, config.JOURNAL_MIN_PAPERS_RECENT)
    wanted = [r for r in rows if r["total"] >= min_papers]
    print(f"  looking up impact for {len(wanted)} of {len(rows)} journals")

    sources = openalex_sources([i for r in wanted for i in r["issns"]])
    print(f"  OpenAlex matched {len({s['id'] for s in sources.values()})} sources")
    overrides = _overrides()

    for row in rows:
        # Cleared first, so a re-run genuinely re-decides: deleting an entry
        # from the overrides file reverts that row, and a value this code no
        # longer accepts does not survive from the previous run.
        row["impact_factor"] = row["impact_source"] = None
        src = next((sources[i] for i in row["issns"] if i in sources), None)
        if src:
            row["journal"] = src.get("display_name") or row["journal"]
            row["issn_l"] = src.get("issn_l")
            row["openalex_id"] = src.get("id")
        override = next(
            (overrides[k] for k in [row.get("issn_l"), *row["issns"], _norm(row["journal"])] if k and k in overrides),
            None,
        )
        if override is not None:
            row["impact_factor"], row["impact_source"] = override, "override"
        elif src:
            # A citedness of exactly 0 means OpenAlex has no value for the
            # source, not that its papers go uncited: it is what the conference
            # proceedings series come back with. Left as None, so those land in
            # the "no impact number" note beside medRxiv rather than being
            # plotted at zero — which a log axis cannot draw anyway, so they
            # would count in the legend and appear nowhere.
            mc = (src.get("summary_stats") or {}).get("2yr_mean_citedness")
            if mc:
                row["impact_factor"] = round(float(mc), 3)
                row["impact_source"] = "openalex_2yr_mean_citedness"

    # A journal that changed name or ISSN appears twice in the PubMed titles but
    # once in OpenAlex; collapse those onto the OpenAlex id.
    merged: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row.get("openalex_id") or _norm(row["journal"])
        if key in merged:
            tgt = merged[key]
            for year, n in row["counts"].items():
                tgt["counts"][year] = tgt["counts"].get(year, 0) + n
            tgt["total"] += row["total"]
            tgt["issns"] = list(dict.fromkeys(tgt["issns"] + row["issns"]))
        else:
            merged[key] = row
    out = sorted(merged.values(), key=lambda r: -r["total"])

    data["journals"] = out
    data["n_journals"] = len(out)
    data["n_with_impact"] = sum(1 for r in out if r["impact_factor"] is not None)
    data["n_overrides"] = sum(1 for r in out if r["impact_source"] == "override")
    return data


def collect(
    query: str | None = None, start: int | None = None, end: int | None = None
) -> dict[str, Any]:
    """Counts joined to impact numbers, ready for the scatter."""
    start = start or config.JOURNAL_START_YEAR
    end = end or config.JOURNAL_END_YEAR
    journals = journal_counts(query, start, end)
    print(f"  {len(journals)} distinct journals")

    rows = [
        {
            "journal": entry["journal"],
            "issns": entry["issns"],
            "issn_l": None,
            "openalex_id": None,
            "counts": entry["counts"],
            "total": sum(entry["counts"].values()),
            "impact_factor": None,
            "impact_source": None,
        }
        for entry in journals.values()
    ]
    rows.sort(key=lambda r: -r["total"])
    data = {
        "query": query or config.JOURNAL_QUERY,
        "start_year": start,
        "end_year": end,
        "n_papers": sum(r["total"] for r in rows),
        "n_journals": len(rows),
        "journals": rows,
    }
    return attach_impact(data)
