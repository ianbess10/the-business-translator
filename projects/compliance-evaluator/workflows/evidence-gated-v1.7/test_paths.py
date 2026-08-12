#!/usr/bin/env python3
import json,sys
from pathlib import Path
from rulebook import derive_mapping,validate_rulebook
W=Path(__file__).resolve().parent; P=W.parents[1]
def main():
 rb=json.loads((P/'rulebooks/coverage-evidence-v1.0/rulebook.json').read_text()); profile=json.loads((P/'profiles/synthetic-investment-wealth-institution-v1.0.json').read_text()); cat={x['control_id'] for x in profile['controls']}; validate_rulebook(rb,cat)
 cases=[]
 for n in ('aml-cft.json','market-conduct.json'): cases+=json.loads((P/'datasets/baseline-v1.0/inputs'/n).read_text())
 entered=[]
 for c in cases:
  if c['upstream_obligation']['supplied'] is True and c['upstream_obligation']['status']=='approved': entered.append(derive_mapping(c['case_id'],c['proposed_mapping']['control_ids'],rb,cat))
 assert len(cases)==24 and len(entered)==8 and all(x['current_mapping_control_ids'] for x in entered)
 assert not (P/'results/evidence-gated-v1.7').exists()
 print('evidence_gated_v1_7_paths_passed: 24 frozen routing paths and 8 deterministic approved-rulebook mappings without labels'); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except Exception as e: print(f'ERROR: {e}',file=sys.stderr); raise SystemExit(1)
