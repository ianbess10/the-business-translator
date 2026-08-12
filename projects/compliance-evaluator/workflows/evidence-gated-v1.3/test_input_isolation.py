#!/usr/bin/env python3
"""Prove v1.3 payload, runtime, benchmark-identity and result isolation."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from run_regression import RESULTS_DIR, evidence_payload, mapping_payload, resolve_approved_obligation


WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORKFLOW_DIR.parents[1]
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def all_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(key)
            keys.update(all_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(all_keys(item))
    return keys


def main() -> int:
    profile = load_json(PROJECT_DIR / "profiles" / "synthetic-investment-wealth-institution-v1.0.json")
    cases: list[dict[str, Any]] = []
    for name in ("aml-cft.json", "market-conduct.json"):
        cases.extend(load_json(DATASET_DIR / "inputs" / name))
    entered = [
        case for case in cases
        if case["upstream_obligation"]["supplied"] is True
        and case["upstream_obligation"]["status"] == "approved"
    ]
    if len(cases) != 24 or len(entered) != 8:
        raise AssertionError("Frozen input topology changed")

    mapping_forbidden = {
        "presented_evidence", "evidence_or_reporting_requirements", "candidate_statement",
        "assurance_outcome", "gap_claim", "escalation_required", "review_question",
    }
    evidence_forbidden = {
        "proposed_mapping", "relevant_control_catalogue", "candidate_additional_control_ids",
        "gap_claim", "escalation_required",
    }
    for case in entered:
        approved = resolve_approved_obligation(case)
        mapping_input = mapping_payload(case, approved, profile)
        if mapping_forbidden & all_keys(mapping_input):
            raise AssertionError(f"Mapping input leaked a forbidden field: {case['case_id']}")
        current_ids = list(case["proposed_mapping"]["control_ids"])
        mapping_output = {
            "case_id": case["case_id"], "proposal_disposition": "accept",
            "current_mapping_control_ids": current_ids, "candidate_additional_control_ids": [],
            "mapping_completeness": "complete", "uncovered_obligation_elements": [],
            "rationale": "Isolation fixture.",
        }
        evidence_input = evidence_payload(case, approved, mapping_output, profile)
        if evidence_forbidden & all_keys(evidence_input):
            raise AssertionError(f"Evidence input leaked a forbidden field: {case['case_id']}")
        emitted = {item["control_id"] for item in evidence_input["current_control_catalogue"]}
        if emitted != set(current_ids):
            raise AssertionError("Evidence input changed current-control membership")

    runtime_paths = [
        WORKFLOW_DIR / "pipeline.py", WORKFLOW_DIR / "run_regression.py",
        WORKFLOW_DIR / "provider_contract.py", WORKFLOW_DIR / "stage_validation.py",
        *(WORKFLOW_DIR / "prompts").glob("*.md"), *(WORKFLOW_DIR / "schemas").glob("*.json"),
    ]
    case_literal = re.compile(r"(?<![A-Z])(?:AML|CON)-[0-9]{3}(?![0-9])")
    for path in runtime_paths:
        if case_literal.search(path.read_text(encoding="utf-8")):
            raise AssertionError(f"Executable workflow contains benchmark case literal: {path}")
    runner_text = (WORKFLOW_DIR / "run_regression.py").read_text(encoding="utf-8")
    prohibited = ("lab" + "els", "evaluator" + "_only")
    if any(term in runner_text for term in prohibited):
        raise AssertionError("Runner references evaluator-side data")
    plan_text = (WORKFLOW_DIR / "certification" / "plan-v1.3.json").read_text(encoding="utf-8")
    if case_literal.search(plan_text):
        raise AssertionError("Certification plan contains a benchmark identity")
    if RESULTS_DIR.exists():
        raise AssertionError("v1.3 result directory exists before regression")
    print(
        "evidence_gated_v1_3_input_isolation_passed: "
        f"24 input paths, {len(entered)} mapping/evidence payload pairs and {len(runtime_paths)} runtime artefacts"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
