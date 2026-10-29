from _support import *
from tools.module0 import validate_charter


class CharterTests(unittest.TestCase):
    def test_06_complete_charter_passes(self):
        self.assertEqual([], validate_charter(completed_charter()))

    def test_07_missing_purpose_is_rejected(self):
        value = completed_charter(); value["purpose"] = "TBD"
        self.assertTrue(any("purpose" in x for x in validate_charter(value)))

    def test_08_missing_stop_work_is_rejected(self):
        value = completed_charter(); value["stop_work_conditions"] = []
        self.assertTrue(any("stop_work" in x for x in validate_charter(value)))

    def test_09_production_requires_authority_reference(self):
        value = completed_charter(); value["authorised_environments"] = ["production"]
        self.assertTrue(any("authority reference" in x for x in validate_charter(value)))

    def test_10_non_reserved_email_is_rejected(self):
        value = completed_charter(); value["purpose"] = "Contact person@example.com"
        self.assertTrue(any("non-reserved email" in x for x in validate_charter(value)))
