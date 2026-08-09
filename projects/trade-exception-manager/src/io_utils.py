from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} of {path}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"Expected object on line {line_number} of {path}")
            cases.append(payload)
    return cases


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def utc_run_id(label: str | None = None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if label:
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in label)
        return f"{stamp}_{safe}"
    return stamp


def newest_run_dir(parent: Path) -> Path | None:
    if not parent.exists():
        return None
    candidates = [path for path in parent.iterdir() if path.is_dir()]
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: path.name)[-1]


def list_case_result_files(run_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in run_dir.glob("*.json")
        if path.name != "meta.json" and not path.name.startswith("_")
    )


def chunked(items: Iterable[Any], size: int) -> list[list[Any]]:
    batch: list[Any] = []
    output: list[list[Any]] = []
    for item in items:
        batch.append(item)
        if len(batch) >= size:
            output.append(batch)
            batch = []
    if batch:
        output.append(batch)
    return output
