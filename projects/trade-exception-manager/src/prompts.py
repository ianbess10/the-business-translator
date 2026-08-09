from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.io_utils import read_text


def load_baseline_prompt(path: Path) -> str:
    return read_text(path).strip()


def load_engineered_prompt(path: Path) -> str:
    return read_text(path).strip()


def build_baseline_user_prompt(case: dict[str, Any], prompt_template: str) -> str:
    return (
        f"{prompt_template}\n\n"
        f"case_id: {case['case_id']}\n"
        f"Exception narrative:\n{case['message']}\n"
    )


def build_engineered_user_prompt(
    case: dict[str, Any],
    schema: dict[str, Any],
) -> str:
    reference = case.get("reference_data") or {}
    return (
        "Transform the following settlement-exception case into the required JSON object.\n"
        "Use only the supplied information. Do not invent facts.\n\n"
        f"case_id: {case['case_id']}\n"
        f"Exception narrative:\n{case['message']}\n\n"
        f"Reference data (JSON):\n{json.dumps(reference, ensure_ascii=False)}\n\n"
        "Return only valid JSON matching this schema:\n"
        f"{json.dumps(schema, ensure_ascii=False, indent=2)}\n"
    )
