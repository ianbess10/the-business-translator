#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent; PROJECT=HERE.parents[1]
def load(name): return json.loads((HERE/name).read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    gates=load('approval-gates.json'); decision=load('go-no-go.json'); schema=load('pilot-record.schema.json')
    Draft202012Validator.check_schema(schema)
    ids=[x['gate_id'] for x in gates['gates']]
    if len(ids)!=10 or len(set(ids))!=10: raise RuntimeError('Pilot requires ten unique approval gates')
    approved=all(x['status']=='approved' and x['approver_name'] and x['decision_at'] and x['evidence_reference'] for x in gates['gates'])
    if gates['execution_permitted'] != approved: raise RuntimeError('Execution permission disagrees with approval evidence')
    if decision['decision']=='no_go' and gates['execution_permitted']: raise RuntimeError('NO-GO record conflicts with execution permission')
    v17=PROJECT/'workflows/evidence-gated-v1.7/workflow-v1.7.meta.json'
    if not v17.exists(): raise RuntimeError('Frozen v1.7 authority is missing')
    print(f"Operational pilot preflight: design valid; approvals={sum(x['status']=='approved' for x in gates['gates'])}/10; execution_permitted={str(gates['execution_permitted']).lower()}; v1.7_manifest_sha256={sha(v17)}")
    return 0 if gates['execution_permitted'] else 2
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as exc: print(f'ERROR: {exc}',file=sys.stderr); raise SystemExit(1)
