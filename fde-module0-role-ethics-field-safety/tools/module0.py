from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_MODES = {"Portable", "Rendered", "Synthetic", "Local live", "Provider live", "Unproved"}
ALLOWED_METHODS = {"Machine-verified", "Assessor-observed", "Peer-observed", "Customer-simulated", "Document-reviewed"}
FORBIDDEN_CONTROL_KEYS = {"customer_credentials", "external_system", "live_data", "production_access", "secret_value"}
PLACEHOLDERS = {"", "REPLACE_ME", "TBD", "CHOOSE", "UNSET"}
SAFE_EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.invalid$")
SAFE_DOMAIN = re.compile(r"(?:^|\.)[A-Za-z0-9-]+\.invalid$")
DOC_IPV4_PREFIXES = ("192.0.2.", "198.51.100.", "203.0.113.")


class ValidationError(ValueError):
    pass


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing file: {path}") from exc


def is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in PLACEHOLDERS
    if isinstance(value, list):
        return bool(value) and all(is_present(item) for item in value)
    if isinstance(value, dict):
        return bool(value)
    return True


def require(obj: dict[str, Any], fields: Iterable[str], label: str) -> list[str]:
    errors: list[str] = []
    for field in fields:
        if field not in obj or not is_present(obj[field]):
            errors.append(f"{label}: '{field}' is required")
    return errors


def walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from walk_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk_strings(nested)


def unsafe_reference_errors(value: Any, label: str) -> list[str]:
    errors: list[str] = []
    for text in walk_strings(value):
        for token in re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
            if not token.endswith(".invalid"):
                errors.append(f"{label}: non-reserved email reference: {token}")
        for token in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text):
            if not token.startswith(DOC_IPV4_PREFIXES):
                errors.append(f"{label}: non-documentation IPv4 reference: {token}")
        for token in re.findall(r"https?://([^/:\s]+)", text):
            if token not in {"www.oaic.gov.au", "www.nist.gov", "www.safeworkaustralia.gov.au", "www.acm.org", "www.legislation.gov.au", "eur-lex.europa.eu"} and not token.endswith(".invalid"):
                errors.append(f"{label}: undeclared external URL host: {token}")
        if re.search(r"(?i)(api[_-]?key|password|secret|token)\s*[:=]\s*[A-Za-z0-9+/=_-]{12,}", text):
            errors.append(f"{label}: possible secret-like value")
    return errors


def validate_charter(obj: dict[str, Any]) -> list[str]:
    errors = require(
        obj,
        ["engagement_id", "purpose", "intended_outcomes", "non_goals", "authorised_environments", "data_boundary", "decision_rights", "stop_work_conditions", "escalation_paths", "review_date_utc", "status"],
        "engagement charter",
    )
    if obj.get("status") not in {"draft", "approved", "paused", "closed"}:
        errors.append("engagement charter: invalid status")
    environments = obj.get("authorised_environments", [])
    if isinstance(environments, list) and any("production" in str(x).lower() for x in environments):
        if not is_present(obj.get("production_authority_reference")):
            errors.append("engagement charter: production-like environment requires an authority reference")
    errors.extend(unsafe_reference_errors(obj, "engagement charter"))
    return errors


def validate_data_inventory(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    required = {"asset_id", "synthetic", "classification", "subjects", "purpose", "source", "destinations", "retention", "deletion_owner", "access_roles", "jurisdiction", "specialist_referral", "notes"}
    if not rows:
        return ["data inventory: at least one row is required"]
    for number, row in enumerate(rows, start=2):
        missing = sorted(field for field in required if field not in row)
        if missing:
            errors.append(f"data inventory row {number}: missing columns {', '.join(missing)}")
            continue
        for field in ("asset_id", "classification", "purpose", "source", "destinations", "retention", "deletion_owner", "access_roles", "jurisdiction"):
            if not is_present(row.get(field)):
                errors.append(f"data inventory row {number}: '{field}' is required")
        if row.get("synthetic", "").strip().lower() != "true":
            errors.append(f"data inventory row {number}: Module 0 permits synthetic=true only")
        errors.extend(unsafe_reference_errors(row, f"data inventory row {number}"))
    return errors


def validate_decision(obj: dict[str, Any], label: str = "ethical decision record") -> list[str]:
    errors = require(
        obj,
        ["decision_id", "request", "purpose_and_affected_people", "authority", "applicable_obligations", "uncertainties", "possible_harms", "safer_options", "specialist_referrals", "decision", "stop_or_proceed", "evidence_mode", "validation_method", "limitations", "review_or_expiry"],
        label,
    )
    if obj.get("evidence_mode") not in ALLOWED_MODES:
        errors.append(f"{label}: invalid evidence_mode")
    if obj.get("validation_method") not in ALLOWED_METHODS:
        errors.append(f"{label}: invalid validation_method")
    if obj.get("stop_or_proceed") not in {"stop", "pause_and_escalate", "proceed_with_controls", "decline"}:
        errors.append(f"{label}: invalid stop_or_proceed value")
    text = " ".join(walk_strings(obj)).lower()
    if any(term in text for term in ("model", "ai-assisted", "language model")):
        if not is_present(obj.get("human_decision_authority")):
            errors.append(f"{label}: AI-related record requires human_decision_authority")
    if obj.get("stop_or_proceed") in {"stop", "pause_and_escalate", "decline"} and not is_present(obj.get("specialist_referrals")):
        errors.append(f"{label}: stopped or escalated work requires a referral path")
    errors.extend(unsafe_reference_errors(obj, label))
    return errors


def validate_field_plan(obj: dict[str, Any]) -> list[str]:
    errors = require(
        obj,
        ["plan_id", "site_contact", "home_team_contact", "working_hours", "on_call_boundary", "maximum_consecutive_hours", "check_in_cadence", "lone_worker_controls", "travel_and_site_logistics", "emergency_contacts", "harassment_and_wellbeing_escalation", "stop_work_conditions", "decompression_and_return_brief", "employer_duty_acknowledgement", "approval"],
        "field-working plan",
    )
    hours = obj.get("maximum_consecutive_hours")
    if isinstance(hours, int) and not 1 <= hours <= 14:
        errors.append("field-working plan: maximum_consecutive_hours must be between 1 and 14")
    elif not isinstance(hours, int):
        errors.append("field-working plan: maximum_consecutive_hours must be an integer")
    if obj.get("employer_duty_acknowledgement") is not True:
        errors.append("field-working plan: employer_duty_acknowledgement must be true")
    errors.extend(unsafe_reference_errors(obj, "field-working plan"))
    return errors


def validate_evidence_manifest(obj: dict[str, Any]) -> list[str]:
    errors = require(obj, ["engagement_id", "manifest_version", "claims"], "evidence manifest")
    claims = obj.get("claims")
    if not isinstance(claims, list) or not claims:
        return errors + ["evidence manifest: at least one claim is required"]
    seen: set[str] = set()
    for index, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict):
            errors.append(f"evidence claim {index}: must be an object")
            continue
        errors.extend(require(claim, ["claim_id", "statement", "mode", "validation_method", "artefacts", "reviewer_or_verifier", "captured_utc", "limitations"], f"evidence claim {index}"))
        claim_id = str(claim.get("claim_id", ""))
        if claim_id in seen:
            errors.append(f"evidence claim {index}: duplicate claim_id {claim_id}")
        seen.add(claim_id)
        if claim.get("mode") not in ALLOWED_MODES:
            errors.append(f"evidence claim {index}: invalid mode")
        if claim.get("validation_method") not in ALLOWED_METHODS:
            errors.append(f"evidence claim {index}: invalid validation_method")
        errors.extend(unsafe_reference_errors(claim, f"evidence claim {index}"))
    return errors


def validate_authority(rows: list[dict[str, str]]) -> list[str]:
    required = {"decision", "accountable_role", "consulted_roles", "fde_role", "escalation_trigger"}
    errors: list[str] = []
    if not rows:
        return ["authority matrix: at least one decision row is required"]
    for number, row in enumerate(rows, start=2):
        if set(row) != required:
            errors.append(f"authority matrix row {number}: columns must be {', '.join(sorted(required))}")
        for field in required:
            if not is_present(row.get(field)):
                errors.append(f"authority matrix row {number}: '{field}' is required")
    return errors


def validate_workspace(workspace: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_charter(read_json(workspace / "engagement-charter.json")))
    errors.extend(validate_authority(read_csv(workspace / "authority-matrix.csv")))
    errors.extend(validate_data_inventory(read_csv(workspace / "data-inventory.csv")))
    errors.extend(validate_decision(read_json(workspace / "ethical-decision-record-01.json"), "ethical decision record 01"))
    errors.extend(validate_decision(read_json(workspace / "ethical-decision-record-02.json"), "ethical decision record 02"))
    errors.extend(validate_field_plan(read_json(workspace / "field-working-plan.json")))
    errors.extend(validate_evidence_manifest(read_json(workspace / "evidence-manifest.json")))
    for required in ("risk-register.csv", "specialist-referrals.csv", "field-observations.csv", "context.json"):
        if not (workspace / required).is_file():
            errors.append(f"workspace: missing file {required}")
    return errors


def validate_scenario(obj: dict[str, Any], path: Path) -> list[str]:
    errors = require(obj, ["scenario_id", "organisation", "sector", "fictional_domain", "customer_request", "stated_outcome", "facts", "visible_tensions", "known_boundaries", "participants", "data_status"], f"scenario {path.name}")
    if obj.get("data_status") != "synthetic_only":
        errors.append(f"scenario {path.name}: data_status must be synthetic_only")
    domain = str(obj.get("fictional_domain", ""))
    if not SAFE_DOMAIN.search(domain):
        errors.append(f"scenario {path.name}: fictional_domain must end in .invalid")
    errors.extend(unsafe_reference_errors(obj, f"scenario {path.name}"))
    return errors


def baseline_errors(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    index = read_json(root / "scenarios" / "index.json")
    entries = index.get("scenarios", []) if isinstance(index, dict) else []
    if len(entries) != 6:
        errors.append("scenario index: exactly six learner scenarios are required")
    ids: set[str] = set()
    for entry in entries:
        path = root / "scenarios" / str(entry.get("file", ""))
        obj = read_json(path)
        errors.extend(validate_scenario(obj, path))
        scenario_id = str(obj.get("scenario_id", ""))
        if scenario_id in ids:
            errors.append(f"scenario index: duplicate scenario_id {scenario_id}")
        ids.add(scenario_id)
        if entry.get("scenario_id") != scenario_id:
            errors.append(f"scenario index: ID mismatch for {path.name}")
    for template in (
        "engagement-charter.json", "authority-matrix.csv", "data-inventory.csv",
        "ethical-decision-record-01.json", "ethical-decision-record-02.json",
        "field-working-plan.json", "risk-register.csv", "specialist-referrals.csv",
        "field-observations.csv", "evidence-manifest.json",
    ):
        if not (root / "templates" / template).is_file():
            errors.append(f"templates: missing {template}")
    return errors


def resolve_inside(path: Path, parent: Path) -> Path:
    candidate = path.resolve()
    root = parent.resolve()
    if candidate == root or root not in candidate.parents:
        raise ValidationError(f"refusing path outside {root}: {candidate}")
    return candidate


def command_baseline(args: argparse.Namespace) -> int:
    errors = baseline_errors(ROOT)
    if errors:
        print("BASELINE FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("BASELINE PASS")
    print("6 synthetic scenarios, 10 learner templates, safe reference checks and control boundaries are valid.")
    return 0


def command_list(args: argparse.Namespace) -> int:
    index = read_json(ROOT / "scenarios" / "index.json")
    for entry in index["scenarios"]:
        print(f"{entry['scenario_id']}  {entry['title']}")
    return 0


def command_prepare(args: argparse.Namespace) -> int:
    workspace = resolve_inside(Path(args.workspace), ROOT / "work")
    index = read_json(ROOT / "scenarios" / "index.json")
    match = next((item for item in index["scenarios"] if item["scenario_id"] == args.scenario), None)
    if match is None:
        raise ValidationError(f"unknown scenario: {args.scenario}")
    if workspace.exists():
        if not args.force:
            raise ValidationError(f"workspace exists: {workspace}; use --force only after retaining required evidence")
        shutil.rmtree(workspace)
    shutil.copytree(ROOT / "templates", workspace)
    context = read_json(ROOT / "scenarios" / match["file"])
    (workspace / "context.json").write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {args.scenario} at {workspace}")
    print("Complete the files in that directory; do not replace synthetic fixtures with customer data.")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    workspace = resolve_inside(Path(args.workspace), ROOT / "work")
    errors = validate_workspace(workspace)
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} issue(s))")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALIDATION PASS")
    print("The readiness pack meets the machine-checkable minimum. Human review and observed assessment remain required.")
    return 0


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_seal(args: argparse.Namespace) -> int:
    workspace = resolve_inside(Path(args.workspace), ROOT / "work")
    evidence = resolve_inside(Path(args.evidence), ROOT / "evidence")
    errors = validate_workspace(workspace)
    if errors:
        raise ValidationError("cannot seal an invalid workspace; run validate first")
    if evidence.exists():
        if not args.force:
            raise ValidationError(f"evidence directory exists: {evidence}")
        shutil.rmtree(evidence)
    evidence.mkdir(parents=True)
    artefacts = []
    for source in sorted(path for path in workspace.iterdir() if path.is_file()):
        destination = evidence / source.name
        shutil.copy2(source, destination)
        artefacts.append({"path": source.name, "sha256": file_digest(destination), "bytes": destination.stat().st_size})
    seal = {
        "format": "fieldbridge-module0-evidence-seal-v1",
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_workspace": str(workspace.relative_to(ROOT)),
        "artefacts": artefacts,
    }
    (evidence / "SHA256SUMS.json").write_text(json.dumps(seal, indent=2) + "\n", encoding="utf-8")
    print(f"SEALED {len(artefacts)} artefacts at {evidence}")
    return 0


def verify_evidence(evidence: Path) -> list[str]:
    seal_path = evidence / "SHA256SUMS.json"
    seal = read_json(seal_path)
    errors: list[str] = []
    for entry in seal.get("artefacts", []):
        path = evidence / str(entry.get("path", ""))
        if not path.is_file():
            errors.append(f"missing sealed artefact: {path.name}")
            continue
        actual = file_digest(path)
        if actual != entry.get("sha256"):
            errors.append(f"digest mismatch: {path.name}")
    return errors


def command_verify(args: argparse.Namespace) -> int:
    evidence = resolve_inside(Path(args.evidence), ROOT / "evidence")
    errors = verify_evidence(evidence)
    if errors:
        print("EVIDENCE VERIFICATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("EVIDENCE VERIFICATION PASS")
    return 0


def control_errors(control: dict[str, Any]) -> list[str]:
    errors = require(control, ["catalogue_version", "fault_id", "assessment_impact", "authorised_by", "issued_utc", "changed_constraint", "learner_visible_text"], "assessor control")
    if control.get("assessment_impact") not in {"A1", "A2", "A3", "A4"}:
        errors.append("assessor control: assessment_impact must be A1, A2, A3 or A4")
    forbidden = FORBIDDEN_CONTROL_KEYS.intersection(control)
    if forbidden:
        errors.append(f"assessor control: forbidden keys: {', '.join(sorted(forbidden))}")
    errors.extend(unsafe_reference_errors(control, "assessor control"))
    return errors


def command_control(args: argparse.Namespace) -> int:
    workspace = resolve_inside(Path(args.workspace), ROOT / "work")
    control_path = Path(args.control).resolve()
    control = read_json(control_path)
    errors = control_errors(control)
    if errors:
        raise ValidationError("; ".join(errors))
    output = workspace / "injected-constraint.json"
    output.write_text(json.dumps(control, indent=2) + "\n", encoding="utf-8")
    print(f"Applied controlled constraint {control['fault_id']} to {workspace}")
    return 0


def command_reset(args: argparse.Namespace) -> int:
    workspace = resolve_inside(Path(args.workspace), ROOT / "work")
    if not workspace.exists():
        print(f"Nothing to reset at {workspace}")
        return 0
    shutil.rmtree(workspace)
    print(f"Removed learner workspace {workspace}")
    return 0


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description="FieldBridge Module 0 readiness-pack and evidence utility")
    sub = top.add_subparsers(dest="command", required=True)
    sub.add_parser("baseline", help="validate the supplied repository baseline").set_defaults(func=command_baseline)
    sub.add_parser("list-scenarios", help="show the six learner-visible scenarios").set_defaults(func=command_list)
    prepare = sub.add_parser("prepare", help="prepare a fresh learner workspace")
    prepare.add_argument("--scenario", required=True)
    prepare.add_argument("--workspace", default="work/current")
    prepare.add_argument("--force", action="store_true")
    prepare.set_defaults(func=command_prepare)
    validate = sub.add_parser("validate", help="validate a completed learner workspace")
    validate.add_argument("--workspace", default="work/current")
    validate.set_defaults(func=command_validate)
    seal = sub.add_parser("seal", help="copy and seal a valid readiness pack")
    seal.add_argument("--workspace", default="work/current")
    seal.add_argument("--evidence", default="evidence/current")
    seal.add_argument("--force", action="store_true")
    seal.set_defaults(func=command_seal)
    verify = sub.add_parser("verify", help="verify a previously sealed evidence directory")
    verify.add_argument("--evidence", default="evidence/current")
    verify.set_defaults(func=command_verify)
    control = sub.add_parser("apply-control", help="apply an assessor-provided changed-constraint record")
    control.add_argument("--control", required=True)
    control.add_argument("--workspace", default="work/current")
    control.set_defaults(func=command_control)
    reset = sub.add_parser("reset", help="remove one declared learner workspace")
    reset.add_argument("--workspace", default="work/current")
    reset.set_defaults(func=command_reset)
    return top


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        return int(args.func(args))
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
