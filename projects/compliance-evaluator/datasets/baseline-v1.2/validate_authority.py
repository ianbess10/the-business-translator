#!/usr/bin/env python3
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = {f"CON-{n:03d}" for n in range(5, 13)}
VALID_COVERAGE = {"complete", "partial", "absent"}
VALID_EVIDENCE = {"sufficient", "missing_operating_evidence", "design_deficiency", "adverse_operating_evidence"}

def validate(payload):
    records = payload["records"]
    ids = [row["case_id"] for row in records]
    if len(records) != 8 or len(set(ids)) != 8 or set(ids) != EXPECTED:
        raise ValueError("Authority must contain exactly one record for every entered case")
    for row in records:
        if row["coverage_state"] not in VALID_COVERAGE or row["evidence_condition"] not in VALID_EVIDENCE:
            raise ValueError(f"Invalid dual-axis authority for {row['case_id']}")
        for key in ("gap_types", "remediation_action_types", "escalation_roles"):
            if len(row[key]) != len(set(row[key])):
                raise ValueError(f"Duplicate {key} for {row['case_id']}")
        if row["escalation_required"] != bool(row["escalation_roles"]):
            raise ValueError(f"Escalation identity mismatch for {row['case_id']}")
    return records

if __name__ == "__main__":
    payload = json.loads((HERE / "entered-assurance-authority.json").read_text())
    validate(payload)
    print("Benchmark authority v1.2 validation passed: 8/8 entered cases, complete dual-axis identity")
