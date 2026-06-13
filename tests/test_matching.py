"""Unit tests for keyword matching and repo filtering (no network)."""

from __future__ import annotations

from pedrad_ai import conferences, github_repos


def test_word_boundary_matching():
    assert conferences._matches("Automatic organ segmentation", ["segmentation"])
    assert conferences._matches("A chest x-ray classifier", ["chest x-ray"])
    # substrings must not match across word boundaries
    assert not conferences._matches("Organizational learning", ["organ"])
    assert not conferences._matches("Production planning", ["pet"])


def test_case_insensitive():
    assert conferences._matches("DEEP LEARNING for MRI", ["deep learning"])
    assert conferences._matches("Radiomics Signatures", ["radiomics"])


def test_repo_list_filter():
    awesome = {"full_name": "x/awesome-medical-ai", "description": "a list"}
    tool = {"full_name": "x/TransUNet", "description": "a segmentation model"}
    assert github_repos._is_list_repo(awesome)
    assert not github_repos._is_list_repo(tool)


def test_new_repos_per_year():
    repos = [
        {"created_at": "2018-01-01"},
        {"created_at": "2018-06-01"},
        {"created_at": "2021-03-01"},
    ]
    counts = github_repos.new_repos_per_year(repos)
    assert counts == {2018: 2, 2021: 1}
