import json
from pathlib import Path
R=Path('/Users/frankzhang/Desktop/投研助手/evidence/rebuild-20261031/live')
def load(n): return json.loads((R/n).read_text())
def save(n,d): (R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
report=load('report.json'); plan=load('plan.json'); sources=load('sources.json')
report['task']=plan['task']='资本投入与现金负担比较'
for item in report['limitations']: item['material']=False
report['limitations'].insert(0,{'text':'FY25Q4 历史机制案例，证据于当前检索时点冻结。','material':True,'claim_ids':['C1','C2']})
f=report['findings'][2]; f['claim_ids']=['C4','C5']; f['why_it_matters']='同时避免漏计租赁本金和重复扣经营现金项。'
for c in sources['candidates']:
 if c['id']=='S19':
  c['publisher']='TechRadar'; c['origin_id']=None; c['origin_basis']='Unused fetched TechRadar article; author and origin family not resolved. No HN attribution.'
  c['access_status']='ok'; c['quote']='Microsoft says it will spend billions this years as AI moves pay off' if False else ''; c['locator']='raw/fetched/techradar/body.txt';
report['limitations'].append({'text':'社区上下文：HN 用户 _aavaa_ 质疑分析师预期与公司指引的基准混用，只记录其个人观点，不作为现金算法依据。','material':False,'claim_ids':['C7']})
save('report.json',report); save('plan.json',plan); save('sources.json',sources)
print('Final content updated; frozen claim texts unchanged.')
