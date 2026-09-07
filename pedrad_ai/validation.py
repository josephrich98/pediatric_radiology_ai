"""Is the radiology-AI query sufficient? Recall, precision proxy, term audit.

Three checks, all reproducible from PubMed alone:

1. **Recall** against :data:`config.GOLD_PAPERS`, a hand-picked set of
   landmark radiology-AI papers. Each DOI is resolved to a PMID and tested for
   membership in the broad query (and, for pediatric entries, the pediatric
   query). A sufficient query should retrieve nearly all of them.
2. **Precision proxy**: the count under a strict title/abstract-only variant of
   the same query, as a share of the broad (MeSH-expanded) count, plus a
   sample of "broad-only" records so a reader can see what the expansion
   adds (mostly MeSH-indexed papers whose abstracts use other wording).
3. **Term audit**: PubMed's automatic translation of each single-word term, to
   catch expansions like ``ultrasound`` -> "diagnostic imaging" subheading.
"""

from __future__ import annotations

import datetime as _dt
import json
import urllib.parse
from typing import Any

from . import config, pubmed, utils

_AUDIT_TERMS = ["ultrasound", "CT", "MRI", "radiology", "tomography", "radiomics", "neural network"]


def recall_check() -> dict[str, Any]:
    rows = []
    for g in config.GOLD_PAPERS:
        pmid = pubmed.pmid_for_doi(g["doi"])
        row = {"doi": g["doi"], "label": g["label"], "pediatric": bool(g.get("pediatric")), "pmid": pmid}
        if pmid:
            row["in_radiology_ai"] = pubmed.query_contains(config.QUERIES["radiology_ai"], pmid)
            if row["pediatric"]:
                row["in_pediatric_radiology_ai"] = pubmed.query_contains(config.QUERIES["pediatric_radiology_ai"], pmid)
        rows.append(row)
    indexed = [r for r in rows if r["pmid"]]
    hit = [r for r in indexed if r.get("in_radiology_ai")]
    ped = [r for r in indexed if r["pediatric"]]
    ped_hit = [r for r in ped if r.get("in_pediatric_radiology_ai")]
    return {
        "rows": rows,
        "n_gold": len(rows),
        "n_indexed": len(indexed),
        "n_retrieved": len(hit),
        "recall": round(len(hit) / len(indexed), 3) if indexed else None,
        "n_pediatric_indexed": len(ped),
        "n_pediatric_retrieved": len(ped_hit),
        "pediatric_recall": round(len(ped_hit) / len(ped), 3) if ped else None,
        "missed": [r["label"] for r in indexed if not r.get("in_radiology_ai")],
        "pediatric_missed": [r["label"] for r in ped if not r.get("in_pediatric_radiology_ai")],
    }


def precision_check(year: int | None = None, n_sample: int = 40) -> dict[str, Any]:
    year = year or (config.PARTIAL_YEAR - 1)
    out: dict[str, Any] = {"year": year, "series": {}}
    for name in ("radiology_ai", "pediatric_radiology_ai"):
        broad = pubmed.count_for_query(config.QUERIES[name], year)
        strict = pubmed.count_for_query(config.STRICT_QUERIES[name], year)
        both = pubmed.count_for_query(f"({config.QUERIES[name]}) AND ({config.STRICT_QUERIES[name]})", year)
        out["series"][name] = {
            "broad": broad, "strict": strict, "strict_in_broad": both,
            "strict_share_of_broad": round(both / broad, 3) if broad else None,
            "strict_not_in_broad": strict - both,
        }
    # What does the MeSH expansion add? Sample records in broad but not strict.
    q = f"({config.QUERIES['radiology_ai']}) NOT ({config.STRICT_QUERIES['radiology_ai']})"
    pmids = pubmed.sample_pmids(q, year, n=n_sample)
    arts = pubmed.article_details(pmids[:n_sample])
    out["broad_only_sample"] = [{"pmid": a["pmid"], "title": a["title"], "journal": a["journal"]} for a in arts]
    # And a sample of the strict set, as the "clearly on-topic" reference.
    pmids = pubmed.sample_pmids(config.STRICT_QUERIES["radiology_ai"], year, n=n_sample // 2)
    arts = pubmed.article_details(pmids[: n_sample // 2])
    out["strict_sample"] = [{"pmid": a["pmid"], "title": a["title"], "journal": a["journal"]} for a in arts]
    return out


def term_audit() -> list[dict[str, str]]:
    rows = []
    pause = 0.12 if config.NCBI_API_KEY else 0.34
    for term in _AUDIT_TERMS:
        params = pubmed._base_params()
        params.update({"term": term, "retmax": 0, "retmode": "json"})
        try:
            d = utils.http_get_json(pubmed.ESEARCH, params, pause=pause)["esearchresult"]
            rows.append({"term": term, "translation": d.get("querytranslation", ""), "count": d.get("count")})
        except Exception as exc:
            rows.append({"term": term, "translation": f"(failed: {exc})", "count": None})
    return rows


def run() -> dict[str, Any]:
    print("  recall against gold papers...")
    rec = recall_check()
    print(f"    {rec['n_retrieved']}/{rec['n_indexed']} retrieved; pediatric {rec['n_pediatric_retrieved']}/{rec['n_pediatric_indexed']}")
    print("  strict vs broad counts + samples...")
    prec = precision_check()
    print("  term-mapping audit...")
    audit = term_audit()
    return {"collected_on": _dt.date.today().isoformat(), "recall": rec, "precision": prec, "term_audit": audit}
