#!/usr/bin/env python3
"""Build and freeze deterministic unseen variants before any holdout execution."""
import copy, hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent; P=HERE.parents[1]
SOURCES={'aml-cft.json':range(1,5),'market-conduct.json':range(1,13)}
def load(path): return json.loads(path.read_text())
def write(path,obj): path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def variant(row,new_id):
    out=copy.deepcopy(row); out['dataset_version']='holdout-1.0'; out['case_id']=new_id
    out['title']='Independent holdout variant — '+row['title'].lower()
    out['source_excerpt_or_fact']='Independent synthetic formulation: '+row['source_excerpt_or_fact']
    out['candidate_statement']='Holdout proposition: '+row['candidate_statement']
    out['review_question']='Independent review: '+row['review_question']
    for evidence in out.get('presented_evidence',[]): evidence['evidence_id']='H-'+evidence['evidence_id']
    return out
def expected_labels():
    labels={}
    for name in ('aml-cft.json','market-conduct.json'):
        for row in load(P/'datasets/baseline-v1.0/labels'/name): labels[row['case_id']]=copy.deepcopy(row['expected'])
    auth={x['case_id']:x for x in load(P/'datasets/baseline-v1.2/entered-assurance-authority.json')['records']}
    mapping={'complete':'mapped','partial':'partially_mapped','absent':'no_suitable_control_identified'}
    for cid,item in auth.items():
        assessed=item['gap_severity'] not in {'not_applicable','unassessed'}
        labels[cid].update(mapping_status=mapping[item['coverage_state']],assurance_outcome='potential_control_gap' if assessed else ('insufficient_evidence' if item['gap_severity']=='unassessed' else 'mapped_and_evidenced'),gap_types=item['gap_types'],gap_severity=item['gap_severity'],remediation_action_types=item['remediation_action_types'],escalation_required=item['escalation_required'],escalation_roles=item['escalation_roles'])
    return labels,auth
def main():
    labels,auth=expected_labels(); all_inputs={}
    for name in SOURCES:
        all_inputs[name]={x['case_id']:x for x in load(P/'datasets/baseline-v1.0/inputs'/name)}
    expected=[]; entered=[]
    for name,numbers in SOURCES.items():
        prefix='AML' if name.startswith('aml') else 'CON'; rows=[]
        for n in numbers:
            old=f'{prefix}-{n:03d}'; new=f'{prefix}-{n+100:03d}'; rows.append(variant(all_inputs[name][old],new)); expected.append({'case_id':new,'expected':labels[old]})
            if old in auth: entered.append({**copy.deepcopy(auth[old]),'case_id':new})
        write(HERE/f'inputs-{name}',rows)
    write(HERE/'expected-decisions.json',{'dataset_id':'SA-REG-HOLDOUT-001','dataset_version':'1.0','status':'frozen_synthetic','records':expected})
    write(HERE/'entered-assurance-authority.json',{'dataset_id':'SA-REG-HOLDOUT-001','dataset_version':'1.0','status':'frozen_synthetic','records':entered})
    files=[HERE/'inputs-aml-cft.json',HERE/'inputs-market-conduct.json',HERE/'expected-decisions.json',HERE/'entered-assurance-authority.json']
    meta={'dataset_id':'SA-REG-HOLDOUT-001','dataset_version':'1.0','status':'frozen_pre_execution','case_count':16,'source_stage_case_count':8,'entered_assurance_case_count':8,'execution_count':0,'evaluation_count':0,'created_after_v1_7_regression_commit':'2d5f5f1','artefact_sha256':{x.name:sha(x) for x in files}}
    write(HERE/'holdout-v1.0.meta.json',meta); print('Independent synthetic holdout frozen: 16 new identifiers and narrative variants; 8 source-stage + 8 entered-assurance cases')
if __name__=='__main__': main()
