#!/usr/bin/env python3
"""Render every figure used in the reports and slides from processed data.

Outputs PNGs to figures/. Safe to run after the collectors; each figure is
skipped if its input file is missing.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from pedrad_ai import analysis, config, utils  # noqa: E402

FIG = config.FIGURE_DIR
BLUE, RED, GREEN, PURPLE, ORANGE = "#3b6ea5", "#c44e52", "#55a868", "#8172b3", "#dd8452"


def _load(name):
    p = config.PROCESSED_DIR / name
    return utils.load_json(p) if p.exists() else None


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=150)
    plt.close(fig)
    print(f"  wrote {name}")


def trend_figures(counts):
    rows = analysis.fractions_over_time(counts)
    if not rows:
        return
    years = [r["year"] for r in rows]

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.bar(years, [r["radiology_ai"] for r in rows], color=BLUE, label="Radiology-AI papers")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Radiology-AI publications (PubMed)", color=BLUE)
    ax1.tick_params(axis="y", labelcolor=BLUE)
    ax2 = ax1.twinx()
    ax2.plot(years, [r["ai_share_of_radiology"] * 100 for r in rows], color=RED, marker="o")
    ax2.set_ylabel("AI share of all radiology (%)", color=RED)
    ax2.tick_params(axis="y", labelcolor=RED)
    plt.title("Growth of radiology AI")
    _save(fig, "radiology_ai_trend.png")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(years, [r["pediatric_share_of_radiology_ai"] * 100 for r in rows], color=GREEN, marker="s")
    ax.set_xlabel("Year")
    ax.set_ylabel("Pediatric share of radiology AI (%)")
    ax.set_title("Pediatric fraction of radiology-AI publications")
    _save(fig, "pediatric_share.png")

    # Absolute volumes: radiology AI vs pediatric radiology AI (log scale).
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(years, [r["radiology_ai"] for r in rows], color=BLUE, marker="o", label="Radiology AI")
    ax.plot(years, [r["pediatric_radiology_ai"] for r in rows], color=GREEN, marker="s", label="Pediatric radiology AI")
    ax.set_yscale("log")
    ax.set_xlabel("Year")
    ax.set_ylabel("Publications per year (log scale)")
    ax.set_title("Radiology AI vs pediatric radiology AI publication volume")
    ax.legend()
    _save(fig, "volume_comparison.png")


def breakdown_figure(counts, prefix, denom, title, fname, color):
    rows = analysis.breakdown_table(counts, prefix, denom_series=denom)
    if not rows:
        return
    labels = [r["label"] for r in rows][::-1]
    fracs = [r.get("fraction", 0) * 100 for r in rows][::-1]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(labels, fracs, color=color)
    ax.set_xlabel("Share of records (%)")
    ax.set_title(title)
    for i, v in enumerate(fracs):
        ax.text(v + 0.3, i, f"{v:.0f}%", va="center", fontsize=9)
    _save(fig, fname)


def rsna_figure(rsna):
    ry = [r["year"] for r in rsna]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(ry, [r["rsna_ai_fraction"] * 100 for r in rsna], color=PURPLE, marker="^")
    ax.set_xlabel("Year")
    ax.set_ylabel("AI share of RSNA-journal articles (%)")
    ax.set_title("AI share of RSNA flagship journals\n(Radiology, RadioGraphics, Radiology: AI)")
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
            ax.plot(xs, ys, marker=markers[i % len(markers)], label=g)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    _save(fig, fname)


def top_papers_figure(papers, title, fname, color, n=12):
    if not papers:
        return
    top = papers[:n][::-1]
    labels = [((p.get("title") or "")[:46] + "…") for p in top]
    cites = [p.get("citation_count", 0) for p in top]
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(top) + 1.2))
    ax.barh(range(len(top)), cites, color=color)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Citations (OpenAlex)")
    ax.set_title(title)
    _save(fig, fname)


def github_figure(repos):
    if not repos:
        return
    seen = {}
    for bucket in repos.values():
        for r in bucket:
            fn = r.get("full_name")
            if fn and (fn not in seen or r["stars"] > seen[fn]["stars"]):
                seen[fn] = r
    board = sorted(seen.values(), key=lambda r: r["stars"], reverse=True)[:15][::-1]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh([r["full_name"] for r in board], [r["stars"] for r in board], color=ORANGE)
    ax.set_xlabel("GitHub stars")
    ax.set_title("Most-starred open-source radiology / medical-imaging AI tools")
    ax.tick_params(axis="y", labelsize=8)
    _save(fig, "github_stars.png")


def main() -> None:
    print(f"Writing figures to {FIG}")
    counts = _load("pubmed_yearly_counts.json")
    if counts:
        trend_figures(counts)
        breakdown_figure(counts, "modality", "radiology_ai",
                         "Radiology AI by imaging modality", "modality_breakdown.png", BLUE)
        breakdown_figure(counts, "task", "radiology_ai",
                         "Radiology AI by clinical task", "task_breakdown.png", RED)
        breakdown_figure(counts, "ped_modality", "pediatric_radiology_ai",
                         "Pediatric radiology AI by modality", "ped_modality_breakdown.png", GREEN)
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
    github_figure(_load("github_repos.json") or {})
    print("Done.")


if __name__ == "__main__":
    main()
