from pathlib import Path
import json, hashlib, shutil, subprocess
from decimal import Decimal, ROUND_HALF_UP

ROOT=Path('/Users/frankzhang/Desktop/投研助手')
BASE=ROOT/'journal/four-type-validation-20261031'
OLD=ROOT/'journal/nvda-full-runs-20261031'
OUT=BASE/'asset'; OUT.mkdir(parents=True, exist_ok=True)
ASOF='2026-10-31T17:14:08Z'
def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def pct(a,b): return (Decimal(str(a))/Decimal(str(b))-1)*100
def num(v): return str(Decimal(v).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
old=json.loads((OLD/'run-0.2.0/claims.json').read_text())
source_index={c['id']:c for c in old['claims']}
price=json.loads((OLD/'run-0.1.1/evidence/price-snapshot.json').read_text())
inputs={'revenue_q2_b': '96.221','revenue_q1_b':'81.615','dc_q2_b':'89','cfo_q2_b':'24.077','cfo_h1_b':'74.421','ar_cash_use_q2_b':'22.346','gm_q2':'.75','revenue_q3_midpoint_b':'108','gm_q3_midpoint':'.74'}
d={k:Decimal(v) for k,v in inputs.items()}
gp2=Decimal('72.142'); gp3=d['revenue_q3_midpoint_b']*d['gm_q3_midpoint']
inputs['gaap_gross_profit_q2_b']='72.142'
cfo1=d['cfo_h1_b']-d['cfo_q2_b']
calc={
 'month_return_pct':num(pct('204.64','228.38')),
 'peak_close_to_month_end_pct':num(pct('204.64','239.24')),
 'last_day_return_pct':num(pct('204.64','213.66')),
 'last_week_return_pct':num(pct('204.64','210.96')),
 'q3_revenue_growth_pct':num(pct(d['revenue_q3_midpoint_b'],d['revenue_q2_b'])),
 'q2_gross_profit_b':str(gp2),'q3_midpoint_implied_gross_profit_b':str(gp3),
 'midpoint_implied_gp_growth_pct':num(pct(gp3,gp2)),
 'q2_ocf_to_revenue_pct':num(d['cfo_q2_b']/d['revenue_q2_b']*100),
 'q1_ocf_b':str(cfo1),'q1_ocf_to_revenue_pct':num(cfo1/d['revenue_q1_b']*100),
 'q3_revenue_range_b':[str(Decimal('108')*Decimal('.98')),str(Decimal('108')*Decimal('1.02'))]
}
save('calculations.json',{'inputs':inputs,'results':calc,'formulas':{'return':'(end/start-1)*100','gross_profit':'revenue * gross_margin','q1_ocf':'half_year_ocf - q2_ocf','cash_conversion':'quarter_ocf / quarter_revenue * 100'},'interpretation':'Q3毛利额为两个指引中点相乘的示例，并非公司另行公布的指引或实现值。现金流/收入不是客户ROI或坏账率。'})
claims=[]
for oldid,newid in [('C1','C1'),('C2','C2'),('C3','C3'),('C4','C4'),('C6','C5'),('C11','C6')]:
    c=json.loads(json.dumps(source_index[oldid])); c['id']=newid;c['as_of']=ASOF
    if oldid=='C11': c['text']='FY2027 Q2经营现金流240.77亿美元，半年累计744.21亿美元；Q2应收账款变动占用现金223.46亿美元。'
    if oldid=='C3': c['text']+=' 同份财报直接披露GAAP毛利额721.42亿美元。'
    for s in c.get('sources',[]):
        s['local_evidence']={'raw/historical/october-response.json':'inputs/historical.json','raw/newsroom/body.txt':'inputs/newsroom.txt','raw/media/body.txt':'inputs/media.txt'}.get(s.get('local_evidence'),s.get('local_evidence'))
        if 'collected_at' in s: s['note']='获取于本轮截点之前；本例复用旧归档，不是新检索。'
        if oldid=='C6': s['date_kind']='update_time; first_publication_unconfirmed'
    claims.append(c)
def infer(cid,text,basis): claims.append({'id':cid,'text':text,'type':'inference','as_of':ASOF,'sources':[],'basis':basis})
infer('C7',f"Q3收入指引中点较Q2高约{calc['q3_revenue_growth_pct']}%；以两项指引中点相乘，Q3示例毛利额799.2亿美元，Q2直接披露GAAP毛利额721.42亿美元，增约{calc['midpoint_implied_gp_growth_pct']}%。这不是已实现利润，也不是股价回报预测。",['C3','C4'])
infer('C8',f"Q2经营现金流/收入约{calc['q2_ocf_to_revenue_pct']}%；从半年减Q2得到Q1经营现金流503.44亿美元，同期收入816.15亿美元，该比值约{calc['q1_ocf_to_revenue_pct']}%。单季变动受营运资本及其他现金流项目影响，应收占用不等于坏账。",['C3','C6'])
infer('C9','这批材料更适合检验增长兑现、利润和现金回收的质量，尚不足以把10月跌幅判定为订单恶化。最后交易日的AI投入回报担忧有媒体归因支持，全月相对表现、估值与预期修订仍缺资料，不能识别整月主因。',['C1','C2','C3','C4','C5','C6'])
infer('C10','最强反方是客户投入回报担忧可能不影响近期GPU采购，收入与毛利额仍能扩张；板块共同重估也可能解释部分回撤，不能只寻找公司特有原因。另一种路径是公司兑现原指引但低于股票隐含要求；区分这些解释需要冻结时点的行业比较、一致预期与估值。',['C3','C4','C5','C7'])
infer('C11','下一次应同口径检查收入对原指引区间的兑现、后续指引、毛利额和现金回收，而不能以单个季度现金流变化直接认定需求失效。',['C3','C4','C6','C7','C8'])
save('claims.json',{'question':'NVDA 10月跌了多少，怎样区分增长、盈利与现金回收？现有材料能解释多少跌幅？','as_of':ASOF,'claims':claims})
sources=[{'id':'S1','title':'NVIDIA FY2027 Q2官方财报（已归档）','url':source_index['C3']['sources'][0]['url'],'published_at':'2026-08-26','quote':'Revenue $96,221 million; Q1 $81,615 million; Q3 revenue $108.0 billion +/-2%; gross margin 74.0% +/-50bps.','local_evidence':'inputs/newsroom.txt'}, {'id':'S2','title':'NVIDIA IR历史行情原始响应（已归档）','url':'https://investor.nvidia.com/stock-info/historical-price-lookup/default.aspx','published_at':'2026-10-30','quote':'09/30 Last 228.38; 10/06 Last 239.24; 10/30 Last 204.64','local_evidence':'inputs/historical.json'}, {'id':'S3','title':'Reuters 10月30日收市报道（已归档）','url':source_index['C6']['sources'][0]['url'],'published_at':'2026-10-30T20:23:00Z','date_kind':'更新时间；首次发布时间未确认','quote':'disappointing quarterly results from Intel and Amazon ... growing worries ... massive spending','local_evidence':'inputs/media.txt'}]
save('sources.json',{'mode':'reuse_frozen_evidence','new_external_fetches':0,'sources':sources,'failed_or_missing':['完整月度行业/指数比较序列','全月事件覆盖','同一截点一致预期及估值']})
findings=[{'title':'月跌幅与高点回撤是两件事','text':'10月价格收益 −10.39%；最高收盘至月末 −14.46%；最后一日 −4.22%。先涨后跌，不能用高点回撤替代整月收益。','claim_ids':['C1','C2']},{'title':'毛利率下降，毛利额仍可能增长','text':f"收入指引中点环比约 +{calc['q3_revenue_growth_pct']}%，毛利率从75%到74%；两项中点隐含毛利额仍增约 {calc['midpoint_implied_gp_growth_pct']}%。关键是增长的规模和质量，不能只看利润率方向。",'claim_ids':['C3','C4','C7']},{'title':'现金回收提供后续核查线索','text':f"Q2经营现金流/收入约{calc['q2_ocf_to_revenue_pct']}%，Q1约{calc['q1_ocf_to_revenue_pct']}%；Q2应收变动占用223.46亿美元。它提示核查营运资本，尚不能诊断坏账或10月订单。",'claim_ids':['C6','C8']}]
report={'title':'NVDA回撤之后，先分清增长与现金','question':'英伟达10月跌了多少，为什么跌，业务变化怎样验证？','as_of':ASOF,'status':'部分完成：数值与业务分析可验证，全月归因未完成','answer':'10月价格收益为−10.39%，月内最高收盘至月末回撤−14.46%。业务原指引仍支持收入与示例毛利额扩张；最后一天的板块抛售有AI投入回报担忧的媒体解释，现有材料仍不能排序整月主因。现金回收是下一步核查线索。','answer_claim_ids':['C1','C2','C9','C7'],'findings':findings,'tables':[{'title':'同口径看增长与现金','columns':['指标','Q1 FY27','Q2 FY27','Q3原指引／中点示例'],'rows':[['收入（十亿美元）','81.615','96.221','108 ±2%'],['毛利率','74.9%','75.0%','74.0% ±0.5个百分点'],['毛利额（十亿美元）','未在本例计算','72.142（GAAP披露）','示例79.92'],['经营现金流（十亿美元）','50.344（由半年减Q2）','24.077','未预测'],['经营现金流/收入','约61.68%','约25.02%','未预测']],'claim_ids':['C3','C4','C6','C7','C8']}], 'alternatives':[{'title':'担忧未必变成近期订单下滑','text':'客户回报疑虑可以与继续采购并存；板块共同重估也可能解释部分回撤；兑现原指引，仍可能不足以满足更高预期。区分这些路径，需要行业比较、同期预期与后续披露。','claim_ids':['C10']}], 'watch':[{'signal':'下一季收入、后续指引与毛利额','meaning':'检验扩张是否兑现；原指引收入区间1058.4—1101.6亿美元。','claim_ids':['C4','C7','C11']},{'signal':'应收、经营现金流及现金转化','meaning':'区分交付扩张的资金占用与持续回收压力。','claim_ids':['C6','C8','C11']}], 'gaps':['本例复用先前冻结材料，没有新增近期检索；不能称为重新完成最新研究。','缺少全月基准行情、同期一致预期与估值，不能排序整月下跌原因。','财务数据为8月披露；未确认10月订单、客户ROI和业务现状。'], 'sources':sources, 'chart':{'title':'NVDA日收盘价（美元）','source':'S2','rows':[price['previous_month_close']]+price['rows'],'claim_ids':['C1','C2']}}
save('report.json',report)
save('datasets.json',{'series':[{'name':'NVDA收盘价','unit':'USD','price_return_excludes_dividends':True,'source_id':'S2','rows':report['chart']['rows']}]})
save('plan.json',{'type':'asset','entity':'NVDA','mode':'frozen-evidence development case','as_of':ASOF,'must_answer':['实际变化','业务到利润/现金机制','候选解释','预期差缺口','下一验证'],'inputs':[str(OLD/'run-0.2.0/claims.json'),str(OLD/'run-0.1.1/evidence/price-snapshot.json')]})
(OUT/'inputs').mkdir(exist_ok=True)
manifest=[]
for src,dest in [('run-0.2.0/raw/newsroom/body.txt','newsroom.txt'),('run-0.2.0/raw/media/body.txt','media.txt'),('run-0.2.0/raw/historical/october-response.json','historical.json')]:
    original=OLD/src; target=OUT/'inputs'/dest; shutil.copyfile(original,target)
    manifest.append({'source':str(original),'copy':str(target.relative_to(OUT)),'sha256':hashlib.sha256(original.read_bytes()).hexdigest()})
save('input-manifest.json',manifest)
lines=['# '+report['title'],'',report['question'],'',f"截点：{ASOF}；复用归档材料；{report['status']}",'',report['answer']+' [C7][C9]']
for f in findings: lines+=['','## '+f['title'],'',f['text']+' '+''.join('['+x+']' for x in f['claim_ids'])]
for t in report['tables']:
 lines+=['','## '+t['title'],'','| '+' | '.join(t['columns'])+' |','|'+'---|'*len(t['columns'])]+['| '+' | '.join(row)+' |' for row in t['rows']]
lines+=['','## 反方与下一观察','',report['alternatives'][0]['text']+' [C10]']
for w in report['watch']: lines+=['',w['signal']+'：'+w['meaning']+' '+''.join('['+x+']' for x in w['claim_ids'])]
lines+=['','## 关键缺口','']+['- '+g for g in report['gaps']]+['','## 来源','']+['- ['+s['id']+' '+s['title']+']('+s['url']+')' for s in sources]
(OUT/'report.md').write_text('\n'.join(lines)+'\n')
r=subprocess.run(['python3',str(ROOT/'scripts/check_claims.py'),str(OUT/'claims.json'),'--json'],capture_output=True,text=True)
(OUT/'check-claims.stdout.json').write_text(r.stdout);(OUT/'check-claims.stderr.txt').write_text(r.stderr)
save('validation.json',{'claim_check_command':['python3',str(ROOT/'scripts/check_claims.py'),str(OUT/'claims.json'),'--json'],'claim_check_exit_code':r.returncode,'question_answer':'partial','mechanism':'growth to gross profit and working-capital observation','limitations':['No new retrieval','No matched benchmark series','No controlled outcome comparison'],'formal_journal_write':False})
print(json.dumps({'case':'asset','claim_check_exit':r.returncode,'calculations':calc},ensure_ascii=False,indent=2))
raise SystemExit(r.returncode)
