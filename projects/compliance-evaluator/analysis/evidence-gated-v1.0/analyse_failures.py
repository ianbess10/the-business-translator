#!/usr/bin/env python3
"""Build the v1.0 case-level failure register from frozen regression evidence."""

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
RESULTS_DIR = PROJECT_DIR / "results" / "evidence-gated-v1.0"
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
COMPARISON_PATH = RESULTS_DIR / "baseline-comparison.json"
RUN_STATE_PATH = RESULTS_DIR / "run-state.json"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def control_ids(record: dict[str, Any]) -> list[str]:
    return sorted(item["control_id"] for item in record["control_mappings"])


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
    comparison = load_json(COMPARISON_PATH)
    run_state = load_json(RUN_STATE_PATH)
    wrappers = {
        item["input_case_id"]: item for item in predictions_payload["predictions"]
    }
    evaluation_cases = {item["case_id"]: item for item in evaluation["per_case"]}

    case_ids = sorted(labels)
    if set(case_ids) != set(inputs) or set(case_ids) != set(wrappers):
        raise ValueError("Frozen inputs, labels and predictions do not contain the same case IDs")
    if predictions_payload["run_id"] != evaluation["run_id"]:
        raise ValueError("Prediction and evaluation run IDs do not match")
    if predictions_payload.get("run_attempt_count") != 1:
        raise ValueError("Analysis requires the preserved one-attempt v1.0 run")
    if predictions_payload.get("tuning_after_observation") is not False:
        raise ValueError("Analysis requires an untuned preserved run")
    if run_state.get("status") != "completed":
        raise ValueError("The frozen v1.0 run did not complete")
    if run_state.get("completed_case_count") != 24:
        raise ValueError("The frozen v1.0 run must contain 24 completed cases")
    if run_state.get("completed_api_call_count") != 32:
        raise ValueError("The frozen v1.0 run must contain 32 completed API calls")

    failed_case_ids = [
        case_id for case_id in case_ids if not evaluation_cases[case_id]["end_to_end_exact"]
    ]
    root_cause_counts: Counter[str] = Counter()
    mismatch_field_counts: Counter[str] = Counter()
    latent_control_counts: Counter[str] = Counter()
    case_register: list[dict[str, Any]] = []

    for case_id in failed_case_ids:
        case_input = inputs[case_id]
        expected = labels[case_id]["expected"]
        wrapper = wrappers[case_id]
        predicted = wrapper["prediction"]
        source_stage = wrapper["stage_outputs"]["source_obligation"]
        assurance_stage = wrapper["stage_outputs"]["control_evidence"]
        mismatched_fields = evaluation_cases[case_id]["mismatched_fields"]
        mismatch_field_counts.update(mismatched_fields)

        root_causes: list[str] = []
        if predicted["applicability_status"] != expected["applicability_status"]:
            root_causes.append("applicability_dimension_conflation")

        expected_control_ids = control_ids(expected)
        predicted_control_ids = control_ids(predicted)
        if (
            expected["assurance_gate"] == "entered"
            and expected["mapping_status"] == "mapped"
            and predicted["mapping_status"] == "partially_mapped"
            and expected_control_ids == predicted_control_ids
        ):
            root_causes.append("mapping_evidence_dimension_conflation")

        if (
            "partial_coverage" in expected["gap_types"]
            and "control_design" in predicted["gap_types"]
        ):
            root_causes.append("partial_coverage_misclassified_as_design_deficiency")

        for root_cause in root_causes:
            root_cause_counts[root_cause] += 1

        latent_controls: list[str] = []
        if source_stage["source_classification"] != expected["source_use_disposition"]:
            latent_controls.append("source_classification_corrected_by_policy")
            latent_control_counts["source_classification_corrected_by_policy"] += 1
        if predicted["source_use_disposition"] == expected["source_use_disposition"]:
            latent_controls.append("authoritative_source_disposition_protected")
            latent_control_counts["authoritative_source_disposition_protected"] += 1
        if predicted["obligation_outcome"] == expected["obligation_outcome"]:
            latent_controls.append("authoritative_obligation_outcome_protected")
            latent_control_counts["authoritative_obligation_outcome_protected"] += 1

        root_fields: list[str] = []
        if "applicability_dimension_conflation" in root_causes:
            root_fields.append("applicability_status")
        if "mapping_evidence_dimension_conflation" in root_causes:
            root_fields.append("mapping_status")
        if "partial_coverage_misclassified_as_design_deficiency" in root_causes:
            root_fields.append("gap_types")
        cascade_fields = [field for field in mismatched_fields if field not in root_fields]

        if "partial_coverage_misclassified_as_design_deficiency" in root_causes:
            operational_consequence = (
                "A partial mapping became a high design gap, creating the sole unnecessary "
                "management escalation."
            )
        elif "mapping_evidence_dimension_conflation" in root_causes:
            operational_consequence = (
                "A valid control relationship was understated because evidence completeness or "
                "control performance was allowed to change mapping completeness."
            )
        else:
            operational_consequence = (
                "Applicability was changed by source or obligation reasoning even though it is a "
                "separate operating decision."
            )

        case_register.append(
            {
                "case_id": case_id,
                "workstream": labels[case_id]["workstream"],
                "case_stage": wrapper["case_stage"],
                "error_tags": labels[case_id]["error_tags"],
                "mismatched_fields": mismatched_fields,
                "root_causes": root_causes,
                "root_fields": root_fields,
                "cascade_fields": cascade_fields,
                "latent_control_observations": latent_controls,
                "operational_consequence": operational_consequence,
                "expected": {
                    "applicability_status": expected["applicability_status"],
                    "mapping_status": expected["mapping_status"],
                    "control_ids": expected_control_ids,
                    "assurance_outcome": expected["assurance_outcome"],
                    "gap_types": expected["gap_types"],
                    "gap_severity": expected["gap_severity"],
                    "remediation_action_types": expected["remediation_action_types"],
                    "escalation_required": expected["escalation_required"],
                    "escalation_roles": expected["escalation_roles"],
                },
                "observed": {
                    "source_stage_model_classification": source_stage[
                        "source_classification"
                    ],
                    "source_stage_applicability_assessment": source_stage[
                        "applicability_assessment"
                    ],
                    "assurance_stage_mapping_completeness": (
                        assurance_stage["mapping_completeness"]
                        if assurance_stage is not None
                        else None
                    ),
                    "assurance_stage_evidence_assessment": (
                        assurance_stage["evidence_assessment"]
                        if assurance_stage is not None
                        else None
                    ),
                    "applicability_status": predicted["applicability_status"],
                    "mapping_status": predicted["mapping_status"],
                    "control_ids": predicted_control_ids,
                    "assurance_outcome": predicted["assurance_outcome"],
                    "gap_types": predicted["gap_types"],
                    "gap_severity": predicted["gap_severity"],
                    "remediation_action_types": predicted[
                        "remediation_action_types"
                    ],
                    "escalation_required": predicted["escalation_required"],
                    "escalation_roles": predicted["escalation_roles"],
                    "applied_policy_rules": wrapper["policy_trace"][
                        "applied_policy_rules"
                    ],
                },
                "model_rationales": {
                    "source_obligation": source_stage["rationale"],
                    "control_evidence": (
                        assurance_stage["rationale"] if assurance_stage is not None else None
                    ),
                },
            }
        )

    acceptance_gates = comparison["acceptance_gates"]
    failed_release_gates = [
        gate for gate, outcome in acceptance_gates.items() if not outcome["passed"]
    ]
    return {
        "analysis_id": "SA-REG-EVIDENCE-GATED-V1.0-FAILURE-ANALYSIS-001",
        "version": "1.0",
        "analysis_type": "post_regression_case_level_failure_analysis",
        "run_id": predictions_payload["run_id"],
        "dataset_id": predictions_payload["dataset_id"],
        "dataset_version": predictions_payload["dataset_version"],
        "workflow_id": predictions_payload["workflow_id"],
        "workflow_version": predictions_payload["workflow_version"],
        "model": predictions_payload["model_requested"],
        "temperature": predictions_payload["temperature"],
        "synthetic_regression_evidence": True,
        "independent_validation": False,
        "production_performance": False,
        "workflow_v1_modified": False,
        "workflow_v1_rerun": False,
        "post_observation_tuning": False,
        "source_evidence_hashes": {
            "run_state_sha256": sha256_file(RUN_STATE_PATH),
            "predictions_sha256": sha256_file(PREDICTIONS_PATH),
            "evaluation_sha256": sha256_file(EVALUATION_PATH),
            "baseline_comparison_sha256": sha256_file(COMPARISON_PATH),
            "aml_cft_inputs_sha256": sha256_file(INPUT_PATHS[0]),
            "market_conduct_inputs_sha256": sha256_file(INPUT_PATHS[1]),
            "aml_cft_labels_sha256": sha256_file(LABEL_PATHS[0]),
            "market_conduct_labels_sha256": sha256_file(LABEL_PATHS[1]),
        },
        "headline": {
            "case_count": evaluation["case_count"],
            "end_to_end_exact_count": evaluation["end_to_end_exact"]["correct"],
            "failed_case_count": len(failed_case_ids),
            "failed_case_ids": failed_case_ids,
            "failed_field_count": sum(mismatch_field_counts.values()),
            "failed_release_gate_count": len(failed_release_gates),
            "failed_release_gates": failed_release_gates,
        },
        "root_cause_case_counts": dict(sorted(root_cause_counts.items())),
        "mismatch_field_case_counts": dict(sorted(mismatch_field_counts.items())),
        "latent_control_case_counts": dict(sorted(latent_control_counts.items())),
        "preserved_strengths": {
            "source_use_disposition_correct": evaluation["field_metrics"][
                "source_use_disposition"
            ]["correct"],
            "obligation_outcome_correct": evaluation["field_metrics"][
                "obligation_outcome"
            ]["correct"],
            "assurance_gate_correct": evaluation["field_metrics"]["assurance_gate"][
                "correct"
            ],
            "catalogue_owner_routing_correct": evaluation["field_metrics"][
                "control_mappings_with_owner"
            ]["correct"],
            "mandatory_escalations_detected": evaluation["binary_metrics"][
                "escalation_required"
            ]["true_positive"],
            "mandatory_escalations_missed": evaluation["binary_metrics"][
                "escalation_required"
            ]["false_negative"],
            "prohibited_compliance_conclusions": evaluation[
                "prohibited_compliance_conclusion_count"
            ],
        },
        "case_register": case_register,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the committed register matches the frozen v1.0 evidence.",
    )
    args = parser.parse_args()
    analysis = build_analysis()
    rendered = json.dumps(analysis, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not OUTPUT_PATH.exists():
            raise FileNotFoundError(f"Missing committed failure register: {OUTPUT_PATH}")
        if OUTPUT_PATH.read_text(encoding="utf-8") != rendered:
            raise ValueError("Committed failure register does not match frozen v1.0 evidence")
        print("evidence_gated_failure_analysis_check_passed: register matches frozen evidence")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"evidence_gated_failure_analysis_written: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
