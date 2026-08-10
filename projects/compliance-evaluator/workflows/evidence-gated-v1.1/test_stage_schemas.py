#!/usr/bin/env python3
"""Offline structured-output schema tests for v1.1; no API calls or labels."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


WORKFLOW_DIR = Path(__file__).resolve().parent


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


SOURCE_SCHEMA = load_json(
    WORKFLOW_DIR / "schemas" / "source-obligation-stage.schema.json"
)["schema"]
CONTROL_SCHEMA = load_json(
    WORKFLOW_DIR / "schemas" / "control-evidence-stage.schema.json"
)["schema"]


def expect_invalid(validator: Draft202012Validator, payload: dict[str, Any]) -> None:
    try:
        validator.validate(payload)
        raise AssertionError("Expected schema validation failure")
    except ValidationError:
        pass


def source_example() -> dict[str, Any]:
    return {
        "case_id": "AML-900",
        "proposal_disposition": "reject",
        "source_classification": "guidance_only",
        "obligation_support": "guidance_context",
        "applicability_assessment": "applicable",
        "material_missing_fact_types": [],
        "source_conflict_present": False,
        "rationale": "Guidance is relevant but does not become a binding obligation.",
    }


def control_example() -> dict[str, Any]:
    return {
        "case_id": "CON-900",
        "proposal_disposition": "reject",
        "mapping_completeness": "complete",
        "supported_control_ids": ["C-CON-006"],
        "coverage_gap_present": False,
        "evidence_assessment": "sufficient",
        "design_deficiency_evidence_present": False,
        "adverse_indicator_present": False,
        "severity_recommendation": "not_applicable",
        "rationale": "Coverage and evidence were assessed independently.",
    }


def run_tests() -> None:
    source_validator = Draft202012Validator(SOURCE_SCHEMA)
    control_validator = Draft202012Validator(CONTROL_SCHEMA)

    valid_sources = []
    for classification, support, applicability in (
        ("guidance_only", "guidance_context", "applicable"),
        ("final_change_event", "final_pending", "uncertain"),
        ("blocked", "blocked", "not_assessed"),
    ):
        item = source_example()
        item["source_classification"] = classification
        item["obligation_support"] = support
        item["applicability_assessment"] = applicability
        valid_sources.append(item)
    for item in valid_sources:
        source_validator.validate(item)

    invalid_sources = []
    item = source_example()
    item.pop("applicability_assessment")
    invalid_sources.append(item)
    item = source_example()
    item["applicability_assessment"] = "binding"
    invalid_sources.append(item)
    item = source_example()
    item["unexpected"] = True
    invalid_sources.append(item)
    item = source_example()
    item["case_id"] = "CASE-900"
    invalid_sources.append(item)
    for item in invalid_sources:
        expect_invalid(source_validator, item)

    valid_controls = []
    for mapping, coverage_gap, evidence, design_gap, adverse in (
        ("complete", False, "sufficient", False, False),
        ("complete", False, "missing_operating_evidence", False, False),
        ("complete", False, "adverse_operating_evidence", False, True),
        ("partial", True, "design_deficiency", True, False),
        ("partial", True, "design_deficiency", False, False),
    ):
        item = control_example()
        item["mapping_completeness"] = mapping
        item["coverage_gap_present"] = coverage_gap
        item["evidence_assessment"] = evidence
        item["design_deficiency_evidence_present"] = design_gap
        item["adverse_indicator_present"] = adverse
        valid_controls.append(item)
    for item in valid_controls:
        control_validator.validate(item)

    invalid_controls = []
    for missing_field in (
        "coverage_gap_present",
        "design_deficiency_evidence_present",
    ):
        item = control_example()
        item.pop(missing_field)
        invalid_controls.append(item)
    item = control_example()
    item["coverage_gap_present"] = "false"
    invalid_controls.append(item)
    item = control_example()
    item["design_deficiency_evidence_present"] = 0
    invalid_controls.append(item)
    item = control_example()
    item["unexpected"] = True
    invalid_controls.append(item)
    item = control_example()
    item["mapping_completeness"] = "evidence_missing"
    invalid_controls.append(item)
    item = control_example()
    item["evidence_assessment"] = "partial_coverage"
    invalid_controls.append(item)
    item = control_example()
    item["supported_control_ids"] = ["UNKNOWN"]
    invalid_controls.append(item)
    for item in invalid_controls:
        expect_invalid(control_validator, item)

    print(
        "evidence_gated_v1_1_schema_tests_passed: "
        f"{len(valid_sources)} source-valid, {len(invalid_sources)} source-invalid, "
        f"{len(valid_controls)} control-valid and {len(invalid_controls)} control-invalid"
    )


if __name__ == "__main__":
    run_tests()
