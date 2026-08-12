#!/usr/bin/env python3
"""Offline mutation tests for the v1.3 provider-certification release gate."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import run_regression as runner


def expect_failure(meta: dict, evidence: dict | None, message: str) -> None:
    original = runner.CERTIFICATION_PATH
    try:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "certification.json"
            if evidence is not None:
                path.write_text(json.dumps(evidence), encoding="utf-8")
            runner.CERTIFICATION_PATH = path
            candidate_meta = copy.deepcopy(meta)
            if evidence is not None:
                candidate_meta["certification_evidence_sha256"] = runner.sha256_file(path)
            try:
                runner.verify_certification(candidate_meta)
            except (FileNotFoundError, RuntimeError) as exc:
                if message not in str(exc):
                    raise AssertionError(f"Expected {message!r}; found {exc}") from exc
                return
            raise AssertionError(f"Expected certification rejection: {message}")
    finally:
        runner.CERTIFICATION_PATH = original


def main() -> int:
    meta = runner.load_json(runner.META_PATH)
    valid = runner.verify_certification(meta)

    expect_failure(meta, None, "No such file")
    failed = copy.deepcopy(valid)
    failed["status"] = "failed"
    expect_failure(meta, failed, "not complete")
    incomplete = copy.deepcopy(valid)
    incomplete["completed_call_count"] = 2
    expect_failure(meta, incomplete, "three accepted calls")
    stale = copy.deepcopy(valid)
    stale["records"][0]["schema_sha256"] = "0" * 64
    expect_failure(meta, stale, "Certified schema is stale")
    wrong_model = copy.deepcopy(valid)
    wrong_model["model_requested"] = "different-model"
    expect_failure(meta, wrong_model, "model does not match")

    print("evidence_gated_v1_3_certification_gate_passed: valid plus 5 rejected release states")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
