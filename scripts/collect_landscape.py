#!/usr/bin/env python3
"""Collect the "biggest players" landscape: cited papers, software, citations.

Pulls:
    * most-cited radiology-AI and pediatric-radiology-AI papers (Semantic Scholar)
    * top GitHub repositories by stars (radiology AI + pediatric)
    * enriches PubMed top-articles with citation counts where DOIs are present

Outputs:
    data/processed/top_papers_radiology_ai.json
    data/processed/top_papers_pediatric_radiology_ai.json
    data/processed/github_repos.json
    data/processed/github_leaderboard.csv
"""

from __future__ import annotations

from pedrad_ai import conferences, config, github_repos, openalex, utils

# A paper is kept only if its title actually contains an imaging or AI term.
# Full-text AND-search occasionally matches papers that mention the words only
# in passing (e.g. a "Zoom fatigue" editorial), and the title check removes them.
_RELEVANCE_KEYWORDS = (
    config.RADIOLOGY_TITLE_KEYWORDS
    + config.AI_TITLE_KEYWORDS
    + ["bone age", "fracture", "pneumonia", "radiograph", "imaging", "ai"]
)


def _is_relevant(paper: dict) -> bool:
    return conferences._matches(paper.get("title") or "", _RELEVANCE_KEYWORDS)


def collect_papers() -> None:
    # OpenAlex full-text AND-search keeps these on-topic; Semantic Scholar's
    # key-less endpoint is too rate-limited to rely on.
    queries = {
        "radiology_ai": "radiology deep learning",
        "pediatric_radiology_ai": "pediatric radiology deep learning",
    }
    for name, q in queries.items():
        print(f"OpenAlex: top-cited for {name!r}...")
        papers = openalex.top_cited(q, per_page=80, min_year=config.START_YEAR)
        papers = [p for p in papers if _is_relevant(p)][:50]
        utils.save_json(papers, config.PROCESSED_DIR / f"top_papers_{name}.json")
        if papers:
            print(f"  top paper: {papers[0]['citation_count']} cites — {papers[0]['title']!r}")


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
