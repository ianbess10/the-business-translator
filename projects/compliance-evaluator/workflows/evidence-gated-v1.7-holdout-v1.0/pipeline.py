"""v1.7 dual-axis assurance composition from approved policy authority."""
from __future__ import annotations
import importlib.util
from copy import deepcopy
from pathlib import Path
from typing import Any
from rulebook import derive_evidence_assessment, validate_observations

BASE_PATH=Path(__file__).resolve().parent.parent/'evidence-gated-v1.2'/'pipeline.py'
SPEC=importlib.util.spec_from_file_location('v12_policy',BASE_PATH)
if SPEC is None or SPEC.loader is None: raise RuntimeError('Could not load retained policy')
BASE=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(BASE)
validate_final_decision=BASE.validate_final_decision

def compose_assurance(coverage_state:str,evidence_condition:str,workstream:str,policy:dict[str,Any])->dict[str,Any]:
    coverage=policy['coverage_rules'][coverage_state]; evidence=policy['evidence_rules'][evidence_condition]
    if 'terminal_disposition' in coverage or 'terminal_disposition' in evidence:
        return {'terminal_disposition':'quarantine_without_policy_conclusion','coverage_state':coverage_state,'evidence_condition':evidence_condition}
    gaps=sorted(set(coverage['gap_types']+evidence['gap_types']))
    actions=sorted(set(coverage['action_types']+evidence['action_types']))
    rank={'not_applicable':0,'medium':1,'high':2,'critical':3}
    assessed=[x for x in (coverage['severity_floor'],evidence['severity_floor']) if x not in {'not_applicable','unassessed'}]
    severity=max(assessed,key=rank.get) if assessed else ('unassessed' if 'unassessed' in {coverage['severity_floor'],evidence['severity_floor']} else 'not_applicable')
    triggers=sorted({x['escalation_trigger'] for x in (coverage,evidence) if 'escalation_trigger' in x})
    roles=sorted({role for trigger in triggers for role in policy['escalation']['triggers'][trigger]['workstream_roles'][workstream]})
    outcome='potential_control_gap' if assessed else ('insufficient_evidence' if severity=='unassessed' else 'mapped_and_evidenced')
    routing={action:list(policy['routing'][action]) for action in actions}
    return {'terminal_disposition':'compose','coverage_state':coverage_state,'evidence_condition':evidence_condition,'assurance_outcome':outcome,'gap_types':gaps,'gap_severity':severity,'remediation_action_types':actions,'remediation_routing':routing,'escalation_required':bool(triggers),'escalation_roles':roles,'escalation_triggers':triggers,'applied_policy_rule_ids':[coverage['rule_id'],evidence['rule_id'],policy['composition']['rule_id']]}

def resolve_routing(abstract:dict[str,list[str]],mapping:dict[str,Any],observations:dict[str,Any],approved:dict[str,Any],profile:dict[str,Any],rulebook:dict[str,Any],workstream:str)->dict[str,list[str]]:
    catalogue={x['control_id']:x for x in profile['controls']}; requirements={x['requirement_id']:x for x in rulebook['evidence_requirements']}
    current=sorted({catalogue[x]['owner_role'] for x in mapping['current_mapping_control_ids']})
    evidence=sorted({requirements[x['requirement_id']]['evidence_owner_role'] for x in observations['observations']})
    mapping_owner=[approved['routing']['proposed_owner_role']]
    compliance=['AML Compliance Officer' if workstream=='aml_cft' else 'Head of Compliance']
    oversight=['AML Compliance Officer' if workstream=='aml_cft' else 'Conduct Risk Officer']
    values={'mapping_authority_owner':mapping_owner,'current_control_owner':current,'evidence_owner':evidence,'workstream_compliance_authority':compliance,'workstream_oversight_authority':oversight}
    return {action:sorted({role for token in tokens for role in values[token]}) for action,tokens in abstract.items()}

def compose_final_decision(case:dict[str,Any],source_stage:dict[str,Any]|None,mapping_stage:dict[str,Any]|None,observations:dict[str,Any]|None,approved:dict[str,Any]|None,source_policy:dict[str,Any],applicability_policy:dict[str,Any],legacy_assurance_policy:dict[str,Any],legacy_escalation_policy:dict[str,Any],profile:dict[str,Any],rulebook:dict[str,Any],composition_policy:dict[str,Any]):
    if mapping_stage is None:
        return BASE.compose_final_decision(case,source_stage,None,None,approved,source_policy,applicability_policy,legacy_assurance_policy,legacy_escalation_policy,profile)
    if observations is None: raise ValueError('Entered assurance requires evidence observations')
    validate_observations(observations,case,rulebook)
    evidence_condition=derive_evidence_assessment(observations,rulebook)
    if evidence_condition=='insufficient_to_assess': evidence_condition='not_assessable'
    coverage_state={'complete':'complete','partial':'partial','no_suitable_control':'absent'}[mapping_stage['mapping_completeness']]
    composed=compose_assurance(coverage_state,evidence_condition,case['workstream'],composition_policy)
    if composed['terminal_disposition']!='compose': raise ValueError('Approved policy authority requires quarantine without conclusion')
    legacy_evidence={'case_id':case['case_id'],'evidence_assessment':'sufficient','design_deficiency_evidence_present':False,'adverse_indicator_present':False,'severity_recommendation':'not_applicable','rationale':observations['rationale']}
    decision,trace=BASE.compose_final_decision(case,source_stage,mapping_stage,legacy_evidence,approved,source_policy,applicability_policy,legacy_assurance_policy,legacy_escalation_policy,profile)
    decision=deepcopy(decision)
    for field in ('assurance_outcome','gap_types','gap_severity','remediation_action_types','escalation_required','escalation_roles'): decision[field]=composed[field]
    BASE.validate_final_decision(decision,profile,legacy_escalation_policy,case['workstream'])
    routing=resolve_routing(composed['remediation_routing'],mapping_stage,observations,approved,profile,rulebook,case['workstream'])
    trace=deepcopy(trace); trace.update({'coverage_state':coverage_state,'evidence_condition':evidence_condition,'concurrent_conditions_preserved':True,'remediation_routing':routing,'escalation_triggers':composed['escalation_triggers'],'composition_policy_id':composition_policy['policy_id'],'composition_policy_version':composition_policy['version']})
    trace['applied_policy_rules']=trace['applied_policy_rules']+composed['applied_policy_rule_ids']
    return decision,trace
