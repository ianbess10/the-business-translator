#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

W=Path(__file__).resolve().parent; P=W.parents[1]; META=W/'workflow-holdout-v1.0.meta.json'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
runtime=[p for p in W.rglob('*') if p.is_file() and p.name not in {'workflow-holdout-v1.0.meta.json','workflow-v1.7.meta.json'} and '__pycache__' not in p.parts]
shared=[P/'datasets/holdout-v1.0'/n for n in ('inputs-aml-cft.json','inputs-market-conduct.json','holdout-v1.0.meta.json')]
shared += [P/'rulebooks/coverage-evidence-v1.0/rulebook.json',P/'policies/assurance-composition-v1.0/policy.json',P/'profiles/synthetic-investment-wealth-institution-v1.0.json',P/'baseline/baseline-prediction.schema.json',P/'workflows/evidence-gated-v1.7/workflow-v1.7.meta.json',P/'workflows/evidence-gated-v1.5/certification/contract-certification-v1.5.json',P/'workflows/evidence-gated-v1.3/certification/contract-certification-v1.3.json',P/'workflows/evidence-gated-v1.4/run_regression.py',P/'workflows/evidence-gated-v1.2/pipeline.py']
shared += [P/f'workflows/evidence-gated-v1.2/policies/{n}' for n in ('source-transition-policy-v1.2.json','applicability-policy-v1.2.json','assurance-decision-policy-v1.2.json','escalation-policy-v1.2.json')]
evaluator=[P/'datasets/holdout-v1.0/expected-decisions.json',P/'datasets/holdout-v1.0/entered-assurance-authority.json']
payload={'workflow_id':'SA-REG-EVIDENCE-GATED-001','workflow_version':'1.7','validation_id':'SA-REG-HOLDOUT-001','validation_version':'1.0','dataset_id':'SA-REG-HOLDOUT-001','dataset_version':'1.0','status':'frozen_pre_holdout','model':'gpt-4o-mini-2024-07-18','temperature':0,'case_count':16,'maximum_api_call_count':16,'holdout_run_count':0,'evaluation_count':0,'retry_count_permitted':0,'tuning_after_observation_permitted':False,'v1_5_certification_lineage_sha256':sha(P/'workflows/evidence-gated-v1.5/certification/contract-certification-v1.5.json'),'frozen_v1_7_workflow_meta_sha256':sha(P/'workflows/evidence-gated-v1.7/workflow-v1.7.meta.json'),'artefact_sha256':{str(x.relative_to(P)):sha(x) for x in sorted(runtime+shared)},'evaluator_only_sha256':{str(x.relative_to(P)):sha(x) for x in evaluator}}
META.write_text(json.dumps(payload,indent=2)+'\n'); print(f"Frozen holdout harness: {len(payload['artefact_sha256'])} execution artefacts, 2 evaluator-only authorities, 16 cases")
