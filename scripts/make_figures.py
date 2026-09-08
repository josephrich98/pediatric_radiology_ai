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

import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MultipleLocator  # noqa: E402

from pedrad_ai import analysis, config, utils  # noqa: E402

FIG = config.FIGURE_DIR
# Fixed categorical order (validated for color-vision-deficiency separation).
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948", "#8c8c8c"]
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED, GRAY = PALETTE
# A hatch on the 9th slot is the secondary encoding for the gray category.
HATCHES = [None] * 8 + ["////"]
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
def trend_figures(counts):
    rows = analysis.fractions_over_time(counts)
    if not rows:
        return
    years = [r["year"] for r in rows]

    # Nested bars: pediatric radiology AI is a subset of radiology AI, so it is
    # drawn on top of (inside) the radiology-AI bar for the same year.
    rad = [r["radiology_ai"] for r in rows]
    ped = [r["pediatric_radiology_ai"] for r in rows]
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.bar(years, rad, width=0.8, color=BLUE, label="Radiology AI")
    ax1.bar(years, ped, width=0.8, color=GREEN, label="Pediatric radiology AI (subset)")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Publications per year (PubMed)")
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
    ax.set_xlabel("Pediatric radiology-AI papers naming the problem (PubMed, title/abstract)")
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
def main() -> None:
    print(f"Writing figures to {FIG}")
    counts = _load("pubmed_yearly_counts.json")
    if counts:
        trend_figures(counts)
        breakdown_figure(counts, "modality", "radiology_ai",
                         "Radiology AI by imaging modality", "modality_breakdown.png", MODALITY_COLOR)
        breakdown_figure(counts, "task", "radiology_ai",
                         "Radiology AI by task", "task_breakdown.png", TASK_COLOR)
        breakdown_figure(counts, "ped_modality", "pediatric_radiology_ai",
                         "Pediatric radiology AI by modality", "ped_modality_breakdown.png", MODALITY_COLOR)
        breakdown_figure(counts, "ped_task", "pediatric_radiology_ai",
                         "Pediatric radiology AI by task", "ped_task_breakdown.png", TASK_COLOR)
    xt = _load("pubmed_crosstab.json") or {}
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
    problems_figure(_load("pubmed_pediatric_problems.json") or {})
    github_figure(_load("github_repos.json") or {})
    newsletter_figures(_load("newsletter_summary.json") or {})
    fda_figures(_load("fda_ai_devices.json") or {})
    print("Done.")


if __name__ == "__main__":
    main()
