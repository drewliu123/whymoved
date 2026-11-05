from pathlib import Path
import json, re, subprocess, hashlib
from decimal import Decimal

ROOT=Path('/Users/frankzhang/Desktop/投研助手')
BASE=ROOT/'journal/four-type-validation-20261031'
results={}
for key in ('event','asset','theme','actor'):
 case=BASE/key
 errors=[]
 required=['report.md','report.json','claims.json','sources.json','plan.json','calculations.json','validation.json']
 for name in required:
  if not (case/name).is_file(): errors.append('missing '+name)
 if errors:
  results[key]={'status':'incomplete','errors':errors};continue
 report=json.loads((case/'report.json').read_text()); ledger=json.loads((case/'claims.json').read_text())
 ids={c['id'] for c in ledger.get('claims',[])}
 for name in ('title','question','as_of','status','answer','findings','tables','alternatives','watch','gaps','sources'):
  if name not in report:errors.append('report missing '+name)
 if not ledger.get('claims'):errors.append('empty claims ledger')
 for claim in ledger.get('claims',[]):
  for source in claim.get('sources',[]):
   local=source.get('local_evidence')
   if local and not (case/local).is_file():errors.append('missing local evidence '+str(local))
 def walk(obj):
  if isinstance(obj,dict):
   for k,v in obj.items():
    if k in ('claim_ids','answer_claim_ids'):
     for cid in v:
      if cid not in ids:errors.append('unresolved report reference '+str(cid))
    walk(v)
  elif isinstance(obj,list):
   for v in obj:walk(v)
 walk(report)
 for table in report.get('tables',[]):
  columns=table.get('columns',table.get('headers',[]))
  for row in table.get('rows',[]):
   if isinstance(row,list) and len(row)!=len(columns):errors.append('table width mismatch '+table.get('title',''))
 command=['python3',str(ROOT/'scripts/check_claims.py'),str(case/'claims.json'),'--json']
 run=subprocess.run(command,capture_output=True,text=True)
 (case/'final-check-claims.stdout.json').write_text(run.stdout);(case/'final-check-claims.stderr.txt').write_text(run.stderr)
 if run.returncode:errors.append('check_claims exit '+str(run.returncode))
 try: check=json.loads(run.stdout)
 except ValueError:check={'raw':run.stdout}
 results[key]={'status':'structural_pass' if not errors else 'fail','errors':errors,'claim_count':len(ids),'check_claims':check,'command':command,'exit_code':run.returncode,'semantic_review':'separate independent review; not proven by structural check','sha256':{n:hashlib.sha256((case/n).read_bytes()).hexdigest() for n in required}}
asset=BASE/'asset'
if (asset/'calculations.json').exists():
 c=json.loads((asset/'calculations.json').read_text()); inp={k:Decimal(v) for k,v in c['inputs'].items()};r=c['results']
 assert inp['gaap_gross_profit_q2_b']==Decimal(r['q2_gross_profit_b'])
 assert inp['revenue_q3_midpoint_b']*inp['gm_q3_midpoint']==Decimal(r['q3_midpoint_implied_gross_profit_b'])
 assert inp['cfo_h1_b']-inp['cfo_q2_b']==Decimal(r['q1_ocf_b'])
 results['asset']['independent_numeric_assertions']=3
out={'cases':results,'scope':'development cases; structural and deterministic checks only','all_present_and_structural_pass':all(r['status']=='structural_pass' for r in results.values())}
(BASE/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({k:{'status':v['status'],'claims':v.get('claim_count'),'errors':v['errors']} for k,v in results.items()},ensure_ascii=False,indent=2))
raise SystemExit(0 if out['all_present_and_structural_pass'] else 1)
