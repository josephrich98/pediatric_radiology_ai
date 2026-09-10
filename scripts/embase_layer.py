"""Parse the Embase exports, deduplicate them against the PubMed corpus, and
summarize what the Embase layer would add to the review.

Embase is exported from embase.com in its labelled-field CSV format (one
``"FIELD","value"`` line per field, records separated by blank lines) — not as a
table. See ``reports/06_search_strategy.md`` section 4.3 for the query and the
export field list.

Two files are read from ``data/raw/embase/``:

    embase_unique.csv            #4 NOT [medline]/lim  — the candidate new records
    embase_medline_overlap.csv   #4 AND [medline]/lim  — a recall audit of REVIEW_QUERY

The central correction this script exists to enforce: ``[medline]/lim`` flags
records that are *MEDLINE-indexed*, which is not the same as "in PubMed". PubMed
also carries a large PubMed-Central-only population (MDPI, Frontiers, NIH-pilot
preprint deposits) that Embase reports as non-MEDLINE and that the review
already holds. Novelty is therefore decided by resolving each DOI to a PMID
through the NCBI ID converter and testing membership in the stored REVIEW_QUERY
PMID set — never by trusting the Embase flag.

    python scripts/embase_layer.py --pmids           # refresh the REVIEW_QUERY PMID set
    python scripts/embase_layer.py                   # parse, dedupe, summarize
    python scripts/embase_layer.py --screen <dir>    # fold in screening decisions
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import time
import urllib.parse
import urllib.request

from pedrad_ai import config, pubmed

csv.field_size_limit(10_000_000)

RAW = pathlib.Path("data/raw/embase")
OUT = pathlib.Path("data/processed")
PMID_SET = OUT / "review_query_pmids.json"
IDCONV = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"

NEW = ("outside PubMed", "no DOI (cannot check)")


def parse_export(path: pathlib.Path) -> list[dict]:
    """Embase's labelled-field CSV -> one dict per record."""
    recs: list[dict] = []
    cur: dict = {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for row in csv.reader(fh):
            if not row or not row[0].strip():
                if cur:
                    recs.append(cur)
                    cur = {}
                continue
            key, vals = row[0].strip(), row[1:]
            val = vals[0] if len(vals) == 1 else [v for v in vals if v.strip()]
            if key in cur:
                if not isinstance(cur[key], list):
                    cur[key] = [cur[key]]
                cur[key].append(val)
            else:
                cur[key] = val
    if cur:
        recs.append(cur)
    return recs


def _one(v) -> str:
    if isinstance(v, list):
        return str(v[0]) if v else ""
    return str(v or "")


def _joined(v) -> str:
    if isinstance(v, list):
        return "; ".join(str(x) for x in v if str(x).strip())
    return str(v or "")


def flatten(recs: list[dict], prefix: str) -> list[dict]:
    return [
        {
            "id": f"{prefix}{i:05d}",
            "title": _one(r.get("TITLE")),
            "journal": _one(r.get("SOURCE TITLE")),
            "year": _one(r.get("PUBLICATION YEAR")),
            "embase_type": _joined(r.get("PUBLICATION TYPE")).split(";")[0].strip(),
            "language": _joined(r.get("LANGUAGE OF ARTICLE")),
            "doi": _one(r.get("DOI")),
            "pmid": _one(r.get("MEDLINE PMID")).split("http")[0].strip(),
            "abstract": _joined(r.get("ABSTRACT")),
        }
        for i, r in enumerate(recs)
    ]


def review_pmids(refresh: bool = False) -> set[str]:
    """Every PMID REVIEW_QUERY returns, cached on disk."""
    if PMID_SET.exists() and not refresh:
        return {str(p) for p in json.loads(PMID_SET.read_text())}
    got: list[str] = []
    for year in range(config.REVIEW_START_YEAR, config.END_YEAR + 1):
        ids = pubmed.pmids_for_year(config.REVIEW_QUERY, year, retmax=10000)
        got.extend(ids)
        print(f"  {year} {len(ids)}", flush=True)
    got = sorted(set(got))
    PMID_SET.write_text(json.dumps(got))
    print(f"  REVIEW_QUERY -> {len(got)} unique PMIDs")
    return set(got)


def resolve_dois(rows: list[dict]) -> dict[str, str]:
    """DOI -> PMID via the NCBI ID converter, 180 at a time.

    The converter returns ``pmid`` as a JSON number; coercing to str here is
    load-bearing, since the caller compares against a set of strings.
    """
    todo = [r for r in rows if r["doi"]]
    mapping: dict[str, str] = {}
    for i in range(0, len(todo), 180):
        chunk = todo[i : i + 180]
        query = urllib.parse.urlencode(
            {
                "ids": ",".join(r["doi"] for r in chunk),
                "format": "json",
                "tool": "pedrad_ai",
                "email": config.CONTACT_EMAIL,
            }
        )
        for attempt in range(4):
            try:
                with urllib.request.urlopen(f"{IDCONV}?{query}", timeout=60) as fh:
                    data = json.loads(fh.read())
                break
            except Exception as exc:  # transient; the converter rate-limits
                print(f"  retry ({exc})")
                time.sleep(3 * (attempt + 1))
        else:
            print(f"  chunk at {i} failed, skipped")
            continue
        for rec in data.get("records", []):
            if rec.get("doi") and rec.get("pmid"):
                mapping[rec["doi"].lower()] = str(rec["pmid"])
        print(f"  {min(i + 180, len(todo))}/{len(todo)} resolved {len(mapping)}", flush=True)
        time.sleep(0.4)
    return mapping


def classify(rows: list[dict], mapping: dict[str, str], ours: set[str]) -> None:
    for r in rows:
        if not r["doi"]:
            r["status"] = "no DOI (cannot check)"
            continue
        pm = mapping.get(r["doi"].lower().strip())
        if not pm:
            r["status"] = "outside PubMed"
        else:
            r["resolved_pmid"] = pm
            r["status"] = "already in our corpus" if pm in ours else "in PubMed, not retrieved"


def audit_overlap(rows: list[dict], ours: set[str]) -> dict:
    """Recall of REVIEW_QUERY against the MEDLINE-indexed half of the Embase run."""
    with_pmid = [r for r in rows if r["pmid"]]
    hit = [r for r in with_pmid if r["pmid"] in ours]
    miss = [r for r in with_pmid if r["pmid"] not in ours]
    return {
        "records": len(rows),
        "carrying_a_pmid": len(with_pmid),
        "retrieved_by_review_query": len(hit),
        "recall": round(len(hit) / len(with_pmid), 4) if with_pmid else None,
        "missed": [
            {k: r[k] for k in ("pmid", "year", "embase_type", "journal", "title")} for r in miss
        ],
        "retrieved_by_us_but_not_by_embase": len(ours - {r["pmid"] for r in with_pmid}),
    }


def load_screen(directory: pathlib.Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for f in sorted(directory.glob("*.json")):
        data = json.loads(f.read_text())
        if isinstance(data, dict):
            data = data.get("results") or list(data.values())
        for d in data:
            out.setdefault(d["id"], d)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pmids", action="store_true", help="refresh the REVIEW_QUERY PMID set")
    ap.add_argument("--screen", type=pathlib.Path, help="directory of screening result JSON files")
    args = ap.parse_args()

    ours = review_pmids(refresh=args.pmids)
    print(f"REVIEW_QUERY PMID set: {len(ours)}")

    uniq = flatten(parse_export(RAW / "embase_unique.csv"), "E")
    over = flatten(parse_export(RAW / "embase_medline_overlap.csv"), "M")
    print(f"Embase-unique (#5): {len(uniq)}   MEDLINE overlap (#6): {len(over)}")

    print("Resolving DOIs to PMIDs...")
    classify(uniq, resolve_dois(uniq), ours)

    by_type: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in uniq:
        by_type[r["embase_type"]][r["status"]] += 1

    summary = {
        "generated_on": time.strftime("%Y-%m-%d"),
        "review_query_records": len(ours),
        "embase_unique_records": len(uniq),
        "embase_medline_overlap_records": len(over),
        "unique_by_type_and_status": {k: dict(v) for k, v in by_type.items()},
        "status_totals": dict(collections.Counter(r["status"] for r in uniq)),
        "recall_audit": audit_overlap(over, ours),
    }

    if args.screen:
        screen = load_screen(args.screen)
        strata: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        for r in uniq:
            d = screen.get(r["id"])
            if not d:
                continue
            k = r["embase_type"]
            strata[k]["screened"] += 1
            if r["status"] in NEW:
                strata[k]["new_screened"] += 1
                if d.get("include"):
                    strata[k]["new_eligible"] += 1
                    if d.get("record_kind") == "primary study":
                        strata[k]["new_primary"] += 1
                    if d.get("substantive"):
                        strata[k]["new_substantive"] += 1
        # project sampled strata up to their full population
        pop = collections.Counter(r["embase_type"] for r in uniq)
        newpop = collections.Counter(r["embase_type"] for r in uniq if r["status"] in NEW)
        for k, c in strata.items():
            if c["new_screened"]:
                f = newpop[k] / c["new_screened"]
                c["projected_new_eligible"] = round(c["new_eligible"] * f)
                c["projected_new_primary"] = round(c["new_primary"] * f)
            c["population"] = pop[k]
            c["new_population"] = newpop[k]
        summary["screening"] = {k: dict(v) for k, v in strata.items()}

    (OUT / "embase_layer.json").write_text(json.dumps(summary, indent=1))
    (OUT / "embase_unique_rows.json").write_text(
        json.dumps([{k: v for k, v in r.items() if k != "abstract"} for r in uniq], indent=1)
    )
    print(f"\nwrote {OUT/'embase_layer.json'} and {OUT/'embase_unique_rows.json'}")
    print(json.dumps(summary["status_totals"], indent=1))
    print("recall audit:", summary["recall_audit"]["recall"])


if __name__ == "__main__":
    main()
