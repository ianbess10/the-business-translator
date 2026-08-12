#!/usr/bin/env python3
"""Prove v1.3 cross-field controls after provider-constrained transport parsing."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

from stage_validation import (
    validate_evidence_stage,
    validate_mapping_stage,
    validate_source_stage,
)


WORKFLOW_DIR = Path(__file__).resolve().parent


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def changed(payload: dict[str, Any], **updates: Any) -> dict[str, Any]:
    result = copy.deepcopy(payload)
    result.update(updates)
    return result


def expect_error(action: Callable[[], None], text: str) -> None:
    try:
        action()
    except ValueError as exc:
        if text not in str(exc):
            raise AssertionError(f"Expected {text!r}; found {exc}") from exc
        return
    raise AssertionError(f"Expected semantic failure containing {text!r}")


SOURCE = {
    "case_id": "CERT-SOURCE-001",
    "proposal_disposition": "accept",
    "source_classification": "binding_candidate",
    "statement_support": "exact_supported",
    "legal_readiness": "human_review_required",
    "applicability_assessment": "applicable",
    "material_missing_fact_types": [],
    "source_conflict_present": False,
    "unsupported_elements": [],
    "rationale": "Generic contract fixture.",
}
MAPPING = {
    "case_id": "CERT-MAPPING-001",
    "proposal_disposition": "accept",
    "current_mapping_control_ids": ["C-CERT-001"],
    "candidate_additional_control_ids": [],
    "mapping_completeness": "complete",
    "uncovered_obligation_elements": [],
    "rationale": "Generic contract fixture.",
}
EVIDENCE = {
    "case_id": "CERT-EVIDENCE-001",
    "evidence_assessment": "sufficient",
    "design_deficiency_evidence_present": False,
    "adverse_indicator_present": False,
    "severity_recommendation": "not_applicable",
    "rationale": "Generic contract fixture.",
}


def main() -> int:
    schemas = {
        "source": load_json(WORKFLOW_DIR / "schemas" / "source-support-stage.schema.json")["schema"],
        "mapping": load_json(WORKFLOW_DIR / "schemas" / "mapping-stage.schema.json")["schema"],
        "evidence": load_json(WORKFLOW_DIR / "schemas" / "evidence-stage.schema.json")["schema"],
    }
    Draft202012Validator(schemas["source"]).validate(SOURCE)
    Draft202012Validator(schemas["mapping"]).validate(MAPPING)
    Draft202012Validator(schemas["evidence"]).validate(EVIDENCE)
    validate_source_stage(SOURCE, SOURCE["case_id"])
    validate_mapping_stage(
        MAPPING,
        MAPPING["case_id"],
        ["C-CERT-001"],
        ["C-CERT-001", "C-CERT-002"],
    )
    validate_evidence_stage(EVIDENCE, EVIDENCE["case_id"])

    source_invalid = [
        (changed(SOURCE, unsupported_elements=["added timing"]), "Exact source support"),
        (changed(SOURCE, statement_support="unsupported_extension"), "requires unsupported elements"),
        (changed(SOURCE, material_missing_fact_types=["other", "other"]), "duplicates"),
        (changed(SOURCE, rationale=" "), "non-empty"),
        (changed(SOURCE, case_id="CERT-SOURCE-OTHER"), "does not match"),
    ]
    for payload, message in source_invalid:
        expect_error(lambda item=payload: validate_source_stage(item, SOURCE["case_id"]), message)

    mapping_invalid = [
        (changed(MAPPING, current_mapping_control_ids=["C-CERT-001", "C-CERT-001"]), "duplicates"),
        (changed(MAPPING, candidate_additional_control_ids=["C-CERT-001"]), "disjoint"),
        (changed(MAPPING, current_mapping_control_ids=["C-CERT-002"]), "subset"),
        (changed(MAPPING, current_mapping_control_ids=[], candidate_additional_control_ids=["C-CERT-001"], mapping_completeness="no_suitable_control", uncovered_obligation_elements=["uncovered"]), "submitted mapping control"),
        (changed(MAPPING, candidate_additional_control_ids=["C-CERT-003"]), "unknown catalogue"),
        (changed(MAPPING, current_mapping_control_ids=[]), "Complete mapping"),
        (changed(MAPPING, uncovered_obligation_elements=["uncovered"]), "Complete mapping"),
        (changed(MAPPING, mapping_completeness="partial"), "Partial mapping"),
        (changed(MAPPING, mapping_completeness="no_suitable_control", uncovered_obligation_elements=["uncovered"]), "No-suitable-control"),
        (changed(MAPPING, rationale=""), "non-empty"),
    ]
    for payload, message in mapping_invalid:
        expect_error(
            lambda item=payload: validate_mapping_stage(
                item,
                MAPPING["case_id"],
                ["C-CERT-001"],
                ["C-CERT-001", "C-CERT-002"],
            ),
            message,
        )

    evidence_invalid = [
        (changed(EVIDENCE, design_deficiency_evidence_present=True, adverse_indicator_present=True, evidence_assessment="design_deficiency", severity_recommendation="high"), "cannot both"),
        (changed(EVIDENCE, evidence_assessment="design_deficiency", severity_recommendation="high"), "must agree"),
        (changed(EVIDENCE, evidence_assessment="adverse_operating_evidence", severity_recommendation="high"), "must agree"),
        (changed(EVIDENCE, severity_recommendation="unassessed"), "not-applicable severity"),
        (changed(EVIDENCE, evidence_assessment="missing_operating_evidence"), "unassessed severity"),
        (changed(EVIDENCE, evidence_assessment="design_deficiency", design_deficiency_evidence_present=True), "assessed severity"),
        (changed(EVIDENCE, rationale=""), "non-empty"),
        (changed(EVIDENCE, case_id="CERT-EVIDENCE-OTHER"), "does not match"),
    ]
    for payload, message in evidence_invalid:
        expect_error(lambda item=payload: validate_evidence_stage(item, EVIDENCE["case_id"]), message)

    semantic_only = [
        ("source", source_invalid[0][0]),
        ("mapping", mapping_invalid[6][0]),
        ("evidence", evidence_invalid[1][0]),
    ]
    for schema_name, payload in semantic_only:
        Draft202012Validator(schemas[schema_name]).validate(payload)

    invalid_count = len(source_invalid) + len(mapping_invalid) + len(evidence_invalid)
    print(
        "evidence_gated_v1_3_semantic_boundary_tests_passed: "
        f"3 valid states, {invalid_count} invalid states and "
        f"{len(semantic_only)} transport-valid semantic rejections"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
