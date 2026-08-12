#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    files=[p for p in HERE.iterdir() if p.is_file() and p.name!='pilot-v1.0.meta.json' and '__pycache__' not in p.parts]
    payload={'pilot_id':'SA-REG-OP-PILOT-001','version':'1.0','status':'governance_design_frozen_execution_not_approved','execution_count':0,'work_item_count':0,'minimum_target_work_items':40,'artefact_sha256':{p.name:sha(p) for p in sorted(files)}}
    (HERE/'pilot-v1.0.meta.json').write_text(json.dumps(payload,indent=2)+'\n')
    print(f"Operational pilot governance design frozen: {len(files)} artefacts; execution remains prohibited")
if __name__=='__main__': main()
