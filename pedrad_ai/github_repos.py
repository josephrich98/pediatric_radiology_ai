"""GitHub collector: open-source software activity and "stars" leaderboards.

New software is one of the requested popularity signals. GitHub stars are an
imperfect but widely used proxy for adoption/mindshare of open-source tools. We
query the GitHub search API for repositories matching radiology-AI topics and
rank them by stars, and separately surface pediatric-specific repositories.

Authentication: uses GITHUB_TOKEN if set, otherwise shells out to the `gh` CLI
to mint a token. Unauthenticated search is limited to 10 requests/minute, so a
token is strongly preferred.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

from . import config, utils

SEARCH_REPOS = "https://api.github.com/search/repositories"

REPO_QUERIES: dict[str, str] = {
    "radiology_ai": "radiology deep learning in:name,description",
    "medical_imaging_ai": "medical image segmentation in:name,description",
    "chest_xray_ai": "chest xray deep learning in:name,description",
    "ct_segmentation": "CT segmentation neural network in:name,description",
    "pediatric_imaging_ai": "pediatric imaging deep learning in:name,description",
    "bone_age": "bone age deep learning in:name,description",
}

# Repos whose name/description match these are topic *lists* or courses, not
# tools; they dominate star sorts and are filtered out of the leaderboards.
_EXCLUDE_TOKENS = (
    "awesome", "course", "tutorial", "roadmap", "interview", "cheatsheet",
    "book", "survey", "papers", "paper-list", "reading", "100-days",
)


def _token() -> str | None:
    if config.GITHUB_TOKEN:
        return config.GITHUB_TOKEN
    try:
        out = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=15
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass
    return None


def search_repos(query: str, limit: int = 50) -> list[dict[str, Any]]:
    """Return repositories matching ``query``, sorted by star count."""
    headers = {"Accept": "application/vnd.github+json"}
    token = _token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": min(limit, 100)}
    try:
        data = utils.http_get_json(SEARCH_REPOS, params, headers=headers, pause=2.0)
    except Exception:
        return []
    repos = [_clean_repo(r) for r in data.get("items", [])]
    return [r for r in repos if not _is_list_repo(r)]


def _is_list_repo(r: dict[str, Any]) -> bool:
    """True for curated-list / course repos that are not actual tools."""
    blob = f"{r.get('full_name', '')} {r.get('description', '')}".lower()
    return any(tok in blob for tok in _EXCLUDE_TOKENS)


def _clean_repo(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "full_name": r.get("full_name"),
        "stars": r.get("stargazers_count", 0),
        "forks": r.get("forks_count", 0),
        "description": (r.get("description") or "").strip(),
        "language": r.get("language"),
        "created_at": r.get("created_at"),
        "updated_at": r.get("updated_at"),
        "topics": r.get("topics", []),
        "url": r.get("html_url"),
    }


def collect_all(limit: int = 50) -> dict[str, list[dict[str, Any]]]:
    """Run every repo query and return a leaderboard per query."""
    return {name: search_repos(q, limit=limit) for name, q in REPO_QUERIES.items()}


def new_repos_per_year(repos: list[dict[str, Any]]) -> dict[int, int]:
    """Count repositories by creation year, to chart open-source momentum."""
    counts: dict[int, int] = {}
    for r in repos:
        created = r.get("created_at")
        if created and len(created) >= 4 and created[:4].isdigit():
            yr = int(created[:4])
            counts[yr] = counts.get(yr, 0) + 1
    return dict(sorted(counts.items()))
