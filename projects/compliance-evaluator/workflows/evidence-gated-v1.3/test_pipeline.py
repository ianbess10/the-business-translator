#!/usr/bin/env python3
"""Run the retained v1.2 policy boundaries through the v1.3 semantic gate."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


WORKFLOW_DIR = Path(__file__).resolve().parent
SOURCE_TEST = WORKFLOW_DIR.parent / "evidence-gated-v1.2" / "test_pipeline.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("retained_v1_2_pipeline_tests", SOURCE_TEST)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the retained v1.2 boundary suite")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    path_count = module.test_all_input_paths()
    print(
        "evidence_gated_v1_3_pipeline_tests_passed: "
        f"{path_count} frozen input paths composed through the retained policy layer"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
