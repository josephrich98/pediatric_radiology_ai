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


def test_repeat_authorizations_fold_into_the_latest():
    rows = build_site._one_row_per_device([
        _fda_row("2022-03-01", "K212365"),
        _fda_row("2023-03-02", "K222176", "yes"),
        _fda_row("2024-01-01", "K999999", device="Other"),
    ])
    assert len(rows) == 2
    bv = next(r for r in rows if r["device"] == "BoneView")
    assert bv["submission"] == "K222176" and bv["earlier_submissions"] == ["K212365 (2022)"]
    assert bv["pediatric"] == "yes" and "this authorization" in bv["pediatric_evidence"]


def test_earlier_pediatric_label_carries_to_the_device():
    rows = build_site._one_row_per_device([
        _fda_row("2023-02-16", "K222755", "yes", device="uMR 680"),
        _fda_row("2025-09-25", "K252371", device="uMR  680 "),
    ])
    assert len(rows) == 1 and rows[0]["submission"] == "K252371"
    assert rows[0]["pediatric"] == "yes" and "K222755 (2023)" in rows[0]["pediatric_evidence"]


def test_products_without_us_authorization_are_rows():
    # BoneXpert is on the slides' product list but not on the FDA list; the
    # site must still show it, marked as not authorized.
    rows = build_site._products_without_us_authorization()
    names = {r["device"] for r in rows}
    assert "BoneXpert" in names
    assert all(r["us_status"] == "not FDA-authorized" and not r["submission"] for r in rows)
    flagged = {p["product"] for p in config.COMMERCIAL_PRODUCTS if p.get("no_us_authorization")}
    assert names == flagged
    assert all(not p["submission"] for p in config.COMMERCIAL_PRODUCTS if p.get("no_us_authorization"))
