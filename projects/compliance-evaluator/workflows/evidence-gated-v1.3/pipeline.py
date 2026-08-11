"""v1.3 semantic gate wrapped around the frozen v1.2 deterministic policy layer."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from stage_validation import (
    validate_evidence_stage,
    validate_mapping_stage,
    validate_source_stage,
)


WORKFLOW_DIR = Path(__file__).resolve().parent
V1_2_PIPELINE_PATH = WORKFLOW_DIR.parent / "evidence-gated-v1.2" / "pipeline.py"
_SPEC = importlib.util.spec_from_file_location("evidence_gated_v1_2_pipeline", V1_2_PIPELINE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Could not load the frozen v1.2 policy layer")
_V1_2 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_V1_2)

derive_escalation = _V1_2.derive_escalation
validate_final_decision = _V1_2.validate_final_decision


def compose_final_decision(
    case: dict[str, Any],
    source_stage: dict[str, Any] | None,
    mapping_stage: dict[str, Any] | None,
    evidence_stage: dict[str, Any] | None,
    approved_obligation: dict[str, Any] | None,
    source_policy: dict[str, Any],
    applicability_policy: dict[str, Any],
    assurance_policy: dict[str, Any],
    escalation_policy: dict[str, Any],
    profile: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    case_id = case["case_id"]
    if source_stage is not None:
        validate_source_stage(source_stage, case_id)
    if mapping_stage is not None:
        validate_mapping_stage(
            mapping_stage,
            case_id,
            case["proposed_mapping"]["control_ids"],
            (item["control_id"] for item in profile["controls"]),
        )
    if evidence_stage is not None:
        validate_evidence_stage(evidence_stage, case_id)
    return _V1_2.compose_final_decision(
        case,
        source_stage,
        mapping_stage,
        evidence_stage,
        approved_obligation,
        source_policy,
        applicability_policy,
        assurance_policy,
        escalation_policy,
        profile,
    )
