#!/usr/bin/env python3
"""Recompute every number the review manuscript quotes, from the screened corpus.

Writes ``data/processed/review_stats.json`` and prints a readable summary. This
is the single source of truth for the manuscript's structured-review results, so
that a number in the text can always be traced to a rerun of this script.

The corpus is partitioned the way the PRISMA flow is:

* **screened**   every record read
* **excluded**   screened out as not pediatric radiology AI
* **non-primary** in scope but a review, editorial, comment or guideline: kept in
  the store (they are part of the literature) but reported separately, because
  the eligibility criteria admit primary research only
* **included**   primary studies — the corpus every composition and rigor number
  below is computed on

Usage:
    python scripts/review_stats.py
"""
from __future__ import annotations

import collections
import csv
import json
import re
import statistics

from pedrad_ai import config

# PubMed publication types that make a record non-primary. `Review` alone is not
# enough — PubMed types Nature Protocols articles and society white papers as
# Review — so a record is non-primary only when its own extracted study_design
# also reads as a review, or when the type is unambiguous.
NONPRIMARY_TYPES = {"Editorial", "Comment", "Letter", "News", "Published Erratum",
                    "Retraction of Publication", "Retracted Publication", "Practice Guideline",
                    "Guideline", "Consensus Development Conference"}
NONPRIMARY_DESIGN = re.compile(
    r"\b(narrative review|systematic review|scoping review|literature review|state-of-the-art review|"
    r"review article|editorial|commentary|consensus statement|position statement|white paper|"
    r"multi-society|perspective|opinion)\b", re.I)


# Conference proceedings are outside the review's publication-form criterion
# (search strategy Section 4.4): they cannot support judgements about study
# design, most are not extractable, and unlike preprints they carry no DOI
# linking them to the later full paper, so deduplication cannot resolve the
# double count. The paper database keeps them for the venue analysis; the
# review corpus does not. Detected from the venue string, because the row
# itself does not record a publication form.
CONFERENCE_VENUE = re.compile(
    r"lecture notes in computer science|proceedings|symposium|conference|workshop|"
    r"\bisbi\b|\bspie\b|\bmiccai\b|\bcvpr\b|\biccv\b|\beccv\b|\bneurips\b|\bmidl\b|"
    r"\bipmi\b|\bembc\b|\bicip\b|\baaai\b|communications in computer and information science",
    re.I,
)


def is_conference(row) -> bool:
    """True when the row's venue is a conference proceedings volume."""
    return bool(CONFERENCE_VENUE.search(str(row.get("journal") or "")))


def multi(rows, field):
    c = collections.Counter()
    for r in rows:
        for v in [x.strip() for x in (r.get(field) or "").split(";") if x.strip()]:
            c[v] += 1
    return c


def pct(n, d):
    return round(100 * n / d, 1) if d else None


def is_nonprimary(row) -> bool:
    design = row.get("study_design") or ""
    if NONPRIMARY_DESIGN.search(design):
        return True
    types = row.get("publication_types") or []
    if isinstance(types, str):
        types = [t.strip(" '\"[]") for t in types.split(",")]
    return bool(NONPRIMARY_TYPES & set(types))


def main() -> None:
    store_path = config.PROCESSED_DIR / "pedrad_paper_db.json"
    csv_path = config.PROCESSED_DIR / "pedrad_paper_db.csv"
    if not store_path.exists():
        print("No paper database; run build_paper_db.py first.")
        return
    store = json.loads(store_path.read_text(encoding="utf-8"))
    raw = store.get("records", [])
    recs = list(raw.values()) if isinstance(raw, dict) else list(raw)
    # PubMed publication types are not stored on the row; they come from the
    # worklist the screener read. Absent that file, study_design alone decides.
    pubtypes: dict[str, list] = {}
    wl = config.PROCESSED_DIR / "review_worklist.json"
    if wl.exists():
        for pap in json.loads(wl.read_text(encoding="utf-8"))["papers"]:
            pubtypes[pap["pmid"]] = pap.get("publication_types") or []
    for r in recs:
        r.setdefault("publication_types", pubtypes.get(r.get("pmid"), []))
    with csv_path.open() as fh:
        rows = list(csv.DictReader(fh))

    screened_all = len(recs)
    conference = [r for r in recs if is_conference(r)]
    conference_ids = {r.get("pmid") or r.get("record_id") for r in conference}
    recs = [r for r in recs if (r.get("pmid") or r.get("record_id")) not in conference_ids]
    rows = [r for r in rows if (r.get("pmid") or r.get("record_id")) not in conference_ids]

    excluded = [r for r in recs if not r.get("include")]
    in_scope = [r for r in recs if r.get("include")]
    nonprimary = [r for r in in_scope if is_nonprimary(r)]
    nonprimary_ids = {r.get("pmid") or r.get("record_id") for r in nonprimary}
    included = [r for r in rows
                if (r.get("pmid") or r.get("record_id")) not in nonprimary_ids]
    n = len(included)

    out = {
        "generated_on": __import__("datetime").date.today().isoformat(),
        "flow": {
            "screened_all_sources": screened_all,
            "screened": len(recs),
            "excluded_screening": len(excluded),
            "in_scope": len(in_scope),
            "conference_excluded": len(conference),
            "non_primary": len(nonprimary),
            "included": n,
        },
        "exclusion_reasons": dict(collections.Counter(
            (r.get("exclusion_reason") or "not stated").strip().lower()[:60]
            for r in excluded).most_common(15)),
    }

    def block(label, counter, denom=n, multilabel=True):
        out[label] = {k: {"n": v, "pct": pct(v, denom)} for k, v in counter.most_common()}

    block("modality", multi(included, "modality"))
    block("task", multi(included, "task"))
    block("age_groups", multi(included, "age_groups"))
    block("validation", collections.Counter(r.get("validation") or "none / not stated" for r in included))
    block("data_source", collections.Counter(r.get("data_source") or "not stated" for r in included))
    block("release_status", collections.Counter(r.get("release_status") or "unclear" for r in included))
    block("body_region", collections.Counter((r.get("body_region") or "not stated").strip().lower() for r in included))

    # Fetal / perinatal share, the review's headline composition claim.
    fetal = [r for r in included
             if "fetal" in (r.get("age_groups") or "")
             or re.search(r"fetal|fetus|placenta|prenatal", (r.get("body_region") or ""), re.I)]
    out["fetal"] = {
        "n": len(fetal), "pct": pct(len(fetal), n),
        "modality": dict(multi(fetal, "modality").most_common()),
        "task": dict(multi(fetal, "task").most_common()),
    }

    # The translational funnel.
    code = [r for r in included if (r.get("code_url") or "").strip()]
    out["funnel"] = {
        "included": n,
        "external_or_multicenter": {"n": sum(1 for r in included if r.get("validation") == "external / multi-center")},
        "reader_study": {"n": sum(1 for r in included if r.get("validation") == "reader study")},
        "prospective": {"n": sum(1 for r in included if r.get("validation") == "prospective")},
        "code_available": {"n": len(code)},
        "open_source": {"n": sum(1 for r in included if r.get("release_status") == "open-source")},
        "commercial": {"n": sum(1 for r in included if r.get("release_status") == "commercial")},
        "named_model": {"n": sum(1 for r in included if (r.get("model_name") or "").strip())},
    }
    for k, v in out["funnel"].items():
        if isinstance(v, dict):
            v["pct"] = pct(v["n"], n)

    # Era trajectory.
    eras = [(2005, 2014), (2015, 2019), (2020, 2022), (2023, config.END_YEAR)]
    out["eras"] = {}
    for lo, hi in eras:
        sub = [r for r in included if str(r.get("year") or "").isdigit() and lo <= int(r["year"]) <= hi]
        if not sub:
            continue
        v = collections.Counter(r.get("validation") or "none / not stated" for r in sub)
        d = collections.Counter(r.get("data_source") or "not stated" for r in sub)
        rel = collections.Counter(r.get("release_status") or "unclear" for r in sub)
        out["eras"][f"{lo}-{hi}"] = {
            "n": len(sub),
            "external_pct": pct(v.get("external / multi-center", 0), len(sub)),
            "reader_pct": pct(v.get("reader study", 0), len(sub)),
            "prospective_pct": pct(v.get("prospective", 0), len(sub)),
            "internal_only_pct": pct(v.get("internal only", 0), len(sub)),
            "none_stated_pct": pct(v.get("none / not stated", 0), len(sub)),
            "multi_center_pct": pct(d.get("multi center", 0), len(sub)),
            "single_center_pct": pct(d.get("single center", 0), len(sub)),
            "open_source_pct": pct(rel.get("open-source", 0), len(sub)),
            "commercial_pct": pct(rel.get("commercial", 0), len(sub)),
            "unclear_pct": pct(rel.get("unclear", 0), len(sub)),
        }

    out["by_year"] = dict(sorted(collections.Counter(
        int(r["year"]) for r in included if str(r.get("year") or "").isdigit()).items()))
    out["top_venues"] = dict(collections.Counter(
        (r.get("journal") or "not stated") for r in included).most_common(25))

    conf = re.compile(r"lecture notes|proceedings|ISBI|MICCAI|IPMI|SPIE|conference|symposium|workshop|CVPR|NeurIPS", re.I)
    out["conference_venue_share"] = {
        "n": sum(1 for r in included if conf.search(r.get("journal") or "")),
        "pct": pct(sum(1 for r in included if conf.search(r.get("journal") or "")), n)}

    sizes = []
    for r in included:
        m = re.findall(r"(\d[\d,]{2,})", (r.get("dataset_size") or "").replace(" ", ""))
        if m:
            sizes.append(max(int(x.replace(",", "")) for x in m))
    out["dataset_size"] = {
        "n_reported": len(sizes),
        "pct_reported": pct(len(sizes), n),
        "median": statistics.median(sizes) if sizes else None,
        "q1": round(statistics.quantiles(sizes, n=4)[0]) if len(sizes) > 3 else None,
        "q3": round(statistics.quantiles(sizes, n=4)[2]) if len(sizes) > 3 else None,
    }


    # The PRISMA figure reads this file. Emitting it here — rather than keeping a
    # hand-written copy — is what stops the diagram from quoting a corpus size the
    # rest of the manuscript no longer uses.
    embase = {}
    emb_path = config.PROCESSED_DIR / "embase_layer.json"
    if emb_path.exists():
        embase = json.loads(emb_path.read_text(encoding="utf-8"))
    pmids = config.PROCESSED_DIR / "review_query_pmids.json"
    n_pubmed = len(json.loads(pmids.read_text(encoding="utf-8"))) if pmids.exists() else 0
    st = embase.get("status_totals", {})
    n_emb_dupe = st.get("already in our corpus", 0)
    n_conf_embase = sum((embase.get("set_aside") or {}).values())

    # PRISMA requires identification -> removal -> screening to balance. Build the
    # removal box as (everything identified) - (everything screened), enumerate the
    # components we can name, and carry any remainder explicitly rather than
    # letting the diagram quietly fail to add up.
    identified = {}
    if n_pubmed:
        identified["PubMed/MEDLINE"] = n_pubmed
    n_emb_total = (embase.get("embase_unique_all_types") or 0) + (
        embase.get("embase_medline_overlap_records") or 0)
    if n_emb_total:
        identified["Embase"] = n_emb_total
    n_legacy = sum(1 for r in recs if r.get("source") == "openalex") + \
               sum(1 for r in conference if r.get("source") == "openalex")
    if n_legacy:
        identified["OpenAlex (earlier build)"] = n_legacy

    total_removed = sum(identified.values()) - len(recs)
    removed = {}
    if embase.get("embase_medline_overlap_records"):
        removed["duplicate of the PubMed layer"] = (
            embase["embase_medline_overlap_records"] + n_emb_dupe)
    if n_conf_embase or conference:
        removed["conference abstracts and proceedings"] = n_conf_embase + len(conference)
    remainder = total_removed - sum(removed.values())
    if remainder:
        removed["other duplicates and unresolved records"] = remainder

    flow_doc = {
        "identified": identified,
        "removed_before_screening": removed,
        "screened": len(recs),
        "excluded_screening": {
            "adult-only, non-radiologic, or no AI/ML component": len(excluded)},
        "eligible": len(in_scope),
        "excluded_eligibility": {
            "review, editorial, guideline or position statement": len(nonprimary)},
        "included": n,
        "note": ("PubMed and Embase layers complete (2005-2026). Conference material is "
                 "retrieved and reported but excluded by the publication-form criterion."),
    }
    (config.PROCESSED_DIR / "review_flow.json").write_text(
        json.dumps(flow_doc, indent=1), encoding="utf-8")

    path = config.PROCESSED_DIR / "review_stats.json"
    path.write_text(json.dumps(out, indent=2))
    # The figures must draw the same set these numbers describe: primary studies
    # only, with reviews and editorials removed. Export the ids rather than
    # re-deriving the rule in two places.
    ids = [(r.get("pmid") or r.get("record_id")) for r in included]
    (config.PROCESSED_DIR / "review_included_ids.json").write_text(json.dumps(ids))

    f = out["flow"]
    print(f"\nPRISMA: {f['screened']:,} screened -> {f['excluded_screening']:,} excluded "
          f"-> {f['non_primary']:,} non-primary -> {f['included']:,} included\n")
    for key in ("modality", "task", "age_groups", "validation", "data_source", "release_status"):
        print(f"== {key} ==")
        for k, v in list(out[key].items())[:9]:
            print(f"   {k:<34} {v['n']:>5}  {v['pct']}%")
        print()
    print(f"fetal/perinatal: {out['fetal']['n']} ({out['fetal']['pct']}%)")
    print(f"conference venues: {out['conference_venue_share']['n']} ({out['conference_venue_share']['pct']}%)")
    print("\n== era trajectory ==")
    for era, v in out["eras"].items():
        print(f"  {era}: n={v['n']:>4}  external {v['external_pct']}%  reader {v['reader_pct']}%  "
              f"prospective {v['prospective_pct']}%  multi-center {v['multi_center_pct']}%  "
              f"commercial {v['commercial_pct']}%")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
