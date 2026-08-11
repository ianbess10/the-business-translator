#!/usr/bin/env python3
"""Offline mutation tests for v1.4 changed and inherited certification gates."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import run_regression as runner


def main() -> int:
    meta = runner.load_json(runner.META_PATH)
    runner.verify_certification(meta)
    original = runner.CERTIFICATION_PATH
    evidence = runner.load_json(original)
    try:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            failed = copy.deepcopy(evidence)
            failed["status"] = "failed"
            path.write_text(json.dumps(failed))
            runner.CERTIFICATION_PATH = path
            candidate = copy.deepcopy(meta)
            candidate["evidence_certification_sha256"] = runner.sha256_file(path)
            try:
                runner.verify_certification(candidate)
            except RuntimeError as exc:
                if "incomplete" not in str(exc):
                    raise
            else:
                raise AssertionError("Failed changed-contract certification was accepted")
            stale = copy.deepcopy(evidence)
            stale["records"][0]["schema_sha256"] = "0" * 64
            path.write_text(json.dumps(stale))
            candidate["evidence_certification_sha256"] = runner.sha256_file(path)
            try:
                runner.verify_certification(candidate)
            except RuntimeError as exc:
                if "schema hash differs" not in str(exc):
                    raise
            else:
                raise AssertionError("Stale changed contract was accepted")
    finally:
        runner.CERTIFICATION_PATH = original
    print("evidence_gated_v1_4_certification_gate_passed: exact lineage plus failed and stale changed-contract rejection")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
