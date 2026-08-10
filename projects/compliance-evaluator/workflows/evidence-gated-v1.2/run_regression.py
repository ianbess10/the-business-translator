#!/usr/bin/env python3
"""Run frozen Evidence-Gated Decision Pipeline v1.2 once against input-only cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from openai import OpenAI

from pipeline import compose_final_decision


WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_DIR = WORKFLOW_DIR.parents[1]
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"
RESULTS_DIR = PROJECT_DIR / "results" / "evidence-gated-v1.2"
META_PATH = WORKFLOW_DIR / "workflow-v1.2.meta.json"
SOURCE_PACK_PATH = PROJECT_DIR / "source-packs" / "source-pack-v1.0" / "manifest.json"
PROFILE_PATH = PROJECT_DIR / "profiles" / "synthetic-investment-wealth-institution-v1.0.json"
FINAL_SCHEMA_PATH = PROJECT_DIR / "baseline" / "baseline-prediction.schema.json"
INPUT_PATHS = (
    DATASET_DIR / "inputs" / "aml-cft.json",
    DATASET_DIR / "inputs" / "market-conduct.json",
)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def verify_frozen_artefacts(meta: dict[str, Any]) -> None:
    mismatches: list[str] = []
    for relative_path, expected_hash in meta["artefact_sha256"].items():
        artifact_path = PROJECT_DIR / relative_path
        if not artifact_path.exists():
            mismatches.append(f"missing: {relative_path}")
            continue
        actual_hash = sha256_file(artifact_path)
        if actual_hash != expected_hash:
            mismatches.append(
                f"{relative_path}: expected {expected_hash}, found {actual_hash}"
            )
    if mismatches:
        raise RuntimeError("Frozen workflow verification failed:\n" + "\n".join(mismatches))
    if meta["status"] != "frozen_pre_regression":
        raise RuntimeError("Workflow metadata is not frozen for regression")
    if meta["regression_run_count"] != 0:
        raise RuntimeError("Workflow metadata does not represent the pre-regression state")


def usage_payload(usage: Any) -> dict[str, int | None]:
    if usage is None:
        return {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }


def request_stage(
    client: OpenAI,
    model: str,
    temperature: float,
    prompt: str,
    response_format: dict[str, Any],
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    started = time.monotonic()
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        response_format={"type": "json_schema", "json_schema": response_format},
    )
    message = response.choices[0].message
    refusal = getattr(message, "refusal", None)
    if refusal:
        raise RuntimeError(f"Model refusal: {refusal}")
    stage_output = json.loads((message.content or "").strip())
    api_record = {
        "response_id": response.id,
        "response_model": response.model,
        "finish_reason": response.choices[0].finish_reason,
        "usage": usage_payload(response.usage),
        "latency_ms": round((time.monotonic() - started) * 1000),
    }
    return stage_output, api_record


def source_payload(
    case: dict[str, Any], source_records: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    permitted_source_fields = (
        "source_id",
        "domain",
        "issuing_authority",
        "title",
        "instrument_type",
        "status",
        "effective_date",
        "effective_date_note",
        "version_position",
        "candidate_statement_extraction",
        "binding_obligation_extraction",
        "permitted_use",
        "prohibited_use",
        "unresolved_issues",
    )
    records = []
    for source_id in case["source_ids"]:
        if source_id not in source_records:
            raise ValueError(f"Unknown source ID in frozen input: {source_id}")
        source = source_records[source_id]
        records.append({field: source.get(field) for field in permitted_source_fields})
    proposal = case["proposal_under_test"]
    return {
        "case_id": case["case_id"],
        "source_records": records,
        "source_excerpt_or_fact": case["source_excerpt_or_fact"],
        "institution_facts": case["institution_facts"],
        "missing_facts": case["missing_facts"],
        "candidate_statement": case["candidate_statement"],
        "proposal_under_test": {
            "source_use_disposition": proposal["source_use_disposition"],
            "obligation_outcome": proposal["obligation_outcome"],
            "applicability_status": proposal["applicability_status"],
        },
        "review_question": case["review_question"],
    }


def approved_obligation_core(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "obligation_id": record["obligation_id"],
        "lifecycle_status": record["lifecycle_status"],
        "source_id": record["source"]["source_id"],
        "atomic_summary": record["obligation"]["atomic_summary"],
        "applicability_status": record["applicability"]["status"],
        "human_review_status": record["human_review"]["status"],
    }


def resolve_approved_obligation(case: dict[str, Any]) -> dict[str, Any]:
    fixture_path = case["upstream_obligation"].get("fixture_path")
    if not fixture_path:
        raise ValueError("Approved assurance case has no obligation fixture path")
    resolved_path = (DATASET_DIR / fixture_path).resolve()
    if not resolved_path.is_relative_to(PROJECT_DIR.resolve()):
        raise ValueError("Approved-obligation fixture resolves outside the project")
    if not resolved_path.exists():
        raise FileNotFoundError(f"Approved-obligation fixture not found: {resolved_path}")
    return load_json(resolved_path)


def relevant_control_catalogue(
    case: dict[str, Any],
    approved_obligation: dict[str, Any],
    profile: dict[str, Any],
) -> list[dict[str, str]]:
    relevant_ids = set(case["proposed_mapping"]["control_ids"])
    relevant_ids.update(
        approved_obligation.get("operating_impact", {}).get("affected_control_ids", [])
    )
    catalogue = {item["control_id"]: item for item in profile["controls"]}
    unknown = sorted(relevant_ids - set(catalogue))
    if unknown:
        raise ValueError(f"Relevant control IDs are absent from the profile: {unknown}")
    return [
        {
            "control_id": control_id,
            "name": catalogue[control_id]["name"],
            "owner_role": catalogue[control_id]["owner_role"],
            "control_type": catalogue[control_id]["control_type"],
        }
        for control_id in sorted(relevant_ids)
    ]


def mapping_payload(
    case: dict[str, Any],
    approved_obligation: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    return {
        "case_id": case["case_id"],
        "approved_obligation": approved_obligation_core(approved_obligation),
        "proposed_mapping": case["proposed_mapping"],
        "relevant_control_catalogue": relevant_control_catalogue(
            case, approved_obligation, profile
        ),
    }


def evidence_payload(
    case: dict[str, Any],
    approved_obligation: dict[str, Any],
    mapping_stage: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    catalogue = {item["control_id"]: item for item in profile["controls"]}
    current_ids = mapping_stage["current_mapping_control_ids"]
    return {
        "case_id": case["case_id"],
        "approved_obligation": {
            **approved_obligation_core(approved_obligation),
            "evidence_or_reporting_requirements": approved_obligation["obligation"][
                "evidence_or_reporting_requirements"
            ],
        },
        "validated_current_mapping": {
            "control_ids": current_ids,
            "mapping_completeness": mapping_stage["mapping_completeness"],
            "uncovered_obligation_elements": mapping_stage[
                "uncovered_obligation_elements"
            ],
        },
        "current_control_catalogue": [
            {
                "control_id": control_id,
                "name": catalogue[control_id]["name"],
                "owner_role": catalogue[control_id]["owner_role"],
                "control_type": catalogue[control_id]["control_type"],
            }
            for control_id in current_ids
        ],
        "institution_facts": case["institution_facts"],
        "missing_facts": case["missing_facts"],
        "presented_evidence": case["presented_evidence"],
        "review_question": case["review_question"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--preflight",
        action="store_true",
        help="Verify the frozen workflow without making an API call.",
    )
    action.add_argument(
        "--execute",
        action="store_true",
        help="Execute the single frozen regression run.",
    )
    args = parser.parse_args()

    meta = load_json(META_PATH)
    verify_frozen_artefacts(meta)

    inputs: list[dict[str, Any]] = []
    for input_path in INPUT_PATHS:
        inputs.extend(load_json(input_path))
    if len(inputs) != meta["case_count"]:
        raise RuntimeError(f"Expected {meta['case_count']} inputs; found {len(inputs)}")
    if len({case["case_id"] for case in inputs}) != len(inputs):
        raise RuntimeError("Duplicate case ID in frozen regression inputs")

    source_pack = load_json(SOURCE_PACK_PATH)
    source_records = {item["source_id"]: item for item in source_pack["sources"]}
    profile = load_json(PROFILE_PATH)
    source_policy = load_json(
        WORKFLOW_DIR / "policies" / "source-transition-policy-v1.2.json"
    )
    applicability_policy = load_json(
        WORKFLOW_DIR / "policies" / "applicability-policy-v1.2.json"
    )
    assurance_policy = load_json(
        WORKFLOW_DIR / "policies" / "assurance-decision-policy-v1.2.json"
    )
    escalation_policy = load_json(
        WORKFLOW_DIR / "policies" / "escalation-policy-v1.2.json"
    )
    if set(source_policy["sources"]) != set(source_records):
        raise RuntimeError("Source policy does not cover the frozen source pack exactly")

    source_prompt = (WORKFLOW_DIR / "prompts" / "source-support-stage-v1.2.md").read_text(
        encoding="utf-8"
    )
    mapping_prompt = (WORKFLOW_DIR / "prompts" / "mapping-stage-v1.2.md").read_text(
        encoding="utf-8"
    )
    evidence_prompt = (WORKFLOW_DIR / "prompts" / "evidence-stage-v1.2.md").read_text(
        encoding="utf-8"
    )
    source_format = load_json(
        WORKFLOW_DIR / "schemas" / "source-support-stage.schema.json"
    )
    mapping_format = load_json(WORKFLOW_DIR / "schemas" / "mapping-stage.schema.json")
    evidence_format = load_json(WORKFLOW_DIR / "schemas" / "evidence-stage.schema.json")
    final_format = load_json(FINAL_SCHEMA_PATH)
    source_validator = Draft202012Validator(source_format["schema"])
    mapping_validator = Draft202012Validator(mapping_format["schema"])
    evidence_validator = Draft202012Validator(evidence_format["schema"])
    final_validator = Draft202012Validator(final_format["schema"])

    entered_count = sum(
        case["upstream_obligation"]["supplied"] is True
        and case["upstream_obligation"]["status"] == "approved"
        for case in inputs
    )
    source_count = len(inputs) - entered_count
    expected_calls = source_count + (entered_count * 2)
    if source_count != meta["source_support_case_count"]:
        raise RuntimeError("Source/support case count changed")
    if entered_count != meta["approved_assurance_case_count"]:
        raise RuntimeError("Approved-assurance case count changed")
    if expected_calls != meta["expected_api_call_count"]:
        raise RuntimeError("Expected API-call count changed")

    for case in inputs:
        if case["upstream_obligation"]["supplied"] is True and case[
            "upstream_obligation"
        ]["status"] == "approved":
            record = resolve_approved_obligation(case)
            if record.get("obligation_id") != case["upstream_obligation"].get(
                "obligation_id"
            ):
                raise RuntimeError("Approved-obligation fixture ID does not match its case")
            if record.get("lifecycle_status") != "approved":
                raise RuntimeError("Approved-obligation fixture is not approved")
            if record.get("human_review", {}).get("status") != "accepted":
                raise RuntimeError("Approved-obligation fixture lacks accepted human review")
            mapping_payload(case, record, profile)

    if args.preflight:
        if RESULTS_DIR.exists():
            raise RuntimeError(
                "Evidence-gated v1.2 result directory already exists; pre-regression boundary is not clear"
            )
        print(
            f"Evidence-gated v1.2 preflight passed: {len(inputs)} cases, "
            f"{source_count} source/support assessments, {entered_count} mapping assessments, "
            f"{entered_count} evidence assessments, {expected_calls} future API calls, "
            f"model {meta['model']}. No API call made."
        )
        return 0

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required; no mock or fallback run is permitted")

    marker_path = RESULTS_DIR / "run-state.json"
    predictions_path = RESULTS_DIR / "predictions.json"
    if marker_path.exists() or predictions_path.exists():
        raise RuntimeError(
            "Evidence-gated v1.2 regression already started or completed; refusing to overwrite it"
        )

    run_id = f"evidence-gated-v1.2-{uuid.uuid4()}"
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
    prediction_records: list[dict[str, Any]] = []
    completed_calls = 0

    try:
        for index, case in enumerate(inputs, start=1):
            assurance_entered = (
                case["upstream_obligation"]["supplied"] is True
                and case["upstream_obligation"]["status"] == "approved"
            )
            if assurance_entered:
                approved_obligation = resolve_approved_obligation(case)
                source_stage = None
                source_api = None
                mapping_stage, mapping_api = request_stage(
                    client,
                    meta["model"],
                    meta["temperature"],
                    mapping_prompt,
                    mapping_format,
                    mapping_payload(case, approved_obligation, profile),
                )
                mapping_validator.validate(mapping_stage)
                completed_calls += 1
                evidence_stage, evidence_api = request_stage(
                    client,
                    meta["model"],
                    meta["temperature"],
                    evidence_prompt,
                    evidence_format,
                    evidence_payload(case, approved_obligation, mapping_stage, profile),
                )
                evidence_validator.validate(evidence_stage)
                completed_calls += 1
            else:
                approved_obligation = None
                source_stage, source_api = request_stage(
                    client,
                    meta["model"],
                    meta["temperature"],
                    source_prompt,
                    source_format,
                    source_payload(case, source_records),
                )
                source_validator.validate(source_stage)
                completed_calls += 1
                mapping_stage = None
                mapping_api = None
                evidence_stage = None
                evidence_api = None

            final_decision, policy_trace = compose_final_decision(
                case,
                source_stage,
                mapping_stage,
                evidence_stage,
                approved_obligation,
                source_policy,
                applicability_policy,
                assurance_policy,
                escalation_policy,
                profile,
            )
            final_validator.validate(final_decision)
            prediction_records.append(
                {
                    "input_case_id": case["case_id"],
                    "workstream": case["workstream"],
                    "case_stage": case["case_stage"],
                    "prediction": final_decision,
                    "stage_outputs": {
                        "source_support": source_stage,
                        "mapping": mapping_stage,
                        "evidence": evidence_stage,
                        "approved_obligation_authority": approved_obligation,
                    },
                    "policy_trace": policy_trace,
                    "reconciliation": {"passed": True, "manual_correction": False},
                    "api": {
                        "source_support": source_api,
                        "mapping": mapping_api,
                        "evidence": evidence_api,
                    },
                }
            )
            run_state["completed_api_call_count"] = completed_calls
            run_state["completed_case_count"] = index
            write_json(marker_path, run_state)
            print(
                f"[{index:02d}/{len(inputs)}] {case['case_id']} completed "
                f"({completed_calls}/{expected_calls} calls)",
                flush=True,
            )

        predictions_payload = {
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
            "predictions": prediction_records,
        }
        write_json(predictions_path, predictions_payload)
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

    print(f"Completed one frozen evidence-gated v1.2 regression: {predictions_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
