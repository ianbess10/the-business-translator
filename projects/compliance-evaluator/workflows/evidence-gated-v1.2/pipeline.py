"""Deterministic policy layer for Evidence-Gated Decision Pipeline v1.2."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


APPLICABILITY_MAP = {
    "applicable": "applicable_candidate",
    "out_of_scope": "out_of_scope",
    "uncertain": "applicability_uncertain",
    "not_assessed": "not_assessed",
}

STATEMENT_SUPPORT_RULES = {
    "exact_supported": "SUP-RULE-EXACT-SOURCE-SUPPORT",
    "partially_supported": "SUP-RULE-PARTIAL-SOURCE-SUPPORT",
    "unsupported_extension": "SUP-RULE-UNSUPPORTED-EXTENSION",
    "not_assessable": "SUP-RULE-NOT-ASSESSABLE",
}


def _catalogue(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["control_id"]: item for item in profile["controls"]}


def _assurance_entered(case: dict[str, Any]) -> bool:
    upstream = case["upstream_obligation"]
    return upstream["supplied"] is True and upstream["status"] == "approved"


def _source_rule(
    case: dict[str, Any],
    source_stage: dict[str, Any],
    source_policy: dict[str, Any],
) -> dict[str, Any]:
    source_ids = case["source_ids"]
    missing_blob = " ".join(case["missing_facts"]).lower()
    conflict_rule = source_policy["multi_source_conflict_rule"]
    conflict_terms_present = any(
        term.lower() in missing_blob for term in conflict_rule["missing_fact_terms"]
    )
    if len(source_ids) >= conflict_rule["minimum_source_count"] and (
        conflict_terms_present or source_stage["source_conflict_present"]
    ):
        return deepcopy(conflict_rule)

    rules = []
    for source_id in source_ids:
        try:
            rules.append(source_policy["sources"][source_id])
        except KeyError as exc:
            raise ValueError(f"Unknown source ID in policy table: {source_id}") from exc
    if not rules:
        raise ValueError("At least one source ID is required")
    if len(rules) > 1:
        decision_keys = (
            "source_use_disposition",
            "obligation_outcome",
            "applicability_mode",
        )
        decisions = {tuple(rule[key] for key in decision_keys) for rule in rules}
        if len(decisions) != 1:
            raise ValueError("Multiple source policies require explicit reconciliation")
    return deepcopy(rules[0])


def _approved_obligation_decisions(
    case: dict[str, Any],
    approved_obligation: dict[str, Any] | None,
    applicability_policy: dict[str, Any],
) -> tuple[str, str, str, str]:
    if approved_obligation is None:
        raise ValueError("Entered assurance requires the reviewed approved-obligation record")
    upstream = case["upstream_obligation"]
    if approved_obligation.get("obligation_id") != upstream.get("obligation_id"):
        raise ValueError("Approved-obligation ID does not match the input case")
    if approved_obligation.get("lifecycle_status") != "approved":
        raise ValueError("Approved-obligation lifecycle status is not approved")
    if approved_obligation.get("human_review", {}).get("status") != "accepted":
        raise ValueError("Approved-obligation human review is not accepted")
    source_id = approved_obligation.get("source", {}).get("source_id")
    if source_id not in case["source_ids"]:
        raise ValueError("Approved-obligation source is not one of the case source IDs")

    source_use = approved_obligation.get("classification", {}).get(
        "source_use_disposition"
    )
    obligation_outcome = approved_obligation.get("assessment", {}).get("outcome")
    applicability = approved_obligation.get("applicability", {}).get("status")
    allowed = applicability_policy["approved_obligation_authority"]
    if source_use not in allowed["allowed_source_use_dispositions"]:
        raise ValueError("Approved-obligation source disposition is not permitted")
    if obligation_outcome not in allowed["allowed_obligation_outcomes"]:
        raise ValueError("Approved-obligation outcome is not permitted")
    if applicability not in allowed["allowed_applicability_statuses"]:
        raise ValueError("Approved-obligation applicability status is not permitted")
    return source_use, obligation_outcome, applicability, allowed["rule_id"]


def _applicability(
    case: dict[str, Any],
    source_rule: dict[str, Any],
    source_stage: dict[str, Any],
    applicability_policy: dict[str, Any],
) -> tuple[str, str]:
    mode = source_rule["applicability_mode"]
    if mode == "fixed_not_assessed":
        rule = applicability_policy["fixed_modes"]["fixed_not_assessed"]
        return rule["status"], rule["rule_id"]
    if mode == "fixed_uncertain":
        rule = applicability_policy["fixed_modes"]["fixed_uncertain"]
        return rule["status"], rule["rule_id"]
    if mode != "model_assessed":
        raise ValueError(f"Unsupported applicability mode: {mode}")

    rule = applicability_policy["fact_based_model_assessed"]
    institution_blob = " ".join(case["institution_facts"]).lower()
    if any(term.lower() in institution_blob for term in rule["out_of_scope_terms"]):
        return rule["out_of_scope_status"], rule["rule_id"]
    if case["missing_facts"]:
        return rule["missing_fact_status"], rule["rule_id"]
    if case["institution_facts"]:
        return rule["supported_fact_status"], rule["rule_id"]
    return APPLICABILITY_MAP[source_stage["applicability_assessment"]], rule[
        "fallback_rule_id"
    ]


def _resolve_controls(
    control_ids: list[str], profile: dict[str, Any]
) -> list[dict[str, str]]:
    catalogue = _catalogue(profile)
    mappings: list[dict[str, str]] = []
    for control_id in sorted(set(control_ids)):
        if control_id not in catalogue:
            raise ValueError(f"Control ID is not in the frozen catalogue: {control_id}")
        mappings.append(
            {
                "control_id": control_id,
                "owner_role": catalogue[control_id]["owner_role"],
            }
        )
    return mappings


def _validate_mapping_boundary(
    case: dict[str, Any],
    mapping_stage: dict[str, Any],
    profile: dict[str, Any],
) -> None:
    proposed = set(case["proposed_mapping"]["control_ids"])
    current = set(mapping_stage["current_mapping_control_ids"])
    candidates = set(mapping_stage["candidate_additional_control_ids"])
    catalogue = _catalogue(profile)

    if not current.issubset(proposed):
        raise ValueError("Current mapping controls must be a subset of the submitted mapping")
    if current & candidates:
        raise ValueError("Current and candidate additional controls must be disjoint")
    if candidates & proposed:
        raise ValueError("A submitted mapping control cannot be an additional candidate")
    unknown = sorted((current | candidates) - set(catalogue))
    if unknown:
        raise ValueError(f"Mapping stage returned unknown catalogue controls: {unknown}")

    completeness = mapping_stage["mapping_completeness"]
    uncovered = mapping_stage["uncovered_obligation_elements"]
    if completeness == "complete" and (not current or uncovered):
        raise ValueError("Complete mapping requires current controls and no uncovered elements")
    if completeness == "partial" and (not current or not uncovered):
        raise ValueError("Partial mapping requires current controls and uncovered elements")
    if completeness == "no_suitable_control" and (current or not uncovered):
        raise ValueError(
            "No-suitable-control mapping requires no current controls and uncovered elements"
        )


def _assurance_decision(
    mapping_stage: dict[str, Any],
    evidence_stage: dict[str, Any],
    assurance_policy: dict[str, Any],
) -> tuple[dict[str, Any], list[str], str]:
    completeness = mapping_stage["mapping_completeness"]
    mapping_status = assurance_policy["mapping_status"][completeness]
    rule_ids = [assurance_policy["mapping_rules"][completeness]]
    assessment = evidence_stage["evidence_assessment"]
    design_present = evidence_stage["design_deficiency_evidence_present"]
    adverse_present = evidence_stage["adverse_indicator_present"]

    if (assessment == "design_deficiency") != design_present:
        raise ValueError("Design-deficiency assessment and evidence flag must agree")
    if (assessment == "adverse_operating_evidence") != adverse_present:
        raise ValueError("Adverse-operating assessment and indicator flag must agree")

    if completeness == "no_suitable_control":
        selected = "not_assessed_no_current_control"
        decision = deepcopy(assurance_policy["evidence_assessments"][selected])
    elif design_present:
        decision = deepcopy(
            assurance_policy["evidence_assessments"]["design_deficiency"]
        )
    elif completeness == "partial":
        decision = deepcopy(assurance_policy["partial_coverage_precedence"])
    else:
        if assessment == "not_assessed_no_current_control":
            raise ValueError("A current control cannot use no-current-control evidence status")
        decision = deepcopy(assurance_policy["evidence_assessments"][assessment])

    rule_ids.append(decision["rule_id"])
    return decision, rule_ids, mapping_status


def derive_escalation(
    decision: dict[str, Any],
    escalation_policy: dict[str, Any],
    workstream: str | None = None,
) -> tuple[bool, list[str], str]:
    trigger: str | None = None
    if (
        decision["obligation_outcome"] == "final_change_pending_commencement"
        and decision["applicability_status"] == "applicability_uncertain"
    ):
        trigger = "final_change_pending_commencement_and_applicability_uncertain"
    elif decision["obligation_outcome"] == "source_conflict":
        trigger = "source_conflict"
    elif (
        decision["assurance_outcome"] == "potential_control_gap"
        and decision["gap_severity"] in {"high", "critical"}
        and "control_design" in decision["gap_types"]
    ):
        trigger = "high_control_design_gap"
    elif (
        decision["assurance_outcome"] == "potential_control_gap"
        and decision["gap_severity"] in {"high", "critical"}
        and "operating_exception" in decision["gap_types"]
    ):
        trigger = "high_operating_exception"

    if trigger is None:
        default = escalation_policy["default"]
        return False, [], default["rule_id"]
    resolved_workstream = workstream or decision.get("workstream")
    if resolved_workstream not in {"aml_cft", "market_conduct"}:
        raise ValueError("A valid workstream is required to derive escalation roles")
    for rule in escalation_policy["rules"]:
        if rule["trigger"] == trigger:
            return True, list(rule["workstream_roles"][resolved_workstream]), rule[
                "rule_id"
            ]
    raise ValueError(f"No escalation policy found for trigger: {trigger}")


def validate_final_decision(
    decision: dict[str, Any],
    profile: dict[str, Any],
    escalation_policy: dict[str, Any],
    workstream: str,
) -> None:
    errors: list[str] = []
    if decision["human_review_required"] is not True:
        errors.append("human_review_required must be true")
    if decision["compliance_conclusion"] != "not_determined":
        errors.append("compliance_conclusion must remain not_determined")

    if decision["assurance_gate"] == "not_entered":
        expected_closed = {
            "mapping_status": "not_applicable",
            "control_mappings": [],
            "assurance_outcome": "not_applicable",
            "gap_types": [],
            "gap_severity": "not_applicable",
            "remediation_action_types": [],
        }
        for field, expected_value in expected_closed.items():
            if decision[field] != expected_value:
                errors.append(
                    f"{field} must be {expected_value!r} when assurance is not entered"
                )
    elif decision["assurance_gate"] == "entered":
        catalogue = _catalogue(profile)
        for mapping in decision["control_mappings"]:
            control_id = mapping["control_id"]
            if control_id not in catalogue:
                errors.append(f"unknown control ID: {control_id}")
            elif mapping["owner_role"] != catalogue[control_id]["owner_role"]:
                errors.append(f"catalogue owner mismatch for {control_id}")
        if decision["mapping_status"] == "no_suitable_control_identified":
            if decision["control_mappings"]:
                errors.append("no suitable control status must not contain control mappings")
        elif not decision["control_mappings"]:
            errors.append("entered mapped or partial assessment requires a control mapping")
    else:
        errors.append(f"unknown assurance_gate: {decision['assurance_gate']}")

    outcome = decision["assurance_outcome"]
    if outcome == "mapped_and_evidenced":
        if decision["gap_types"] or decision["remediation_action_types"]:
            errors.append("mapped_and_evidenced cannot contain gaps or remediation")
        if decision["gap_severity"] != "not_applicable":
            errors.append("mapped_and_evidenced severity must be not_applicable")
    if outcome == "insufficient_evidence":
        if "evidence_request" not in decision["remediation_action_types"]:
            errors.append("insufficient_evidence requires an evidence request")
        if decision["gap_severity"] != "unassessed":
            errors.append("insufficient_evidence severity must remain unassessed")
    if outcome == "potential_control_gap":
        if not decision["gap_types"]:
            errors.append("potential_control_gap requires at least one gap type")
        if decision["gap_severity"] in {"not_applicable", "unassessed"}:
            errors.append("potential_control_gap requires an assessed severity")

    expected_required, expected_roles, _ = derive_escalation(
        decision, escalation_policy, workstream
    )
    if decision["escalation_required"] != expected_required:
        errors.append("escalation_required conflicts with the escalation policy")
    if sorted(decision["escalation_roles"]) != sorted(expected_roles):
        errors.append("escalation_roles conflict with the escalation policy")
    if errors:
        raise ValueError("Cross-field reconciliation failed: " + "; ".join(errors))


def compose_final_decision(
    case: dict[str, Any],
    source_stage: dict[str, Any] | None,
    mapping_stage: dict[str, Any] | None,
    evidence_stage: dict[str, Any] | None,
    approved_obligation: dict[str, Any] | None,
    source_policy: dict[str, Any],
    applicability_policy: dict[str, Any],
    assurance_policy: dict[str, Any],
    escalation_policy: dict[str, Any],
    profile: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    case_id = case["case_id"]
    assurance_entered = _assurance_entered(case)
    applied_rules: list[str] = []
    statement_support: str | None = None
    legal_readiness: str | None = None

    if assurance_entered:
        if source_stage is not None:
            raise ValueError("Approved assurance must bypass the source/support model stage")
        (
            source_use_disposition,
            obligation_outcome,
            applicability_status,
            approved_rule_id,
        ) = _approved_obligation_decisions(
            case, approved_obligation, applicability_policy
        )
        applied_rules.append(approved_rule_id)
        source_text = (
            "Reviewed approved-obligation authority supplied source, obligation and "
            "applicability decisions."
        )
        applicability_rule_id = approved_rule_id
    else:
        if source_stage is None:
            raise ValueError("A non-approved case requires a source/support stage output")
        if source_stage["case_id"] != case_id:
            raise ValueError("Source-stage case ID does not match the input case")
        if approved_obligation is not None:
            raise ValueError("A non-approved case cannot supply an approved-obligation record")
        source_rule = _source_rule(case, source_stage, source_policy)
        source_use_disposition = source_rule["source_use_disposition"]
        obligation_outcome = source_rule["obligation_outcome"]
        statement_support = source_stage["statement_support"]
        legal_readiness = source_stage["legal_readiness"]
        support_rule_id = STATEMENT_SUPPORT_RULES[statement_support]
        if obligation_outcome == "candidate_binding_obligation" and statement_support in {
            "partially_supported",
            "unsupported_extension",
            "not_assessable",
        }:
            obligation_outcome = "unsupported_obligation"
        applicability_status, applicability_rule_id = _applicability(
            case, source_rule, source_stage, applicability_policy
        )
        applied_rules.extend(
            [source_rule["rule_id"], support_rule_id, applicability_rule_id]
        )
        source_text = source_stage["rationale"]

    decision: dict[str, Any] = {
        "case_id": case_id,
        "source_use_disposition": source_use_disposition,
        "obligation_outcome": obligation_outcome,
        "applicability_status": applicability_status,
        "assurance_gate": "entered" if assurance_entered else "not_entered",
        "mapping_status": "not_applicable",
        "control_mappings": [],
        "assurance_outcome": "not_applicable",
        "gap_types": [],
        "gap_severity": "not_applicable",
        "remediation_action_types": [],
        "escalation_required": False,
        "escalation_roles": [],
        "human_review_required": True,
        "compliance_conclusion": "not_determined",
        "rationale": "",
    }

    current_ids: list[str] = []
    candidate_ids: list[str] = []
    uncovered_elements: list[str] = []
    if assurance_entered:
        if mapping_stage is None or evidence_stage is None:
            raise ValueError("Entered assurance requires isolated mapping and evidence stages")
        if mapping_stage["case_id"] != case_id or evidence_stage["case_id"] != case_id:
            raise ValueError("Assurance-stage case ID does not match the input case")
        _validate_mapping_boundary(case, mapping_stage, profile)
        current_ids = list(mapping_stage["current_mapping_control_ids"])
        candidate_ids = list(mapping_stage["candidate_additional_control_ids"])
        uncovered_elements = list(mapping_stage["uncovered_obligation_elements"])
        evidence_decision, assurance_rule_ids, mapping_status = _assurance_decision(
            mapping_stage, evidence_stage, assurance_policy
        )
        decision.update(
            {
                "mapping_status": mapping_status,
                "control_mappings": _resolve_controls(current_ids, profile),
                "assurance_outcome": evidence_decision["assurance_outcome"],
                "gap_types": evidence_decision["gap_types"],
                "gap_severity": evidence_decision["gap_severity"],
                "remediation_action_types": evidence_decision[
                    "remediation_action_types"
                ],
            }
        )
        applied_rules.extend(assurance_rule_ids)
        assurance_text = (
            f" Mapping stage: {mapping_stage['rationale']}"
            f" Evidence stage: {evidence_stage['rationale']}"
        )
    else:
        if mapping_stage is not None or evidence_stage is not None:
            raise ValueError("Closed assurance cannot contain mapping or evidence output")
        assurance_text = " Assurance was not entered; downstream fields were normalised."

    escalation_required, escalation_roles, escalation_rule_id = derive_escalation(
        decision, escalation_policy, case["workstream"]
    )
    decision["escalation_required"] = escalation_required
    decision["escalation_roles"] = escalation_roles
    applied_rules.append(escalation_rule_id)
    decision["rationale"] = (
        f"Source/obligation authority: {source_text}"
        f"{assurance_text} Policy rules: {', '.join(applied_rules)}."
    )

    validate_final_decision(decision, profile, escalation_policy, case["workstream"])

    proposal = case["proposal_under_test"]
    compared_fields = (
        "source_use_disposition",
        "obligation_outcome",
        "applicability_status",
        "assurance_outcome",
        "escalation_required",
    )
    proposal_comparison = {
        field: {
            "proposed": proposal.get(field),
            "decided": decision[field],
            "changed": proposal.get(field) is not None
            and proposal.get(field) != decision[field],
        }
        for field in compared_fields
    }
    trace = {
        "applied_policy_rules": applied_rules,
        "approved_obligation_authority_used": assurance_entered,
        "source_stage_bypassed": assurance_entered,
        "statement_support": statement_support,
        "legal_readiness": legal_readiness,
        "applicability_rule_id": applicability_rule_id,
        "current_mapping_control_ids": sorted(current_ids),
        "candidate_additional_control_ids": sorted(candidate_ids),
        "uncovered_obligation_elements": uncovered_elements,
        "mapping_completeness_decided": (
            None if mapping_stage is None else mapping_stage["mapping_completeness"]
        ),
        "mapping_stage_received_evidence_status": False,
        "mapping_stage_received_escalation_proposal": False,
        "evidence_stage_can_change_mapping": False,
        "proposal_comparison": proposal_comparison,
        "proposed_owner": case["proposed_mapping"]["owner_role"],
        "resolved_control_owners": {
            item["control_id"]: item["owner_role"]
            for item in decision["control_mappings"]
        },
        "candidate_control_owners": {
            item["control_id"]: item["owner_role"]
            for item in _resolve_controls(candidate_ids, profile)
        },
        "case_specific_override": False,
        "rule_identity_case_id_collision": any(
            rule_id == case_id for rule_id in applied_rules
        ),
        "reconciliation_passed": True,
        "human_review_required": True,
    }
    return decision, trace
