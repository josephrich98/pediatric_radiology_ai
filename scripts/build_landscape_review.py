#!/usr/bin/env python3
"""Offline landscape analysis of the shared review cohort; no re-screening.

Run with PYTHONPATH=. after review_stats.py. Produces an auditable topic/resource mention table,
JSON counts, supplementary tables, and three manuscript figures (PNG + PDF).
Rules are exploratory text matches, not adjudicated diagnoses or dataset use.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from pedrad_ai import config, corpus, paper_db

TOPICS = {
    "Brain development / cognition": r"neurodevelop|brain develop|brain matur|brain age|cognitiv|connectom|functional connectivity|intelligence quotient|intelligence score|brain.behavio",
    "Autism / ADHD / psychiatric": r"autis|\badhd\b|attention.deficit|psychiatr|depress|anxiet|schizophren|bipolar",
    "Fetal assessment / prenatal": r"fetal|foetal|fetus|foetus|prenatal|antenatal|gestational age|placent",
    "Bone age / skeletal maturation": r"bone age|skeletal age|skeletal matur",
    "Pulmonary infection": r"pneumonia|tuberculos|bronchiolitis|\brsv\b|respiratory syncytial|covid|sars.cov",
    "Fracture / trauma / abuse": r"fracture|traumat|\btrauma\b|child abuse|non.accidental|abusive head",
    "Brain / CNS tumors": r"(?:brain|cerebral|intracranial|cns|central nervous system).{0,30}(?:tumou?r|neoplasm|cancer)|glioma|glioblastoma|medulloblastoma|ependymoma|craniopharyngioma",
    "Cardiac / congenital heart": r"cardiac|myocardi|heart|ventricular function|echocardi",
    "Epilepsy": r"epilep|seizure|cortical dysplasia",
    "Neonatal brain injury": r"hypoxic.isch|hypoxic isch|\bhie\b|intraventricular hemorrhage|intraventricular haemorrhage|periventricular leukomalacia|(?:neonat|preterm).{0,30}brain injur",
    "Renal / urinary": r"kidney|renal|hydronephro|vesicoureter|urinary|ureter|bladder",
    "Scoliosis / spine deformity": r"scoliosis|spinal deform|spine deform|cobb angle",
    "Acute abdomen": r"appendici|intussuscep|necrotizing enterocolitis|necrotising enterocolitis|\bnec\b",
    "Hydrocephalus": r"hydrocephal|ventriculomegal|ventricular dilat|cerebrospinal fluid shunt",
    "Liver / biliary": r"liver|hepati|biliary|cholestas",
    "Chronic lung / airway": r"cystic fibrosis|asthma|bronchopulmonary dysplasia|chronic lung|airway|foreign body aspir",
    "Hip dysplasia": r"hip dysplasia|dysplasia of the hip|developmental dysplasia|\bddh\b",
    "Inflammatory bowel disease": r"crohn|inflammatory bowel|ulcerative colitis",
}
DATASETS = {
    "ABIDE": r"\babide(?:[- _]?[12i]+)?\b|autism brain imaging data exchange",
    "ABCD": r"\babcd\b|adolescent brain cognitive development",
    "RSNA bone age": r"\brsna\b.{0,60}(?:bone|skeletal)|(?:bone|skeletal).{0,60}\brsna\b",
    "Guangzhou / Kermany": r"kermany|guangzhou|guang[ -]?zhou",
    "GRAZPEDWRI-DX": r"grazpedwri|graz.ped.wri",
    "dHCP": r"\bdhcp\b|developing human connectome",
    "FeTA": r"\bfeta\b|fetal tissue annotation",
    "FETAL_PLANES_DB": r"fetal[_ -]planes(?:[_ -]db)?",
    "BraTS-PEDs": r"brats[-_ ]?peds|pediatric brats|brats.{0,25}pediatric|pediatric.{0,25}brats",
    "Pediatric-CT-SEG": r"pediatric[-_ ]ct[-_ ]seg",
    "CBTN": r"\bcbtn\b|children.s brain tumou?r network",
    "PediCXR / VinDr-PCXR": r"pedicxr|vindr[-_ ]?pcxr",
    "Regensburg appendicitis": r"regensburg",
    "ADHD-200": r"adhd[-_ ]?200",
    "MIMIC-CXR (general resource)": r"mimic[-_ ]?cxr",
    "CheXpert (general resource)": r"chexpert",
}
ERAS = [("2005–2014", 2005, 2014), ("2015–2019", 2015, 2019),
        ("2020–2022", 2020, 2022), ("2023–2024", 2023, 2024),
        ("2025", 2025, 2025), ("2026 YTD", 2026, 2026)]
MODS = ["MRI", "ultrasound", "x-ray / radiography", "CT", "nuclear / PET", "fluoroscopy"]
MOD_NAMES = ["MRI", "Ultrasound", "Radiography", "CT", "Nuclear / PET", "Fluoroscopy"]
AGES = ["fetal", "neonate", "infant", "child", "adolescent", "pediatric (unspecified)", "mixed pediatric and adult"]
AGE_NAMES = ["Fetal", "Neonate", "Infant", "Child", "Adolescent", "Unspecified", "Mixed ages"]


def labels(row, field):
    return {x.strip() for x in (row.get(field) or "").split(";") if x.strip()}


def count_labels(rows, field):
    return dict(Counter(x for row in rows for x in labels(row, field)).most_common())


def matched(text, rules):
    return [label for label, pattern in rules.items() if re.search(pattern, text, re.I)]


def summarize(rows):
    return {"n": len(rows), "modality": count_labels(rows, "modality"),
            "task": count_labels(rows, "task"), "age_groups": count_labels(rows, "age_groups"),
            "topics": dict(Counter(t for r in rows for t in r["topics"]).most_common()),
            "dataset_mentions": dict(Counter(t for r in rows for t in r["datasets"]).most_common()),
            "preprints": sum(str(r.get("is_preprint")).lower() == "true" for r in rows),
            "release_status": dict(Counter(r["release_status"] for r in rows)),
            "validation": dict(Counter(r["validation"] for r in rows))}


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(config.FIGURE_DIR / f"{name}.{ext}", dpi=220, bbox_inches="tight")
    plt.close(fig)


def heatmap(matrix, rows, cols, title, subtitle, name):
    arr = np.array(matrix)
    fig, ax = plt.subplots(figsize=(11.5, max(4.5, len(rows) * .38 + 1.8)))
    ax.imshow(np.log1p(arr), cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(cols)), cols, fontsize=10)
    ax.set_yticks(range(len(rows)), rows, fontsize=10)
    for i in range(len(rows)):
        for j in range(len(cols)):
            ax.text(j, i, str(arr[i, j]), ha="center", va="center", fontsize=9,
                    color="white" if np.log1p(arr[i, j]) > np.log1p(arr.max()) * .64 else "#222222")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(title, loc="left", fontsize=14, pad=35)
    fig.text(.02, .015, subtitle, fontsize=9, color="#555555")
    fig.tight_layout(rect=(0, .045, 1, 1))
    save(fig, name)


def main():
    path = config.PROCESSED_DIR / "pedrad_paper_db.csv"
    with path.open() as fh:
        rows = list(csv.DictReader(fh))
    expected = {corpus.key(r) for r in corpus.partition(paper_db.presented(paper_db.load())).included}
    ids = [corpus.key(r) for r in rows]
    if len(set(ids)) != len(ids) or set(ids) != expected:
        raise ValueError("Corpus CSV is stale or duplicated; rebuild it before analyzing.")
    stats = json.loads((config.PROCESSED_DIR / "review_stats.json").read_text())
    if stats["flow"]["included"] != len(rows):
        raise ValueError("Run review_stats.py before landscape analysis.")
    for row in rows:
        row["topics"] = matched(" ".join(row.get(f) or "" for f in ("title", "clinical_problem")), TOPICS)
        row["datasets"] = matched(" ".join(row.get(f) or "" for f in
            ("title", "clinical_problem", "patient_population", "model_description", "dataset_size")), DATASETS)
    title_groups = defaultdict(list)
    for row in rows:
        title_groups[re.sub(r"[^a-z0-9]", "", row["title"].lower())].append(row)
    duplicate_titles = [[{"record_id": corpus.key(r), "year": r["year"], "title": r["title"], "doi": r["doi"]}
                         for r in group] for title, group in title_groups.items() if len(title) >= 20 and len(group) > 1]
    collapsed = [max(group, key=lambda r: (str(r.get("is_preprint")).lower() != "true",
                    r.get("source") == "pubmed", int(r["year"]))) for group in title_groups.values()]
    eras = {name: summarize([r for r in rows if lo <= int(r["year"]) <= hi]) for name, lo, hi in ERAS}
    out = {"generated_on": dt.date.today().isoformat(), "search_cutoff": "2026-09-09",
           "source_csv": str(path.relative_to(config.REPO_ROOT)),
           "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
           "definitions": {"topic_fields": ["title", "clinical_problem"],
               "dataset_fields": ["title", "clinical_problem", "patient_population", "model_description", "dataset_size"],
               "topic_rules": TOPICS, "dataset_rules": DATASETS,
               "interpretation": "Exploratory, overlapping text mentions, not adjudicated diseases or confirmed dataset reuse; no match is not proof of absence."},
           "all": summarize(rows), "eras": eras,
           "duplicate_title_candidates": duplicate_titles,
           "title_collapsed_sensitivity": summarize(collapsed),
           "topic_unmatched": sum(not r["topics"] for r in rows),
           "topic_by_modality": {t: {m: sum(t in r["topics"] and m in labels(r, "modality") for r in rows) for m in MODS} for t in TOPICS},
           "age_by_modality": {a: {m: sum(a in labels(r, "age_groups") and m in labels(r, "modality") for r in rows) for m in MODS} for a in AGES}}
    (config.PROCESSED_DIR / "review_landscape_stats.json").write_text(json.dumps(out, indent=2) + "\n")
    with (config.PROCESSED_DIR / "review_landscape_audit.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["record_id", "year", "title", "clinical_problem", "topics", "dataset_mentions"])
        writer.writeheader()
        for r in rows:
            writer.writerow({"record_id": corpus.key(r), "year": r["year"], "title": r["title"],
                             "clinical_problem": r["clinical_problem"], "topics": "; ".join(r["topics"]),
                             "dataset_mentions": "; ".join(r["datasets"])})
    order = sorted(TOPICS, key=lambda t: out["all"]["topics"].get(t, 0), reverse=True)
    heatmap([[out["topic_by_modality"][t][m] for m in MODS] for t in order], order, MOD_NAMES,
            f"Clinical topic × modality (n = {len(rows):,} records)",
            "Cells are record counts; color uses log(1 + count) to retain visibility of small cells.\n"
            "Exploratory title/clinical-question matches; topics and modalities overlap. Unmatched studies are retained in the cohort.",
            "review_topic_modality")
    heatmap([[out["age_by_modality"][a][m] for m in MODS] for a in AGES], AGE_NAMES, MOD_NAMES,
            f"Age group × modality (n = {len(rows):,} records)",
            "Cells are record counts; color uses log(1 + count). Age and modality labels overlap.\n"
            "Age labels identify populations mentioned, not age-stratified performance or unique children.", "review_age_modality")
    tasks = ["detection / diagnosis", "measurement / quantification", "outcome prediction", "segmentation",
             "reconstruction / imputation", "workflow / non-interpretive", "report generation / LLM",
             "foundation model / vision-language", "agent / autonomous"]
    fig, ax = plt.subplots(figsize=(12, 6))
    yy = np.arange(len(tasks))
    for offset, (era, color) in enumerate(zip(["2023–2024", "2025", "2026 YTD"], ["#999999", "#2a78d6", "#eb6834"])):
        sub = eras[era]
        vals = [100 * sub["task"].get(t, 0) / sub["n"] for t in tasks]
        bars = ax.barh(yy + (offset - 1) * .25, vals, height=.23, color=color, label=f"{era} (n={sub['n']:,})")
        ax.bar_label(bars, labels=[f"{v:.1f}%" for v in vals], padding=3, fontsize=8)
    ax.set_yticks(yy, [t.replace(" / ", " / ") for t in tasks], fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, max(100 * eras[e]["task"].get(t, 0) / eras[e]["n"] for e in ["2023–2024", "2025", "2026 YTD"] for t in tasks) + 8)
    ax.set_xlabel("Percentage of records in each period (overlapping task labels)")
    ax.set_title("The recent task mix: established applications and emerging directions", loc="left", pad=15)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    save(fig, "review_recent_tasks")
    lines = ["# Landscape analysis: reproducible supplementary tables", "",
        f"Generated {out['generated_on']} from **{len(rows):,} included primary-study records**; search cutoff September 9, 2026.", "",
        "Run `PYTHONPATH=. python scripts/review_stats.py` then `PYTHONPATH=. python scripts/build_landscape_review.py`. The latter verifies exact membership against the shared cohort and writes the source CSV SHA-256 to `data/processed/review_landscape_stats.json`.", "",
        "Topic counts below are exploratory matches to the title and extracted clinical question. Dataset counts are name mentions across the title and extracted clinical question, population, model description, and dataset size. They cannot establish whether a dataset was used for training, testing, or mentioned as context. No-match does not mean no use. All rules and row-level matches are exported in the JSON and `review_landscape_audit.csv`.", "",
        f"There are {out['topic_unmatched']:,} records with no match to the selected topic rules; these remain in every whole-cohort denominator. Categories overlap; counts are records, not independent datasets, models, or patients.", "",
        "## Table L1. Modality, task, and age by era", "",
        "| Axis / label | All | " + " | ".join(f"{e} (n={s['n']})" for e, s in eras.items()) + " |",
        "|:--|--:|" + "--:|" * len(eras)]
    def cell(n, total):
        return f"{n:,} ({100*n/total:.1f}%)" if total else "—"
    for axis in ["modality", "task", "age_groups"]:
        for label, n in out["all"][axis].items():
            lines.append("| " + axis + ": " + label + " | " + cell(n, len(rows)) + " | " + " | ".join(cell(s[axis].get(label, 0), s["n"]) for s in eras.values()) + " |")
    lines += ["", "## Table L2. Selected clinical topic mentions", "", "| Topic | All | 2023–2024 | 2025 | 2026 YTD |", "|:--|--:|--:|--:|--:|"]
    for t in order:
        lines.append("| " + t + " | " + cell(out["all"]["topics"].get(t, 0), len(rows)) + " | " + " | ".join(cell(eras[e]["topics"].get(t, 0), eras[e]["n"]) for e in ["2023–2024", "2025", "2026 YTD"]) + " |")
    lines += ["", "## Table L3. Named dataset mentions", "", "| Resource | All | 2025 | 2026 YTD |", "|:--|--:|--:|--:|"]
    for t, n in out["all"]["dataset_mentions"].items():
        lines.append(f"| {t} | {n} | {eras['2025']['dataset_mentions'].get(t, 0)} | {eras['2026 YTD']['dataset_mentions'].get(t, 0)} |")
    lines += ["", "## Table L4. Publication status", "", "| Period | Records | Preprint flag |", "|:--|--:|--:|"]
    for era, s in eras.items():
        lines.append(f"| {era} | {s['n']} | {cell(s['preprints'], s['n'])} |")
    lines += ["", "The preprint flag follows the stored source record; online-first and issue dates are not harmonized. Annual counts use the exported publication year. The clinical examples in the manuscript identify earlier online publication where relevant.", ""]
    lines += ["## Table L5. Unresolved publication-version candidates", "",
        f"Exact normalized-title matching identified {len(duplicate_titles)} groups ({sum(len(g) for g in duplicate_titles)} records). These are candidates for adjudication, not automatic exclusions. The analysis preserves the shared cohort; the record count is not a verified count of unique investigations. Different titles for different versions will escape this audit.", "",
        "| Group | Record | Year | Title | DOI |", "|--:|:--|--:|:--|:--|"]
    for i, group in enumerate(duplicate_titles, 1):
        for r in group:
            lines.append(f"| {i} | {r['record_id']} | {r['year']} | {r['title'].replace('|', '/')} | {r['doi']} |")
    lines += ["", "## Table L6. Sensitivity to retaining one record per normalized title", "",
        "Prefer a record without a preprint flag, then a PubMed record, then the latest publication year. This heuristic tests composition stability; it is not a replacement for version adjudication. Different titles can still represent the same investigation.", "",
        f"The sensitivity set contains {len(collapsed):,} records, compared with {len(rows):,} in the shared cohort.", "",
        "| Modality | Shared cohort | One record per title |", "|:--|--:|--:|"]
    for m in MODS:
        lines.append(f"| {m} | {cell(out['all']['modality'].get(m, 0), len(rows))} | {cell(out['title_collapsed_sensitivity']['modality'].get(m, 0), len(collapsed))} |")
    lines.append("")
    (config.REPORT_DIR / "05_landscape_analysis.md").write_text("\n".join(lines))
    print(json.dumps({"n": len(rows), "eras": {e: s["n"] for e, s in eras.items()},
                      "topics": out["all"]["topics"], "datasets": out["all"]["dataset_mentions"],
                      "unmatched": out["topic_unmatched"]}, indent=2))


if __name__ == "__main__":
    main()
