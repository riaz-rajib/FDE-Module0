from _support import *
from tools.module0 import validate_field_plan


class FieldPlanTests(unittest.TestCase):
    def test_21_complete_field_plan_passes(self):
        self.assertEqual([], validate_field_plan(completed_field_plan()))

    def test_22_home_team_contact_is_required(self):
        value = completed_field_plan(); value["home_team_contact"] = ""
        self.assertTrue(any("home_team_contact" in x for x in validate_field_plan(value)))

    def test_23_maximum_hours_must_be_bounded(self):
        value = completed_field_plan(); value["maximum_consecutive_hours"] = 18
        self.assertTrue(any("maximum_consecutive_hours" in x for x in validate_field_plan(value)))

    def test_24_lone_worker_controls_are_required(self):
        value = completed_field_plan(); value["lone_worker_controls"] = []
        self.assertTrue(any("lone_worker_controls" in x for x in validate_field_plan(value)))

    def test_25_employer_duty_acknowledgement_is_required(self):
        value = completed_field_plan(); value["employer_duty_acknowledgement"] = False
        self.assertTrue(any("employer_duty_acknowledgement" in x for x in validate_field_plan(value)))
