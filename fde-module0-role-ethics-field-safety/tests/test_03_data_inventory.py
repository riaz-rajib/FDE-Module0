from _support import *
from tools.module0 import validate_data_inventory


def row():
    return {"asset_id":"DATA-001","synthetic":"true","classification":"training synthetic","subjects":"synthetic personas","purpose":"workflow exercise","source":"generated fixture","destinations":"local synthetic lab","retention":"delete after assessment","deletion_owner":"learner","access_roles":"learner and assessor","jurisdiction":"fictional","specialist_referral":"privacy adviser if boundary changes","notes":"none"}


class DataInventoryTests(unittest.TestCase):
    def test_11_complete_synthetic_row_passes(self):
        self.assertEqual([], validate_data_inventory([row()]))

    def test_12_non_synthetic_row_is_rejected(self):
        value = row(); value["synthetic"] = "false"
        self.assertTrue(any("synthetic=true" in x for x in validate_data_inventory([value])))

    def test_13_empty_purpose_is_rejected(self):
        value = row(); value["purpose"] = ""
        self.assertTrue(any("purpose" in x for x in validate_data_inventory([value])))

    def test_14_missing_deletion_owner_is_rejected(self):
        value = row(); value["deletion_owner"] = "TBD"
        self.assertTrue(any("deletion_owner" in x for x in validate_data_inventory([value])))

    def test_15_live_ip_reference_is_rejected(self):
        value = row(); value["destinations"] = "10.0.0.12"
        self.assertTrue(any("non-documentation IPv4" in x for x in validate_data_inventory([value])))
