#!/usr/bin/env python3
"""Score one future v1.3 regression using the retained 14-gate evaluator."""

from __future__ import annotations

import importlib.util
import copy
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

BASE.RESULTS_DIR = PROJECT_DIR / "results" / "evidence-gated-v1.3"
BASE.PREDICTIONS_PATH = BASE.RESULTS_DIR / "predictions.json"
BASE.EVALUATION_PATH = BASE.RESULTS_DIR / "evaluation.json"
BASE.COMPARISON_PATH = BASE.RESULTS_DIR / "regression-comparison.json"
BASE.REPORT_PATH = BASE.RESULTS_DIR / "README.md"
BASE.META_PATH = WORKFLOW_DIR / "workflow-v1.3.meta.json"
ORIGINAL_BUILD_COMPARISON = BASE.build_comparison
ORIGINAL_BUILD_REPORT = BASE.build_report
ORIGINAL_PERFECT_PAYLOAD = BASE.perfect_payload


def build_comparison(
    evaluation: dict[str, Any], baseline: dict[str, Any], v1: dict[str, Any],
    v1_1: dict[str, Any], gates: dict[str, Any],
) -> dict[str, Any]:
    comparison = ORIGINAL_BUILD_COMPARISON(evaluation, baseline, v1, v1_1, gates)
    comparison["run_ids"]["evidence_gated_v1_3"] = comparison["run_ids"].pop("evidence_gated_v1_2")
    comparison["end_to_end_exact"]["evidence_gated_v1_3"] = comparison["end_to_end_exact"].pop("evidence_gated_v1_2")
    for metrics in comparison["field_metrics"].values():
        metrics["evidence_gated_v1_3_accuracy"] = metrics.pop("evidence_gated_v1_2_accuracy")
    return comparison


def build_report(evaluation: dict[str, Any], comparison: dict[str, Any]) -> str:
    compatible = copy.deepcopy(comparison)
    compatible["end_to_end_exact"]["evidence_gated_v1_2"] = compatible["end_to_end_exact"]["evidence_gated_v1_3"]
    report = ORIGINAL_BUILD_REPORT(evaluation, compatible).replace("v1.2", "v1.3")
    return report + "\nEvaluator lineage: Evidence-Gated Decision Pipeline v1.2 release gates retained.\n"


def perfect_payload() -> dict[str, Any]:
    payload = ORIGINAL_PERFECT_PAYLOAD()
    payload["run_id"] = "evidence-gated-v1.3-self-test"
    payload["workflow_version"] = "1.3"
    return payload


BASE.build_comparison = build_comparison
BASE.build_report = build_report
BASE.perfect_payload = perfect_payload


def main() -> int:
    return BASE.main()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
