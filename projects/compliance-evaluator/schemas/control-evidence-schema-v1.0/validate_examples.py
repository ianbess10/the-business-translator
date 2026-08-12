#!/usr/bin/env python3
"""Validate connected control-and-evidence examples and operational guardrails."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:
    raise SystemExit(
        "Missing test dependency. Install it with: python3 -m pip install jsonschema"
    ) from exc


SCHEMA_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCHEMA_DIR.parents[1]
SCHEMA_PATH = SCHEMA_DIR / "control-evidence-assessment.schema.json"
OBLIGATION_SCHEMA_PATH = (
    SCHEMA_DIR.parent / "obligation-schema-v1.0" / "obligation-record.schema.json"
)
OBLIGATION_FIXTURE_PATH = SCHEMA_DIR / "fixtures" / "approved-obligation.json"
PROFILE_PATH = (
    PROJECT_DIR
    / "profiles"
    / "synthetic-investment-wealth-institution-v1.0.json"
)
SOURCE_MANIFEST_PATH = (
    PROJECT_DIR / "source-packs" / "source-pack-v1.0" / "manifest.json"
)
VALID_EXAMPLES = SCHEMA_DIR / "examples" / "valid"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_approved_obligation_fixture(
    obligation_validator: Draft202012Validator,
    obligation: dict,
    manifest: dict,
) -> None:
    obligation_validator.validate(obligation)
    if obligation["lifecycle_status"] != "approved":
        raise AssertionError("Upstream fixture is not an approved obligation")
    if obligation["human_review"]["status"] not in {"accepted", "amended"}:
        raise AssertionError("Upstream fixture lacks an accepted human decision")

    expected = {
        item["source_id"]: item for item in manifest["sources"]
    }[obligation["source"]["source_id"]]
    comparisons = {
        "source title": (obligation["source"]["source_title"], expected["title"]),
        "source status": (obligation["source"]["source_status"], expected["status"]),
        "instrument type": (
            obligation["source"]["instrument_type"],
            expected["instrument_type"],
        ),
        "source hash": (
            obligation["source"]["document_sha256"],
            expected["document_sha256"],
        ),
        "candidate gate": (
            obligation["source_gate"]["manifest_candidate_statement_extraction"],
            expected["candidate_statement_extraction"],
        ),
        "binding gate": (
            obligation["source_gate"]["manifest_binding_obligation_extraction"],
            expected["binding_obligation_extraction"],
        ),
    }
    mismatches = [
        f"{name}: fixture={actual!r}, manifest={wanted!r}"
        for name, (actual, wanted) in comparisons.items()
        if actual != wanted
    ]
    if mismatches:
        raise AssertionError("; ".join(mismatches))


def cross_record_errors(
    record: dict,
    obligation: dict,
    obligation_hash: str,
    profile: dict,
    profile_hash: str,
) -> list[str]:
    errors: list[str] = []
    reference = record["obligation_reference"]
    review = obligation["human_review"]

    obligation_comparisons = {
        "obligation hash": (
            reference["obligation_record_sha256"],
            obligation_hash,
        ),
        "obligation ID": (reference["obligation_id"], obligation["obligation_id"]),
        "source ID": (reference["source_id"], obligation["source"]["source_id"]),
        "atomic summary": (
            reference["atomic_summary"],
            obligation["obligation"]["atomic_summary"],
        ),
        "approver role": (reference["approved_by_role"], review["reviewer_role"]),
        "approver ID": (reference["approved_by_id"], review["reviewer_id"]),
        "approval time": (reference["approved_at"], review["reviewed_at"]),
    }
    errors.extend(
        f"{name} does not match the frozen approved obligation"
        for name, (actual, expected) in obligation_comparisons.items()
        if actual != expected
    )

    profile_reference = record["institution_profile"]
    profile_comparisons = {
        "profile ID": (profile_reference["profile_id"], profile["profile_id"]),
        "profile version": (profile_reference["profile_version"], profile["version"]),
        "profile hash": (profile_reference["profile_sha256"], profile_hash),
    }
    errors.extend(
        f"{name} does not match the frozen institution profile"
        for name, (actual, expected) in profile_comparisons.items()
        if actual != expected
    )

    process_ids = {item["process_id"] for item in profile["processes"]}
    for process_id in record["assessment_scope"]["in_scope_process_ids"]:
        if process_id not in process_ids:
            errors.append(f"unknown profile process: {process_id}")

    controls = {item["control_id"]: item for item in profile["controls"]}
    mapped_control_ids: set[str] = set()
    evidence_ref_ids: set[str] = set()

    for mapping in record["control_mappings"]:
        control_id = mapping["control_id"]
        if control_id in mapped_control_ids:
            errors.append(f"duplicate control mapping: {control_id}")
        mapped_control_ids.add(control_id)

        control = controls.get(control_id)
        if control is None:
            errors.append(f"unknown profile control: {control_id}")
        else:
            for field, profile_field in (
                ("control_name", "name"),
                ("catalog_owner_role", "owner_role"),
                ("control_type", "control_type"),
            ):
                if mapping[field] != control[profile_field]:
                    errors.append(
                        f"{control_id} {field} does not match the frozen profile"
                    )

        requirements = {
            item["evidence_requirement_id"]: item
            for item in mapping["expected_evidence"]
        }
        if len(requirements) != len(mapping["expected_evidence"]):
            errors.append(f"duplicate evidence requirement in {control_id}")

        supplied_by_requirement: dict[str, list[dict]] = {}
        for evidence in mapping["supplied_evidence"]:
            evidence_ref = evidence["evidence_ref_id"]
            if evidence_ref in evidence_ref_ids:
                errors.append(f"duplicate evidence reference: {evidence_ref}")
            evidence_ref_ids.add(evidence_ref)

            requirement_id = evidence["evidence_requirement_id"]
            requirement = requirements.get(requirement_id)
            if requirement is None:
                errors.append(
                    f"{evidence_ref} links to unknown requirement {requirement_id}"
                )
            else:
                supplied_by_requirement.setdefault(requirement_id, []).append(evidence)
                if evidence["evidence_type"] != requirement["evidence_type"]:
                    errors.append(
                        f"{evidence_ref} type does not match {requirement_id}"
                    )

            if evidence["status"] == "supplied":
                evidence_path = (
                    SCHEMA_DIR / evidence["location_or_reference"]
                ).resolve()
                if SCHEMA_DIR.resolve() not in evidence_path.parents:
                    errors.append(f"{evidence_ref} resolves outside the schema package")
                elif not evidence_path.is_file():
                    errors.append(f"{evidence_ref} file does not exist")
                elif sha256(evidence_path) != evidence["document_sha256"]:
                    errors.append(f"{evidence_ref} hash does not match its file")

        for requirement_id, requirement in requirements.items():
            linked = supplied_by_requirement.get(requirement_id, [])
            if requirement["mandatory"] and not linked:
                errors.append(f"mandatory requirement not represented: {requirement_id}")
            if mapping["evidence_assessment"]["status"] == "sufficient":
                if requirement["mandatory"] and not any(
                    item["status"] == "supplied" for item in linked
                ):
                    errors.append(
                        f"sufficient assessment lacks supplied mandatory evidence: "
                        f"{requirement_id}"
                    )

    gap_ids: set[str] = set()
    for gap in record["assurance_gaps"]:
        gap_id = gap["gap_id"]
        if gap_id in gap_ids:
            errors.append(f"duplicate assurance gap: {gap_id}")
        gap_ids.add(gap_id)
        for control_id in gap["affected_control_ids"]:
            if control_id not in mapped_control_ids:
                errors.append(
                    f"{gap_id} links to control not mapped in this record: {control_id}"
                )

    for action in record["remediation_actions"]:
        for gap_id in action["linked_gap_ids"]:
            if gap_id not in gap_ids:
                errors.append(
                    f"{action['action_id']} links to unknown gap {gap_id}"
                )
        for evidence_ref in action["closure_evidence_refs"]:
            if evidence_ref not in evidence_ref_ids:
                errors.append(
                    f"{action['action_id']} links to unknown closure evidence "
                    f"{evidence_ref}"
                )

    for evidence_ref in record["closure"]["closure_evidence_refs"]:
        if evidence_ref not in evidence_ref_ids:
            errors.append(f"closure links to unknown evidence {evidence_ref}")

    return errors


def record_errors(
    validator: Draft202012Validator,
    record: dict,
    obligation: dict,
    obligation_hash: str,
    profile: dict,
    profile_hash: str,
) -> list[str]:
    errors = [
        error.message
        for error in sorted(
            validator.iter_errors(record), key=lambda error: list(error.path)
        )
    ]
    errors.extend(
        cross_record_errors(
            record, obligation, obligation_hash, profile, profile_hash
        )
    )
    return errors


def expect_invalid(
    validator: Draft202012Validator,
    name: str,
    record: dict,
    obligation: dict,
    obligation_hash: str,
    profile: dict,
    profile_hash: str,
) -> None:
    errors = record_errors(
        validator, record, obligation, obligation_hash, profile, profile_hash
    )
    if not errors:
        raise AssertionError(f"Prohibited state unexpectedly validated: {name}")
    print(f"prohibited_state_rejected: {name}")


def main() -> None:
    schema = load_json(SCHEMA_PATH)
    obligation_schema = load_json(OBLIGATION_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(obligation_schema)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    obligation_validator = Draft202012Validator(
        obligation_schema, format_checker=FormatChecker()
    )
    obligation = load_json(OBLIGATION_FIXTURE_PATH)
    profile = load_json(PROFILE_PATH)
    manifest = load_json(SOURCE_MANIFEST_PATH)
    obligation_hash = sha256(OBLIGATION_FIXTURE_PATH)
    profile_hash = sha256(PROFILE_PATH)

    validate_approved_obligation_fixture(
        obligation_validator, obligation, manifest
    )
    print("approved_obligation_fixture_passed")

    examples: dict[str, dict] = {}
    for path in sorted(VALID_EXAMPLES.glob("*.json")):
        record = load_json(path)
        errors = record_errors(
            validator, record, obligation, obligation_hash, profile, profile_hash
        )
        if errors:
            raise AssertionError(f"{path.name}: {'; '.join(errors)}")
        examples[path.stem] = record
        print(f"valid_example_passed: {path.name}")

    unapproved_obligation = copy.deepcopy(examples["insufficient-evidence"])
    unapproved_obligation["obligation_reference"]["lifecycle_status"] = (
        "generated_candidate"
    )
    expect_invalid(
        validator,
        "unapproved_obligation_entered_assurance",
        unapproved_obligation,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    wrong_obligation_hash = copy.deepcopy(examples["insufficient-evidence"])
    wrong_obligation_hash["obligation_reference"]["obligation_record_sha256"] = (
        "0" * 64
    )
    expect_invalid(
        validator,
        "obligation_integrity_mismatch",
        wrong_obligation_hash,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    unknown_control = copy.deepcopy(examples["insufficient-evidence"])
    unknown_control["control_mappings"][0]["control_id"] = "C-CON-999"
    expect_invalid(
        validator,
        "unknown_control_mapping",
        unknown_control,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    wrong_owner = copy.deepcopy(examples["insufficient-evidence"])
    wrong_owner["control_mappings"][0]["catalog_owner_role"] = (
        "Conduct Risk Officer"
    )
    expect_invalid(
        validator,
        "incorrect_catalog_owner",
        wrong_owner,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    description_only = copy.deepcopy(examples["mapped-and-evidenced"])
    description_only["control_mappings"][0]["supplied_evidence"] = []
    expect_invalid(
        validator,
        "control_description_treated_as_evidence",
        description_only,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    missing_as_evidenced = copy.deepcopy(examples["insufficient-evidence"])
    missing_as_evidenced["assurance_assessment"]["outcome"] = (
        "mapped_and_evidenced"
    )
    missing_as_evidenced["assurance_gaps"] = []
    missing_as_evidenced["remediation_actions"] = []
    expect_invalid(
        validator,
        "missing_evidence_treated_as_sufficient",
        missing_as_evidenced,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    generated_self_approval = copy.deepcopy(examples["insufficient-evidence"])
    generated_self_approval["assurance_assessment"]["decision_status"] = "approved"
    generated_self_approval["human_review"] = copy.deepcopy(
        examples["mapped-and-evidenced"]["human_review"]
    )
    expect_invalid(
        validator,
        "generated_assessment_self_approved",
        generated_self_approval,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    reviewed_bypassed_approval = copy.deepcopy(examples["mapped-and-evidenced"])
    reviewed_bypassed_approval["lifecycle_status"] = "human_reviewed"
    expect_invalid(
        validator,
        "reviewed_record_bypassed_approval_lifecycle",
        reviewed_bypassed_approval,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    generated_confirmed_gap = copy.deepcopy(examples["potential-control-gap"])
    generated_confirmed_gap["assurance_gaps"][0]["status"] = "confirmed"
    expect_invalid(
        validator,
        "ai_generated_gap_marked_confirmed",
        generated_confirmed_gap,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    missed_material_escalation = copy.deepcopy(examples["potential-control-gap"])
    missed_material_escalation["remediation_actions"][0]["escalation"] = {
        "required": False,
        "route_to_role": None,
        "reason": None,
    }
    expect_invalid(
        validator,
        "high_severity_gap_not_escalated",
        missed_material_escalation,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    evidence_hash_mismatch = copy.deepcopy(examples["mapped-and-evidenced"])
    evidence_hash_mismatch["control_mappings"][0]["supplied_evidence"][0][
        "document_sha256"
    ] = "0" * 64
    expect_invalid(
        validator,
        "evidence_integrity_mismatch",
        evidence_hash_mismatch,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    unknown_gap_route = copy.deepcopy(examples["potential-control-gap"])
    unknown_gap_route["remediation_actions"][0]["linked_gap_ids"] = [
        "GAP-UNKNOWN-001"
    ]
    expect_invalid(
        validator,
        "remediation_linked_to_unknown_gap",
        unknown_gap_route,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    closure_without_authority = copy.deepcopy(examples["mapped-and-evidenced"])
    closure_without_authority["lifecycle_status"] = "closed"
    closure_without_authority["closure"]["status"] = "closed"
    expect_invalid(
        validator,
        "closure_without_authority_or_evidence",
        closure_without_authority,
        obligation,
        obligation_hash,
        profile,
        profile_hash,
    )

    print(
        "control_evidence_schema_validation_passed: "
        f"{len(examples)} valid examples and 13 prohibited states"
    )


if __name__ == "__main__":
    main()
