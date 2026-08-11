#!/usr/bin/env python3
"""Audit all v1.4 model-facing schemas and the changed-contract boundary."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from provider_contract import assert_provider_subset, provider_subset_errors


WORKFLOW_DIR = Path(__file__).resolve().parent


def main() -> int:
    schemas = []
    for path in sorted((WORKFLOW_DIR / "schemas").glob("*.json")):
        payload = json.loads(path.read_text())
        assert_provider_subset(payload)
        schemas.append(payload)
    evidence = next(item for item in schemas if item["name"] == "evidence_stage_v1_4")
    if set(evidence["schema"]["properties"]) != {"case_id", "evidence_assessment", "rationale"}:
        raise AssertionError("Evidence schema is not canonical")
    invalid = copy.deepcopy(evidence)
    invalid["schema"]["allOf"] = []
    errors = provider_subset_errors(invalid)
    if not any("allOf" in error for error in errors):
        raise AssertionError("Provider audit accepted prohibited composition")
    print("evidence_gated_v1_4_provider_subset_passed: 3 schemas, canonical changed contract and prohibited composition rejection")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
