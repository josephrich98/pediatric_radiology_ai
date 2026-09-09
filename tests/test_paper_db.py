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


# --------------------------------------------------------------------------- #
# Citation filter
# --------------------------------------------------------------------------- #
def _fake_icite(monkeypatch, table):
    from pedrad_ai import icite

    monkeypatch.setattr(paper_db, "candidate_pmids",
                        lambda *a, **k: {p: v["year"] for p, v in table.items()})
    monkeypatch.setattr(icite, "metrics", lambda pmids: {
        p: {k: v for k, v in table[p].items() if k != "year"} for p in pmids})


def test_candidates_with_citations_applies_the_floor(monkeypatch):
    _fake_icite(monkeypatch, {
        "1": {"year": 2020, "citations": 5, "citations_per_year": 1.0, "rcr": 0.4},
        "2": {"year": 2021, "citations": 25, "citations_per_year": 5.0, "rcr": 2.0},
        "3": {"year": 2022, "citations": 100, "citations_per_year": 25.0, "rcr": 9.0},
    })
    kept = paper_db.candidates_with_citations(2015, 2026, min_citations=20)
    assert set(kept) == {"2", "3"}
    assert kept["3"]["citations"] == 100
    assert kept["3"]["year"] == 2022


def test_citation_floor_of_zero_keeps_uncited_papers(monkeypatch):
    _fake_icite(monkeypatch, {"1": {"year": 2026, "citations": 0, "citations_per_year": 0.0, "rcr": None}})
    assert set(paper_db.candidates_with_citations(min_citations=0)) == {"1"}


def test_rate_floor_admits_a_recent_paper_the_count_floor_would_reject(monkeypatch):
    """The point of the rate clause: this year's papers cannot clear a raw count."""
    _fake_icite(monkeypatch, {
        "new": {"year": 2026, "citations": 6, "citations_per_year": 12.0, "rcr": None},
        "old": {"year": 2016, "citations": 6, "citations_per_year": 0.5, "rcr": 0.2},
    })
    kept = paper_db.collect_candidates(
        2015, 2026, min_citations=20, min_citations_per_year=8.0, min_rcr=0.0,
        include_preprints=False, include_conference=False,
    )
    assert set(kept) == {"new"}


def test_rcr_floor_admits_a_field_normalized_standout(monkeypatch):
    _fake_icite(monkeypatch, {
        "a": {"year": 2024, "citations": 9, "citations_per_year": 4.5, "rcr": 6.0},
        "b": {"year": 2024, "citations": 9, "citations_per_year": 4.5, "rcr": 0.3},
    })
    kept = paper_db.collect_candidates(
        2015, 2026, min_citations=20, min_citations_per_year=0.0, min_rcr=3.0,
        include_preprints=False, include_conference=False,
    )
    assert set(kept) == {"a"}


@pytest.mark.parametrize(
    "metrics,expected",
    [
        ({"citations": 30}, True),
        ({"citations": 3, "citations_per_year": 9.0}, True),
        ({"citations": 3, "citations_per_year": 1.0, "rcr": 4.0}, True),
        ({"citations": 3, "citations_per_year": 1.0, "rcr": 0.5}, False),
        ({}, False),
    ],
)
def test_impact_floors_are_combined_with_or(metrics, expected):
    assert paper_db.passes_impact_floor(metrics, 20, 8.0, 3.0) is expected


def test_no_floors_at_all_keeps_everything():
    assert paper_db.passes_impact_floor({"citations": 0}, 0, 0.0, 0.0) is True


def test_citations_reach_the_row_and_the_csv(tmp_path):
    row = paper_db.build_row(_article(), _extraction(), citations=42)
    assert row["citations"] == 42
    text = paper_db.write_csv(_store(row), tmp_path / "db.csv", overrides={}).read_text()
    assert ",42," in text


def test_citations_cannot_be_overridden_by_hand():
    row = paper_db.build_row(_article(), _extraction(), citations=42)
    shown = paper_db.presented(_store(row), {"12345678": {"citations": 9999}})[0]
    assert shown["citations"] == 42
    assert shown["overridden_fields"] == []


def test_named_models_table_is_ordered_by_citations(tmp_path):
    store = _store(
        paper_db.build_row(_article("111"), _extraction(model_name="LowCite"), citations=10),
        paper_db.build_row(_article("222"), _extraction(model_name="HighCite"), citations=900),
    )
    text = paper_db.write_markdown(store, tmp_path / "db.md", overrides={}).read_text()
    assert text.index("HighCite") < text.index("LowCite")


# --------------------------------------------------------------------------- #
# Worklist / ingest path
# --------------------------------------------------------------------------- #
def test_hand_written_row_validates_against_the_same_schema():
    """The no-API-key path must not be able to introduce values the model could not."""
    good = {k: v for k, v in _extraction().items() if k in
            extract.PaperExtraction.model_fields}
    assert extract.PaperExtraction.model_validate(good)
    with pytest.raises(Exception):
        extract.PaperExtraction.model_validate({**good, "release_status": "sort of released"})
    with pytest.raises(Exception):
        extract.PaperExtraction.model_validate({**good, "modality": ["PET-MR"]})


# --------------------------------------------------------------------------- #
# Year-normalized impact
# --------------------------------------------------------------------------- #
def test_normalized_impact_columns_reach_the_row():
    row = paper_db.build_row(_article(), _extraction(), metrics={
        "citations": 40, "citations_per_year": 20.0, "rcr": 3.5,
        "nih_percentile": 91.2, "fwci": 2.8, "source": "pubmed", "is_preprint": False,
    })
    assert (row["citations"], row["citations_per_year"], row["rcr"]) == (40, 20.0, 3.5)
    assert (row["nih_percentile"], row["fwci"]) == (91.2, 2.8)


def test_rcr_and_fwci_may_be_absent_without_breaking_export(tmp_path):
    """iCite leaves RCR unset for very recent papers; the table must still write."""
    row = paper_db.build_row(_article(year=2026), _extraction(), metrics={
        "citations": 3, "citations_per_year": 3.0, "rcr": None, "fwci": None,
    })
    assert row["rcr"] is None
    store = _store(row)
    assert paper_db.write_csv(store, tmp_path / "db.csv", overrides={}).exists()
    assert paper_db.summarize(store, {})["median_rcr"] is None


def test_markdown_falls_back_to_fwci_when_rcr_is_missing(tmp_path):
    store = _store(paper_db.build_row(
        _article(year=2026), _extraction(model_name="NewNet"),
        metrics={"citations": 5, "citations_per_year": 5.0, "rcr": None, "fwci": 4.2},
    ))
    text = paper_db.write_markdown(store, tmp_path / "db.md", overrides={}).read_text()
    assert "4.2" in text


# --------------------------------------------------------------------------- #
# Preprints
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "record,expected",
    [
        ({"publication_types": ["Preprint"]}, True),
        ({"doi": "10.1101/2025.06.06.25328913"}, True),
        ({"journal": "medRxiv : the preprint server for health sciences"}, True),
        ({"journal": "bioRxiv"}, True),
        ({"journal": "Pediatr Radiol", "doi": "10.1007/s00247-024-00000-0"}, False),
        ({}, False),
    ],
)
def test_preprint_detection(record, expected):
    assert paper_db.looks_like_preprint(record) is expected


def test_preprint_release_status_is_unreleased_not_unclear():
    """'Unclear' would read as an open question; for a preprint it is a known fact."""
    article = _article(journal="medRxiv : the preprint server for health sciences")
    row = paper_db.build_row(article, _extraction(release_status="unclear"))
    assert row["is_preprint"] is True
    assert row["release_status"] == "unreleased"


def test_a_released_preprint_keeps_its_open_source_status():
    article = _article(journal="bioRxiv", abstract="Code at https://github.com/x/y.")
    row = paper_db.build_row(article, _extraction())
    assert row["is_preprint"] is True
    assert row["release_status"] == "open-source"


def test_openalex_preprints_are_deduplicated_against_pubmed(monkeypatch):
    from pedrad_ai import icite

    _fake_icite(monkeypatch, {"111": {"year": 2025, "citations": 30, "citations_per_year": 30.0, "rcr": 4.0}})
    monkeypatch.setattr(paper_db, "candidate_pmids", lambda *a, **k: {"111": 2025})
    monkeypatch.setattr(icite, "metrics", lambda pmids: {
        "111": {"citations": 30, "citations_per_year": 30.0, "rcr": 4.0, "nih_percentile": 90.0}})
    monkeypatch.setattr(paper_db, "preprint_candidates", lambda *a, **k: [
        {"openalex_id": "https://openalex.org/W1", "pmid": "111", "title": "Same paper",
         "citation_count": 30, "year": 2025},                      # same PMID
        {"openalex_id": "https://openalex.org/W2", "pmid": None, "title": "Only a preprint",
         "citation_count": 30, "year": 2025, "fwci": 5.0},         # genuinely new
    ])
    kept = paper_db.collect_candidates(2015, 2026, min_citations=20,
                                       include_preprints=True, include_conference=False)
    assert set(kept) == {"111", "oa:W2"}
    assert kept["oa:W2"]["is_preprint"] is True
    assert kept["oa:W2"]["fwci"] == 5.0


def test_fetch_articles_reshapes_a_preprint_without_calling_pubmed(monkeypatch):
    monkeypatch.setattr(paper_db.pubmed, "article_details",
                        lambda *a, **k: pytest.fail("should not query PubMed for a preprint"))
    candidates = {"oa:W2": {"record_id": "oa:W2", "pmid": "", "source": "openalex",
                            "is_preprint": True,
                            "_work": {"title": "A preprint", "venue_label": "arXiv", "year": 2026,
                                      "doi": "10.48550/arXiv.1", "authors": ["Doe J"],
                                      "abstract": "We propose a network."}}}
    articles = paper_db.fetch_articles(candidates)
    assert len(articles) == 1
    assert articles[0]["record_id"] == "oa:W2"
    assert articles[0]["publication_types"] == ["Preprint"]
    assert articles[0]["abstract"].startswith("We propose")
