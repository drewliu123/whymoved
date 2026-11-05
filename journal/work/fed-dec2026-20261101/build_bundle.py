# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime, timezone
import json, subprocess
W=Path('/Users/frankzhang/Desktop/投研助手/journal/work/fed-dec2026-20261101')
TY=Path('/Users/frankzhang/.claude/plugins/cache/touyan-local/touyan/0.4.1')
def read(n): return json.loads((W/n).read_text())
def save(n,v): (W/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def run(script,*args):
    r=subprocess.run(['python3',str(TY/'scripts'/script),*map(str,args)],capture_output=True,text=True)
    (W/(script.replace('.py','')+'-'+str(len(list(W.glob('*.log'))))+'.log')).write_text(r.stdout+r.stderr)
    print(r.stdout,r.stderr)
    if r.returncode: raise SystemExit(r.returncode)
notes=read('official-notes.json')
now=datetime.now(timezone.utc).isoformat()
p=read('plan.json'); p['as_of']=now; save('plan.json',p)
s=[]
for n in notes['sources']:
    z={**n,'canonical_url':n['url'],'retrieved_at':notes['retrieved_at'],'supports':['fact'],'evidence_kind':'document','access_status':'ok','selection':{'selected':True,'reason':'官方资料直接支持会议安排、政策基准与收紧条件。','relevance':'direct','purpose':'核对事件定义与政策现状','priority':'decisive'}}
    s.append(z)
# Additional researcher-selected evidence is frozen separately after collector review.
extra=read('additional-evidence.json')
s.extend(extra['sources'])
community=read('community.json')
for idx,z in enumerate(community['candidates']):
    z=dict(z); z['id']='COMM'+str(idx+1); s.append(z)
extra['source_status']['community']={'status':'partial','reason':'引擎已执行，原文未核实，无正式入选社区证据；比较词触发内部拆分，第二分支偏题。'}
source_doc={'schema_version':2,'as_of':now,'historical':False,'candidates':s,'source_status':extra['source_status']}
save('sources-before-selection.json',source_doc)
run('sources.py','validate',W/'sources-before-selection.json')
run('sources.py','select',W/'sources-before-selection.json','--out',W/'selected-sources.json')
save('sources.json',read('selected-sources.json'))
claims=[]
def fact(i,t,ss): claims.append({'id':i,'text':t,'type':'fact','as_of':now,'sources':[{'source_id':v} for v in ss]})
def inference(i,t,b): claims.append({'id':i,'text':t,'type':'inference','as_of':now,'sources':[],'basis':b})
fact('C1','2026年12月FOMC例行会议安排在12月8—9日；10月例会为27—28日。',['S1'])
fact('C2','10月28日FOMC维持联邦基金利率目标区间3.75%—4.00%。',['S2','S3'])
fact('C3','10月声明评估经济增长强劲、失业率大致稳定、通胀仍高于目标；10比2通过维持利率，Cook和Hammack主张加息25个基点。',['S2'])
fact('C4','FOMC每年举行八次例行会议。',['S4'])
claims.extend([{**x,'as_of':now} for x in extra['claims']])
inference('C5','按已公布例会安排，12月只有一次常规决策机会；若加息25个基点，目标区间由3.75%—4.00%变成4.00%—4.25%，属于加息一次。临时行动不包含在这个次数判断中。',['C1','C2','C4'])
for x in extra['inferences']: inference(x['id'],x['text'],x['basis'])
save('claims.json',{'schema_version':2,'as_of':now,'claims':claims})
run('check_claims.py',W/'claims.json','--sources',W/'sources.json','--json')
r=extra['report']
r.update({'schema_version':2,'question':p['question'],'type':p['type'],'task':p['task'],'as_of':now})
d=p['research_design']
a={k:d[k] for k in ['question_kind','method','price_relevance','baseline','mechanism_chain']}
a.update({'version':1,'baseline_claim_ids':['C1','C2'],'hypotheses':[{'id':h['id'],'explanation':h['explanation']} for h in p['hypotheses']],'conclusion':r['answer']['text'],'conclusion_claim_ids':r['answer']['claim_ids'],'model_status':'not_applicable','model_reason':'本轮为离散政策情景与会议次数研究，不适用企业经营或DCF固定模型。','models':[],'market':extra['market'],'tests':[]})
for t in d['discrimination_tests']:
    a['tests'].append({'id':t['id'],'outcomes':t['outcomes'],**extra['tests'][t['id']]})
r['analysis']=a
save('report.json',r)
run('analysis_contract.py','check','--plan',W/'plan.json','--report',W/'report.json','--claims',W/'claims.json','--sources',W/'sources.json')
