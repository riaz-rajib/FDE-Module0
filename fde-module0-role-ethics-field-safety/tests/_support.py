from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.module0 import ROOT, file_digest


def completed_charter():
    return {
        "engagement_id": "ENG-FDE0-001",
        "purpose": "Evaluate a synthetic workflow within the authorised lab.",
        "intended_outcomes": ["A traceable readiness decision"],
        "non_goals": ["Production deployment", "Legal conclusion"],
        "authorised_environments": ["Local synthetic lab"],
        "data_boundary": "Generated records only; no customer or personal information.",
        "decision_rights": [{"decision": "Technical experiment", "owner": "FDE"}],
        "stop_work_conditions": ["Undeclared data", "Missing authority", "Unsafe field condition"],
        "escalation_paths": [{"topic": "Privacy", "role": "Privacy adviser"}],
        "review_date_utc": "2026-09-01T00:00:00Z",
        "status": "approved"
    }


def completed_decision():
    return {
        "decision_id": "EDR-001",
        "request": "Use a synthetic dataset for a bounded experiment.",
        "purpose_and_affected_people": "Test workflow feasibility; synthetic operator personas are affected.",
        "authority": "Product owner approves the experiment; FDE owns technical execution.",
        "applicable_obligations": ["Engagement charter", "Synthetic-data boundary"],
        "uncertainties": ["Future production basis is not assessed"],
        "possible_harms": ["Evidence could be overstated"],
        "safer_options": ["Use generated fixtures and label evidence Synthetic"],
        "specialist_referrals": ["Privacy adviser for any future personal information"],
        "decision": "Proceed only in the synthetic lab.",
        "stop_or_proceed": "proceed_with_controls",
        "evidence_mode": "Synthetic",
        "validation_method": "Document-reviewed",
        "limitations": ["No production equivalence"],
        "review_or_expiry": "Review if purpose, data or environment changes."
    }


def completed_field_plan():
    return {
        "plan_id": "FIELD-001",
        "site_contact": "site.coordinator@northstar-relief-lab.invalid",
        "home_team_contact": "duty.manager@fieldbridge.invalid",
        "working_hours": "09:00-17:00 local; changes require manager approval",
        "on_call_boundary": "No on-call duty in this exercise",
        "maximum_consecutive_hours": 10,
        "check_in_cadence": "Start, midpoint and end of site day",
        "lone_worker_controls": ["Buddy contact", "Escalate missed check-in"],
        "travel_and_site_logistics": ["Approved transport", "Confirmed access window"],
        "emergency_contacts": ["Organisation emergency channel"],
        "harassment_and_wellbeing_escalation": ["Leave unsafe setting", "Contact manager"],
        "stop_work_conditions": ["No reliable communication", "Unsafe fatigue", "Harassment or threat"],
        "decompression_and_return_brief": "Protected recovery time and a structured return briefing.",
        "employer_duty_acknowledgement": True,
        "approval": "home-team manager"
    }


def completed_manifest():
    return {
        "engagement_id": "ENG-FDE0-001",
        "manifest_version": "1.0",
        "claims": [{
            "claim_id": "CLM-001",
            "statement": "The readiness pack passed the local validator.",
            "mode": "Local live",
            "validation_method": "Machine-verified",
            "artefacts": ["validation.txt"],
            "reviewer_or_verifier": "tools/module0.py",
            "captured_utc": "2026-08-19T00:00:00Z",
            "limitations": ["Human judgement remains assessor-reviewed"]
        }]
    }
