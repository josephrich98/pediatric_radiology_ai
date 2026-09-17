"""The commercial derived view: problem assignment, pediatric join, curation.

The last test is the one that matters in practice: every pediatric claim in
``config.COMMERCIAL_PRODUCTS`` that cites an FDA submission has to point at a
record the snapshot actually holds, or the product slide quotes a number that
nothing in the repository supports.
"""

import unittest

from pedrad_ai import commercial, config, utils


def _devices(*rows):
    out = []
    for i, r in enumerate(rows):
        out.append({"submission": r.get("submission", f"K{i:06d}"), "year": r.get("year", 2024),
                    "device": r.get("device", ""), "company": r.get("company", "Acme, Inc."),
                    "company_norm": r.get("company_norm", r.get("company", "Acme")),
                    "product_code": r.get("product_code", "QIH")})
    return {"devices": out}


class ClinicalProblemTests(unittest.TestCase):
    def test_device_name_beats_a_generic_product_code(self):
        # QIH is "Automated Radiological Image Processing Software": generic.
        self.assertEqual(commercial.clinical_problem("Rapid Obstructive Hydrocephalus", "QIH"),
                         "brain / neurologic")
        self.assertEqual(commercial.clinical_problem("Fetal EchoScan", "QIH"), "fetal / obstetric")

    def test_product_code_fills_in_a_name_that_says_nothing(self):
        self.assertEqual(commercial.clinical_problem("BriefCase", "QAS"),
                         "triage / worklist prioritization")
        self.assertIsNone(commercial.clinical_problem("uMR Astra", "LNH"))

    def test_specific_problems_win_over_the_cross_cutting_ones(self):
        # Almost any product could be called measurement or triage; a product
        # that names a body part or a disease is filed under that instead.
        self.assertEqual(commercial.clinical_problem("Bone Age Pro Assessment", "QIH"),
                         "bone age / growth")
        self.assertEqual(commercial.clinical_problem("Auto-Seg", "QIH"), "measurement / quantification")


class PediatricJoinTests(unittest.TestCase):
    def test_only_label_positive_candidates_count_as_pediatric(self):
        fda = _devices({"submission": "K1", "product_code": "QIH"},
                       {"submission": "K2", "product_code": "IYN"},
                       {"submission": "K3", "product_code": "QIH"})
        inv = {"records": [{"submission": "K1", "status": "label-positive-candidate"},
                           {"submission": "K2", "status": "label-positive-candidate"},
                           {"submission": "K3", "status": "needs-label-review"}]}
        recs = commercial.records(fda, inv)
        self.assertEqual([r["pediatric_label"] for r in recs], [True, True, False])
        # IYN is an ultrasound system: labeled for pediatric imaging as a
        # scanner, which is not the same claim as pediatric AI.
        self.assertEqual([r["kind"] for r in recs], ["software", "system", "software"])
        counts = commercial.problem_counts(recs)
        self.assertEqual((counts["total_pediatric"], counts["systems_pediatric"]), (2, 1))

    def test_company_spelling_variants_are_one_company(self):
        fda = _devices({"company_norm": "EOS imaging", "year": 2024},
                       {"company_norm": "Eos Imaging", "year": 2025},
                       {"company_norm": "EOS imaging", "year": 2025})
        groups = commercial.by_company(commercial.records(fda, None))
        self.assertEqual({k: len(v) for k, v in groups.items()}, {"EOS imaging": 3})

    def test_series_are_cumulative_and_pediatric_is_a_subset(self):
        # The series runs over the years the panel has decisions in, from this
        # company's first one: 2024 carries the running total unchanged.
        fda = _devices({"company_norm": "Acme", "year": 2023, "submission": "K1"},
                       {"company_norm": "Acme", "year": 2025, "submission": "K2"},
                       {"company_norm": "Other", "year": 2024, "submission": "K3"})
        inv = {"records": [{"submission": "K2", "status": "label-positive-candidate"}]}
        recs = commercial.records(fda, inv)
        all_by, ped_by = commercial.company_series(recs, top_n=2, always=[])["Acme"]
        self.assertEqual(all_by, {2023: 1, 2024: 1, 2025: 2})
        self.assertEqual(ped_by, {2023: 0, 2024: 0, 2025: 1})
        self.assertTrue(all(ped_by[y] <= all_by[y] for y in all_by))


class CuratedProductTests(unittest.TestCase):
    def setUp(self):
        path = config.PROCESSED_DIR / "fda_ai_devices.json"
        if not path.exists():
            self.skipTest("FDA snapshot not collected")
        self.fda = utils.load_json(path)

    def test_every_cited_submission_is_in_the_snapshot(self):
        held = {d["submission"] for d in self.fda.get("devices", [])}
        missing = [p["product"] for p in config.COMMERCIAL_PRODUCTS
                   if p.get("submission") and p["submission"] not in held]
        self.assertEqual(missing, [], "cited FDA submissions absent from the saved list")

    def test_product_rows_are_complete(self):
        fields = {"product", "vendor", "problem", "modality", "task", "pediatric", "standing"}
        for p in config.COMMERCIAL_PRODUCTS:
            self.assertTrue(fields <= set(p), f"{p.get('product')} is missing {fields - set(p)}")
            self.assertIn(p["problem"], set(config.COMMERCIAL_PROBLEM_TERMS) | {"other"})
