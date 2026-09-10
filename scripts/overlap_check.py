#!/usr/bin/env python3
"""External recall check against an independently assembled corpus.

The strongest validation available for a search strategy is whether it retrieves
the studies that other reviewers, working independently, judged eligible. This
resolves the 789 articles included in Kamran et al.'s scoping review
(Pediatr Radiol 2026) to PMIDs by title, then asks two questions:

1. **Search recall** — what share of those 789 does ``config.REVIEW_QUERY``
   retrieve? A record the search never returns cannot be recovered at screening,
   so this is the number that bounds the review.
2. **Screening agreement** — of the records retrieved, how many did our screen
   also judge eligible? Two independent reviews disagreeing about eligibility is
   a different problem from a search that never saw the paper, and the two must
   not be conflated.

Their search ran to August 2024, so records our search retrieves but they did
not include are not necessarily errors on either side.

Usage:
    python scripts/overlap_check.py --articles <parsed.json>
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from pedrad_ai import config, pubmed

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


STOP = {"the","and","for","with","from","using","use","based","study","data","that","this","are",
        "was","were","its","into","via","new","novel","among","between","after","before","during"}


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def tokens(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]{4,}", (t or "").lower()) if w not in STOP}


def _esearch(term: str, retmax: int = 8) -> list[str] | None:
    """PMIDs for a term, or None when the request itself failed.

    The distinction matters: a failed request is not evidence that a paper is
    absent from PubMed, and conflating the two silently understates recall.
    """
    params = {"db": "pubmed", "term": term, "retmax": str(retmax), "retmode": "json",
              "email": config.CONTACT_EMAIL}
    if config.NCBI_API_KEY:
        params["api_key"] = config.NCBI_API_KEY
    url = ESEARCH + "?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)["esearchresult"].get("idlist", [])
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None


def resolve(title: str) -> tuple[str | None, str]:
    """(PMID, status) for a reference-list title.

    PubMed's ``[Title]`` *phrase* match fails whenever the stored title differs
    by a character, and an *unfielded* word search returns date-sorted noise
    (thousands of matches, the right one nowhere near the top). What works is a
    title-FIELDED word AND: precise enough to land on the paper, loose enough to
    survive punctuation differences. The candidate is then verified by token
    overlap, so a loose search cannot produce a false match.
    """
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9\-]{3,}", title)
             if w.lower() not in STOP]
    if len(words) < 3:
        return None, "title too short to resolve"
    ids = None
    for n in (8, 5, 4):
        got = _esearch(" AND ".join(f"{w}[Title]" for w in words[:n]), retmax=20)
        if got is None:
            return None, "request failed"
        if got:
            ids = got
            break
    if not ids:
        return None, "no PubMed record"
    want = tokens(title)
    best, best_score = None, 0.0
    for a in pubmed.article_details(ids[:20]):
        got_t = tokens(a.get("title", ""))
        if not got_t:
            continue
        score = len(want & got_t) / max(1, len(want | got_t))
        if score > best_score:
            best, best_score = a["pmid"], score
    if best and best_score >= 0.6:
        return best, "resolved"
    return None, f"no confident match (best Jaccard {best_score:.2f})"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--articles", required=True, help="parsed supplement JSON")
    ap.add_argument("--out", default=str(config.PROCESSED_DIR / "overlap_check.json"))
    args = ap.parse_args()

    arts = json.loads(Path(args.articles).read_text(encoding="utf-8"))
    print(f"Resolving {len(arts)} titles to PMIDs (paced under the NCBI limit)...")
    pause = 0.12 if config.NCBI_API_KEY else 0.36
    for i, a in enumerate(arts, 1):
        a["pmid"], a["status"] = resolve(a["title"])
        time.sleep(pause)
        if i % 100 == 0:
            got = sum(1 for x in arts[:i] if x["pmid"])
            print(f"  {i}/{len(arts)}  resolved {got}", flush=True)
    resolved = [a for a in arts if a["pmid"]]
    print(f"Resolved {len(resolved)}/{len(arts)} to PMIDs")

    # Membership in our search, tested in batches of UID terms.
    print("Testing membership in config.REVIEW_QUERY...")
    retrieved: set[str] = set()
    pmids = [a["pmid"] for a in resolved]
    for i in range(0, len(pmids), 100):
        chunk = pmids[i:i + 100]
        uids = " OR ".join(f"{p}[uid]" for p in chunk)
        hit = pubmed.pmids_for_query(f"({config.REVIEW_QUERY}) AND ({uids})") \
            if hasattr(pubmed, "pmids_for_query") else None
        if hit is None:
            # Fall back to counting one at a time (slower but always available)
            for p in chunk:
                if pubmed.count_for_query(f"({config.REVIEW_QUERY}) AND {p}[uid]"):
                    retrieved.add(p)
        else:
            retrieved.update(hit)
        print(f"  {min(i+100, len(pmids))}/{len(pmids)}")

    store = json.loads((config.PROCESSED_DIR / "pedrad_paper_db.json").read_text(encoding="utf-8"))
    recs = store.get("records", [])
    recs = list(recs.values()) if isinstance(recs, dict) else recs
    screened = {r.get("pmid"): bool(r.get("include")) for r in recs if r.get("pmid")}

    n = len(resolved)
    n_ret = sum(1 for p in pmids if p in retrieved)
    in_store = [p for p in pmids if p in screened]
    incl = [p for p in in_store if screened[p]]

    misses = [a for a in resolved if a["pmid"] not in retrieved]
    unresolved = [a for a in arts if not a["pmid"]]

    import collections
    status_counts = dict(collections.Counter(a.get("status", "?") for a in arts))
    out = {
        "n_articles": len(arts),
        "resolution_status": status_counts,
        "n_resolved_to_pmid": n,
        "n_retrieved_by_our_search": n_ret,
        "search_recall": round(n_ret / n, 4) if n else None,
        "n_reaching_our_screen": len(in_store),
        "n_our_screen_included": len(incl),
        "screen_agreement_on_their_includes": round(len(incl) / len(in_store), 4) if in_store else None,
        "misses": [{"n": a["n"], "pmid": a["pmid"], "title": a["title"]} for a in misses],
        "unresolved_titles": [{"n": a["n"], "title": a["title"]} for a in unresolved],
    }
    Path(args.out).write_text(json.dumps(out, indent=2))

    print(f"\n{'='*66}")
    print("Resolution status:", json.dumps(status_counts))
    print(f"Their included articles          : {len(arts)}")
    print(f"Resolved to a PubMed record      : {n}")
    print(f"Retrieved by our search          : {n_ret}  ({100*n_ret/n:.1f}% search recall)")
    print(f"Reaching our screen              : {len(in_store)}")
    print(f"Our screen also judged eligible  : {len(incl)}"
          + (f"  ({100*len(incl)/len(in_store):.1f}%)" if in_store else ""))
    print(f"{'='*66}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
