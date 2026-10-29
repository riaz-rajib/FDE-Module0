from _support import *
from tools.module0 import baseline_errors, read_json, validate_scenario


class BundleTests(unittest.TestCase):
    def test_01_index_has_six_unique_scenarios(self):
        index = read_json(ROOT / "scenarios" / "index.json")
        ids = [item["scenario_id"] for item in index["scenarios"]]
        self.assertEqual(6, len(ids))
        self.assertEqual(6, len(set(ids)))

    def test_02_scenario_ids_match_index(self):
        self.assertEqual([], baseline_errors(ROOT))

    def test_03_all_domains_are_reserved_invalid(self):
        index = read_json(ROOT / "scenarios" / "index.json")
        for item in index["scenarios"]:
            data = read_json(ROOT / "scenarios" / item["file"])
            self.assertTrue(data["fictional_domain"].endswith(".invalid"))

    def test_04_all_scenarios_are_synthetic_only(self):
        index = read_json(ROOT / "scenarios" / "index.json")
        for item in index["scenarios"]:
            data = read_json(ROOT / "scenarios" / item["file"])
            self.assertEqual("synthetic_only", data["data_status"])

    def test_05_no_scenario_contains_unsafe_reference(self):
        index = read_json(ROOT / "scenarios" / "index.json")
        for item in index["scenarios"]:
            path = ROOT / "scenarios" / item["file"]
            self.assertEqual([], validate_scenario(read_json(path), path))
