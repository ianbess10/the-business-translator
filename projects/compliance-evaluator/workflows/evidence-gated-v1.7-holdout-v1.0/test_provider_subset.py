#!/usr/bin/env python3
import json,sys
from pathlib import Path
from provider_contract import assert_provider_subset
W=Path(__file__).resolve().parent
def main():
 for p in (W/'schemas').glob('*.json'): assert_provider_subset(json.loads(p.read_text()))
 print('evidence_gated_v1_6_provider_subset_passed: both unchanged provider contracts remain within the supported subset'); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except Exception as e: print(f'ERROR: {e}',file=sys.stderr); raise SystemExit(1)
