#!/usr/bin/env python3
"""Collect the "biggest players" landscape: cited papers, software, citations.

Pulls:
    * most-cited radiology-AI and pediatric-radiology-AI papers (Semantic Scholar,
      incl. preprints; overall, per era, per year). FWCI is filled in later by
      scripts/enrich_fwci.py (batched OpenAlex DOI lookups, cheap on the daily budget).
    * top GitHub repositories by stars (radiology AI + pediatric)
    * enriches PubMed top-articles with citation counts where DOIs are present

Outputs:
    data/processed/top_papers_radiology_ai.json
    data/processed/top_papers_pediatric_radiology_ai.json
    data/processed/github_repos.json
    data/processed/github_leaderboard.csv
"""

from __future__ import annotations

import re

from pedrad_ai import conferences, config, github_repos, semantic_scholar, utils

def _is_relevant(paper: dict, pediatric: bool = False) -> bool:
    """Title-level filter (see config.PAPER_MEDICAL_SIGNAL / PAPER_EXCLUDE_DOMAIN).

    The pediatric list must actually be pediatric: the union search otherwise
    floats in highly-cited adult papers (TotalSegmentator, etc.).
    """
    title = paper.get("title") or ""
    if not conferences.is_radiology_paper(title):
        return False
    # Semantic Scholar occasionally carries a wrong year; a DOI that embeds a
    # year (IEEE ACCESS.2020.xxx) two or more years away gives it away.
    m = re.search(r"\.(20[0-3]\d)\.", paper.get("doi") or "")
    if m and isinstance(paper.get("year"), int) and abs(int(m.group(1)) - paper["year"]) > 1:
        return False
    if pediatric and not conferences.is_pediatric_title(title):
        return False
    return True


def collect_papers() -> None:
    # Union of modality/task-specific searches (Semantic Scholar bulk API, which
    # indexes arXiv / medRxiv preprints and has no daily budget), so landmark papers whose
    # titles never say "radiology" (TotalSegmentator, nnU-Net, ...) are included.
    query_sets = {
        "radiology_ai": config.RADIOLOGY_AI_QUERIES,
        "pediatric_radiology_ai": config.PEDIATRIC_RADIOLOGY_AI_QUERIES,
    }
    for name, queries in query_sets.items():
        print(f"Semantic Scholar: top-cited union ({len(queries)} queries) for {name!r}...")
        is_ped = name == "pediatric_radiology_ai"
        papers = semantic_scholar.union_search(queries, config.START_YEAR, config.END_YEAR)
        papers = [p for p in papers if _is_relevant(p, pediatric=is_ped)][:50]
        utils.save_json(papers, config.PROCESSED_DIR / f"top_papers_{name}.json")
        if papers:
            print(f"  {len(papers)} papers; top: {papers[0]['citation_count']} cites — {papers[0]['title']!r}")
        # Per-era lists: citation counts favor old papers, so the recent era is
        # ranked on its own (top_papers_<name>_<era>.json, era label with '-').
        for label, start, end in config.ERAS:
            era = semantic_scholar.union_search(queries, start, end)
            era = [p for p in era if _is_relevant(p, pediatric=is_ped)][:50]
            utils.save_json(era, config.PROCESSED_DIR / f"top_papers_{name}_{label}.json")
            if era:
                print(f"  {label}: {len(era)} papers; top: {era[0]['citation_count']} cites — {era[0]['title']!r}")
        # Per-year lists for the recent era (top_papers_<name>_<year>.json):
        # within one publication year raw citations are comparable, and the
        # slides show the FWCI next to them.
        for year in range(config.ERAS[-1][1], config.END_YEAR + 1):
            yr = semantic_scholar.union_search(queries, year, year)
            yr = [p for p in yr if _is_relevant(p, pediatric=is_ped)][:50]
            utils.save_json(yr, config.PROCESSED_DIR / f"top_papers_{name}_{year}.json")
            if yr:
                print(f"  {year}: {len(yr)} papers; top: {yr[0]['citation_count']} cites — {yr[0]['title']!r}")


def collect_software() -> None:
    print("GitHub: repository leaderboards by stars...")
    repos = github_repos.collect_all(limit=40)
    utils.save_json(repos, config.PROCESSED_DIR / "github_repos.json")
    # Flatten into a single deduped, star-sorted leaderboard.
    seen: dict[str, dict] = {}
    for bucket in repos.values():
        for r in bucket:
            fn = r.get("full_name")
            if fn and (fn not in seen or r["stars"] > seen[fn]["stars"]):
                seen[fn] = r
    leaderboard = sorted(seen.values(), key=lambda r: r["stars"], reverse=True)
    utils.save_csv(
        leaderboard,
        config.PROCESSED_DIR / "github_leaderboard.csv",
        columns=["full_name", "stars", "forks", "language", "created_at", "description", "url"],
    )
    for r in leaderboard[:10]:
        print(f"  {r['stars']:>6}  {r['full_name']}")


def main() -> None:
    collect_papers()
    collect_software()


if __name__ == "__main__":
    main()
