from _support import *
from tools.module0 import control_errors, resolve_inside, validate_evidence_manifest, verify_evidence, ValidationError


class EvidenceControlTests(unittest.TestCase):
    def test_26_complete_manifest_passes(self):
        self.assertEqual([], validate_evidence_manifest(completed_manifest()))

    def test_27_invalid_validation_method_is_rejected(self):
        value = completed_manifest(); value["claims"][0]["validation_method"] = "Self-certified"
        self.assertTrue(any("validation_method" in x for x in validate_evidence_manifest(value)))

    def test_28_seal_detects_tampering(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "evidence") as temp:
            directory = Path(temp)
            artefact = directory / "artefact.txt"; artefact.write_text("original", encoding="utf-8")
            seal = {"artefacts":[{"path":"artefact.txt","sha256":file_digest(artefact)}]}
            (directory / "SHA256SUMS.json").write_text(json.dumps(seal), encoding="utf-8")
            self.assertEqual([], verify_evidence(directory))
            artefact.write_text("changed", encoding="utf-8")
            self.assertTrue(any("digest mismatch" in x for x in verify_evidence(directory)))

    def test_29_unsafe_control_key_is_rejected(self):
        control = {"catalogue_version":"1","fault_id":"ENV-PRE-001","assessment_impact":"A4","authorised_by":"assessor","issued_utc":"2026-08-19T00:00:00Z","changed_constraint":"test","learner_visible_text":"test","live_data":"customers.csv"}
        self.assertTrue(any("forbidden keys" in x for x in control_errors(control)))

    def test_30_reset_path_must_stay_inside_work(self):
        with self.assertRaises(ValidationError):
            resolve_inside(ROOT / "README.md", ROOT / "work")
