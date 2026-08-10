#!/usr/bin/env python3
"""Offline policy and reconciliation tests; makes no API calls and loads no labels."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from pipeline import compose_final_decision, validate_final_decision


WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORKFLOW_DIR.parents[1]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


SOURCE_POLICY = load_json(WORKFLOW_DIR / "policies" / "source-transition-policy-v1.0.json")
EVIDENCE_POLICY = load_json(WORKFLOW_DIR / "policies" / "evidence-decision-policy-v1.0.json")
ESCALATION_POLICY = load_json(WORKFLOW_DIR / "policies" / "escalation-policy-v1.0.json")
PROFILE = load_json(PROJECT_DIR / "profiles" / "synthetic-investment-wealth-institution-v1.0.json")


def case(
    case_id: str,
    workstream: str,
    source_ids: list[str],
    approved: bool,
    missing_facts: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "workstream": workstream,
        "source_ids": source_ids,
        "missing_facts": missing_facts or [],
        "upstream_obligation": {
            "supplied": approved,
            "status": "approved" if approved else "pending",
        },
        "proposed_mapping": {
            "control_ids": ["C-CON-006"],
            "owner_role": "Conduct Risk Officer",
            "mapping_status": "mapped",
        },
        "proposal_under_test": {
            "source_use_disposition": "binding_candidate",
            "obligation_outcome": "candidate_binding_obligation",
            "applicability_status": "applicable_candidate",
            "assurance_outcome": "mapped_and_evidenced",
            "escalation_required": False,
        },
    }


def source_stage(case_id: str, applicability: str = "applicable") -> dict[str, Any]:
    return {
        "case_id": case_id,
        "proposal_disposition": "reject",
        "source_classification": "binding_candidate",
        "obligation_support": "supported_binding",
        "applicability_assessment": applicability,
        "material_missing_fact_types": [],
        "source_conflict_present": False,
        "rationale": "The supplied facts were assessed independently of the proposal.",
    }


def assurance_stage(
    case_id: str,
    evidence_assessment: str,
    control_ids: list[str] | None = None,
    mapping_completeness: str = "complete",
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "proposal_disposition": "reject",
        "mapping_completeness": mapping_completeness,
        "supported_control_ids": control_ids or ["C-CON-006"],
        "evidence_assessment": evidence_assessment,
        "adverse_indicator_present": evidence_assessment == "adverse_operating_evidence",
        "severity_recommendation": "high"
        if evidence_assessment in {"design_deficiency", "adverse_operating_evidence"}
        else "not_applicable",
        "rationale": "The evidence was assessed against the authoritative catalogue.",
    }


def compose(
    input_case: dict[str, Any],
    stage_one: dict[str, Any],
    stage_two: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    return compose_final_decision(
        input_case,
        stage_one,
        stage_two,
        SOURCE_POLICY,
        EVIDENCE_POLICY,
        ESCALATION_POLICY,
        PROFILE,
    )


def run_tests() -> None:
    final_pending = case(
        "AML-900", "aml_cft", ["SA-AML-SP-005"], approved=False
    )
    decision, trace = compose(final_pending, source_stage("AML-900"), None)
    assert decision["source_use_disposition"] == "final_change_event"
    assert decision["obligation_outcome"] == "final_change_pending_commencement"
    assert decision["applicability_status"] == "applicability_uncertain"
    assert decision["assurance_gate"] == "not_entered"
    assert decision["control_mappings"] == []
    assert decision["escalation_required"] is True
    assert decision["escalation_roles"] == ["AML Compliance Officer", "Legal Counsel"]
    assert trace["reconciliation_passed"] is True

    sufficient = case(
        "CON-900", "market_conduct", ["SA-CONDUCT-SP-003"], approved=True
    )
    decision, _ = compose(
        sufficient, source_stage("CON-900"), assurance_stage("CON-900", "sufficient")
    )
    assert decision["assurance_gate"] == "entered"
    assert decision["control_mappings"] == [
        {"control_id": "C-CON-006", "owner_role": "Complaints Manager"}
    ]
    assert decision["assurance_outcome"] == "mapped_and_evidenced"
    assert decision["escalation_required"] is False

    missing = case(
        "CON-901", "market_conduct", ["SA-CONDUCT-SP-003"], approved=True
    )
    decision, _ = compose(
        missing,
        source_stage("CON-901"),
        assurance_stage("CON-901", "missing_operating_evidence"),
    )
    assert decision["assurance_outcome"] == "insufficient_evidence"
    assert decision["gap_severity"] == "unassessed"
    assert decision["remediation_action_types"] == ["evidence_request"]
    assert decision["escalation_required"] is False

    adverse = case(
        "CON-902", "market_conduct", ["SA-CONDUCT-SP-003"], approved=True
    )
    decision, _ = compose(
        adverse,
        source_stage("CON-902"),
        assurance_stage("CON-902", "adverse_operating_evidence"),
    )
    assert decision["gap_types"] == ["operating_exception"]
    assert decision["gap_severity"] == "high"
    assert decision["remediation_action_types"] == ["operating_remediation"]
    assert decision["escalation_roles"] == ["Conduct Risk Officer", "Head of Compliance"]

    conflict = case(
        "CON-903",
        "market_conduct",
        ["SA-CONDUCT-SP-002", "SA-CONDUCT-SP-003"],
        approved=False,
        missing_facts=["complete amendment chain", "provision-level reconciliation"],
    )
    conflict_stage = source_stage("CON-903")
    conflict_stage["source_conflict_present"] = True
    decision, _ = compose(conflict, conflict_stage, None)
    assert decision["source_use_disposition"] == "blocked"
    assert decision["obligation_outcome"] == "source_conflict"
    assert decision["escalation_roles"] == ["Head of Compliance", "Legal Counsel"]

    unknown_control = assurance_stage("CON-904", "sufficient", ["C-CON-999"])
    try:
        compose(
            case("CON-904", "market_conduct", ["SA-CONDUCT-SP-003"], True),
            source_stage("CON-904"),
            unknown_control,
        )
        raise AssertionError("Unknown catalogue control should have been rejected")
    except ValueError as exc:
        assert "not in the frozen catalogue" in str(exc)

    tampered = deepcopy(decision)
    tampered["escalation_required"] = False
    tampered["escalation_roles"] = []
    try:
        validate_final_decision(
            tampered, PROFILE, ESCALATION_POLICY, "market_conduct"
        )
        raise AssertionError("Policy-inconsistent escalation should have been rejected")
    except ValueError as exc:
        assert "escalation" in str(exc)

    proposal_a = case(
        "CON-905", "market_conduct", ["SA-CONDUCT-SP-003"], approved=True
    )
    proposal_b = deepcopy(proposal_a)
    proposal_b["proposal_under_test"].update(
        {
            "source_use_disposition": "blocked",
            "obligation_outcome": "source_conflict",
            "applicability_status": "out_of_scope",
            "assurance_outcome": "potential_control_gap",
            "escalation_required": True,
        }
    )
    proposal_b["proposed_mapping"]["owner_role"] = "Head of Compliance"
    stage_one = source_stage("CON-905")
    stage_two = assurance_stage("CON-905", "sufficient")
    decision_a, _ = compose(proposal_a, stage_one, stage_two)
    decision_b, _ = compose(proposal_b, stage_one, stage_two)
    assert decision_a == decision_b

    input_paths = (
        PROJECT_DIR / "datasets" / "baseline-v1.0" / "inputs" / "aml-cft.json",
        PROJECT_DIR
        / "datasets"
        / "baseline-v1.0"
        / "inputs"
        / "market-conduct.json",
    )
    frozen_inputs: list[dict[str, Any]] = []
    for path in input_paths:
        frozen_inputs.extend(load_json(path))
    for input_case in frozen_inputs:
        case_id = input_case["case_id"]
        stage_one = source_stage(case_id)
        stage_one["source_conflict_present"] = len(input_case["source_ids"]) > 1
        entered = (
            input_case["upstream_obligation"]["supplied"] is True
            and input_case["upstream_obligation"]["status"] == "approved"
        )
        if entered:
            stage_two = assurance_stage(
                case_id,
                "sufficient",
                input_case["proposed_mapping"]["control_ids"],
                "complete",
            )
        else:
            stage_two = None
        smoke_decision, smoke_trace = compose(input_case, stage_one, stage_two)
        assert smoke_decision["case_id"] == case_id
        assert smoke_trace["reconciliation_passed"] is True
        if not entered:
            assert smoke_decision["assurance_gate"] == "not_entered"
            assert smoke_decision["control_mappings"] == []

    assert len(frozen_inputs) == 24
    print(
        "evidence_gated_pipeline_offline_tests_passed: "
        "7 control scenarios and 24 input-path smoke cases"
    )


if __name__ == "__main__":
    run_tests()
