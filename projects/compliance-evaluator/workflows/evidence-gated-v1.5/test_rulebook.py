#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
from rulebook import derive_evidence_assessment,derive_mapping,validate_observations,validate_rulebook
W=Path(__file__).resolve().parent; P=W.parents[1]
def main():
 rb=json.loads((P/'rulebooks/coverage-evidence-v1.0/rulebook.json').read_text()); profile=json.loads((P/'profiles/synthetic-investment-wealth-institution-v1.0.json').read_text()); cat={x['control_id'] for x in profile['controls']}; validate_rulebook(rb,cat)
 text=json.dumps(rb); assert not re.search(r'(?<![A-Z-])(?:AML|CON)-[0-9]{3}(?![0-9])',text); assert not re.search(r'EV-(?:AML|CON)-[0-9]+',text)
 assert derive_mapping('GEN',['C-CON-006','C-CON-007'],rb,cat)['mapping_completeness']=='complete'; assert derive_mapping('GEN',['C-CON-006'],rb,cat)['mapping_completeness']=='partial'; assert derive_mapping('GEN',['C-CON-007'],rb,cat)['mapping_completeness']=='partial'
 cases=[
  ({'case_id':'G1','presented_evidence':[{'evidence_id':'E1','evidence_type':'procedure','status':'supplied'}]}, {'case_id':'G1','observations':[{'evidence_id':'E1','requirement_id':'ER-CON-DESIGN-001','observed_state':'present_deficient','rationale':'generic'}],'rationale':'generic'},'design_deficiency'),
  ({'case_id':'G2','presented_evidence':[{'evidence_id':'E2','evidence_type':'completed_control_record','status':'missing'}]}, {'case_id':'G2','observations':[{'evidence_id':'E2','requirement_id':'ER-CON-OPERATE-001','observed_state':'missing','rationale':'generic'}],'rationale':'generic'},'missing_operating_evidence'),
  ({'case_id':'G3','presented_evidence':[{'evidence_id':'E3','evidence_type':'completed_control_record','status':'supplied'}]}, {'case_id':'G3','observations':[{'evidence_id':'E3','requirement_id':'ER-CON-ADVERSE-001','observed_state':'adverse_indicator_present','rationale':'generic'}],'rationale':'generic'},'adverse_operating_evidence')]
 for case,payload,want in cases: validate_observations(payload,case,rb); assert derive_evidence_assessment(payload,rb)==want
 print('evidence_gated_v1_5_rulebook_passed: approval, anti-case-identity, deterministic coverage and typed evidence derivation'); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except Exception as e: print(f'ERROR: {e}',file=sys.stderr); raise SystemExit(1)
