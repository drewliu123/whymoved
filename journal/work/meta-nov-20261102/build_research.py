# -*- coding: utf-8 -*-
import json, datetime, copy
from pathlib import Path
W=Path('/Users/frankzhang/Desktop/投研助手/journal/work/meta-nov-20261102')
def load(p): return json.loads((W/p).read_text())
def save(p,x): (W/p).write_text(json.dumps(x,ensure_ascii=False,indent=2))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=load('plan.json'); p['as_of']=now; save('plan.json',p)
f=load('facts.json'); candidates=copy.deepcopy(f['candidates'])
for c in candidates:
    if c['id']=='PX-PATH':
        c['selection']['selected']=False; c['selection']['reason']='历史价格另拆为具时刻的price片段，不作为fact绕过价格要求。'
    if c['id']=='CAL-BLS': c['quote']+='; November 6, 2026 08:30 AM Employment Situation for October 2026; November 10, 2026 08:30 AM Consumer Price Index for October 2026 (table transcription).'
    if c['id']=='CAL-FEC': c['quote']+='; General election date: 11/03/2026 (table transcription).'
base=next(c for c in candidates if c['id']=='PX-CLOSE')
c=copy.deepcopy(base); c['id']='PX-OCT21'; c['quote']='Oct 21, 2026 | Close 697.52 (USD)'; c['locator']='Historical Data table Oct21 2026 Close column'; c['market_quote']['value']=697.52; c['market_quote']['quoted_at']='2026-10-21T16:00:00-04:00'; c['origin_id']='spglobal-meta-eod'; candidates.append(c)
e=load('evidence/gamma-event.json')[0]
common={'tier':'T0','published_at':'unknown','retrieved_at':now,'access_status':'ok','selection':{'selected':True,'reason':'直接核对11月触及合约规则和交易成本。','relevance':'direct','purpose':'T3合约及成本','priority':'decisive'}}
def add_source(s):
    c=copy.deepcopy(common); c.update(s); candidates.append(c)
add_source({'id':'S-RULES','publisher':'Polymarket Gamma','url':'https://gamma-api.polymarket.com/events?slug='+e['slug'],'quote':e['markets'][0]['description'],'locator':'event1250206 markets[].description; endDate='+e['endDate'],'origin_id':'polymarket-meta-nov-rules','origin_basis':'交易平台逐合约正式描述','supports':['fact'],'evidence_kind':'document'})
add_source({'id':'S-FEES','publisher':'Polymarket Documentation','url':'https://docs.polymarket.com/trading/fees.md','quote':'fee = C × feeRate × p × (1 - p). Makers are never charged fees. Only takers pay fees. Finance: fee rate 0.04. Fees are rounded to 5 decimal places.','locator':'Fee structure / Finance row / rounding; evidence/fees.md','origin_id':'polymarket-fee-doc','origin_basis':'平台手续费原始规则','supports':['fact'],'evidence_kind':'document'})
add_source({'id':'S-FEESCHEDULE','publisher':'Polymarket Gamma','url':'https://gamma-api.polymarket.com/events?slug='+e['slug'],'quote':json.dumps({'feesEnabled':True,'feeType':'finance_prices_fees','feeSchedule':e['markets'][0]['feeSchedule']}),'locator':'markets[].feesEnabled/feeType/feeSchedule; evidence/gamma-event.json','origin_id':'polymarket-meta-nov-fees','origin_basis':'各合约费用参数与文档相互核对','supports':['fact'],'evidence_kind':'document'})
books=load('evidence/clob-books.json'); bmap={}
for m in books:
    threshold=int(m['label'].split('$')[1]); side='UP' if '↑' in m['label'] else 'DOWN'
    for t in m['tokens']:
        b=t.get('book',{}); bids=sorted(b.get('bids',[]),key=lambda x:float(x['price']),reverse=True); asks=sorted(b.get('asks',[]),key=lambda x:float(x['price']))
        if not bids or not asks: continue
        sid=f'S-{side}{threshold}-{t["outcome"]}'; bmap[(side,threshold,t['outcome'])]=(sid,bids,asks,t)
        qt=datetime.datetime.fromtimestamp(int(b['timestamp'])/1000,datetime.timezone.utc).isoformat()
        add_source({'id':sid,'publisher':'Polymarket CLOB','url':'https://clob.polymarket.com/book?token_id='+t['token_id'],'retrieved_at':t['book_retrieved_at'],'quote':json.dumps({'market_id':m['id'],'outcome':t['outcome'],'timestamp':b['timestamp'],'best_bid':bids[0],'best_ask':asks[0],'next_asks':asks[1:3]},ensure_ascii=False),'locator':'evidence/clob-books.json; market='+m['id']+' outcome='+t['outcome'],'origin_id':'clob-'+m['id'],'origin_basis':'平台订单簿，Yes/No为同一市场来源家族','supports':['price'],'evidence_kind':'market_quote','market_quote':{'quoted_at':qt,'instrument':'Polymarket:'+m['id'],'outcome':t['outcome'],'direction':'buy','value':float(asks[0]['price']),'unit':'USD/share','quote_type':'executable','bid':float(bids[0]['price']),'ask':float(asks[0]['price'])},'token_id':t['token_id'],'depth':{'best_ask_shares':float(asks[0]['size']),'best_bid_shares':float(bids[0]['size'])},'market_url':'https://polymarket.com/event/'+e['slug']+'/'+m['slug']})
community=load('community/sources.json')
for c in community['candidates']:
    c['id']='COMM-'+c['id']; candidates.append(c)
sources={'schema_version':2,'as_of':now,'historical':False,'candidates':candidates,'source_status':{'official':{'status':'ok','reason':'原始财报与宏观日历已核对'},'market':{'status':'ok','reason':'Gamma规则与30个token的CLOB订单簿及fee-rate已取得；异步快照，价格可变'},'consensus':{'status':'partial','reason':'检索到具名预期线索但缺调查方法样本，不纳为consensus'},'volatility':{'status':'partial','reason':'有AlphaQuery显示值，缺完整期权链和校准方法'},'community':{'status':'partial','reason':'Last30Days候选保留；原文获取失败，全部未选中'},'relative_returns':{'status':'not_run','reason':'未收集同窗QQQ及同业，不能作个股/宏观收益归因'}}}
save('sources-before-selection.json',sources); save('sources.json',sources)
claims=[]
def claim(cid,text,typ,src=None,basis=None,**kw):
    c={'id':cid,'text':text,'type':typ,'as_of':now,'sources':[{'source_id':s} for s in (src or [])]}
    if basis: c['basis']=basis
    c.update(kw); claims.append(c)
claim('C-REVENUE','Meta于2026年10月21日披露Q3收入646.01亿美元，同比增长26%；广告展示量增长10%、单价增长14%。','fact',['META-AD','META-PROFIT'])
claim('C-LEGAL','Q3营业利润129.88亿美元，含98.9亿美元法律计提；公司列示剔除该项后营业利润228.8亿美元。计提不等同于当季现金支付。','fact',['META-PROFIT','META-LEGAL'])
claim('C-CASH','Q3经营现金流327.86亿美元，购买固定资产339.42亿美元，融资租赁本金9.64亿美元；公司自由现金流-21.20亿美元，对比去年同期106.25亿美元。','fact',['META-CASH'])
claim('C-GUIDE','Meta指引Q4收入730—760亿美元；2026资本开支含租赁本金1350—1450亿美元，之前1300—1450亿美元；2027继续积极投入但未给总capex数值。','view',['META-Q4','META-CAPEX','META-2027'])
claim('C-RL','公司预计2026 Reality Labs亏损180—190亿美元，2027约150亿美元；剔除法律计提后，预计2026营业利润高于2025。','view',['META-RL','META-COST'])
claim('C-CLASSC','公司拟设立C类普通股的修章生效日为2027年1月19日；股票股息登记和支付日尚待董事会确定，不是已经确认的11月拆股。','fact',['META-CLASSC'])
claim('C-CLOSE','2026年10月30日16:00 EDT，META常规收盘614.99美元。','price',['PX-CLOSE'],price_kind='close')
claim('C-OCT21','2026年10月21日16:00 EDT，META常规收盘697.52美元。','price',['PX-OCT21'],price_kind='close')
claim('C-RULE','月内触及合约：2026年11月常规交易时段Pyth最终1分钟K线High≥上档或Low≤下档即Yes；盘前盘后排除，价格不四舍五入，拆股调整；Pyth技术不可用时用主交易所官方日高低价。不是月末收盘事件，不同档位可以同时Yes。','fact',['S-RULES'])
claim('C-FEE','该组启用Finance吃单费，rate=0.04、exponent=1；手续费=C×0.04×p×(1−p)，按总费用五位小数取整；挂单方费率0。','fact',['S-FEES','S-FEESCHEDULE'])
claim('C-CALENDAR','11月3日美国大选；11月6日8:30美东时间公布10月就业报告，11月10日8:30公布10月CPI；2026常规FOMC会议10月27—28日和12月8—9日，11月无常规会议。','fact',['CAL-FEC','CAL-BLS','CAL-FED'])
claim('C-VOL','AlphaQuery在2026年10月30日显示30天IV Mean 0.3873、Close-to-Close历史波动0.3649；未取得完整计算及期限行权价方法，不直接转换为本合约触及概率。','view',['VOL-AQ'])
for (side,n,out),(sid,bids,asks,t) in bmap.items():
    claim(f'P-{side}{n}-{out}',f'{side} {n} {out}，11月2日约08:05—08:09 UTC盘口：买入ask {asks[0]["price"]}美元/份，卖出bid {bids[0]["price"]}；ask档量{asks[0]["size"]}份。精确时刻见来源。','price',[sid],price_kind='executable')
calcs=[]
def calc(k,desc,formula,inputs,value,unit,cids):
    calcs.append({'id':k,'description':desc,'formula':formula,'inputs':[{'name':name,'value':v,'unit':u,'claim_ids':refs} for name,v,u,refs in inputs],'result':{'value':value,'unit':unit},'claim_ids':cids})
for side,n,out in [('DOWN',600,'Yes'),('DOWN',600,'No'),('UP',660,'Yes'),('UP',700,'Yes'),('UP',740,'Yes'),('UP',760,'Yes'),('DOWN',580,'Yes')]:
    cid=f'P-{side}{n}-{out}'; k=f'K-{side}{n}-{out}'; a=float(bmap[(side,n,out)][2][0]['price']); total=round(a+round(100*0.04*a*(1-a),5)/100,8)
    calc(k,'100份顶档成交的每份含费成本及持有至结算盈亏平衡概率','p + round(100 × rate × p × (1-p),5)/100',[('p',a,'USD/share',[cid]),('rate',.04,'ratio',['C-FEE']),('C',100,'shares',['C-FEE'])],total,'USD/share',[cid,'C-FEE'])
    claim('E-'+side+str(n)+'-'+out,f'{side}{n} {out}按顶档价理论100份、忽略滑点的每份含费成本{total:.6f}美元，持有至1美元/0美元结算的盈亏平衡胜率{total*100:.2f}%；实际顶档不足100份时不保证此成本。','inference',basis=[cid,'C-FEE'],calculation_id=k)
for n in [600,660,700,740,760]:
    value=(n/614.99-1)*100
    calc('K-DIST'+str(n),'相对10月30日收盘的档位距离','(threshold / close - 1) × 100',[('threshold',n,'USD/share',['C-RULE']),('close',614.99,'USD/share',['C-CLOSE'])],value,'percent',['C-RULE','C-CLOSE'])
    claim('D-'+str(n),f'{n}美元相对614.99美元收盘的距离为{value:+.2f}%。这不是触及概率。','inference',basis=['C-CLOSE','C-RULE'],calculation_id='K-DIST'+str(n))
value=(614.99/697.52-1)*100
calc('K-DROP','10月21日至30日常规收盘变化','(close_end / close_start - 1) × 100',[('close_end',614.99,'USD/share',['C-CLOSE']),('close_start',697.52,'USD/share',['C-OCT21'])],value,'percent',['C-CLOSE','C-OCT21'])
claim('C-DROP',f'10月21日至30日META常规收盘从697.52至614.99美元，下降{abs(value):.2f}%；未核同期指数，不能据此归因全是资本开支。此段已发生下跌不能作为尚未定价的新增利空重复计入。','inference',basis=['C-CLOSE','C-OCT21'],calculation_id='K-DROP')
value=(22.878/20.535-1)*100
calc('K-CORE','剔除法律计提后营业利润对去年报告营业利润的机械比较','((12.988 + 9.890) / 20.535 - 1) × 100',[('reported',12.988,'USD billion',['C-LEGAL']),('legal',9.890,'USD billion',['C-LEGAL']),('prior',20.535,'USD billion',['C-LEGAL'])],value,'percent',['C-LEGAL'])
claim('C-CORE',f'本期报告营业利润加回法律计提为228.78亿美元，比去年报告营业利润205.35亿美元高{value:.1f}%。这是单项调整比较，未对去年作全面非经常项调整，足以反驳仅用报告利润率推断业务崩塌。','inference',basis=['C-LEGAL'],calculation_id='K-CORE')
claim('C-MECHANISM','11月倾向偏弱且双向波动：广告量价仍增长提供反弹基础，但资本开支消耗超过当季经营现金流，2027投入计划延长现金回报不确定性。收入增长不能单独推出股价上涨；法律计提与Reality Labs改善又限制单边崩塌解释。','inference',basis=['C-REVENUE','C-CASH','C-GUIDE','C-LEGAL','C-RL','C-CORE'])
claim('C-DOMINANCE','相同月内触及及调整规则下，UP780 Yes ask0.343被UP760 ask0.11覆盖；DOWN540 Yes ask0.63被DOWN560 ask0.43覆盖；DOWN500 Yes ask0.31被DOWN520 ask0.16覆盖。更便宜的合约在所有正常1/0裁决路径下支付至少相同，吃单费后排序仍不变；这是报价劣后，不代表能同时成交的无风险套利。','inference',basis=['C-RULE','C-FEE','P-UP780-Yes','P-UP760-Yes','P-DOWN540-Yes','P-DOWN560-Yes','P-DOWN500-Yes','P-DOWN520-Yes'])
claim('C-MARKET','订单簿的方向代理：DOWN600 Yes bid/ask0.74/0.79，而UP660 Yes为0.40/0.55，显示这两档的成交报价更偏重下探风险；门槛距离不同，不能把报价差当纯粹看空概率，也不代表全市场共识。','inference',basis=['P-DOWN600-Yes','P-UP660-Yes','D-600','D-660'])
claim('C-RANK','研究排序：第一看DOWN600 Yes（方向机制最匹配、5¢价差较其他主档窄，但79¢吃单后需约79.66%胜率且利空已伴随11.83%下跌，当前无可证明优势）；第二看UP660 Yes（只需一次约7.32%反弹，但55¢吃单后门槛55.99%，不能仅凭强收入证明）；DOWN600 No优先级低，便宜的26¢对应整月不下探，仅2.44%下行缓冲，与能反弹不是同一判断。UP740/760较远，缺新增强催化和尾部概率依据。','inference',basis=['C-MECHANISM','C-DROP','C-MARKET','E-DOWN600-Yes','E-DOWN600-No','E-UP660-Yes','E-UP740-Yes','E-UP760-Yes','D-600','D-660','D-740','D-760'])
claim('C-COSTRISK','低顶档量使页面胜率与可执行成本差异显著：UP660 Yes55¢顶档仅20份，DOWN580 Yes60¢仅20份、下一档68¢；这些价格下足量市价单会滑点。持有至结算若事件失败可损失全部买入成本与费用，提前退出还面对价差；DOWN600 No一旦常规时段触及600即使之后大涨也失败。','inference',basis=['C-RULE','C-FEE','P-UP660-Yes','P-DOWN580-Yes','P-DOWN600-No'])
claim('C-TRIGGER','观察11月2—10日常规价格路径、11月3日选举、11月6日就业及11月10日CPI；若META在利率及板块压力缓解后仍弱且公司上修投入，增强下探解释；若公司给出可核实的投入收敛/回报兑现且价格修复，增强反弹解释。实际收益归因须补同窗指数，未观察前不裁定宏观主导。','inference',basis=['C-CALENDAR','C-MECHANISM','C-COSTRISK','C-RULE'])
claim('C-GAP','有规则、时刻盘口与收入现金对照，但无完整期权链/参考类校准、合格同财季调查共识及同窗板块基准，因此能评估持有至结算的成本门槛，不能证明任何一档独立胜率高于该成本。AlphaQuery数值仅线索，不伪造精确概率；研究状态watch。','inference',basis=['C-VOL','C-RANK','C-COSTRISK','C-MARKET'])
claim('C-CONCLUSION','截至11月2日美股开盘前，META十一月研究倾向偏弱且双向波动，优先研究600下探Yes、其次660上触Yes；两者都尚无经成本验证的概率优势。整月不碰600的No和昂贵远端档位吸引力较低。方向判断与可成交优势分开，等待11月2—10日路径和现金投入新证据。','inference',basis=['C-MECHANISM','C-RANK','C-GAP','C-DOMINANCE','C-TRIGGER'])
save('claims.json',{'schema_version':2,'as_of':now,'claims':claims})
answer='我对META在2026年11月的倾向是偏弱、同时保留反弹触及的可能。广告增长仍强，但AI投入已把季度自由现金流压成负数。对应Polymarket，先研究“月内触及600美元”的Yes，其次研究“触及660美元”的Yes；当前吃单成本下，两者都未形成可证明的胜率优势，状态为观察。尤其不能把反弹判断等同于“整月不碰600美元”。'
findings=[
{'title':'广告韧性与现金压力并存，不能从收入增长直接推上涨','text':'Q3收入646.01亿美元、同比增长26%，广告展示量+10%、单价+14%；经营现金流327.86亿美元，却被339.42亿美元固定资产购买和9.64亿美元租赁本金超过，自由现金流为负21.20亿美元。公司将2026资本开支指引下限从1300亿收窄至1350亿美元、上限1450亿不变，并预计2027继续积极投入。11月真正影响定价的是现金回报和未来投入预期能否改善。','claim_ids':['C-REVENUE','C-CASH','C-GUIDE','C-MECHANISM'],'why_it_matters':'持续收入增长为反弹提供基础，现金缺口让估值修复需要额外证据。','increment':{'kind':'connection','baseline':'单看Q3收入同比增长26%','detail':'将同季经营现金与投资支出配对，定位现金回报约束。'}},
{'title':'利润下降不能全算经营恶化，已发生跌幅也不能再当新增利空','text':'Q3报告营业利润129.88亿美元包含98.9亿美元法律计提；加回该项后为228.78亿美元，比去年报告营业利润高11.4%（单项机械调整，并非全面调整后利润比较）。10月21日至30日常规收盘已从697.52降至614.99美元，跌11.83%。这些数字支持偏弱而有反弹可能的判断，既不支持业务崩塌，也不证明利空已经出尽。','claim_ids':['C-LEGAL','C-CORE','C-DROP','C-MECHANISM'],'why_it_matters':'在已经下跌后继续押下行，必须证明剩余概率足以补偿高买入成本。','increment':{'kind':'connection','baseline':'报告营业利润率20%对比去年40%','detail':'识别法律项和已实现价格调整，避免把报告利润下降全归因于核心经营。'}},
{'title':'合约押价格路径：600下探和660反弹可以同时赢','text':'月内触及依Pyth常规交易时段最终1分钟K线高低价裁决，盘前盘后不算；一旦合格触及，即使月底回到原价也不改变该触及事件。相对614.99美元收盘，600只低2.44%，660高7.32%。当前600下探Yes的79¢含费约79.66¢，660上触Yes的55¢含费约55.99¢；前者机制更直接，后者允许先跌后涨，但当前证据不能给出超过这些成本的独立胜率。','claim_ids':['C-RULE','D-600','D-660','E-DOWN600-Yes','E-UP660-Yes','C-RANK','C-GAP'],'why_it_matters':'看反弹不等于看下沿不被触及，不能用月底方向替代整月路径判断。','increment':{'kind':'connection','baseline':'页面分别显示各档参考概率','detail':'结合结算语义、离现价距离与实际吃单费门槛，形成研究排序。'}},
{'title':'部分报价存在可确定的劣后关系，低价标签并不等于便宜','text':'快照中780上触Yes要34.3¢，而更容易发生的760上触只要11¢；540下探Yes要63¢，更容易发生的560下探只要43¢；500下探31¢也贵于520下探16¢。同规则下这些昂贵档位被更便宜档位覆盖，计费后排序仍不变。20份左右的顶档量和宽价差意味着即使方向判断正确，也可能被滑点及退出成本侵蚀。','claim_ids':['C-DOMINANCE','C-COSTRISK'],'why_it_matters':'先排除劣后报价，可以避免无需预测公司方向就能识别的成本错误。','increment':{'kind':'contradiction','baseline':'将各档显示价格视为一致的概率预测','detail':'用触及事件包含关系核对真实ask，识别报价不一致。'}}]
rows=[]
for label,side,n,out,verdict in [('触及600 / Yes','DOWN',600,'Yes','第一研究；现金压力支持，但未证实>79.66%胜率'),('触及660 / Yes','UP',660,'Yes','第二研究；反弹场景，未证实>55.99%胜率'),('触及600 / No','DOWN',600,'No','低优先；要求整月不下探，不是只看涨'),('触及700 / Yes','UP',700,'Yes','距离+13.82%，需更强催化'),('触及740 / Yes','UP',740,'Yes','尾部事件；缺概率优势'),('触及580 / Yes','DOWN',580,'Yes','更深下探；首档仅20份，滑点明显')]:
    sid,bids,asks,t=bmap[(side,n,out)]; a=float(asks[0]['price']); net=a+.04*a*(1-a)
    rows.append([label,f'{float(bids[0]["price"])*100:g}¢',f'{a*100:g}¢',float(asks[0]['size']),f'{net*100:.2f}%',verdict])
tests=[]
for t in p['research_design']['discrimination_tests']:
    refs=['C-REVENUE','C-CASH','C-LEGAL','C-GUIDE','C-RL'] if t['id']=='T1' else ['C-CALENDAR','C-CLASSC'] if t['id']=='T2' else ['C-RULE','C-CLOSE','P-DOWN600-Yes','P-UP660-Yes']
    interpretation={'T1':'现金压力支持H2，收入量价增长和法律单项调整为H1保留依据；不能把法律计提视作现金流唯一原因。','T2':'已观察日历与未来公司行动时间；11月结果及相对收益尚未发生/未取证，日历本身不能区分H2和H3。','T3':'已核结算和成本，600离现价近于660；缺校准参考类，不能用盘口反向证明H1或H2真实概率。'}[t['id']]
    tests.append({'id':t['id'],'outcomes':t['outcomes'],'status':'observed','claim_ids':refs,'interpretation':interpretation,'supports':['H2'] if t['id']=='T1' else [],'weakens':[],'next_observation':'实际11月价格路径、公司投入及盈利预期新披露；补同窗板块基准和期权参考类','by':t['by'],'supports_if':'投入继续超过现金增长且股价在宏观改善后仍弱，增强H2；收入现金同步改善增强H1','weakens_if':'新增证据显示成本收敛和现金回报改善，削弱H2；只有日历而没有结果不裁定H3'})
report={'schema_version':2,'title':'META十一月：现金压力偏空，触及合约须看路径与成本','question':p['question'],'type':p['type'],'task':p['task'],'as_of':now,'answer':{'text':answer,'claim_ids':['C-CONCLUSION']},'findings':findings,
'alternatives':[{'title':'广告兑现可能引发反弹','text':'收入量价仍强、利润含大额法律计提，Reality Labs预计缩亏。这使反弹到660具有经营情景基础；不过7.32%的距离和55.99%的含费胜率门槛仍需额外验证。','claim_ids':['C-REVENUE','C-LEGAL','C-RL','D-660','E-UP660-Yes','C-RANK']},{'title':'宏观冲击可能改变整个科技板块路径','text':'就业、CPI与选举结果可经利率和风险偏好传导。11月没有常规FOMC会议，不能将“11月降息决议”写成既定催化。未取同窗指数及利率数据，不能判断宏观已经主导本次下跌。','claim_ids':['C-CALENDAR','C-TRIGGER','C-DROP']}],
'watch':[{'signal':'11月3日选举、6日8:30 ET就业、10日8:30 ET CPI','meaning':'检验利率与板块风险偏好；数据盘前发布，合约仍要等常规时段合格触及。','claim_ids':['C-CALENDAR','C-RULE','C-TRIGGER']},{'signal':'11月2—10日价格路径与可核实的新投入/现金回报信息','meaning':'600下探与660反弹分开跟踪；一旦常规触及600，600 No的原判断失效。到11月10日无新证据则继续标记未建立优势，不自动升级。','claim_ids':['C-TRIGGER','C-COSTRISK','C-GAP']},{'signal':'11月公司行动与2027预算正式披露','meaning':'当前公司所述C类设立生效日是2027年1月19日、股息日期未定；不把它当已确认11月拆股催化。','claim_ids':['C-CLASSC','C-GUIDE']}],
'limitations':[{'text':'没有足够方法透明的期权/参考类输入来校准月内触及概率；所以给出有方向的情景和成本门槛，未宣称任一档已验证错价。','material':True,'claim_ids':['C-GAP']},{'text':'未取得合格同口径财报调查共识、同窗板块基准；社区原文未读到，候选不进入正式主张。订单簿为约08:05—08:09 UTC异步快照、仅保证所见挂单量，不保证现在或足量成交。','material':False,'claim_ids':['C-GAP','C-COSTRISK']}],
'tables':[{'title':'11月2日开盘前盘口与研究排序','columns':['合约 / 选项','卖出bid','买入ask','顶档可买份数','含费盈亏平衡胜率','判断'],'rows':rows,'claim_ids':['C-RANK','C-COSTRISK','E-DOWN600-Yes','E-UP660-Yes','E-DOWN600-No','E-UP700-Yes','E-UP740-Yes','E-DOWN580-Yes'],'note':'成本按ask与Finance费率计算，顶档外滑点另计；胜率门槛是支付结构计算，并非研究预测。每份合约结算1或0美元，费用总额五位小数取整。快照约2026-11-02 08:05—08:09 UTC。'}],
'calculations':calcs,
'analysis':{'version':1,'question_kind':'event_forecast','method':'reference_class_scenarios','price_relevance':True,'baseline':p['research_design']['baseline'],'baseline_claim_ids':['C-CLOSE','C-REVENUE','P-DOWN600-Yes','P-UP660-Yes'],'mechanism_chain':p['research_design']['mechanism_chain'],'hypotheses':[{k:h[k] for k in ['id','explanation']} for h in p['hypotheses']],'tests':tests,'conclusion':answer,'conclusion_claim_ids':['C-CONCLUSION'],'model_status':'not_applicable','model_reason':'事件触及研究；不进行经营或DCF金额预测。成本、距离及历史变化为透明算术，保留calculations和执行脚本；触及概率因参考类不足不建模型。','models':[],
'market':{'status':'assessed','reason':'已评估指定事件盘口隐含的持有成本门槛与有据研究情景；独立触及概率尚未校准，评估不代表已发现错价。','claim_ids':['P-DOWN600-Yes','P-UP660-Yes','C-MARKET','C-RANK','C-GAP','E-DOWN600-Yes','E-UP660-Yes'],'model_ids':[],'implied_expectation':'下探600 Yes ask79¢、660反弹Yes ask55¢，含费胜率门槛约79.66%及55.99%；宽价差，均非精确客观概率。','research_expectation':'收入有韧性但现金压力使11月倾向偏弱且保留反弹，不推导整月不碰600。','gap':'方向机制与下探报价一致，未校准独立概率，尚无可证明超过成本的分歧；确定增量在报价包含关系及成本筛选。','conditions':'参考类/期权分布及11月实际路径、宏观和公司投入新证据可改变概率判断；盘口变化须重算。'}},
'opportunity':{'version':1,'applicability':'trading','market_view':{'text':'根据600下探Yes和660上触Yes买卖价推断，该两档更重视下探风险；距离不同、价差较宽，只是该组盘口代理，非全市场共识。','basis':'proxy','claim_ids':['C-MARKET']},'variant':{'text':'方向上暂无有力逆共识分歧。增量是区分现金压力与法律计提，以及看反弹与整月不下探；不把方向判断冒充概率优势。','claim_ids':['C-MECHANISM','C-RANK','C-GAP']},'edge':{'text':'可核实的优势在规则与相对成本筛选：剔除被更便宜合约覆盖的780/540/500 Yes；其余档位尚未证明概率优势。','claim_ids':['C-DOMINANCE','C-GAP']},'catalyst':{'text':'11月3日选举、6日就业和10日CPI，加上11月2—10日常规价格路径与公司投入/现金新证据。','by':'2026-11-10T21:00:00Z；之后至11月30日常规收盘继续裁决','claim_ids':['C-CALENDAR','C-TRIGGER']},'payoff':{'text':'股价10月21—30日已下跌11.83%，既有利空可能已有部分反映但程度不明。600 Yes含费约79.66¢，胜出每份净赚约20.34¢、失败亏约79.66¢；660 Yes成本约55.99¢。概率优势未建立，顶档不足及提前退出价差可进一步侵蚀空间。','claim_ids':['C-DROP','E-DOWN600-Yes','E-UP660-Yes','C-COSTRISK','C-GAP']},'assessment':{'status':'watch','text':'先研究600下探Yes，其次660上触Yes；当前均未证明独立胜率高于成本。600 No、被覆盖的远端档优先级低。首个复核窗口11月2—10日，不因没有新证据自动升级。','claim_ids':['C-RANK','C-CONCLUSION','C-GAP']},'triggers':[{'id':'TR-PATH','signal':'11月2—10日常规Pyth一分钟K线是否触及600或660，并复核新盘口','by':'2026-11-10T21:00:00Z；最终2026-11-30T21:00:00Z','claim_ids':['C-RULE','C-RANK','C-COSTRISK'],'supports_if':'持续现金压力且常规触及600支持下探事件；现金回报改善并上触660支持反弹情景，两者可并存','weakens_if':'公司现金回报改善且在宏观压力下仍保持韧性，削弱单边看空；上行失败但不触及不自动构成最终否定','invalidates_if':'常规触及600使600 No失效；到期仍未达到相应门槛使对应Yes失效。价格变化后旧成本比较到期，须重新取证'}, {'id':'TR-INFO','signal':'就业、CPI、选举结果及可验证的公司投入/现金新信息','by':'2026-11-10T21:00:00Z；公司信息截至11月30日','claim_ids':['C-CALENDAR','C-MECHANISM','C-TRIGGER'],'supports_if':'投入继续超过现金增长、宏观改善后META仍弱，增强H2；投入收敛与现金兑现增强H1','weakens_if':'核心现金增长覆盖新增投入削弱H2；板块同步冲击且无公司修订降低公司特有解释','invalidates_if':'没有新证据或缺完整对照时不升级优势；公司披露与本轮机制相反则重写假设，旧判断保留在归档'}]}}
save('report.json',report)
audit={'as_of':now,'queries':f.get('queries',f.get('query_log',[])),'main_queries':[{'query':'Polymarket META November2026 Gamma/CLOB rules and fees','status':'ok','evidence':['evidence/gamma-event.json','evidence/clob-books.json','evidence/fees.md']},{'query':'Pyth META feed page','status':'partial','reason':'页面无完整价格日期，不以615.94替代常规收盘','evidence':['evidence/pyth-page.html','evidence/pyth-feed.json']}],'community':{'status':'partial','raw':'community/last30days-raw.json','query_log':'community/query-log.json','selection':'community/sources.json','reason':'原文获取失败，保留候选不纳事实'},'context_review':{'long_term':'广告现金引擎与AI投资资本周期','recent':'10月21财报及至30日价格路径','prior_expectations':'具名报道但调查方法不足，不宣称超预期','new_transmission':'收入韧性与现金投入配对；10月资料是已知基准，不当作11月新消息','next_test':'11月2—10日路径、宏观与投入新证据','unresolved':'同窗指数、完整期权和参考类、同财季合格共识'},'review':{'status':'pending'},'execution':[{'command':'analysis_contract.py route event_forecast','exit_code':0},{'command':'research_plan.py plan.json (initial)','exit_code':1,'reason':'补discriminating_observation后通过'},{'command':'research_plan.py plan.json (corrected)','exit_code':0},{'command':'python3 -I fetch_books.py','exit_code':0,'log':'evidence/clob-books.json'},{'command':'python3 -I build_research.py','exit_code':0,'note':'calculations由显式Python算术生成；后续脚本仅校验结构、固定模型不适用；算术仍需独立审查'}],'exclusions':['社区融资10%利率等未经原件核对，未纳事实','Pyth盘外参考价未作常规结算依据','未以不完整共识计算超预期或历史预期修订'],'scope_note':'用户未指定具体合约；选用匹配月内触及市场。月末收盘市场为不同事件。'}
save('audit.json',audit)
print(json.dumps({'as_of':now,'sources':len(candidates),'claims':len(claims),'calculations':len(calcs)},ensure_ascii=False))
