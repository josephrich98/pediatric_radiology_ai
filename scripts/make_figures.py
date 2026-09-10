#!/usr/bin/env python3
"""Render every figure used in the reports and slides from processed data.

Outputs PNGs to figures/. Safe to run after the collectors; each figure is
skipped if its input file is missing.

Chart conventions (kept deliberately simple so every figure reads the same):
one axis per chart (no twin axes), a fixed categorical palette assigned in a
fixed order, thin marks, recessive grids, integer year ticks, and the current
partial year labelled "YTD" (a text label only; no shading).
"""

from __future__ import annotations

import re
import shutil
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.transforms  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MultipleLocator  # noqa: E402

from pedrad_ai import analysis, config, utils  # noqa: E402

FIG = config.FIGURE_DIR
# Fixed categorical order (validated for color-vision-deficiency separation).
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948", "#8c8c8c"]
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED, GRAY = PALETTE
# The 9th (gray) category is solid; no hatching anywhere.
HATCHES = [None] * 9
# Modality colors are fixed by name so the same modality has the same color on
# every chart (adult and pediatric alike).
MODALITY_COLOR = {
    "x-ray / radiography": BLUE, "CT": ORANGE, "MRI": AQUA, "ultrasound": YELLOW,
    "mammography": MAGENTA, "nuclear / PET": GREEN,
}
TASK_COLOR = {t: PALETTE[i] for i, t in enumerate(config.TASK_TERMS)}
TASK_HATCH = {t: HATCHES[i] for i, t in enumerate(config.TASK_TERMS)}


def _load(name):
    p = config.PROCESSED_DIR / name
    return utils.load_json(p) if p.exists() else None


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=160)
    plt.close(fig)
    print(f"  wrote {name}")


def _style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e3e3e3", linewidth=0.6)
    ax.set_axisbelow(True)


def _year_axis(ax, years):
    """Integer year ticks every 2 years (no fractional-year ticks)."""
    if not years:
        return
    lo, hi = min(years), max(years)
    start = lo if lo % 2 == 0 else lo + 1
    ax.set_xticks(range(start, hi + 1, 2))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.set_xlim(lo - 0.6, hi + 0.6)


def _mark_partial(ax, years):
    """Annotate the current (year-to-date) year so it is not read as a drop."""
    if years and max(years) == config.PARTIAL_YEAR:
        ax.text(config.PARTIAL_YEAR, ax.get_ylim()[1] * 0.97, "YTD", ha="center", va="top", fontsize=8, color="0.35")


# --------------------------------------------------------------------------- #
# Publication trends
# --------------------------------------------------------------------------- #
def trend_figures(counts, preprints=None):
    """``counts`` is the merged (PubMed + arXiv preprint) series; ``preprints``
    only decides the axis label (one solid bar per series)."""
    rows = analysis.fractions_over_time(counts)
    if not rows:
        return
    years = [r["year"] for r in rows]

    # Nested bars: pediatric radiology AI is a subset of radiology AI, so it is
    # drawn on top of (inside) the radiology-AI bar for the same year.
    has_pre = bool(preprints and (preprints.get("yearly") or {}).get("radiology_ai"))
    rad = [r["radiology_ai"] for r in rows]
    ped = [r["pediatric_radiology_ai"] for r in rows]
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.bar(years, rad, width=0.8, color=BLUE, label="Radiology AI" + (" (PubMed + arXiv)" if has_pre else ""))
    ax1.bar(years, ped, width=0.8, color=GREEN, label="Pediatric radiology AI (subset)")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Publications per year (PubMed + arXiv preprints)" if has_pre else "Publications per year (PubMed)")
    ax1.yaxis.set_major_formatter(lambda v, _: f"{int(v):,}")
    _style(ax1)
    ax1.annotate(f"{rad[-1]:,}", (years[-1], rad[-1]), xytext=(0, 3),
                 textcoords="offset points", ha="center", va="bottom", fontsize=8)
    ax1.annotate(f"{ped[-1]:,}", (years[-1], ped[-1]), xytext=(0, 3),
                 textcoords="offset points", ha="center", va="bottom", fontsize=8, color="white")
    if len(rad) >= 2:
        ax1.annotate(f"{rad[-2]:,}", (years[-2], rad[-2]), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8)
    ax1.legend(loc="upper left", frameon=False)
    _year_axis(ax1, years)
    _mark_partial(ax1, years)
    ax1.set_title("Growth of radiology AI and pediatric radiology AI publications")
    _save(fig, "radiology_ai_trend.png")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(years, [r["pediatric_share_of_radiology_ai"] * 100 for r in rows], color=GREEN, marker="s", linewidth=2)
    ax.set_xlabel("Year")
    ax.set_ylabel("Pediatric share of radiology AI (%)")
    ax.set_title("Pediatric fraction of radiology-AI publications")
    _style(ax)
    _year_axis(ax, years)
    _mark_partial(ax, years)
    _save(fig, "pediatric_share.png")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(years, [r["radiology_ai"] for r in rows], color=BLUE, marker="o", linewidth=2, label="Radiology AI")
    ax.plot(years, [r["pediatric_radiology_ai"] for r in rows], color=GREEN, marker="s", linewidth=2, label="Pediatric radiology AI")
    ax.set_yscale("log")
    ax.set_xlabel("Year")
    ax.set_ylabel("Publications per year (log scale)")
    ax.set_title("Radiology AI vs pediatric radiology AI publication volume")
    _style(ax)
    _year_axis(ax, years)
    _mark_partial(ax, years)
    ax.legend(frameon=False)
    _save(fig, "volume_comparison.png")


def breakdown_figure(counts, prefix, denom, title, fname, colors):
    rows = analysis.breakdown_table(counts, prefix, denom_series=denom)
    if not rows:
        return
    labels = [r["label"] for r in rows][::-1]
    fracs = [r.get("fraction", 0) * 100 for r in rows][::-1]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(labels, fracs, color=[colors.get(l, GRAY) for l in labels])
    ax.set_xlabel("Share of records mentioning the term group (%)")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    for i, v in enumerate(fracs):
        ax.text(v + 0.3, i, f"{v:.0f}%", va="center", fontsize=9)
    _save(fig, fname)


# --------------------------------------------------------------------------- #
# Modality x task sub-stratification (stacked composition)
# --------------------------------------------------------------------------- #
def crosstab_figure(tab, rows_are, title, fname, exclude_rows=()):
    """Bars = share of the corpus mentioning each row label; each bar is split
    by the *composition* of column-label mentions within it (overlapping
    labels, normalised to the bar length so the picture is proportional).
    ``exclude_rows`` drops rows that are not meaningful for the corpus (the
    pediatric chart drops mammography: its hits are adult breast papers whose
    abstracts happen to mention children)."""
    if not tab:
        return
    total = tab["total"] or 1
    cells = tab["cells"]
    if rows_are == "modality":
        row_labels = [m for m in config.MODALITY_TERMS if m not in exclude_rows]
        col_labels = list(config.TASK_TERMS)
        col_color, col_hatch = TASK_COLOR, TASK_HATCH
        row_tot = tab["row_totals"]
        get = lambda r, c: cells[r][c]
    else:
        row_labels = list(config.TASK_TERMS)
        col_labels = list(config.MODALITY_TERMS)
        col_color, col_hatch = MODALITY_COLOR, {m: None for m in MODALITY_COLOR}
        row_tot = tab["col_totals"]
        get = lambda r, c: cells[c][r]
    order = sorted(row_labels, key=lambda r: row_tot.get(r, 0))
    fig, ax = plt.subplots(figsize=(10, 5.2))
    y = range(len(order))
    for i, r in enumerate(order):
        share = 100 * row_tot.get(r, 0) / total
        parts = [get(r, c) for c in col_labels]
        s = sum(parts) or 1
        left = 0.0
        for c, v in zip(col_labels, parts):
            w = share * v / s
            if w <= 0:
                continue
            ax.barh(i, w, left=left, color=col_color[c], hatch=col_hatch.get(c), edgecolor="white", linewidth=0.8,
                    label=c if i == len(order) - 1 else None)
            if w > 3.5:
                ax.text(left + w / 2, i, f"{100 * v / s:.0f}%", ha="center", va="center", fontsize=7, color="white")
            left += w
        ax.text(share + 0.4, i, f"{share:.0f}%", va="center", fontsize=9)
    ax.set_yticks(list(y))
    ax.set_yticklabels(order)
    ax.set_xlabel("Percentage of papers")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, max(100 * row_tot.get(r, 0) / total for r in order) * 1.12 + 3)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=7.5, loc="lower right", frameon=False, ncol=1)
    _save(fig, fname)


# --------------------------------------------------------------------------- #
# Clinical problems addressed (pediatric corpus, per era)
# --------------------------------------------------------------------------- #
def problems_figure(prob, fname="ped_problems.png"):
    """Grouped horizontal bars: papers per clinical problem, one bar per era,
    sorted by the recent era. Labels carry the count and share of the era's
    pediatric radiology-AI papers."""
    if not prob or not prob.get("counts"):
        return
    eras = [e["label"] for e in prob["eras"]]
    totals = prob["totals"]
    rows = sorted(prob["counts"].items(), key=lambda kv: kv[1].get(eras[-1], 0))
    fig, ax = plt.subplots(figsize=(10, 6.4))
    h = 0.8 / len(eras)
    era_colors = [GRAY, GREEN, BLUE]
    for j, era in enumerate(eras):
        ys = [i + (j - (len(eras) - 1) / 2) * h for i in range(len(rows))]
        vals = [c.get(era, 0) for _, c in rows]
        ax.barh(ys, vals, height=h, color=era_colors[j % len(era_colors)], label=f"{era} (n = {totals.get(era, 0):,})")
        for y, v in zip(ys, vals):
            share = 100 * v / (totals.get(era) or 1)
            ax.text(v + max(vals) * 0.01, y, f"{v:,} ({share:.0f}%)", va="center", fontsize=6.5)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r for r, _ in rows], fontsize=8)
    src = "PubMed + preprints" if prob.get("preprint_totals") else "PubMed"
    ax.set_xlabel(f"Pediatric radiology-AI papers naming the problem ({src}, title/abstract)")
    ax.set_title("Which clinical problems pediatric radiology AI addresses, by era")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, max(c.get(e, 0) for _, c in rows for e in eras) * 1.2)
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    _save(fig, fname)


# --------------------------------------------------------------------------- #
# Society / venue lines
# --------------------------------------------------------------------------- #
def rsna_figure(rsna):
    ry = [r["year"] for r in rsna]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(ry, [r["rsna_ai_fraction"] * 100 for r in rsna], color=VIOLET, marker="^", linewidth=2)
    ax.set_xlabel("Year")
    ax.set_ylabel("AI share of RSNA-journal articles (%)")
    ax.set_title("AI share of RSNA flagship journals\n(Radiology, RadioGraphics, Radiology: AI)")
    _style(ax)
    _year_axis(ax, ry)
    _mark_partial(ax, ry)
    _save(fig, "rsna_ai_share.png")


def venue_line_figure(rows, value_key, group_key, title, ylabel, fname):
    if not rows:
        return
    groups = sorted({r[group_key] for r in rows})
    fig, ax = plt.subplots(figsize=(8.5, 5))
    markers = "os^Dv<>P*"
    for i, g in enumerate(groups):
        gr = sorted((r for r in rows if r[group_key] == g), key=lambda r: r["year"])
        xs = [r["year"] for r in gr]
        ys = [r[value_key] * 100 for r in gr]
        if any(ys):
            ax.plot(xs, ys, marker=markers[i % len(markers)], color=PALETTE[i % 8], linewidth=2, label=g)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    _style(ax)
    _year_axis(ax, [r["year"] for r in rows])
    ax.legend(frameon=False)
    _save(fig, fname)


# --------------------------------------------------------------------------- #
# Biggest players
# --------------------------------------------------------------------------- #
def top_papers_figure(papers, title, fname, color, n=12, width=78):
    """Full titles (wrapped to two lines) so nothing is truncated on the slide."""
    if not papers:
        return
    top = papers[:n][::-1]
    labels = ["\n".join(textwrap.wrap(p.get("title") or "", width=width, max_lines=2, placeholder=" …")) for p in top]
    cites = [p.get("citation_count", 0) for p in top]
    fig, ax = plt.subplots(figsize=(13, 0.52 * len(top) + 1.0))
    ax.barh(range(len(top)), cites, color=color, height=0.72)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Citations (OpenAlex)")
    ax.xaxis.set_major_formatter(lambda v, _: f"{int(v):,}")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    for i, (c, p) in enumerate(zip(cites, top)):
        ax.text(c + max(cites) * 0.01, i, f"{c:,}  ({p.get('year')})", va="center", fontsize=8)
    ax.set_xlim(0, max(cites) * 1.22)
    _save(fig, fname)


def github_board(repos, n=15):
    seen = {}
    for bucket in repos.values():
        for r in bucket:
            fn = r.get("full_name")
            if fn and (fn not in seen or r["stars"] > seen[fn]["stars"]):
                seen[fn] = r
    return sorted(seen.values(), key=lambda r: r["stars"], reverse=True)[:n]


def github_figure(repos):
    if not repos:
        return
    board = github_board(repos)[::-1]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh([r["full_name"] for r in board], [r["stars"] for r in board], color=ORANGE, height=0.72)
    ax.set_xlabel("GitHub stars")
    ax.xaxis.set_major_formatter(lambda v, _: f"{int(v):,}")
    ax.set_title("Most-starred open-source radiology / medical-imaging AI tools")
    ax.tick_params(axis="y", labelsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    for i, r in enumerate(board):
        ax.text(r["stars"] + 60, i, f"{r['stars']:,}", va="center", fontsize=7.5)
    ax.set_xlim(0, board[-1]["stars"] * 1.15)
    _save(fig, "github_stars.png")


# --------------------------------------------------------------------------- #
# Newsletters
# --------------------------------------------------------------------------- #
def _stacked_by_source(summary, key, ylabel, title, fname, min_year=2016):
    by_year = summary.get("by_year", {}) if summary else {}
    if not by_year:
        return
    years = sorted({int(y) for s in by_year.values() for y in s if y.isdigit()})
    years = [y for y in years if y >= min_year]
    if not years:
        return
    names = [n for n in summary["sources"] if n in by_year]
    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = [0] * len(years)
    for i, n in enumerate(names):
        vals = [by_year[n].get(str(y), {}).get(key, 0) for y in years]
        if not any(vals):
            continue
        ax.bar(years, vals, bottom=bottom, color=PALETTE[i % 8], label=n, edgecolor="white", linewidth=0.6)
        bottom = [b + v for b, v in zip(bottom, vals)]
    for x, b in zip(years, bottom):
        if b:
            ax.text(x, b, f"{b:,}", ha="center", va="bottom", fontsize=7.5)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(bottom + [1]) * 1.25)
    ax.set_title(title)
    _style(ax)
    _year_axis(ax, years)
    ax.legend(fontsize=8, loc="upper left", frameon=False)
    _mark_partial(ax, years)
    _save(fig, fname)


def newsletter_figures(summary):
    if not summary:
        return
    _stacked_by_source(summary, "pediatric_radiology_ai", "Pediatric radiology-AI stories",
                       "Pediatric radiology AI in newsletters and trade press", "newsletter_watch.png")
    _stacked_by_source(summary, "radiology_ai", "Radiology-AI stories (all ages)",
                       "Radiology AI in newsletters and trade press", "newsletter_radiology_ai.png")
    players = summary.get("players") or {}
    rows = [(k, v["radiology_ai"], v["pediatric_radiology_ai"]) for k, v in players.items() if v["radiology_ai"]]
    rows = sorted(rows, key=lambda r: r[1], reverse=True)[:20][::-1]
    if not rows:
        return
    fig, ax = plt.subplots(figsize=(10, 6.2))
    names = [r[0] for r in rows]
    ax.barh(names, [r[1] for r in rows], color=BLUE, height=0.72, label="Radiology-AI stories mentioning")
    ax.barh(names, [r[2] for r in rows], color=GREEN, height=0.72, label="...of which pediatric")
    for i, r in enumerate(rows):
        ax.text(r[1] + 2, i, f"{r[1]:,}" + (f"  (ped {r[2]})" if r[2] else ""), va="center", fontsize=7.5)
    ax.set_xlabel("Newsletter / trade-press stories mentioning the company or tool")
    ax.set_title("Who the trade press talks about: radiology-AI story mentions")
    ax.tick_params(axis="y", labelsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, rows[-1][1] * 1.25)
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    _save(fig, "newsletter_players.png")


# --------------------------------------------------------------------------- #
# Commercial: FDA AI-enabled devices
# --------------------------------------------------------------------------- #
def fda_figures(fda):
    if not fda or not fda.get("by_year"):
        return
    by = {int(k): v for k, v in fda["by_year"].items()}
    allp = {int(k): v for k, v in fda.get("all_panels_by_year", {}).items()}
    years = [y for y in sorted(by) if y >= 2012]
    fig, ax = plt.subplots(figsize=(9, 5))
    other = [allp.get(y, 0) - by.get(y, 0) for y in years]
    ax.bar(years, [by.get(y, 0) for y in years], color=BLUE, label="Radiology panel", edgecolor="white", linewidth=0.6)
    ax.bar(years, other, bottom=[by.get(y, 0) for y in years], color="#c9d7ea", label="All other panels", edgecolor="white", linewidth=0.6)
    for y in years:
        ax.text(y, by.get(y, 0) / 2, str(by.get(y, 0)), ha="center", va="center", fontsize=7.5, color="white")
    ax.set_xlabel("Year of FDA decision")
    ax.set_ylabel("AI-enabled devices authorized")
    ax.set_title("FDA-authorized AI-enabled medical devices per year (radiology vs all other panels)")
    _style(ax)
    _year_axis(ax, years)
    _mark_partial(ax, years)
    ax.legend(frameon=False, loc="upper left")
    _save(fig, "fda_devices_per_year.png")

    top = fda.get("top_companies", [])[:15][::-1]
    if top:
        fig, ax = plt.subplots(figsize=(9, 5.5))
        ax.barh([c["company"] for c in top], [c["devices"] for c in top], color=ORANGE, height=0.72)
        for i, c in enumerate(top):
            ax.text(c["devices"] + 0.5, i, f"{c['devices']}  ({c['first_year']}–{c['last_year']})", va="center", fontsize=7.5)
        ax.set_xlabel("Radiology AI-enabled devices authorized by FDA")
        ax.set_title("Commercial players: companies with the most FDA-authorized radiology AI devices")
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="y", labelsize=8)
        ax.set_xlim(0, top[-1]["devices"] * 1.3)
        _save(fig, "fda_companies.png")


# --------------------------------------------------------------------------- #
# Journal impact scatter
# --------------------------------------------------------------------------- #
# Which journals publish pediatric radiology AI, and how high-impact are they?
# One point per journal: x = journal impact, y = cumulative papers. Points are
# colored by what kind of journal it is, because "who publishes this work" is
# really a question about whether it lands in imaging journals, pediatrics
# journals, or the general-medicine and computational literature.
JOURNAL_KINDS = [
    ("Radiology / imaging", BLUE),
    ("Pediatrics", ORANGE),
    ("General medicine / science", GREEN),
    ("Other specialty / technical", GRAY),
]
_KIND_PATTERNS = [
    ("Radiology / imaging", (
        "radiolog", "roentgen", "imaging", "magnetic resonance", "ultrasound", "ultrason",
        "sonograph", "tomograph", "nuclear medicine", "neuroimag", "radiograph", "radiat",
        "medical physics", "echocardiograph",
    )),
    ("Pediatrics", ("pediatr", "paediatr", "child", "neonat", "fetal", "perinat", "adolescen")),
    ("General medicine / science", (
        "nature", "lancet", "jama", "new england journal", "science", "scientific reports",
        "plos one", "bmj", "cell reports medicine", "npj", "communications medicine",
        "annals of internal", "medicine (baltimore", "heliyon", "cureus", "plos digital",
    )),
]


def _journal_kind(name: str) -> str:
    low = (name or "").lower()
    for kind, pats in _KIND_PATTERNS:
        if any(p in low for p in pats):
            return kind
    return "Other specialty / technical"


def _cumulative(counts: dict, upto: int, since: int) -> int:
    return sum(n for y, n in counts.items() if since <= int(y) <= upto)


# PubMed's full journal titles carry the subtitle ("Journal of ultrasound in
# medicine : official journal of the American Institute of ..."), which is
# unreadable as a point label. OpenAlex's display_name is used when the lookup
# matched; this trims whatever is left.
def _journal_label(name: str, limit: int = 34) -> str:
    label = re.split(r"\s+:\s+|\.\s+(?:official|the official)\b", name, maxsplit=1)[0]
    label = re.sub(r"\s*\([^)]*\)\s*$", "", label).strip(" .")
    if len(label) > limit:
        label = label[: limit - 1].rstrip() + "\u2026"
    return label


def _place_labels(ax, points, fontsize=7.0):
    """Label every point without overlaps: greedy placement + leader lines.

    Each label is tried at a ring of candidate offsets around its marker,
    nearest first, and takes the first that collides with neither an
    already-placed label nor another marker and stays inside the axes. Labels
    that end up away from their dot get a thin leader line back to it. A
    physics-style repel diverges on a cluster this dense — labels drift off the
    axes and lose their points — so placement is discrete and greedy. Candidate
    boxes are found by translating each label's measured size rather than by
    redrawing the figure, which is what makes trying seventy positions per
    label cheap enough to do twelve times for the animation.
    """
    fig = ax.figure
    # The leader lines below are ordinary plot calls, and a plot call rescales
    # the axes: a label anchor sitting just outside the data range would widen
    # the axis under it, which across the animation means limits that no longer
    # match frame to frame.
    ax.set_autoscale_on(False)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    # Candidate offsets in points, ordered by distance. Right and left first (a
    # label reads best beside its dot), then rings of diagonals.
    candidates = [(8.0, 0.0), (-8.0, 0.0)]
    for r in (9, 13, 18, 24, 31, 39, 48, 58, 70, 84, 100, 118, 140, 165):
        for dx, dy in ((1, 0.5), (-1, 0.5), (1, -0.5), (-1, -0.5),
                       (0.3, 1), (0.3, -1), (-0.3, 1), (-0.3, -1)):
            candidates.append((r * dx + (8 if dx > 0 else -8), r * dy))

    dpi_scale = fig.dpi / 72.0  # offsets are in points, bounding boxes in pixels
    Bbox = matplotlib.transforms.Bbox

    texts, sizes, xy_px = [], [], []
    for x, y, label in points:
        t = ax.annotate(label, (x, y), xytext=(8, 0), textcoords="offset points",
                        fontsize=fontsize, color="0.15", va="center", ha="left",
                        annotation_clip=False, zorder=4)
        texts.append(t)
        box = t.get_window_extent(renderer=renderer)
        sizes.append((box.width, box.height))
        xy_px.append(ax.transData.transform((x, y)))

    marker_boxes = [Bbox.from_bounds(px - 5, py - 5, 10, 10) for px, py in xy_px]
    axes_box = ax.get_window_extent(renderer=renderer)

    placed = []
    # Biggest counts first: the journals that matter most get the closest slots.
    for i in sorted(range(len(points)), key=lambda k: -points[k][1]):
        (px, py), (w, h) = xy_px[i], sizes[i]
        chosen = None
        for dx, dy in candidates:
            ox, oy = dx * dpi_scale, dy * dpi_scale
            x0 = px + ox if dx >= 0 else px + ox - w
            box = Bbox.from_bounds(x0, py + oy - h / 2, w, h)
            if (box.x0 < axes_box.x0 or box.x1 > axes_box.x1
                    or box.y0 < axes_box.y0 or box.y1 > axes_box.y1):
                continue
            if any(box.overlaps(b) for b in placed):
                continue
            if any(box.overlaps(b) for j, b in enumerate(marker_boxes) if j != i):
                continue
            chosen = (dx, dy, box)
            break
        if chosen is None:  # keep the journal on the chart rather than dropping it
            chosen = (8.0, 0.0, Bbox.from_bounds(px + 8 * dpi_scale, py - h / 2, w, h))
        dx, dy, box = chosen
        texts[i].set_ha("left" if dx >= 0 else "right")
        texts[i].set_position((dx, dy))
        placed.append(box)
        if abs(dx) > 12 or abs(dy) > 6:
            # Leader line from the dot to whichever end of the label faces it.
            # Drawn as a plain line in data coordinates: an annotation anchored
            # to the text artist (xycoords=text) makes tight_layout recurse.
            end_px = (box.x0 - 1.5, box.y0 + h * 0.45) if dx >= 0 else (box.x1 + 1.5, box.y0 + h * 0.45)
            lx, ly = ax.transData.inverted().transform(end_px)
            ax.plot([points[i][0], lx], [points[i][1], ly], linewidth=0.5,
                    color="0.72", zorder=2, solid_capstyle="butt")
    return placed


def _journal_scatter(rows, *, upto, since, appear_at, xlim, ylim, impact_label,
                     title, subtitle=None, fontsize=7.0):
    """One frame of the scatter. ``rows`` is already the plotted universe."""
    pts = []
    for r in rows:
        n = _cumulative(r["counts"], upto, since)
        if n < appear_at:
            continue
        pts.append((float(r["impact_factor"]), n, _journal_label(r["journal"]),
                    _journal_kind(r["journal"])))

    fig, ax = plt.subplots(figsize=(11.5, 6.3))
    for kind, color in JOURNAL_KINDS:
        sel = [p for p in pts if p[3] == kind]
        ax.scatter([p[0] for p in sel], [p[1] for p in sel], s=46, color=color,
                   edgecolor="white", linewidth=0.8, zorder=3,
                   label=f"{kind} ({len(sel)})")
    ax.set_xscale("log")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xlabel(impact_label)
    ax.set_ylabel(f"Pediatric radiology AI papers, {since}\u2013{upto} (cumulative)")
    if title:
        ax.set_title(title, loc="left")
    if subtitle:
        ax.set_title(subtitle, loc="right", fontsize=11, color="0.35")
    # A log axis labelled only at 1 and 10 gives the reader nothing to place a
    # point against, and this range spans barely one decade: label the halves.
    lo, hi = xlim
    ticks = [t for t in (0.3, 0.5, 0.7, 1, 1.5, 2, 3, 5, 7, 10, 15, 20, 30, 50) if lo <= t <= hi]
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color="#e8e8e8", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    if pts:
        _place_labels(ax, [(p[0], p[1], p[2]) for p in pts], fontsize=fontsize)
    return fig


def _impact_label(data):
    return ("Journal impact factor" if data.get("n_overrides")
            else "Journal impact (OpenAlex 2-year mean citedness)")


def journal_impact_figures(data):
    """Cumulative scatter per year, an animated GIF, and a 2023-present still."""
    rows = [r for r in ((data or {}).get("journals") or []) if r.get("impact_factor") is not None]
    if not rows:
        print("  ! journal_impact.json has no impact numbers; skipping the scatter")
        return
    start, end = data["start_year"], data["end_year"]
    label = _impact_label(data)
    title = "Which journals publish pediatric radiology AI"

    # The plotted universe is fixed by the *final* year, so a journal never pops
    # into the middle of the animation; each point simply rises as its count
    # accumulates. Axis limits are fixed for the same reason.
    universe = [r for r in rows if _cumulative(r["counts"], end, start) >= config.JOURNAL_MIN_PAPERS]
    if not universe:
        return
    ifs = [float(r["impact_factor"]) for r in universe]
    ymax = max(_cumulative(r["counts"], end, start) for r in universe)
    xlim = (min(ifs) * 0.8, max(ifs) * 1.45)
    ylim = (0, ymax * 1.14)

    frames = []
    for year in range(start, end + 1):
        fig = _journal_scatter(
            universe, upto=year, since=start, appear_at=config.JOURNAL_APPEAR_AT,
            xlim=xlim, ylim=ylim, impact_label=label, title=title,
            subtitle=f"{start}\u2013{year}" + (" YTD" if year == config.PARTIAL_YEAR else ""),
        )
        name = f"journal_impact_{year}.png"
        _save(fig, name)
        frames.append(FIG / name)

    # The slide still is re-rendered without the in-chart title: Beamer puts
    # that title above the figure already, and the space buys a larger plot.
    _save(_journal_scatter(
        universe, upto=end, since=start, appear_at=config.JOURNAL_APPEAR_AT,
        xlim=xlim, ylim=ylim, impact_label=label, title=None,
        subtitle=f"{start}\u2013{end}" + (" YTD" if end == config.PARTIAL_YEAR else ""),
    ), "journal_impact.png")

    try:
        from PIL import Image
    except ImportError:
        print("  ! Pillow not installed; skipping journal_impact.gif")
    else:
        imgs = [Image.open(f).convert("RGB") for f in frames]
        # 900 ms a year, and the final complete frame holds for 4 s.
        imgs[0].save(FIG / "journal_impact.gif", save_all=True, append_images=imgs[1:],
                     duration=[900] * (len(imgs) - 1) + [4000], loop=0)
        print(f"  wrote journal_impact.gif ({len(imgs)} frames)")

    recent = 2023
    recent_universe = [r for r in rows
                       if _cumulative(r["counts"], end, recent) >= config.JOURNAL_MIN_PAPERS_RECENT]
    if recent_universe:
        rymax = max(_cumulative(r["counts"], end, recent) for r in recent_universe)
        rifs = [float(r["impact_factor"]) for r in recent_universe]
        fig = _journal_scatter(
            recent_universe, upto=end, since=recent, appear_at=1,
            xlim=(min(rifs) * 0.8, max(rifs) * 1.45), ylim=(0, rymax * 1.14),
            impact_label=label, title=None,
            subtitle=f"{recent}\u2013{end}" + (" YTD" if end == config.PARTIAL_YEAR else ""),
        )
        _save(fig, f"journal_impact_{recent}_{end}.png")


# --------------------------------------------------------------------------- #
def main() -> None:
    print(f"Writing figures to {FIG}")
    preprints = _load("preprint_counts.json") or {}
    counts = _load("pubmed_yearly_counts.json")
    if counts:
        counts = analysis.add_preprints(counts, preprints)
        trend_figures(counts, preprints)
        breakdown_figure(counts, "modality", "radiology_ai",
                         "Radiology AI by imaging modality", "modality_breakdown.png", MODALITY_COLOR)
        breakdown_figure(counts, "task", "radiology_ai",
                         "Radiology AI by task", "task_breakdown.png", TASK_COLOR)
        breakdown_figure(counts, "ped_modality", "pediatric_radiology_ai",
                         "Pediatric radiology AI by modality", "ped_modality_breakdown.png", MODALITY_COLOR)
        breakdown_figure(counts, "ped_task", "pediatric_radiology_ai",
                         "Pediatric radiology AI by task", "ped_task_breakdown.png", TASK_COLOR)
    xt = _load("pubmed_crosstab.json") or {}
    xt = {k: analysis.merge_crosstab(v, (preprints.get("crosstab") or {}).get(k)) for k, v in xt.items()}
    if xt.get("radiology_ai"):
        yrs = xt["radiology_ai"]["years"]
        crosstab_figure(xt["radiology_ai"], "modality",
                        f"Radiology AI by modality, split by task ({yrs[0]}–{yrs[1]})", "modality_by_task.png")
        crosstab_figure(xt["radiology_ai"], "task",
                        f"Radiology AI by task, split by modality ({yrs[0]}–{yrs[1]})", "task_by_modality.png")
    if xt.get("pediatric_radiology_ai"):
        yrs = xt["pediatric_radiology_ai"]["years"]
        crosstab_figure(xt["pediatric_radiology_ai"], "modality",
                        f"Pediatric radiology AI by modality, split by task ({yrs[0]}–{yrs[1]})", "ped_modality_by_task.png",
                        exclude_rows=("mammography",))
        crosstab_figure(xt["pediatric_radiology_ai"], "task",
                        f"Pediatric radiology AI by task, split by modality ({yrs[0]}–{yrs[1]})", "ped_task_by_modality.png")
    rsna = _load("rsna_ai_fraction.json")
    if rsna:
        rsna_figure(rsna)
    venue_line_figure(_load("conference_ml_venues.json") or [], "radiology_fraction", "venue",
                      "Radiology / medical-imaging share of ML venues",
                      "Radiology share of papers (%)", "ml_venue_radiology_share.png")
    venue_line_figure(_load("conference_society_venues.json") or [], "ai_fraction", "society",
                      "AI share of radiology-society journals",
                      "AI share of articles (%)", "society_ai_share.png")
    top_papers_figure(_load("top_papers_radiology_ai.json") or [],
                      "Most-cited radiology AI papers", "top_papers_radiology.png", BLUE)
    top_papers_figure(_load("top_papers_pediatric_radiology_ai.json") or [],
                      "Most-cited pediatric radiology AI papers", "top_papers_pediatric.png", GREEN)
    for label, _, _ in config.ERAS:
        top_papers_figure(_load(f"top_papers_radiology_ai_{label}.json") or [],
                          f"Most-cited radiology AI papers, {label}", f"top_papers_radiology_{label}.png", BLUE)
        top_papers_figure(_load(f"top_papers_pediatric_radiology_ai_{label}.json") or [],
                          f"Most-cited pediatric radiology AI papers, {label}", f"top_papers_pediatric_{label}.png", GREEN)
    problems_figure(analysis.merge_problems(_load("pubmed_pediatric_problems.json") or {}, preprints.get("problems")) or {})
    github_figure(_load("github_repos.json") or {})
    newsletter_figures(_load("newsletter_summary.json") or {})
    fda_figures(_load("fda_ai_devices.json") or {})
    journal_impact_figures(_load("journal_impact.json") or {})
    print("Done.")


if __name__ == "__main__":
    main()
