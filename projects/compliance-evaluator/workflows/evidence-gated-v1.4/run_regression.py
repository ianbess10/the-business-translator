#!/usr/bin/env python3
"""Run frozen Evidence-Gated Decision Pipeline v1.4 once after certification."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from openai import OpenAI

from execution_contract import StageFailure, execute_stage, quarantine_record
from pipeline import compose_final_decision
from provider_contract import assert_provider_subset
from stage_validation import validate_evidence_stage, validate_mapping_stage, validate_source_stage


WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORKFLOW_DIR.parents[1]
V1_3_DIR = WORKFLOW_DIR.parent / "evidence-gated-v1.3"
V1_2_DIR = WORKFLOW_DIR.parent / "evidence-gated-v1.2"
SOURCE_RUNNER = V1_3_DIR / "run_regression.py"
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"
RESULTS_DIR = PROJECT_DIR / "results" / "evidence-gated-v1.4"
META_PATH = WORKFLOW_DIR / "workflow-v1.4.meta.json"
CERTIFICATION_PATH = WORKFLOW_DIR / "certification" / "contract-certification-v1.4.json"
CERTIFICATION_PLAN_PATH = WORKFLOW_DIR / "certification" / "plan-v1.4.json"
V1_3_CERTIFICATION_PATH = V1_3_DIR / "certification" / "contract-certification-v1.3.json"
SOURCE_PACK_PATH = PROJECT_DIR / "source-packs" / "source-pack-v1.0" / "manifest.json"
PROFILE_PATH = PROJECT_DIR / "profiles" / "synthetic-investment-wealth-institution-v1.0.json"
FINAL_SCHEMA_PATH = PROJECT_DIR / "baseline" / "baseline-prediction.schema.json"
INPUT_PATHS = (DATASET_DIR / "inputs" / "aml-cft.json", DATASET_DIR / "inputs" / "market-conduct.json")

SPEC = importlib.util.spec_from_file_location("evidence_gated_v1_3_runner_utilities", SOURCE_RUNNER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load the frozen v1.3 runner utilities")
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)

load_json = BASE.load_json
write_json = BASE.write_json
sha256_file = BASE.sha256_file
utc_now = BASE.utc_now
request_stage = BASE.request_stage
source_payload = BASE.source_payload
resolve_approved_obligation = BASE.resolve_approved_obligation
mapping_payload = BASE.mapping_payload
evidence_payload = BASE.evidence_payload


def verify_frozen_artefacts(meta: dict[str, Any]) -> None:
    mismatches = []
    for relative_path, expected in meta["artefact_sha256"].items():
        path = PROJECT_DIR / relative_path
        if not path.exists() or sha256_file(path) != expected:
            mismatches.append(relative_path)
    if mismatches:
        raise RuntimeError("Frozen v1.4 verification failed: " + ", ".join(mismatches))
    if meta.get("status") != "frozen_pre_regression" or meta.get("regression_run_count") != 0:
        raise RuntimeError("Workflow metadata is not the frozen zero-run state")


def verify_certification(meta: dict[str, Any]) -> None:
    current = load_json(CERTIFICATION_PATH)
    if current.get("status") != "completed" or current.get("completed_call_count") != 1:
        raise RuntimeError("Changed evidence contract certification is incomplete")
    if sha256_file(CERTIFICATION_PATH) != meta["evidence_certification_sha256"]:
        raise RuntimeError("v1.4 evidence certification is stale")
    if sha256_file(CERTIFICATION_PLAN_PATH) != meta["certification_plan_sha256"]:
        raise RuntimeError("v1.4 certification plan is stale")
    record = current["records"][0]
    if record.get("stage") != "evidence" or record.get("provider_schema_accepted") is not True:
        raise RuntimeError("Changed evidence contract was not accepted")
    if record.get("schema_sha256") != sha256_file(WORKFLOW_DIR / "schemas" / "evidence-stage.schema.json"):
        raise RuntimeError("Certified evidence schema hash differs")
    if record.get("prompt_sha256") != sha256_file(WORKFLOW_DIR / "prompts" / "evidence-stage-v1.4.md"):
        raise RuntimeError("Certified evidence prompt hash differs")
    if current.get("model_requested") != meta["model"] or current.get("endpoint") != meta["api"]:
        raise RuntimeError("Changed-contract certification provider configuration differs")

    lineage = load_json(V1_3_CERTIFICATION_PATH)
    if sha256_file(V1_3_CERTIFICATION_PATH) != meta["v1_3_certification_lineage_sha256"]:
        raise RuntimeError("v1.3 certification lineage is stale")
    records = {item["stage"]: item for item in lineage.get("records", [])}
    for stage, schema_name, prompt_name in (
        ("source_support", "source-support-stage.schema.json", "source-support-stage-v1.3.md"),
        ("mapping", "mapping-stage.schema.json", "mapping-stage-v1.3.md"),
    ):
        record = records.get(stage, {})
        if record.get("provider_schema_accepted") is not True:
            raise RuntimeError(f"Inherited {stage} contract was not certified")
        if record.get("schema_sha256") != sha256_file(WORKFLOW_DIR / "schemas" / schema_name):
            raise RuntimeError(f"Inherited {stage} schema changed")
        if record.get("prompt_sha256") != sha256_file(WORKFLOW_DIR / "prompts" / prompt_name):
            raise RuntimeError(f"Inherited {stage} prompt changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--preflight", action="store_true")
    action.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    meta = load_json(META_PATH)
    verify_frozen_artefacts(meta)
    verify_certification(meta)

    inputs: list[dict[str, Any]] = []
    for path in INPUT_PATHS:
        inputs.extend(load_json(path))
    if len(inputs) != 24 or len({item["case_id"] for item in inputs}) != 24:
        raise RuntimeError("Frozen regression input count or identity changed")
    entered_count = sum(item["upstream_obligation"]["supplied"] is True and item["upstream_obligation"]["status"] == "approved" for item in inputs)
    expected_calls = (len(inputs) - entered_count) + entered_count * 2
    if expected_calls != 32:
        raise RuntimeError("Frozen call topology changed")
    if args.preflight:
        if RESULTS_DIR.exists():
            raise RuntimeError("v1.4 result directory already exists")
        print("Evidence-gated v1.4 preflight passed: inherited contracts 2/2, changed contract 1/1, 24 cases and at most 32 calls. No API call made.")
        return 0
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required; no mock or fallback is permitted")
    if RESULTS_DIR.exists():
        raise RuntimeError("v1.4 regression already started or completed; refusing to overwrite")

    source_pack = load_json(SOURCE_PACK_PATH)
    source_records = {item["source_id"]: item for item in source_pack["sources"]}
    profile = load_json(PROFILE_PATH)
    policies = [
        load_json(V1_2_DIR / "policies" / name)
        for name in ("source-transition-policy-v1.2.json", "applicability-policy-v1.2.json", "assurance-decision-policy-v1.2.json", "escalation-policy-v1.2.json")
    ]
    prompt_paths = {
        "source_support": WORKFLOW_DIR / "prompts" / "source-support-stage-v1.3.md",
        "mapping": WORKFLOW_DIR / "prompts" / "mapping-stage-v1.3.md",
        "evidence": WORKFLOW_DIR / "prompts" / "evidence-stage-v1.4.md",
    }
    schema_paths = {stage: WORKFLOW_DIR / "schemas" / f"{name}-stage.schema.json" for stage, name in (("source_support", "source-support"), ("mapping", "mapping"), ("evidence", "evidence"))}
    prompts = {stage: path.read_text(encoding="utf-8") for stage, path in prompt_paths.items()}
    formats = {stage: load_json(path) for stage, path in schema_paths.items()}
    for item in formats.values():
        assert_provider_subset(item)
    validators = {stage: Draft202012Validator(item["schema"]) for stage, item in formats.items()}
    final_validator = Draft202012Validator(load_json(FINAL_SCHEMA_PATH)["schema"])

    run_id = f"evidence-gated-v1.4-{uuid.uuid4()}"
    state_path = RESULTS_DIR / "run-state.json"
    ledger_path = RESULTS_DIR / "stage-ledger.jsonl"
    predictions_path = RESULTS_DIR / "predictions.json"
    run_state = {
        "run_id": run_id, "status": "running", "started_at": utc_now(), "completed_at": None,
        "dataset_id": meta["dataset_id"], "dataset_version": meta["dataset_version"],
        "workflow_id": meta["workflow_id"], "workflow_version": meta["version"],
        "model": meta["model"], "temperature": meta["temperature"], "case_count": 24,
        "maximum_api_call_count": 32, "requested_api_call_count": 0,
        "semantically_valid_api_call_count": 0, "completed_case_count": 0,
        "quarantined_case_count": 0, "active_case_id": None, "active_stage": None,
        "tuning_after_observation": False, "retry_count": 0, "error": None,
    }
    write_json(state_path, run_state)
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.environ.get("OPENAI_BASE_URL", "").strip() or "https://api.openai.com/v1")
    predictions: list[dict[str, Any]] = []
    quarantines: list[dict[str, Any]] = []

    def stage_call(case: dict[str, Any], position: int, stage: str, payload: dict[str, Any], semantic) -> tuple[dict[str, Any], dict[str, Any]]:
        run_state["requested_api_call_count"] += 1
        ordinal = run_state["requested_api_call_count"]
        run_state["active_case_id"] = case["case_id"]
        run_state["active_stage"] = stage
        write_json(state_path, run_state)
        output = execute_stage(
            run_id=run_id, case_id=case["case_id"], execution_position=position, stage=stage,
            request_ordinal=ordinal,
            request=lambda: request_stage(client, meta["model"], meta["temperature"], prompts[stage], formats[stage], payload),
            transport_validate=validators[stage].validate, semantic_validate=semantic, ledger_path=ledger_path,
        )
        run_state["semantically_valid_api_call_count"] += 1
        write_json(state_path, run_state)
        return output

    try:
        for position, case in enumerate(inputs, start=1):
            try:
                entered = case["upstream_obligation"]["supplied"] is True and case["upstream_obligation"]["status"] == "approved"
                if entered:
                    approved = resolve_approved_obligation(case)
                    source_stage = source_api = None
                    mapping_stage, mapping_api = stage_call(case, position, "mapping", mapping_payload(case, approved, profile), lambda value: validate_mapping_stage(value, case["case_id"], case["proposed_mapping"]["control_ids"], (item["control_id"] for item in profile["controls"])))
                    evidence_stage, evidence_api = stage_call(case, position, "evidence", evidence_payload(case, approved, mapping_stage, profile), lambda value: validate_evidence_stage(value, case["case_id"]))
                else:
                    approved = None
                    source_stage, source_api = stage_call(case, position, "source_support", source_payload(case, source_records), lambda value: validate_source_stage(value, case["case_id"]))
                    mapping_stage = mapping_api = evidence_stage = evidence_api = None
                decision, trace = compose_final_decision(case, source_stage, mapping_stage, evidence_stage, approved, *policies, profile)
                final_validator.validate(decision)
                predictions.append({
                    "input_case_id": case["case_id"], "workstream": case["workstream"], "case_stage": case["case_stage"],
                    "terminal_status": "completed", "prediction": decision,
                    "stage_outputs": {"source_support": source_stage, "mapping": mapping_stage, "evidence": evidence_stage, "approved_obligation_authority": approved},
                    "policy_trace": trace, "reconciliation": {"passed": True, "manual_correction": False},
                    "api": {"source_support": source_api, "mapping": mapping_api, "evidence": evidence_api},
                })
                run_state["completed_case_count"] += 1
            except StageFailure as failure:
                quarantines.append(quarantine_record(case, position, failure))
                run_state["quarantined_case_count"] += 1
            run_state["active_case_id"] = None
            run_state["active_stage"] = None
            write_json(state_path, run_state)
            print(f"[{position:02d}/24] {case['case_id']} terminal: completed={run_state['completed_case_count']} quarantined={run_state['quarantined_case_count']}", flush=True)
        status = "completed_with_quarantine" if quarantines else "completed"
        write_json(predictions_path, {
            "run_id": run_id, "status": status, "dataset_id": meta["dataset_id"], "dataset_version": meta["dataset_version"],
            "workflow_id": meta["workflow_id"], "workflow_version": meta["version"], "workflow_meta_sha256": sha256_file(META_PATH),
            "model_requested": meta["model"], "temperature": meta["temperature"], "run_attempt_count": 1,
            "requested_api_call_count": run_state["requested_api_call_count"], "retry_count": 0,
            "tuning_after_observation": False, "case_count": 24, "predictions": predictions,
            "quarantines": quarantines,
        })
        run_state["status"] = status
        run_state["completed_at"] = utc_now()
        write_json(state_path, run_state)
    except Exception as exc:
        run_state["status"] = "failed_batch"
        run_state["completed_at"] = utc_now()
        run_state["error"] = f"{type(exc).__name__}: {exc}"
        write_json(state_path, run_state)
        raise
    print(f"Completed one frozen v1.4 regression batch: completed={len(predictions)}, quarantined={len(quarantines)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
