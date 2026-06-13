#!/usr/bin/env python3
"""Render the trend figures used in the reports from processed PubMed data.

Outputs PNGs to figures/. Safe to run after collect_pubmed.py.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from pedrad_ai import analysis, config, utils  # noqa: E402


def main() -> None:
    path = config.PROCESSED_DIR / "pubmed_yearly_counts.json"
    if not path.exists():
        print("No pubmed_yearly_counts.json — run scripts/collect_pubmed.py first.")
        return
    counts = utils.load_json(path)
    rows = analysis.fractions_over_time(counts)
    if not rows:
        print("No rows to plot.")
        return
    years = [r["year"] for r in rows]

    # Figure 1: absolute radiology-AI volume + AI share of radiology.
    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.bar(years, [r["radiology_ai"] for r in rows], color="#3b6ea5", label="Radiology-AI papers")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Radiology-AI publications (PubMed)", color="#3b6ea5")
    ax1.tick_params(axis="y", labelcolor="#3b6ea5")
    ax2 = ax1.twinx()
    ax2.plot(
        years, [r["ai_share_of_radiology"] * 100 for r in rows],
        color="#c44e52", marker="o", label="AI share of radiology",
    )
    ax2.set_ylabel("AI share of all radiology (%)", color="#c44e52")
    ax2.tick_params(axis="y", labelcolor="#c44e52")
    plt.title("Growth of radiology AI")
    fig.tight_layout()
    fig.savefig(config.FIGURE_DIR / "radiology_ai_trend.png", dpi=150)
    plt.close(fig)

    # Figure 2: pediatric share of radiology AI over time.
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(
        years, [r["pediatric_share_of_radiology_ai"] * 100 for r in rows],
        color="#55a868", marker="s",
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Pediatric share of radiology AI (%)")
    ax.set_title("Pediatric fraction of radiology-AI publications")
    fig.tight_layout()
    fig.savefig(config.FIGURE_DIR / "pediatric_share.png", dpi=150)
    plt.close(fig)

    # Figure 3: RSNA-journal AI share over time (if collected).
    rsna_path = config.PROCESSED_DIR / "rsna_ai_fraction.json"
    if rsna_path.exists():
        rsna = utils.load_json(rsna_path)
        ry = [r["year"] for r in rsna]
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(ry, [r["rsna_ai_fraction"] * 100 for r in rsna], color="#8172b3", marker="^")
        ax.set_xlabel("Year")
        ax.set_ylabel("AI share of RSNA-journal articles (%)")
        ax.set_title("AI share of RSNA flagship journals (Radiology, RadioGraphics, Radiology: AI)")
        fig.tight_layout()
        fig.savefig(config.FIGURE_DIR / "rsna_ai_share.png", dpi=150)
        plt.close(fig)

    print(f"Figures written to {config.FIGURE_DIR}")


if __name__ == "__main__":
    main()
