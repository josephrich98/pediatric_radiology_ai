"""PubMed / NCBI E-utilities collector.

PubMed is the most reliable free source for "how much is being published" and it
covers the clinical radiology literature far better than the CS-paper databases.
Two things are pulled:

1. Yearly publication counts for each query in :data:`config.QUERIES` (and for
   the modality / task breakdowns). This is the core popularity time series.
2. The most-cited / representative articles for a query, used in the landscape
   reports. PubMed itself has no citation count, so citation enrichment is done
   later via :mod:`pedrad_ai.semantic_scholar`.

E-utilities docs: https://www.ncbi.nlm.nih.gov/books/NBK25501/
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from . import config, utils

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def _base_params() -> dict[str, Any]:
    params: dict[str, Any] = {"db": "pubmed", "tool": "pedrad_ai", "email": config.CONTACT_EMAIL}
    if config.NCBI_API_KEY:
        params["api_key"] = config.NCBI_API_KEY
    return params


def count_for_query(query: str, year: int | None = None) -> int:
    """Return the number of PubMed records matching ``query`` (optionally for a
    single publication ``year``)."""
    params = _base_params()
    term = query
    if year is not None:
        term = f"({query}) AND {year}[pdat]"
    params.update({"term": term, "retmax": 0, "rettype": "count", "retmode": "json"})
    # NCBI allows ~3 req/s without a key; the cached client paces us.
    pause = 0.12 if config.NCBI_API_KEY else 0.34
    data = utils.http_get_json(ESEARCH, params, pause=pause)
    return int(data["esearchresult"]["count"])


def yearly_counts(query: str, start: int | None = None, end: int | None = None) -> dict[int, int]:
    """Per-year record counts for ``query`` across the configured year range."""
    start = start or config.START_YEAR
    end = end or config.END_YEAR
    return {yr: count_for_query(query, yr) for yr in range(start, end + 1)}


def collect_all_yearly() -> dict[str, dict[int, int]]:
    """Yearly counts for every named query, modality, and task.

    Returns a nested dict keyed by series name, then by year. This is the single
    pull that feeds the trend figures and the pediatric-fraction analysis.
    """
    out: dict[str, dict[int, int]] = {}
    for name, query in config.QUERIES.items():
        out[name] = yearly_counts(query)
    for modality, terms in config.MODALITY_TERMS.items():
        q = f"{config.QUERIES['radiology_ai']} AND {terms}"
        out[f"modality::{modality}"] = yearly_counts(q)
    for task, terms in config.TASK_TERMS.items():
        q = f"{config.QUERIES['radiology_ai']} AND {terms}"
        out[f"task::{task}"] = yearly_counts(q)
    # Pediatric modality breakdown, so the report can say which pediatric
    # imaging modalities attract the most AI work.
    for modality, terms in config.MODALITY_TERMS.items():
        q = f"{config.QUERIES['pediatric_radiology_ai']} AND {terms}"
        out[f"ped_modality::{modality}"] = yearly_counts(q)
    return out


# RSNA's flagship journals, by PubMed journal abbreviation ([ta]). Used to
# answer "what fraction of RSNA papers deal with AI" directly, rather than only
# inferring it from a CS conference. "Radiol Artif Intell" is the dedicated AI
# journal and is counted in both numerator and denominator.
RSNA_JOURNALS = ["Radiology", "Radiographics", "Radiol Artif Intell"]


def rsna_ai_fraction(start: int | None = None, end: int | None = None) -> list[dict[str, Any]]:
    """Per-year AI fraction of articles in RSNA's flagship journals.

    For each year, counts all articles in the RSNA journals and the subset that
    also match the AI vocabulary, and returns the fraction. This is the closest
    PubMed-indexable proxy for "the share of RSNA output that is about AI".
    """
    from . import config as _cfg

    start = start or config.START_YEAR
    end = end or config.END_YEAR
    journal_clause = "(" + " OR ".join(f'"{j}"[ta]' for j in RSNA_JOURNALS) + ")"
    ai_clause = _cfg.QUERIES["all_ai"]
    rows: list[dict[str, Any]] = []
    for yr in range(start, end + 1):
        total = count_for_query(journal_clause, yr)
        ai = count_for_query(f"{journal_clause} AND {ai_clause}", yr)
        rows.append(
            {
                "year": yr,
                "rsna_total": total,
                "rsna_ai": ai,
                "rsna_ai_fraction": round(ai / total, 4) if total else 0.0,
            }
        )
    return rows


def journal_ai_fraction(
    journals: list[str], start: int, end: int
) -> list[dict[str, Any]]:
    """Per-year AI fraction of articles in a set of journals (by [ta] abbrev).

    Generalizes :func:`rsna_ai_fraction` to any society's flagship journals, so
    the conference analysis can report the AI share of RSNA, ACR, ECR, and SPR
    output on a common basis.
    """
    from . import config as _cfg

    journal_clause = "(" + " OR ".join(f'"{j}"[ta]' for j in journals) + ")"
    ai_clause = _cfg.QUERIES["all_ai"]
    rows: list[dict[str, Any]] = []
    for yr in range(start, end + 1):
        total = count_for_query(journal_clause, yr)
        ai = count_for_query(f"{journal_clause} AND {ai_clause}", yr)
        rows.append(
            {
                "year": yr,
                "total": total,
                "ai": ai,
                "ai_fraction": round(ai / total, 4) if total else 0.0,
            }
        )
    return rows


def top_articles(query: str, retmax: int = 200) -> list[dict[str, Any]]:
    """Fetch metadata for up to ``retmax`` recent articles matching ``query``.

    Returns dicts with pmid, title, journal, year, doi, and authors. Citation
    counts are added downstream. Sorted by PubMed relevance, which surfaces the
    canonical papers reasonably well; the caller can re-rank by citations.
    """
    params = _base_params()
    params.update({"term": query, "retmax": retmax, "sort": "relevance", "retmode": "json"})
    pause = 0.12 if config.NCBI_API_KEY else 0.34
    data = utils.http_get_json(ESEARCH, params, pause=pause)
    ids = data["esearchresult"].get("idlist", [])
    if not ids:
        return []
    return _fetch_article_details(ids)


def _fetch_article_details(pmids: list[str]) -> list[dict[str, Any]]:
    """Pull full records via EFetch XML for a list of PMIDs (chunked)."""
    articles: list[dict[str, Any]] = []
    pause = 0.12 if config.NCBI_API_KEY else 0.34
    for i in range(0, len(pmids), 100):
        chunk = pmids[i : i + 100]
        params = _base_params()
        params.update({"id": ",".join(chunk), "retmode": "xml"})
        xml = utils.http_get(EFETCH, params, pause=pause)
        articles.extend(_parse_pubmed_xml(xml))
    return articles


def _parse_pubmed_xml(xml: str) -> list[dict[str, Any]]:
    root = ET.fromstring(xml)
    out: list[dict[str, Any]] = []
    for art in root.findall(".//PubmedArticle"):
        medline = art.find(".//MedlineCitation")
        if medline is None:
            continue
        pmid_el = medline.find("PMID")
        pmid = pmid_el.text if pmid_el is not None else None
        article = medline.find("Article")
        if article is None:
            continue
        title_el = article.find("ArticleTitle")
        title = "".join(title_el.itertext()).strip() if title_el is not None else ""
        journal_el = article.find(".//Journal/Title")
        journal = journal_el.text if journal_el is not None else ""
        year = _extract_year(article)
        doi = None
        for idnode in art.findall(".//ArticleIdList/ArticleId"):
            if idnode.get("IdType") == "doi":
                doi = (idnode.text or "").strip()
        authors = []
        for a in article.findall(".//AuthorList/Author"):
            last = a.find("LastName")
            init = a.find("Initials")
            if last is not None:
                authors.append(f"{last.text} {init.text if init is not None else ''}".strip())
        out.append(
            {
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "year": year,
                "doi": doi,
                "authors": authors[:8],
            }
        )
    return out


def _extract_year(article: ET.Element) -> int | None:
    for path in (".//Journal/JournalIssue/PubDate/Year", ".//ArticleDate/Year"):
        el = article.find(path)
        if el is not None and el.text and el.text.isdigit():
            return int(el.text)
    medline_date = article.find(".//Journal/JournalIssue/PubDate/MedlineDate")
    if medline_date is not None and medline_date.text:
        token = medline_date.text.strip()[:4]
        if token.isdigit():
            return int(token)
    return None
