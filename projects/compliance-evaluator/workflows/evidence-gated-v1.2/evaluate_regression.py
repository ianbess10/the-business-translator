#!/usr/bin/env python3
"""Score one v1.2 regression against preserved regression evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from pipeline import validate_final_decision


WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORKFLOW_DIR.parents[1]
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"
RESULTS_DIR = PROJECT_DIR / "results" / "evidence-gated-v1.2"
PREDICTIONS_PATH = RESULTS_DIR / "predictions.json"
EVALUATION_PATH = RESULTS_DIR / "evaluation.json"
COMPARISON_PATH = RESULTS_DIR / "regression-comparison.json"
REPORT_PATH = RESULTS_DIR / "README.md"
META_PATH = WORKFLOW_DIR / "workflow-v1.2.meta.json"
BASELINE_EVALUATION_PATH = PROJECT_DIR / "results" / "baseline-v1.0" / "evaluation.json"
V1_EVALUATION_PATH = PROJECT_DIR / "results" / "evidence-gated-v1.0" / "evaluation.json"
V1_1_EVALUATION_PATH = PROJECT_DIR / "results" / "evidence-gated-v1.1" / "evaluation.json"
BASELINE_EVALUATOR_PATH = PROJECT_DIR / "baseline" / "evaluate_baseline.py"
LABEL_PATHS = (
    DATASET_DIR / "labels" / "aml-cft.json",
    DATASET_DIR / "labels" / "market-conduct.json",
)
INPUT_PATHS = (
    DATASET_DIR / "inputs" / "aml-cft.json",
    DATASET_DIR / "inputs" / "market-conduct.json",
)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_evaluator_evidence(meta: dict[str, Any]) -> None:
    mismatches = []
    for hash_group in ("artefact_sha256", "evaluator_only_sha256"):
        for relative_path, expected_hash in meta[hash_group].items():
            artifact_path = PROJECT_DIR / relative_path
            if not artifact_path.exists():
                mismatches.append(f"missing: {relative_path}")
                continue
            actual_hash = sha256_file(artifact_path)
            if actual_hash != expected_hash:
                mismatches.append(
                    f"{relative_path}: expected {expected_hash}, found {actual_hash}"
                )
    if mismatches:
        raise RuntimeError(
            "Frozen evaluator evidence verification failed:\n" + "\n".join(mismatches)
        )


def validate_prediction_contract(payload: dict[str, Any]) -> None:
    final_format = load_json(PROJECT_DIR / "baseline" / "baseline-prediction.schema.json")
    validator = Draft202012Validator(final_format["schema"])
    profile = load_json(
        PROJECT_DIR / "profiles" / "synthetic-investment-wealth-institution-v1.0.json"
    )
    escalation_policy = load_json(
        WORKFLOW_DIR / "policies" / "escalation-policy-v1.2.json"
    )
    for wrapper in payload["predictions"]:
        validator.validate(wrapper["prediction"])
        validate_final_decision(
            wrapper["prediction"],
            profile,
            escalation_policy,
            wrapper["workstream"],
        )


def baseline_evaluator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "frozen_baseline_evaluator", BASELINE_EVALUATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the frozen baseline evaluator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def labels_by_id() -> dict[str, dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for label_path in LABEL_PATHS:
        records.extend(load_json(label_path))
    return {item["case_id"]: item for item in records}


def inputs_by_id() -> dict[str, dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for input_path in INPUT_PATHS:
        records.extend(load_json(input_path))
    return {item["case_id"]: item for item in records}


def runtime_generality_errors() -> list[str]:
    runtime_paths = [
        WORKFLOW_DIR / "pipeline.py",
        WORKFLOW_DIR / "run_regression.py",
        *(WORKFLOW_DIR / "prompts").glob("*.md"),
        *(WORKFLOW_DIR / "policies").glob("*.json"),
        *(WORKFLOW_DIR / "schemas").glob("*.json"),
    ]
    case_literal = re.compile(r"(?<![A-Z])(?:AML|CON)-[0-9]{3}(?![0-9])")
    errors: list[str] = []
    for runtime_path in runtime_paths:
        text = runtime_path.read_text(encoding="utf-8")
        if case_literal.search(text):
            errors.append(str(runtime_path.relative_to(PROJECT_DIR)))
    runner_text = (WORKFLOW_DIR / "run_regression.py").read_text(encoding="utf-8")
    if "labels" in runner_text or "evaluator_only" in runner_text:
        errors.append("runner_evaluator_data_reference")
    return sorted(errors)


def acceptance_gates(
    payload: dict[str, Any], evaluation: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    labels = labels_by_id()
    wrappers = {item["input_case_id"]: item for item in payload["predictions"]}
    predictions = {case_id: item["prediction"] for case_id, item in wrappers.items()}

    not_entered_ids = [
        case_id
        for case_id, label in labels.items()
        if label["expected"]["assurance_gate"] == "not_entered"
    ]
    entered_ids = [
        case_id
        for case_id, label in labels.items()
        if label["expected"]["assurance_gate"] == "entered"
    ]
    closed_state = {
        "mapping_status": "not_applicable",
        "control_mappings": [],
        "assurance_outcome": "not_applicable",
        "gap_types": [],
        "gap_severity": "not_applicable",
        "remediation_action_types": [],
    }
    stage_leak_ids = []
    for case_id in not_entered_ids:
        stages = wrappers[case_id].get("stage_outputs", {})
        if (
            any(
                predictions[case_id][field] != value
                for field, value in closed_state.items()
            )
            or stages.get("mapping") is not None
            or stages.get("evidence") is not None
        ):
            stage_leak_ids.append(case_id)

    source_error_ids = []
    for case_id in not_entered_ids:
        expected = labels[case_id]["expected"]
        stages = wrappers[case_id].get("stage_outputs", {})
        if (
            predictions[case_id]["source_use_disposition"]
            != expected["source_use_disposition"]
            or predictions[case_id]["obligation_outcome"]
            != expected["obligation_outcome"]
            or stages.get("source_support") is None
        ):
            source_error_ids.append(case_id)

    owner_error_ids = []
    for case_id in entered_ids:
        predicted = sorted(
            (item["control_id"], item["owner_role"])
            for item in predictions[case_id]["control_mappings"]
        )
        expected = sorted(
            (item["control_id"], item["owner_role"])
            for item in labels[case_id]["expected"]["control_mappings"]
        )
        mapping_output = wrappers[case_id].get("stage_outputs", {}).get("mapping") or {}
        if (
            predicted != expected
            or sorted(mapping_output.get("current_mapping_control_ids", []))
            != sorted(item[0] for item in expected)
        ):
            owner_error_ids.append(case_id)

    routine_evidence_ids = [
        case_id
        for case_id, label in labels.items()
        if "operating_evidence_missing" in label["error_tags"]
        and label["expected"]["escalation_required"] is False
    ]
    routine_evidence_error_ids = [
        case_id
        for case_id in routine_evidence_ids
        if predictions[case_id]["assurance_outcome"] != "insufficient_evidence"
        or predictions[case_id]["gap_severity"] != "unassessed"
        or predictions[case_id]["remediation_action_types"] != ["evidence_request"]
        or predictions[case_id]["escalation_required"] is not False
    ]

    reconciliation_error_ids = [
        case_id
        for case_id, wrapper in wrappers.items()
        if wrapper.get("reconciliation", {}).get("passed") is not True
        or wrapper.get("reconciliation", {}).get("manual_correction") is not False
    ]
    applicability_error_ids = [
        case_id
        for case_id in labels
        if predictions[case_id]["applicability_status"]
        != labels[case_id]["expected"]["applicability_status"]
    ]
    approved_authority_error_ids = []
    for case_id in entered_ids:
        stages = wrappers[case_id].get("stage_outputs", {})
        trace = wrappers[case_id].get("policy_trace", {})
        if (
            stages.get("source_support") is not None
            or stages.get("approved_obligation_authority") is None
            or stages.get("mapping") is None
            or stages.get("evidence") is None
            or trace.get("approved_obligation_authority_used") is not True
            or trace.get("source_stage_bypassed") is not True
        ):
            approved_authority_error_ids.append(case_id)

    mapping_status_error_ids = [
        case_id
        for case_id in entered_ids
        if predictions[case_id]["mapping_status"]
        != labels[case_id]["expected"]["mapping_status"]
    ]
    assurance_fields = (
        "assurance_outcome",
        "gap_types",
        "gap_severity",
        "remediation_action_types",
    )
    assurance_decision_error_ids = [
        case_id
        for case_id in entered_ids
        if any(
            predictions[case_id][field] != labels[case_id]["expected"][field]
            for field in assurance_fields
        )
    ]
    partial_coverage_ids = [
        case_id
        for case_id, label in labels.items()
        if "partial_coverage" in label["expected"]["gap_types"]
    ]
    partial_coverage_error_ids = [
        case_id
        for case_id in partial_coverage_ids
        if predictions[case_id]["gap_types"] != ["partial_coverage"]
        or predictions[case_id]["gap_severity"] != "medium"
        or predictions[case_id]["escalation_required"] is not False
    ]
    evidence_independence_ids = [
        case_id
        for case_id in entered_ids
        if labels[case_id]["expected"]["mapping_status"] == "mapped"
        and labels[case_id]["expected"]["assurance_outcome"]
        in {"insufficient_evidence", "potential_control_gap"}
    ]
    evidence_independence_error_ids = [
        case_id
        for case_id in evidence_independence_ids
        if predictions[case_id]["mapping_status"] != "mapped"
        or wrappers[case_id]["policy_trace"].get("evidence_stage_can_change_mapping")
        is not False
    ]

    generality_error_ids = []
    for case_id, wrapper in wrappers.items():
        trace = wrapper.get("policy_trace", {})
        rules = trace.get("applied_policy_rules", [])
        if (
            trace.get("case_specific_override") is not False
            or trace.get("rule_identity_case_id_collision") is not False
            or any(rule_id == case_id for rule_id in rules)
            or (
                case_id in entered_ids
                and (
                    trace.get("mapping_stage_received_evidence_status") is not False
                    or trace.get("mapping_stage_received_escalation_proposal") is not False
                    or trace.get("evidence_stage_can_change_mapping") is not False
                )
            )
        ):
            generality_error_ids.append(case_id)
    runtime_errors = runtime_generality_errors()

    escalation = evaluation["binary_metrics"]["escalation_required"]
    return {
        "zero_assurance_stage_leakage": {
            "passed": not stage_leak_ids,
            "expected_case_count": len(not_entered_ids),
            "failure_case_ids": stage_leak_ids,
        },
        "zero_prohibited_compliance_conclusions": {
            "passed": evaluation["prohibited_compliance_conclusion_count"] == 0,
            "count": evaluation["prohibited_compliance_conclusion_count"],
        },
        "exact_source_boundary_and_statement_support": {
            "passed": not source_error_ids,
            "expected_case_count": len(not_entered_ids),
            "failure_case_ids": source_error_ids,
        },
        "exact_current_control_and_catalogue_owner_routing": {
            "passed": not owner_error_ids,
            "expected_case_count": len(entered_ids),
            "failure_case_ids": owner_error_ids,
        },
        "all_mandatory_escalations_detected": {
            "passed": escalation["false_negative"] == 0
            and escalation["true_positive"] == 6,
            "true_positive": escalation["true_positive"],
            "false_negative": escalation["false_negative"],
        },
        "zero_unnecessary_escalations": {
            "passed": escalation["false_positive"] == 0
            and escalation["true_negative"] == 18,
            "true_negative": escalation["true_negative"],
            "false_positive": escalation["false_positive"],
        },
        "routine_missing_evidence_kept_distinct": {
            "passed": not routine_evidence_error_ids,
            "expected_case_count": len(routine_evidence_ids),
            "failure_case_ids": routine_evidence_error_ids,
        },
        "cross_field_reconciliation_without_manual_correction": {
            "passed": not reconciliation_error_ids,
            "expected_case_count": len(wrappers),
            "failure_case_ids": reconciliation_error_ids,
        },
        "exact_applicability_and_approved_authority": {
            "passed": not applicability_error_ids and not approved_authority_error_ids,
            "expected_applicability_case_count": len(labels),
            "expected_approved_authority_case_count": len(entered_ids),
            "applicability_failure_case_ids": applicability_error_ids,
            "approved_authority_failure_case_ids": approved_authority_error_ids,
        },
        "exact_mapping_status_for_entered_assurance": {
            "passed": not mapping_status_error_ids,
            "expected_case_count": len(entered_ids),
            "failure_case_ids": mapping_status_error_ids,
        },
        "exact_entered_assurance_decisions": {
            "passed": not assurance_decision_error_ids,
            "expected_case_count": len(entered_ids),
            "failure_case_ids": assurance_decision_error_ids,
        },
        "partial_coverage_not_promoted_to_design_escalation": {
            "passed": not partial_coverage_error_ids,
            "expected_case_count": len(partial_coverage_ids),
            "failure_case_ids": partial_coverage_error_ids,
        },
        "evidence_condition_does_not_demote_mapping": {
            "passed": not evidence_independence_error_ids,
            "expected_case_count": len(evidence_independence_ids),
            "failure_case_ids": evidence_independence_error_ids,
        },
        "general_policy_identity_and_runtime_isolation": {
            "passed": not generality_error_ids and not runtime_errors,
            "expected_case_count": len(wrappers),
            "failure_case_ids": generality_error_ids,
            "runtime_failure_paths": runtime_errors,
        },
    }


def delta(current: float | None, prior: float | None) -> float | None:
    if current is None or prior is None:
        return None
    return round(current - prior, 4)


def build_comparison(
    evaluation: dict[str, Any],
    baseline: dict[str, Any],
    v1: dict[str, Any],
    v1_1: dict[str, Any],
    gates: dict[str, Any],
) -> dict[str, Any]:
    field_names = (
        "source_use_disposition",
        "obligation_outcome",
        "applicability_status",
        "assurance_gate",
        "mapping_status",
        "control_ids",
        "control_mappings_with_owner",
        "assurance_outcome",
        "gap_types",
        "gap_severity",
        "remediation_action_types",
        "escalation_required",
    )
    fields = {}
    for field in field_names:
        current = evaluation["field_metrics"][field]["accuracy"]
        fields[field] = {
            "simple_baseline_accuracy": baseline["field_metrics"][field]["accuracy"],
            "evidence_gated_v1_0_accuracy": v1["field_metrics"][field]["accuracy"],
            "evidence_gated_v1_1_accuracy": v1_1["field_metrics"][field]["accuracy"],
            "evidence_gated_v1_2_accuracy": current,
            "delta_vs_v1_1": delta(current, v1_1["field_metrics"][field]["accuracy"]),
        }
    return {
        "comparison_id": evaluation["run_id"] + "-regression-comparison",
        "evidence_boundary": "frozen_regression_comparison_not_independent_validation",
        "run_ids": {
            "simple_baseline": baseline["run_id"],
            "evidence_gated_v1_0": v1["run_id"],
            "evidence_gated_v1_1": v1_1["run_id"],
            "evidence_gated_v1_2": evaluation["run_id"],
        },
        "end_to_end_exact": {
            "simple_baseline": baseline["end_to_end_exact"],
            "evidence_gated_v1_0": v1["end_to_end_exact"],
            "evidence_gated_v1_1": v1_1["end_to_end_exact"],
            "evidence_gated_v1_2": evaluation["end_to_end_exact"],
            "accuracy_delta_vs_v1_1": delta(
                evaluation["end_to_end_exact"]["accuracy"],
                v1_1["end_to_end_exact"]["accuracy"],
            ),
        },
        "field_metrics": fields,
        "binary_metrics": evaluation["binary_metrics"],
        "acceptance_gates": gates,
        "all_acceptance_gates_passed": all(item["passed"] for item in gates.values()),
    }


def percent(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def build_report(evaluation: dict[str, Any], comparison: dict[str, Any]) -> str:
    exact = comparison["end_to_end_exact"]
    lines = [
        "# Evidence-Gated Decision Pipeline v1.2 — Regression Results",
        "",
        "> **Evidence boundary:** This is comparison on the same 24 frozen synthetic regression cases used for workflow design. It is not independent validation or production performance.",
        "",
        "## Headline comparison",
        "",
        "| Workflow | Exact | Accuracy |",
        "|---|---:|---:|",
    ]
    for key, label in (
        ("simple_baseline", "Simple baseline"),
        ("evidence_gated_v1_0", "v1.0"),
        ("evidence_gated_v1_1", "v1.1"),
        ("evidence_gated_v1_2", "v1.2"),
    ):
        item = exact[key]
        lines.append(
            f"| {label} | {item['correct']}/{item['total']} | {percent(item['accuracy'])} |"
        )
    lines.extend(["", "## Release gates", "", "| Gate | Result |", "|---|---|"])
    for gate, outcome in comparison["acceptance_gates"].items():
        lines.append(f"| {gate.replace('_', ' ')} | {'PASS' if outcome['passed'] else 'FAIL'} |")
    escalation = evaluation["binary_metrics"]["escalation_required"]
    lines.extend(
        [
            "",
            "## Escalation confusion matrix",
            "",
            "| True positive | False positive | True negative | False negative |",
            "|---:|---:|---:|---:|",
            f"| {escalation['true_positive']} | {escalation['false_positive']} | {escalation['true_negative']} | {escalation['false_negative']} |",
            "",
            "## Interpretation",
            "",
            "This run must be reported exactly as observed. The frozen v1.2 workflow must not be tuned or rerun after these results are seen. Passing every regression gate permits preparation of a separate unseen holdout; it does not establish production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def evidence_fixture(expected: dict[str, Any]) -> dict[str, Any]:
    gaps = set(expected["gap_types"])
    if expected["assurance_outcome"] == "mapped_and_evidenced":
        assessment, design, adverse, severity = "sufficient", False, False, "not_applicable"
    elif expected["assurance_outcome"] == "insufficient_evidence":
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
        "case_id": expected["case_id"],
        "evidence_assessment": assessment,
        "design_deficiency_evidence_present": design,
        "adverse_indicator_present": adverse,
        "severity_recommendation": severity,
        "rationale": "Evaluator self-test fixture.",
    }


def perfect_payload() -> dict[str, Any]:
    labels = labels_by_id()
    inputs = inputs_by_id()
    predictions = []
    for case_id in sorted(labels):
        expected = dict(labels[case_id]["expected"])
        expected["case_id"] = case_id
        entered = expected["assurance_gate"] == "entered"
        current_ids = [item["control_id"] for item in expected["control_mappings"]]
        mapping_status = expected["mapping_status"]
        completeness = {
            "mapped": "complete",
            "partially_mapped": "partial",
            "no_suitable_control_identified": "no_suitable_control",
        }.get(mapping_status)
        if entered:
            mapping_output = {
                "case_id": case_id,
                "proposal_disposition": "accept" if completeness == "complete" else "amend",
                "current_mapping_control_ids": current_ids,
                "candidate_additional_control_ids": [],
                "mapping_completeness": completeness,
                "uncovered_obligation_elements": (
                    [] if completeness == "complete" else ["self-test uncovered element"]
                ),
                "rationale": "Evaluator self-test fixture.",
            }
            evidence_output = evidence_fixture(expected)
            source_output = None
            approved = {"status": "accepted_self_test_authority"}
        else:
            mapping_output = None
            evidence_output = None
            source_output = {
                "case_id": case_id,
                "statement_support": "exact_supported",
                "legal_readiness": "human_review_required",
            }
            approved = None
        predictions.append(
            {
                "input_case_id": case_id,
                "workstream": labels[case_id]["workstream"],
                "case_stage": inputs[case_id]["case_stage"],
                "prediction": expected,
                "stage_outputs": {
                    "source_support": source_output,
                    "mapping": mapping_output,
                    "evidence": evidence_output,
                    "approved_obligation_authority": approved,
                },
                "policy_trace": {
                    "applied_policy_rules": ["SELF-TEST-GENERAL-RULE"],
                    "approved_obligation_authority_used": entered,
                    "source_stage_bypassed": entered,
                    "mapping_stage_received_evidence_status": False,
                    "mapping_stage_received_escalation_proposal": False,
                    "evidence_stage_can_change_mapping": False,
                    "case_specific_override": False,
                    "rule_identity_case_id_collision": False,
                    "reconciliation_passed": True,
                    "human_review_required": True,
                },
                "reconciliation": {"passed": True, "manual_correction": False},
                "api": {"source_support": None, "mapping": None, "evidence": None},
            }
        )
    return {
        "run_id": "evidence-gated-v1.2-self-test",
        "status": "completed",
        "dataset_id": "SA-REG-BASELINE-001",
        "dataset_version": "1.0",
        "workflow_id": "SA-REG-EVIDENCE-GATED-001",
        "workflow_version": "1.2",
        "model_requested": "self-test",
        "temperature": 0,
        "run_attempt_count": 1,
        "api_call_count": 32,
        "source_support_api_call_count": 16,
        "mapping_api_call_count": 8,
        "evidence_api_call_count": 8,
        "tuning_after_observation": False,
        "predictions": predictions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Prove the comparison adapter and all release gates accept exact decisions.",
    )
    args = parser.parse_args()
    meta = load_json(META_PATH)
    verify_evaluator_evidence(meta)
    evaluator = baseline_evaluator()

    if args.self_test:
        payload = perfect_payload()
        validate_prediction_contract(payload)
        evaluation = evaluator.evaluate(payload)
        gates = acceptance_gates(payload, evaluation)
        comparison = build_comparison(
            evaluation,
            load_json(BASELINE_EVALUATION_PATH),
            load_json(V1_EVALUATION_PATH),
            load_json(V1_1_EVALUATION_PATH),
            gates,
        )
        report = build_report(evaluation, comparison)
        if evaluation["end_to_end_exact"]["accuracy"] != 1.0:
            raise AssertionError("Regression evaluator self-test did not score 100%")
        if not all(item["passed"] for item in gates.values()):
            raise AssertionError("At least one release gate rejected exact decisions")
        if "Evidence-Gated Decision Pipeline v1.2" not in report:
            raise AssertionError("Regression comparison report did not render v1.2")
        print(
            f"regression_evaluator_v1_2_self_test_passed: 24/24 exact and "
            f"{len(gates)}/{len(gates)} gates"
        )
        return 0

    if any(path.exists() for path in (EVALUATION_PATH, COMPARISON_PATH, REPORT_PATH)):
        raise RuntimeError("Regression evaluation evidence already exists; refusing to overwrite it")
    payload = load_json(PREDICTIONS_PATH)
    if payload.get("status") != "completed" or payload.get("run_attempt_count") != 1:
        raise RuntimeError("Predictions are not one completed frozen workflow run")
    if payload.get("api_call_count") != 32 or payload.get("tuning_after_observation") is not False:
        raise RuntimeError("Run controls do not match the frozen regression protocol")
    if (
        payload.get("source_support_api_call_count") != 16
        or payload.get("mapping_api_call_count") != 8
        or payload.get("evidence_api_call_count") != 8
    ):
        raise RuntimeError("Stage call counts do not match the frozen regression protocol")
    if payload.get("workflow_meta_sha256") != sha256_file(META_PATH):
        raise RuntimeError("Predictions do not match the frozen workflow metadata")

    validate_prediction_contract(payload)
    evaluation = evaluator.evaluate(payload)
    gates = acceptance_gates(payload, evaluation)
    comparison = build_comparison(
        evaluation,
        load_json(BASELINE_EVALUATION_PATH),
        load_json(V1_EVALUATION_PATH),
        load_json(V1_1_EVALUATION_PATH),
        gates,
    )
    write_json(EVALUATION_PATH, evaluation)
    write_json(COMPARISON_PATH, comparison)
    REPORT_PATH.write_text(build_report(evaluation, comparison), encoding="utf-8")
    print(
        f"Regression evaluation completed: {evaluation['end_to_end_exact']['correct']}/"
        f"{evaluation['case_count']} end-to-end exact; "
        f"release_gates_passed={comparison['all_acceptance_gates_passed']}."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
