#!/usr/bin/env python3
"""Offline structured-output contract tests for all v1.2 model stages."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


WORKFLOW_DIR = Path(__file__).resolve().parent


def load_schema(name: str) -> dict[str, Any]:
    with (WORKFLOW_DIR / "schemas" / name).open(encoding="utf-8") as handle:
        return json.load(handle)["schema"]


def expect_valid(validator: Draft202012Validator, payloads: list[dict[str, Any]]) -> None:
    for payload in payloads:
        validator.validate(payload)


def expect_invalid(validator: Draft202012Validator, payloads: list[dict[str, Any]]) -> None:
    for payload in payloads:
        if not list(validator.iter_errors(payload)):
            raise AssertionError(f"Schema unexpectedly accepted invalid payload: {payload}")


def main() -> int:
    source_validator = Draft202012Validator(
        load_schema("source-support-stage.schema.json")
    )
    mapping_validator = Draft202012Validator(load_schema("mapping-stage.schema.json"))
    evidence_validator = Draft202012Validator(load_schema("evidence-stage.schema.json"))

    source_base = {
        "case_id": "AML-001",
        "proposal_disposition": "accept",
        "source_classification": "binding_candidate",
        "statement_support": "exact_supported",
        "legal_readiness": "human_review_required",
        "applicability_assessment": "applicable",
        "material_missing_fact_types": [],
        "source_conflict_present": False,
        "unsupported_elements": [],
        "rationale": "The wording is supported while approval remains pending.",
    }
    source_valid = [source_base]
    for support in ("partially_supported", "unsupported_extension"):
        item = copy.deepcopy(source_base)
        item["statement_support"] = support
        item["proposal_disposition"] = "amend" if support == "partially_supported" else "reject"
        item["unsupported_elements"] = ["unsupported frequency"]
        source_valid.append(item)
    conflict = copy.deepcopy(source_base)
    conflict.update(
        {
            "source_classification": "source_conflict",
            "statement_support": "not_assessable",
            "legal_readiness": "source_conflict",
            "applicability_assessment": "not_assessed",
            "source_conflict_present": True,
        }
    )
    source_valid.append(conflict)

    source_invalid = []
    item = copy.deepcopy(source_base)
    item["unexpected"] = True
    source_invalid.append(item)
    item = copy.deepcopy(source_base)
    item["unsupported_elements"] = ["should be empty"]
    source_invalid.append(item)
    item = copy.deepcopy(source_base)
    item["statement_support"] = "unsupported_extension"
    source_invalid.append(item)
    item = copy.deepcopy(source_base)
    item["legal_readiness"] = "ready"
    source_invalid.append(item)
    item = copy.deepcopy(source_base)
    del item["statement_support"]
    source_invalid.append(item)
    item = copy.deepcopy(source_base)
    item["case_id"] = "CASE-1"
    source_invalid.append(item)

    mapping_complete = {
        "case_id": "CON-005",
        "proposal_disposition": "accept",
        "current_mapping_control_ids": ["C-CON-006"],
        "candidate_additional_control_ids": [],
        "mapping_completeness": "complete",
        "uncovered_obligation_elements": [],
        "rationale": "The submitted current control covers the assessed scope.",
    }
    mapping_partial = copy.deepcopy(mapping_complete)
    mapping_partial.update(
        {
            "proposal_disposition": "amend",
            "candidate_additional_control_ids": ["C-CON-007"],
            "mapping_completeness": "partial",
            "uncovered_obligation_elements": ["customer outcomes oversight"],
        }
    )
    mapping_none = copy.deepcopy(mapping_complete)
    mapping_none.update(
        {
            "proposal_disposition": "reject",
            "current_mapping_control_ids": [],
            "mapping_completeness": "no_suitable_control",
            "uncovered_obligation_elements": ["entire obligation"],
        }
    )
    mapping_valid = [mapping_complete, mapping_partial, mapping_none]

    mapping_invalid = []
    item = copy.deepcopy(mapping_complete)
    item["evidence_assessment"] = "sufficient"
    mapping_invalid.append(item)
    item = copy.deepcopy(mapping_complete)
    item["uncovered_obligation_elements"] = ["unexpected gap"]
    mapping_invalid.append(item)
    item = copy.deepcopy(mapping_complete)
    item["current_mapping_control_ids"] = []
    mapping_invalid.append(item)
    item = copy.deepcopy(mapping_partial)
    item["uncovered_obligation_elements"] = []
    mapping_invalid.append(item)
    item = copy.deepcopy(mapping_partial)
    item["current_mapping_control_ids"] = []
    mapping_invalid.append(item)
    item = copy.deepcopy(mapping_none)
    item["current_mapping_control_ids"] = ["C-CON-006"]
    mapping_invalid.append(item)
    item = copy.deepcopy(mapping_none)
    item["uncovered_obligation_elements"] = []
    mapping_invalid.append(item)
    item = copy.deepcopy(mapping_complete)
    item["current_mapping_control_ids"] = ["C-CON-006", "C-CON-006"]
    mapping_invalid.append(item)

    evidence_valid = []
    for assessment, design, adverse, severity in (
        ("sufficient", False, False, "not_applicable"),
        ("missing_operating_evidence", False, False, "unassessed"),
        ("design_deficiency", True, False, "high"),
        ("adverse_operating_evidence", False, True, "high"),
        ("insufficient_to_assess", False, False, "unassessed"),
        ("not_assessed_no_current_control", False, False, "unassessed"),
    ):
        evidence_valid.append(
            {
                "case_id": "CON-005",
                "evidence_assessment": assessment,
                "design_deficiency_evidence_present": design,
                "adverse_indicator_present": adverse,
                "severity_recommendation": severity,
                "rationale": "Evidence condition assessed independently from mapping.",
            }
        )

    evidence_invalid = []
    item = copy.deepcopy(evidence_valid[0])
    item["mapping_completeness"] = "complete"
    evidence_invalid.append(item)
    item = copy.deepcopy(evidence_valid[0])
    item["evidence_assessment"] = "missing_mapping"
    evidence_invalid.append(item)
    item = copy.deepcopy(evidence_valid[0])
    del item["rationale"]
    evidence_invalid.append(item)
    item = copy.deepcopy(evidence_valid[0])
    item["case_id"] = "CONDUCT-5"
    evidence_invalid.append(item)
    item = copy.deepcopy(evidence_valid[0])
    del item["adverse_indicator_present"]
    evidence_invalid.append(item)

    expect_valid(source_validator, source_valid)
    expect_invalid(source_validator, source_invalid)
    expect_valid(mapping_validator, mapping_valid)
    expect_invalid(mapping_validator, mapping_invalid)
    expect_valid(evidence_validator, evidence_valid)
    expect_invalid(evidence_validator, evidence_invalid)
    print(
        "evidence_gated_v1_2_schema_tests_passed: "
        f"{len(source_valid)} source-valid, {len(source_invalid)} source-invalid, "
        f"{len(mapping_valid)} mapping-valid, {len(mapping_invalid)} mapping-invalid, "
        f"{len(evidence_valid)} evidence-valid and {len(evidence_invalid)} evidence-invalid"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
