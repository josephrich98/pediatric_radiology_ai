#!/usr/bin/env python3
"""Recompute every number the review manuscript quotes, from the screened corpus.

Writes ``data/processed/review_stats.json`` and prints a readable summary. This
is the single source of truth for the manuscript's structured-review results, so
that a number in the text can always be traced to a rerun of this script.

The corpus is partitioned the way the PRISMA flow is (the rule itself lives in
``pedrad_ai.corpus``, so the exported table, the figures and the slides use the
same one):

* **conference** removed before screening by the publication-form criterion
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

from pedrad_ai import config, corpus

# What counts as a conference proceeding, what counts as a non-primary
# publication form, and therefore which stored records make up the corpus, is
# defined once in pedrad_ai.corpus and shared with the exported table
# (pedrad_ai.paper_db), the review figures and the slides.
is_conference = corpus.is_conference
is_nonprimary = corpus.is_nonprimary

# Topics that make an MRI study part of the developmental-neuroscience and
# child-psychiatry literature rather than of diagnostic radiology practice. Used
# only for the sensitivity analysis; nothing is excluded from the corpus on it.
# Two readings of "the developmental-neuroscience MRI literature", because the
# result is sensitive to which one is used and reporting only one would be
# choosing the answer. The narrow rule takes studies of an explicit
# neurodevelopmental or psychiatric diagnosis. The wide rule adds the methods
# and outcome vocabulary of cognitive neuroscience — resting-state and task
# fMRI, connectomics, brain age, cognitive and behavioral outcomes — which is
# the same literature approached by technique rather than by diagnosis.
NEURO_DIAGNOSIS = (
    r"autis|adhd|attention.deficit|psychiat|depressive|anxiet|schizophren|bipolar|"
    r"internali[sz]ing|externali[sz]ing|substance use|addiction|gaming disorder|"
    r"problematic gaming|neurodevelopmental disorder")
NEURO_WIDE = (
    NEURO_DIAGNOSIS + r"|neurodevelopment|depress|cognitiv|behaviou?ral|intelligence quotient|"
    r"language development|brain age|brain development|connectom|functional connectivity|"
    r"\bfmri\b|gaming|resting.state|executive function|intelligence score|emotion|temperament|"
    r"reward|abcd study|brain.behavio|neurocognit|developmental outcome|psychopatholog|puberty|"
    r"functional magnetic resonance|graph theor|social")
# Do not match bare "intelligence": "artificial intelligence" is present in
# many non-neuroscience titles and would inflate this sensitivity subset.
NEURO_RULES = {
    "diagnosis": (re.compile(NEURO_DIAGNOSIS, re.I),
                  "MRI studies naming an explicit neurodevelopmental or psychiatric diagnosis"),
    "diagnosis_or_neuroscience": (re.compile(NEURO_WIDE, re.I),
                                  "the same, plus MRI studies using cognitive-neuroscience methods "
                                  "(resting-state and task fMRI, connectomics, brain age) or "
                                  "reporting cognitive or behavioral outcomes"),
}


def multi(rows, field):
    c = collections.Counter()
    for r in rows:
        for v in [x.strip() for x in (r.get(field) or "").split(";") if x.strip()]:
            c[v] += 1
    return c


def pct(n, d):
    return round(100 * n / d, 1) if d else None


def main() -> None:
    store_path = config.PROCESSED_DIR / "pedrad_paper_db.json"
    csv_path = config.PROCESSED_DIR / "pedrad_paper_db.csv"
    if not store_path.exists():
        print("No paper database; run build_paper_db.py first.")
        return
    store = json.loads(store_path.read_text(encoding="utf-8"))
    raw = store.get("records", [])
    part = corpus.partition(list(raw.values()) if isinstance(raw, dict) else list(raw))
    recs, conference = part.screened, part.conference
    excluded, in_scope, nonprimary = part.excluded, part.in_scope, part.non_primary
    included_ids = {corpus.key(r) for r in part.included}

    # Composition is read off the exported CSV rather than the store, because
    # the CSV is what has the hand corrections applied. It is now written from
    # the same partition, so this is a join, not a second filter.
    with csv_path.open() as fh:
        included = [r for r in csv.DictReader(fh)
                    if (r.get("record_id") or r.get("pmid")) in included_ids]
    n = len(included)

    out = {
        "generated_on": __import__("datetime").date.today().isoformat(),
        "flow": part.counts,
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

    # Sensitivity analysis (post hoc; the rules were written after the corpus
    # existed, and the manuscript says so): what the modality mix looks like
    # without the developmental-neuroscience MRI literature. That literature is
    # eligible — it is machine learning applied to diagnostic MRI in children —
    # but it is also why this review ranks MRI first where reviews built on
    # narrower vocabulary rank radiography first, so the composition has to be
    # reported both ways.
    #
    # Both rules are run because the ranking turns on which one is used: under
    # the narrow rule MRI keeps a clear lead, under the wide one it falls level
    # with ultrasound. Reporting a single rule would be picking the answer. Each
    # is a keyword match over the extracted clinical problem, body region,
    # population, description and title, applied only to studies labelled MRI.
    out["sensitivity_neuro"] = {}
    for key, (pattern, description) in NEURO_RULES.items():
        neuro = [r for r in included
                 if "MRI" in (r.get("modality") or "") and pattern.search(
                     " ".join((r.get(k) or "") for k in
                              ("clinical_problem", "body_region", "patient_population",
                               "model_description", "title")))]
        ids = {corpus.key(r) for r in neuro}
        rest = [r for r in included if corpus.key(r) not in ids]
        mods = multi(rest, "modality")
        out["sensitivity_neuro"][key] = {
            "rule": description,
            "n_excluded": len(neuro),
            "n_remaining": len(rest),
            "modality": {k: {"n": v, "pct": pct(v, len(rest))} for k, v in mods.most_common(6)},
            "external_pct": pct(
                sum(1 for r in rest if r.get("validation") == "external / multi-center"), len(rest)),
        }

    # Which database each included study came from, and how the corpus looks
    # when it is restricted to work the field demonstrably engaged with. The
    # slides cannot name three and a half thousand studies, so they name the
    # high-impact subset; reporting its composition next to the whole corpus is
    # what shows whether that selection distorts the picture.
    out["by_search_source"] = corpus.counts_by_source(included)
    scored = [r for r in included if corpus.impact_value(r) is not None]
    top = corpus.high_impact(included)
    values = sorted(corpus.impact_value(r) for r in scored)
    out["impact"] = {
        "measure": "FWCI where OpenAlex has computed it, else iCite RCR; 1.0 = the average "
                   "paper of the same field and year",
        "n_scored": len(scored),
        "pct_scored": pct(len(scored), n),
        "by_measure": dict(collections.Counter(corpus.impact(r)[1] for r in scored)),
        "median": round(statistics.median(values), 2) if values else None,
        "q3": round(statistics.quantiles(values, n=4)[2], 2) if len(values) > 3 else None,
        "percentile": config.SLIDE_IMPACT_PERCENTILE,
        "floor": corpus.impact_threshold(included),
        "n_above_floor": len(top),
        "pct_above_floor": pct(len(top), n),
        "above_floor_by_source": corpus.counts_by_source(top),
        "above_floor_modality": {k: v for k, v in multi(top, "modality").most_common()},
        "above_floor_validation": dict(collections.Counter(
            r.get("validation") or "none / not stated" for r in top).most_common()),
        "above_floor_external_pct": pct(
            sum(1 for r in top if r.get("validation") == "external / multi-center"), len(top)),
        "above_floor_by_year": dict(sorted(collections.Counter(
            int(r["year"]) for r in top if str(r.get("year") or "").isdigit()).items())),
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
    ids = [corpus.key(r) for r in included]
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
    imp = out["impact"]
    print(f"sources: " + ", ".join(f"{k} {v:,}" for k, v in out["by_search_source"].items()))
    print(f"impact: {imp['n_scored']:,} scored ({imp['pct_scored']}%), median {imp['median']}, "
          f"top decile {imp['n_above_floor']:,} at or above {imp['floor']:g}x average "
          f"({imp['pct_above_floor']}%)")
    print(f"conference venues: {out['conference_venue_share']['n']} ({out['conference_venue_share']['pct']}%)")
    for key, sens in out["sensitivity_neuro"].items():
        print(f"without neuro MRI [{key}] (-{sens['n_excluded']}): n={sens['n_remaining']}, "
              + ", ".join(f"{k} {v['pct']}%" for k, v in list(sens["modality"].items())[:3])
              + f", external {sens['external_pct']}%")
    print("\n== era trajectory ==")
    for era, v in out["eras"].items():
        print(f"  {era}: n={v['n']:>4}  external {v['external_pct']}%  reader {v['reader_pct']}%  "
              f"prospective {v['prospective_pct']}%  multi-center {v['multi_center_pct']}%  "
              f"commercial {v['commercial_pct']}%")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
