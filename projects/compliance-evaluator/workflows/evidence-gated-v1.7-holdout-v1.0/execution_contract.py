"""Reuse frozen v1.4 stage-ledger and quarantine controls."""
from __future__ import annotations
import importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent.parent/'evidence-gated-v1.4'/'execution_contract.py'
S=importlib.util.spec_from_file_location('v14_execution_contract',P)
if S is None or S.loader is None: raise RuntimeError('Could not load execution contract')
M=importlib.util.module_from_spec(S); S.loader.exec_module(M)
StageFailure=M.StageFailure
execute_stage=M.execute_stage
quarantine_record=M.quarantine_record
