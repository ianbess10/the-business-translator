#!/usr/bin/env python3
"""Score one future v1.4 terminal-case record, including quarantines."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORKFLOW_DIR.parents[1]
SOURCE = WORKFLOW_DIR.parent / "evidence-gated-v1.2" / "evaluate_regression.py"
SPEC = importlib.util.spec_from_file_location("retained_v1_2_evaluator", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load the retained evaluator")
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)

RESULTS_DIR = PROJECT_DIR / "results" / "evidence-gated-v1.4"
PREDICTIONS_PATH = RESULTS_DIR / "predictions.json"
EVALUATION_PATH = RESULTS_DIR / "evaluation.json"
COMPARISON_PATH = RESULTS_DIR / "regression-comparison.json"
REPORT_PATH = RESULTS_DIR / "README.md"
META_PATH = WORKFLOW_DIR / "workflow-v1.4.meta.json"


def verify_evaluator_evidence(meta: dict[str, Any]) -> None:
    mismatches = []
    for group in ("artefact_sha256", "evaluator_only_sha256"):
        for relative, expected in meta[group].items():
            path = PROJECT_DIR / relative
            if not path.exists() or BASE.sha256_file(path) != expected:
                mismatches.append(relative)
    if mismatches:
        raise RuntimeError("Frozen evaluator evidence mismatch: " + ", ".join(mismatches))


def score_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    predictions = payload["predictions"]
    quarantines = payload.get("quarantines", [])
    terminal_ids = [item["input_case_id"] for item in predictions + quarantines]
    labels = BASE.labels_by_id()
    if len(terminal_ids) != 24 or len(set(terminal_ids)) != 24 or set(terminal_ids) != set(labels):
        raise RuntimeError("Every frozen case must have one completed or quarantined terminal record")
    if any(item.get("terminal_status") != "quarantined" or item.get("retry_count") != 0 for item in quarantines):
        raise RuntimeError("Invalid quarantine terminal record")
    if predictions:
        BASE.validate_prediction_contract({**payload, "predictions": predictions})

    if not quarantines:
        evaluator = BASE.baseline_evaluator()
        evaluation = evaluator.evaluate(payload)
        gates = BASE.acceptance_gates(payload, evaluation)
        gates["no_quarantined_cases"] = {"passed": True, "quarantine_count": 0, "case_ids": []}
    else:
        evaluator = BASE.baseline_evaluator()
        predicted = {item["input_case_id"]: item["prediction"] for item in predictions}
        completed_ids = sorted(predicted)
        field_metrics = {}
        for field in evaluator.ALL_SCORED_FIELDS:
            correct = sum(evaluator.field_equal(field, predicted[case_id], labels[case_id]["expected"]) for case_id in completed_ids)
            field_metrics[field] = evaluator.rate(correct, len(completed_ids))
        exact_completed = sum(
            all(evaluator.field_equal(field, predicted[case_id], labels[case_id]["expected"]) for field in evaluator.ALL_SCORED_FIELDS)
            for case_id in completed_ids
        )
        escalation = evaluator.binary_confusion(completed_ids, predicted, labels, lambda item: item["escalation_required"] is True)
        evaluation = {
            "evaluation_id": payload["run_id"] + "-evaluation", "run_id": payload["run_id"],
            "dataset_id": payload["dataset_id"], "dataset_version": payload["dataset_version"],
            "case_count": 24, "completed_prediction_count": len(predictions), "quarantine_count": len(quarantines),
            "quarantine_case_ids": sorted(item["input_case_id"] for item in quarantines),
            "end_to_end_exact": evaluator.rate(exact_completed, 24),
            "field_metrics_completed_predictions_only": field_metrics,
            "binary_metrics_completed_predictions_only": {"escalation_required": escalation},
            "metric_denominator_disclosure": "Decision-field and escalation metrics exclude quarantined cases because no decision was generated; end-to-end exactness includes all 24 cases and counts quarantine as incorrect.",
        }
        gates = {
            "no_quarantined_cases": {"passed": False, "quarantine_count": len(quarantines), "case_ids": evaluation["quarantine_case_ids"]},
            "complete_terminal_coverage": {"passed": True, "terminal_case_count": 24},
            "release_blocked_by_quarantine": {"passed": False, "required": True},
        }
    comparison = {
        "comparison_id": payload["run_id"] + "-regression-comparison",
        "evidence_boundary": "frozen_regression_not_independent_validation",
        "workflow_version": "1.4", "end_to_end_exact": evaluation["end_to_end_exact"],
        "quarantine_count": len(quarantines), "acceptance_gates": gates,
        "all_acceptance_gates_passed": all(item["passed"] for item in gates.values()),
    }
    return evaluation, comparison


def report(evaluation: dict[str, Any], comparison: dict[str, Any]) -> str:
    exact = evaluation["end_to_end_exact"]
    return "\n".join([
        "# Evidence-Gated Decision Pipeline v1.4 — Regression Results", "",
        "> Synthetic frozen regression evidence; not independent validation or production performance.", "",
        f"- End-to-end exact: {exact['correct']}/{exact['total']} ({exact['accuracy']})",
        f"- Quarantined cases: {comparison['quarantine_count']}",
        f"- All release gates passed: {comparison['all_acceptance_gates_passed']}", "",
        "Quarantined cases are counted as end-to-end errors and block release. They are not repaired, retried or represented as predictions.", "",
    ])


def perfect_payload() -> dict[str, Any]:
    payload = BASE.perfect_payload()
    payload.update({"run_id": "evidence-gated-v1.4-self-test", "workflow_version": "1.4", "status": "completed", "case_count": 24, "requested_api_call_count": 32, "retry_count": 0, "quarantines": []})
    for item in payload["predictions"]:
        item["terminal_status"] = "completed"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    meta = BASE.load_json(META_PATH)
    verify_evaluator_evidence(meta)
    if args.self_test:
        perfect = perfect_payload()
        evaluation, comparison = score_payload(perfect)
        if evaluation["end_to_end_exact"]["correct"] != 24 or not comparison["all_acceptance_gates_passed"]:
            raise AssertionError("Perfect terminal record failed evaluator self-test")
        quarantined = json.loads(json.dumps(perfect))
        removed = quarantined["predictions"].pop()
        quarantined["status"] = "completed_with_quarantine"
        quarantined["quarantines"] = [{
            "input_case_id": removed["input_case_id"], "workstream": removed["workstream"], "case_stage": removed["case_stage"],
            "terminal_status": "quarantined", "failed_stage": "evidence", "failure_type": "semantic_failure",
            "error": "offline fixture", "retry_count": 0, "policy_composition_performed": False, "mandatory_human_review": True,
        }]
        q_evaluation, q_comparison = score_payload(quarantined)
        if q_evaluation["end_to_end_exact"]["total"] != 24 or q_comparison["all_acceptance_gates_passed"]:
            raise AssertionError("Quarantine-aware evaluator did not block release")
        print("regression_evaluator_v1_4_self_test_passed: 24/24 perfect and one quarantine counted as error with release blocked")
        return 0
    if any(path.exists() for path in (EVALUATION_PATH, COMPARISON_PATH, REPORT_PATH)):
        raise RuntimeError("v1.4 evaluation evidence already exists; refusing to overwrite")
    payload = BASE.load_json(PREDICTIONS_PATH)
    if payload.get("run_attempt_count") != 1 or payload.get("retry_count") != 0 or payload.get("tuning_after_observation") is not False:
        raise RuntimeError("Run controls do not match the frozen v1.4 protocol")
    if payload.get("workflow_meta_sha256") != BASE.sha256_file(META_PATH):
        raise RuntimeError("Predictions do not match frozen v1.4 metadata")
    evaluation, comparison = score_payload(payload)
    BASE.write_json(EVALUATION_PATH, evaluation)
    BASE.write_json(COMPARISON_PATH, comparison)
    REPORT_PATH.write_text(report(evaluation, comparison), encoding="utf-8")
    print(f"v1.4 evaluation completed once: exact={evaluation['end_to_end_exact']['correct']}/24 quarantines={comparison['quarantine_count']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
