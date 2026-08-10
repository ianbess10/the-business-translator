#!/usr/bin/env python3
"""Run the frozen regulatory-intelligence baseline exactly once.

This runner deliberately has no access to the evaluator-only label directory.
It verifies every frozen artefact before making one request per input case and
refuses to overwrite an existing run.
"""

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


BASELINE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASELINE_DIR.parent
DATASET_DIR = PROJECT_DIR / "datasets" / "baseline-v1.0"
RESULTS_DIR = PROJECT_DIR / "results" / "baseline-v1.0"
META_PATH = BASELINE_DIR / "baseline-v1.0.meta.json"
INPUT_PATHS = (
    DATASET_DIR / "inputs" / "aml-cft.json",
    DATASET_DIR / "inputs" / "market-conduct.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def verify_frozen_files(meta: dict[str, Any]) -> None:
    checks = {
        BASELINE_DIR / "baseline-prompt-v1.0.md": meta["prompt_sha256"],
        BASELINE_DIR / "baseline-prediction.schema.json": meta["prediction_schema_sha256"],
        BASELINE_DIR / "run_baseline.py": meta["runner_sha256"],
        BASELINE_DIR / "evaluate_baseline.py": meta["evaluator_sha256"],
        INPUT_PATHS[0]: meta["aml_cft_inputs_sha256"],
        INPUT_PATHS[1]: meta["market_conduct_inputs_sha256"],
    }
    mismatches = [
        f"{path}: expected {expected}, found {sha256_file(path)}"
        for path, expected in checks.items()
        if sha256_file(path) != expected
    ]
    if mismatches:
        raise RuntimeError("Frozen artefact verification failed:\n" + "\n".join(mismatches))


def usage_payload(usage: Any) -> dict[str, int | None]:
    if usage is None:
        return {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Verify frozen artefacts and runtime configuration without calling the API.",
    )
    args = parser.parse_args()

    meta = load_json(META_PATH)
    verify_frozen_files(meta)

    prompt_path = BASELINE_DIR / "baseline-prompt-v1.0.md"
    schema_path = BASELINE_DIR / "baseline-prediction.schema.json"
    prompt = prompt_path.read_text(encoding="utf-8")
    response_format = load_json(schema_path)
    prediction_validator = Draft202012Validator(response_format["schema"])

    inputs: list[dict[str, Any]] = []
    for path in INPUT_PATHS:
        inputs.extend(load_json(path))
    if len(inputs) != meta["case_count"]:
        raise RuntimeError(f"Expected {meta['case_count']} input cases; found {len(inputs)}")
    if len({case["case_id"] for case in inputs}) != len(inputs):
        raise RuntimeError("Duplicate case_id found in frozen inputs")

    if args.preflight:
        print(
            f"Preflight passed: {len(inputs)} frozen inputs, model {meta['model']}, "
            f"temperature {meta['temperature']}. No API call made."
        )
        return 0

    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required; no fallback or mock run is permitted")

    marker_path = RESULTS_DIR / "run-state.json"
    predictions_path = RESULTS_DIR / "predictions.json"
    if marker_path.exists() or predictions_path.exists():
        raise RuntimeError(
            "Baseline run already started or completed. Refusing to overwrite one-run evidence."
        )

    run_id = f"baseline-v1.0-{uuid.uuid4()}"
    run_state: dict[str, Any] = {
        "run_id": run_id,
        "status": "running",
        "started_at": utc_now(),
        "completed_at": None,
        "dataset_id": meta["dataset_id"],
        "dataset_version": meta["dataset_version"],
        "model": meta["model"],
        "temperature": meta["temperature"],
        "case_count": len(inputs),
        "completed_case_count": 0,
        "tuning_after_observation": False,
        "error": None,
    }
    write_json(marker_path, run_state)

    base_url = os.environ.get("OPENAI_BASE_URL", "").strip() or "https://api.openai.com/v1"
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=base_url)
    predictions: list[dict[str, Any]] = []

    try:
        for index, case in enumerate(inputs, start=1):
            request_started = time.monotonic()
            response = client.chat.completions.create(
                model=meta["model"],
                temperature=meta["temperature"],
                messages=[
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": "Assess this synthetic case:\n" + json.dumps(case, ensure_ascii=False),
                    },
                ],
                response_format={"type": "json_schema", "json_schema": response_format},
            )
            latency_ms = round((time.monotonic() - request_started) * 1000)
            message = response.choices[0].message
            refusal = getattr(message, "refusal", None)
            if refusal:
                raise RuntimeError(f"{case['case_id']} was refused: {refusal}")
            content = (message.content or "").strip()
            prediction = json.loads(content)
            prediction_validator.validate(prediction)

            predictions.append(
                {
                    "input_case_id": case["case_id"],
                    "workstream": case["workstream"],
                    "case_stage": case["case_stage"],
                    "prediction": prediction,
                    "response_id": response.id,
                    "response_model": response.model,
                    "finish_reason": response.choices[0].finish_reason,
                    "usage": usage_payload(response.usage),
                    "latency_ms": latency_ms,
                }
            )
            run_state["completed_case_count"] = index
            write_json(marker_path, run_state)
            print(f"[{index:02d}/{len(inputs)}] {case['case_id']} completed", flush=True)

        completed_at = utc_now()
        result = {
            "run_id": run_id,
            "status": "completed",
            "started_at": run_state["started_at"],
            "completed_at": completed_at,
            "dataset_id": meta["dataset_id"],
            "dataset_version": meta["dataset_version"],
            "provider": "openai",
            "model_requested": meta["model"],
            "temperature": meta["temperature"],
            "prompt_sha256": meta["prompt_sha256"],
            "prediction_schema_sha256": meta["prediction_schema_sha256"],
            "input_hashes": {
                "aml_cft": meta["aml_cft_inputs_sha256"],
                "market_conduct": meta["market_conduct_inputs_sha256"],
            },
            "run_attempt_count": 1,
            "tuning_after_observation": False,
            "predictions": predictions,
        }
        write_json(predictions_path, result)
        run_state.update(
            {"status": "completed", "completed_at": completed_at, "completed_case_count": len(inputs)}
        )
        write_json(marker_path, run_state)
        print(f"Completed one frozen baseline run: {predictions_path}")
        return 0
    except Exception as exc:
        run_state.update({"status": "failed", "completed_at": utc_now(), "error": str(exc)})
        if predictions:
            write_json(RESULTS_DIR / "partial-predictions.json", {"run_id": run_id, "predictions": predictions})
        write_json(marker_path, run_state)
        raise


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
