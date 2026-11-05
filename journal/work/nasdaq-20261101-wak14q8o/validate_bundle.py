import json,subprocess
from pathlib import Path
W=Path('/Users/frankzhang/Desktop/投研助手/journal/work/nasdaq-20261101-wak14q8o')
T=Path('/Users/frankzhang/.claude/plugins/cache/touyan-local/touyan/0.3.1/scripts')
def load(p):return json.loads((W/p).read_text())
def save(p,v):(W/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
doc=load('sources-before-selection.json');community=load('community/sources.json')
for r in community['candidates']:
 r['id']='COMM-'+r['id'];r['selection']['selected']=False;r['selection']['reason']='Retained investigation lead; original discussion too indirect for Nasdaq attribution, or original text unavailable.';doc['candidates'].append(r)
for k,v in community['source_status'].items():doc['source_status']['community_'+k]=v
# Parent preflight placeholders are replaced by actual subtask outcomes.
doc['source_status']['community']={'status':'partial','reason':'Actual57.35s public engine run plus supplemental retrieval; insufficient relevant original community evidence for causal attribution. Polymarket not_run.'}
save('sources-before-selection.json',doc)
a=load('audit.json');a['community_audit']='community/audit.json';a['company_audit']='facts/query-log.json';save('audit.json',a)
commands=[['research_plan.py',str(W/'plan.json')],['sources.py','validate',str(W/'sources-before-selection.json')],['sources.py','select',str(W/'sources-before-selection.json'),'--out',str(W/'selected-sources.json')]]
for i,args in enumerate(commands):
 cmd=['python3',str(T/args[0])]+args[1:];p=subprocess.run(cmd,text=True,capture_output=True);log='validation-'+str(i)+'.log';(W/log).write_text(p.stdout+p.stderr);a['execution'].append({'command':cmd,'exit_code':p.returncode,'log':log});print(args[0],p.returncode,p.stdout[:1800]);save('audit.json',a)
 if p.returncode:raise SystemExit(p.returncode)
save('sources.json',load('selected-sources.json'))
cmd=['python3',str(T/'check_claims.py'),str(W/'claims.json'),'--sources',str(W/'sources.json'),'--json'];p=subprocess.run(cmd,text=True,capture_output=True);(W/'claims-validation.log').write_text(p.stdout+p.stderr);a['execution'].append({'command':cmd,'exit_code':p.returncode,'log':'claims-validation.log'});save('audit.json',a);print(p.stdout);raise SystemExit(p.returncode)
