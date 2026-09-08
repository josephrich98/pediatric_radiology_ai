"""Unit tests for the paper database's pure logic (no network, no API calls).

Covers the parts that decide what the database says: which papers get re-read,
how the release column is settled, and how hand overrides interact with stored
extractions.
"""

from __future__ import annotations

import pytest

from pedrad_ai import config, extract, paper_db


def _article(pmid: str = "12345678", **kw):
    art = {
        "pmid": pmid,
        "title": "A deep learning model for pediatric bone age",
        "journal": "Pediatr Radiol",
        "year": 2024,
        "doi": "10.1007/s00247-024-00000-0",
        "authors": ["Smith J", "Doe A"],
        "publication_types": ["Journal Article"],
        "mesh_terms": ["Age Determination by Skeleton"],
        "abstract": "BACKGROUND: bone age is tedious. METHODS: a CNN on 1000 radiographs.",
    }
    art.update(kw)
    return art


def _extraction(**kw):
    ext = {
        "is_pediatric_radiology_ai": True,
        "exclusion_reason": "",
        "model_name": "PedBone",
        "model_family": "ResNet-50",
        "modality": ["x-ray / radiography"],
        "body_region": "hand and wrist",
        "clinical_problem": "skeletal maturity assessment",
        "patient_population": "children 2-17 referred for bone age",
        "age_groups": ["child", "adolescent"],
        "task": [config.PAPER_DB_TASKS[0]],
        "model_description": "Takes a hand radiograph, returns a bone age.",
        "release_status": "unclear",
        "release_evidence": "",
        "code_url": "",
        "dataset_size": "1,000 radiographs",
        "data_source": "single center",
        "validation": "internal only",
        "headline_result": "MAD 0.5 years",
        "study_design": "retrospective single-center diagnostic accuracy",
        "confidence": "high",
        "extractor_model": "claude-opus-5",
        "extractor_effort": "low",
        "prompt_version": extract.PROMPT_VERSION,
        "prompt_fingerprint": extract.prompt_fingerprint(),
        "input_fingerprint": extract.input_fingerprint(_article()),
    }
    ext.update(kw)
    return ext


def _store(*rows):
    return {"schema_version": config.PAPER_DB_SCHEMA_VERSION, "updated": None,
            "records": {r["pmid"]: r for r in rows}}


# --------------------------------------------------------------------------- #
# Release status
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "text,expected",
    [
        ("Code is available at https://github.com/foo/bar.", "https://github.com/foo/bar"),
        ("Weights at huggingface.co/org/model-v2, see paper.", "https://huggingface.co/org/model-v2"),
        ("Available on request from the corresponding author.", ""),
        ("", ""),
    ],
)
def test_find_code_url(text, expected):
    assert paper_db.find_code_url(text) == expected


def test_code_url_in_abstract_upgrades_unclear_to_open_source():
    article = _article(abstract="We trained a CNN. Code is available at https://github.com/x/pedbone.")
    row = paper_db.build_row(article, _extraction())
    assert row["release_status"] == "open-source"
    assert row["code_url"] == "https://github.com/x/pedbone"
    assert "github.com/x/pedbone" in row["release_evidence"]


def test_explicit_release_status_is_not_overridden():
    article = _article(abstract="Code is available at https://github.com/x/pedbone.")
    row = paper_db.build_row(article, _extraction(release_status="commercial",
                                                 release_evidence="sold as a device"))
    assert row["release_status"] == "commercial"
    assert row["release_evidence"] == "sold as a device"


def test_known_commercial_product_settles_the_release_column():
    row = paper_db.build_row(_article(), _extraction(model_name="BoneXpert"))
    assert row["release_status"] == "commercial"
    assert "commercial list" in row["release_evidence"]


def test_unknown_model_stays_unclear():
    row = paper_db.build_row(_article(), _extraction(model_name="PedBone"))
    assert row["release_status"] == "unclear"


# --------------------------------------------------------------------------- #
# Rows
# --------------------------------------------------------------------------- #
def test_row_links_prefer_doi_and_fall_back_to_pubmed():
    with_doi = paper_db.build_row(_article(), _extraction())
    assert with_doi["url"] == "https://doi.org/10.1007/s00247-024-00000-0"
    without = paper_db.build_row(_article(doi=None), _extraction())
    assert without["url"] == "https://pubmed.ncbi.nlm.nih.gov/12345678/"


def test_failed_extraction_is_stored_but_excluded():
    row = paper_db.build_row(_article(), {"error": "APIStatusError: 500"})
    assert row["include"] is False
    assert row["error"].startswith("APIStatusError")


def test_screened_out_paper_is_stored_with_a_reason():
    row = paper_db.build_row(
        _article(), _extraction(is_pediatric_radiology_ai=False, exclusion_reason="adults only")
    )
    assert row["include"] is False
    assert row["exclusion_reason"] == "adults only"
    # It stays in the store so the next refresh does not pay to read it again.
    assert paper_db.needs_extraction(_store(row), row["pmid"]) is False


# --------------------------------------------------------------------------- #
# Re-extraction policy
# --------------------------------------------------------------------------- #
def test_unread_paper_needs_extraction():
    assert paper_db.needs_extraction(_store(), "999") is True


def test_current_row_is_not_re_read():
    row = paper_db.build_row(_article(), _extraction())
    store = _store(row)
    assert paper_db.needs_extraction(store, row["pmid"]) is False
    assert paper_db.stale_fingerprint(store, _article()) is False


def test_prompt_version_bump_forces_re_read():
    row = paper_db.build_row(_article(), _extraction(prompt_fingerprint="deadbeef0000"))
    assert paper_db.needs_extraction(_store(row), row["pmid"]) is True


def test_changed_abstract_forces_re_read():
    store = _store(paper_db.build_row(_article(), _extraction()))
    later = _article(abstract="BACKGROUND: bone age is tedious. RESULTS: AUC 0.97.")
    assert paper_db.stale_fingerprint(store, later) is True


def test_errored_row_is_retried():
    row = paper_db.build_row(_article(), {"error": "APIConnectionError"})
    assert paper_db.needs_extraction(_store(row), row["pmid"]) is True


# --------------------------------------------------------------------------- #
# Overrides
# --------------------------------------------------------------------------- #
def test_override_applies_on_export_only():
    row = paper_db.build_row(_article(), _extraction())
    store = _store(row)
    overrides = {"12345678": {"release_status": "commercial", "model_name": "BoneXpert"}}
    shown = paper_db.presented(store, overrides)[0]
    assert shown["release_status"] == "commercial"
    assert shown["overridden_fields"] == ["model_name", "release_status"]
    # The stored row is untouched, so dropping the override reverts the table.
    assert store["records"]["12345678"]["release_status"] == "unclear"
    assert paper_db.presented(store, {})[0]["release_status"] == "unclear"


def test_override_can_force_a_paper_back_into_the_table():
    row = paper_db.build_row(_article(), _extraction(is_pediatric_radiology_ai=False,
                                                    exclusion_reason="looked adult-only"))
    store = _store(row)
    assert paper_db.included(store, {}) == []
    assert len(paper_db.included(store, {"12345678": {"include": True}})) == 1


def test_provenance_columns_cannot_be_overridden():
    row = paper_db.build_row(_article(), _extraction())
    shown = paper_db.presented(_store(row), {"12345678": {"pmid": "999", "extractor_model": "fake"}})[0]
    assert shown["pmid"] == "12345678"
    assert shown["extractor_model"] == "claude-opus-5"
    assert shown["overridden_fields"] == []


# --------------------------------------------------------------------------- #
# Exports
# --------------------------------------------------------------------------- #
def test_records_sort_newest_first_then_by_pmid():
    store = _store(
        paper_db.build_row(_article("111", year=2020), _extraction()),
        paper_db.build_row(_article("333", year=2024), _extraction()),
        paper_db.build_row(_article("222", year=2024), _extraction()),
    )
    assert [r["pmid"] for r in paper_db.sorted_records(store)] == ["222", "333", "111"]


def test_csv_has_every_column_and_flattens_lists(tmp_path):
    store = _store(paper_db.build_row(_article(), _extraction()))
    path = paper_db.write_csv(store, tmp_path / "db.csv", overrides={})
    header, first = path.read_text(encoding="utf-8").splitlines()[:2]
    assert header.split(",") == paper_db.COLUMNS
    assert "child; adolescent" in first


def test_summary_counts_only_included_rows():
    store = _store(
        paper_db.build_row(_article("111"), _extraction()),
        paper_db.build_row(_article("222"), _extraction(is_pediatric_radiology_ai=False,
                                                        exclusion_reason="adult")),
    )
    summary = paper_db.summarize(store, {})
    assert summary["n_candidates_screened"] == 2
    assert summary["n_included"] == 1
    assert summary["n_excluded"] == 1
    assert summary["by_modality"] == {"x-ray / radiography": 1}


def test_markdown_view_renders(tmp_path):
    store = _store(paper_db.build_row(_article(), _extraction()))
    text = paper_db.write_markdown(store, tmp_path / "db.md", overrides={}).read_text(encoding="utf-8")
    assert "# Pediatric radiology AI: paper database" in text
    assert "PedBone" in text
    assert "https://doi.org/10.1007/s00247-024-00000-0" in text


# --------------------------------------------------------------------------- #
# Schema
# --------------------------------------------------------------------------- #
def test_extraction_schema_matches_the_configured_vocabularies():
    props = extract.PaperExtraction.model_json_schema()["properties"]
    assert set(props["release_status"]["enum"]) == set(config.PAPER_DB_RELEASE_STATUS)
    assert set(props["task"]["items"]["enum"]) == set(config.PAPER_DB_TASKS)
    # Every extracted field must have somewhere to go in the exported table.
    extracted = set(props) - {"is_pediatric_radiology_ai"}
    assert extracted <= set(paper_db.COLUMNS) | {"exclusion_reason"}


def test_prompt_fingerprint_changes_with_the_prompt(monkeypatch):
    before = extract.prompt_fingerprint()
    monkeypatch.setattr(extract, "SYSTEM_PROMPT", extract.SYSTEM_PROMPT + " one more rule.")
    assert extract.prompt_fingerprint() != before
