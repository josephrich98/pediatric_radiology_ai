"""Static site builder: config drift and link helpers."""

import importlib.util
from pathlib import Path

from pedrad_ai import config

_spec = importlib.util.spec_from_file_location(
    "build_site", Path(__file__).resolve().parent.parent / "scripts" / "build_site.py")
build_site = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_site)


def test_product_splits_match_config():
    # A config edit that renames a grouped entry must also update the split,
    # or the site silently shows that entry unsplit.
    keys = {(c["vendor"], c["product"]) for c in config.COMMERCIAL_PEDIATRIC}
    assert set(build_site.PRODUCT_SPLITS) <= keys


def test_product_rows_one_per_company_product():
    fda = {"devices": [
        {"company": "GE HealthCare", "company_norm": "GE HealthCare", "device": "x", "year": 2020},
        {"company": "Imagen Technologies", "company_norm": "Imagen", "device": "y", "year": 2021},
    ]}
    rows = build_site.products(fda)
    ge = next(r for r in rows if r["vendor"] == "GE HealthCare")
    assert ge["fda_entries"] == 1 and ge["fda_companies"] == ["GE HealthCare"]
    assert sum(r["vendor"] == "BrightHeart" for r in rows) == 2


def test_repo_key_normalizes_github_urls():
    k = build_site._repo_key
    assert k("https://github.com/MIC-DKFZ/nnUNet") == k("http://www.github.com/mic-dkfz/nnunet.git/")
    assert k("https://github.com/a/b/tree/main/src") == "github.com/a/b"


def test_submission_url():
    assert build_site._submission_url("K234042").endswith("pmn.cfm?ID=K234042")
    assert "denovo.cfm" in build_site._submission_url("DEN230023")
    assert build_site._submission_url("") == ""


def _fda_row(date, submission, pediatric="", device="BoneView", company="Gleamer"):
    return {"date": date, "device": device, "company": company, "submission": submission,
            "pediatric": pediatric, "pediatric_status": "label-positive-candidate" if pediatric else "",
            "pediatric_evidence_pages": "5" if pediatric else "", "pediatric_name": "",
            "pediatric_evidence": "label" if pediatric else ""}


def test_every_authorization_is_a_row():
    # The tab counts authorizations, like the slides (1,230 / 230): a device
    # cleared twice is two rows, each naming the clearances before it.
    rows = build_site._earlier_authorizations([
        _fda_row("2022-03-01", "K212365"),
        _fda_row("2023-03-02", "K222176", "yes"),
        _fda_row("2024-01-01", "K999999", device="Other"),
    ])
    assert len(rows) == 3
    by_sub = {r["submission"]: r for r in rows}
    assert by_sub["K212365"]["earlier_submissions"] == []
    assert by_sub["K222176"]["earlier_submissions"] == ["K212365 (2022)"]
    assert by_sub["K999999"]["earlier_submissions"] == []


def test_pediatric_tick_is_the_authorizations_own():
    rows = build_site._earlier_authorizations([
        _fda_row("2023-02-16", "K222755", "yes", device="uMR 680"),
        _fda_row("2025-09-25", "K252371", device="uMR  680 "),
    ])
    by_sub = {r["submission"]: r for r in rows}
    assert by_sub["K222755"]["pediatric"] == "yes"
    assert by_sub["K252371"]["pediatric"] == "" and by_sub["K252371"]["earlier_submissions"] == ["K222755 (2023)"]
