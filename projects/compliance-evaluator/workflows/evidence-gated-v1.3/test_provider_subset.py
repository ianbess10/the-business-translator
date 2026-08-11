#!/usr/bin/env python3
"""Prove all v1.3 response schemas use the conservative provider subset."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

from provider_contract import assert_provider_subset, provider_subset_errors


WORKFLOW_DIR = Path(__file__).resolve().parent
SCHEMA_DIR = WORKFLOW_DIR / "schemas"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def expect_failure(payload: dict[str, Any], expected_text: str) -> None:
    errors = provider_subset_errors(payload)
    if not any(expected_text in error for error in errors):
        raise AssertionError(f"Expected {expected_text!r}; found {errors}")


def mutated(payload: dict[str, Any], action: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    result = copy.deepcopy(payload)
    action(result)
    return result


def main() -> int:
    formats = {
        path.name: load_json(path) for path in sorted(SCHEMA_DIR.glob("*.json"))
    }
    if len(formats) != 3:
        raise AssertionError(f"Expected three response schemas; found {len(formats)}")
    for response_format in formats.values():
        assert_provider_subset(response_format)

    source = formats["source-support-stage.schema.json"]
    mapping = formats["mapping-stage.schema.json"]
    evidence = formats["evidence-stage.schema.json"]
    invalid: list[tuple[dict[str, Any], str]] = [
        (mutated(source, lambda item: item["schema"].update({"allOf": []})), ".allOf"),
        (mutated(source, lambda item: item["schema"]["properties"]["case_id"].update({"if": {}})), ".if"),
        (mutated(mapping, lambda item: item["schema"]["properties"]["current_mapping_control_ids"].update({"uniqueItems": True})), "uniqueItems"),
        (mutated(evidence, lambda item: item.update({"strict": False})), "strict"),
        (mutated(evidence, lambda item: item.update({"description": "extra"})), "wrapper keys"),
        (mutated(evidence, lambda item: item["schema"].pop("required")), ".required"),
        (mutated(evidence, lambda item: item["schema"]["required"].pop()), "must contain every property"),
        (mutated(evidence, lambda item: item["schema"].update({"additionalProperties": True})), "additionalProperties"),
        (mutated(mapping, lambda item: item["schema"]["properties"]["current_mapping_control_ids"].pop("items")), ".items"),
        (mutated(source, lambda item: item["schema"].update({"type": "string"})), "root must be object"),
        (mutated(source, lambda item: item["schema"]["required"].append("case_id")), "duplicate field names"),
        (mutated(mapping, lambda item: item["schema"]["properties"]["case_id"].update({"properties": {}})), "object-only keywords"),
    ]
    for payload, expected_text in invalid:
        expect_failure(payload, expected_text)
    print(
        "evidence_gated_v1_3_provider_subset_tests_passed: "
        f"{len(formats)} valid schemas and {len(invalid)} prohibited contract states"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
