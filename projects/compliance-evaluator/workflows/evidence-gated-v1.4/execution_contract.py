"""Append-only stage evidence and fail-closed case quarantine for v1.4."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


class StageFailure(RuntimeError):
    def __init__(self, case_id: str, stage: str, failure_type: str, message: str) -> None:
        super().__init__(message)
        self.case_id = case_id
        self.stage = stage
        self.failure_type = failure_type


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_stage_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def execute_stage(
    *, run_id: str, case_id: str, execution_position: int, stage: str,
    request_ordinal: int, request: Callable[[], tuple[dict[str, Any], dict[str, Any]]],
    transport_validate: Callable[[dict[str, Any]], None],
    semantic_validate: Callable[[dict[str, Any]], None], ledger_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    parsed: dict[str, Any] | None = None
    api: dict[str, Any] | None = None
    try:
        parsed, api = request()
        transport_validate(parsed)
    except Exception as exc:
        append_stage_record(ledger_path, {
            "run_id": run_id, "case_id": case_id, "execution_position": execution_position,
            "stage": stage, "request_ordinal": request_ordinal, "recorded_at": utc_now(),
            "retry_count": 0, "raw_parsed_response": parsed, "provider_metadata": api,
            "transport_valid": False, "semantic_valid": False, "composition_status": "blocked",
            "failure_type": "provider_or_transport_failure", "error": f"{type(exc).__name__}: {exc}",
        })
        raise StageFailure(case_id, stage, "provider_or_transport_failure", str(exc)) from exc
    try:
        semantic_validate(parsed)
    except Exception as exc:
        append_stage_record(ledger_path, {
            "run_id": run_id, "case_id": case_id, "execution_position": execution_position,
            "stage": stage, "request_ordinal": request_ordinal, "recorded_at": utc_now(),
            "retry_count": 0, "raw_parsed_response": parsed, "provider_metadata": api,
            "transport_valid": True, "semantic_valid": False, "composition_status": "blocked",
            "failure_type": "semantic_failure", "error": f"{type(exc).__name__}: {exc}",
        })
        raise StageFailure(case_id, stage, "semantic_failure", str(exc)) from exc
    append_stage_record(ledger_path, {
        "run_id": run_id, "case_id": case_id, "execution_position": execution_position,
        "stage": stage, "request_ordinal": request_ordinal, "recorded_at": utc_now(),
        "retry_count": 0, "raw_parsed_response": parsed, "provider_metadata": api,
        "transport_valid": True, "semantic_valid": True, "composition_status": "eligible",
        "failure_type": None, "error": None,
    })
    return parsed, api


def quarantine_record(case: dict[str, Any], position: int, failure: StageFailure) -> dict[str, Any]:
    return {
        "input_case_id": case["case_id"],
        "workstream": case["workstream"],
        "case_stage": case["case_stage"],
        "execution_position": position,
        "terminal_status": "quarantined",
        "failed_stage": failure.stage,
        "failure_type": failure.failure_type,
        "error": str(failure),
        "retry_count": 0,
        "policy_composition_performed": False,
        "mandatory_human_review": True,
    }
