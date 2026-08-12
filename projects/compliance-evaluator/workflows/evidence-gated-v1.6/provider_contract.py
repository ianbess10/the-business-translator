"""Reuse the frozen conservative provider-subset audit."""
from __future__ import annotations
import importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent.parent/'evidence-gated-v1.3'/'provider_contract.py'
S=importlib.util.spec_from_file_location('v13_provider_contract',P)
if S is None or S.loader is None: raise RuntimeError('Could not load provider audit')
M=importlib.util.module_from_spec(S); S.loader.exec_module(M)
assert_provider_subset=M.assert_provider_subset
provider_subset_errors=M.provider_subset_errors
