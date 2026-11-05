# -*- coding: utf-8 -*-
import json,copy
from pathlib import Path
W=Path('/Users/frankzhang/Desktop/投研助手/journal/work/warsh-20261101')
def load(n):return json.loads((W/n).read_text())
def save(n,x):(W/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
r=load('report.json');c=load('claims.json');s=load('sources-before-selection.json');a=load('audit.json')
for sid,quote,loc in [('S38','economic growth is higher, but that doesn’t tell me that economic growth is somehow causing inflation','PRELIMINARY transcript p.16, Howard Schneider Q&A; pp.16 lines about tighter financial conditions'),('S39','in 2027, one meeting will focus exclusively on broad monetary policy strategy','PRELIMINARY transcript p.3, opening statement; neither rate vote nor policy statement anticipated; starting next fall; 2028 described as expectation')]:
 row=copy.deepcopy(next(x for x in s['candidates'] if x['id']=='S22'));row.update(id=sid,quote=quote,locator=loc);s['candidates'].append(row)
c['claims'].append(dict(id='C21',text='沃什10月28日表示，多数同事并不判断经济过热；增长较快本身不说明它正在造成通胀。他认为生产率已有改善，并希望通过收紧金融条件实现价格稳定，而不必主动损害就业。',type='view',as_of=c['as_of'],sources=[dict(source_id='S38')]))
c['claims'].append(dict(id='C22',text='沃什10月28日宣布，从2027年秋开始，全年八次FOMC会议中的一次将专门讨论战略，预计不进行利率表决或发布政策声明；其预计2028年有两次战略讨论、六次政策会议。2028年安排属于其预期。',type='fact',as_of=c['as_of'],sources=[dict(source_id='S39')]))
r['findings'][3]['text']+=' 已宣布的会议安排也有调整：从2027年秋起，全年八次会议中的一次专门讨论战略，预计不进行利率表决或发布政策声明；2028年两次战略会议仍是其预期。'
r['findings'][3]['claim_ids'].append('C22')
r['findings'][4]['text']='沃什认为生产率改善可能使较快增长与价格稳定兼容：其10月表示，多数同事并不判断经济过热，增长强本身不说明它正在造成通胀；其希望通过收紧金融条件实现价格稳定，而不必主动损害就业。同时，生产率改善仍难精确测量，大部分近期改善早于超级智能讨论。研究上仍需区分AI建设先拉动需求、未来生产率改善再扩展供给的两条路径，不能据技术叙事直接推出当期降息空间。'
r['findings'][4]['claim_ids'].append('C21')
r['findings'][4]['increment']['detail']='补全其强增长不等于过热的判断，再区分研究者提出的AI需求与供给路径。'
r['findings'][5]['text']=r['findings'][5]['text'].replace('减少债券持有并行','减少长期债券持有并行')+' 本轮仅解释条件传导，不评估即时市场定价。'
next(x for x in c['claims'] if x['id']=='C17')['text']=next(x for x in c['claims'] if x['id']=='C17')['text'].replace('减少债券持有同时出现','减少长期债券持有同时出现')
r['limitations']=[dict(text='记者会引用为美联储官方标注PRELIMINARY的文本版本。',material=False,claim_ids=['C10','C12','C14','C21','C22'])]
r['alternatives'][0]['text']='最强竞争解释是委员会对通胀和就业状况作常规反应，而非沃什个人偏好的独立作用；两位希望继续加息的委员，也说明其不代表委员会中最鹰派的立场。现有行动支持的结论限于：快速宽松叙事与当前记录不符。'
r['alternatives'][0]['claim_ids']=['C3','C5','C6','C7']
a['review']=dict(status='completed',blocking_findings=0,findings=[dict(severity='material-nonblocking',issue='生产率段遗漏增长强不等于过热的本人判断',disposition='已核对原文第16页，加入C21/S38并补全文本。'),dict(severity='minor',issue='遗漏2027年专门战略会议安排',disposition='已核对第3页，加入C22/S39，区分2027宣布安排与2028预期。'),dict(severity='minor',issue='重复限制',disposition='限制留在相关判断附近，limitations仅留PRELIMINARY版本说明。')],core_conclusion='独立回查身份及9、10月政策记录，无阻塞问题；保留行动不支持快速宽松的结论，不作个人动机识别。',followups='一轮定向原文核对已完成，无新增检索。')
a['execution'].append(dict(command=['python3','build_bundle.py'],exit_code=0,note='Initial run syntax error corrected with explicit UTF-8 source encoding before successful execution.'))
save('report.json',r);save('claims.json',c);save('sources-before-selection.json',s);save('audit.json',a)
print('Applied all three review findings; 22 claims, 39 candidate fragments.')
