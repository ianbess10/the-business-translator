#!/usr/bin/env python3
"""Offline stage-ledger and quarantine-continuation boundary tests."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from execution_contract import StageFailure, execute_stage, quarantine_record


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        ledger = Path(directory) / "ledger.jsonl"
        calls = 0

        def request_valid():
            nonlocal calls
            calls += 1
            return {"case_id": "GEN-001", "value": "valid"}, {"response_id": "offline-1"}

        execute_stage(
            run_id="offline", case_id="GEN-001", execution_position=1, stage="evidence",
            request_ordinal=1, request=request_valid, transport_validate=lambda value: None,
            semantic_validate=lambda value: None, ledger_path=ledger,
        )

        def semantic_invalid(value):
            raise ValueError("semantic contradiction")

        try:
            execute_stage(
                run_id="offline", case_id="GEN-002", execution_position=2, stage="evidence",
                request_ordinal=2,
                request=lambda: ({"case_id": "GEN-002", "value": "contradictory"}, {"response_id": "offline-2"}),
                transport_validate=lambda value: None, semantic_validate=semantic_invalid, ledger_path=ledger,
            )
        except StageFailure as failure:
            quarantined = quarantine_record({"case_id": "GEN-002", "workstream": "generic", "case_stage": "assurance"}, 2, failure)
        else:
            raise AssertionError("Semantic failure did not quarantine")

        execute_stage(
            run_id="offline", case_id="GEN-003", execution_position=3, stage="evidence",
            request_ordinal=3,
            request=lambda: ({"case_id": "GEN-003", "value": "valid"}, {"response_id": "offline-3"}),
            transport_validate=lambda value: None, semantic_validate=lambda value: None, ledger_path=ledger,
        )
        records = [json.loads(line) for line in ledger.read_text().splitlines()]
        if len(records) != 3 or records[1]["raw_parsed_response"]["value"] != "contradictory":
            raise AssertionError("Failed raw stage output was not checkpointed")
        if records[1]["semantic_valid"] is not False or records[2]["case_id"] != "GEN-003":
            raise AssertionError("Case quarantine did not preserve continuation")
        if quarantined["retry_count"] != 0 or quarantined["terminal_status"] != "quarantined":
            raise AssertionError("Quarantine terminal contract changed")
        if calls != 1:
            raise AssertionError("Offline request count changed unexpectedly")
    print("evidence_gated_v1_4_execution_contract_passed: append-before-block, zero retry, quarantine and continuation")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
