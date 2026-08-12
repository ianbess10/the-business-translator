#!/usr/bin/env python3
"""Offline v1.1 boundary and reconciliation tests; no API calls or labels."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from pipeline import compose_final_decision, validate_final_decision


WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORKFLOW_DIR.parents[1]
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


SOURCE_POLICY = load_json(WORKFLOW_DIR / "policies" / "source-transition-policy-v1.1.json")
APPLICABILITY_POLICY = load_json(WORKFLOW_DIR / "policies" / "applicability-policy-v1.1.json")
EVIDENCE_POLICY = load_json(WORKFLOW_DIR / "policies" / "evidence-decision-policy-v1.1.json")
ESCALATION_POLICY = load_json(WORKFLOW_DIR / "policies" / "escalation-policy-v1.1.json")
PROFILE = load_json(PROJECT_DIR / "profiles" / "synthetic-investment-wealth-institution-v1.0.json")
APPROVED_OBLIGATION = load_json(
    PROJECT_DIR
    / "schemas"
    / "control-evidence-schema-v1.0"
    / "fixtures"
    / "approved-obligation.json"
)


def case(
    case_id: str,
    workstream: str,
    source_ids: list[str],
    approved: bool,
    missing_facts: list[str] | None = None,
    institution_facts: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "workstream": workstream,
        "source_ids": source_ids,
        "institution_facts": institution_facts or ["The relevant activity is in scope."],
        "missing_facts": missing_facts or [],
        "upstream_obligation": {
            "supplied": approved,
            "status": "approved" if approved else "pending",
            "obligation_id": "OBL-CONDUCT-0001" if approved else None,
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
    coverage_gap_present: bool = False,
    design_deficiency_evidence_present: bool = False,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "proposal_disposition": "reject",
        "mapping_completeness": mapping_completeness,
        "supported_control_ids": control_ids or ["C-CON-006"],
        "coverage_gap_present": coverage_gap_present,
        "evidence_assessment": evidence_assessment,
        "design_deficiency_evidence_present": design_deficiency_evidence_present,
        "adverse_indicator_present": evidence_assessment == "adverse_operating_evidence",
        "severity_recommendation": "high"
        if evidence_assessment in {"design_deficiency", "adverse_operating_evidence"}
        else "not_applicable",
        "rationale": "Coverage and evidence were assessed as separate dimensions.",
    }


def compose(
    input_case: dict[str, Any],
    stage_one: dict[str, Any] | None,
    stage_two: dict[str, Any] | None,
    approved_obligation: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    return compose_final_decision(
        input_case,
        stage_one,
        stage_two,
        approved_obligation,
        SOURCE_POLICY,
        APPLICABILITY_POLICY,
        EVIDENCE_POLICY,
        ESCALATION_POLICY,
        PROFILE,
    )


def expect_value_error(action: Any, text: str) -> None:
    try:
        action()
        raise AssertionError(f"Expected ValueError containing: {text}")
    except ValueError as exc:
        assert text in str(exc)


def run_tests() -> None:
    scenario_count = 0

    final_pending = case("AML-900", "aml_cft", ["SA-AML-SP-005"], approved=False)
    decision, trace = compose(final_pending, source_stage("AML-900"), None)
    assert decision["source_use_disposition"] == "final_change_event"
    assert decision["obligation_outcome"] == "final_change_pending_commencement"
    assert decision["applicability_status"] == "applicability_uncertain"
    assert decision["assurance_gate"] == "not_entered"
    assert decision["escalation_roles"] == ["AML Compliance Officer", "Legal Counsel"]
    assert trace["source_stage_bypassed"] is False
    scenario_count += 1

    guidance = case("AML-901", "aml_cft", ["SA-AML-SP-003"], approved=False)
    guidance_stage = source_stage("AML-901", applicability="out_of_scope")
    decision, _ = compose(guidance, guidance_stage, None)
    assert decision["source_use_disposition"] == "guidance_only"
    assert decision["applicability_status"] == "applicable_candidate"
    scenario_count += 1

    excluded = case(
        "AML-902",
        "aml_cft",
        ["SA-AML-SP-003"],
        approved=False,
        institution_facts=["Virtual-asset services are explicitly excluded from the profile."],
    )
    decision, _ = compose(excluded, source_stage("AML-902"), None)
    assert decision["applicability_status"] == "out_of_scope"
    scenario_count += 1

    uncertain = case(
        "AML-903",
        "aml_cft",
        ["SA-AML-SP-003"],
        approved=False,
        missing_facts=["the institution classification"],
    )
    decision, _ = compose(uncertain, source_stage("AML-903"), None)
    assert decision["applicability_status"] == "applicability_uncertain"
    scenario_count += 1

    approved = case("CON-900", "market_conduct", ["SA-CONDUCT-SP-003"], True)
    decision, trace = compose(
        approved,
        None,
        assurance_stage("CON-900", "sufficient"),
        APPROVED_OBLIGATION,
    )
    assert decision["source_use_disposition"] == "binding_candidate"
    assert decision["obligation_outcome"] == "candidate_binding_obligation"
    assert decision["applicability_status"] == "applicable_candidate"
    assert decision["mapping_status"] == "mapped"
    assert trace["approved_obligation_authority_used"] is True
    assert trace["source_stage_bypassed"] is True
    scenario_count += 1

    expect_value_error(
        lambda: compose(
            approved,
            source_stage("CON-900", "uncertain"),
            assurance_stage("CON-900", "sufficient"),
            APPROVED_OBLIGATION,
        ),
        "must bypass",
    )
    scenario_count += 1

    unreviewed = deepcopy(APPROVED_OBLIGATION)
    unreviewed["human_review"]["status"] = "pending"
    expect_value_error(
        lambda: compose(
            approved,
            None,
            assurance_stage("CON-900", "sufficient"),
            unreviewed,
        ),
        "human review",
    )
    scenario_count += 1

    missing = assurance_stage(
        "CON-901",
        "missing_operating_evidence",
        mapping_completeness="partial",
        coverage_gap_present=False,
    )
    decision, trace = compose(
        case("CON-901", "market_conduct", ["SA-CONDUCT-SP-003"], True),
        None,
        missing,
        APPROVED_OBLIGATION,
    )
    assert decision["mapping_status"] == "mapped"
    assert decision["assurance_outcome"] == "insufficient_evidence"
    assert decision["gap_severity"] == "unassessed"
    assert decision["escalation_required"] is False
    assert trace["mapping_completeness_raw"] == "partial"
    assert trace["mapping_completeness_decided"] == "complete"
    scenario_count += 1

    adverse = assurance_stage(
        "CON-902",
        "adverse_operating_evidence",
        mapping_completeness="partial",
        coverage_gap_present=False,
    )
    decision, _ = compose(
        case("CON-902", "market_conduct", ["SA-CONDUCT-SP-003"], True),
        None,
        adverse,
        APPROVED_OBLIGATION,
    )
    assert decision["mapping_status"] == "mapped"
    assert decision["gap_types"] == ["operating_exception"]
    assert decision["escalation_roles"] == ["Conduct Risk Officer", "Head of Compliance"]
    scenario_count += 1

    partial = assurance_stage(
        "CON-903",
        "sufficient",
        mapping_completeness="complete",
        coverage_gap_present=True,
    )
    decision, trace = compose(
        case("CON-903", "market_conduct", ["SA-CONDUCT-SP-003"], True),
        None,
        partial,
        APPROVED_OBLIGATION,
    )
    assert decision["mapping_status"] == "partially_mapped"
    assert decision["gap_types"] == ["partial_coverage"]
    assert decision["gap_severity"] == "medium"
    assert decision["escalation_required"] is False
    assert trace["mapping_completeness_decided"] == "partial"
    scenario_count += 1

    partial_not_design = assurance_stage(
        "CON-904",
        "design_deficiency",
        mapping_completeness="partial",
        coverage_gap_present=True,
        design_deficiency_evidence_present=False,
    )
    decision, _ = compose(
        case("CON-904", "market_conduct", ["SA-CONDUCT-SP-003"], True),
        None,
        partial_not_design,
        APPROVED_OBLIGATION,
    )
    assert decision["gap_types"] == ["partial_coverage"]
    assert decision["gap_severity"] == "medium"
    assert decision["escalation_required"] is False
    scenario_count += 1

    design_gap = assurance_stage(
        "CON-905",
        "design_deficiency",
        mapping_completeness="partial",
        coverage_gap_present=True,
        design_deficiency_evidence_present=True,
    )
    decision, _ = compose(
        case("CON-905", "market_conduct", ["SA-CONDUCT-SP-003"], True),
        None,
        design_gap,
        APPROVED_OBLIGATION,
    )
    assert decision["gap_types"] == ["control_design"]
    assert decision["gap_severity"] == "high"
    assert decision["escalation_roles"] == ["Head of Compliance"]
    scenario_count += 1

    conflict = case(
        "CON-906",
        "market_conduct",
        ["SA-CONDUCT-SP-002", "SA-CONDUCT-SP-003"],
        False,
        missing_facts=["complete amendment chain", "provision-level reconciliation"],
    )
    conflict_stage = source_stage("CON-906")
    conflict_stage["source_conflict_present"] = True
    decision, _ = compose(conflict, conflict_stage, None)
    assert decision["source_use_disposition"] == "blocked"
    assert decision["obligation_outcome"] == "source_conflict"
    assert decision["escalation_roles"] == ["Head of Compliance", "Legal Counsel"]
    scenario_count += 1

    unknown_control = assurance_stage("CON-907", "sufficient", ["C-CON-999"])
    expect_value_error(
        lambda: compose(
            case("CON-907", "market_conduct", ["SA-CONDUCT-SP-003"], True),
            None,
            unknown_control,
            APPROVED_OBLIGATION,
        ),
        "not in the frozen catalogue",
    )
    scenario_count += 1

    tampered = deepcopy(decision)
    tampered["escalation_required"] = False
    tampered["escalation_roles"] = []
    expect_value_error(
        lambda: validate_final_decision(
            tampered, PROFILE, ESCALATION_POLICY, "market_conduct"
        ),
        "escalation",
    )
    scenario_count += 1

    proposal_a = case("CON-908", "market_conduct", ["SA-CONDUCT-SP-003"], True)
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
    stage_two = assurance_stage("CON-908", "sufficient")
    decision_a, _ = compose(proposal_a, None, stage_two, APPROVED_OBLIGATION)
    decision_b, _ = compose(proposal_b, None, stage_two, APPROVED_OBLIGATION)
    assert decision_a == decision_b
    scenario_count += 1

    input_paths = (
        DATASET_DIR / "inputs" / "aml-cft.json",
        DATASET_DIR / "inputs" / "market-conduct.json",
    )
    frozen_inputs: list[dict[str, Any]] = []
    for path in input_paths:
        frozen_inputs.extend(load_json(path))
    for input_case in frozen_inputs:
        case_id = input_case["case_id"]
        entered = (
            input_case["upstream_obligation"]["supplied"] is True
            and input_case["upstream_obligation"]["status"] == "approved"
        )
        if entered:
            stage_one = None
            approved_record = APPROVED_OBLIGATION
            stage_two = assurance_stage(
                case_id,
                "sufficient",
                input_case["proposed_mapping"]["control_ids"],
            )
        else:
            stage_one = source_stage(case_id)
            stage_one["source_conflict_present"] = len(input_case["source_ids"]) > 1
            approved_record = None
            stage_two = None
        smoke_decision, smoke_trace = compose(
            input_case, stage_one, stage_two, approved_record
        )
        assert smoke_decision["case_id"] == case_id
        assert smoke_trace["reconciliation_passed"] is True
        assert smoke_trace["case_specific_override"] is False
        if entered:
            assert smoke_trace["approved_obligation_authority_used"] is True
            assert smoke_trace["source_stage_bypassed"] is True
        else:
            assert smoke_decision["assurance_gate"] == "not_entered"
            assert smoke_decision["control_mappings"] == []

    assert len(frozen_inputs) == 24
    assert scenario_count == 16
    print(
        "evidence_gated_v1_1_offline_tests_passed: "
        "16 boundary scenarios and 24 input-path smoke cases"
    )


if __name__ == "__main__":
    run_tests()
