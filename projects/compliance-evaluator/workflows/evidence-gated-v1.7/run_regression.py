#!/usr/bin/env python3
"""Run frozen v1.7 once: deterministic mapping and bounded evidence observations."""
from __future__ import annotations
import argparse,importlib.util,json,os,sys,uuid
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator
from openai import OpenAI
from execution_contract import StageFailure,execute_stage,quarantine_record
from pipeline import compose_final_decision
from provider_contract import assert_provider_subset
from rulebook import derive_mapping,validate_observations,validate_rulebook

W=Path(__file__).resolve().parent; P=W.parents[1]; V15=W.parent/'evidence-gated-v1.5'; V14=W.parent/'evidence-gated-v1.4'; V12=W.parent/'evidence-gated-v1.2'
R=P/'results'/'evidence-gated-v1.7'; META=W/'workflow-v1.7.meta.json'; V15CERT=V15/'certification'/'contract-certification-v1.5.json'; RULEBOOK=P/'rulebooks'/'coverage-evidence-v1.0'/'rulebook.json'; COMPOSITION=P/'policies'/'assurance-composition-v1.0'/'policy.json'
S=importlib.util.spec_from_file_location('v14_runner',V14/'run_regression.py')
if S is None or S.loader is None: raise RuntimeError('Could not load runner utilities')
B=importlib.util.module_from_spec(S); S.loader.exec_module(B)
load_json=B.load_json; write_json=B.write_json; sha256_file=B.sha256_file; utc_now=B.utc_now; request_stage=B.request_stage; source_payload=B.source_payload; resolve_approved_obligation=B.resolve_approved_obligation; evidence_payload=B.evidence_payload
INPUTS=(P/'datasets/baseline-v1.0/inputs/aml-cft.json',P/'datasets/baseline-v1.0/inputs/market-conduct.json')

def verify(meta:dict[str,Any]):
    bad=[p for p,h in meta['artefact_sha256'].items() if not (P/p).exists() or sha256_file(P/p)!=h]
    if bad or meta['status']!='frozen_pre_regression' or meta['regression_run_count']!=0: raise RuntimeError('Frozen v1.7 verification failed: '+','.join(bad))
    lineage=load_json(V15CERT)
    if sha256_file(V15CERT)!=meta['v1_5_certification_lineage_sha256']: raise RuntimeError('v1.5 certification lineage changed')
    evidence=lineage['records'][0]
    if evidence['schema_sha256']!=sha256_file(W/'schemas/evidence-observation-stage.schema.json') or evidence['prompt_sha256']!=sha256_file(W/'prompts/evidence-observation-stage-v1.5.md'): raise RuntimeError('Inherited evidence contract differs')
    if sha256_file(V15/'schemas/source-support-stage.schema.json')!=sha256_file(W/'schemas/source-support-stage.schema.json') or sha256_file(V15/'prompts/source-support-stage-v1.3.md')!=sha256_file(W/'prompts/source-support-stage-v1.3.md'): raise RuntimeError('Inherited source contract differs')

def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument('--preflight',action='store_true'); g.add_argument('--execute',action='store_true'); a=ap.parse_args()
    meta=load_json(META); verify(meta)
    cases=[]
    for p in INPUTS: cases+=load_json(p)
    profile=load_json(P/'profiles/synthetic-investment-wealth-institution-v1.0.json'); catalogue={x['control_id'] for x in profile['controls']}; rb=load_json(RULEBOOK); composition=load_json(COMPOSITION); validate_rulebook(rb,catalogue)
    if len(cases)!=24: raise RuntimeError('Frozen cases changed')
    if a.preflight:
        if R.exists(): raise RuntimeError('v1.7 results already exist')
        print('Evidence-gated v1.7 preflight passed: approved rulebook and composition policy, inherited provider contracts 2/2, 24 cases and at most 24 calls. No API call made.'); return 0
    if R.exists(): raise RuntimeError('v1.7 already started; refusing overwrite')
    if not os.environ.get('OPENAI_API_KEY'): raise RuntimeError('OPENAI_API_KEY required')
    source_manifest=load_json(P/'source-packs/source-pack-v1.0/manifest.json'); source_records={x['source_id']:x for x in source_manifest['sources']}
    policies=[load_json(V12/'policies'/n) for n in ('source-transition-policy-v1.2.json','applicability-policy-v1.2.json','assurance-decision-policy-v1.2.json','escalation-policy-v1.2.json')]
    prompts={'source_support':(W/'prompts/source-support-stage-v1.3.md').read_text(),'evidence':(W/'prompts/evidence-observation-stage-v1.5.md').read_text()}; formats={'source_support':load_json(W/'schemas/source-support-stage.schema.json'),'evidence':load_json(W/'schemas/evidence-observation-stage.schema.json')}
    for f in formats.values(): assert_provider_subset(f)
    validators={k:Draft202012Validator(v['schema']) for k,v in formats.items()}; final=Draft202012Validator(load_json(P/'baseline/baseline-prediction.schema.json')['schema'])
    run_id=f'evidence-gated-v1.7-{uuid.uuid4()}'; state_path=R/'run-state.json'; ledger=R/'stage-ledger.jsonl'; out_path=R/'predictions.json'
    state={'run_id':run_id,'status':'running','started_at':utc_now(),'completed_at':None,'dataset_id':meta['dataset_id'],'dataset_version':meta['dataset_version'],'workflow_id':meta['workflow_id'],'workflow_version':'1.7','model':meta['model'],'temperature':0,'case_count':24,'maximum_api_call_count':24,'requested_api_call_count':0,'semantically_valid_api_call_count':0,'completed_case_count':0,'quarantined_case_count':0,'active_case_id':None,'active_stage':None,'tuning_after_observation':False,'retry_count':0,'error':None}; write_json(state_path,state)
    client=OpenAI(api_key=os.environ['OPENAI_API_KEY'],base_url=os.environ.get('OPENAI_BASE_URL','').strip() or 'https://api.openai.com/v1'); predictions=[]; quarantines=[]
    def call(case,pos,stage,payload,semantic):
        state['requested_api_call_count']+=1; ordinal=state['requested_api_call_count']; state['active_case_id']=case['case_id']; state['active_stage']=stage; write_json(state_path,state)
        result=execute_stage(run_id=run_id,case_id=case['case_id'],execution_position=pos,stage=stage,request_ordinal=ordinal,request=lambda:request_stage(client,meta['model'],0,prompts[stage],formats[stage],payload),transport_validate=validators[stage].validate,semantic_validate=semantic,ledger_path=ledger); state['semantically_valid_api_call_count']+=1; return result
    for pos,case in enumerate(cases,1):
        try:
            entered=case['upstream_obligation']['supplied'] is True and case['upstream_obligation']['status']=='approved'
            if entered:
                approved=resolve_approved_obligation(case); mapping=derive_mapping(case['case_id'],case['proposed_mapping']['control_ids'],rb,catalogue); source=source_api=None
                payload=evidence_payload(case,approved,mapping,profile); payload['approved_evidence_requirements']=rb['evidence_requirements']
                observations,evidence_api=call(case,pos,'evidence',payload,lambda x:validate_observations(x,case,rb))
            else:
                approved=None; mapping=observations=evidence_api=None
                source,source_api=call(case,pos,'source_support',source_payload(case,source_records),lambda x:B.validate_source_stage(x,case['case_id']))
            decision,trace=compose_final_decision(case,source,mapping,observations,approved,*policies,profile,rb,composition); final.validate(decision)
            predictions.append({'input_case_id':case['case_id'],'workstream':case['workstream'],'case_stage':case['case_stage'],'terminal_status':'completed','prediction':decision,'stage_outputs':{'source_support':source,'mapping':mapping,'evidence_observations':observations,'approved_obligation_authority':approved},'policy_trace':trace,'reconciliation':{'passed':True,'manual_correction':False},'api':{'source_support':source_api,'mapping':None,'evidence':evidence_api}}); state['completed_case_count']+=1
        except StageFailure as f: quarantines.append(quarantine_record(case,pos,f)); state['quarantined_case_count']+=1
        except ValueError as exc: quarantines.append(quarantine_record(case,pos,StageFailure(case['case_id'],'policy_composition','policy_authority_failure',str(exc)))); state['quarantined_case_count']+=1
        state['active_case_id']=state['active_stage']=None; write_json(state_path,state)
    status='completed_with_quarantine' if quarantines else 'completed'; write_json(out_path,{'run_id':run_id,'status':status,'dataset_id':meta['dataset_id'],'dataset_version':meta['dataset_version'],'workflow_id':meta['workflow_id'],'workflow_version':'1.7','workflow_meta_sha256':sha256_file(META),'model_requested':meta['model'],'temperature':0,'run_attempt_count':1,'requested_api_call_count':state['requested_api_call_count'],'retry_count':0,'tuning_after_observation':False,'case_count':24,'predictions':predictions,'quarantines':quarantines}); state['status']=status; state['completed_at']=utc_now(); write_json(state_path,state); print(f'Completed one frozen v1.7 regression: completed={len(predictions)} quarantined={len(quarantines)} calls={state["requested_api_call_count"]}'); return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as e: print(f'ERROR: {e}',file=sys.stderr); raise SystemExit(1)
