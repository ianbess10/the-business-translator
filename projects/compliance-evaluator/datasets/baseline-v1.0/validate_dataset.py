#!/usr/bin/env python3
"""Validate the 24-case baseline against frozen project inputs and schemas."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:
    raise SystemExit(
        "Missing test dependency. Install it with: python3 -m pip install jsonschema"
    ) from exc


DATASET_DIR = Path(__file__).resolve().parent
PROJECT_DIR = DATASET_DIR.parents[1]
SCHEMA_PATH = DATASET_DIR / "baseline-record.schema.json"
META_PATH = DATASET_DIR / "baseline-v1.0.meta.json"
INPUT_PATHS = [
    DATASET_DIR / "inputs" / "aml-cft.json",
    DATASET_DIR / "inputs" / "market-conduct.json",
]
LABEL_PATHS = [
    DATASET_DIR / "labels" / "aml-cft.json",
    DATASET_DIR / "labels" / "market-conduct.json",
]
SOURCE_MANIFEST_PATH = (
    PROJECT_DIR / "source-packs" / "source-pack-v1.0" / "manifest.json"
)
PROFILE_PATH = (
    PROJECT_DIR
    / "profiles"
    / "synthetic-investment-wealth-institution-v1.0.json"
)
OBLIGATION_SCHEMA_PATH = (
    PROJECT_DIR
    / "schemas"
    / "obligation-schema-v1.0"
    / "obligation-record.schema.json"
)
CONTROL_SCHEMA_PATH = (
    PROJECT_DIR
    / "schemas"
    / "control-evidence-schema-v1.0"
    / "control-evidence-assessment.schema.json"
)

REQUIRED_COVERAGE = {
    "guidance_boundary",
    "draft_boundary",
    "superseded_source",
    "commencement_uncertainty",
    "blocked_source",
    "unofficial_compilation",
    "missing_applicability_fact",
    "out_of_scope_profile",
    "unsupported_extension",
    "premature_control_assurance",
    "human_approval_boundary",
    "source_conflict",
    "correct_mapping",
    "owner_routing",
    "operating_evidence_missing",
    "genuine_control_gap",
    "false_positive_gap",
    "partial_mapping",
    "missed_escalation",
    "unnecessary_escalation",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def schema_enum(schema: dict, path: tuple[str, ...]) -> set[str]:
    value = schema
    for key in path:
        value = value[key]
    return set(value)


def expected_source_use(source: dict) -> str:
    status = source["status"]
    binding_gate = source["binding_obligation_extraction"]
    if status == "current_official_guidance":
        return "guidance_only"
    if status == "superseded":
        return "historical_only"
    if status == "final_issued_commencement_unverified":
        return "final_change_event"
    if status == "draft_consultation":
        return "draft_watchlist"
    if status == "strategy_not_binding_instrument":
        return "strategy_context"
    if binding_gate == "allowed_with_human_review_and_staged_date_control":
        return "binding_candidate"
    return "blocked"


def expected_outcomes_for_source_use(source_use: str) -> set[str]:
    return {
        "guidance_only": {"guidance_context"},
        "historical_only": {"superseded"},
        "final_change_event": {"final_change_pending_commencement"},
        "draft_watchlist": {"draft_or_watchlist"},
        "strategy_context": {"strategy_context"},
        "binding_candidate": {"candidate_binding_obligation"},
        "blocked": {"blocked_source", "source_conflict"},
    }[source_use]


def validate_vocabularies(
    baseline_schema: dict,
    obligation_schema: dict,
    control_schema: dict,
) -> list[str]:
    errors: list[str] = []
    comparisons = {
        "source use": (
            schema_enum(baseline_schema, ("$defs", "source_use", "enum")),
            schema_enum(
                obligation_schema,
                ("$defs", "source_gate", "properties", "record_use", "enum"),
            ),
        ),
        "obligation outcome": (
            schema_enum(
                baseline_schema, ("$defs", "obligation_outcome", "enum")
            ),
            schema_enum(
                obligation_schema,
                ("$defs", "assessment", "properties", "outcome", "enum"),
            ),
        ),
        "applicability": (
            schema_enum(
                baseline_schema, ("$defs", "applicability_status", "enum")
            ),
            schema_enum(
                obligation_schema,
                ("$defs", "applicability", "properties", "status", "enum"),
            ),
        ),
        "mapping": (
            schema_enum(baseline_schema, ("$defs", "mapping_status", "enum")),
            schema_enum(
                control_schema,
                ("$defs", "mapping_summary", "properties", "status", "enum"),
            ),
        ),
        "assurance outcome": (
            schema_enum(
                baseline_schema, ("$defs", "assurance_outcome", "enum")
            ),
            schema_enum(
                control_schema,
                (
                    "$defs",
                    "assurance_assessment",
                    "properties",
                    "outcome",
                    "enum",
                ),
            ),
        ),
        "gap type": (
            schema_enum(baseline_schema, ("$defs", "gap_type", "enum")),
            schema_enum(
                control_schema,
                ("$defs", "assurance_gap", "properties", "gap_type", "enum"),
            ),
        ),
        "action type": (
            schema_enum(baseline_schema, ("$defs", "action_type", "enum")),
            schema_enum(
                control_schema,
                (
                    "$defs",
                    "remediation_action",
                    "properties",
                    "action_type",
                    "enum",
                ),
            ),
        ),
        "evidence type": (
            schema_enum(baseline_schema, ("$defs", "evidence_type", "enum")),
            schema_enum(control_schema, ("$defs", "evidence_type", "enum")),
        ),
    }
    for name, (baseline_values, frozen_values) in comparisons.items():
        if baseline_values != frozen_values:
            errors.append(f"baseline {name} vocabulary differs from frozen schema")
    return errors


def validate_freeze_metadata(meta: dict) -> list[str]:
    errors: list[str] = []
    hash_checks = {
        "baseline_record_schema_sha256": SCHEMA_PATH,
        "aml_cft_inputs_sha256": INPUT_PATHS[0],
        "market_conduct_inputs_sha256": INPUT_PATHS[1],
        "aml_cft_labels_sha256": LABEL_PATHS[0],
        "market_conduct_labels_sha256": LABEL_PATHS[1],
        "institution_profile_sha256": PROFILE_PATH,
        "source_pack_manifest_sha256": SOURCE_MANIFEST_PATH,
        "obligation_schema_sha256": OBLIGATION_SCHEMA_PATH,
        "control_evidence_schema_sha256": CONTROL_SCHEMA_PATH,
    }
    for field, path in hash_checks.items():
        if meta[field] != sha256(path):
            errors.append(f"freeze hash mismatch: {field}")
    return errors


def validate_dataset(
    inputs: list[dict],
    labels: list[dict],
    validator: Draft202012Validator,
    sources: dict[str, dict],
    profile: dict,
    obligation_validator: Draft202012Validator,
    require_coverage: bool = True,
) -> list[str]:
    errors: list[str] = []
    for record in inputs + labels:
        errors.extend(
            f"{record.get('case_id', 'unknown')}: {error.message}"
            for error in validator.iter_errors(record)
        )

    input_ids = [record["case_id"] for record in inputs]
    label_ids = [record["case_id"] for record in labels]
    duplicate_inputs = [
        case_id for case_id, count in Counter(input_ids).items() if count > 1
    ]
    duplicate_labels = [
        case_id for case_id, count in Counter(label_ids).items() if count > 1
    ]
    if duplicate_inputs:
        errors.append(f"duplicate input IDs: {duplicate_inputs}")
    if duplicate_labels:
        errors.append(f"duplicate label IDs: {duplicate_labels}")
    if set(input_ids) != set(label_ids):
        errors.append("input and label case IDs do not match")

    input_by_id = {record["case_id"]: record for record in inputs}
    label_by_id = {record["case_id"]: record for record in labels}
    controls = {item["control_id"]: item for item in profile["controls"]}

    for case_id in sorted(set(input_by_id) & set(label_by_id)):
        case = input_by_id[case_id]
        label = label_by_id[case_id]
        expected = label["expected"]

        if case["workstream"] != label["workstream"]:
            errors.append(f"{case_id}: input and label workstreams differ")
        if case_id.startswith("AML-") and case["workstream"] != "aml_cft":
            errors.append(f"{case_id}: AML prefix has wrong workstream")
        if case_id.startswith("CON-") and case["workstream"] != "market_conduct":
            errors.append(f"{case_id}: CON prefix has wrong workstream")

        case_sources = []
        for source_id in case["source_ids"]:
            source = sources.get(source_id)
            if source is None:
                errors.append(f"{case_id}: unknown source {source_id}")
            else:
                case_sources.append(source)

        if case_sources:
            permitted_source_uses = {
                expected_source_use(source) for source in case_sources
            }
            if len(case_sources) > 1 and "blocked" in permitted_source_uses:
                permitted_source_uses.add("blocked")
            if expected["source_use_disposition"] not in permitted_source_uses:
                errors.append(
                    f"{case_id}: expected source use conflicts with manifest gates"
                )
            permitted_outcomes = expected_outcomes_for_source_use(
                expected["source_use_disposition"]
            )
            if expected["obligation_outcome"] not in permitted_outcomes:
                errors.append(
                    f"{case_id}: obligation outcome conflicts with source use"
                )

        for control_id in case["proposed_mapping"]["control_ids"]:
            if control_id not in controls:
                errors.append(f"{case_id}: unknown proposed control {control_id}")

        for mapping in expected["control_mappings"]:
            control = controls.get(mapping["control_id"])
            if control is None:
                errors.append(
                    f"{case_id}: unknown expected control {mapping['control_id']}"
                )
            elif control["owner_role"] != mapping["owner_role"]:
                errors.append(
                    f"{case_id}: expected owner for {mapping['control_id']} "
                    "differs from frozen profile"
                )

        upstream = case["upstream_obligation"]
        upstream_approved = upstream["supplied"] and upstream["status"] == "approved"
        if upstream_approved:
            fixture_path = (DATASET_DIR / upstream["fixture_path"]).resolve()
            if not fixture_path.is_file():
                errors.append(f"{case_id}: upstream obligation fixture not found")
            else:
                fixture = load_json(fixture_path)
                fixture_errors = list(obligation_validator.iter_errors(fixture))
                if fixture_errors:
                    errors.append(
                        f"{case_id}: upstream fixture fails Obligation Schema v1.0"
                    )
                if fixture.get("lifecycle_status") != "approved":
                    errors.append(f"{case_id}: upstream fixture is not approved")
                if fixture.get("obligation_id") != upstream["obligation_id"]:
                    errors.append(f"{case_id}: upstream obligation ID mismatch")

        gate_entered = expected["assurance_gate"] == "entered"
        if gate_entered != upstream_approved:
            errors.append(
                f"{case_id}: assurance gate does not match upstream approval state"
            )

        if gate_entered:
            if expected["source_use_disposition"] != "binding_candidate":
                errors.append(
                    f"{case_id}: assurance entered without a binding-candidate source"
                )
            if expected["obligation_outcome"] != "candidate_binding_obligation":
                errors.append(
                    f"{case_id}: assurance entered without a binding obligation outcome"
                )

        outcome = expected["assurance_outcome"]
        gaps = expected["gap_types"]
        actions = expected["remediation_action_types"]
        if outcome == "mapped_and_evidenced" and (gaps or actions):
            errors.append(
                f"{case_id}: mapped-and-evidenced label cannot contain gaps or actions"
            )
        if outcome == "insufficient_evidence":
            if not gaps or not actions:
                errors.append(
                    f"{case_id}: insufficient-evidence label requires a gap and action"
                )
        if outcome == "potential_control_gap":
            if not gaps or not actions:
                errors.append(
                    f"{case_id}: potential-gap label requires a gap and action"
                )

        escalation_required = expected["escalation_required"]
        escalation_roles = expected["escalation_roles"]
        if escalation_required and not escalation_roles:
            errors.append(f"{case_id}: required escalation has no route")
        if not escalation_required and escalation_roles:
            errors.append(f"{case_id}: non-escalated case has escalation roles")
        if expected["gap_severity"] in {"high", "critical"}:
            if not escalation_required:
                errors.append(f"{case_id}: material gap is not escalated")

    counts = Counter(record["workstream"] for record in inputs)
    if counts != Counter({"aml_cft": 12, "market_conduct": 12}):
        errors.append(f"workstream balance is not 12/12: {dict(counts)}")
    if len(inputs) != 24 or len(labels) != 24:
        errors.append(
            f"dataset must contain 24 inputs and 24 labels, got "
            f"{len(inputs)} and {len(labels)}"
        )

    serialized = json.dumps(inputs + labels)
    if "non_compliant" in serialized or '"compliant"' in serialized:
        errors.append("dataset contains a prohibited compliance conclusion")

    if require_coverage:
        actual_coverage = {
            tag for label in labels for tag in label["error_tags"]
        }
        missing_coverage = sorted(REQUIRED_COVERAGE - actual_coverage)
        if missing_coverage:
            errors.append(f"required coverage tags missing: {missing_coverage}")

    return errors


def expect_invalid(
    name: str,
    inputs: list[dict],
    labels: list[dict],
    validator: Draft202012Validator,
    sources: dict[str, dict],
    profile: dict,
    obligation_validator: Draft202012Validator,
    require_coverage: bool = True,
) -> None:
    errors = validate_dataset(
        inputs,
        labels,
        validator,
        sources,
        profile,
        obligation_validator,
        require_coverage=require_coverage,
    )
    if not errors:
        raise AssertionError(f"Prohibited dataset state validated: {name}")
    print(f"prohibited_state_rejected: {name}")


def main() -> None:
    baseline_schema = load_json(SCHEMA_PATH)
    obligation_schema = load_json(OBLIGATION_SCHEMA_PATH)
    control_schema = load_json(CONTROL_SCHEMA_PATH)
    Draft202012Validator.check_schema(baseline_schema)

    vocabulary_errors = validate_vocabularies(
        baseline_schema, obligation_schema, control_schema
    )
    if vocabulary_errors:
        raise AssertionError("; ".join(vocabulary_errors))
    print("frozen_schema_vocabularies_aligned")

    validator = Draft202012Validator(
        baseline_schema, format_checker=FormatChecker()
    )
    obligation_validator = Draft202012Validator(
        obligation_schema, format_checker=FormatChecker()
    )
    manifest = load_json(SOURCE_MANIFEST_PATH)
    sources = {item["source_id"]: item for item in manifest["sources"]}
    profile = load_json(PROFILE_PATH)
    meta = load_json(META_PATH)
    inputs = [record for path in INPUT_PATHS for record in load_json(path)]
    labels = [record for path in LABEL_PATHS for record in load_json(path)]

    errors = validate_dataset(
        inputs, labels, validator, sources, profile, obligation_validator
    )
    if errors:
        raise AssertionError("; ".join(errors))

    freeze_errors = validate_freeze_metadata(meta)
    if freeze_errors:
        raise AssertionError("; ".join(freeze_errors))

    metadata_counts = {
        "input_case_count": len(inputs),
        "label_count": len(labels),
        "aml_cft_case_count": sum(
            record["workstream"] == "aml_cft" for record in inputs
        ),
        "market_conduct_case_count": sum(
            record["workstream"] == "market_conduct" for record in inputs
        ),
        "control_assurance_case_count": sum(
            label["expected"]["assurance_gate"] == "entered" for label in labels
        ),
        "required_coverage_tag_count": len(REQUIRED_COVERAGE),
        "prohibited_state_test_count": 12,
    }
    for field, actual in metadata_counts.items():
        if meta[field] != actual:
            raise AssertionError(
                f"freeze metadata count mismatch: {field}={meta[field]}, actual={actual}"
            )
    print("dataset_freeze_metadata_passed")

    print("baseline_inputs_passed: 24")
    print("baseline_labels_passed: 24")
    print("workstream_balance_passed: 12 AML/CFT and 12 market conduct")
    entered = sum(
        label["expected"]["assurance_gate"] == "entered" for label in labels
    )
    print(f"control_assurance_cases_passed: {entered}")
    print(f"required_coverage_tags_passed: {len(REQUIRED_COVERAGE)}")

    duplicate_inputs = copy.deepcopy(inputs)
    duplicate_inputs[-1]["case_id"] = duplicate_inputs[0]["case_id"]
    expect_invalid(
        "duplicate_case_id",
        duplicate_inputs,
        labels,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    missing_label = copy.deepcopy(labels[:-1])
    expect_invalid(
        "input_without_label",
        inputs,
        missing_label,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    unknown_source = copy.deepcopy(inputs)
    unknown_source[0]["source_ids"] = ["SA-UNKNOWN-001"]
    expect_invalid(
        "unknown_source",
        unknown_source,
        labels,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    unknown_control = copy.deepcopy(inputs)
    next(item for item in unknown_control if item["case_id"] == "CON-005")[
        "proposed_mapping"
    ]["control_ids"] = ["C-CON-999"]
    expect_invalid(
        "unknown_control",
        unknown_control,
        labels,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    wrong_owner = copy.deepcopy(labels)
    next(item for item in wrong_owner if item["case_id"] == "CON-006")[
        "expected"
    ]["control_mappings"][0]["owner_role"] = "Conduct Risk Officer"
    expect_invalid(
        "wrong_frozen_control_owner",
        inputs,
        wrong_owner,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    premature_gate = copy.deepcopy(labels)
    next(item for item in premature_gate if item["case_id"] == "AML-011")[
        "expected"
    ].update(
        {
            "assurance_gate": "entered",
            "mapping_status": "mapped",
            "control_mappings": [
                {"control_id": "C-AML-004", "owner_role": "AML Operations Manager"}
            ],
            "assurance_outcome": "mapped_and_evidenced",
        }
    )
    expect_invalid(
        "assurance_without_approved_obligation",
        inputs,
        premature_gate,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    wrong_draft_use = copy.deepcopy(labels)
    draft_label = next(item for item in wrong_draft_use if item["case_id"] == "AML-004")
    draft_label["expected"]["source_use_disposition"] = "binding_candidate"
    draft_label["expected"]["obligation_outcome"] = "candidate_binding_obligation"
    expect_invalid(
        "draft_labelled_binding",
        inputs,
        wrong_draft_use,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    evidenced_with_gap = copy.deepcopy(labels)
    positive = next(item for item in evidenced_with_gap if item["case_id"] == "CON-005")
    positive["expected"]["gap_types"] = ["control_design"]
    expect_invalid(
        "mapped_and_evidenced_with_gap",
        inputs,
        evidenced_with_gap,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    insufficient_without_action = copy.deepcopy(labels)
    insufficient = next(
        item for item in insufficient_without_action if item["case_id"] == "CON-007"
    )
    insufficient["expected"]["remediation_action_types"] = []
    expect_invalid(
        "insufficient_evidence_without_action",
        inputs,
        insufficient_without_action,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    missed_escalation = copy.deepcopy(labels)
    material = next(item for item in missed_escalation if item["case_id"] == "CON-011")
    material["expected"]["escalation_required"] = False
    material["expected"]["escalation_roles"] = []
    expect_invalid(
        "high_gap_without_escalation",
        inputs,
        missed_escalation,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    unbalanced_inputs = copy.deepcopy(inputs[:-1])
    expect_invalid(
        "workstream_not_balanced",
        unbalanced_inputs,
        labels,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    missing_coverage = copy.deepcopy(labels)
    for label in missing_coverage:
        label["error_tags"] = [
            tag for tag in label["error_tags"] if tag != "false_positive_gap"
        ] or ["correct_mapping"]
    expect_invalid(
        "required_failure_mode_missing",
        inputs,
        missing_coverage,
        validator,
        sources,
        profile,
        obligation_validator,
    )

    print(
        "baseline_dataset_validation_passed: "
        "24 cases, 20 required coverage tags and 12 prohibited states"
    )


if __name__ == "__main__":
    main()
