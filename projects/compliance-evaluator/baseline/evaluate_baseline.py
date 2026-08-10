#!/usr/bin/env python3
"""Deterministically score baseline predictions against frozen labels."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator


BASELINE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASELINE_DIR.parent
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"
RESULTS_DIR = PROJECT_DIR / "results" / "baseline-v1.0"
PREDICTIONS_PATH = RESULTS_DIR / "predictions.json"
EVALUATION_PATH = RESULTS_DIR / "evaluation.json"
REPORT_PATH = RESULTS_DIR / "README.md"
LABEL_PATHS = (
    DATASET_DIR / "labels" / "aml-cft.json",
    DATASET_DIR / "labels" / "market-conduct.json",
)
INPUT_PATHS = (
    DATASET_DIR / "inputs" / "aml-cft.json",
    DATASET_DIR / "inputs" / "market-conduct.json",
)

SCALAR_FIELDS = (
    "source_use_disposition",
    "obligation_outcome",
    "applicability_status",
    "assurance_gate",
    "mapping_status",
    "assurance_outcome",
    "gap_severity",
    "escalation_required",
    "human_review_required",
    "compliance_conclusion",
)
SET_FIELDS = ("gap_types", "remediation_action_types", "escalation_roles")
ALL_SCORED_FIELDS = SCALAR_FIELDS + (
    "control_ids",
    "control_mappings_with_owner",
) + SET_FIELDS


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_set(values: list[str]) -> tuple[str, ...]:
    return tuple(sorted(values))


def control_ids(record: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(item["control_id"] for item in record["control_mappings"]))


def control_mappings(record: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((item["control_id"], item["owner_role"]) for item in record["control_mappings"]))


def field_equal(field: str, predicted: dict[str, Any], expected: dict[str, Any]) -> bool:
    if field == "control_ids":
        return control_ids(predicted) == control_ids(expected)
    if field == "control_mappings_with_owner":
        return control_mappings(predicted) == control_mappings(expected)
    if field in SET_FIELDS:
        return canonical_set(predicted[field]) == canonical_set(expected[field])
    return predicted[field] == expected[field]


def rate(correct: int, total: int) -> dict[str, int | float | None]:
    return {
        "correct": correct,
        "total": total,
        "accuracy": round(correct / total, 4) if total else None,
    }


def binary_confusion(
    case_ids: list[str],
    predictions: dict[str, dict[str, Any]],
    labels: dict[str, dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
) -> dict[str, int | float | None]:
    tp = fp = tn = fn = 0
    for case_id in case_ids:
        predicted_positive = predicate(predictions[case_id])
        expected_positive = predicate(labels[case_id]["expected"])
        if predicted_positive and expected_positive:
            tp += 1
        elif predicted_positive and not expected_positive:
            fp += 1
        elif not predicted_positive and expected_positive:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    accuracy = (tp + tn) / len(case_ids) if case_ids else None
    return {
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
        "precision": round(precision, 4) if precision is not None else None,
        "recall": round(recall, 4) if recall is not None else None,
        "accuracy": round(accuracy, 4) if accuracy is not None else None,
    }


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    label_records: list[dict[str, Any]] = []
    for path in LABEL_PATHS:
        label_records.extend(load_json(path))
    labels = {item["case_id"]: item for item in label_records}

    prediction_records = payload["predictions"]
    predictions = {item["input_case_id"]: item["prediction"] for item in prediction_records}
    if len(predictions) != len(prediction_records):
        raise ValueError("Duplicate input_case_id in predictions")
    if set(predictions) != set(labels):
        missing = sorted(set(labels) - set(predictions))
        extra = sorted(set(predictions) - set(labels))
        raise ValueError(f"Prediction/label case mismatch; missing={missing}, extra={extra}")

    case_ids = sorted(labels)
    field_metrics: dict[str, dict[str, int | float | None]] = {}
    for field in ALL_SCORED_FIELDS:
        correct = sum(
            field_equal(field, predictions[case_id], labels[case_id]["expected"])
            for case_id in case_ids
        )
        field_metrics[field] = rate(correct, len(case_ids))

    entered_ids = [
        case_id for case_id in case_ids if labels[case_id]["expected"]["assurance_gate"] == "entered"
    ]
    entered_metrics = {
        field: rate(
            sum(
                field_equal(field, predictions[case_id], labels[case_id]["expected"])
                for case_id in entered_ids
            ),
            len(entered_ids),
        )
        for field in (
            "mapping_status",
            "control_ids",
            "control_mappings_with_owner",
            "assurance_outcome",
            "gap_types",
            "gap_severity",
            "remediation_action_types",
        )
    }

    per_case: list[dict[str, Any]] = []
    end_to_end_correct = 0
    echo_correct = 0
    for case_id in case_ids:
        mismatches = [
            field
            for field in ALL_SCORED_FIELDS
            if not field_equal(field, predictions[case_id], labels[case_id]["expected"])
        ]
        exact = not mismatches
        end_to_end_correct += int(exact)
        echo = predictions[case_id]["case_id"] == case_id
        echo_correct += int(echo)
        wrapper = next(item for item in prediction_records if item["input_case_id"] == case_id)
        per_case.append(
            {
                "case_id": case_id,
                "workstream": labels[case_id]["workstream"],
                "case_stage": wrapper["case_stage"],
                "error_tags": labels[case_id]["error_tags"],
                "end_to_end_exact": exact,
                "case_id_echo_correct": echo,
                "mismatched_fields": mismatches,
            }
        )

    tag_cases: dict[str, list[str]] = defaultdict(list)
    for record in label_records:
        for tag in record["error_tags"]:
            tag_cases[tag].append(record["case_id"])
    error_tag_slices = {
        tag: rate(
            sum(
                all(
                    field_equal(field, predictions[case_id], labels[case_id]["expected"])
                    for field in ALL_SCORED_FIELDS
                )
                for case_id in ids
            ),
            len(ids),
        )
        for tag, ids in sorted(tag_cases.items())
    }

    workstream_slices = {}
    for workstream in ("aml_cft", "market_conduct"):
        ids = [case_id for case_id in case_ids if labels[case_id]["workstream"] == workstream]
        correct = sum(
            all(
                field_equal(field, predictions[case_id], labels[case_id]["expected"])
                for field in ALL_SCORED_FIELDS
            )
            for case_id in ids
        )
        workstream_slices[workstream] = rate(correct, len(ids))

    prohibited_conclusions = sum(
        predictions[case_id]["compliance_conclusion"] != "not_determined" for case_id in case_ids
    )
    return {
        "evaluation_id": payload["run_id"] + "-evaluation",
        "evaluated_at": utc_now(),
        "run_id": payload["run_id"],
        "dataset_id": payload["dataset_id"],
        "dataset_version": payload["dataset_version"],
        "model": payload["model_requested"],
        "temperature": payload["temperature"],
        "synthetic_benchmark_evidence": True,
        "production_performance": False,
        "case_count": len(case_ids),
        "scoring_note": "Rationale wording is retained as evidence but excluded from exact-match scoring.",
        "case_id_echo": rate(echo_correct, len(case_ids)),
        "end_to_end_exact": rate(end_to_end_correct, len(case_ids)),
        "field_metrics": field_metrics,
        "entered_assurance_metrics": entered_metrics,
        "binary_metrics": {
            "potential_control_gap": binary_confusion(
                case_ids,
                predictions,
                labels,
                lambda item: item["assurance_outcome"] == "potential_control_gap",
            ),
            "insufficient_evidence": binary_confusion(
                case_ids,
                predictions,
                labels,
                lambda item: item["assurance_outcome"] == "insufficient_evidence",
            ),
            "escalation_required": binary_confusion(
                case_ids,
                predictions,
                labels,
                lambda item: item["escalation_required"],
            ),
        },
        "prohibited_compliance_conclusion_count": prohibited_conclusions,
        "workstream_slices": workstream_slices,
        "error_tag_slices": error_tag_slices,
        "per_case": per_case,
    }


def percent(metric: dict[str, Any], key: str = "accuracy") -> str:
    value = metric.get(key)
    return "n/a" if value is None else f"{value * 100:.1f}%"


def build_report(evaluation: dict[str, Any]) -> str:
    field = evaluation["field_metrics"]
    entered = evaluation["entered_assurance_metrics"]
    binary = evaluation["binary_metrics"]
    failed_cases = [item for item in evaluation["per_case"] if not item["end_to_end_exact"]]

    lines = [
        "# Simple Baseline v1.0 — Synthetic Benchmark Results",
        "",
        "> **Evidence boundary:** These are results from 24 frozen synthetic cases. They are not production performance, legal advice or a compliance conclusion.",
        "",
        "## Run control",
        "",
        f"- Run ID: `{evaluation['run_id']}`",
        f"- Model snapshot: `{evaluation['model']}`",
        f"- Temperature: `{evaluation['temperature']}`",
        "- Run attempts: one",
        "- Prompt tuning after observation: none",
        "- Scoring: deterministic exact comparison; rationale wording excluded",
        "",
        "## Headline results",
        "",
        "| Measure | Result |",
        "|---|---:|",
        f"| End-to-end exact disposition | {percent(evaluation['end_to_end_exact'])} ({evaluation['end_to_end_exact']['correct']}/{evaluation['case_count']}) |",
        f"| Source-use disposition | {percent(field['source_use_disposition'])} |",
        f"| Obligation outcome | {percent(field['obligation_outcome'])} |",
        f"| Applicability status | {percent(field['applicability_status'])} |",
        f"| Approved-obligation gate | {percent(field['assurance_gate'])} |",
        f"| Control mapping on entered cases | {percent(entered['control_ids'])} |",
        f"| Owner routing on entered cases | {percent(entered['control_mappings_with_owner'])} |",
        f"| Evidence/gap outcome on entered cases | {percent(entered['assurance_outcome'])} |",
        f"| Escalation precision | {percent(binary['escalation_required'], 'precision')} |",
        f"| Escalation recall | {percent(binary['escalation_required'], 'recall')} |",
        f"| Potential-gap precision | {percent(binary['potential_control_gap'], 'precision')} |",
        f"| Potential-gap recall | {percent(binary['potential_control_gap'], 'recall')} |",
        f"| Prohibited compliance conclusions | {evaluation['prohibited_compliance_conclusion_count']} |",
        "",
        "## Escalation confusion matrix",
        "",
        "| True positive | False positive | True negative | False negative |",
        "|---:|---:|---:|---:|",
        "| {true_positive} | {false_positive} | {true_negative} | {false_negative} |".format(
            **binary["escalation_required"]
        ),
        "",
        "## Cases requiring failure analysis",
        "",
    ]
    if failed_cases:
        lines.extend(
            [
                "| Case | Workstream | Mismatched decision fields |",
                "|---|---|---|",
            ]
        )
        for item in failed_cases:
            lines.append(
                f"| `{item['case_id']}` | {item['workstream']} | {', '.join(item['mismatched_fields'])} |"
            )
    else:
        lines.append("No end-to-end mismatches were observed.")

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "This is the deliberately simple, pre-engineering baseline. Its errors are preserved for failure analysis. No prompt changes or reruns were made after results were observed.",
            "",
            "The next controlled step is to examine the recorded failures by source boundary, obligation decision, applicability, control mapping, evidence, ownership and escalation—then design one traceable workflow intervention against the same frozen regression set.",
            "",
        ]
    )
    return "\n".join(lines)


def build_perfect_payload() -> dict[str, Any]:
    inputs: list[dict[str, Any]] = []
    labels: list[dict[str, Any]] = []
    for path in INPUT_PATHS:
        inputs.extend(load_json(path))
    for path in LABEL_PATHS:
        labels.extend(load_json(path))
    stages = {item["case_id"]: item["case_stage"] for item in inputs}
    predictions = []
    for label in labels:
        prediction = dict(label["expected"])
        prediction["case_id"] = label["case_id"]
        predictions.append(
            {
                "input_case_id": label["case_id"],
                "workstream": label["workstream"],
                "case_stage": stages[label["case_id"]],
                "prediction": prediction,
            }
        )
    return {
        "run_id": "self-test",
        "dataset_id": "SA-REG-BASELINE-001",
        "dataset_version": "1.0",
        "model_requested": "self-test",
        "temperature": 0,
        "predictions": predictions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Prove the scorer reaches 100% on labels-as-predictions.")
    args = parser.parse_args()

    if args.self_test:
        result = evaluate(build_perfect_payload())
        if result["end_to_end_exact"]["accuracy"] != 1.0:
            raise AssertionError("Evaluator self-test failed")
        print("Evaluator self-test passed: 24/24 exact labels score 100%.")
        return 0

    if EVALUATION_PATH.exists() or REPORT_PATH.exists():
        raise RuntimeError("Evaluation evidence already exists; refusing to overwrite it")

    payload = load_json(PREDICTIONS_PATH)
    if payload.get("status") != "completed" or payload.get("run_attempt_count") != 1:
        raise RuntimeError("Predictions do not represent one completed frozen baseline run")

    response_format = load_json(BASELINE_DIR / "baseline-prediction.schema.json")
    validator = Draft202012Validator(response_format["schema"])
    for item in payload["predictions"]:
        validator.validate(item["prediction"])

    evaluation = evaluate(payload)
    write_json(EVALUATION_PATH, evaluation)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_report(evaluation), encoding="utf-8")
    print(
        f"Evaluation completed: {evaluation['end_to_end_exact']['correct']}/"
        f"{evaluation['case_count']} end-to-end exact."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
