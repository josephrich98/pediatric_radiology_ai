#!/usr/bin/env python3
"""Descriptive figures for the systematic review, from the screened corpus.

Chart conventions mirror ``scripts/make_figures.py`` (the source of truth): one
axis per chart, the same fixed categorical palette in the same fixed order, thin
marks, recessive grids, integer year ticks, current partial year marked "YTD".

The palette was re-validated with the dataviz validator: lightness band, CVD
separation (worst adjacent pair dE 9.1) and normal-vision floor all pass. Three
hues sit below 3:1 contrast against the surface, which obliges visible relief, so
every chart here carries direct value labels rather than relying on fill alone.
The gray slot is the deliberate "other" category, not a generated 9th hue.

Outputs to figures/. Each figure is skipped if its input is missing.

Usage:
    python scripts/make_review_figures.py
"""
from __future__ import annotations

import collections
import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402
from matplotlib.ticker import MultipleLocator  # noqa: E402

from pedrad_ai import config  # noqa: E402

FIG = config.FIGURE_DIR
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948", "#8c8c8c"]
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED, GRAY = PALETTE
INK, MUTED = "#222222", "#666666"

MODALITY_COLOR = {
    "x-ray / radiography": BLUE, "CT": ORANGE, "MRI": AQUA, "ultrasound": YELLOW,
    "mammography": MAGENTA, "nuclear / PET": GREEN, "fluoroscopy": VIOLET,
    "multiple": RED, "other": GRAY,
}
# Ten task categories, nine palette slots. A tenth hue is never generated: the
# three rarest tasks (each ~1% of the corpus) fold into "other", which owns the
# gray slot. That keeps identity stable across charts and keeps every adjacent
# pair inside the validated CVD separation.
TASK_FOLD = {"agent / autonomous": "other",
             "report generation / LLM": "other",
             "foundation model / vision-language": "other"}
TASK_ORDER = [t for t in config.PAPER_DB_TASKS if t not in TASK_FOLD and t != "other"] + ["other"]
TASK_COLOR = {t: PALETTE[i] for i, t in enumerate(TASK_ORDER[:-1])}
TASK_COLOR["other"] = GRAY
AGE_COLOR = {a: PALETTE[i] for i, a in enumerate(config.PAPER_DB_AGE_GROUPS)}
VALIDATION_ORDER = ["prospective", "reader study", "external / multi-center",
                    "internal only", "none / not stated"]
VALIDATION_COLOR = dict(zip(VALIDATION_ORDER, [GREEN, AQUA, BLUE, YELLOW, GRAY]))


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=160)
    plt.close(fig)
    print(f"  wrote {name}")


def _style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e3e3e3", linewidth=0.6)
    ax.set_axisbelow(True)


def _style_x(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#e3e3e3", linewidth=0.6)
    ax.set_axisbelow(True)


def _year_axis(ax, years):
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.set_xlim(min(years) - 0.6, max(years) + 0.6)


def _mark_partial(ax, years):
    if config.END_YEAR in years:
        ax.annotate("YTD", xy=(config.END_YEAR, 0), xytext=(0, -22),
                    textcoords="offset points", ha="center", fontsize=7, color=MUTED)


def load_rows():
    """Included primary studies — the same set review_stats.py reports on.

    The CSV holds every in-scope record, reviews and editorials included. The
    review's eligibility criteria admit primary research only, so the figures
    filter to the id list review_stats.py exports. Without that filter the
    figures and the tables would disagree by the number of reviews.
    """
    path = config.PROCESSED_DIR / "pedrad_paper_db.csv"
    if not path.exists():
        return []
    with path.open() as fh:
        rows = list(csv.DictReader(fh))
    ids_path = config.PROCESSED_DIR / "review_included_ids.json"
    if ids_path.exists():
        keep = set(json.loads(ids_path.read_text(encoding="utf-8")))
        rows = [r for r in rows if (r.get("pmid") or r.get("record_id")) in keep]
    return rows


def load_store():
    path = config.PAPER_DB_JSON if hasattr(config, "PAPER_DB_JSON") else None
    for cand in (path, config.PROCESSED_DIR / "pedrad_paper_db.json"):
        if cand and cand.exists():
            return json.loads(cand.read_text(encoding="utf-8"))
    return {}


def multi(rows, field):
    """Count a semicolon-joined multi-label field."""
    c = collections.Counter()
    for r in rows:
        for v in [x.strip() for x in (r.get(field) or "").split(";") if x.strip()]:
            c[v] += 1
    return c


# --------------------------------------------------------------------------- #
# 1. PRISMA flow
# --------------------------------------------------------------------------- #
def prisma_figure(flow):
    """PRISMA 2020 flow. A diagram, not a chart: boxes and arrows, no axes."""
    fig, ax = plt.subplots(figsize=(9.5, 8.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

    def box(x, y, w, h, lines, face="#f4f7fb", edge=BLUE):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12,rounding_size=0.10",
                                    facecolor=face, edgecolor=edge, linewidth=1.1))
        ax.text(x + w / 2, y + h / 2, "\n".join(lines), ha="center", va="center",
                fontsize=8.4, color=INK, linespacing=1.45)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=11, color="#888888", linewidth=1.0))

    stage = lambda y, t: ax.text(0.15, y, t, rotation=90, va="center", ha="center",
                                 fontsize=8.6, color=MUTED, fontweight="bold")

    ident = flow["identified"]
    pending = flow.get("identified_not_screened") or {}
    ident_lines = ["Records identified"] + [f"  {k}: {v:,}" for k, v in ident.items()]
    if pending:
        ident_lines += ["", "Identified, not yet screened"] + \
                       [f"  {k}: {v:,}" for k, v in pending.items()]
    stage(8.65, "Identification")
    box(1.1, 7.75, 4.6, 1.8, ident_lines)
    # Pre-screening removals. Duplicates and publication-form exclusions are both
    # removed before screening under PRISMA 2020, so they share one box.
    removed = flow.get("removed_before_screening")
    if not removed and flow.get("duplicates"):
        removed = {"duplicate records": flow["duplicates"]}
    if removed:
        lines = [f"Removed before screening: n = {sum(removed.values()):,}"] + \
                [f"  {k}: {v:,}" for k, v in sorted(removed.items(), key=lambda kv: -kv[1])]
        box(6.2, 7.85, 3.3, 1.6, lines, face="#f7f7f7", edge="#b0b0b0")
        arrow(5.7, 8.65, 6.2, 8.65)

    stage(6.45, "Screening")
    box(1.1, 5.95, 4.6, 1.0, ["Records screened (title / abstract)", f"n = {flow['screened']:,}"])
    arrow(3.4, 7.75, 3.4, 6.95)

    excl = flow["excluded_screening"]
    excl_lines = [f"Excluded at screening: n = {sum(excl.values()):,}"]
    if len(excl) > 1:
        excl_lines += [f"  {k}: {v:,}" for k, v in sorted(excl.items(), key=lambda kv: -kv[1])]
    elif excl:
        excl_lines = [f"Excluded at screening", f"({next(iter(excl))})", f"n = {sum(excl.values()):,}"]
    box(6.2, 5.55, 3.3, 1.8, excl_lines, face="#fdf6f2", edge=ORANGE)
    arrow(5.7, 6.45, 6.2, 6.45)

    stage(4.3, "Eligibility")
    box(1.1, 3.8, 4.6, 1.0, ["Records assessed for eligibility", f"n = {flow['eligible']:,}"])
    arrow(3.4, 5.95, 3.4, 4.8)

    if flow.get("excluded_eligibility"):
        e2 = flow["excluded_eligibility"]
        lines = [f"Excluded, not primary research: n = {sum(e2.values()):,}"]
        if len(e2) > 1:
            lines += [f"  {k}: {v:,}" for k, v in sorted(e2.items(), key=lambda kv: -kv[1])[:5]]
        else:
            lines = ["Excluded, not primary research",
                     f"({next(iter(e2))})", f"n = {sum(e2.values()):,}"]
        box(6.2, 3.5, 3.3, 1.6, lines, face="#fdf6f2", edge=ORANGE)
        arrow(5.7, 4.3, 6.2, 4.3)

    stage(2.0, "Included")
    box(1.1, 1.4, 4.6, 1.2, ["Studies included in the review",
                             f"n = {flow['included']:,}"], face="#f1f9f5", edge=GREEN)
    arrow(3.4, 3.8, 3.4, 2.6)

    ax.set_title("Study selection", fontsize=11, color=INK, loc="left", pad=6)
    fig.text(0.02, 0.015, flow.get("note", ""), fontsize=7, color=MUTED)
    _save(fig, "review_prisma.png")


# --------------------------------------------------------------------------- #
# 2. Screened vs included per year
# --------------------------------------------------------------------------- #
def year_figure(store):
    raw = store.get("records", [])
    recs = list(raw.values()) if isinstance(raw, dict) else list(raw)
    if not recs:
        return
    years = sorted({int(r["year"]) for r in recs if str(r.get("year") or "").isdigit()})
    years = [y for y in years if y >= config.REVIEW_START_YEAR]
    inc = collections.Counter(int(r["year"]) for r in recs
                              if r.get("include") and str(r.get("year") or "").isdigit())
    exc = collections.Counter(int(r["year"]) for r in recs
                              if not r.get("include") and str(r.get("year") or "").isdigit())
    fig, ax = plt.subplots(figsize=(9, 4.2))
    inc_v = [inc.get(y, 0) for y in years]
    exc_v = [exc.get(y, 0) for y in years]
    ax.bar(years, inc_v, color=BLUE, label="Included", width=0.74)
    ax.bar(years, exc_v, bottom=inc_v, color=GRAY, label="Excluded at screening", width=0.74)
    # Direct labels on the included series (contrast relief; every 2nd year to avoid collision)
    for y, v in zip(years, inc_v):
        if v and y % 2 == 0:
            ax.text(y, v / 2, f"{v}", ha="center", va="center", fontsize=6.5, color="white")
    _style(ax); _year_axis(ax, years); _mark_partial(ax, years)
    ax.set_ylabel("Records")
    ax.set_title("Records screened per publication year", fontsize=11, color=INK, loc="left")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    _save(fig, "review_by_year.png")


# --------------------------------------------------------------------------- #
# 3. Composition over time (modality / task)
# --------------------------------------------------------------------------- #
def composition_over_time(rows, field, colors, order, title, fname, min_year=2015):
    per = collections.defaultdict(collections.Counter)
    for r in rows:
        y = r.get("year")
        if not str(y or "").isdigit() or int(y) < min_year:
            continue
        for v in [x.strip() for x in (r.get(field) or "").split(";") if x.strip()]:
            if field == "task":
                v = TASK_FOLD.get(v, v)
            per[int(y)][v] += 1
    if not per:
        return
    years = sorted(per)
    cats = [c for c in order if any(per[y].get(c) for y in years)]
    fig, ax = plt.subplots(figsize=(9, 4.4))
    bottom = [0] * len(years)
    for c in cats:
        vals = [per[y].get(c, 0) for y in years]
        ax.bar(years, vals, bottom=bottom, color=colors.get(c, GRAY), label=c,
               width=0.74, linewidth=0.6, edgecolor="white")  # 2px-equivalent surface gap
        bottom = [b + v for b, v in zip(bottom, vals)]
    # The stack total is mentions, not papers; a paper naming CT and MRI counts
    # in both segments. Labelled as the stack total so it cannot be read as a
    # paper count.
    for y, t in zip(years, bottom):
        ax.text(y, t + max(bottom) * 0.015, str(t), ha="center", fontsize=6.5, color=MUTED)
    _style(ax); _year_axis(ax, years); _mark_partial(ax, years)
    ax.set_ylabel("Mentions (a paper may name several)")
    ax.set_title(title, fontsize=11, color=INK, loc="left")
    ax.legend(frameon=False, fontsize=7.6, ncol=3, loc="upper left")
    _save(fig, fname)


# --------------------------------------------------------------------------- #
# 4. Simple horizontal category bars
# --------------------------------------------------------------------------- #
def category_bar(counter, colors, title, fname, denom=None, xlabel="Included papers"):
    if not counter:
        return
    items = counter.most_common()
    labels = [k for k, _ in items][::-1]
    vals = [v for _, v in items][::-1]
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(labels) + 1.6))
    ax.barh(labels, vals, color=[colors.get(l, GRAY) for l in labels], height=0.66)
    span = max(vals)
    for i, v in enumerate(vals):
        txt = f"{v}" + (f"  ({100 * v / denom:.1f}%)" if denom else "")
        ax.text(v + span * 0.012, i, txt, va="center", fontsize=8, color=INK)
    _style_x(ax)
    ax.set_xlim(0, span * 1.18)
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=11, color=INK, loc="left")
    _save(fig, fname)


# --------------------------------------------------------------------------- #
# 5. Validation strategy by era
# --------------------------------------------------------------------------- #
def validation_era_figure(rows, eras=((2005, 2014), (2015, 2019), (2020, 2022), (2023, 2026))):
    per = {}
    for lo, hi in eras:
        sub = [r for r in rows if str(r.get("year") or "").isdigit() and lo <= int(r["year"]) <= hi]
        if sub:
            per[f"{lo}-{hi}"] = (collections.Counter(
                (x.get("validation") or "none / not stated") for x in sub), len(sub))
    if not per:
        return
    labels = list(per)
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    bottom = [0.0] * len(labels)
    for cat in VALIDATION_ORDER:
        vals = [100 * per[l][0].get(cat, 0) / per[l][1] for l in labels]
        ax.bar(labels, vals, bottom=bottom, color=VALIDATION_COLOR[cat], label=cat,
               width=0.62, linewidth=0.6, edgecolor="white")
        for i, (b, v) in enumerate(zip(bottom, vals)):
            if v >= 6:
                ax.text(i, b + v / 2, f"{v:.0f}%", ha="center", va="center",
                        fontsize=7.5, color="white" if cat != "none / not stated" else INK)
        bottom = [b + v for b, v in zip(bottom, vals)]
    _style(ax)
    ax.set_ylim(0, 108)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("Share of included papers (%)")
    ax.set_title("Strongest validation reported, by era", fontsize=11, color=INK, loc="left")
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="lower center", bbox_to_anchor=(0.5, -0.30))
    for i, l in enumerate(labels):
        ax.text(i, 101.5, f"n = {per[l][1]}", ha="center", fontsize=7.5, color=MUTED)
    _save(fig, "review_validation_era.png")


# --------------------------------------------------------------------------- #
# 6. The translational funnel
# --------------------------------------------------------------------------- #
def funnel_figure(steps, note=""):
    """Descending horizontal bars, not a tapered funnel: a funnel graphic distorts
    area and cannot be read against an axis. Each bar is labelled with its count
    and its share of the corpus."""
    labels = [s[0] for s in steps][::-1]
    vals = [s[1] for s in steps][::-1]
    top = max(vals)
    fig, ax = plt.subplots(figsize=(8.6, 0.5 * len(labels) + 1.7))
    shades = [BLUE] * len(labels)
    ax.barh(labels, vals, color=shades, height=0.62)
    for i, v in enumerate(vals):
        ax.text(v + top * 0.012, i, f"{v:,}   ({100 * v / top:.1f}% of corpus)",
                va="center", fontsize=8, color=INK)
    _style_x(ax)
    ax.set_xlim(0, top * 1.30)
    ax.set_xlabel("Papers")
    ax.set_title("From published study to a tool a child could benefit from",
                 fontsize=11, color=INK, loc="left")
    if note:
        fig.subplots_adjust(bottom=0.30)
        fig.text(0.02, 0.02, note, fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    _save(fig, "review_funnel.png")


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    store = load_store()
    if not rows:
        print("No paper database found; nothing to draw.")
        return
    n = len(rows)
    print(f"Drawing review figures from {n} included papers...")

    flow_path = config.PROCESSED_DIR / "review_flow.json"
    if flow_path.exists():
        prisma_figure(json.loads(flow_path.read_text(encoding="utf-8")))
    year_figure(store)
    composition_over_time(rows, "modality", MODALITY_COLOR, config.PAPER_DB_MODALITIES,
                          "Included papers by imaging modality and year",
                          "review_modality_year.png")
    composition_over_time(rows, "task", TASK_COLOR, TASK_ORDER,
                          "Included papers by task (what the model produces) and year",
                          "review_task_year.png")
    category_bar(multi(rows, "age_groups"), AGE_COLOR,
                 "Included papers by age group", "review_age_groups.png", denom=n)
    category_bar(collections.Counter(r.get("data_source") or "not stated" for r in rows),
                 {"single center": YELLOW, "multi center": BLUE, "public dataset": AQUA,
                  "not stated": GRAY},
                 "Data source", "review_data_source.png", denom=n)
    category_bar(collections.Counter(r.get("release_status") or "unclear" for r in rows),
                 {"open-source": GREEN, "commercial": ORANGE, "unreleased": VIOLET,
                  "unclear": GRAY},
                 "Model availability as stated in the paper", "review_release.png", denom=n)
    validation_era_figure(rows)

    ext = sum(1 for r in rows if r.get("validation") == "external / multi-center")
    rdr = sum(1 for r in rows if r.get("validation") == "reader study")
    pro = sum(1 for r in rows if r.get("validation") == "prospective")
    code = sum(1 for r in rows if (r.get("code_url") or "").strip())
    comm = sum(1 for r in rows if r.get("release_status") == "commercial")
    funnel_figure(
        [("Included studies", n),
         ("External / multi-center validation", ext),
         ("Reader study", rdr),
         ("Prospective", pro),
         ("Code or model available", code),
         ("Commercial product involved", comm)],
        note="Validation categories are mutually exclusive (the strongest reported). "
             "Counts are of included studies; see Table 4 for cleared devices.",
    )
    print("done.")


if __name__ == "__main__":
    main()
