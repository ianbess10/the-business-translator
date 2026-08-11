"""Approved rulebook integrity, deterministic mapping and assurance derivation."""

from __future__ import annotations

from typing import Any


def validate_rulebook(rulebook: dict[str, Any], catalogue_ids: set[str]) -> None:
    if rulebook.get("status") != "approved" or rulebook.get("human_review", {}).get("status") != "accepted":
        raise ValueError("Rulebook requires accepted human approval")
    elements = [x["element_id"] for x in rulebook["obligation_elements"]]
    if len(elements) != len(set(elements)) or not elements:
        raise ValueError("Obligation element IDs must be unique and non-empty")
    expected = set(elements)
    coverage = rulebook["control_coverage_assertions"]
    controls = {x["control_id"] for x in coverage}
    if not controls <= catalogue_ids:
        raise ValueError("Rulebook contains an unknown control")
    for control in controls:
        if {x["element_id"] for x in coverage if x["control_id"] == control} != expected:
            raise ValueError("Every relevant control requires an assertion for every element")
    requirements = [x["requirement_id"] for x in rulebook["evidence_requirements"]]
    if len(requirements) != len(set(requirements)):
        raise ValueError("Evidence requirement IDs must be unique")
    if rulebook.get("generality_controls") != {"benchmark_case_ids_permitted": False, "benchmark_evidence_ids_permitted": False, "evaluator_labels_used": False, "case_specific_exceptions_permitted": False}:
        raise ValueError("Rulebook generality controls are not closed")


def derive_mapping(case_id: str, submitted_ids: list[str], rulebook: dict[str, Any], catalogue_ids: set[str]) -> dict[str, Any]:
    validate_rulebook(rulebook, catalogue_ids)
    submitted = set(submitted_ids)
    if not submitted or not submitted <= catalogue_ids:
        raise ValueError("Submitted mapping contains no valid current control")
    assertions = rulebook["control_coverage_assertions"]
    known = {x["control_id"] for x in assertions}
    if not submitted <= known:
        raise ValueError("Submitted control lacks approved coverage authority")
    required = {x["element_id"] for x in rulebook["obligation_elements"] if x["mandatory"]}
    covered = {x["element_id"] for x in assertions if x["control_id"] in submitted and x["coverage_state"] == "covers"}
    missing = sorted(required - covered)
    completeness = "complete" if not missing else "partial"
    candidates = sorted({x["control_id"] for x in assertions if x["control_id"] not in submitted and x["coverage_state"] == "covers" and x["element_id"] in missing})
    return {"case_id": case_id, "proposal_disposition": "accept" if completeness == "complete" else "amend", "current_mapping_control_ids": sorted(submitted), "candidate_additional_control_ids": candidates, "mapping_completeness": completeness, "uncovered_obligation_elements": missing, "rationale": "Deterministically derived from the approved obligation-element coverage rulebook."}


def validate_observations(payload: dict[str, Any], case: dict[str, Any], rulebook: dict[str, Any]) -> None:
    if payload.get("case_id") != case["case_id"]:
        raise ValueError("Observation case ID mismatch")
    evidence = {x["evidence_id"]: x for x in case["presented_evidence"]}
    requirements = {x["requirement_id"]: x for x in rulebook["evidence_requirements"]}
    observations = payload.get("observations", [])
    ids = [x["evidence_id"] for x in observations]
    if set(ids) != set(evidence) or len(ids) != len(set(ids)):
        raise ValueError("Every supplied evidence item requires exactly one observation")
    for item in observations:
        if item["requirement_id"] not in requirements:
            raise ValueError("Unknown approved evidence requirement")
        source = evidence[item["evidence_id"]]
        requirement = requirements[item["requirement_id"]]
        if source["evidence_type"] not in requirement["accepted_evidence_types"]:
            raise ValueError("Evidence type is incompatible with approved requirement")
        if source["status"] == "missing" and item["observed_state"] != "missing":
            raise ValueError("Explicitly missing evidence must remain missing")


def derive_evidence_assessment(payload: dict[str, Any], rulebook: dict[str, Any]) -> str:
    requirements = {x["requirement_id"]: x for x in rulebook["evidence_requirements"]}
    pairs = [(requirements[x["requirement_id"]]["requirement_class"], x["observed_state"]) for x in payload["observations"]]
    if any(state == "adverse_indicator_present" for _, state in pairs):
        return "adverse_operating_evidence"
    if any(kind == "design_attribute" and state in {"present_deficient", "missing"} for kind, state in pairs):
        return "design_deficiency"
    if any(kind == "operating_record" and state == "missing" for kind, state in pairs):
        return "missing_operating_evidence"
    if any(state == "not_assessable" for _, state in pairs):
        return "insufficient_to_assess"
    return "sufficient"
