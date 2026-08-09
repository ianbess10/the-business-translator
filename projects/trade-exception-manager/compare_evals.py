#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.compare import main


if __name__ == "__main__":
    # Default baseline is benchmarks/v4-reference.json; prefer the frozen release copy:
    #   --baseline releases/v4/evaluation/v4-reference.json
    raise SystemExit(main())
