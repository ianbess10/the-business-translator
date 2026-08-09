from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.config import load_settings
from src.io_utils import list_case_result_files, load_jsonl, newest_run_dir, utc_run_id, write_json
from src.schema_validate import load_schema, parse_json_object, validate_engineered_output

TOKEN_PATTERNS = [
    re.compile(r"\bTrade\s+\d+\b", re.IGNORECASE),
    re.compile(r"\bACCT-\d+\b", re.IGNORECASE),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"\bLEI[:\s-]?[A-Z0-9]{10,20}\b", re.IGNORECASE),
    re.compile(r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b"),  # BIC-like
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def missing_information_match(
    predicted: list[str],
    expected: list[str],
) -> dict[str, Any]:
    if not expected:
        # Vacuous success when no missing fields are required.
        return {
            "score": 1.0,
            "matched_expected": [],
            "unmatched_expected": [],
            "extra_predicted": predicted,
        }

    matched: list[str] = []
    unmatched: list[str] = []
    predicted_norm = [(_normalize(item), item) for item in predicted]

    for expected_item in expected:
        expected_norm = _normalize(expected_item)
        expected_tokens = _tokenize(expected_item)
        hit = False
        for pred_norm, _pred_raw in predicted_norm:
            if expected_norm in pred_norm or pred_norm in expected_norm:
                hit = True
                break
            pred_tokens = _tokenize(pred_norm)
            if expected_tokens and expected_tokens.issubset(pred_tokens):
                hit = True
                break
            # Partial conceptual overlap: majority token overlap
            if expected_tokens and len(expected_tokens & pred_tokens) / len(expected_tokens) >= 0.6:
                hit = True
                break
        if hit:
            matched.append(expected_item)
        else:
            unmatched.append(expected_item)

    score = len(matched) / len(expected)
    return {
        "score": score,
        "matched_expected": matched,
        "unmatched_expected": unmatched,
        "extra_predicted": predicted,
    }


def extract_claim_tokens(text: str) -> set[str]:
    found: set[str] = set()
    for pattern in TOKEN_PATTERNS:
        for match in pattern.findall(text):
            found.add(match if isinstance(match, str) else match[0])
    # Also catch invented account-like tokens used in the mock baseline.
    for match in re.findall(r"\b[A-Z]{2,5}-\d{4,}\b", text):
        found.add(match)
    return {_normalize(token) for token in found}


def unsupported_claim_flags(output_text: str, source_text: str) -> list[str]:
    source_norm = _normalize(source_text)
    flags: list[str] = []
    for token in sorted(extract_claim_tokens(output_text)):
        if token and token not in source_norm:
            flags.append(token)
    return flags


def load_run_records(run_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    meta_path = run_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    records: list[dict[str, Any]] = []
    for path in list_case_result_files(run_dir):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return meta, records


def evaluate_engineered_run(
    run_dir: Path,
    test_cases: list[dict[str, Any]],
    schema: dict[str, Any],
) -> dict[str, Any]:
    meta, records = load_run_records(run_dir)
    by_id = {case["case_id"]: case for case in test_cases}

    case_scores: list[dict[str, Any]] = []
    classification_hits = 0
    schema_hits = 0
    missing_score_total = 0.0
    escalation_hits = 0
    escalation_true_positives = 0
    escalation_false_positives = 0
    escalation_true_negatives = 0
    escalation_false_negatives = 0
    unsupported_total = 0

    for record in records:
        case_id = record["case_id"]
        gold = by_id.get(case_id, {})
        output_json = record.get("output_json")
        output_text = record.get("output_text") or ""

        if output_json is None:
            parsed, parse_error = parse_json_object(output_text)
            output_json = parsed
            schema_errors = [parse_error] if parse_error else validate_engineered_output(parsed or {}, schema)
        else:
            schema_errors = record.get("schema_errors")
            if schema_errors is None:
                schema_errors = validate_engineered_output(output_json, schema)

        schema_valid = len(schema_errors) == 0
        if schema_valid:
            schema_hits += 1

        predicted_type = (output_json or {}).get("exception_type")
        expected_type = gold.get("expected_type")
        classification_correct = predicted_type == expected_type
        if classification_correct:
            classification_hits += 1

        predicted_missing = list((output_json or {}).get("missing_information") or [])
        expected_missing = list(gold.get("expected_missing_information") or [])
        missing_eval = missing_information_match(predicted_missing, expected_missing)
        missing_score_total += missing_eval["score"]

        predicted_escalation = (output_json or {}).get("escalation_required")
        expected_escalation = gold.get("expected_escalation")
        escalation_correct = (
            isinstance(predicted_escalation, bool)
            and expected_escalation is not None
            and predicted_escalation == expected_escalation
        )
        if escalation_correct:
            escalation_hits += 1
        if isinstance(predicted_escalation, bool) and isinstance(
            expected_escalation, bool
        ):
            if predicted_escalation and expected_escalation:
                escalation_true_positives += 1
            elif predicted_escalation and not expected_escalation:
                escalation_false_positives += 1
            elif not predicted_escalation and not expected_escalation:
                escalation_true_negatives += 1
            else:
                escalation_false_negatives += 1

        source = " ".join(
            [
                gold.get("message") or record.get("input", {}).get("message") or "",
                json.dumps(gold.get("reference_data") or {}, ensure_ascii=False),
                case_id,
            ]
        )
        # Inspect all string fields in structured output plus raw text.
        claim_text_parts = [output_text]
        if isinstance(output_json, dict):
            for key in ("known_facts", "missing_information", "evidence", "recommended_next_action"):
                value = output_json.get(key)
                if isinstance(value, list):
                    claim_text_parts.extend(str(item) for item in value)
                elif value is not None:
                    claim_text_parts.append(str(value))
        flags = unsupported_claim_flags("\n".join(claim_text_parts), source)
        unsupported_total += len(flags)

        case_scores.append(
            {
                "case_id": case_id,
                "classification_correct": classification_correct,
                "predicted_type": predicted_type,
                "expected_type": expected_type,
                "schema_valid": schema_valid,
                "schema_errors": schema_errors,
                "missing_information_score": missing_eval["score"],
                "missing_information_detail": missing_eval,
                "escalation_correct": escalation_correct,
                "predicted_escalation": predicted_escalation,
                "expected_escalation": expected_escalation,
                "unsupported_claim_flags": flags,
                "unsupported_claim_count": len(flags),
            }
        )

    n = len(case_scores) or 1
    escalation_precision_denominator = (
        escalation_true_positives + escalation_false_positives
    )
    escalation_recall_denominator = (
        escalation_true_positives + escalation_false_negatives
    )
    summary = {
        "case_count": len(case_scores),
        "classification_accuracy": classification_hits / n if case_scores else 0.0,
        "json_schema_compliance": schema_hits / n if case_scores else 0.0,
        "missing_information_detection": missing_score_total / n if case_scores else 0.0,
        "escalation_accuracy": escalation_hits / n if case_scores else 0.0,
        "escalation_precision": (
            escalation_true_positives / escalation_precision_denominator
            if escalation_precision_denominator
            else None
        ),
        "escalation_recall": (
            escalation_true_positives / escalation_recall_denominator
            if escalation_recall_denominator
            else None
        ),
        "escalation_true_positives": escalation_true_positives,
        "escalation_false_positives": escalation_false_positives,
        "escalation_true_negatives": escalation_true_negatives,
        "escalation_false_negatives": escalation_false_negatives,
        "unsupported_claim_flags_total": unsupported_total,
        "unsupported_claim_rate": unsupported_total / n if case_scores else 0.0,
    }

    return {
        "prompt_variant": "engineered",
        "run_dir": str(run_dir),
        "run_meta": meta,
        "summary": summary,
        "cases": case_scores,
    }


def evaluate_baseline_run(
    run_dir: Path,
    test_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    """Baseline outputs are free text; score only unsupported-claim flags and presence."""
    meta, records = load_run_records(run_dir)
    by_id = {case["case_id"]: case for case in test_cases}
    case_scores: list[dict[str, Any]] = []
    unsupported_total = 0

    for record in records:
        case_id = record["case_id"]
        gold = by_id.get(case_id, {})
        output_text = record.get("output_text") or ""
        source = " ".join(
            [
                gold.get("message") or record.get("input", {}).get("message") or "",
                case_id,
            ]
        )
        flags = unsupported_claim_flags(output_text, source)
        unsupported_total += len(flags)
        case_scores.append(
            {
                "case_id": case_id,
                "schema_valid": False,
                "classification_correct": None,
                "missing_information_score": None,
                "escalation_correct": None,
                "unsupported_claim_flags": flags,
                "unsupported_claim_count": len(flags),
                "notes": "Baseline is free text; structured metrics apply to engineered runs.",
            }
        )

    n = len(case_scores) or 1
    return {
        "prompt_variant": "baseline",
        "run_dir": str(run_dir),
        "run_meta": meta,
        "summary": {
            "case_count": len(case_scores),
            "classification_accuracy": None,
            "json_schema_compliance": 0.0,
            "missing_information_detection": None,
            "escalation_accuracy": None,
            "escalation_precision": None,
            "escalation_recall": None,
            "escalation_true_positives": None,
            "escalation_false_positives": None,
            "escalation_true_negatives": None,
            "escalation_false_negatives": None,
            "unsupported_claim_flags_total": unsupported_total,
            "unsupported_claim_rate": unsupported_total / n if case_scores else 0.0,
        },
        "cases": case_scores,
    }


def resolve_run_dir(results_dir: Path, variant: str, run_dir: str | None) -> Path:
    if run_dir:
        path = Path(run_dir)
        if not path.is_absolute():
            path = (results_dir / variant / run_dir).resolve()
            if not path.exists():
                path = Path(run_dir).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Run directory not found: {run_dir}")
        return path

    latest = newest_run_dir(results_dir / variant)
    if latest is None:
        raise FileNotFoundError(
            f"No {variant} runs found under {results_dir / variant}. "
            f"Run run_{variant}.py first."
        )
    return latest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate Trade Exception Intelligence model outputs."
    )
    parser.add_argument(
        "--variant",
        choices=["engineered", "baseline", "both"],
        default="engineered",
        help="Which result set to evaluate (default: engineered).",
    )
    parser.add_argument(
        "--run-dir",
        help="Specific run directory or run_id under results/<variant>/.",
    )
    parser.add_argument(
        "--baseline-run-dir",
        help="Optional baseline run directory when --variant both.",
    )
    parser.add_argument(
        "--engineered-run-dir",
        help="Optional engineered run directory when --variant both.",
    )
    args = parser.parse_args(argv)

    settings = load_settings()
    test_cases = load_jsonl(settings.test_set_path)
    schema = load_schema(settings.schema_path)
    eval_id = utc_run_id(settings.run_label)
    reports: dict[str, Any] = {
        "evaluation_id": eval_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "test_set": settings.test_set_path.name,
        "test_set_id": settings.test_set_id,
        "test_set_version": settings.test_set_version,
        "prompt_version": settings.prompt_version,
        "data_policy": "synthetic examples only",
        "disclaimer": (
            "These metrics were generated from a local evaluation run. "
            "Do not substitute illustrative portfolio figures for this report."
        ),
        "variants": {},
    }

    if args.variant in {"engineered", "both"}:
        engineered_dir = resolve_run_dir(
            settings.results_dir,
            "engineered",
            args.engineered_run_dir or (args.run_dir if args.variant == "engineered" else None),
        )
        reports["variants"]["engineered"] = evaluate_engineered_run(
            engineered_dir, test_cases, schema
        )

    if args.variant in {"baseline", "both"}:
        baseline_dir = resolve_run_dir(
            settings.results_dir,
            "baseline",
            args.baseline_run_dir or (args.run_dir if args.variant == "baseline" else None),
        )
        reports["variants"]["baseline"] = evaluate_baseline_run(baseline_dir, test_cases)

    out_path = settings.results_dir / "evaluation" / f"{eval_id}.json"
    write_json(out_path, reports)

    print(f"Wrote evaluation report: {out_path}")
    for variant, report in reports["variants"].items():
        summary = report["summary"]
        print(f"\n[{variant}] cases={summary['case_count']}")
        for key in (
            "classification_accuracy",
            "json_schema_compliance",
            "missing_information_detection",
            "escalation_accuracy",
            "escalation_precision",
            "escalation_recall",
            "escalation_true_positives",
            "escalation_false_positives",
            "escalation_true_negatives",
            "escalation_false_negatives",
            "unsupported_claim_flags_total",
            "unsupported_claim_rate",
        ):
            value = summary.get(key)
            if value is None:
                print(f"  {key}: n/a")
            elif isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
