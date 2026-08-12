#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
W=Path(__file__).resolve().parent; P=W.parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 lineage=json.loads((W/'certification/inherited-contract-lineage-v1.6.json').read_text()); assert lineage['status']=='accepted_no_new_provider_call_required' and lineage['changed_provider_contract_count']==0 and lineage['new_certification_call_count']==0
 paths={'source_support':(W/'prompts/source-support-stage-v1.3.md',W/'schemas/source-support-stage.schema.json'),'evidence':(W/'prompts/evidence-observation-stage-v1.5.md',W/'schemas/evidence-observation-stage.schema.json')}
 for item in lineage['contracts']:
  prompt,schema=paths[item['stage']]; assert sha(prompt)==item['prompt_sha256'] and sha(schema)==item['schema_sha256']; source=P/item['certification_source']; assert sha(source)==item['certification_source_sha256']; assert item['provider_contract_changed'] is False and item['inheritance_accepted'] is True
 assert sha(W/'provider_contract.py')==lineage['shared_request_components']['provider_contract_module_sha256']; assert sha(W/'execution_contract.py')==lineage['shared_request_components']['execution_contract_module_sha256']; assert sha(P/lineage['shared_request_components']['request_function_source'])==lineage['shared_request_components']['request_function_source_sha256']
 print('evidence_gated_v1_6_contract_lineage_passed: 2/2 provider contracts byte-identical to certified lineage; 0 new calls required'); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except Exception as exc: print(f'ERROR: {exc}',file=sys.stderr); raise SystemExit(1)
