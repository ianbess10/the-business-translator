"""v1.5 deterministic mapping and rulebook-derived evidence policy adapter."""
from __future__ import annotations
import importlib.util
from pathlib import Path
from typing import Any
from rulebook import derive_evidence_assessment, validate_observations

P=Path(__file__).resolve().parent.parent/'evidence-gated-v1.2'/'pipeline.py'
S=importlib.util.spec_from_file_location('v12_policy',P)
if S is None or S.loader is None: raise RuntimeError('Could not load policy')
POLICY=importlib.util.module_from_spec(S); S.loader.exec_module(POLICY)
validate_final_decision=POLICY.validate_final_decision

def compose_final_decision(case:dict[str,Any], source_stage:dict[str,Any]|None, mapping_stage:dict[str,Any]|None, observations:dict[str,Any]|None, approved:dict[str,Any]|None, source_policy:dict[str,Any], applicability_policy:dict[str,Any], assurance_policy:dict[str,Any], escalation_policy:dict[str,Any], profile:dict[str,Any], rulebook:dict[str,Any]):
    evidence=None
    if observations is not None:
        validate_observations(observations,case,rulebook)
        assessment=derive_evidence_assessment(observations,rulebook)
        evidence={"case_id":case["case_id"],"evidence_assessment":assessment,"design_deficiency_evidence_present":assessment=="design_deficiency","adverse_indicator_present":assessment=="adverse_operating_evidence","severity_recommendation":"high" if assessment in {"design_deficiency","adverse_operating_evidence"} else "not_applicable" if assessment=="sufficient" else "unassessed","rationale":observations["rationale"]}
    return POLICY.compose_final_decision(case,source_stage,mapping_stage,evidence,approved,source_policy,applicability_policy,assurance_policy,escalation_policy,profile)
