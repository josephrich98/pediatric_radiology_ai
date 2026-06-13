"""Analysis helpers: turn raw collector output into trend tables and fractions.

These functions are deliberately pandas-light at the core (so the package
imports cheaply) but return tidy structures that pandas/matplotlib consume in
the notebooks. The two headline derived quantities are:

* the radiology-AI share of all radiology publishing over time, and
* the pediatric share of radiology-AI publishing over time.
"""

from __future__ import annotations

from typing import Any

from . import utils


def _series(counts: dict[str, dict[Any, int]], name: str) -> dict[int, int]:
    raw = counts.get(name, {})
    return {int(k): int(v) for k, v in raw.items()}


def fractions_over_time(counts: dict[str, dict[Any, int]]) -> list[dict[str, Any]]:
    """Build a per-year table of counts and the key fractions.

    Expects the nested dict produced by :func:`pubmed.collect_all_yearly`.
    Returns one row per year with absolute counts and:

    * ``ai_share_of_radiology`` = radiology_ai / all_radiology
    * ``pediatric_share_of_radiology_ai`` = pediatric_radiology_ai / radiology_ai
    * ``ai_share_of_pediatric_radiology`` = pediatric_radiology_ai / pediatric_radiology
    """
    all_rad = _series(counts, "all_radiology")
    rad_ai = _series(counts, "radiology_ai")
    ped_rad = _series(counts, "pediatric_radiology")
    ped_rad_ai = _series(counts, "pediatric_radiology_ai")

    years = sorted(set(all_rad) | set(rad_ai) | set(ped_rad) | set(ped_rad_ai))
    rows: list[dict[str, Any]] = []
    for yr in years:
        a = all_rad.get(yr, 0)
        ra = rad_ai.get(yr, 0)
        pr = ped_rad.get(yr, 0)
        pra = ped_rad_ai.get(yr, 0)
        rows.append(
            {
                "year": yr,
                "all_radiology": a,
                "radiology_ai": ra,
                "pediatric_radiology": pr,
                "pediatric_radiology_ai": pra,
                "ai_share_of_radiology": _safe_div(ra, a),
                "pediatric_share_of_radiology_ai": _safe_div(pra, ra),
                "ai_share_of_pediatric_radiology": _safe_div(pra, pr),
            }
        )
    return rows


def breakdown_table(counts: dict[str, dict[Any, int]], prefix: str) -> list[dict[str, Any]]:
    """Collapse a ``prefix::label`` family of series into total counts per label.

    Used for modality / task breakdowns. Returns rows sorted by total,
    descending, with the most recent-year count and the cumulative total.
    """
    rows: list[dict[str, Any]] = []
    for key, series in counts.items():
        if not key.startswith(prefix + "::"):
            continue
        label = key.split("::", 1)[1]
        clean = {int(k): int(v) for k, v in series.items()}
        total = sum(clean.values())
        recent = max(clean) if clean else None
        rows.append(
            {
                "label": label,
                "total": total,
                "latest_year": recent,
                "latest_count": clean.get(recent, 0) if recent else 0,
            }
        )
    rows.sort(key=lambda r: r["total"], reverse=True)
    return rows


def cagr(series: dict[int, int], start: int | None = None, end: int | None = None) -> float | None:
    """Compound annual growth rate of a count series between two years."""
    clean = {int(k): int(v) for k, v in series.items() if int(v) > 0}
    if not clean:
        return None
    start = start or min(clean)
    end = end or max(clean)
    if start not in clean or end not in clean or end <= start:
        return None
    ratio = clean[end] / clean[start]
    return ratio ** (1.0 / (end - start)) - 1.0


def _safe_div(num: float, den: float) -> float:
    return round(num / den, 5) if den else 0.0


def summarize(counts: dict[str, dict[Any, int]]) -> dict[str, Any]:
    """A compact headline summary used at the top of reports."""
    frac = fractions_over_time(counts)
    if not frac:
        return {}
    latest = frac[-1]
    first = frac[0]
    return {
        "year_range": [first["year"], latest["year"]],
        "radiology_ai_latest": latest["radiology_ai"],
        "radiology_ai_cagr": cagr(_series(counts, "radiology_ai")),
        "pediatric_radiology_ai_latest": latest["pediatric_radiology_ai"],
        "pediatric_radiology_ai_cagr": cagr(_series(counts, "pediatric_radiology_ai")),
        "ai_share_of_radiology_first": first["ai_share_of_radiology"],
        "ai_share_of_radiology_latest": latest["ai_share_of_radiology"],
        "pediatric_share_of_radiology_ai_latest": latest["pediatric_share_of_radiology_ai"],
    }


def write_trend_csv(counts: dict[str, dict[Any, int]], path: str) -> str:
    rows = fractions_over_time(counts)
    utils.save_csv(rows, path)
    return path
