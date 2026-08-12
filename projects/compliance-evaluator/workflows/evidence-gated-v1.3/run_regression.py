#!/usr/bin/env python3
"""Run frozen Evidence-Gated Decision Pipeline v1.3 once after certification."""

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

from pipeline import compose_final_decision
from provider_contract import assert_provider_subset
from stage_validation import validate_evidence_stage, validate_mapping_stage, validate_source_stage


WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORKFLOW_DIR.parents[1]
V1_2_DIR = WORKFLOW_DIR.parent / "evidence-gated-v1.2"
V1_2_RUNNER_PATH = V1_2_DIR / "run_regression.py"
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"
RESULTS_DIR = PROJECT_DIR / "results" / "evidence-gated-v1.3"
META_PATH = WORKFLOW_DIR / "workflow-v1.3.meta.json"
CERTIFICATION_PATH = WORKFLOW_DIR / "certification" / "contract-certification-v1.3.json"
CERTIFICATION_PLAN_PATH = WORKFLOW_DIR / "certification" / "plan-v1.3.json"
SOURCE_PACK_PATH = PROJECT_DIR / "source-packs" / "source-pack-v1.0" / "manifest.json"
PROFILE_PATH = PROJECT_DIR / "profiles" / "synthetic-investment-wealth-institution-v1.0.json"
FINAL_SCHEMA_PATH = PROJECT_DIR / "baseline" / "baseline-prediction.schema.json"
INPUT_PATHS = (
    DATASET_DIR / "inputs" / "aml-cft.json",
    DATASET_DIR / "inputs" / "market-conduct.json",
)

_SPEC = importlib.util.spec_from_file_location("evidence_gated_v1_2_runner", V1_2_RUNNER_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("Could not load the frozen v1.2 runner utilities")
_V1_2 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_V1_2)

load_json = _V1_2.load_json
write_json = _V1_2.write_json
sha256_file = _V1_2.sha256_file
utc_now = _V1_2.utc_now
request_stage = _V1_2.request_stage
source_payload = _V1_2.source_payload
approved_obligation_core = _V1_2.approved_obligation_core
resolve_approved_obligation = _V1_2.resolve_approved_obligation
relevant_control_catalogue = _V1_2.relevant_control_catalogue
mapping_payload = _V1_2.mapping_payload
evidence_payload = _V1_2.evidence_payload


def verify_frozen_artefacts(meta: dict[str, Any]) -> None:
    mismatches: list[str] = []
    for relative_path, expected_hash in meta["artefact_sha256"].items():
        path = PROJECT_DIR / relative_path
        if not path.exists():
            mismatches.append(f"missing: {relative_path}")
        elif sha256_file(path) != expected_hash:
            mismatches.append(f"hash mismatch: {relative_path}")
    if mismatches:
        raise RuntimeError("Frozen v1.3 verification failed:\n" + "\n".join(mismatches))
    if meta.get("status") != "frozen_pre_regression":
        raise RuntimeError("Workflow metadata is not frozen for regression")
    if meta.get("regression_run_count") != 0:
        raise RuntimeError("Workflow metadata does not represent the pre-regression state")


def verify_certification(meta: dict[str, Any]) -> dict[str, Any]:
    evidence = load_json(CERTIFICATION_PATH)
    if evidence.get("status") != "completed":
        raise RuntimeError("Provider contract certification is not complete")
    if evidence.get("completed_call_count") != 3 or len(evidence.get("records", [])) != 3:
        raise RuntimeError("Provider contract certification does not contain three accepted calls")
    if evidence.get("model_requested") != meta["model"]:
        raise RuntimeError("Certification model does not match the frozen regression model")
    if evidence.get("endpoint") != meta["api"]:
        raise RuntimeError("Certification endpoint does not match the frozen regression endpoint")
    if sha256_file(CERTIFICATION_PATH) != meta["certification_evidence_sha256"]:
        raise RuntimeError("Certification evidence hash does not match frozen metadata")
    if sha256_file(CERTIFICATION_PLAN_PATH) != meta["certification_plan_sha256"]:
        raise RuntimeError("Certification plan hash does not match frozen metadata")
    schema_by_stage = {
        "source_support": WORKFLOW_DIR / "schemas" / "source-support-stage.schema.json",
        "mapping": WORKFLOW_DIR / "schemas" / "mapping-stage.schema.json",
        "evidence": WORKFLOW_DIR / "schemas" / "evidence-stage.schema.json",
    }
    prompt_by_stage = {
        "source_support": WORKFLOW_DIR / "prompts" / "source-support-stage-v1.3.md",
        "mapping": WORKFLOW_DIR / "prompts" / "mapping-stage-v1.3.md",
        "evidence": WORKFLOW_DIR / "prompts" / "evidence-stage-v1.3.md",
    }
    seen: set[str] = set()
    for record in evidence["records"]:
        stage = record.get("stage")
        if stage not in schema_by_stage or stage in seen:
            raise RuntimeError("Certification contains an unknown or duplicate stage")
        seen.add(stage)
        if record.get("provider_schema_accepted") is not True:
            raise RuntimeError(f"Provider did not accept the certified {stage} schema")
        if record.get("transport_output_valid") is not True or record.get("semantic_output_valid") is not True:
            raise RuntimeError(f"Certification validation did not pass for {stage}")
        if record.get("schema_sha256") != sha256_file(schema_by_stage[stage]):
            raise RuntimeError(f"Certified schema is stale for {stage}")
        if record.get("prompt_sha256") != sha256_file(prompt_by_stage[stage]):
            raise RuntimeError(f"Certified prompt is stale for {stage}")
        if record.get("response_model") != meta["model"]:
            raise RuntimeError(f"Provider response model differs for {stage}")
    if seen != set(schema_by_stage):
        raise RuntimeError("Certification stage coverage is incomplete")
    return evidence


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
    if len(inputs) != meta["case_count"] or len({item["case_id"] for item in inputs}) != len(inputs):
        raise RuntimeError("Frozen regression input count or identity changed")

    source_pack = load_json(SOURCE_PACK_PATH)
    source_records = {item["source_id"]: item for item in source_pack["sources"]}
    profile = load_json(PROFILE_PATH)
    source_policy = load_json(V1_2_DIR / "policies" / "source-transition-policy-v1.2.json")
    applicability_policy = load_json(V1_2_DIR / "policies" / "applicability-policy-v1.2.json")
    assurance_policy = load_json(V1_2_DIR / "policies" / "assurance-decision-policy-v1.2.json")
    escalation_policy = load_json(V1_2_DIR / "policies" / "escalation-policy-v1.2.json")
    if set(source_policy["sources"]) != set(source_records):
        raise RuntimeError("Source policy does not cover the frozen source pack exactly")

    prompt_paths = {
        "source_support": WORKFLOW_DIR / "prompts" / "source-support-stage-v1.3.md",
        "mapping": WORKFLOW_DIR / "prompts" / "mapping-stage-v1.3.md",
        "evidence": WORKFLOW_DIR / "prompts" / "evidence-stage-v1.3.md",
    }
    schema_paths = {
        "source_support": WORKFLOW_DIR / "schemas" / "source-support-stage.schema.json",
        "mapping": WORKFLOW_DIR / "schemas" / "mapping-stage.schema.json",
        "evidence": WORKFLOW_DIR / "schemas" / "evidence-stage.schema.json",
    }
    prompts = {stage: path.read_text(encoding="utf-8") for stage, path in prompt_paths.items()}
    formats = {stage: load_json(path) for stage, path in schema_paths.items()}
    for response_format in formats.values():
        assert_provider_subset(response_format)
    validators = {
        stage: Draft202012Validator(response_format["schema"])
        for stage, response_format in formats.items()
    }
    final_validator = Draft202012Validator(load_json(FINAL_SCHEMA_PATH)["schema"])

    entered_count = sum(
        item["upstream_obligation"]["supplied"] is True
        and item["upstream_obligation"]["status"] == "approved"
        for item in inputs
    )
    source_count = len(inputs) - entered_count
    expected_calls = source_count + (entered_count * 2)
    if (source_count, entered_count, expected_calls) != (
        meta["source_support_case_count"],
        meta["approved_assurance_case_count"],
        meta["expected_regression_api_call_count"],
    ):
        raise RuntimeError("Frozen stage or API-call count changed")

    for case in inputs:
        if case["upstream_obligation"]["supplied"] is True and case["upstream_obligation"]["status"] == "approved":
            record = resolve_approved_obligation(case)
            if record.get("obligation_id") != case["upstream_obligation"].get("obligation_id"):
                raise RuntimeError("Approved-obligation fixture ID does not match its case")
            mapping_payload(case, record, profile)

    if args.preflight:
        if RESULTS_DIR.exists():
            raise RuntimeError("v1.3 result directory already exists; regression boundary is not clear")
        print(
            f"Evidence-gated v1.3 preflight passed: 3/3 provider contracts certified, "
            f"{len(inputs)} cases and {expected_calls} future regression calls. No API call made."
        )
        return 0

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required; no mock or fallback is permitted")
    if RESULTS_DIR.exists():
        raise RuntimeError("v1.3 regression already started or completed; refusing to overwrite")

    marker_path = RESULTS_DIR / "run-state.json"
    predictions_path = RESULTS_DIR / "predictions.json"
    run_id = f"evidence-gated-v1.3-{uuid.uuid4()}"
    run_state: dict[str, Any] = {
        "run_id": run_id,
        "status": "running",
        "started_at": utc_now(),
        "completed_at": None,
        "dataset_id": meta["dataset_id"],
        "dataset_version": meta["dataset_version"],
        "workflow_id": meta["workflow_id"],
        "workflow_version": meta["version"],
        "model": meta["model"],
        "temperature": meta["temperature"],
        "case_count": len(inputs),
        "expected_api_call_count": expected_calls,
        "completed_api_call_count": 0,
        "completed_case_count": 0,
        "tuning_after_observation": False,
        "error": None,
    }
    write_json(marker_path, run_state)
    base_url = os.environ.get("OPENAI_BASE_URL", "").strip() or "https://api.openai.com/v1"
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=base_url)
    predictions: list[dict[str, Any]] = []
    completed_calls = 0
    try:
        for index, case in enumerate(inputs, start=1):
            entered = case["upstream_obligation"]["supplied"] is True and case["upstream_obligation"]["status"] == "approved"
            if entered:
                approved = resolve_approved_obligation(case)
                source_stage = source_api = None
                mapping_stage, mapping_api = request_stage(client, meta["model"], meta["temperature"], prompts["mapping"], formats["mapping"], mapping_payload(case, approved, profile))
                validators["mapping"].validate(mapping_stage)
                validate_mapping_stage(
                    mapping_stage,
                    case["case_id"],
                    case["proposed_mapping"]["control_ids"],
                    (item["control_id"] for item in profile["controls"]),
                )
                completed_calls += 1
                evidence_stage, evidence_api = request_stage(client, meta["model"], meta["temperature"], prompts["evidence"], formats["evidence"], evidence_payload(case, approved, mapping_stage, profile))
                validators["evidence"].validate(evidence_stage)
                validate_evidence_stage(evidence_stage, case["case_id"])
                completed_calls += 1
            else:
                approved = None
                source_stage, source_api = request_stage(client, meta["model"], meta["temperature"], prompts["source_support"], formats["source_support"], source_payload(case, source_records))
                validators["source_support"].validate(source_stage)
                validate_source_stage(source_stage, case["case_id"])
                completed_calls += 1
                mapping_stage = mapping_api = evidence_stage = evidence_api = None
            decision, trace = compose_final_decision(
                case,
                source_stage,
                mapping_stage,
                evidence_stage,
                approved,
                source_policy,
                applicability_policy,
                assurance_policy,
                escalation_policy,
                profile,
            )
            final_validator.validate(decision)
            predictions.append({
                "input_case_id": case["case_id"],
                "workstream": case["workstream"],
                "case_stage": case["case_stage"],
                "prediction": decision,
                "stage_outputs": {"source_support": source_stage, "mapping": mapping_stage, "evidence": evidence_stage, "approved_obligation_authority": approved},
                "policy_trace": trace,
                "reconciliation": {"passed": True, "manual_correction": False},
                "api": {"source_support": source_api, "mapping": mapping_api, "evidence": evidence_api},
            })
            run_state["completed_api_call_count"] = completed_calls
            run_state["completed_case_count"] = index
            write_json(marker_path, run_state)
            print(f"[{index:02d}/{len(inputs)}] {case['case_id']} completed ({completed_calls}/{expected_calls} calls)", flush=True)
        write_json(predictions_path, {
            "run_id": run_id,
            "status": "completed",
            "dataset_id": meta["dataset_id"],
            "dataset_version": meta["dataset_version"],
            "workflow_id": meta["workflow_id"],
            "workflow_version": meta["version"],
            "workflow_meta_sha256": sha256_file(META_PATH),
            "model_requested": meta["model"],
            "temperature": meta["temperature"],
            "run_attempt_count": 1,
            "api_call_count": completed_calls,
            "source_support_api_call_count": source_count,
            "mapping_api_call_count": entered_count,
            "evidence_api_call_count": entered_count,
            "tuning_after_observation": False,
            "predictions": predictions,
        })
        run_state["status"] = "completed"
        run_state["completed_at"] = utc_now()
        write_json(marker_path, run_state)
    except Exception as exc:
        run_state["status"] = "failed"
        run_state["completed_at"] = utc_now()
        run_state["completed_api_call_count"] = completed_calls
        run_state["error"] = f"{type(exc).__name__}: {exc}"
        write_json(marker_path, run_state)
        raise
    print(f"Completed one frozen evidence-gated v1.3 regression: {predictions_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
