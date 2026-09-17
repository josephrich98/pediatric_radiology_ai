"""Company counts must not include unrelated names containing an alias."""

import unittest

from pedrad_ai.fda_devices import company_lookup


class CompanyLookupTests(unittest.TestCase):
    def test_scanner_aliases_exclude_unrelated_substrings(self):
        names = [
            "GE Healthcare", "GE Medical Systems", "General Electric Company",
            "Canon Medical Systems", "Siemens Healthineers",
            "Koninklijke Philips N.V.", "Imagen", "Change Healthcare",
            "Merge Incorporated", "Visage Imaging", "Genesis Software",
        ]
        fda = {"devices": [
            {"company": n, "device": n, "year": 2024} for n in names
        ]}
        result = company_lookup(fda, "GE|General Electric|Canon|Siemens|Philips")
        self.assertEqual(result["devices"], 6)
        self.assertEqual(result["years"], [2024])

    def test_punctuation_and_case_in_literal_aliases(self):
        fda = {"devices": [
            {"company": "Ever Fortune.AI Co., Ltd.", "device": "Bone Age", "year": 2024},
            {"company": "Qure.Ai Technologies", "device": "qXR", "year": 2025},
            {"company": "QureXai Technologies", "device": "Other", "year": 2025},
        ]}
        self.assertEqual(company_lookup(fda, "Ever Fortune|Qure.ai")["devices"], 2)
        self.assertEqual(company_lookup(fda, " | ")["devices"], 0)
