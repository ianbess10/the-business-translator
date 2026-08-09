#!/usr/bin/env python3
"""Validate obligation-schema examples and prohibited-state controls."""

from __future__ import annotations

import copy
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
SCHEMA_PATH = SCHEMA_DIR / "obligation-record.schema.json"
VALID_EXAMPLES = SCHEMA_DIR / "examples" / "valid"
SOURCE_MANIFEST = (
    PROJECT_DIR / "source-packs" / "source-pack-v1.0" / "manifest.json"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_source_manifest_alignment(record: dict, manifest_by_id: dict) -> None:
    source = record["source"]
    gate = record["source_gate"]
    expected = manifest_by_id[source["source_id"]]

    comparisons = {
        "source title": (source["source_title"], expected["title"]),
        "source status": (source["source_status"], expected["status"]),
        "instrument type": (source["instrument_type"], expected["instrument_type"]),
        "document hash": (source["document_sha256"], expected["document_sha256"]),
        "candidate extraction gate": (
            gate["manifest_candidate_statement_extraction"],
            expected["candidate_statement_extraction"],
        ),
        "binding extraction gate": (
            gate["manifest_binding_obligation_extraction"],
            expected["binding_obligation_extraction"],
        ),
    }

    mismatches = [
        f"{name}: record={actual!r}, manifest={wanted!r}"
        for name, (actual, wanted) in comparisons.items()
        if actual != wanted
    ]
    if mismatches:
        raise AssertionError("; ".join(mismatches))


def expect_invalid(validator: Draft202012Validator, name: str, record: dict) -> None:
    errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
    if not errors:
        raise AssertionError(f"Prohibited state unexpectedly validated: {name}")
    print(f"prohibited_state_rejected: {name}")


def main() -> None:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    manifest = load_json(SOURCE_MANIFEST)
    manifest_by_id = {source["source_id"]: source for source in manifest["sources"]}

    examples = {}
    for path in sorted(VALID_EXAMPLES.glob("*.json")):
        record = load_json(path)
        validator.validate(record)
        assert_source_manifest_alignment(record, manifest_by_id)
        examples[path.stem] = record
        print(f"valid_example_passed: {path.name}")

    draft_as_in_force = copy.deepcopy(examples["draft-watchlist"])
    draft_as_in_force["classification"].update(
        {
            "normative_strength": "binding_candidate",
            "legal_effect": "in_force",
            "source_use_disposition": "binding_candidate",
            "effective_from": "2026-08-03",
        }
    )
    draft_as_in_force["source_gate"]["record_use"] = "binding_candidate"
    draft_as_in_force["assessment"]["outcome"] = "candidate_binding_obligation"
    expect_invalid(validator, "draft_classified_as_in_force", draft_as_in_force)

    blocked_source_as_binding = copy.deepcopy(examples["binding-candidate"])
    blocked_source_as_binding["source_gate"][
        "manifest_binding_obligation_extraction"
    ] = "blocked"
    expect_invalid(validator, "blocked_source_as_binding", blocked_source_as_binding)

    applicability_without_resolution = copy.deepcopy(examples["binding-candidate"])
    applicability_without_resolution["applicability"]["missing_facts"] = [
        "unresolved licence permission"
    ]
    expect_invalid(
        validator,
        "applicable_candidate_with_missing_facts",
        applicability_without_resolution,
    )

    approval_without_reviewer = copy.deepcopy(examples["binding-candidate"])
    approval_without_reviewer["lifecycle_status"] = "approved"
    expect_invalid(validator, "approval_without_human_review", approval_without_reviewer)

    unsupported_as_binding = copy.deepcopy(examples["binding-candidate"])
    unsupported_as_binding["obligation"]["support_status"] = "unsupported"
    expect_invalid(validator, "unsupported_statement_as_binding", unsupported_as_binding)

    missing_locator = copy.deepcopy(examples["binding-candidate"])
    missing_locator["source"]["locator"].update(
        {"page_label": None, "section": None, "clause": None, "paragraph": None}
    )
    expect_invalid(validator, "record_without_precise_locator", missing_locator)

    print(
        f"obligation_schema_validation_passed: "
        f"{len(examples)} valid examples and 6 prohibited states"
    )


if __name__ == "__main__":
    main()
