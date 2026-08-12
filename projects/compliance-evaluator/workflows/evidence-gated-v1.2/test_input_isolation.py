#!/usr/bin/env python3
"""Prove v1.2 stage-input, runtime and identity isolation without API calls."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from run_regression import (
    RESULTS_DIR,
    evidence_payload,
    mapping_payload,
    resolve_approved_obligation,
)


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


def rule_ids(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "rule_id":
                found.append(item)
            else:
                found.extend(rule_ids(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(rule_ids(item))
    return found


def main() -> int:
    profile = load_json(
        PROJECT_DIR / "profiles" / "synthetic-investment-wealth-institution-v1.0.json"
    )
    cases: list[dict[str, Any]] = []
    for name in ("aml-cft.json", "market-conduct.json"):
        cases.extend(load_json(DATASET_DIR / "inputs" / name))
    entered = [
        case
        for case in cases
        if case["upstream_obligation"]["supplied"] is True
        and case["upstream_obligation"]["status"] == "approved"
    ]
    if len(entered) != 8:
        raise AssertionError(f"Expected eight entered assurance cases; found {len(entered)}")

    mapping_forbidden = {
        "presented_evidence",
        "evidence_or_reporting_requirements",
        "proposal_under_test",
        "candidate_statement",
        "assurance_outcome",
        "gap_claim",
        "escalation_required",
        "review_question",
    }
    evidence_forbidden = {
        "proposed_mapping",
        "relevant_control_catalogue",
        "candidate_additional_control_ids",
        "proposal_under_test",
        "gap_claim",
        "escalation_required",
    }

    for case in entered:
        approved = resolve_approved_obligation(case)
        mapping_input = mapping_payload(case, approved, profile)
        mapping_overlap = mapping_forbidden & all_keys(mapping_input)
        if mapping_overlap:
            raise AssertionError(
                f"Mapping input leaked forbidden fields for {case['case_id']}: {mapping_overlap}"
            )
        expected_mapping_keys = {
            "case_id",
            "approved_obligation",
            "proposed_mapping",
            "relevant_control_catalogue",
        }
        if set(mapping_input) != expected_mapping_keys:
            raise AssertionError("Mapping input topology changed")

        current_ids = list(case["proposed_mapping"]["control_ids"])
        synthetic_mapping = {
            "case_id": case["case_id"],
            "proposal_disposition": "accept",
            "current_mapping_control_ids": current_ids,
            "candidate_additional_control_ids": [],
            "mapping_completeness": "complete",
            "uncovered_obligation_elements": [],
            "rationale": "Isolation test fixture.",
        }
        evidence_input = evidence_payload(
            case, approved, synthetic_mapping, profile
        )
        evidence_overlap = evidence_forbidden & all_keys(evidence_input)
        if evidence_overlap:
            raise AssertionError(
                f"Evidence input leaked forbidden fields for {case['case_id']}: {evidence_overlap}"
            )
        if set(evidence_input) != {
            "case_id",
            "approved_obligation",
            "validated_current_mapping",
            "current_control_catalogue",
            "institution_facts",
            "missing_facts",
            "presented_evidence",
            "review_question",
        }:
            raise AssertionError("Evidence input topology changed")
        emitted_ids = {
            item["control_id"] for item in evidence_input["current_control_catalogue"]
        }
        if emitted_ids != set(current_ids):
            raise AssertionError("Evidence input catalogue changed current mapping membership")

    runtime_paths = [
        WORKFLOW_DIR / "pipeline.py",
        WORKFLOW_DIR / "run_regression.py",
        *(WORKFLOW_DIR / "prompts").glob("*.md"),
        *(WORKFLOW_DIR / "policies").glob("*.json"),
        *(WORKFLOW_DIR / "schemas").glob("*.json"),
    ]
    case_literal = re.compile(r"(?<![A-Z])(?:AML|CON)-[0-9]{3}(?![0-9])")
    for runtime_path in runtime_paths:
        text = runtime_path.read_text(encoding="utf-8")
        if case_literal.search(text):
            raise AssertionError(
                f"Executable workflow contains benchmark case literal: {runtime_path}"
            )
    runner_text = (WORKFLOW_DIR / "run_regression.py").read_text(encoding="utf-8")
    for prohibited_term in ("labels", "evaluator_only"):
        if prohibited_term in runner_text:
            raise AssertionError(f"Runner contains prohibited term: {prohibited_term}")

    policy_rule_ids: list[str] = []
    for policy_path in (WORKFLOW_DIR / "policies").glob("*.json"):
        policy_rule_ids.extend(rule_ids(load_json(policy_path)))
    if len(policy_rule_ids) != len(set(policy_rule_ids)):
        raise AssertionError("Policy rule IDs must be unique")
    if any(case_literal.search(rule_id) for rule_id in policy_rule_ids):
        raise AssertionError("Policy rule ID resembles a benchmark case ID")
    if RESULTS_DIR.exists():
        raise AssertionError("v1.2 result directory exists before regression")

    print(
        "evidence_gated_v1_2_input_isolation_passed: "
        f"{len(entered)} mapping payloads, {len(entered)} evidence payloads, "
        f"{len(runtime_paths)} runtime artefacts and {len(policy_rule_ids)} rule identities"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
