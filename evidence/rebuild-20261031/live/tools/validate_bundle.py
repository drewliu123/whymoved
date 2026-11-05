import json, subprocess, sys, os, time, hashlib
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
ROOT=Path('/Users/frankzhang/Desktop/投研助手/evidence/rebuild-20261031/live')
SCRIPTS=Path('/Users/frankzhang/Desktop/投研助手/scripts')
LOG=ROOT/'logs'
records=json.loads((LOG/'commands.json').read_text()) if (LOG/'commands.json').exists() else []

def write(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def run(name,script,*args):
    wrapper='import runpy,sys; sys.path.insert(0,sys.argv.pop(1)); sys.argv.pop(0); runpy.run_path(sys.argv[0],run_name="__main__")'
    cmd=[sys.executable,'-I','-c',wrapper,str(SCRIPTS),str(SCRIPTS/script),*map(str,args)]
    env=os.environ.copy(); env['TOUYAN_HOME']=str(ROOT/'isolated-home'); env['PYTHONDONTWRITEBYTECODE']='1'
    started=datetime.now(timezone.utc).isoformat(); before=time.monotonic()
    p=subprocess.run(cmd,cwd=ROOT/'tools',env=env,capture_output=True,text=True)
    attempt=1+sum(r['step']==name for r in records)
    logstem=name if attempt==1 else name+'-retry'+str(attempt)
    (LOG/(logstem+'.stdout')).write_text(p.stdout); (LOG/(logstem+'.stderr')).write_text(p.stderr)
    rec=dict(step=name,command=cmd,environment={'TOUYAN_HOME':env['TOUYAN_HOME'],'PYTHONDONTWRITEBYTECODE':'1'},started_at=started,elapsed_seconds=round(time.monotonic()-before,4),exit_code=p.returncode,stdout=f'logs/{logstem}.stdout',stderr=f'logs/{logstem}.stderr')
    records.append(rec); write(LOG/'commands.json',records)
    print(name,p.returncode,p.stdout[:1000],p.stderr[:1000])
    if p.returncode: raise SystemExit(p.returncode)
    return p.stdout
run('select','sources.py','select',ROOT/'sources.annotated.json','--out',ROOT/'sources.json')
run('sources-validate','sources.py','validate',ROOT/'sources.json')
run('plan-validate','research_plan.py',ROOT/'plan.json')
run('claims-validate','check_claims.py',ROOT/'claims.json','--sources',ROOT/'sources.json','--json')
calcs=json.loads((ROOT/'calculations.json').read_text())['calculations']
computed={'K1':Decimal('24.2')-Decimal('17.079'),'K2':Decimal('24.2')-Decimal('17.079')-Decimal('6.5'),'K3':Decimal('136.162')-Decimal('64.551'),'K4':Decimal('136.162')-Decimal('64.551')-Decimal('2.283')}
rows=[]
for row in calcs:
    expected=Decimal(str(row['result']['value'])); actual=computed[row['id']]
    rows.append({'id':row['id'],'expected':str(expected),'independently_recomputed':str(actual),'passed':expected==actual})
assert all(r['passed'] for r in rows)
write(LOG/'arithmetic-check.json',{'method':'Independently specified Decimal arithmetic; does not evaluate formula strings','passed':True,'checks':rows,'limitations':'Input truth and accounting bridge need fetched evidence review; arithmetic does not identify residual components. Rounded source values make quarterly differences approximate.'})
run('render','render_report.py',ROOT/'report.json','--claims',ROOT/'claims.json','--sources',ROOT/'sources.json','--out-dir',ROOT/'rendered')
archive=json.loads(run('archive','research_run.py','archive','--report',ROOT/'report.json','--claims',ROOT/'claims.json','--sources',ROOT/'sources.json','--plan',ROOT/'plan.json','--calculations',ROOT/'calculations.json'))
print('archive_result',json.dumps(archive))
runid=archive.get('run_id') or archive.get('manifest',{}).get('run_id')
if not runid:
    runid=next((ROOT/'isolated-home/journal/runs').iterdir()).name
run('archive-show','research_run.py','show',runid)
# Confirm separately rendered and archived outputs are byte-identical and source input isn't mutated.
archivepath=ROOT/'isolated-home/journal/runs'/runid
compare={name:(ROOT/'rendered'/name).read_bytes()==(archivepath/name).read_bytes() for name in ('report.md','report.html')}
assert all(compare.values())
write(LOG/'archive-roundtrip.json',dict(passed=True,run_id=runid,home=str(ROOT/'isolated-home'),rendered_archive_byte_equal=compare,limitations='Local immutable archive/hash loading checked. No real journal, forecasts, publishing, browser visual or external integration claim.'))
ended=datetime.now(timezone.utc)
started=datetime.fromisoformat((LOG/'retrieval-start.txt').read_text())
write(LOG/'outcomes.json',{'completed_at':ended.isoformat(),'elapsed_wall_seconds_from_retrieval_start':round((ended-started).total_seconds(),3),'engine_exit':int((LOG/'last30days.exit').read_text()),'engine_reported_wall_seconds':5.3,'actual_engine_search_queries':2,'native_search_queries':5,'direct_algolia_search_queries':2,'logical_total_search_queries':9,'selected_sources':json.loads((ROOT/'sources.json').read_text())['selection_summary']['selected'],'engine_relevant_selected':0,'supplementary_community_original_selected':1,'report_findings':3,'all_validation_commands_exit_zero':True,'arithmetic_independent_check_passed':True,'archive_run_id':runid,'product_code_modified':False,'scope_note':'Timing starts at runtime preparation immediately before resolver/engine; excludes earlier skill/code reading and 2 pre-engine WebSearch calls. 5.3s is engine own stderr duration. Search counts exclude non-search GETs and unobservable provider internals.'})
