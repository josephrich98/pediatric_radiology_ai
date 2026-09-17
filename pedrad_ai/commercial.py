"""The commercial landscape: who holds the clearances, and for what.

``fda_devices`` counts the FDA AI-enabled device list. This module turns that
count into the two things the slides actually ask of it:

**Who.** Radiology-panel authorizations per company per year, and the subset of
them whose decision summary states a pediatric or fetal patient population
(``data/processed/fda_pediatric_inventory.json``, built by
``scripts/build_fda_pediatric_inventory.py``). The two series join on the
submission number, so the pediatric line is always a subset of the company's
own line and never a separately counted quantity.

**What.** A clinical problem per device. The list carries none, so one is
assigned from the device name first and the FDA product code second
(``config.COMMERCIAL_PROBLEM_TERMS`` / ``COMMERCIAL_PROBLEM_CODES``). Names win
because the codes are mostly generic: a quarter of the radiology panel is QIH,
"Automated Radiological Image Processing Software", which says nothing about
what the software is for. A device that neither names a problem nor sits under
a problem-specific code stays unassigned; that is reported as a count, not
filled in by guessing, and it is most of the list.

Two cautions that every figure built from this has to carry:

* A pediatric population statement in a decision summary is not a pediatric
  indication, still less pediatric evidence. Scanner platforms in particular
  (``config.COMMERCIAL_SYSTEM_CODES``) list pediatric imaging as one clinical
  application among many, which is why ultrasound systems dominate the
  pediatric-labeled set; ``kind`` separates them from standalone software.
* An entry is a submission, not a product. Versions, resubmissions and
  multi-device submissions each count once, so company totals run ahead of the
  number of distinct algorithms a company sells.
"""

from __future__ import annotations

import re
from typing import Any

from . import config

_PROBLEM_RX: dict[str, list[re.Pattern[str]]] = {
    label: [re.compile(p, re.I) for p in pats]
    for label, pats in config.COMMERCIAL_PROBLEM_TERMS.items()
}

UNASSIGNED = "clinical problem not named"


def clinical_problem(device: str, product_code: str = "") -> str | None:
    """Clinical problem for one device, or ``None`` when neither the name nor
    the product code names one."""
    name = device or ""
    for label, pats in _PROBLEM_RX.items():
        if any(p.search(name) for p in pats):
            return label
    return config.COMMERCIAL_PROBLEM_CODES.get((product_code or "").strip().upper())


def pediatric_submissions(inventory: dict[str, Any] | None) -> set[str]:
    """Submission numbers whose decision summary states a pediatric or fetal
    patient population (the screen's ``label-positive-candidate`` tier; the
    ``needs-label-review`` tier is deliberately excluded)."""
    if not inventory:
        return set()
    return {
        r["submission"] for r in inventory.get("records", [])
        if r.get("status") == "label-positive-candidate" and r.get("submission")
    }


def records(fda: dict[str, Any] | None, inventory: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Every radiology-panel device, annotated with the pediatric label flag,
    the device kind (``system`` vs ``software``) and the clinical problem."""
    if not fda:
        return []
    ped = pediatric_submissions(inventory)
    out = []
    for d in fda.get("devices", []):
        code = (d.get("product_code") or "").strip().upper()
        out.append({
            **d,
            "pediatric_label": d.get("submission") in ped,
            "kind": "system" if code in config.COMMERCIAL_SYSTEM_CODES else "software",
            "problem": clinical_problem(d.get("device", ""), code),
        })
    return out


# --------------------------------------------------------------------------- #
# Who: authorizations per company per year
# --------------------------------------------------------------------------- #
def by_company(recs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group records by company, folding the spelling variants the FDA list
    carries (``EOS imaging`` and ``Eos Imaging``, ``BrightHeart`` and
    ``Brightheart``) into one entry under the company's commonest spelling."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for r in recs:
        groups.setdefault((r.get("company_norm") or "").lower(), []).append(r)
    out = {}
    for rows in groups.values():
        spellings: dict[str, int] = {}
        for r in rows:
            spellings[r["company_norm"]] = spellings.get(r["company_norm"], 0) + 1
        out[max(spellings, key=lambda s: (spellings[s], s))] = rows
    return out


def company_series(recs: list[dict[str, Any]], *, top_n: int | None = None,
                   always: list[str] | None = None, cumulative: bool = True,
                   pediatric_kind: str | None = "software"
                   ) -> dict[str, tuple[dict[int, int], dict[int, int]]]:
    """``{company: (all_by_year, pediatric_by_year)}`` for the line chart.

    Companies are the ``top_n`` with the most radiology entries plus everyone
    in ``always``; the pediatric-focused vendors hold a handful of clearances
    each and would otherwise never appear next to the scanner makers. With
    ``cumulative`` the series is the running total of products held, which is
    what "how big is this company's portfolio" means; the per-year counts are
    one or two products and read as noise.

    ``pediatric_kind="software"`` restricts the pediatric series to standalone
    software, because a scanner is labeled for pediatric imaging whether or not
    its AI was built for children: of the 230 radiology entries whose summary
    states a pediatric population, only about half are software, and counting
    the rest would put a long pediatric line under every ultrasound maker.
    """
    top_n = config.COMMERCIAL_LINE_TOP_N if top_n is None else top_n
    always = config.COMMERCIAL_LINE_ALWAYS if always is None else always
    groups = by_company(recs)
    ranked = sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    chosen = [c for c, _ in ranked[:top_n]]
    lower = {c.lower(): c for c in groups}
    for name in always:
        canon = lower.get(name.lower())
        if canon and canon not in chosen:
            chosen.append(canon)

    years = sorted({r["year"] for r in recs if r.get("year")})
    if not years:
        return {}

    def is_ped(r):
        return r["pediatric_label"] and (pediatric_kind is None or r["kind"] == pediatric_kind)

    series: dict[str, tuple[dict[int, int], dict[int, int]]] = {}
    for company in chosen:
        mine = [r for r in groups[company] if r.get("year")]
        if not mine:
            continue
        first = min(r["year"] for r in mine)
        all_by, ped_by, a, p = {}, {}, 0, 0
        for y in [y for y in years if y >= first]:
            na = sum(1 for r in mine if r["year"] == y)
            np_ = sum(1 for r in mine if r["year"] == y and is_ped(r))
            a, p = (a + na, p + np_) if cumulative else (na, np_)
            all_by[y], ped_by[y] = a, p
        series[company] = (all_by, ped_by)
    # Biggest portfolio first, so the legend reads in the order the lines end.
    return dict(sorted(series.items(), key=lambda kv: -max(kv[1][0].values() or [0])))


# --------------------------------------------------------------------------- #
# What: clinical problems
# --------------------------------------------------------------------------- #
def problem_counts(recs: list[dict[str, Any]]) -> dict[str, Any]:
    """Devices per clinical problem, overall and for the pediatric-labeled
    subset, with the unassigned remainder kept as an explicit count."""
    counts: dict[str, dict[str, int]] = {}
    unassigned = {"all": 0, "pediatric": 0}
    for r in recs:
        bucket = counts.setdefault(r["problem"], {"all": 0, "pediatric": 0}) if r["problem"] else unassigned
        bucket["all"] += 1
        if r["pediatric_label"]:
            bucket["pediatric"] += 1
    return {
        "counts": dict(sorted(counts.items(), key=lambda kv: -kv[1]["all"])),
        "unassigned": unassigned,
        "total": len(recs),
        "total_pediatric": sum(1 for r in recs if r["pediatric_label"]),
        "systems_pediatric": sum(1 for r in recs if r["pediatric_label"] and r["kind"] == "system"),
    }


# --------------------------------------------------------------------------- #
# Tables
# --------------------------------------------------------------------------- #
def _alias_rx(pattern: str) -> re.Pattern[str] | None:
    aliases = [re.escape(p.strip()) for p in (pattern or "").split("|") if p.strip()]
    if not aliases:
        return None
    return re.compile(r"(?<!\w)(?:" + "|".join(aliases) + r")(?!\w)", re.I)


def company_rows(recs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per curated company (``config.COMMERCIAL_PEDIATRIC``): the
    counts the slide quotes, joined to the same records the figures use.

    ``fda_entries`` matches the company aliases against the raw company field,
    as ``fda_devices.company_lookup`` does, because a grouped row such as the
    scanner makers is several companies; ``pediatric_entries`` is the subset of
    those entries whose decision summary states a pediatric population, and
    ``pediatric_software`` drops the scanner platforms from it.
    """
    rows = []
    for c in config.COMMERCIAL_PEDIATRIC:
        rx = _alias_rx(c.get("fda_company", ""))
        hits = [r for r in recs if rx and rx.search(r.get("company") or "")]
        ped = [r for r in hits if r["pediatric_label"]]
        years = sorted({r["year"] for r in hits if r.get("year")})
        rows.append({
            **c,
            "fda_entries": len(hits),
            "fda_years": years,
            "pediatric_entries": len(ped),
            "pediatric_software": sum(1 for r in ped if r["kind"] == "software"),
            "problems": sorted({r["problem"] for r in hits if r["problem"]}),
        })
    return sorted(rows, key=lambda r: (-r["pediatric_entries"], -r["fda_entries"], r["vendor"]))


def product_rows(recs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per product (``config.COMMERCIAL_PRODUCTS``), with the FDA
    decision year attached where the row names a supporting submission."""
    by_sub = {r.get("submission"): r for r in recs if r.get("submission")}
    rows = []
    for p in config.COMMERCIAL_PRODUCTS:
        rec = by_sub.get(p.get("submission") or "")
        rows.append({**p, "year": rec.get("year") if rec else None,
                     "fda_device": rec.get("device") if rec else ""})
    return rows
