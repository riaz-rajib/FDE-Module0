from _support import *
from tools.module0 import validate_decision


class DecisionTests(unittest.TestCase):
    def test_16_complete_record_passes(self):
        self.assertEqual([], validate_decision(completed_decision()))

    def test_17_missing_authority_is_rejected(self):
        value = completed_decision(); value["authority"] = "UNSET"
        self.assertTrue(any("authority" in x for x in validate_decision(value)))

    def test_18_invalid_evidence_label_is_rejected(self):
        value = completed_decision(); value["evidence_mode"] = "Production-like"
        self.assertTrue(any("evidence_mode" in x for x in validate_decision(value)))

    def test_19_stopped_work_requires_referral(self):
        value = completed_decision(); value["stop_or_proceed"] = "stop"; value["specialist_referrals"] = []
        self.assertTrue(any("referral" in x for x in validate_decision(value)))

    def test_20_ai_record_requires_human_authority(self):
        value = completed_decision(); value["request"] = "Use a language model for response drafting"
        self.assertTrue(any("human_decision_authority" in x for x in validate_decision(value)))
