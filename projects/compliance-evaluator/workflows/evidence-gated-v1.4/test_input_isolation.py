#!/usr/bin/env python3
"""Prove v1.4 input, runtime, identity and pre-regression isolation."""

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
    return json.loads(path.read_text())


def keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for name, item in value.items():
            found.add(name)
            found.update(keys(item))
    elif isinstance(value, list):
        for item in value:
            found.update(keys(item))
    return found


def main() -> int:
    profile = load_json(PROJECT_DIR / "profiles" / "synthetic-investment-wealth-institution-v1.0.json")
    cases = []
    for name in ("aml-cft.json", "market-conduct.json"):
        cases.extend(load_json(DATASET_DIR / "inputs" / name))
    entered = [item for item in cases if item["upstream_obligation"]["supplied"] is True and item["upstream_obligation"]["status"] == "approved"]
    if len(cases) != 24 or len(entered) != 8:
        raise AssertionError("Frozen input topology changed")
    mapping_forbidden = {"presented_evidence", "evidence_or_reporting_requirements", "assurance_outcome", "gap_claim", "escalation_required", "review_question"}
    evidence_forbidden = {"proposed_mapping", "relevant_control_catalogue", "candidate_additional_control_ids", "gap_claim", "escalation_required"}
    for case in entered:
        approved = resolve_approved_obligation(case)
        mapping_input = mapping_payload(case, approved, profile)
        if keys(mapping_input) & mapping_forbidden:
            raise AssertionError("Mapping input leaked forbidden evidence or decision data")
        current_ids = list(case["proposed_mapping"]["control_ids"])
        mapping = {"case_id": case["case_id"], "proposal_disposition": "accept", "current_mapping_control_ids": current_ids, "candidate_additional_control_ids": [], "mapping_completeness": "complete", "uncovered_obligation_elements": [], "rationale": "Offline isolation fixture."}
        evidence_input = evidence_payload(case, approved, mapping, profile)
        if keys(evidence_input) & evidence_forbidden:
            raise AssertionError("Evidence input leaked mapping proposal or decision data")
        if {item["control_id"] for item in evidence_input["current_control_catalogue"]} != set(current_ids):
            raise AssertionError("Evidence payload changed current-control membership")
    runtime = [WORKFLOW_DIR / name for name in ("pipeline.py", "run_regression.py", "execution_contract.py", "provider_contract.py", "stage_validation.py")]
    runtime += list((WORKFLOW_DIR / "prompts").glob("*.md")) + list((WORKFLOW_DIR / "schemas").glob("*.json"))
    literal = re.compile(r"(?<![A-Z])(?:AML|CON)-[0-9]{3}(?![0-9])")
    for path in runtime:
        if literal.search(path.read_text()):
            raise AssertionError(f"Runtime contains benchmark identity: {path}")
    runner = (WORKFLOW_DIR / "run_regression.py").read_text()
    if ("lab" + "els") in runner or ("evaluator" + "_only") in runner:
        raise AssertionError("Runner references evaluator-side data")
    if RESULTS_DIR.exists():
        raise AssertionError("v1.4 result directory exists before regression")
    print(f"evidence_gated_v1_4_input_isolation_passed: 24 paths, {len(entered)} assurance payload pairs and {len(runtime)} runtime artefacts")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
