from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.config import Settings
from src.io_utils import load_jsonl, utc_run_id, write_json
from src.prompts import build_baseline_user_prompt, load_baseline_prompt
from src.providers import get_provider
from src.providers.base import GenerationRequest


def run_baseline(settings: Settings, case_ids: list[str] | None = None) -> dict[str, Any]:
    cases = load_jsonl(settings.test_set_path)
    if case_ids:
        wanted = set(case_ids)
        cases = [case for case in cases if case.get("case_id") in wanted]

    provider = get_provider(settings)
    prompt_template = load_baseline_prompt(settings.baseline_prompt_path)
    run_id = utc_run_id(settings.run_label)
    run_dir = settings.results_dir / "baseline" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    outputs: list[dict[str, Any]] = []
    for case in cases:
        request = GenerationRequest(
            system_prompt=None,
            user_prompt=build_baseline_user_prompt(case, prompt_template),
            expect_json=False,
        )
        result = provider.generate(request)
        record = {
            "case_id": case["case_id"],
            "prompt_variant": "baseline",
            "provider": result.provider,
            "model": result.model,
            "input": {
                "message": case["message"],
                "expected_type": case.get("expected_type"),
            },
            "output_text": result.text,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        write_json(run_dir / f"{case['case_id']}.json", record)
        outputs.append(record)

    meta = {
        "run_id": run_id,
        "prompt_variant": "baseline",
        "provider": provider.name,
        "model": outputs[0]["model"] if outputs else None,
        "case_count": len(outputs),
        "test_set": str(settings.test_set_path.name),
        "test_set_id": settings.test_set_id,
        "test_set_version": settings.test_set_version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "notes": "Synthetic test data only. Metrics require evaluate.py.",
    }
    write_json(run_dir / "meta.json", meta)
    return {"run_dir": str(run_dir), "meta": meta, "outputs": outputs}
