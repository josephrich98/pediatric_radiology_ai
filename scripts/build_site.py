#!/usr/bin/env python3
"""Build the static database website into ``dist/``.

The site is a read-only browser over the processed data: one tab per kind of
thing the project tracks (articles, open-source software, trade-press stories,
commercial products and FDA devices, public datasets). Search, sort, column
choice and CSV export all run in the browser over JSON snapshots, so the output
can be served by any static host with no backend (same design as
conference-agent's ``build_static.py``).

Reads only files in ``data/processed`` and ``pedrad_ai.config``; makes no
network calls. Run it after the collectors / ``export_unified_db.py``.

    python scripts/build_site.py              # writes dist/
    python scripts/build_site.py --out /tmp/site
    ( cd dist && python -m http.server 8000 ) # preview at http://localhost:8000

Output::

    dist/
      index.html, app.js, search.js     # copied from web/
      data/meta.json                    # snapshot dates and counts
      data/articles.json                # the review corpus of
                                        #   data/processed/pediatric_radiology_ai.csv
      data/software.json                # GitHub leaderboards + code links in papers
      data/news.json                    # newsletter_items.json
      data/fda.json                     # FDA AI-enabled devices, Radiology panel,
                                        # one row per device (repeat clearances
                                        # folded into the latest), plus the curated
                                        # products with no US authorization
                                        # (config.COMMERCIAL_PEDIATRIC rides on it
                                        #  as the curated_product column)
      data/datasets.json                # config.PEDIATRIC_DATASETS
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import shutil
from pathlib import Path
from typing import Any

from pedrad_ai import config, fda_devices

WEB_DIR = config.REPO_ROOT / "web"
ASSETS = ("index.html", "app.js", "search.js")

# --------------------------------------------------------------------------- #
# Articles
# --------------------------------------------------------------------------- #

# What each unified-table record type is, in words a reader of the site knows.
RECORD_TYPE_LABELS = {
    "corpus": "included study",
    "non_primary": "review / editorial",
    "screened_out": "screened out",
    "conference_proceeding": "conference proceeding",
    "most_cited": "most-cited list",
    "venue_work": "venue table",
    "embase_not_retrieved": "Embase, not retrieved",
}

# Unified-table columns carried to the site. Extraction provenance
# (extractor_model, prompt_version, confidence, ...) stays in the CSV.
ARTICLE_COLUMNS = [
    "record_id", "record_type", "publication_form", "scope", "title", "first_author",
    "year", "venue", "doi", "pmid", "arxiv_id", "url", "publication_types",
    "search_source", "source_files", "exclusion_reason", "model_name", "model_family",
    "modality", "body_region", "patient_population", "age_groups", "clinical_problem",
    "task", "model_description", "release_status", "release_evidence", "code_url",
    "study_design", "dataset_size", "data_source", "validation", "headline_result",
    "citations", "citations_per_year", "rcr", "fwci", "impact", "impact_measure",
    "nih_percentile", "citations_source", "conference_venue", "top_lists",
]
INT_COLUMNS = {"year", "citations"}
FLOAT_COLUMNS = {"citations_per_year", "rcr", "fwci", "impact", "nih_percentile"}


def _num(value: str, kind: type) -> int | float | None:
    if value in ("", None):
        return None
    try:
        return kind(float(value)) if kind is int else round(float(value), 2)
    except ValueError:
        return None


def articles() -> list[dict[str, Any]]:
    csv.field_size_limit(10**9)
    out = []
    with open(config.UNIFIED_DB_CSV, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            row: dict[str, Any] = {}
            for col in ARTICLE_COLUMNS:
                if col == "venue":
                    row[col] = r.get("journal") or r.get("venue_label") or ""
                elif col == "record_type":
                    row[col] = RECORD_TYPE_LABELS.get(r[col], r[col])
                elif col == "scope":
                    row[col] = "radiology AI (all ages)" if r[col] == "radiology_ai" else r[col]
                elif col in INT_COLUMNS:
                    row[col] = _num(r.get(col, ""), int)
                elif col in FLOAT_COLUMNS:
                    row[col] = _num(r.get(col, ""), float)
                else:
                    row[col] = r.get(col, "")
            if not row["url"]:
                if row["doi"]:
                    row["url"] = f"https://doi.org/{row['doi']}"
                elif row["pmid"]:
                    row["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{row['pmid']}/"
            out.append(row)
    return out


# --------------------------------------------------------------------------- #
# Open-source software
# --------------------------------------------------------------------------- #

REPO_LIST_LABELS = {
    "known_tools": "well-known tool",
    "radiology_ai": "radiology AI",
    "medical_imaging_ai": "medical imaging AI",
    "chest_xray_ai": "chest X-ray AI",
    "ct_segmentation": "CT segmentation",
    "pediatric_imaging_ai": "pediatric imaging AI",
    "bone_age": "bone age",
}


# "Intended pediatric use" for a repository. Two kinds of evidence, both
# recorded in ``pediatric_evidence``: the repository was found by the pediatric
# leaderboard searches, or it names a pediatric population in its own metadata.
# A general tool that a pediatric paper happens to use does not count.
PEDIATRIC_REPO_LISTS = ("pediatric imaging AI", "bone age")
PEDIATRIC_TERM_RE = re.compile(
    r"(?<!\w)(p(a)?ediatric(s)?|child(ren|hood)?|infant(s)?|neonat\w*|newborn(s)?|"
    r"fetal|foetal|fetus(es)?|prenatal|preterm|premature|adolescen\w*|bone.?age)(?!\w)",
    re.I,
)


def _repo_pediatric(row: dict[str, Any]) -> tuple[str, str]:
    """('yes' | '', why) for the pediatric yes / no of one repository row."""
    why = [f"{name} leaderboard" for name in row["lists"] if name in PEDIATRIC_REPO_LISTS]
    text = " ".join([row["name"], row["description"], " ".join(row["topics"])])
    terms = sorted({m.group(0).lower() for m in PEDIATRIC_TERM_RE.finditer(text)})
    if terms:
        why.append("names " + ", ".join(terms))
    return ("yes" if why else ""), "; ".join(why)


def _repo_key(url: str) -> str:
    u = url.strip().lower().rstrip("/")
    u = re.sub(r"\.git$", "", u)
    u = re.sub(r"^https?://(www\.)?", "", u)
    m = re.match(r"github\.com/([^/]+/[^/#?]+)", u)
    return f"github.com/{m.group(1)}" if m else u


def software(article_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """GitHub leaderboard repositories, plus every code link stated in a paper.

    A paper's code link that is already a leaderboard repository is attached to
    that row, so each repository appears once with the papers that cite it.
    """
    board = json.loads((config.PROCESSED_DIR / "github_repos.json").read_text())
    rows: dict[str, dict[str, Any]] = {}
    for list_name, repos in board.items():
        for r in repos:
            key = _repo_key(r["url"])
            row = rows.setdefault(key, {
                "name": r["full_name"], "url": r["url"], "host": "GitHub",
                "stars": r.get("stars"), "forks": r.get("forks"),
                "language": r.get("language") or "", "description": r.get("description") or "",
                "topics": r.get("topics") or [], "created": (r.get("created_at") or "")[:10],
                "updated": (r.get("updated_at") or "")[:10], "lists": [],
                "source": "GitHub leaderboard", "papers": [], "paper_urls": [], "paper_years": [],
            })
            label = REPO_LIST_LABELS.get(list_name, list_name)
            if label not in row["lists"]:
                row["lists"].append(label)

    for a in article_rows:
        code = (a.get("code_url") or "").strip()
        if not code or a["record_type"] == "screened out":
            continue
        for link in re.split(r"[;\s]+", code):
            if not link.startswith("http"):
                continue
            key = _repo_key(link)
            host = re.sub(r"^https?://(www\.)?", "", link).split("/")[0]
            row = rows.get(key)
            if row is None:
                m = re.search(r"github\.com/([^/]+/[^/#?]+)", link, re.I)
                name = re.sub(r"\.git$", "", m.group(1)) if m else re.sub(r"^https?://(www\.)?", "", link).rstrip("/")
                row = rows[key] = {
                    "name": name, "url": link.rstrip("/"), "host": "GitHub" if "github.com" in host else host,
                    "stars": None, "forks": None, "language": "", "description": "",
                    "topics": [], "created": "", "updated": "", "lists": [],
                    "source": "code link in a paper", "papers": [], "paper_urls": [], "paper_years": [],
                }
            elif row["source"] == "GitHub leaderboard":
                row["source"] = "GitHub leaderboard + paper"
            if a["title"] not in row["papers"]:
                row["papers"].append(a["title"])
                row["paper_urls"].append(a["url"])
                row["paper_years"].append(a["year"])
                if not row["description"] and a.get("model_description"):
                    row["description"] = a["model_description"]
    for row in rows.values():
        row["n_papers"] = len(row["papers"])
        row["pediatric"], row["pediatric_evidence"] = _repo_pediatric(row)
    return sorted(rows.values(), key=lambda r: (-(r["stars"] or -1), r["name"].lower()))


# --------------------------------------------------------------------------- #
# Newsletters
# --------------------------------------------------------------------------- #

def news() -> list[dict[str, Any]]:
    items = json.loads((config.PROCESSED_DIR / "newsletter_items.json").read_text())
    out = []
    for it in items:
        paper = it.get("paper") or {}
        out.append({
            "date": it.get("date") or "", "year": _num((it.get("date") or "")[:4], int),
            "source": it.get("source") or "", "story": it.get("story") or "",
            "url": it.get("url") or "", "issue_title": it.get("issue_title") or "",
            "snippet": (it.get("snippet") or "").strip("…").strip(),
            "topics": it.get("topics") or [], "players": it.get("players") or [],
            "pediatric_terms": it.get("pediatric_terms") or [], "ai_terms": it.get("ai_terms") or [],
            "paper": paper.get("citation") or "", "paper_title": paper.get("title") or "",
            "paper_url": (f"https://doi.org/{paper['doi']}" if paper.get("doi") else paper.get("url") or ""),
        })
    return sorted(out, key=lambda r: r["date"], reverse=True)


# --------------------------------------------------------------------------- #
# Commercial
# --------------------------------------------------------------------------- #

# config.COMMERCIAL_PEDIATRIC groups some vendors into one slide row. The site
# lists one row per company product, so those entries are split here. Keys are
# the config's (vendor, product); each split row overrides only what differs.
# If a config entry changes, its key stops matching and the entry is shown
# unsplit (with a warning) rather than with stale text.
PRODUCT_SPLITS: dict[tuple[str, str], list[dict[str, str]]] = {
    ("BrightHeart", "Fetal EchoScan; View Classifier"): [
        {"product": "Fetal EchoScan",
         "task": "Flags 8 findings suspicious for fetal congenital heart defects",
         "pediatric": "Prenatal: 2nd-trimester exams; maternal age 18+"},
        {"product": "View Classifier",
         "task": "Identifies standard fetal cardiac views; checks exam completeness",
         "pediatric": "Prenatal: 2nd / 3rd-trimester exams; maternal age 18+"},
    ],
    ("Subtle Medical / AIRS Medical", "SubtleMR, SwiftMR"): [
        {"vendor": "Subtle Medical", "product": "SubtleMR", "fda_company": "Subtle Medical",
         "pediatric": "No adult-only restriction in reviewed US indications"},
        {"vendor": "AIRS Medical", "product": "SwiftMR", "fda_company": "AIRS Medical",
         "pediatric": "No adult-only restriction in reviewed US indications; 2026 validation includes ages 0-21"},
    ],
    ("Qure.ai", "qXR / qER families"): [
        {"product": "qXR family", "modality": "x-ray",
         "task": "Chest X-ray detection / triage, TB screening, tube / heart measurements"},
        {"product": "qER family", "modality": "CT",
         "task": "Head CT triage / quantification and CTA LVO",
         "pediatric": "US eligibility varies by module"},
    ],
    ("Aidoc / Viz.ai", "BriefCase, Viz LVO / ICH"): [
        {"vendor": "Aidoc", "product": "BriefCase", "fda_company": "Aidoc",
         "task": "CT / CTA triage (e.g., ICH, LVO, PE, pneumothorax, fractures, free gas)"},
        {"vendor": "Viz.ai", "product": "Viz LVO / ICH", "fda_company": "Viz.ai", "url": "",
         "task": "LVO / ICH alerts, care coordination"},
    ],
}


def _detex(s: str) -> str:
    return s.replace("--", "–").replace("\\_", "_").replace("\\&", "&")


def _matched_companies(fda: dict[str, Any], pattern: str) -> list[str]:
    """Normalized company names behind a company_lookup count (same alias rule)."""
    aliases = [re.escape(p.strip()) for p in pattern.split("|") if p.strip()]
    if not aliases:
        return []
    rx = re.compile(r"(?<!\w)(?:" + "|".join(aliases) + r")(?!\w)", re.I)
    return sorted({d.get("company_norm") or d["company"]
                   for d in fda.get("devices", []) if rx.search(d.get("company") or "")})


def products(fda: dict[str, Any]) -> list[dict[str, Any]]:
    used = set()
    out = []
    for entry in config.COMMERCIAL_PEDIATRIC:
        key = (entry["vendor"], entry["product"])
        splits = PRODUCT_SPLITS.get(key)
        if splits:
            used.add(key)
        for part in splits or [{}]:
            c = {**entry, **part}
            look = fda_devices.company_lookup(fda, c["fda_company"])
            years = look.get("years") or []
            out.append({
                "vendor": c["vendor"], "product": c["product"], "modality": c["modality"],
                "task": _detex(c["task"]), "pediatric": _detex(c["pediatric"]), "url": c.get("url") or "",
                "fda_entries": look.get("devices", 0),
                "fda_years": (f"{years[0]}–{years[-1]}" if len(years) > 1 else str(years[0])) if years else "",
                "fda_companies": _matched_companies(fda, c["fda_company"]),
            })
    for key in set(PRODUCT_SPLITS) - used:
        print(f"  warning: PRODUCT_SPLITS key {key} no longer matches config.COMMERCIAL_PEDIATRIC")
    return out


def _submission_url(number: str) -> str:
    n = number.strip().upper()
    base = "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs"
    if n.startswith("K"):
        return f"{base}/cfpmn/pmn.cfm?ID={n}"
    if n.startswith("DEN"):
        return f"{base}/cfpmn/denovo.cfm?ID={n}"
    if n.startswith("P"):
        return f"{base}/cfpma/pma.cfm?id={n}"
    return ""


def _curated_by_company(product_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Normalized FDA company name -> the curated pediatric products it sells.

    The commercial tab is one table of authorizations, so the curated product
    list survives as a company-level column rather than a second table. It is a
    company flag, not a claim about the authorization on that row.
    """
    out: dict[str, list[str]] = {}
    for r in product_rows:
        for company in r["fda_companies"]:
            names = out.setdefault(company, [])
            if r["product"] not in names:
                names.append(r["product"])
    return out


def _device_key(company: str, device: str) -> tuple[str, str]:
    """Same company and same device name, ignoring case and spacing."""
    norm = lambda x: re.sub(r"\s+", " ", (x or "").strip().lower())
    return norm(company), norm(device)


def _one_row_per_device(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fold repeat authorizations of one device into its most recent row.

    The FDA list has one entry per authorization, so a device cleared again
    for a new version or indication (BoneView: K212365 in 2022, K222176 in
    2023) appears once per clearance. The site shows the device once, dated by
    its latest authorization, and lists the earlier ones. The pediatric tick
    is the device's: set if any of its authorizations has a label-positive
    screen, and the evidence says which one, because a later clearance whose
    label was not screened positive does not undo an earlier pediatric one.
    """
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in rows:
        groups.setdefault(_device_key(r["company"], r["device"]), []).append(r)
    out = []
    for group in groups.values():
        group.sort(key=lambda r: (r["date"], r["submission"]), reverse=True)
        latest = dict(group[0])
        latest["earlier_submissions"] = [
            f"{r['submission']} ({r['date'][:4]})" if r["date"] else r["submission"] for r in group[1:]]
        positive = next((r for r in group if r["pediatric"] == "yes"), None)
        if positive is not None:
            for k in ("pediatric", "pediatric_status", "pediatric_evidence_pages"):
                latest[k] = positive[k]
            pages = f", pages {positive['pediatric_evidence_pages']}" if positive["pediatric_evidence_pages"] else ""
            which = "this authorization" if positive is group[0] else \
                f"an earlier authorization, {positive['submission']} ({positive['date'][:4]})"
            latest["pediatric_evidence"] = (
                f"Pediatric intended use or population in the label of {which}{pages}")
        if any(r["pediatric_name"] for r in group):
            latest["pediatric_name"] = "yes"
        out.append(latest)
    return out


def _products_without_us_authorization() -> list[dict[str, Any]]:
    """Curated products with no US authorization, as rows of the commercial tab.

    The tab is the FDA list, so a product the FDA never authorized (BoneXpert,
    for one) would otherwise be missing from the site while it is on the
    slides. These rows have no date, submission or product code, and say why
    in ``us_status`` and ``pediatric_evidence``.
    """
    urls = {c["vendor"]: c.get("url") or "" for c in config.COMMERCIAL_PEDIATRIC}
    out = []
    for p in config.COMMERCIAL_PRODUCTS:
        if not p.get("no_us_authorization"):
            continue
        out.append({
            "date": "", "year": None, "device": p["product"], "company": p["vendor"],
            "company_full": p["vendor"], "submission": "", "submission_url": urls.get(p["vendor"], ""),
            "product_code": "", "pediatric_name": "", "pediatric_status": "",
            "pediatric_evidence_pages": "", "curated_product": [p["product"]],
            "us_status": "not FDA-authorized",
            "pediatric_evidence": _detex(p["pediatric"]),
            "pediatric": "yes",
            "earlier_submissions": [],
        })
    return out


def fda_rows(fda: dict[str, Any], product_rows: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    curated = _curated_by_company(product_rows or [])
    # Join the dated FDA pediatric-use screen by submission number.
    inventory_path = config.PROCESSED_DIR / "fda_pediatric_inventory.json"
    inventory = json.loads(inventory_path.read_text()) if inventory_path.exists() else {}
    pediatric = {
        r.get("submission"): r for r in inventory.get("records", [])
        if r.get("status") == "label-positive-candidate"
    }

    def row(date: str, year: Any, device: str, company: str, company_full: str,
            submission: str, product_code: str, name_hit: bool) -> dict[str, Any]:
        candidate = pediatric.get(submission)
        pages = ", ".join(str(p) for p in (candidate or {}).get("evidence_pages", []))
        return {
            "date": date, "year": year, "device": device, "company": company,
            "company_full": company_full, "submission": submission,
            "submission_url": _submission_url(submission), "product_code": product_code,
            "pediatric_name": "yes" if name_hit else "",
            "pediatric_status": "label-positive-candidate" if candidate else "",
            "pediatric_evidence_pages": pages,
            "curated_product": curated.get(company, []),
            "us_status": "FDA-authorized",
            "pediatric_evidence": ("Pediatric intended use or population in the label"
                                   + (f", pages {pages}" if pages else "")) if candidate else "",
            "pediatric": "yes" if candidate else "",
        }

    def iso(s: str) -> str:
        try:
            return dt.datetime.strptime(s or "", "%m/%d/%Y").date().isoformat()
        except ValueError:
            return ""

    out = []
    seen_submissions = set()
    for d in fda.get("devices", []):
        submission = d.get("submission") or ""
        seen_submissions.add(submission)
        company = d.get("company_norm") or d.get("company") or ""
        out.append(row(iso(d.get("date")), d.get("year"), d.get("device") or "", company,
                       d.get("company") or "", submission, d.get("product_code") or "",
                       bool(d.get("pediatric_name_hit"))))
    # The general FDA snapshot predates some of the pediatric candidates in the
    # inventory; add those so every candidate reaches the tab.
    for r in pediatric.values():
        submission = r.get("submission") or ""
        if submission in seen_submissions:
            continue
        date = iso(r.get("decision_date"))
        out.append(row(date, int(date[:4]) if date else None, r.get("device") or "",
                       r.get("company") or "", r.get("company") or "", submission,
                       r.get("product_code") or "", False))
    out = _one_row_per_device(out) + _products_without_us_authorization()
    return sorted(out, key=lambda r: r["date"], reverse=True)


# --------------------------------------------------------------------------- #
# Datasets
# --------------------------------------------------------------------------- #

def datasets() -> list[dict[str, Any]]:
    return [{k: _detex(v) for k, v in d.items()} for d in config.PEDIATRIC_DATASETS]


# --------------------------------------------------------------------------- #

def _write(path: Path, rows: list[dict[str, Any]]) -> None:
    """Rows as {columns, rows}: keys once, values as arrays (about half the size)."""
    cols = list(rows[0]) if rows else []
    payload = {"columns": cols, "rows": [[r.get(c) for c in cols] for r in rows]}
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def build(out_dir: Path) -> dict[str, Any]:
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    fda = json.loads((config.PROCESSED_DIR / "fda_ai_devices.json").read_text())

    arts = articles()
    # The articles tab is the review corpus, so only the included primary
    # studies are shipped; the other record types of the unified table (screened
    # out, reviews, venue and most-cited rows) stay in
    # data/processed/pediatric_radiology_ai.csv. `software` still reads every
    # record, because a code link in a review is still a code link.
    corpus = [r for r in arts if r["record_type"] == "included study"]
    # The curated pediatric-product list is not a table of its own on the site:
    # the commercial tab is the FDA authorization list, and each curated product
    # rides along as a company-level column on it.
    product_rows = products(fda)
    tables = {
        "articles": corpus,
        "software": software(arts),
        "news": news(),
        "fda": fda_rows(fda, product_rows),
        "datasets": datasets(),
    }
    for name, rows in tables.items():
        _write(data_dir / f"{name}.json", rows)

    def mtime(p: Path) -> str:
        return dt.date.fromtimestamp(p.stat().st_mtime).isoformat()

    meta = {
        "built_on": dt.date.today().isoformat(),
        "counts": {
            **{k: len(v) for k, v in tables.items()},
            "products": len(product_rows),
            "fda_pediatric": sum(r["pediatric"] == "yes" and r["us_status"] == "FDA-authorized" for r in tables["fda"]),
            "fda_not_authorized": sum(r["us_status"] != "FDA-authorized" for r in tables["fda"]),
            "fda_authorizations": sum(1 + len(r["earlier_submissions"]) for r in tables["fda"] if r["submission"]),
        },
        "snapshots": {
            "articles": mtime(config.UNIFIED_DB_CSV),
            "software": mtime(config.PROCESSED_DIR / "github_repos.json"),
            "news": mtime(config.PROCESSED_DIR / "newsletter_items.json"),
            "fda": fda.get("collected_on", ""),
            "fda_pediatric": json.loads((config.PROCESSED_DIR / "fda_pediatric_inventory.json").read_text()).get("retrieved_on", "") if (config.PROCESSED_DIR / "fda_pediatric_inventory.json").exists() else "",
            "products": "2026-09-16",
            "datasets": "2026-09-07",
        },
        "news_blocked": [{"name": k, **v} for k, v in config.NEWSLETTER_BLOCKED.items()],
        "fda_source": fda.get("source", ""),
    }
    (data_dir / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")

    for name in ASSETS:
        shutil.copyfile(WEB_DIR / name, out_dir / name)
    return meta


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=config.REPO_ROOT / "dist")
    args = ap.parse_args()
    meta = build(args.out)
    print(f"wrote {args.out}/")
    for name, n in meta["counts"].items():
        path = args.out / "data" / f"{name}.json"
        if not path.exists():  # a derived count (articles_included, products)
            continue
        print(f"  {name:10s} {n:6d} rows  {path.stat().st_size / 1e6:5.1f} MB")


if __name__ == "__main__":
    main()
