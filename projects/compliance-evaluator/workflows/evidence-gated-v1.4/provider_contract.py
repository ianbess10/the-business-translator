"""Reuse the frozen v1.3 conservative provider-subset audit."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SOURCE = Path(__file__).resolve().parent.parent / "evidence-gated-v1.3" / "provider_contract.py"
SPEC = importlib.util.spec_from_file_location("evidence_gated_v1_3_provider_contract", SOURCE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load the frozen v1.3 provider-subset audit")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

provider_subset_errors = MODULE.provider_subset_errors
assert_provider_subset = MODULE.assert_provider_subset
ALLOWED_SCHEMA_KEYWORDS = MODULE.ALLOWED_SCHEMA_KEYWORDS
FORBIDDEN_COMPOSITION_KEYWORDS = MODULE.FORBIDDEN_COMPOSITION_KEYWORDS
