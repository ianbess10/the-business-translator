"""v1.4 canonical evidence adapter around the frozen deterministic policy layer."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from stage_validation import derive_evidence_fields, validate_evidence_stage, validate_mapping_stage, validate_source_stage


SOURCE = Path(__file__).resolve().parent.parent / "evidence-gated-v1.2" / "pipeline.py"
SPEC = importlib.util.spec_from_file_location("evidence_gated_v1_2_policy", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load the frozen deterministic policy layer")
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)

derive_escalation = POLICY.derive_escalation
validate_final_decision = POLICY.validate_final_decision


def compose_final_decision(
    case: dict[str, Any], source_stage: dict[str, Any] | None,
    mapping_stage: dict[str, Any] | None, evidence_stage: dict[str, Any] | None,
    approved_obligation: dict[str, Any] | None, source_policy: dict[str, Any],
    applicability_policy: dict[str, Any], assurance_policy: dict[str, Any],
    escalation_policy: dict[str, Any], profile: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    case_id = case["case_id"]
    if source_stage is not None:
        validate_source_stage(source_stage, case_id)
    if mapping_stage is not None:
        validate_mapping_stage(
            mapping_stage, case_id, case["proposed_mapping"]["control_ids"],
            (item["control_id"] for item in profile["controls"]),
        )
    policy_evidence = None
    if evidence_stage is not None:
        validate_evidence_stage(evidence_stage, case_id)
        policy_evidence = derive_evidence_fields(evidence_stage)
    return POLICY.compose_final_decision(
        case, source_stage, mapping_stage, policy_evidence, approved_obligation,
        source_policy, applicability_policy, assurance_policy, escalation_policy, profile,
    )
