#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import load_settings
from src.runners.engineered import run_engineered


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run engineered prompt over synthetic test cases with JSON schema validation."
    )
    parser.add_argument(
        "--case-id",
        action="append",
        dest="case_ids",
        help="Optional case_id filter. Repeatable.",
    )
    parser.add_argument(
        "--prompt-version",
        choices=["v4", "v5"],
        help=(
            "Engineered prompt version to run. Default remains v4 "
            "(prompts/engineered-v4.md). v5 uses engineered-prompt-v5.md."
        ),
    )
    parser.add_argument(
        "--prompt-file",
        help="Optional explicit engineered prompt path (overrides --prompt-version mapping).",
    )
    args = parser.parse_args()

    # Selection only — does not alter V4 artefacts or default V4 behaviour.
    if args.prompt_version:
        os.environ["PROMPT_VERSION"] = args.prompt_version
    if args.prompt_file:
        os.environ["ENGINEERED_PROMPT_PATH"] = args.prompt_file

    settings = load_settings()
    result = run_engineered(settings, case_ids=args.case_ids)
    meta = result["meta"]
    print(f"Engineered run complete: {result['run_dir']}")
    print(
        f"Cases: {meta['case_count']} | schema_valid: {meta['schema_valid_count']} | "
        f"provider={meta['provider']} | prompt_version={meta.get('prompt_version')} | "
        f"prompt_file={meta.get('prompt_file')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
