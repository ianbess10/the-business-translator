#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import load_settings
from src.runners.baseline import run_baseline


def main() -> int:
    parser = argparse.ArgumentParser(description="Run baseline prompt over synthetic test cases.")
    parser.add_argument(
        "--case-id",
        action="append",
        dest="case_ids",
        help="Optional case_id filter. Repeatable.",
    )
    args = parser.parse_args()

    settings = load_settings()
    result = run_baseline(settings, case_ids=args.case_ids)
    print(f"Baseline run complete: {result['run_dir']}")
    print(f"Cases: {result['meta']['case_count']} | provider={result['meta']['provider']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
