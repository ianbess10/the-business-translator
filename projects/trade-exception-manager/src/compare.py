from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.config import PROJECT_ROOT

METRIC_KEYS = (
    "classification_accuracy",
    "json_schema_compliance",
    "missing_information_detection",
    "escalation_accuracy",
    "unsupported_claim_rate",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _metrics_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if "metrics" in payload:
        return payload["metrics"]
    variants = payload.get("variants") or {}
    engineered = variants.get("engineered") or {}
    summary = engineered.get("summary")
    if not summary:
        raise ValueError("Could not find engineered summary metrics in candidate report")
    return summary


def _identity(payload: dict[str, Any]) -> dict[str, str | None]:
    if "test_set_id" in payload or "prompt_version" in payload:
        return {
            "test_set_id": payload.get("test_set_id"),
            "prompt_version": payload.get("prompt_version"),
            "reference_id": payload.get("reference_id") or payload.get("evaluation_id"),
        }
    return {
        "test_set_id": payload.get("test_set_id"),
        "prompt_version": None,
        "reference_id": payload.get("evaluation_id"),
    }


def compare(baseline_path: Path, candidate_path: Path) -> dict[str, Any]:
    baseline = _load(baseline_path)
    candidate = _load(candidate_path)
    base_metrics = _metrics_from_payload(baseline)
    cand_metrics = _metrics_from_payload(candidate)

    deltas: dict[str, Any] = {}
    for key in METRIC_KEYS:
        left = base_metrics.get(key)
        right = cand_metrics.get(key)
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            deltas[key] = {
                "baseline": left,
                "candidate": right,
                "delta": right - left,
            }
        else:
            deltas[key] = {
                "baseline": left,
                "candidate": right,
                "delta": None,
            }

    base_id = _identity(baseline)
    cand_id = _identity(candidate)
    # Candidate evaluate.py reports may only carry test_set_id at top level;
    # older reports may omit it — infer from engineered run meta when present.
    if not cand_id.get("test_set_id"):
        eng_meta = ((candidate.get("variants") or {}).get("engineered") or {}).get("run_meta") or {}
        cand_id["test_set_id"] = eng_meta.get("test_set_id") or candidate.get("test_set")
        cand_id["prompt_version"] = cand_id.get("prompt_version") or eng_meta.get("prompt_version") or candidate.get("prompt_version")

    required = "trade-exception-test-set-v1.0"
    same_test_set = (
        base_id.get("test_set_id") == required
        and (
            cand_id.get("test_set_id") == required
            or cand_id.get("test_set_id") in {
                "trade-exception-test-set-v1.0.jsonl",
                "test-set.jsonl",  # compatibility alias used by the V4 source run
            }
        )
    )

    return {
        "baseline": {
            "path": str(baseline_path),
            **base_id,
        },
        "candidate": {
            "path": str(candidate_path),
            **cand_id,
        },
        "same_frozen_test_set": bool(same_test_set),
        "required_test_set_id": "trade-exception-test-set-v1.0",
        "deltas": deltas,
        "interpretation": (
            "Positive delta is improvement for accuracy/detection metrics; "
            "negative delta is improvement for unsupported_claim_rate."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare a candidate evaluation against a frozen prompt-version baseline "
            "on the same test set."
        )
    )
    parser.add_argument(
        "--baseline",
        default=str(PROJECT_ROOT / "releases" / "v4" / "evaluation" / "v4-reference.json"),
        help="Baseline reference JSON (default: releases/v4/evaluation/v4-reference.json).",
    )
    parser.add_argument(
        "--candidate",
        required=True,
        help="Candidate evaluate.py report JSON.",
    )
    parser.add_argument(
        "--out",
        help="Optional path to write the comparison JSON.",
    )
    args = parser.parse_args(argv)

    baseline_path = Path(args.baseline)
    candidate_path = Path(args.candidate)
    if not baseline_path.is_absolute():
        baseline_path = (PROJECT_ROOT / baseline_path).resolve()
    if not candidate_path.is_absolute():
        candidate_path = (PROJECT_ROOT / candidate_path).resolve()

    report = compare(baseline_path, candidate_path)
    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = (PROJECT_ROOT / out_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote comparison: {out_path}")

    print(
        f"baseline={report['baseline'].get('prompt_version') or report['baseline'].get('reference_id')} "
        f"candidate={report['candidate'].get('reference_id')}"
    )
    print(f"same_frozen_test_set={report['same_frozen_test_set']}")
    if not report["same_frozen_test_set"]:
        print(
            "WARNING: test_set_id mismatch or missing. "
            "Measured difference is only valid on trade-exception-test-set-v1.0."
        )
    for key, row in report["deltas"].items():
        delta = row["delta"]
        if delta is None:
            print(f"  {key}: n/a")
        else:
            print(
                f"  {key}: {row['baseline']:.3f} -> {row['candidate']:.3f} "
                f"(delta {delta:+.3f})"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
