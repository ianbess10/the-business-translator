from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEST_SET_ID = "trade-exception-test-set-v1.0"
DEFAULT_TEST_SET_PATH = PROJECT_ROOT / "datasets" / f"{DEFAULT_TEST_SET_ID}.jsonl"
DEFAULT_PROMPT_VERSION = "v4"
DEFAULT_ENGINEERED_PROMPT_PATH = PROJECT_ROOT / "prompts" / "engineered-v4.md"

# Version → prompt file. V4 path unchanged; V5 uses the new root file.
PROMPT_VERSION_FILES = {
    "v4": PROJECT_ROOT / "prompts" / "engineered-v4.md",
    "v5": PROJECT_ROOT / "engineered-prompt-v5.md",
}


@dataclass(frozen=True)
class Settings:
    provider: str
    openai_api_key: str | None
    openai_model: str
    openai_base_url: str | None
    temperature: float
    run_label: str | None
    prompt_version: str
    project_root: Path
    test_set_path: Path
    test_set_id: str
    test_set_version: str
    schema_path: Path
    results_dir: Path
    baseline_prompt_path: Path
    engineered_prompt_path: Path


def _load_test_set_identity(path: Path) -> tuple[str, str]:
    meta_path = path.with_suffix(".meta.json")
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return (
            str(meta.get("id") or path.stem),
            str(meta.get("version") or "unknown"),
        )
    return path.stem, "unknown"


def load_settings(env_file: Path | None = None) -> Settings:
    load_dotenv(env_file or PROJECT_ROOT / ".env", override=False)

    temperature_raw = os.getenv("OPENAI_TEMPERATURE", "0").strip() or "0"
    try:
        temperature = float(temperature_raw)
    except ValueError as exc:
        raise ValueError("OPENAI_TEMPERATURE must be a number") from exc

    provider = (os.getenv("MODEL_PROVIDER") or "mock").strip().lower()
    base_url = (os.getenv("OPENAI_BASE_URL") or "").strip() or None
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip() or None
    run_label = (os.getenv("RUN_LABEL") or "").strip() or None
    prompt_version = (os.getenv("PROMPT_VERSION") or DEFAULT_PROMPT_VERSION).strip()

    test_set_override = (os.getenv("TEST_SET_PATH") or "").strip()
    if test_set_override:
        test_set_path = Path(test_set_override)
        if not test_set_path.is_absolute():
            test_set_path = (PROJECT_ROOT / test_set_path).resolve()
    else:
        test_set_path = DEFAULT_TEST_SET_PATH

    prompt_override = (os.getenv("ENGINEERED_PROMPT_PATH") or "").strip()
    if prompt_override:
        engineered_prompt_path = Path(prompt_override)
        if not engineered_prompt_path.is_absolute():
            engineered_prompt_path = (PROJECT_ROOT / engineered_prompt_path).resolve()
    else:
        # Prefer explicit version map so V4 keeps using prompts/engineered-v4.md
        # and V5 uses engineered-prompt-v5.md without touching engineered-prompt.md.
        mapped = PROMPT_VERSION_FILES.get(prompt_version)
        if mapped is not None and mapped.exists():
            engineered_prompt_path = mapped
        else:
            versioned = PROJECT_ROOT / "prompts" / f"engineered-{prompt_version}.md"
            engineered_prompt_path = (
                versioned if versioned.exists() else DEFAULT_ENGINEERED_PROMPT_PATH
            )
            if not engineered_prompt_path.exists():
                engineered_prompt_path = PROJECT_ROOT / "engineered-prompt.md"

    test_set_id, test_set_version = _load_test_set_identity(test_set_path)

    return Settings(
        provider=provider,
        openai_api_key=api_key,
        openai_model=(os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip(),
        openai_base_url=base_url,
        temperature=temperature,
        run_label=run_label,
        prompt_version=prompt_version,
        project_root=PROJECT_ROOT,
        test_set_path=test_set_path,
        test_set_id=test_set_id,
        test_set_version=test_set_version,
        schema_path=PROJECT_ROOT / "schema" / "engineered_output.schema.json",
        results_dir=PROJECT_ROOT / "results",
        baseline_prompt_path=PROJECT_ROOT / "baseline-prompt.md",
        engineered_prompt_path=engineered_prompt_path,
    )
