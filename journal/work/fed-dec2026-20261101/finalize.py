# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime, timezone
import json,subprocess
W=Path('/Users/frankzhang/Desktop/投研助手/journal/work/fed-dec2026-20261101')
TY=Path('/Users/frankzhang/.claude/plugins/cache/touyan-local/touyan/0.4.1')
def load(n): return json.loads((W/n).read_text())
def save(n,x): (W/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
a=load('audit.json')
a['collector_queries']=load('facts.json')['queries']
a['community_execution']=load('community-execution.json')
a['community_candidates_path']=str(W/'community.json')
a['candidate_pool_path']=str(W/'sources-before-selection.json')
a['review']={'report_path':str(W/'review.json'),'status':'completed','findings':load('review.json'),'dispositions':load('review-dispositions.json')}
a['queries'].extend([{'url':'https://apnews.com/article/991eeb23f8acd1e84b11de9b35278681','status':'error','reason':'WebFetch unable to fetch'},{'url':'https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20261028.pdf','status':'ok','reason':'WebFetch downloaded PDF; text extracted through ephemeral uv pypdf with isolated Python'},{'url':'https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm','status':'ok','purpose':'核验此前加息而非降息'}])
a['execution'].extend([{'command':'urllib request official statement','exit_code':1,'reason':'HTTP403；已有WebFetch原文提取，不影响该材料核验'},{'command':'python3 -I prepare_evidence.py','exit_code':1,'reason':'初版UTF8声明错误，已补齐后执行成功'},{'command':'sources validate','exit_code':1,'reason':'未核验origin_id初版为空字符串，已改null'},{'command':'check_claims','exit_code':1,'reason':'R6命中推断中的否定句泛化词；改成精确委员会承诺表述，未提高判断强度'},{'command':'build_bundle.py','exit_code':0,'reason':'来源75候选、12主张、全链check已通过'}])
a['targeted_followup']=load('review-dispositions.json')['targeted_followup']
a['execution'].append({'command':'build_bundle.py after SEP followup','exit_code':0,'reason':'76来源候选，13主张，全链check通过'})
for log in sorted(W.glob('*.log')): a.setdefault('logs',[]).append(str(log))
save('audit.json',a)
commands=[['analysis_contract.py','check','--plan',W/'plan.json','--report',W/'report.json','--claims',W/'claims.json','--sources',W/'sources.json'],['render_report.py',W/'report.json','--claims',W/'claims.json','--sources',W/'sources.json','--out-dir',W/'output','--overwrite'],['research_run.py','archive','--report',W/'report.json','--claims',W/'claims.json','--sources',W/'sources.json','--plan',W/'plan.json','--audit',W/'audit.json']]
for j,c in enumerate(commands):
    cmd=['python3',str(TY/'scripts'/c[0]),*map(str,c[1:])]
    r=subprocess.run(cmd,capture_output=True,text=True)
    log=W/('final-'+str(j)+'.log');log.write_text(r.stdout+r.stderr)
    print(r.stdout,r.stderr)
    if r.returncode: raise SystemExit(r.returncode)
    if j==2: save('archive-result.json',json.loads(r.stdout))
    else:
        a['execution'].append({'command':cmd,'exit_code':r.returncode,'log':str(log)})
        save('audit.json',a)
