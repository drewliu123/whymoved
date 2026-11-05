# -*- coding: utf-8 -*-
from pathlib import Path
from datetime import datetime, timezone
import json
W=Path('/Users/frankzhang/Desktop/投研助手/journal/work/fed-dec2026-20261101')
f=json.loads((W/'facts.json').read_text())
now=datetime.now(timezone.utc).isoformat()
s=[]
for z in f['candidates']:
    if z['id'] in ['FC1','FC2']: continue
    z=dict(z)
    if z['id']=='FC10': z['quote']=''; z['origin_id']=None; z['origin_basis']='未取得原文，不判定出处独立性'
    if z['id'] in ['FC11','FC12']: z['quote']=''; z['origin_id']=None; z['origin_basis']='搜索线索未打开'
    s.append(z)
def source(i,u,q,l,pub):
    s.append({'id':i,'url':u,'canonical_url':u,'publisher':'Federal Reserve','tier':'T0','published_at':pub,'retrieved_at':now,'quote':q,'locator':l,'origin_id':i,'origin_basis':'官方原文','supports':['fact'],'evidence_kind':'document','access_status':'ok','selection':{'selected':True,'reason':'确认已发生收紧及主席未承诺12月行动，直接区分方向与确定性。','relevance':'direct','purpose':'补足政策方向与前瞻指引','priority':'decisive'}})
source('S5','https://www.federalreserve.gov/mediacenter/files/FOMCpresconf20261028.pdf','The FOMC’s discussion over the last couple of days focused mainly on the price stability side of our remit. ... I also don’t believe in prejudging meetings.','Transcript pp. 2 and 13; first quotation capitalization normalized from sentence continuation; second phrase apostrophe normalized; PDF text in raw-fed-conference/conference.txt','2026-10-29')
source('S6','https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm','raise the target range for the federal funds rate by 1/4 percentage point to 3-3/4 to 4 percent','September 16 FOMC statement, policy decision paragraph','2026-09-16')
source('S7','https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm','Federal funds rate: 2026 median 4.1; range 3.9–4.4; central tendency 4.1–4.4.','Table 1, 2026 federal funds rate row; Figure 2: 3.875% (2 participants), 4.125% (12), 4.375% (4). Table values transcribed, not continuous prose quotation.','2026-09-16T14:00:00-04:00')
def fact(i,t,ss): return {'id':i,'text':t,'type':'fact','sources':[{'source_id':v} for v in ss]}
claims=[fact('C6','BEA9月PCE价格指数环比上升0.5%、同比上升3.6%；剔除食品能源的核心PCE环比0.3%、同比3.1%。',['FC3','FC4','FC5']),fact('C7','BLS10月2日公布的9月非农就业初值增加29000；失业率由7、8月的4.1%升至9月的4.2%；7、8月新增就业分别下修31000和29000。',['FC6','FC7','FC8','FC9']),fact('C8','9月16日FOMC一致决定加息25个基点，至3.75%—4.00%。',['S6']),fact('C9','10月28日记者会中主席称讨论主要集中于价格稳定，并明确表示不预判会议；针对六周后会议未承诺行动。',['S5'])]
conclusion='截至2026年11月1日，我倾向于12月加息一次、幅度25个基点，属于有条件的基准情景。如果实施，目标区间将升至4.00%—4.25%。主席尚未承诺12月行动；就业疲软是转向维持利率的主要反证，本轮未取得可核验的实时期货概率。'
inferences=[{'id':'C10','text':conclusion,'basis':['C1','C2','C3','C5','C6','C7','C8','C9']},{'id':'C11','text':'9月已加息、10月仍强调价格稳定而非准备降息，结合核心PCE仍在3.1%，使12月再加息25个基点成为当前有条件基准；10月10位委员支持等待与9月就业弱说明该情景尚未锁定。两位异议者要求的是10月立即加息，不能算成委员会承诺12月加息。','basis':['C3','C6','C7','C8','C9']},{'id':'C12','text':'若会前核心通胀持续偏高且就业企稳，支持12月加息；若新增就业继续低迷、失业率上升，同时核心通胀降温，维持利率的理由增强。单次会议上调50个基点仍算一次，不能称为加息两次；本轮材料不足以将50个基点列为基准。','basis':['C1','C3','C5','C6','C7','C9']}]
report={'title':'美联储12月：倾向加息一次25个基点，关键在就业能否企稳','answer':{'text':conclusion,'claim_ids':['C10']},'findings':[{'title':'9月已经加息，10月暂停观察','text':'9月16日美联储一致加息25个基点，10月28日维持3.75%—4.00%。10月有两位委员要求立即再加25个基点；主席在记者会表示讨论主要集中在价格稳定，同时拒绝预判下一次会议。这个组合支持继续收紧的可能，也保留等待新数据的空间。','claim_ids':['C2','C3','C8','C9'],'why_it_matters':'12月的政策问题是是否继续此前的收紧，10月暂停本身不能推导为即将降息。','increment':{'kind':'connection','baseline':'仅看10月维持利率的决定','detail':'与9月已加息和10月记者会串联，区分暂停观察与结束收紧。'}},{'title':'通胀支持加息，就业构成反证','text':'9月总体PCE同比3.6%、核心PCE同比3.1%，核心环比0.3%；价格压力仍在。同期非农就业仅增加2.9万人，失业率升至4.2%，7、8月新增就业均遭下修。继续加息能压低需求与通胀，也可能加重就业压力，因此需要会前数据确认。','claim_ids':['C6','C7','C11'],'why_it_matters':'这是加息与继续维持之间真正的权衡，不能只看通胀一侧。','increment':{'kind':'connection','baseline':'只据两张加息异议票推测12月','detail':'同时纳入价格与就业观察，限制基准情景的确定性。'}},{'title':'12月一次例会，次数和幅度分开','text':'官方日历只有12月8—9日这一场例行会议。正常安排下，12月若加息就是一次。25个基点等于0.25个百分点，对应目标区间4.00%—4.25%；一次上调50个基点依然是一次决策。次数判断不包含临时行动。','claim_ids':['C1','C5','C12'],'why_it_matters':'避免把幅度的25基点单位误作会议次数，或将12月与全年累计变化混淆。','increment':{'kind':'connection','baseline':'用户询问12月加几次','detail':'将日历允许的决策机会与条件性幅度拆开。'}}],'alternatives':[{'title':'继续维持3.75%—4.00%','text':'若就业疲弱延续、失业率继续上升，且核心通胀降温，继续等待的理由会增强；10月多数选择维持已说明委员会重视新增信息。','claim_ids':['C2','C3','C7','C9','C12']}],'watch':[{'signal':'12月会议前新公布的核心PCE、非农就业与失业率','meaning':'核心通胀仍高且就业企稳支持加息；核心通胀降温并伴随就业继续走弱支持维持。关注连续变化，而非单一数值。','claim_ids':['C12']}],'limitations':[],'tables':[]}
e={'sources':s,'claims':claims,'inferences':inferences,'report':report,'market':{'status':'missing','reason':'未取得带报价时刻及12月9日会议完整映射的FedWatch分布。85%仅搜索线索；不报告实时概率或宣称研究有定价优势。','claim_ids':[],'model_ids':[]},'tests':{'T1':{'status':'observed','claim_ids':['C3','C6','C7','C8','C9'],'interpretation':'政策侧已收紧且强调通胀，支持H1；就业数据疲弱符合H2中的就业渠道。综合偏向有条件再加25基点，但不判定另一解释已排除。','supports':['H1','H2'],'weakens':[],'next_observation':'核心PCE与非农就业、失业率','by':'2026年12月9日前','supports_if':'通胀持续偏高而就业企稳增强H1','weakens_if':'就业继续走弱且核心通胀降温削弱H1'},'T2':{'status':'missing','claim_ids':[],'supports':[],'weakens':[],'gap_reason':'Axios/AP正文获取失败，未取得CME原始带时刻分布。','interpretation':'不能以未核验85%裁定任何解释，也不能推算其余结果概率。','next_observation':'指定12月9日会议的FedWatch目标区间分布及快照时刻','by':'下一次更新','supports_if':'高于10月区间的权重占优支持H1','weakens_if':'维持或降息权重占优削弱H1'}},'source_status':{'official':{'status':'ok'},'macro':{'status':'partial','reason':'取得9月PCE就业，未补足完整三个月核心通胀序列'},'market':{'status':'error','reason':'Axios403；AP正文不可获取；未取得实时CME分布'},'community':{'status':'not_run','reason':'等待独立侦察结果；定稿前更新'}}}
claims.append(fact('C13','9月16日官方SEP中18位参与者的年底利率中点预测为：3.875%有2位，4.125%有12位，4.375%有4位；表中年底中位数四舍五入为4.1%。这是决策者的条件预测，不是市场概率或已作出的12月决定。',['S7']))
inferences[0]['basis'].append('C13')
inferences[1]['text']='9月SEP的18位参与者中12位预计年底利率中点4.125%，比当前3.875%高25个基点；结合9月已收紧、10月仍强调物价稳定与9月核心PCE同比3.1%，支持有条件倾向12月再加25个基点。9月预测未在10月更新，10月10位委员选择等待，限制这一倾向的确定性。'
inferences[1]['basis'].append('C13')
inferences[2]['text']='核心通胀持续偏高且就业企稳增强12月加息情景；就业连续显著恶化本身亦削弱加息倾向，即使核心通胀尚未降温。核心通胀同步降温会进一步增强维持理由。单次会议上调50个基点仍算一次；本轮不将50个基点列为基准。'
report['findings'][0]['text']='9月16日美联储一致加息25个基点。同期官方SEP中，18位参与者有12位预计年底利率中点4.125%，对应4.00%—4.25%的目标区间，也就是从当前水平再加25个基点。10月28日维持利率，主席仍强调价格稳定，同时拒绝预判下一次会议。9月预测为加息情景提供直接基准，10月等待的决定则提醒这一预测尚未获重新确认。'
report['findings'][0]['claim_ids'].append('C13')
report['findings'][0]['increment']['detail']='把9月官方年底利率分布与10月实际利率对照，得到条件性的25基点差距；不把点阵图当承诺或市场概率。'
report['findings'][1]['text']+=' 主席的积极就业评价侧重年度比较与初请失业金等高频指标；这里的疲弱观察来自单月非农和修订，两者口径不同，不能直接抵消。若就业连续显著恶化，即使通胀仍高，也会削弱加息理由。'
report['alternatives'][0]['text']='9月收紧已开始传导，委员会可以继续观察效果。若就业连续显著恶化，即使核心通胀未降，维持利率的理由也会增强；核心通胀同步降温会进一步支持等待。'
report['watch'][0]['meaning']='核心通胀持续偏高且就业企稳支持加息；就业连续显著恶化本身亦削弱加息倾向，若核心通胀同步降温则进一步支持维持。关注连续变化。'
e['tests']['T1']['claim_ids'].append('C13')
e['tests']['T1']['interpretation']='9月SEP的年底利率分布直接支持再加25基点情景，结合近期通胀与政策侧重而有条件偏向H1；就业弱支持H2中的就业渠道。10月尚未确认未来决定，不能把年度与单月就业评价混为一个趋势。'
e['tests']['T1']['weakens_if']='就业连续显著恶化本身就削弱H1，即使核心通胀未降；通胀同步降温进一步增强维持理由'
(W/'additional-evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n')
