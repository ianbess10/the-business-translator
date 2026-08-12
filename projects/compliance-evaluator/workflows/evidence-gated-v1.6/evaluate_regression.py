#!/usr/bin/env python3
"""Evaluate one future v1.6 terminal record against benchmark authority v1.1."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
from typing import Any

W=Path(__file__).resolve().parent; P=W.parents[1]; R=P/'results/evidence-gated-v1.6'; META=W/'workflow-v1.6.meta.json'
PRED=R/'predictions.json'; EVAL=R/'evaluation.json'; COMP=R/'regression-comparison.json'; REPORT=R/'README.md'
FIELDS=('source_use_disposition','obligation_outcome','applicability_status','assurance_gate','mapping_status','control_mappings','assurance_outcome','gap_types','gap_severity','remediation_action_types','escalation_required','escalation_roles','human_review_required','compliance_conclusion')
def load(path:Path): return json.loads(path.read_text())
def write(path:Path,obj:Any): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def sha(path:Path): return hashlib.sha256(path.read_bytes()).hexdigest()
def base_labels():
    rows=[]
    for name in ('aml-cft.json','market-conduct.json'): rows+=load(P/'datasets/baseline-v1.0/labels'/name)
    return {x['case_id']:x['expected'] for x in rows}
def authority(): return {x['case_id']:x for x in load(P/'datasets/baseline-v1.1/label-authority-overlay.json')['overlays']}
def expected_labels(policy:dict[str,Any]):
    labels=base_labels()
    for case_id,item in authority().items():
        c=policy['coverage_rules'][item['coverage_state']]; e=policy['evidence_rules'][item['evidence_condition']]
        gaps=sorted(set(c['gap_types']+e['gap_types'])); actions=sorted(set(c['action_types']+e['action_types']))
        assessed=[x for x in (c['severity_floor'],e['severity_floor']) if x not in {'not_applicable','unassessed'}]
        rank={'medium':1,'high':2,'critical':3}; severity=max(assessed,key=rank.get) if assessed else ('unassessed' if 'unassessed' in {c['severity_floor'],e['severity_floor']} else 'not_applicable')
        labels[case_id]={**labels[case_id],'mapping_status':{'complete':'mapped','partial':'partially_mapped','absent':'no_suitable_control_identified'}[item['coverage_state']],'assurance_outcome':'potential_control_gap' if assessed else ('insufficient_evidence' if severity=='unassessed' else 'mapped_and_evidenced'),'gap_types':gaps,'gap_severity':severity,'remediation_action_types':actions,'escalation_required':item['escalation_required'],'escalation_roles':item['escalation_roles']}
    return labels
def verify(meta):
    bad=[]
    for group in ('artefact_sha256','evaluator_only_sha256'):
        for rel,digest in meta[group].items():
            path=P/rel
            if not path.exists() or sha(path)!=digest: bad.append(rel)
    if bad: raise RuntimeError('Frozen v1.6 evaluator evidence mismatch: '+','.join(bad))
def rate(correct,total): return {'correct':correct,'total':total,'accuracy':round(correct/total,4) if total else None}
def score(payload):
    labels=expected_labels(load(P/'policies/assurance-composition-v1.0/policy.json')); completed={x['input_case_id']:x for x in payload['predictions']}; quarantines=payload.get('quarantines',[]); terminal=set(completed)|{x['input_case_id'] for x in quarantines}
    if len(terminal)!=24 or terminal!=set(labels): raise RuntimeError('Every authority case requires one terminal record')
    per_case=[]; field_metrics={f:0 for f in FIELDS}; exact=0
    for case_id,wrapper in completed.items():
        prediction=wrapper['prediction']; mismatched=[]
        for field in FIELDS:
            equal=prediction[field]==labels[case_id][field] if field not in {'gap_types','remediation_action_types','escalation_roles','control_mappings'} else sorted(prediction[field],key=str)==sorted(labels[case_id][field],key=str)
            field_metrics[field]+=int(equal)
            if not equal: mismatched.append(field)
        trace=wrapper.get('policy_trace',{}); auth=authority().get(case_id); authority_match=True
        if auth: authority_match=trace.get('coverage_state')==auth['coverage_state'] and trace.get('evidence_condition')==auth['evidence_condition'] and trace.get('concurrent_conditions_preserved') is True
        if not authority_match: mismatched.append('benchmark_authority_trace')
        case_exact=not mismatched; exact+=int(case_exact); per_case.append({'case_id':case_id,'end_to_end_exact':case_exact,'mismatched_fields':mismatched})
    exp_pos={c for c,x in labels.items() if x['escalation_required']}; pred_pos={c for c,x in completed.items() if x['prediction']['escalation_required']}; tp=len(exp_pos&pred_pos); fp=len(pred_pos-exp_pos); fn=len(exp_pos-pred_pos); tn=24-tp-fp-fn
    evaluation={'evaluation_id':payload['run_id']+'-evaluation','run_id':payload['run_id'],'workflow_version':'1.6','dataset_id':payload['dataset_id'],'dataset_version':payload['dataset_version'],'benchmark_authority_version':'1.1','case_count':24,'quarantine_count':len(quarantines),'end_to_end_exact':rate(exact,24),'field_metrics':{f:rate(n,24) for f,n in field_metrics.items()},'binary_metrics':{'escalation_required':{'true_positive':tp,'false_positive':fp,'true_negative':tn,'false_negative':fn}},'per_case':per_case,'synthetic_benchmark_evidence':True,'production_performance':False}
    failed_authority=[x['case_id'] for x in per_case if 'benchmark_authority_trace' in x['mismatched_fields']]
    gates={'complete_terminal_coverage':{'passed':len(terminal)==24},'no_quarantined_cases':{'passed':not quarantines,'case_ids':[x['input_case_id'] for x in quarantines]},'exact_dual_axis_authority':{'passed':not failed_authority,'failure_case_ids':failed_authority},'all_mandatory_escalations_detected':{'passed':fn==0,'false_negative':fn},'zero_unnecessary_escalations':{'passed':fp==0,'false_positive':fp},'all_decision_fields_exact':{'passed':exact==24,'exact_case_count':exact}}
    comparison={'comparison_id':payload['run_id']+'-regression-comparison','workflow_version':'1.6','dataset_version':'1.1','evidence_boundary':'frozen_regression_not_independent_validation','end_to_end_exact':evaluation['end_to_end_exact'],'quarantine_count':len(quarantines),'acceptance_gates':gates,'all_acceptance_gates_passed':all(x['passed'] for x in gates.values())}
    return evaluation,comparison
def perfect_payload():
    labels=expected_labels(load(P/'policies/assurance-composition-v1.0/policy.json')); auth=authority(); predictions=[]
    for case_id,expected in labels.items():
        trace={'concurrent_conditions_preserved':True}
        if case_id in auth: trace.update({'coverage_state':auth[case_id]['coverage_state'],'evidence_condition':auth[case_id]['evidence_condition']})
        predictions.append({'input_case_id':case_id,'terminal_status':'completed','prediction':expected,'policy_trace':trace})
    return {'run_id':'evidence-gated-v1.6-self-test','workflow_version':'1.6','dataset_id':'SA-REG-BASELINE-001','dataset_version':'1.1','run_attempt_count':1,'retry_count':0,'tuning_after_observation':False,'predictions':predictions,'quarantines':[]}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--self-test',action='store_true'); a=ap.parse_args(); meta=load(META); verify(meta)
    if a.self_test:
        ev,co=score(perfect_payload()); assert ev['end_to_end_exact']['correct']==24 and co['all_acceptance_gates_passed']; print('v1.6 evaluator self-test passed: 24/24 under authority v1.1, identity exact, all gates passed'); return 0
    if any(x.exists() for x in (EVAL,COMP,REPORT)): raise RuntimeError('v1.6 evaluation evidence already exists; refusing overwrite')
    payload=load(PRED)
    if payload.get('workflow_version')!='1.6' or payload.get('dataset_version')!='1.1' or payload.get('workflow_meta_sha256')!=sha(META): raise RuntimeError('v1.6 workflow or benchmark authority identity mismatch')
    if payload.get('run_attempt_count')!=1 or payload.get('retry_count')!=0 or payload.get('tuning_after_observation') is not False: raise RuntimeError('Frozen execution controls invalid')
    ev,co=score(payload); write(EVAL,ev); write(COMP,co); REPORT.write_text(f"# Evidence-Gated Decision Pipeline v1.6 — Regression Results\n\n> Synthetic regression evidence against benchmark authority v1.1; not independent validation or production performance.\n\n- End-to-end exact: {ev['end_to_end_exact']['correct']}/24\n- Quarantines: {ev['quarantine_count']}\n- All gates passed: {co['all_acceptance_gates_passed']}\n")
    print(f"v1.6 evaluation completed once: exact={ev['end_to_end_exact']['correct']}/24 quarantines={ev['quarantine_count']}"); return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as exc: print(f'ERROR: {exc}',file=sys.stderr); raise SystemExit(1)
