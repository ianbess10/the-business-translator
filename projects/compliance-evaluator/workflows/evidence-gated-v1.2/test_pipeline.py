#!/usr/bin/env python3
"""Offline boundary and 24-path smoke tests for Evidence-Gated v1.2."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from pipeline import compose_final_decision


WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORKFLOW_DIR.parents[1]
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


PROFILE = load_json(
    PROJECT_DIR / "profiles" / "synthetic-investment-wealth-institution-v1.0.json"
)
SOURCE_POLICY = load_json(
    WORKFLOW_DIR / "policies" / "source-transition-policy-v1.2.json"
)
APPLICABILITY_POLICY = load_json(
    WORKFLOW_DIR / "policies" / "applicability-policy-v1.2.json"
)
ASSURANCE_POLICY = load_json(
    WORKFLOW_DIR / "policies" / "assurance-decision-policy-v1.2.json"
)
ESCALATION_POLICY = load_json(
    WORKFLOW_DIR / "policies" / "escalation-policy-v1.2.json"
)


def all_records(kind: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for name in ("aml-cft.json", "market-conduct.json"):
        records.extend(load_json(DATASET_DIR / kind / name))
    return records


INPUTS = {item["case_id"]: item for item in all_records("inputs")}
LABELS = {item["case_id"]: item for item in all_records("labels")}


def approved_obligation(case: dict[str, Any]) -> dict[str, Any] | None:
    fixture = case["upstream_obligation"].get("fixture_path")
    if not fixture:
        return None
    return load_json((DATASET_DIR / fixture).resolve())


def source_stage_for(case_id: str) -> dict[str, Any]:
    expected = LABELS[case_id]["expected"]
    support = (
        "unsupported_extension"
        if expected["obligation_outcome"] == "unsupported_obligation"
        else "exact_supported"
    )
    outcome = expected["obligation_outcome"]
    if outcome == "final_change_pending_commencement":
        readiness = "pending_commencement"
    elif outcome == "source_conflict":
        readiness = "source_conflict"
    elif outcome == "blocked_source":
        readiness = "blocked_source"
    else:
        readiness = "human_review_required"
    source_use = expected["source_use_disposition"]
    classification = source_use if source_use in {
        "binding_candidate",
        "guidance_only",
        "final_change_event",
        "draft_watchlist",
        "historical_only",
        "strategy_context",
        "blocked",
    } else "source_conflict"
    applicability = {
        "applicable_candidate": "applicable",
        "out_of_scope": "out_of_scope",
        "applicability_uncertain": "uncertain",
        "not_assessed": "not_assessed",
    }[expected["applicability_status"]]
    return {
        "case_id": case_id,
        "proposal_disposition": "reject" if support != "exact_supported" else "accept",
        "source_classification": classification,
        "statement_support": support,
        "legal_readiness": readiness,
        "applicability_assessment": applicability,
        "material_missing_fact_types": [],
        "source_conflict_present": outcome == "source_conflict",
        "unsupported_elements": [] if support == "exact_supported" else ["extension"],
        "rationale": "Synthetic offline stage output for the frozen expected boundary.",
    }


def mapping_stage_for(case_id: str) -> dict[str, Any]:
    case = INPUTS[case_id]
    expected = LABELS[case_id]["expected"]
    current_ids = [item["control_id"] for item in expected["control_mappings"]]
    status_to_completeness = {
        "mapped": "complete",
        "partially_mapped": "partial",
        "no_suitable_control_identified": "no_suitable_control",
    }
    completeness = status_to_completeness[expected["mapping_status"]]
    reviewed = approved_obligation(case)
    affected = set(
        reviewed.get("operating_impact", {}).get("affected_control_ids", [])
        if reviewed
        else []
    )
    proposed = set(case["proposed_mapping"]["control_ids"])
    candidates = sorted(affected - proposed) if completeness == "partial" else []
    return {
        "case_id": case_id,
        "proposal_disposition": "accept" if completeness == "complete" else "amend",
        "current_mapping_control_ids": current_ids,
        "candidate_additional_control_ids": candidates,
        "mapping_completeness": completeness,
        "uncovered_obligation_elements": (
            [] if completeness == "complete" else ["uncovered obligation element"]
        ),
        "rationale": "Synthetic offline current-mapping assessment.",
    }


def evidence_stage_for(case_id: str) -> dict[str, Any]:
    expected = LABELS[case_id]["expected"]
    outcome = expected["assurance_outcome"]
    gaps = set(expected["gap_types"])
    if outcome == "mapped_and_evidenced":
        assessment, design, adverse, severity = "sufficient", False, False, "not_applicable"
    elif outcome == "insufficient_evidence":
        assessment, design, adverse, severity = (
            "missing_operating_evidence",
            False,
            False,
            "unassessed",
        )
    elif "control_design" in gaps:
        assessment, design, adverse, severity = "design_deficiency", True, False, "high"
    elif "operating_exception" in gaps:
        assessment, design, adverse, severity = (
            "adverse_operating_evidence",
            False,
            True,
            "high",
        )
    elif "no_control" in gaps:
        assessment, design, adverse, severity = (
            "not_assessed_no_current_control",
            False,
            False,
            "unassessed",
        )
    else:
        assessment, design, adverse, severity = "sufficient", False, False, "not_applicable"
    return {
        "case_id": case_id,
        "evidence_assessment": assessment,
        "design_deficiency_evidence_present": design,
        "adverse_indicator_present": adverse,
        "severity_recommendation": severity,
        "rationale": "Synthetic offline evidence assessment independent from mapping.",
    }


def compose(
    case: dict[str, Any],
    source_stage: dict[str, Any] | None,
    mapping_stage: dict[str, Any] | None,
    evidence_stage: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    return compose_final_decision(
        case,
        source_stage,
        mapping_stage,
        evidence_stage,
        approved_obligation(case),
        SOURCE_POLICY,
        APPLICABILITY_POLICY,
        ASSURANCE_POLICY,
        ESCALATION_POLICY,
        PROFILE,
    )


def expect_error(action: Callable[[], Any], text: str) -> None:
    try:
        action()
    except ValueError as exc:
        if text not in str(exc):
            raise AssertionError(f"Expected error containing {text!r}; found {exc}") from exc
        return
    raise AssertionError(f"Expected ValueError containing {text!r}")


def test_selected_boundaries() -> int:
    scenario_count = 0

    source_case = copy.deepcopy(INPUTS["CON-001"])
    exact = source_stage_for("CON-001")
    exact["legal_readiness"] = "pending_commencement"
    decision, trace = compose(source_case, exact, None, None)
    assert decision["obligation_outcome"] == "candidate_binding_obligation"
    assert trace["statement_support"] == "exact_supported"
    scenario_count += 1

    unsupported = copy.deepcopy(exact)
    unsupported.update(
        {
            "proposal_disposition": "reject",
            "statement_support": "unsupported_extension",
            "unsupported_elements": ["added frequency"],
        }
    )
    decision, _ = compose(source_case, unsupported, None, None)
    assert decision["obligation_outcome"] == "unsupported_obligation"
    scenario_count += 1

    assurance_case = copy.deepcopy(INPUTS["CON-007"])
    mapping = mapping_stage_for("CON-007")
    evidence = evidence_stage_for("CON-007")
    expect_error(
        lambda: compose(assurance_case, source_stage_for("CON-007"), mapping, evidence),
        "bypass",
    )
    scenario_count += 1

    decision, trace = compose(assurance_case, None, mapping, evidence)
    assert decision["mapping_status"] == "mapped"
    assert decision["assurance_outcome"] == "insufficient_evidence"
    assert trace["evidence_stage_can_change_mapping"] is False
    scenario_count += 1

    partial_case = copy.deepcopy(INPUTS["CON-010"])
    partial_mapping = mapping_stage_for("CON-010")
    partial_evidence = evidence_stage_for("CON-010")
    decision, trace = compose(partial_case, None, partial_mapping, partial_evidence)
    assert [item["control_id"] for item in decision["control_mappings"]] == ["C-CON-006"]
    assert trace["candidate_additional_control_ids"] == ["C-CON-007"]
    assert "C-CON-007" not in trace["resolved_control_owners"]
    assert trace["candidate_control_owners"]["C-CON-007"] == "Conduct Risk Officer"
    scenario_count += 1

    invalid_current = copy.deepcopy(partial_mapping)
    invalid_current["current_mapping_control_ids"] = ["C-CON-006", "C-CON-007"]
    invalid_current["candidate_additional_control_ids"] = []
    invalid_current["mapping_completeness"] = "complete"
    invalid_current["uncovered_obligation_elements"] = []
    expect_error(
        lambda: compose(partial_case, None, invalid_current, partial_evidence),
        "subset",
    )
    scenario_count += 1

    overlap = copy.deepcopy(partial_mapping)
    overlap["candidate_additional_control_ids"] = ["C-CON-006"]
    expect_error(lambda: compose(partial_case, None, overlap, partial_evidence), "disjoint")
    scenario_count += 1

    submitted_candidate = copy.deepcopy(mapping_stage_for("CON-005"))
    submitted_candidate["current_mapping_control_ids"] = ["C-CON-006"]
    submitted_candidate["candidate_additional_control_ids"] = ["C-CON-007"]
    submitted_candidate["mapping_completeness"] = "partial"
    submitted_candidate["uncovered_obligation_elements"] = ["submitted but unsupported"]
    expect_error(
        lambda: compose(INPUTS["CON-005"], None, submitted_candidate, evidence_stage_for("CON-005")),
        "submitted mapping control",
    )
    scenario_count += 1

    adverse_case = copy.deepcopy(INPUTS["CON-011"])
    adverse_decision, _ = compose(
        adverse_case,
        None,
        mapping_stage_for("CON-011"),
        evidence_stage_for("CON-011"),
    )
    assert adverse_decision["mapping_status"] == "mapped"
    assert adverse_decision["gap_types"] == ["operating_exception"]
    assert adverse_decision["escalation_required"] is True
    scenario_count += 1

    partial_missing = copy.deepcopy(partial_evidence)
    partial_missing.update(
        {
            "evidence_assessment": "missing_operating_evidence",
            "severity_recommendation": "unassessed",
        }
    )
    decision, _ = compose(partial_case, None, partial_mapping, partial_missing)
    assert decision["gap_types"] == ["partial_coverage"]
    assert decision["escalation_required"] is False
    scenario_count += 1

    design_case = copy.deepcopy(INPUTS["CON-008"])
    design_decision, _ = compose(
        design_case,
        None,
        mapping_stage_for("CON-008"),
        evidence_stage_for("CON-008"),
    )
    assert design_decision["gap_types"] == ["control_design"]
    assert design_decision["escalation_required"] is True
    scenario_count += 1

    no_control_mapping = copy.deepcopy(mapping_stage_for("CON-010"))
    no_control_mapping.update(
        {
            "current_mapping_control_ids": [],
            "candidate_additional_control_ids": ["C-CON-007"],
            "mapping_completeness": "no_suitable_control",
        }
    )
    no_control_evidence = copy.deepcopy(partial_evidence)
    no_control_evidence.update(
        {
            "evidence_assessment": "not_assessed_no_current_control",
            "severity_recommendation": "unassessed",
        }
    )
    decision, _ = compose(partial_case, None, no_control_mapping, no_control_evidence)
    assert decision["mapping_status"] == "no_suitable_control_identified"
    assert decision["gap_types"] == ["no_control"]
    scenario_count += 1

    mismatched_design = copy.deepcopy(evidence_stage_for("CON-008"))
    mismatched_design["design_deficiency_evidence_present"] = False
    expect_error(
        lambda: compose(design_case, None, mapping_stage_for("CON-008"), mismatched_design),
        "Design-deficiency",
    )
    scenario_count += 1

    mismatched_adverse = copy.deepcopy(evidence_stage_for("CON-011"))
    mismatched_adverse["adverse_indicator_present"] = False
    expect_error(
        lambda: compose(adverse_case, None, mapping_stage_for("CON-011"), mismatched_adverse),
        "Adverse-operating",
    )
    scenario_count += 1

    invalid_no_current = copy.deepcopy(evidence_stage_for("CON-007"))
    invalid_no_current["evidence_assessment"] = "not_assessed_no_current_control"
    expect_error(
        lambda: compose(assurance_case, None, mapping_stage_for("CON-007"), invalid_no_current),
        "current control",
    )
    scenario_count += 1

    expect_error(lambda: compose(source_case, None, None, None), "requires a source")
    scenario_count += 1

    expect_error(
        lambda: compose(source_case, source_stage_for("CON-001"), partial_mapping, partial_evidence),
        "Closed assurance",
    )
    scenario_count += 1

    owner_case = copy.deepcopy(INPUTS["CON-006"])
    owner_case["proposed_mapping"]["owner_role"] = "Conduct Risk Officer"
    owner_decision, _ = compose(
        owner_case,
        None,
        mapping_stage_for("CON-006"),
        evidence_stage_for("CON-006"),
    )
    assert owner_decision["control_mappings"] == [
        {"control_id": "C-CON-006", "owner_role": "Complaints Manager"}
    ]
    scenario_count += 1

    _, trace = compose(source_case, exact, None, None)
    assert trace["rule_identity_case_id_collision"] is False
    assert all(rule_id != source_case["case_id"] for rule_id in trace["applied_policy_rules"])
    scenario_count += 1

    complete_with_uncovered = copy.deepcopy(mapping_stage_for("CON-007"))
    complete_with_uncovered["uncovered_obligation_elements"] = ["should not exist"]
    expect_error(
        lambda: compose(assurance_case, None, complete_with_uncovered, evidence),
        "Complete mapping",
    )
    scenario_count += 1

    return scenario_count


def test_all_input_paths() -> int:
    scored_fields = (
        "source_use_disposition",
        "obligation_outcome",
        "applicability_status",
        "assurance_gate",
        "mapping_status",
        "control_mappings",
        "assurance_outcome",
        "gap_types",
        "gap_severity",
        "remediation_action_types",
        "escalation_required",
        "escalation_roles",
        "human_review_required",
        "compliance_conclusion",
    )
    for case_id in sorted(INPUTS):
        case = INPUTS[case_id]
        entered = case["upstream_obligation"]["supplied"] is True and case[
            "upstream_obligation"
        ]["status"] == "approved"
        if entered:
            decision, _ = compose(
                case,
                None,
                mapping_stage_for(case_id),
                evidence_stage_for(case_id),
            )
        else:
            decision, _ = compose(case, source_stage_for(case_id), None, None)
        expected = LABELS[case_id]["expected"]
        for field in scored_fields:
            if decision[field] != expected[field]:
                raise AssertionError(
                    f"{case_id} {field}: expected {expected[field]!r}, found {decision[field]!r}"
                )
    return len(INPUTS)


def main() -> int:
    scenarios = test_selected_boundaries()
    paths = test_all_input_paths()
    print(
        f"evidence_gated_v1_2_offline_tests_passed: {scenarios} boundary scenarios "
        f"and {paths} input-path smoke cases"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
