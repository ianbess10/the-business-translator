#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

W=Path(__file__).resolve().parent; P=W.parents[1]; META=W/'workflow-v1.7.meta.json'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
runtime=[p for p in W.rglob('*') if p.is_file() and p.name!='workflow-v1.7.meta.json' and '__pycache__' not in p.parts]
shared=[
 P/'rulebooks/coverage-evidence-v1.0/rulebook.json',P/'policies/assurance-composition-v1.0/policy.json',P/'policies/assurance-composition-v1.0/approval-record.json',
 P/'datasets/baseline-v1.0/inputs/aml-cft.json',P/'datasets/baseline-v1.0/inputs/market-conduct.json',P/'profiles/synthetic-investment-wealth-institution-v1.0.json',P/'baseline/baseline-prediction.schema.json',
 P/'workflows/evidence-gated-v1.5/certification/contract-certification-v1.5.json',P/'workflows/evidence-gated-v1.3/certification/contract-certification-v1.3.json',P/'workflows/evidence-gated-v1.4/run_regression.py',P/'workflows/evidence-gated-v1.2/pipeline.py',
 *[P/f'workflows/evidence-gated-v1.2/policies/{n}' for n in ('source-transition-policy-v1.2.json','applicability-policy-v1.2.json','assurance-decision-policy-v1.2.json','escalation-policy-v1.2.json')]
]
evaluator=[P/'datasets/baseline-v1.0/labels/aml-cft.json',P/'datasets/baseline-v1.0/labels/market-conduct.json',P/'datasets/baseline-v1.2/entered-assurance-authority.json',P/'datasets/baseline-v1.2/baseline-v1.2.meta.json',P/'adjudications/dual-axis-authority-v1.0/adjudication.json']
payload={
 'workflow_id':'SA-REG-EVIDENCE-GATED-001','version':'1.7','dataset_id':'SA-REG-BASELINE-001','dataset_version':'1.2','status':'frozen_pre_regression','based_on_decision_id':'SA-REG-EVIDENCE-GATED-V1.7-DECISION-001','model':'gpt-4o-mini-2024-07-18','temperature':0,
 'provider_contract_status':'inherited_certified_unchanged','provider_contract_count':2,'new_provider_certification_call_count':0,'v1_5_certification_lineage_sha256':sha(P/'workflows/evidence-gated-v1.5/certification/contract-certification-v1.5.json'),'regression_run_count':0,'evaluation_count':0,'retry_count_permitted':0,'tuning_after_observation_permitted':False,
 'artefact_sha256':{str(x.relative_to(P)):sha(x) for x in sorted(runtime+shared)},'evaluator_only_sha256':{str(x.relative_to(P)):sha(x) for x in evaluator}
}
META.write_text(json.dumps(payload,indent=2)+'\n')
print(f"Frozen v1.7 manifest written: {len(payload['artefact_sha256'])} runtime/control artefacts and {len(payload['evaluator_only_sha256'])} evaluator-only artefacts")
