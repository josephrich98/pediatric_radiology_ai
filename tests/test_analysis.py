"""Unit tests for the pure-logic analysis helpers (no network)."""

from __future__ import annotations

from pedrad_ai import analysis


def _synthetic_counts():
    return {
        "all_radiology": {2018: 1000, 2019: 1100, 2020: 1200},
        "radiology_ai": {2018: 100, 2019: 200, 2020: 400},
        "pediatric_radiology": {2018: 80, 2019: 90, 2020: 100},
        "pediatric_radiology_ai": {2018: 5, 2019: 12, 2020: 30},
        "modality::CT": {2018: 40, 2019: 90, 2020: 200},
        "modality::MRI": {2018: 30, 2019: 60, 2020: 100},
        "task::segmentation": {2018: 20, 2019: 40, 2020: 80},
    }


def test_fractions_over_time_shapes():
    rows = analysis.fractions_over_time(_synthetic_counts())
    assert [r["year"] for r in rows] == [2018, 2019, 2020]
    last = rows[-1]
    assert last["ai_share_of_radiology"] == round(400 / 1200, 5)
    assert last["pediatric_share_of_radiology_ai"] == round(30 / 400, 5)
    assert last["ai_share_of_pediatric_radiology"] == round(30 / 100, 5)


def test_breakdown_table_sorted_desc():
    rows = analysis.breakdown_table(_synthetic_counts(), "modality")
    labels = [r["label"] for r in rows]
    assert labels == ["CT", "MRI"]  # CT total (330) > MRI total (190)
    assert rows[0]["total"] == 330
    assert rows[0]["latest_year"] == 2020
    assert "fraction" not in rows[0]  # no denom -> no fraction column


def test_breakdown_table_fraction():
    counts = _synthetic_counts()
    rows = analysis.breakdown_table(counts, "modality", denom_series="radiology_ai")
    # radiology_ai total = 100+200+400 = 700; CT total = 330
    ct = next(r for r in rows if r["label"] == "CT")
    assert ct["fraction"] == round(330 / 700, 4)


def test_cagr_and_summary():
    counts = _synthetic_counts()
    growth = analysis.cagr(counts["radiology_ai"])
    # 100 -> 400 over two years = doubling per year = 1.0
    assert abs(growth - 1.0) < 1e-9
    summary = analysis.summarize(counts)
    assert summary["radiology_ai_latest"] == 400
    assert summary["year_range"] == [2018, 2020]


def test_safe_div_zero():
    assert analysis._safe_div(5, 0) == 0.0
