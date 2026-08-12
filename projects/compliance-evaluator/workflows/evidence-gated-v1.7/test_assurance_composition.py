#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
from pipeline import compose_assurance,resolve_routing
W=Path(__file__).resolve().parent; P=W.parents[1]
def main():
 policy=json.loads((P/'policies/assurance-composition-v1.0/policy.json').read_text()); fixtures=json.loads((P/'policies/assurance-composition-v1.0/boundary-fixtures.json').read_text())['fixtures']
 assert policy['status']=='approved_synthetic' and policy['approval']['approval_status']=='accepted'
 runtime=''.join((W/n).read_text() for n in ('pipeline.py','run_regression.py'))
 assert not re.search(r'(?<![A-Z])(?:AML|CON)-[0-9]{3}(?![0-9])',runtime)
 for fixture in fixtures:
  got=compose_assurance(fixture['coverage_state'],fixture['evidence_condition'],fixture['workstream'],policy); want=fixture['expected']
  if 'terminal_disposition' in want: assert got['terminal_disposition']==want['terminal_disposition']; continue
  assert got['assurance_outcome']==want['headline']; assert got['gap_types']==sorted(want['gap_types']); assert got['gap_severity']==want['severity']; assert got['remediation_action_types']==sorted(want['action_types']); assert got['escalation_required']==want['escalation_required']; assert got['escalation_roles']==sorted(want['escalation_roles'])
 partial_adverse=compose_assurance('partial','adverse_operating_evidence','market_conduct',policy); assert partial_adverse['gap_types']==['operating_exception','partial_coverage'] and partial_adverse['remediation_action_types']==['mapping_review','operating_remediation'] and partial_adverse['escalation_required']
 profile=json.loads((P/'profiles/synthetic-investment-wealth-institution-v1.0.json').read_text()); rb=json.loads((P/'rulebooks/coverage-evidence-v1.0/rulebook.json').read_text()); mapping={'current_mapping_control_ids':['C-CON-006']}; observations={'observations':[{'requirement_id':'ER-CON-ADVERSE-001'}]}; approved={'routing':{'proposed_owner_role':'Conduct Risk Officer'}}
 routed=resolve_routing(partial_adverse['remediation_routing'],mapping,observations,approved,profile,rb,'market_conduct'); assert routed=={'mapping_review':['Conduct Risk Officer'],'operating_remediation':['Complaints Manager','Conduct Risk Officer']}
 print(f'evidence_gated_v1_6_composition_passed: {len(fixtures)}/{len(fixtures)} general boundaries, concurrent conditions, accountable routing and escalation floor exact'); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except Exception as exc: print(f'ERROR: {exc}',file=sys.stderr); raise SystemExit(1)
