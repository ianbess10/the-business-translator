#!/usr/bin/env python3
"""Build a reproducible operational failure register from frozen baseline evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ANALYSIS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = ANALYSIS_DIR.parents[1]
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"
RESULTS_DIR = PROJECT_DIR / "results" / "baseline-v1.0"
OUTPUT_PATH = ANALYSIS_DIR / "failure-analysis.json"

INPUT_PATHS = (
    DATASET_DIR / "inputs" / "aml-cft.json",
    DATASET_DIR / "inputs" / "market-conduct.json",
)
LABEL_PATHS = (
    DATASET_DIR / "labels" / "aml-cft.json",
    DATASET_DIR / "labels" / "market-conduct.json",
)
PREDICTIONS_PATH = RESULTS_DIR / "predictions.json"
EVALUATION_PATH = RESULTS_DIR / "evaluation.json"

PROPOSAL_FIELDS = (
    "source_use_disposition",
    "obligation_outcome",
    "applicability_status",
    "assurance_outcome",
    "escalation_required",
)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_mappings(record: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple(
        sorted((item["control_id"], item["owner_role"]) for item in record["control_mappings"])
    )


def control_ids(record: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(item["control_id"] for item in record["control_mappings"]))


def stage_gate_leaked(predicted: dict[str, Any], expected: dict[str, Any]) -> bool:
    if expected["assurance_gate"] != "not_entered":
        return False
    return any(
        (
            predicted["mapping_status"] != "not_applicable",
            bool(predicted["control_mappings"]),
            predicted["assurance_outcome"] != "not_applicable",
            bool(predicted["gap_types"]),
            predicted["gap_severity"] != "not_applicable",
            bool(predicted["remediation_action_types"]),
        )
    )


def proposal_anchor_fields(
    case_input: dict[str, Any], predicted: dict[str, Any], expected: dict[str, Any]
) -> list[str]:
    anchored: list[str] = []
    proposal = case_input["proposal_under_test"]
    for field in PROPOSAL_FIELDS:
        proposed_value = proposal.get(field)
        if proposed_value is None or proposed_value == expected[field]:
            continue
        if predicted[field] == proposed_value:
            anchored.append(field)
    return anchored


def build_analysis() -> dict[str, Any]:
    inputs_list: list[dict[str, Any]] = []
    labels_list: list[dict[str, Any]] = []
    for path in INPUT_PATHS:
        inputs_list.extend(load_json(path))
    for path in LABEL_PATHS:
        labels_list.extend(load_json(path))

    inputs = {item["case_id"]: item for item in inputs_list}
    labels = {item["case_id"]: item for item in labels_list}
    predictions_payload = load_json(PREDICTIONS_PATH)
    evaluation = load_json(EVALUATION_PATH)
    prediction_wrappers = {
        item["input_case_id"]: item for item in predictions_payload["predictions"]
    }
    predictions = {
        case_id: wrapper["prediction"] for case_id, wrapper in prediction_wrappers.items()
    }

    case_ids = sorted(labels)
    if set(case_ids) != set(inputs) or set(case_ids) != set(predictions):
        raise ValueError("Frozen inputs, labels and predictions do not contain the same case IDs")
    if predictions_payload["run_id"] != evaluation["run_id"]:
        raise ValueError("Prediction and evaluation run IDs do not match")
    if predictions_payload.get("run_attempt_count") != 1:
        raise ValueError("Failure analysis requires the preserved one-run baseline evidence")

    evaluation_cases = {item["case_id"]: item for item in evaluation["per_case"]}
    case_register: list[dict[str, Any]] = []
    category_counts: Counter[str] = Counter()
    proposal_challenges: Counter[str] = Counter()
    proposal_anchors: Counter[str] = Counter()
    owner_challenge_count = 0
    owner_anchor_count = 0

    for case_id in case_ids:
        case_input = inputs[case_id]
        label = labels[case_id]
        expected = label["expected"]
        predicted = predictions[case_id]
        entered = expected["assurance_gate"] == "entered"

        anchored_fields = proposal_anchor_fields(case_input, predicted, expected)
        for field in PROPOSAL_FIELDS:
            proposed_value = case_input["proposal_under_test"].get(field)
            if proposed_value is not None and proposed_value != expected[field]:
                proposal_challenges[field] += 1
        for field in anchored_fields:
            proposal_anchors[field] += 1

        expected_owners = sorted({item["owner_role"] for item in expected["control_mappings"]})
        predicted_owners = sorted({item["owner_role"] for item in predicted["control_mappings"]})
        proposed_owner = case_input["proposed_mapping"]["owner_role"]
        owner_anchored = False
        if proposed_owner is not None and expected_owners != [proposed_owner]:
            owner_challenge_count += 1
            owner_anchored = predicted_owners == [proposed_owner]
            owner_anchor_count += int(owner_anchored)

        flags: list[str] = []
        if (
            predicted["source_use_disposition"] != expected["source_use_disposition"]
            or predicted["obligation_outcome"] != expected["obligation_outcome"]
        ):
            flags.append("source_or_obligation_decision_error")
        if predicted["applicability_status"] != expected["applicability_status"]:
            flags.append("applicability_decision_error")
        if stage_gate_leaked(predicted, expected):
            flags.append("assurance_stage_gate_leakage")
        if entered and control_ids(predicted) != control_ids(expected):
            flags.append("control_selection_error")
        if entered and canonical_mappings(predicted) != canonical_mappings(expected):
            flags.append("owner_routing_error")
        if entered and any(
            predicted[field] != expected[field]
            for field in (
                "mapping_status",
                "assurance_outcome",
                "gap_types",
                "gap_severity",
                "remediation_action_types",
            )
        ):
            flags.append("evidence_gap_or_severity_error")
        if predicted["escalation_required"] != expected["escalation_required"]:
            flags.append("escalation_decision_error")
        if anchored_fields or owner_anchored:
            flags.append("proposal_anchoring")

        for flag in flags:
            category_counts[flag] += 1

        case_register.append(
            {
                "case_id": case_id,
                "workstream": label["workstream"],
                "case_stage": prediction_wrappers[case_id]["case_stage"],
                "end_to_end_exact": evaluation_cases[case_id]["end_to_end_exact"],
                "mismatched_fields": evaluation_cases[case_id]["mismatched_fields"],
                "failure_flags": flags,
                "proposal_anchor_fields": anchored_fields,
                "proposed_owner_anchor": owner_anchored,
                "expected": {
                    "source_use_disposition": expected["source_use_disposition"],
                    "obligation_outcome": expected["obligation_outcome"],
                    "applicability_status": expected["applicability_status"],
                    "assurance_gate": expected["assurance_gate"],
                    "mapping_status": expected["mapping_status"],
                    "control_mappings": expected["control_mappings"],
                    "assurance_outcome": expected["assurance_outcome"],
                    "gap_types": expected["gap_types"],
                    "gap_severity": expected["gap_severity"],
                    "remediation_action_types": expected["remediation_action_types"],
                    "escalation_required": expected["escalation_required"],
                    "escalation_roles": expected["escalation_roles"],
                },
                "predicted": {
                    "source_use_disposition": predicted["source_use_disposition"],
                    "obligation_outcome": predicted["obligation_outcome"],
                    "applicability_status": predicted["applicability_status"],
                    "assurance_gate": predicted["assurance_gate"],
                    "mapping_status": predicted["mapping_status"],
                    "control_mappings": predicted["control_mappings"],
                    "assurance_outcome": predicted["assurance_outcome"],
                    "gap_types": predicted["gap_types"],
                    "gap_severity": predicted["gap_severity"],
                    "remediation_action_types": predicted["remediation_action_types"],
                    "escalation_required": predicted["escalation_required"],
                    "escalation_roles": predicted["escalation_roles"],
                },
                "model_rationale": predicted["rationale"],
            }
        )

    not_entered_ids = [
        case_id for case_id in case_ids if labels[case_id]["expected"]["assurance_gate"] == "not_entered"
    ]
    entered_ids = [case_id for case_id in case_ids if case_id not in not_entered_ids]
    escalation_challenge_ids = [
        case_id
        for case_id in case_ids
        if inputs[case_id]["proposal_under_test"]["escalation_required"]
        != labels[case_id]["expected"]["escalation_required"]
    ]
    escalation_anchor_ids = [
        case_id
        for case_id in escalation_challenge_ids
        if predictions[case_id]["escalation_required"]
        == inputs[case_id]["proposal_under_test"]["escalation_required"]
    ]

    return {
        "analysis_id": "SA-REG-BASELINE-FAILURE-ANALYSIS-001",
        "version": "1.0",
        "analysis_type": "post_baseline_operational_failure_analysis",
        "run_id": predictions_payload["run_id"],
        "dataset_id": predictions_payload["dataset_id"],
        "dataset_version": predictions_payload["dataset_version"],
        "model": predictions_payload["model_requested"],
        "temperature": predictions_payload["temperature"],
        "synthetic_benchmark_evidence": True,
        "production_performance": False,
        "baseline_prompt_modified": False,
        "baseline_rerun": False,
        "source_evidence_hashes": {
            "predictions_sha256": sha256_file(PREDICTIONS_PATH),
            "evaluation_sha256": sha256_file(EVALUATION_PATH),
            "aml_cft_inputs_sha256": sha256_file(INPUT_PATHS[0]),
            "market_conduct_inputs_sha256": sha256_file(INPUT_PATHS[1]),
            "aml_cft_labels_sha256": sha256_file(LABEL_PATHS[0]),
            "market_conduct_labels_sha256": sha256_file(LABEL_PATHS[1]),
        },
        "headline": {
            "case_count": len(case_ids),
            "end_to_end_exact_count": sum(
                item["end_to_end_exact"] for item in evaluation["per_case"]
            ),
            "failed_case_count": sum(
                not item["end_to_end_exact"] for item in evaluation["per_case"]
            ),
            "not_entered_case_count": len(not_entered_ids),
            "entered_case_count": len(entered_ids),
            "not_entered_cases_with_stage_leakage": sum(
                stage_gate_leaked(predictions[case_id], labels[case_id]["expected"])
                for case_id in not_entered_ids
            ),
            "escalation_challenge_case_count": len(escalation_challenge_ids),
            "escalation_proposal_anchor_count": len(escalation_anchor_ids),
        },
        "failure_category_case_counts": dict(sorted(category_counts.items())),
        "proposal_anchoring": {
            "field_challenge_counts": dict(sorted(proposal_challenges.items())),
            "field_anchor_counts": dict(sorted(proposal_anchors.items())),
            "owner_challenge_count": owner_challenge_count,
            "owner_anchor_count": owner_anchor_count,
            "escalation_challenge_case_ids": escalation_challenge_ids,
            "escalation_anchor_case_ids": escalation_anchor_ids,
        },
        "case_register": case_register,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the committed failure register matches a fresh analysis of frozen evidence.",
    )
    args = parser.parse_args()
    analysis = build_analysis()
    rendered = json.dumps(analysis, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not OUTPUT_PATH.exists():
            raise FileNotFoundError(f"Missing committed failure register: {OUTPUT_PATH}")
        if OUTPUT_PATH.read_text(encoding="utf-8") != rendered:
            raise ValueError("Committed failure register does not match frozen evidence")
        print("failure_analysis_check_passed: committed register matches frozen evidence")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"failure_analysis_written: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
