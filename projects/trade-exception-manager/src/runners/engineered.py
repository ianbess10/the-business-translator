from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.config import Settings
from src.io_utils import load_jsonl, utc_run_id, write_json
from src.prompts import build_engineered_user_prompt, load_engineered_prompt
from src.providers import get_provider
from src.providers.base import GenerationRequest
from src.schema_validate import load_schema, parse_json_object, validate_engineered_output


def run_engineered(settings: Settings, case_ids: list[str] | None = None) -> dict[str, Any]:
    cases = load_jsonl(settings.test_set_path)
    if case_ids:
        wanted = set(case_ids)
        cases = [case for case in cases if case.get("case_id") in wanted]

    provider = get_provider(settings)
    system_prompt = load_engineered_prompt(settings.engineered_prompt_path)
    schema = load_schema(settings.schema_path)
    run_id = utc_run_id(settings.run_label)
    run_dir = settings.results_dir / "engineered" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    outputs: list[dict[str, Any]] = []
    for case in cases:
        request = GenerationRequest(
            system_prompt=system_prompt,
            user_prompt=build_engineered_user_prompt(case, schema),
            expect_json=True,
        )
        result = provider.generate(request)
        parsed, parse_error = parse_json_object(result.text)
        schema_errors: list[str] = []
        if parsed is None:
            schema_errors = [parse_error or "Unable to parse JSON object"]
        else:
            schema_errors = validate_engineered_output(parsed, schema)

        record = {
            "case_id": case["case_id"],
            "prompt_variant": "engineered",
            "provider": result.provider,
            "model": result.model,
            "input": {
                "message": case["message"],
                "expected_type": case.get("expected_type"),
                "expected_escalation": case.get("expected_escalation"),
                "expected_missing_information": case.get("expected_missing_information", []),
            },
            "output_text": result.text,
            "output_json": parsed,
            "schema_valid": len(schema_errors) == 0,
            "schema_errors": schema_errors,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        write_json(run_dir / f"{case['case_id']}.json", record)
        outputs.append(record)

    meta = {
        "run_id": run_id,
        "prompt_variant": "engineered",
        "prompt_version": settings.prompt_version,
        "prompt_file": str(settings.engineered_prompt_path.name),
        "provider": provider.name,
        "model": outputs[0]["model"] if outputs else None,
        "case_count": len(outputs),
        "schema": str(settings.schema_path.name),
        "test_set": str(settings.test_set_path.name),
        "test_set_id": settings.test_set_id,
        "test_set_version": settings.test_set_version,
        "schema_valid_count": sum(1 for item in outputs if item["schema_valid"]),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Synthetic test data only. Metrics require evaluate.py.",
    }
    write_json(run_dir / "meta.json", meta)
    return {"run_dir": str(run_dir), "meta": meta, "outputs": outputs}
