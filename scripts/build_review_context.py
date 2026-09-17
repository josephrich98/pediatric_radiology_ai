#!/usr/bin/env python3
"""Offline dissemination figures for the review, separate from its screened cohort.

Run with PYTHONPATH=. python scripts/build_review_context.py. Uses the stored
September 2026 snapshots; does not fetch records or alter cohort membership.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.ticker import StrMethodFormatter
import numpy as np

from pedrad_ai import arxiv, config, medrxiv

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
FIGURES = ROOT / "figures"
PARTIAL_YEAR = 2026
VENUES = ["MICCAI", "MIDL", "CVPR", "NeurIPS", "ICLR", "ICML"]
BLUE, GREEN, ORANGE = "#245b85", "#287f73", "#bd651c"


def read(name):
    return json.loads((DATA / f"{name}.json").read_text())


def save(fig, name):
    for extension in ("png", "pdf"):
        fig.savefig(FIGURES / f"{name}.{extension}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def publication_figure(pubmed, preprints):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout="constrained")
    for ax, key, title in zip(
        axes, ("radiology_ai", "pediatric_radiology_ai"),
        ("A  Radiology AI, all ages", "B  Pediatric radiology AI"),
    ):
        series = [("PubMed", pubmed[key], BLUE, "o"),
                  ("arXiv", preprints["by_source"]["arXiv"]["yearly"][key], GREEN, "s"),
                  ("medRxiv", preprints["by_source"]["medRxiv"]["yearly"][key], ORANGE, "^")]
        for label, values, color, marker in series:
            years = sorted(int(y) for y in values if label != "medRxiv" or int(y) >= 2019)
            full = [y for y in years if y < PARTIAL_YEAR]
            ax.plot(full, [values[str(y)] for y in full], color=color, marker=marker,
                    markersize=3.5, linewidth=1.6, label=label)
            if PARTIAL_YEAR in years:
                ax.scatter(PARTIAL_YEAR, values[str(PARTIAL_YEAR)], edgecolors=color,
                           facecolors="none", marker=marker, s=30, zorder=4)
        ax.axvspan(2025.55, 2026.45, color="0.93", zorder=-1)
        ax.set(title=title, xlabel="Publication / submission year", ylabel="Retrieved records",
               xlim=(2007.5, 2026.5), ylim=(0, None))
        ax.set_xticks([2008, 2012, 2016, 2020, 2024, 2026],
                      ["2008", "2012", "2016", "2020", "2024", "2026\nYTD"])
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.18)
        ax.legend(frameon=False, loc="upper left")
    save(fig, "review_publication_sources")


def journal_figure(journals):
    rows = sorted(journals["journals"], key=lambda r: (-r["total"], r["journal"]))[:12]
    assert sum(r["total"] for r in journals["journals"]) == journals["n_papers"]
    assert all(sum(r["counts"].values()) == r["total"] for r in journals["journals"])
    full = [sum(n for y, n in r["counts"].items() if int(y) < PARTIAL_YEAR) for r in rows]
    partial = [r["counts"].get(str(PARTIAL_YEAR), 0) for r in rows]
    fig, ax = plt.subplots(figsize=(10.5, 5.7), layout="constrained")
    ys = np.arange(len(rows))
    ax.barh(ys, full, color=BLUE, label="2015–2025")
    ax.barh(ys, partial, left=full, color="#dbe8f0", edgecolor=BLUE,
            hatch="///", label="2026 YTD")
    for y, row in zip(ys, rows):
        ax.text(row["total"] + 2, y, str(row["total"]), va="center", fontsize=9)
    ax.set_yticks(ys, [r["journal"] for r in rows])
    ax.invert_yaxis()
    ax.set(xlabel="Retrieved records per journal", xlim=(0, rows[0]["total"] * 1.16),
           title="Journals with the most records in the separate PubMed search")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    save(fig, "review_journal_output")
    return rows


def heatmap(ax, values, labels, title, cmap="Blues"):
    values = np.array(values, dtype=float)
    norm = Normalize(0, max(1, np.nanmax(values)))
    palette = matplotlib.colormaps[cmap].copy()
    palette.set_bad("#e5e5e5")
    ax.imshow(np.ma.masked_invalid(values), norm=norm, cmap=palette, aspect="auto")
    ax.set_xticks(range(4), ["2023", "2024", "2025", "2026*"])
    ax.set_yticks(range(len(labels)), labels)
    ax.set_title(title, loc="left", pad=12)
    for (i, j), value in np.ndenumerate(values):
        text = "NA" if np.isnan(value) else str(int(value))
        color = "white" if np.isfinite(value) and norm(value) > .55 else "#202020"
        ax.text(j, i, text, ha="center", va="center", color=color)
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)


def conference_figure(conferences):
    rad, ped = [], []
    for name in VENUES:
        row = conferences[name]
        assert row["count_source"] == "accepted-paper list"
        rad.append([row["by_year"].get(str(y), np.nan) for y in range(2023, 2027)])
        ped.append([row["pediatric_by_year"].get(str(y), 0)
                    if str(y) in row["by_year"] else np.nan for y in range(2023, 2027)])
        for y, n in row["by_year"].items():
            assert row["pediatric_by_year"].get(y, 0) <= n <= row["accepted_by_year"][y]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.5), layout="constrained")
    heatmap(axes[0], rad, VENUES, "A  Radiology-AI title matches")
    heatmap(axes[1], ped, VENUES, "B  Pediatric subset", "Greens")
    fig.supxlabel("*2026 coverage varies by venue; NA = no retrieved list. Panel color scales differ.", fontsize=9)
    save(fig, "review_conference_context")


def newsletter_figure(news):
    names = list(news["sources"])
    names.sort(key=lambda name: -sum(v["pediatric_radiology_ai"]
               for y, v in news["by_year"].get(name, {}).items() if 2023 <= int(y) <= 2026))
    values = [[news["by_year"].get(name, {}).get(str(y), {}).get("pediatric_radiology_ai", np.nan)
               for y in range(2023, 2027)] for name in names]
    fig, ax = plt.subplots(figsize=(8, 4.8), layout="constrained")
    heatmap(ax, values, names, "Pediatric radiology-AI story matches in retrieved news archives", "Greens")
    fig.supxlabel("*2026 YTD. NA = no retrieved coverage; zero = no matches in retrieved items.\n"
                  "Archive depth and screening differ between sources.", fontsize=9)
    save(fig, "review_news_context")


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    pubmed, preprints = read("pubmed_yearly_counts"), read("preprint_counts")
    journals, conferences, news = read("journal_impact"), read("conference_works"), read("newsletter_summary")
    publication_figure(pubmed, preprints)
    top = journal_figure(journals)
    conference_figure(conferences)
    newsletter_figure(news)

    files = ["pubmed_yearly_counts", "pubmed_summary", "preprint_counts", "journal_impact",
             "conference_works", "newsletter_summary"]
    inventory = {f"data/processed/{name}.json": hashlib.sha256((DATA / f"{name}.json").read_bytes()).hexdigest()
                 for name in files}
    rules = {key: getattr(config, key) for key in ["PAPER_MEDICAL_SIGNAL", "PAPER_AI_SIGNAL",
             "PAPER_IMAGING_SIGNAL", "PAPER_PEDIATRIC_SIGNAL", "PAPER_EXCLUDE_DOMAIN",
             "NEWS_PEDIATRIC_PATTERNS", "NEWS_AI_PATTERNS", "NEWS_RADIOLOGY_PATTERNS"]}
    manifest = {"analysis_date": "2026-09-16", "partial_year": PARTIAL_YEAR, "source_sha256": inventory,
                "pubmed_metadata_date": read("pubmed_summary")["collected_on"],
                "preprint_collection_date": preprints["collected_on"],
                "news_collection_date": news["collected_on"],
                "journal_and_conference_collection_dates": "not recorded in source JSON",
                "rules_from_current_collectors": rules,
                "conference_source_urls": config.VENUE_ACCEPTED_LISTS,
                "journal_query_from_snapshot": journals["query"]}
    (DATA / "review_context_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    lines = ["# Supplementary dissemination analysis", "",
             "Offline analysis of archived source snapshots, September 16, 2026. These descriptive searches are separate from the 3,496 included primary-study records. No source totals are pooled or interpreted as unique studies, adoption, or clinical benefit.", "",
             "## Source inventory", "", "| File | Recorded collection date | SHA-256 |", "|:--|:--|:--|"]
    dates = {"pubmed_summary": manifest["pubmed_metadata_date"], "pubmed_yearly_counts": "See companion pubmed_summary (2026-09-07)",
             "preprint_counts": preprints["collected_on"], "newsletter_summary": news["collected_on"]}
    for name in files:
        path = f"data/processed/{name}.json"
        lines.append(f"| `{path}` | {dates.get(name, 'Not recorded; archived snapshot analyzed 2026-09-16')} | `{inventory[path]}` |")
    lines += ["", "Collection dates describe metadata, not necessarily the dates of every cached API response. The screened cohort retains its September 9 search cutoff. The current collector rules and source URLs are frozen in `data/processed/review_context_manifest.json`; rule snapshots are not evidence that all historical retrievals used identical code.", "",
              "## Table D1. Publication-source counts", "", "| Year | PubMed, all ages | PubMed, pediatric | arXiv, all ages | arXiv, pediatric | medRxiv, all ages | medRxiv, pediatric |", "|--:|--:|--:|--:|--:|--:|--:|"]
    for year in range(2008, 2027):
        y = str(year)
        vals = [pubmed[k][y] for k in ("radiology_ai", "pediatric_radiology_ai")]
        vals += [preprints["by_source"][source]["yearly"][k].get(y, 0)
                 for source in ("arXiv", "medRxiv") for k in ("radiology_ai", "pediatric_radiology_ai")]
        lines.append("| " + " | ".join([y + (" YTD" if year == PARTIAL_YEAR else ""), *map(str, vals)]) + " |")
    lines += ["", "PubMed includes multiple publication types and is not a journal-only primary-study cohort. Preprints can overlap PubMed and later journal versions; sources have not been linked at record level. medRxiv counts before 2019 are structural zeros and are not plotted. Approximate translated queries have different field and indexing behavior.", "",
              "## Table D2. Twelve highest-output journals in the separate search", "", "| Journal | 2015–2025 | 2026 YTD | Total |", "|:--|--:|--:|--:|"]
    for row in top:
        n = row["counts"].get("2026", 0)
        lines.append(f"| {row['journal']} | {row['total'] - n} | {n} | {row['total']} |")
    lines += ["", f"The underlying source inventory contains {journals['n_papers']:,} records across {journals['n_journals']:,} source labels, including a small number of proceedings/preprint labels. The displayed twelve are journals and account for {sum(r['total'] for r in top):,} records. Journal aliases already matched to the same OpenAlex source were merged by the collector. No citedness threshold was used for this figure.", "",
              "## Table D3. Conference title matches", "", "| Venue | Year | Retrieved accepted titles | Radiology-AI matches | Pediatric matches |", "|:--|--:|--:|--:|--:|"]
    for name in VENUES:
        row = conferences[name]
        for y in map(str, range(2023, 2027)):
            vals = [str(row["accepted_by_year"][y]), str(row["by_year"][y]), str(row["pediatric_by_year"].get(y, 0))] if y in row["by_year"] else ["NA"] * 3
            lines.append("| " + " | ".join([name, y, *vals]) + " |")
    lines += ["", "Counts use the meetings' own accepted-paper lists, not the older DBLP samples or the citation-ranked Semantic Scholar example tables. A title must match medical, imaging, and AI terms and avoid excluded domains; the pediatric subset additionally matches pediatric terms. Missing lists are NA, not zero. Proceedings remain excluded from the primary review cohort. RSNA/SPR journal proxies are omitted from this conference analysis.", "",
              "## Table D4. News archive coverage and pediatric story matches", "", "| Source | Retrieved date range | 2023 | 2024 | 2025 | 2026 YTD |", "|:--|:--|--:|--:|--:|--:|"]
    for name, row in news["sources"].items():
        counts = [str(news["by_year"].get(name, {}).get(str(y), {}).get("pediatric_radiology_ai", "NA")) for y in range(2023, 2027)]
        lines.append("| " + " | ".join([name, row["archive_from"] + " to " + row["archive_to"], *counts]) + " |")
    lines += ["", "These are automated story matches, not adjudicated pediatric-AI stories or unique research events. Archive depth, source selection, sponsor text, and repeated coverage prevent comparisons of popularity or market share. Blocked sources: " + "; ".join(news["blocked"]) + ".", "",
              "## Queries and collector provenance", "", "### Journal search stored with the source snapshot", "", "```text", journals["query"], "```", "",
              "### Broad publication queries and preprint translations", "", "The following reproduce the current collector definitions used for the contextual count analysis; the annual aggregate JSON does not retain individual query responses. PubMed uses annual [pdat] restrictions; arXiv uses submittedDate and medRxiv uses PUB_YEAR through Europe PMC. These are distinct from the review eligibility search.", ""]
    for key in ("all_radiology", "pediatric_radiology", "radiology_ai", "pediatric_radiology_ai"):
        query = config.QUERIES[key]
        lines += [f"**{key}**", "", "```text",
                  "PubMed: (" + query + ") AND YYYY:YYYY[pdat]",
                  "arXiv: (" + arxiv.to_arxiv_query(query)
                  + ") AND submittedDate:[YYYY01010000 TO YYYY12312359]",
                  'medRxiv / Europe PMC: SRC:PPR AND PUBLISHER:"medRxiv" AND ('
                  + medrxiv.to_europepmc_query(query) + ") AND PUB_YEAR:[YYYY TO YYYY]",
                  "```", ""]
    lines += ["### Classification rules and conference source URLs", "", "```json", json.dumps({"rules": rules, "conference_sources": config.VENUE_ACCEPTED_LISTS}, indent=2), "```", "",
              "Rebuild with `PYTHONPATH=. python scripts/build_review_context.py`. It writes four PNG/PDF figures, this report, and the source manifest without network requests. Rebuilding from refreshed inputs requires editorial review of the manuscript's numbers and snapshot dates.", ""]
    (ROOT / "reports/05_dissemination_analysis.md").write_text("\n".join(lines))
    print("Created four context figures (PNG/PDF), dissemination tables, and source manifest.")


if __name__ == "__main__":
    main()
