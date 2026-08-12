#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,sys,time,uuid
from datetime import datetime,timezone
from pathlib import Path
from openai import OpenAI
from jsonschema import Draft202012Validator
from provider_contract import assert_provider_subset
W=Path(__file__).resolve().parent; PLAN=W/'certification/plan-v1.5.json'; OUT=W/'certification/contract-certification-v1.5.json'; MODEL='gpt-4o-mini-2024-07-18'
def h(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def write(x): OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(x,indent=2)+'\n')
def main():
 if OUT.exists(): raise RuntimeError('Certification already exists')
 if not os.environ.get('OPENAI_API_KEY'): raise RuntimeError('OPENAI_API_KEY required')
 plan=json.loads(PLAN.read_text()); assert plan['planned_call_count']==1 and not plan['benchmark_cases_used'] and not plan['evaluator_labels_used']
 schema_path=W/'schemas/evidence-observation-stage.schema.json'; prompt_path=W/'prompts/evidence-observation-stage-v1.5.md'; schema=json.loads(schema_path.read_text()); assert_provider_subset(schema)
 evidence={'certification_id':f'v1.5-{uuid.uuid4()}','status':'running','started_at':now(),'completed_at':None,'purpose':plan['purpose'],'provider':'openai','endpoint':'chat_completions','model_requested':MODEL,'temperature':0,'planned_call_count':1,'completed_call_count':0,'benchmark_cases_used':False,'evaluator_labels_used':False,'model_quality_scored':False,'records':[],'error':None}; write(evidence)
 user={'certification_only':True,'required_semantic_fixture':plan['expected_output']}; client=OpenAI(api_key=os.environ['OPENAI_API_KEY'],base_url=os.environ.get('OPENAI_BASE_URL','').strip() or 'https://api.openai.com/v1'); started=time.monotonic()
 try:
  r=client.chat.completions.create(model=MODEL,temperature=0,messages=[{'role':'system','content':prompt_path.read_text()},{'role':'user','content':json.dumps(user)}],response_format={'type':'json_schema','json_schema':schema}); parsed=json.loads(r.choices[0].message.content or '{}'); Draft202012Validator(schema['schema']).validate(parsed)
  assert parsed['case_id']==plan['case_id'] and len(parsed['observations'])==1
  evidence['records']=[{'stage':'evidence','case_id':plan['case_id'],'benchmark_case':False,'response_format_name':schema['name'],'schema_sha256':h(schema_path),'prompt_sha256':h(prompt_path),'response_id':r.id,'response_model':r.model,'finish_reason':r.choices[0].finish_reason,'provider_schema_accepted':True,'transport_output_valid':True,'semantic_output_valid':True,'latency_ms':round((time.monotonic()-started)*1000),'certified_at':now()}]; evidence['completed_call_count']=1; evidence['status']='completed'; evidence['completed_at']=now(); write(evidence)
 except Exception as e: evidence['status']='failed'; evidence['completed_at']=now(); evidence['error']=f'{type(e).__name__}: {e}'; write(evidence); raise
 print('v1.5 provider contract certification completed: 1/1 changed non-benchmark evidence schema accepted'); return 0
if __name__=='__main__':
 try: raise SystemExit(main())
 except Exception as e: print(f'ERROR: {e}',file=sys.stderr); raise SystemExit(1)
