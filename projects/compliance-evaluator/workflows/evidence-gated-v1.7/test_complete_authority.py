#!/usr/bin/env python3
import copy, importlib.util, json
from pathlib import Path

W=Path(__file__).resolve().parent; P=W.parents[1]
S=importlib.util.spec_from_file_location('authority_validator',P/'datasets/baseline-v1.2/validate_authority.py')
if S is None or S.loader is None: raise RuntimeError('Authority validator unavailable')
M=importlib.util.module_from_spec(S); S.loader.exec_module(M)

def rejected(payload):
    try: M.validate(payload); return False
    except (ValueError, KeyError): return True

def main():
    payload=json.loads((P/'datasets/baseline-v1.2/entered-assurance-authority.json').read_text()); M.validate(payload)
    missing=copy.deepcopy(payload); missing['records'].pop(); assert rejected(missing)
    duplicate=copy.deepcopy(payload); duplicate['records'][-1]=copy.deepcopy(duplicate['records'][0]); assert rejected(duplicate)
    invalid=copy.deepcopy(payload); invalid['records'][0]['coverage_state']='legacy_fallback'; assert rejected(invalid)
    extra=copy.deepcopy(payload); extra['records'].append({**copy.deepcopy(extra['records'][0]),'case_id':'CON-013'}); assert rejected(extra)
    runner=(W/'run_regression.py').read_text()
    assert 'entered-assurance-authority' not in runner and '/labels/' not in runner and 'label-authority-overlay' not in runner
    print('evidence_gated_v1_7_complete_authority_passed: exact 8/8 identity; missing, duplicate, invalid and extra authority fail closed; runtime isolated')
    return 0
if __name__=='__main__': raise SystemExit(main())
