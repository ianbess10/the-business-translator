"""Deterministic cross-field semantic validation for v1.3 stage outputs."""

from __future__ import annotations

from typing import Any, Iterable


def _non_empty_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _unique_strings(values: Any, field: str, *, allow_empty_items: bool = False) -> set[str]:
    if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
        raise ValueError(f"{field} must be an array of strings")
    if not allow_empty_items and any(not item.strip() for item in values):
        raise ValueError(f"{field} cannot contain an empty string")
    if len(values) != len(set(values)):
        raise ValueError(f"{field} must not contain duplicates")
    return set(values)


def _case_id(payload: dict[str, Any], expected_case_id: str | None) -> None:
    _non_empty_string(payload.get("case_id"), "case_id")
    if expected_case_id is not None and payload["case_id"] != expected_case_id:
        raise ValueError("Stage case ID does not match the supplied input")


def validate_source_stage(
    payload: dict[str, Any], expected_case_id: str | None = None
) -> None:
    _case_id(payload, expected_case_id)
    _non_empty_string(payload.get("rationale"), "rationale")
    _unique_strings(payload.get("material_missing_fact_types"), "material_missing_fact_types")
    unsupported = _unique_strings(payload.get("unsupported_elements"), "unsupported_elements")
    support = payload.get("statement_support")
    if support == "exact_supported" and unsupported:
        raise ValueError("Exact source support requires no unsupported elements")
    if support in {"partially_supported", "unsupported_extension"} and not unsupported:
        raise ValueError("Partial or unsupported source support requires unsupported elements")


def validate_mapping_stage(
    payload: dict[str, Any],
    expected_case_id: str | None = None,
    submitted_control_ids: Iterable[str] | None = None,
    catalogue_control_ids: Iterable[str] | None = None,
) -> None:
    _case_id(payload, expected_case_id)
    _non_empty_string(payload.get("rationale"), "rationale")
    current = _unique_strings(payload.get("current_mapping_control_ids"), "current_mapping_control_ids")
    candidates = _unique_strings(payload.get("candidate_additional_control_ids"), "candidate_additional_control_ids")
    uncovered = _unique_strings(payload.get("uncovered_obligation_elements"), "uncovered_obligation_elements")
    if current & candidates:
        raise ValueError("Current and candidate additional controls must be disjoint")
    if submitted_control_ids is not None:
        submitted = set(submitted_control_ids)
        if not current.issubset(submitted):
            raise ValueError("Current mapping controls must be a subset of the submitted mapping")
        if candidates & submitted:
            raise ValueError("A submitted mapping control cannot be an additional candidate")
    if catalogue_control_ids is not None:
        unknown = sorted((current | candidates) - set(catalogue_control_ids))
        if unknown:
            raise ValueError(f"Mapping stage returned unknown catalogue controls: {unknown}")
    completeness = payload.get("mapping_completeness")
    if completeness == "complete" and (not current or uncovered):
        raise ValueError("Complete mapping requires current controls and no uncovered elements")
    if completeness == "partial" and (not current or not uncovered):
        raise ValueError("Partial mapping requires current controls and uncovered elements")
    if completeness == "no_suitable_control" and (current or not uncovered):
        raise ValueError("No-suitable-control mapping requires no current controls and uncovered elements")


def validate_evidence_stage(
    payload: dict[str, Any], expected_case_id: str | None = None
) -> None:
    _case_id(payload, expected_case_id)
    _non_empty_string(payload.get("rationale"), "rationale")
    assessment = payload.get("evidence_assessment")
    design = payload.get("design_deficiency_evidence_present")
    adverse = payload.get("adverse_indicator_present")
    severity = payload.get("severity_recommendation")
    if design is True and adverse is True:
        raise ValueError("Design-deficiency and adverse-operating flags cannot both be true")
    if (assessment == "design_deficiency") != (design is True):
        raise ValueError("Design-deficiency assessment and evidence flag must agree")
    if (assessment == "adverse_operating_evidence") != (adverse is True):
        raise ValueError("Adverse-operating assessment and indicator flag must agree")
    if assessment == "sufficient" and severity != "not_applicable":
        raise ValueError("Sufficient evidence requires not-applicable severity")
    if assessment in {
        "missing_operating_evidence",
        "insufficient_to_assess",
        "not_assessed_no_current_control",
    } and severity != "unassessed":
        raise ValueError("Unassessed evidence outcomes require unassessed severity")
    if assessment in {"design_deficiency", "adverse_operating_evidence"} and severity in {
        "not_applicable",
        "unassessed",
    }:
        raise ValueError("Observed deficiency or adverse evidence requires assessed severity")
