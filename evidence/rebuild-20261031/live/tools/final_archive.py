import json,sys,runpy,os,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
R=Path('/Users/frankzhang/Desktop/投研助手/evidence/rebuild-20261031/live')
S='/Users/frankzhang/Desktop/投研助手/scripts'
sys.path.insert(0,S); os.environ['TOUYAN_HOME']=str(R/'isolated-home'); os.environ['PYTHONDONTWRITEBYTECODE']='1'
from sources import validate_sources
from check_claims import validate_ledger
from research_plan import validate_plan
from render_report import validate_report,render_markdown,render_html,write_outputs
from research_run import archive_run,load_run
load=lambda n:json.loads((R/n).read_text())
report,claims,sources,plan=[load(n) for n in ('report.json','claims.json','sources.json','plan.json')]
errors=validate_sources(sources)+validate_plan(plan)+validate_report(report,claims,sources)
assert not errors,errors
assert validate_ledger(claims,sources)['passed']
page,md=render_html(report,claims,sources),render_markdown(report,claims,sources)
write_outputs(R/'final-rendered',md,page)
audit={'schema_version':2,'role':'untrusted execution metadata; no quality certification','queries':load('raw/searches.json'),'engine':load('logs/engine-command.json'),'diagnostic':{'file':'raw/parent-diagnose.json','scope':'parent-provided; run source_status is in raw/last30days.json'},'commands':load('logs/commands.json'),'previous_outcomes':load('logs/outcomes.json'),'arithmetic':load('logs/arithmetic-check.json'),'paired_replay':load('logs/comparison-metadata.json'),'content_review':{'reviewer':'same author, nonblind','correction':'Only period scope early. Operational diagnostics moved to later limitations. Community view removed as reference for cash arithmetic. Unused TechRadar metadata corrected.'},'final_api_validation':{'sources':[],'plan':[],'claims':validate_ledger(claims,sources),'report':[],'rendered':True},'limitations':['No browser visual check','No entire old-plugin run or independent quality/alpha evaluation','13 engine candidates rejected; useful community source fetched through supplement','Residual 0.621B not reconciled','Final archive APIs validate schema and hashes, not truth of metadata']}
(R/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
a=archive_run(R/'report.json',R/'claims.json',R/'sources.json',R/'plan.json',R/'calculations.json',home=R/'isolated-home',audit_path=R/'audit.json')
verified=load_run(a['run_id'],home=R/'isolated-home')
for name in ('report.md','report.html'): assert (R/'final-rendered'/name).read_bytes()==(Path(a['path'])/name).read_bytes()
assert verified['manifest']['audit_role']=='untrusted_metadata'
end=datetime.now(timezone.utc); start=datetime.fromisoformat((R/'logs/retrieval-start.txt').read_text())
result={'passed':True,'final_run_id':a['run_id'],'final_archive_path':a['path'],'audit_role':verified['manifest']['audit_role'],'completed_at':end.isoformat(),'wall_seconds_from_retrieval_start_through_final_archive':round((end-start).total_seconds(),3),'native_queries':5,'engine_queries':2,'direct_algolia_queries':2,'total_logical_search_queries':9,'raw_engine_exit':0,'engine_seconds':5.3,'note':'9 search queries only; 2 host WebFetch requests and 10 urllib GETs (2 are Algolia search requests) also recorded. Excludes earlier bootstrap reads and first 2 WebSearch calls from wall clock. No further retrieval for replay. Final validation through APIs exit0.'}
(R/'logs/final-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
