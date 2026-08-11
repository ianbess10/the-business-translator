#!/usr/bin/env python3
"""Certify the three exact v1.3 schemas with non-benchmark sentinel requests."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator
from openai import OpenAI

from provider_contract import assert_provider_subset
from stage_validation import (
    validate_evidence_stage,
    validate_mapping_stage,
    validate_source_stage,
)


WORKFLOW_DIR = Path(__file__).resolve().parent
PLAN_PATH = WORKFLOW_DIR / "certification" / "plan-v1.3.json"
EVIDENCE_PATH = WORKFLOW_DIR / "certification" / "contract-certification-v1.3.json"
MODEL = "gpt-4o-mini-2024-07-18"
TEMPERATURE = 0
EXPECTED_STAGE_COUNT = 3


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


def sha256_json(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def usage_payload(usage: Any) -> dict[str, int | None]:
    if usage is None:
        return {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }


def validate_semantics(stage: str, payload: dict[str, Any], expected: dict[str, Any]) -> None:
    case_id = expected["case_id"]
    if stage == "source_support":
        validate_source_stage(payload, case_id)
    elif stage == "mapping":
        validate_mapping_stage(payload, case_id, ["C-CERT-001"], ["C-CERT-001"])
    elif stage == "evidence":
        validate_evidence_stage(payload, case_id)
    else:
        raise ValueError(f"Unknown certification stage: {stage}")


def main() -> int:
    if EVIDENCE_PATH.exists():
        raise RuntimeError("v1.3 contract certification evidence already exists; refusing to overwrite")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required; no mock or fallback is permitted")
    plan = load_json(PLAN_PATH)
    stages = plan.get("stages", [])
    if len(stages) != EXPECTED_STAGE_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_STAGE_COUNT} certification stages")
    if plan.get("benchmark_cases_used") is not False or plan.get("evaluator_labels_used") is not False:
        raise RuntimeError("Certification plan does not preserve the non-benchmark boundary")
    if any(not item.get("case_id", "").startswith("CERT-") for item in stages):
        raise RuntimeError("Certification plan contains a non-sentinel case ID")

    base_url = os.environ.get("OPENAI_BASE_URL", "").strip() or "https://api.openai.com/v1"
    endpoint_host = urlparse(base_url).hostname or "unknown"
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=base_url)
    evidence: dict[str, Any] = {
        "certification_id": f"evidence-gated-v1.3-contract-{uuid.uuid4()}",
        "status": "running",
        "started_at": utc_now(),
        "completed_at": None,
        "purpose": plan["purpose"],
        "plan_sha256": sha256_file(PLAN_PATH),
        "provider": "openai",
        "endpoint": "chat_completions",
        "endpoint_host": endpoint_host,
        "model_requested": MODEL,
        "temperature": TEMPERATURE,
        "planned_call_count": EXPECTED_STAGE_COUNT,
        "completed_call_count": 0,
        "benchmark_cases_used": False,
        "evaluator_labels_used": False,
        "model_quality_scored": False,
        "records": [],
        "error": None,
    }
    write_json(EVIDENCE_PATH, evidence)

    try:
        for item in stages:
            prompt_path = WORKFLOW_DIR / item["prompt_path"]
            schema_path = WORKFLOW_DIR / item["schema_path"]
            prompt = prompt_path.read_text(encoding="utf-8")
            response_format = load_json(schema_path)
            assert_provider_subset(response_format)
            user_payload = {
                "certification_only": True,
                "benchmark_case": False,
                "instruction": "Return exactly the required semantic fixture so only the provider transport contract is being certified.",
                "input": item["input"],
                "required_semantic_fixture": item["expected_output"],
            }
            started = time.monotonic()
            response = client.chat.completions.create(
                model=MODEL,
                temperature=TEMPERATURE,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
                ],
                response_format={"type": "json_schema", "json_schema": response_format},
            )
            message = response.choices[0].message
            refusal = getattr(message, "refusal", None)
            if refusal:
                raise RuntimeError(f"Certification refusal for {item['stage']}: {refusal}")
            parsed = json.loads((message.content or "").strip())
            Draft202012Validator(response_format["schema"]).validate(parsed)
            validate_semantics(item["stage"], parsed, item["expected_output"])
            record = {
                "stage": item["stage"],
                "case_id": item["case_id"],
                "benchmark_case": False,
                "response_format_name": response_format["name"],
                "schema_sha256": sha256_file(schema_path),
                "prompt_sha256": sha256_file(prompt_path),
                "request_payload_sha256": sha256_json(user_payload),
                "response_id": response.id,
                "response_model": response.model,
                "finish_reason": response.choices[0].finish_reason,
                "provider_schema_accepted": True,
                "transport_output_valid": True,
                "semantic_output_valid": True,
                "output_sha256": sha256_json(parsed),
                "usage": usage_payload(response.usage),
                "latency_ms": round((time.monotonic() - started) * 1000),
                "certified_at": utc_now(),
            }
            evidence["records"].append(record)
            evidence["completed_call_count"] = len(evidence["records"])
            write_json(EVIDENCE_PATH, evidence)
            print(f"Certified {item['stage']} ({evidence['completed_call_count']}/3)", flush=True)
        evidence["status"] = "completed"
        evidence["completed_at"] = utc_now()
        write_json(EVIDENCE_PATH, evidence)
    except Exception as exc:
        evidence["status"] = "failed"
        evidence["completed_at"] = utc_now()
        evidence["error"] = f"{type(exc).__name__}: {exc}"
        write_json(EVIDENCE_PATH, evidence)
        raise

    print("v1.3 provider contract certification completed: 3/3 non-benchmark schemas accepted")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
