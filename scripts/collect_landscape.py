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

# A paper is kept only if its title carries a radiology / medical-imaging signal
# AND is not from an adjacent imaging domain that is not radiology. This keeps
# recall high (TotalSegmentator, nnU-Net) while dropping generic CS papers (a
# data-augmentation survey) and non-radiology imaging (diabetic retinopathy,
# histopathology).
_MEDICAL_SIGNAL = (
    config.RADIOLOGY_TITLE_KEYWORDS
    + [
        "ct", "mri", "imaging", "radiograph", "tumor", "tumour", "lesion",
        "nodule", "cancer", "disease", "diagnosis", "diagnostic", "medical",
        "clinical", "biomedical", "segment", "radiomics", "pneumonia",
        "fracture", "bone age", "covid", "chest", "u-net", "unet", "nnu-net",
        "brain", "cardiac", "abdominal", "anatomic", "anatomical", "pulmonary",
    ]
)
_EXCLUDE_DOMAIN = [
    "retinopathy", "fundus", "ophthalmolog", "retinal", "dermatolog",
    "skin lesion", "skin cancer", "histopath", "whole slide", "whole-slide",
    "microscop", "cytolog", "genomic", "electrocardiogram", "endoscop",
]


_PEDIATRIC_SIGNAL = config.PEDIATRIC_TITLE_KEYWORDS + [
    "bone age", "pediatrics", "paediatrics", "kawasaki", "scoliosis",
]


def _is_relevant(paper: dict, pediatric: bool = False) -> bool:
    title = paper.get("title") or ""
    if conferences._matches(title, _EXCLUDE_DOMAIN):
        return False
    if not conferences._matches(title, _MEDICAL_SIGNAL):
        return False
    # The pediatric list must actually be pediatric: full-text union search
    # otherwise floats in highly-cited adult papers (TotalSegmentator, etc.).
    if pediatric and not conferences._matches(title, _PEDIATRIC_SIGNAL):
        return False
    return True


def collect_papers() -> None:
    # Union of modality/task-specific OpenAlex searches, so landmark papers whose
    # titles never say "radiology" (TotalSegmentator, nnU-Net, ...) are included.
    query_sets = {
        "radiology_ai": config.RADIOLOGY_AI_QUERIES,
        "pediatric_radiology_ai": config.PEDIATRIC_RADIOLOGY_AI_QUERIES,
    }
    for name, queries in query_sets.items():
        print(f"OpenAlex: top-cited union ({len(queries)} queries) for {name!r}...")
        papers = openalex.top_cited_union(queries, per_query=80, min_year=config.START_YEAR)
        is_ped = name == "pediatric_radiology_ai"
        papers = [p for p in papers if _is_relevant(p, pediatric=is_ped)][:50]
        utils.save_json(papers, config.PROCESSED_DIR / f"top_papers_{name}.json")
        if papers:
            print(f"  {len(papers)} papers; top: {papers[0]['citation_count']} cites — {papers[0]['title']!r}")


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
