"""arXiv collector: preprint counts for the count-based views, key-free.

PubMed indexes journals, not arXiv, and arXiv is where the preprint-first part
of radiology AI (foundation models, vision-language models, most ML-venue
work) appears. The arXiv API (https://info.arxiv.org/help/api/) takes boolean
queries over title/abstract (``all:``), with ``AND`` / ``OR`` / ``ANDNOT``,
parentheses, quoted phrases and a ``submittedDate`` range, and returns the
total hit count in every feed, so one request per (query, year) is enough.

The PubMed queries in :mod:`pedrad_ai.config` are translated by
:func:`to_arxiv_query` (via the OpenAlex translation, which already expands
truncations and drops field tags). arXiv stems query terms, so ``segment``
matches ``segmentation``. Results are stored in the same shapes as the PubMed
files (``pubmed_yearly_counts.json``, ``pubmed_crosstab.json``,
``pubmed_pediatric_problems.json``) so figures and slides can add the layers.

arXiv asks for no more than one request every three seconds from a single
client; the collector paces at ``PAUSE`` and everything is cached.
"""

from __future__ import annotations

import html
import re
from typing import Any

from . import config, openalex, utils

API = "http://export.arxiv.org/api/query"
PAUSE = 3.0
_RETRIES = 6


def _get(params: dict[str, Any]) -> str:
    """GET with a 429-aware schedule (arXiv throttles per client; a burst is
    answered with 429s for a while, so back off for tens of seconds)."""
    import time
    import urllib.error

    last: Exception | None = None
    for attempt in range(_RETRIES):
        try:
            return utils.http_get(API, params, pause=PAUSE, max_retries=1, timeout=90)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code not in (429, 500, 502, 503):
                raise
            time.sleep(15.0 * (attempt + 1))
        except Exception as exc:
            last = exc
            time.sleep(10.0 * (attempt + 1))
    assert last is not None
    raise last
_TOTAL_RE = re.compile(r"<opensearch:totalResults[^>]*>(\d+)<")
_TERM_RE = re.compile(r'"[^"]+"|[A-Za-z][\w\'\-]*')
_KEYWORDS = {"AND", "OR", "NOT"}


def to_arxiv_query(pubmed_query: str) -> str:
    """PubMed boolean -> arXiv ``all:`` boolean (``NOT`` -> ``ANDNOT``).

    Every bare term or quoted phrase gets the ``all:`` field prefix; the
    boolean structure and parentheses are kept; the ``NOT`` operator becomes
    arXiv's ``ANDNOT``. Groups are wrapped so ``A NOT B AND C`` keeps PubMed's
    left-to-right meaning.
    """
    s = openalex.translate_pubmed_query(pubmed_query)

    def _prefix(m: re.Match[str]) -> str:
        tok = m.group(0)
        if tok in _KEYWORDS:
            return "ANDNOT" if tok == "NOT" else tok
        return "all:" + tok

    s = _TERM_RE.sub(_prefix, s)
    return re.sub(r"\s+", " ", s).strip()


def count(query: str, start: int, end: int) -> int:
    """Number of arXiv papers matching ``query`` submitted in ``start``..``end``."""
    params = {
        "search_query": f"({query}) AND submittedDate:[{start}01010000 TO {end}12312359]",
        "max_results": 1,
    }
    xml = _get(params)
    m = _TOTAL_RE.search(xml)
    if not m:
        raise RuntimeError("arXiv reply without totalResults")
    return int(m.group(1))


def yearly_counts(query: str, start: int | None = None, end: int | None = None) -> dict[int, int]:
    start = start or config.START_YEAR
    end = end or config.END_YEAR
    return {yr: count(query, yr, yr) for yr in range(start, end + 1)}


def crosstab(
    base_query: str,
    rows: dict[str, str],
    cols: dict[str, str],
    start: int | None = None,
    end: int | None = None,
) -> dict[str, Any]:
    """arXiv counterpart of :func:`pubmed.crosstab` (same output shape)."""
    start = start or config.START_YEAR
    end = end or config.END_YEAR
    base = to_arxiv_query(base_query)
    rq = {r: to_arxiv_query(q) for r, q in rows.items()}
    cq = {c: to_arxiv_query(q) for c, q in cols.items()}
    total = count(base, start, end)
    row_tot = {r: count(f"({base}) AND {q}", start, end) for r, q in rq.items()}
    col_tot = {c: count(f"({base}) AND {q}", start, end) for c, q in cq.items()}
    cells = {r: {c: count(f"({base}) AND {rq[r]} AND {cq[c]}", start, end) for c in cq} for r in rq}
    return {"years": [start, end], "total": total, "row_totals": row_tot, "col_totals": col_tot, "cells": cells}


def problem_counts(
    base_query: str,
    problems: dict[str, str],
    eras: list[tuple[str, int, int]] | None = None,
) -> dict[str, Any]:
    """arXiv counterpart of :func:`pubmed.problem_counts` (same shape)."""
    eras = eras or config.ERAS
    base = to_arxiv_query(base_query)
    out: dict[str, Any] = {"eras": [{"label": lab, "start": a, "end": b} for lab, a, b in eras], "totals": {}, "counts": {}}
    for lab, a, b in eras:
        out["totals"][lab] = count(base, a, b)
    for name, q in problems.items():
        tq = to_arxiv_query(q)
        out["counts"][name] = {lab: count(f"({base}) AND {tq}", a, b) for lab, a, b in eras}
    return out


def paper_meta(arxiv_id: str) -> dict[str, Any] | None:
    """Title, first author, author count and year for one arXiv id."""
    try:
        xml = _get({"id_list": arxiv_id, "max_results": 1})
    except Exception:
        return None
    entry = re.search(r"<entry>(.*?)</entry>", xml, re.S)
    if not entry:
        return None
    e = entry.group(1)
    authors = re.findall(r"<name>(.*?)</name>", e)
    title = re.search(r"<title>(.*?)</title>", e, re.S)
    pub = re.search(r"<published>(\d{4})", e)
    if not authors or not pub:
        return None
    return {
        "title": html.unescape(re.sub(r"\s+", " ", title.group(1)).strip()) if title else None,
        "first_author": html.unescape(authors[0]).split()[-1],
        "n_authors": len(authors),
        "year": int(pub.group(1)),
        "venue": "arXiv",
        "is_preprint": True,
    }
