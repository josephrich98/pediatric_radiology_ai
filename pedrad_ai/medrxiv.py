"""medRxiv collector: preprint counts via Europe PMC, key-free.

arXiv is one half of the preprint layer (:mod:`pedrad_ai.arxiv`); the other is
medRxiv, the clinical-medicine preprint server, which is not itself searchable
by keyword (``api.biorxiv.org`` only lists/details by DOI or date, no full-text
query). Europe PMC indexes medRxiv full text and exposes a keyword search
(https://www.ebi.ac.uk/europepmc/webservices/rest/search) that supports the
same boolean structure PubMed queries already use, so this module translates
and counts the same way :mod:`pedrad_ai.arxiv` does for arXiv.

Query syntax, settled empirically (2026-09-16):

* ``SRC:PPR`` restricts to preprints (Europe PMC's "PPR" source, distinct from
  ``MED``/PubMed, ``PMC``, etc.).
* ``PUBLISHER:"medRxiv"`` restricts the preprint set to medRxiv (bioRxiv is a
  different ``PUBLISHER`` value under the same ``SRC:PPR`` umbrella and is
  never matched here).
* ``TITLE:term`` / ``ABSTRACT:term`` are separate fields; there is no combined
  title+abstract field (``TITLE_ABSTRACT`` returns zero), so each query term is
  expanded to ``(TITLE:term OR ABSTRACT:term)``, mirroring arXiv's ``all:``.
* ``NOT`` works as a direct boolean operator (unlike the arXiv API, which needs
  ``ANDNOT``).
* ``*`` truncation works natively, but :func:`pedrad_ai.openalex.translate_pubmed_query`
  (reused for the boolean rewrite) already expands or strips truncation, so it
  is moot here; kept for parity with arXiv's translation path.
* ``PUB_YEAR:[start TO end]`` filters by publication year and matches
  ``FIRST_PDATE`` range filtering exactly for a same-year window, so the
  simpler ``PUB_YEAR`` form is used.

Validated against the headline queries: the pediatric radiology AI query
returns single digits to high twenties per year (2019-2026), and a spot check
of the 2024 hits (25 titles) was on-topic (e.g. "NeoCLIP: A Self-Supervised
Foundation Model for the Interpretation of Neonatal Radiographs", "Detection
of Pneumonia in Children through Chest Radiographs using Artificial
Intelligence") with no off-topic false positives noticed. The broad radiology
AI query returns roughly 150-350 per year over the same window, i.e. tens to
low hundreds, not thousands, consistent with medRxiv's much smaller size next
to arXiv.

No official rate limit is published for Europe PMC's REST API; this module
paces at the same conservative interval as :mod:`pedrad_ai.arxiv` and relies on
the same on-disk cache.
"""

from __future__ import annotations

import re
from typing import Any

from . import config, openalex, utils

API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
PAUSE = 1.0
_RETRIES = 6

_SOURCE_FILTER = 'SRC:PPR AND PUBLISHER:"medRxiv"'
_TERM_RE = re.compile(r'"[^"]+"|[A-Za-z][\w\'\-]*')
_KEYWORDS = {"AND", "OR", "NOT"}


def _get(params: dict[str, Any]) -> dict[str, Any]:
    """GET with a 429/5xx-aware retry schedule, like the other collectors."""
    import time
    import urllib.error

    last: Exception | None = None
    for attempt in range(_RETRIES):
        try:
            return utils.http_get_json(API, params, pause=PAUSE, max_retries=1, timeout=60)
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code not in (429, 500, 502, 503):
                raise
            time.sleep(10.0 * (attempt + 1))
        except Exception as exc:
            last = exc
            time.sleep(8.0 * (attempt + 1))
    assert last is not None
    raise last


def to_europepmc_query(pubmed_query: str) -> str:
    """PubMed boolean -> Europe PMC ``TITLE``/``ABSTRACT`` boolean.

    Reuses :func:`pedrad_ai.openalex.translate_pubmed_query` for the same
    field-tag stripping, MeSH-to-phrase and truncation handling as the arXiv
    translation, then wraps every bare term or quoted phrase as
    ``(TITLE:term OR ABSTRACT:term)``. Europe PMC supports ``NOT`` directly, so
    (unlike arXiv) no operator rewrite is needed.
    """
    s = openalex.translate_pubmed_query(pubmed_query)

    def _field(m: re.Match[str]) -> str:
        tok = m.group(0)
        if tok in _KEYWORDS:
            return tok
        return f"(TITLE:{tok} OR ABSTRACT:{tok})"

    s = _TERM_RE.sub(_field, s)
    return re.sub(r"\s+", " ", s).strip()


def count(query: str, start: int, end: int) -> int:
    """Number of medRxiv preprints matching ``query`` with ``PUB_YEAR`` in ``start``..``end``."""
    full_query = f"{_SOURCE_FILTER} AND ({query}) AND PUB_YEAR:[{start} TO {end}]"
    params = {"query": full_query, "format": "json", "resultType": "lite", "pageSize": 1}
    data = _get(params)
    return int(data.get("hitCount") or 0)


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
    """medRxiv counterpart of :func:`pubmed.crosstab` (same output shape)."""
    start = start or config.START_YEAR
    end = end or config.END_YEAR
    base = to_europepmc_query(base_query)
    rq = {r: to_europepmc_query(q) for r, q in rows.items()}
    cq = {c: to_europepmc_query(q) for c, q in cols.items()}
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
    """medRxiv counterpart of :func:`pubmed.problem_counts` (same shape)."""
    eras = eras or config.ERAS
    base = to_europepmc_query(base_query)
    out: dict[str, Any] = {"eras": [{"label": lab, "start": a, "end": b} for lab, a, b in eras], "totals": {}, "counts": {}}
    for lab, a, b in eras:
        out["totals"][lab] = count(base, a, b)
    for name, q in problems.items():
        tq = to_europepmc_query(q)
        out["counts"][name] = {lab: count(f"({base}) AND {tq}", a, b) for lab, a, b in eras}
    return out
