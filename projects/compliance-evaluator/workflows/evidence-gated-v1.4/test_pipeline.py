#!/usr/bin/env python3
"""Compose all frozen paths through canonical evidence and retained policy."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


WORKFLOW_DIR = Path(__file__).resolve().parent
SOURCE_TEST = WORKFLOW_DIR.parent / "evidence-gated-v1.2" / "test_pipeline.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("retained_policy_tests", SOURCE_TEST)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load retained path fixtures")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = module.evidence_stage_for

    def canonical(case_id: str):
        item = original(case_id)
        return {"case_id": item["case_id"], "evidence_assessment": item["evidence_assessment"], "rationale": item["rationale"]}

    module.evidence_stage_for = canonical
    count = module.test_all_input_paths()
    print(f"evidence_gated_v1_4_pipeline_passed: {count} frozen input paths through canonical evidence")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
