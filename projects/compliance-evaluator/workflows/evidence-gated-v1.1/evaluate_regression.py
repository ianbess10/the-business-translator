#!/usr/bin/env python3
"""Score one v1.1 regression against the preserved baseline and v1.0 evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from pipeline import validate_final_decision


WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORKFLOW_DIR.parents[1]
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"
RESULTS_DIR = PROJECT_DIR / "results" / "evidence-gated-v1.1"
PREDICTIONS_PATH = RESULTS_DIR / "predictions.json"
EVALUATION_PATH = RESULTS_DIR / "evaluation.json"
COMPARISON_PATH = RESULTS_DIR / "regression-comparison.json"
REPORT_PATH = RESULTS_DIR / "README.md"
META_PATH = WORKFLOW_DIR / "workflow-v1.1.meta.json"
BASELINE_EVALUATION_PATH = PROJECT_DIR / "results" / "baseline-v1.0" / "evaluation.json"
V1_EVALUATION_PATH = PROJECT_DIR / "results" / "evidence-gated-v1.0" / "evaluation.json"
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
            path = PROJECT_DIR / relative_path
            actual_hash = sha256_file(path)
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
        WORKFLOW_DIR / "policies" / "escalation-policy-v1.1.json"
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
    labels: list[dict[str, Any]] = []
    for path in LABEL_PATHS:
        labels.extend(load_json(path))
    return {item["case_id"]: item for item in labels}


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
    closed_state = {
        "mapping_status": "not_applicable",
        "control_mappings": [],
        "assurance_outcome": "not_applicable",
        "gap_types": [],
        "gap_severity": "not_applicable",
        "remediation_action_types": [],
    }
    stage_leak_ids = [
        case_id
        for case_id in not_entered_ids
        if any(predictions[case_id][field] != value for field, value in closed_state.items())
    ]

    boundary_values = {"draft_watchlist", "historical_only", "strategy_context", "blocked"}
    boundary_ids = [
        case_id
        for case_id, label in labels.items()
        if label["expected"]["source_use_disposition"] in boundary_values
    ]
    boundary_error_ids = [
        case_id
        for case_id in boundary_ids
        if predictions[case_id]["source_use_disposition"]
        != labels[case_id]["expected"]["source_use_disposition"]
        or predictions[case_id]["obligation_outcome"]
        != labels[case_id]["expected"]["obligation_outcome"]
    ]

    entered_ids = [
        case_id
        for case_id, label in labels.items()
        if label["expected"]["assurance_gate"] == "entered"
    ]
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
        if predicted != expected:
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
        wrapper = wrappers[case_id]
        stages = wrapper.get("stage_outputs", {})
        trace = wrapper.get("policy_trace", {})
        if (
            stages.get("source_obligation") is not None
            or stages.get("approved_obligation_authority") is None
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
    ]

    case_specific_rule_error_ids = []
    for case_id, wrapper in wrappers.items():
        trace = wrapper.get("policy_trace", {})
        applied_rules = trace.get("applied_policy_rules", [])
        if trace.get("case_specific_override") is not False or any(
            case_id in str(rule) for rule in applied_rules
        ):
            case_specific_rule_error_ids.append(case_id)

    escalation = evaluation["binary_metrics"]["escalation_required"]
    gates = {
        "zero_assurance_stage_leakage": {
            "passed": not stage_leak_ids,
            "expected_case_count": len(not_entered_ids),
            "failure_case_ids": stage_leak_ids,
        },
        "zero_prohibited_compliance_conclusions": {
            "passed": evaluation["prohibited_compliance_conclusion_count"] == 0,
            "count": evaluation["prohibited_compliance_conclusion_count"],
        },
        "exact_source_boundary_treatment": {
            "passed": not boundary_error_ids,
            "expected_case_count": len(boundary_ids),
            "failure_case_ids": boundary_error_ids,
        },
        "exact_catalogue_owner_routing": {
            "passed": not owner_error_ids,
            "expected_case_count": len(entered_ids),
            "failure_case_ids": owner_error_ids,
        },
        "all_mandatory_escalations_detected": {
            "passed": escalation["false_negative"] == 0 and escalation["true_positive"] == 6,
            "true_positive": escalation["true_positive"],
            "false_negative": escalation["false_negative"],
        },
        "zero_unnecessary_escalations": {
            "passed": escalation["false_positive"] == 0 and escalation["true_negative"] == 18,
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
        "general_policy_rules_without_case_overrides": {
            "passed": not case_specific_rule_error_ids,
            "expected_case_count": len(wrappers),
            "failure_case_ids": case_specific_rule_error_ids,
        },
    }
    return gates


def delta(current: float | None, baseline: float | None) -> float | None:
    if current is None or baseline is None:
        return None
    return round(current - baseline, 4)


def build_comparison(
    evaluation: dict[str, Any],
    baseline: dict[str, Any],
    v1_evaluation: dict[str, Any],
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
        current_accuracy = evaluation["field_metrics"][field]["accuracy"]
        baseline_accuracy = baseline["field_metrics"][field]["accuracy"]
        v1_accuracy = v1_evaluation["field_metrics"][field]["accuracy"]
        fields[field] = {
            "simple_baseline_accuracy": baseline_accuracy,
            "evidence_gated_v1_0_accuracy": v1_accuracy,
            "evidence_gated_v1_1_accuracy": current_accuracy,
            "delta_vs_simple_baseline": delta(current_accuracy, baseline_accuracy),
            "delta_vs_v1_0": delta(current_accuracy, v1_accuracy),
        }
    binary = {}
    for metric in ("potential_control_gap", "insufficient_evidence", "escalation_required"):
        binary[metric] = {}
        for measure in ("precision", "recall", "accuracy"):
            current_value = evaluation["binary_metrics"][metric][measure]
            baseline_value = baseline["binary_metrics"][metric][measure]
            v1_value = v1_evaluation["binary_metrics"][metric][measure]
            binary[metric][measure] = {
                "simple_baseline": baseline_value,
                "evidence_gated_v1_0": v1_value,
                "evidence_gated_v1_1": current_value,
                "delta_vs_simple_baseline": delta(current_value, baseline_value),
                "delta_vs_v1_0": delta(current_value, v1_value),
            }
    return {
        "comparison_id": evaluation["run_id"] + "-regression-comparison",
        "evidence_boundary": "frozen_regression_comparison_not_independent_validation",
        "simple_baseline_run_id": baseline["run_id"],
        "evidence_gated_v1_0_run_id": v1_evaluation["run_id"],
        "evidence_gated_v1_1_run_id": evaluation["run_id"],
        "end_to_end_exact": {
            "simple_baseline": baseline["end_to_end_exact"],
            "evidence_gated_v1_0": v1_evaluation["end_to_end_exact"],
            "evidence_gated_v1_1": evaluation["end_to_end_exact"],
            "accuracy_delta_vs_simple_baseline": delta(
                evaluation["end_to_end_exact"]["accuracy"],
                baseline["end_to_end_exact"]["accuracy"],
            ),
            "accuracy_delta_vs_v1_0": delta(
                evaluation["end_to_end_exact"]["accuracy"],
                v1_evaluation["end_to_end_exact"]["accuracy"],
            ),
        },
        "field_metrics": fields,
        "binary_metrics": binary,
        "acceptance_gates": gates,
        "all_acceptance_gates_passed": all(item["passed"] for item in gates.values()),
    }


def percent(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def build_report(evaluation: dict[str, Any], comparison: dict[str, Any]) -> str:
    baseline = comparison["end_to_end_exact"]["simple_baseline"]
    v1 = comparison["end_to_end_exact"]["evidence_gated_v1_0"]
    current = comparison["end_to_end_exact"]["evidence_gated_v1_1"]
    lines = [
        "# Evidence-Gated Decision Pipeline v1.1 — Regression Results",
        "",
        "> **Evidence boundary:** This is comparison on the same 24 frozen synthetic regression cases used for workflow design. It is not independent validation or production performance.",
        "",
        "## Headline comparison",
        "",
        "| Measure | Simple baseline | v1.0 | v1.1 | v1.1 vs v1.0 |",
        "|---|---:|---:|---:|---:|",
        f"| End-to-end exact | {percent(baseline['accuracy'])} | {percent(v1['accuracy'])} | {percent(current['accuracy'])} | {percent(comparison['end_to_end_exact']['accuracy_delta_vs_v1_0'])} |",
    ]
    for field, label in (
        ("source_use_disposition", "Source-use disposition"),
        ("obligation_outcome", "Obligation outcome"),
        ("applicability_status", "Applicability status"),
        ("control_mappings_with_owner", "Control and owner mapping"),
        ("assurance_outcome", "Assurance outcome"),
        ("escalation_required", "Escalation decision"),
    ):
        metric = comparison["field_metrics"][field]
        lines.append(
            f"| {label} | {percent(metric['simple_baseline_accuracy'])} | "
            f"{percent(metric['evidence_gated_v1_0_accuracy'])} | "
            f"{percent(metric['evidence_gated_v1_1_accuracy'])} | "
            f"{percent(metric['delta_vs_v1_0'])} |"
        )

    lines.extend(
        [
            "",
            "## Release gates",
            "",
            "| Gate | Result |",
            "|---|---|",
        ]
    )
    for name, result in comparison["acceptance_gates"].items():
        lines.append(f"| {name.replace('_', ' ')} | {'PASS' if result['passed'] else 'FAIL'} |")

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
            "This run must be reported exactly as observed. The frozen v1.1 workflow must not be tuned or rerun after these results are seen. Passing every regression gate permits preparation of a separate unseen holdout; it does not establish production readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def perfect_payload() -> dict[str, Any]:
    labels = labels_by_id()
    inputs: list[dict[str, Any]] = []
    for path in INPUT_PATHS:
        inputs.extend(load_json(path))
    inputs_by_id = {item["case_id"]: item for item in inputs}
    predictions = []
    for case_id, label in sorted(labels.items()):
        prediction = dict(label["expected"])
        prediction["case_id"] = case_id
        entered = prediction["assurance_gate"] == "entered"
        predictions.append(
            {
                "input_case_id": case_id,
                "workstream": label["workstream"],
                "case_stage": inputs_by_id[case_id]["case_stage"],
                "prediction": prediction,
                "stage_outputs": {
                    "source_obligation": None if entered else {"self_test": True},
                    "control_evidence": {"self_test": True} if entered else None,
                    "approved_obligation_authority": (
                        {"self_test": True} if entered else None
                    ),
                },
                "policy_trace": {
                    "approved_obligation_authority_used": entered,
                    "source_stage_bypassed": entered,
                    "case_specific_override": False,
                    "applied_policy_rules": ["SELF-TEST-GENERAL-RULE"],
                },
                "reconciliation": {"passed": True, "manual_correction": False},
            }
        )
    return {
        "run_id": "evidence-gated-v1.1-self-test",
        "status": "completed",
        "dataset_id": "SA-REG-BASELINE-001",
        "dataset_version": "1.0",
        "workflow_id": "SA-REG-EVIDENCE-GATED-001",
        "workflow_version": "1.1",
        "model_requested": "self-test",
        "temperature": 0,
        "run_attempt_count": 1,
        "api_call_count": 24,
        "tuning_after_observation": False,
        "predictions": predictions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Prove the comparison adapter and all release gates accept exact labels.",
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
            gates,
        )
        report = build_report(evaluation, comparison)
        if evaluation["end_to_end_exact"]["accuracy"] != 1.0:
            raise AssertionError("Regression evaluator self-test did not score 100%")
        if not all(item["passed"] for item in gates.values()):
            raise AssertionError("At least one release gate rejected exact predictions")
        if "Evidence-Gated Decision Pipeline v1.1" not in report:
            raise AssertionError("Regression comparison report did not render v1.1")
        print(
            f"regression_evaluator_v1_1_self_test_passed: 24/24 exact and "
            f"{len(gates)}/{len(gates)} gates"
        )
        return 0

    if any(path.exists() for path in (EVALUATION_PATH, COMPARISON_PATH, REPORT_PATH)):
        raise RuntimeError("Regression evaluation evidence already exists; refusing to overwrite it")
    payload = load_json(PREDICTIONS_PATH)
    if payload.get("status") != "completed" or payload.get("run_attempt_count") != 1:
        raise RuntimeError("Predictions are not one completed frozen workflow run")
    if payload.get("api_call_count") != 24 or payload.get("tuning_after_observation") is not False:
        raise RuntimeError("Run controls do not match the frozen regression protocol")
    if payload.get("workflow_meta_sha256") != sha256_file(META_PATH):
        raise RuntimeError("Predictions do not match the current frozen workflow metadata")

    validate_prediction_contract(payload)
    evaluation = evaluator.evaluate(payload)
    baseline = load_json(BASELINE_EVALUATION_PATH)
    v1_evaluation = load_json(V1_EVALUATION_PATH)
    gates = acceptance_gates(payload, evaluation)
    comparison = build_comparison(evaluation, baseline, v1_evaluation, gates)
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
