"""v1.4 canonical evidence validation with retained source and mapping controls."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


SOURCE = Path(__file__).resolve().parent.parent / "evidence-gated-v1.3" / "stage_validation.py"
SPEC = importlib.util.spec_from_file_location("evidence_gated_v1_3_stage_validation", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load the frozen v1.3 semantic validators")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

validate_source_stage = MODULE.validate_source_stage
validate_mapping_stage = MODULE.validate_mapping_stage

EVIDENCE_ASSESSMENTS = {
    "sufficient",
    "missing_operating_evidence",
    "design_deficiency",
    "adverse_operating_evidence",
    "insufficient_to_assess",
    "not_assessed_no_current_control",
}


def validate_evidence_stage(payload: dict[str, Any], expected_case_id: str | None = None) -> None:
    if set(payload) != {"case_id", "evidence_assessment", "rationale"}:
        raise ValueError("Canonical evidence output must contain only case_id, evidence_assessment and rationale")
    case_id = payload.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id must be a non-empty string")
    if expected_case_id is not None and case_id != expected_case_id:
        raise ValueError("Stage case ID does not match the supplied input")
    if payload.get("evidence_assessment") not in EVIDENCE_ASSESSMENTS:
        raise ValueError("Unknown canonical evidence assessment")
    rationale = payload.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("rationale must be a non-empty string")


def derive_evidence_fields(payload: dict[str, Any]) -> dict[str, Any]:
    """Derive the legacy policy adapter fields from one accepted classification."""
    validate_evidence_stage(payload, payload.get("case_id"))
    assessment = payload["evidence_assessment"]
    if assessment == "design_deficiency":
        severity = "high"
    elif assessment == "adverse_operating_evidence":
        severity = "high"
    elif assessment == "sufficient":
        severity = "not_applicable"
    else:
        severity = "unassessed"
    return {
        **payload,
        "design_deficiency_evidence_present": assessment == "design_deficiency",
        "adverse_indicator_present": assessment == "adverse_operating_evidence",
        "severity_recommendation": severity,
    }
