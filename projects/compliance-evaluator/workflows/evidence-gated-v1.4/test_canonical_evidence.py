#!/usr/bin/env python3
"""Prove canonical evidence shape and deterministic operational derivation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from stage_validation import EVIDENCE_ASSESSMENTS, derive_evidence_fields, validate_evidence_stage


WORKFLOW_DIR = Path(__file__).resolve().parent


def main() -> int:
    response_format = json.loads((WORKFLOW_DIR / "schemas" / "evidence-stage.schema.json").read_text())
    properties = set(response_format["schema"]["properties"])
    redundant = {"design_deficiency_evidence_present", "adverse_indicator_present", "severity_recommendation"}
    if properties & redundant:
        raise AssertionError("Canonical evidence schema contains redundant classification fields")
    validator = Draft202012Validator(response_format["schema"])
    expected = {
        "sufficient": (False, False, "not_applicable"),
        "missing_operating_evidence": (False, False, "unassessed"),
        "design_deficiency": (True, False, "high"),
        "adverse_operating_evidence": (False, True, "high"),
        "insufficient_to_assess": (False, False, "unassessed"),
        "not_assessed_no_current_control": (False, False, "unassessed"),
    }
    for assessment in sorted(EVIDENCE_ASSESSMENTS):
        payload = {"case_id": "CERT-EVIDENCE-001", "evidence_assessment": assessment, "rationale": "Generic boundary fixture."}
        validator.validate(payload)
        validate_evidence_stage(payload, payload["case_id"])
        derived = derive_evidence_fields(payload)
        actual = (derived["design_deficiency_evidence_present"], derived["adverse_indicator_present"], derived["severity_recommendation"])
        if actual != expected[assessment]:
            raise AssertionError(f"Incorrect deterministic derivation for {assessment}")
    con007_shape = {"case_id": "GENERIC-MISSING-RECORD", "evidence_assessment": "missing_operating_evidence", "rationale": "A framework exists but a required completed record is absent."}
    validate_evidence_stage(con007_shape, con007_shape["case_id"])
    for invalid in (
        {**con007_shape, "design_deficiency_evidence_present": False},
        {**con007_shape, "rationale": ""},
        {**con007_shape, "case_id": "OTHER"},
    ):
        try:
            validate_evidence_stage(invalid, con007_shape["case_id"])
        except ValueError:
            continue
        raise AssertionError("Invalid canonical evidence state was accepted")
    print("evidence_gated_v1_4_canonical_evidence_passed: 6 assessments, 6 deterministic derivations and 3 rejected states")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
