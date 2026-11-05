"""Build the task-local research artifacts from preserved public responses only."""
import datetime
import html
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
NOW = json.loads((ROOT / 'report.json').read_text())['as_of']  # Evidence cutoff preserved during no-search review revision.

def load(p):
    return json.loads((ROOT / p).read_text())

def save(p, data):
    (ROOT / p).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

event = load('raw-market/gamma-event.json')[0]
gamma_meta = load('raw-market/gamma-event-meta.json')
official_meta = {s['id']: s for s in load('raw-official-first/fetch-log.json')}
clob_meta = load('raw-clob/fetch-log.json')
calc = load('calculations.json')
freeze = load('independent-freeze.json')
url = 'https://polymarket.com/event/' + event['slug']

sources = [
    {'id':'S1','title':'Polymarket：12月Fed决议完整事件与五个子合约','publisher':'Polymarket','tier':'T0','url':gamma_meta['url'],'display_url':url,'published_at':'unknown','event_time':'2026-12-08/2026-12-09','retrieved_at':gamma_meta['retrieved_at'],'response_date':gamma_meta['response_date'],'document_version':event['updatedAt'],'status':'success','raw_path':'raw-market/gamma-event.json','locator':'[0].description; [0].active/closed/endDate; [0].markets[*]','quote':event['description'],'data_quote':{'active':event['active'],'closed':event['closed'],'endDate':event['endDate'],'outcomes':[{k:m.get(k) for k in ['id','groupItemTitle','active','closed','endDate','acceptingOrders','outcomePrices','bestBid','bestAsk','lastTradePrice','updatedAt']} for m in event['markets']]},'independence_group':'polymarket-event-770450'},
    {'id':'S2','title':'Polymarket CLOB：五个Yes token原始订单簿','publisher':'Polymarket','tier':'T0','url':clob_meta[3]['url'],'published_at':'unknown','event_time':'snapshot','retrieved_at_start':min(x['retrieved_at'] for x in clob_meta if x['id'].isdigit()),'retrieved_at_end':max(x['retrieved_at'] for x in clob_meta if x['id'].isdigit()),'status':'success','locator':'bids/asks[*].price,size; timestamp; hash','quote':'原始数值记录，见 data_quote；这是官方盘口数据而非文字引语。','data_quote':[{**x,'raw_path':'raw-clob/'+x['id']+'.json','timestamp':load('raw-clob/'+x['id']+'.json')['timestamp'],'last_trade_price':load('raw-clob/'+x['id']+'.json').get('last_trade_price'),'bids':load('raw-clob/'+x['id']+'.json')['bids'],'asks':load('raw-clob/'+x['id']+'.json')['asks']} for x in clob_meta if x['id'].isdigit()],'independence_group':'polymarket-event-770450','note':'S1与S2为同一市场不同接口，不能充当独立共识来源。只抓Yes侧，No侧深度未抓取。'},
    {'id':'S3','title':'Federal Reserve：2026/2027 FOMC会议日历','publisher':'Federal Reserve','tier':'T0','url':official_meta['fomc_calendar']['url'],'published_at':'unknown','document_version':'页面Last Update October 28, 2026','event_time':'2026-12-08/09; 2027-01-26/27','retrieved_at':official_meta['fomc_calendar']['retrieved_at'],'status':'success','raw_path':'raw-official-first/fomc_calendar.html','locator':'2026 FOMC Meetings > December；2027 > January；日历说明','quote':'December\n8-9*\n* Meeting associated with a Summary of Economic Projections.','quotes':['The minutes of regularly scheduled meetings are released three weeks after the date of the policy decision.','2027 FOMC Meetings\nJanuary\n26-27','Each meeting date is tentative until confirmed at the meeting immediately preceding it.'],'independence_group':'fed-calendar'},
    {'id':'S4','title':'Federal Reserve：2026年10月28日FOMC声明','publisher':'Federal Reserve','tier':'T0','url':official_meta['fomc_october']['url'],'published_at':'2026-10-28T14:00:00-04:00','event_time':'2026-10-28','retrieved_at':official_meta['fomc_october']['retrieved_at'],'status':'success','raw_path':'raw-official-first/fomc_october.html','locator':'正文政策段、经济评价、通胀段、异议段；txt 285–289行','quote':'The Committee decided to maintain the target range for the federal funds rate at 3-3/4 to 4 percent, in support of the Federal Reserve\'s dual mandate.','quotes':['The Federal Open Market Committee approved the following statement for release by a 10 – 2 vote:','Economic activity is expanding at a strong pace.','Job gains have kept pace with the workforce, and the unemployment rate has changed little.','Inflation remains elevated. The accumulation of more information will help the Committee determine the policy stance appropriate to ensure a timely return of inflation to the Committee\'s 2 percent goal.','Voting against the monetary policy action were Lisa D. Cook and Beth M. Hammack, who preferred to raise the target range for the federal funds rate by 1/4 percentage point at this meeting.'],'independence_group':'fed-oct-statement'},
    {'id':'S5','title':'BEA：Personal Income and Outlays, September 2026','publisher':'BEA','tier':'T0','url':official_meta['bea_pce']['url'],'published_at':'2026-10-29T08:30:00-04:00','event_time':'2026-09','retrieved_at':official_meta['bea_pce']['retrieved_at'],'status':'success','raw_path':'raw-official-first/bea_pce.html','locator':'正文价格、实际消费、月度对照表、Next release；txt 68–71行','quote':'From the preceding month, the PCE price index for September increased 0.5 percent . Excluding food and energy, the PCE price index increased 0.3 percent.','quotes':['From the same month one year ago, the PCE price index for September increased 3.6 percent . Excluding food and energy, the PCE price index increased 3.1 percent from one year ago.','Real PCE increased $2.6 billion ( less than 0.1 percent at a monthly rate) in September.','Real DPI 0.0 -0.3','PCE price index excluding food and energy 0.3 0.3','Next release: November 25, 2026, at 8:30 a.m. EST'],'independence_group':'bea-sep-pio'},
    {'id':'S6','title':'Federal Reserve：2026年9月16日FOMC声明','publisher':'Federal Reserve','tier':'T0','url':'https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm','published_at':'2026-09-16T14:00:00-04:00','event_time':'2026-09-16','retrieved_at':next(x['retrieved_at'] for x in clob_meta if x['id']=='fomc_september'),'status':'success','raw_path':'raw-clob/fomc_september.html','locator':'正文投票与政策段','quote':'The Committee decided to raise the target range for the federal funds rate by 1/4 percentage point to 3-3/4 to 4 percent, in support of the Federal Reserve\'s dual mandate.','quotes':['The Federal Open Market Committee approved the following statement for release by a 12 – 0 vote:'],'independence_group':'fed-sep-statement','note':'盘口后追加的官方上下文；不回写盘口前初判依据。'}
]
failures = [x for x in official_meta.values() if x.get('status')=='failed']
search_audit = {'tool':'mcp__zhihu__global_search','queries':['site.federalreserve.gov 2026 October 28 FOMC statement','site.bls.gov 2026 September employment situation October 2026 unemployment','site.bea.gov September 2026 personal income outlays October 2026 PCE'],'retrieved_window':'2026-10-31T17:15–17:16Z','timestamp_precision':'分钟近似；工具未返回调用时间，未伪造精确秒','results_used_as_fact':False,'note':'返回知乎/媒体转述、无关失业数据及陈旧BEA首页摘要；仅用来定位Fed原始链接。搜索摘要中的机构加息观点属于初判污染披露，未用于数字概率。未继续社区扩搜。','representative_urls':['https://zhuanlan.zhihu.com/p/2098975768223208349','https://finance.sina.com.cn/stock/stockzmt/2026-10-29/doc-iniwvwre2890431.shtml']}
save('sources.json', {'as_of':NOW,'sources':sources,'failed_sources':failures,'search_audit':search_audit,'source_count':6,'dependency_note':'六个关键T0记录包括一条CLOB聚合记录；五本订单簿作为其子记录。Fed声明/日历同一发布方；不能按URL数推断信息独立性。'})
S={s['id']:s for s in sources}
def cite(*ids):
    return [{k:S[i][k] for k in ['id','url','publisher','tier','published_at']} for i in ids]
claims=[]
def claim(cid,text,typ,ids=(),basis=None):
    c={'id':cid,'text':text,'type':typ,'as_of':NOW,'sources':cite(*ids)}
    if basis:c['basis']=basis
    claims.append(c)
claim('C1','12月Fed事件及五个子合约active=true、closed=false、acceptingOrders=true；事件endDate为2026-12-10T04:59:00Z，子合约均为2026-12-09T23:59:00Z。','fact',('S1',))
# acceptingOrders belongs to child markets only; remove ambiguity explicitly.
claims[-1]['text']='12月Fed事件active=true、closed=false；五个子合约也active=true、closed=false且acceptingOrders=true。事件endDate为2026-12-10T04:59:00Z，子合约均为2026-12-09T23:59:00Z。'
claim('C2','规则按12月会议前后联邦基金目标区间上限的变化结算，不按从今天到年底的累计变化；非展示幅度向上取至25bp档，例子为12.5bp算25bp。正式来源为12月8–9日会议声明，声明可触发提前结算；原文条件为“If no statement is released by the end date of the next scheduled meeting”则归No change；未明确next相对哪个时点，因此不能据此指定某次会议为默认截止。','fact',('S1',))
claim('C3','Fed日历列2026年12月8–9日会议并附经济预测；12月之后的日历会议列2027年1月26–27日，日历说明日期在前次会议确认前为暂定。','fact',('S3',))
claim('C4','10月28日Fed以10–2维持3.75%–4.00%；Cook与Hammack要求加25bp。声明形容经济强劲、就业与劳动力同步、失业率变化不大，通胀仍高，需要更多信息。','fact',('S4',))
claim('C5','BEA在10月29日公布9月PCE：总价格环比0.5%、同比3.6%，核心环比0.3%、同比3.1%；8月核心环比同为0.3%。','fact',('S5',))
claim('C6','同份BEA发布中，9月名义PCE环比0.5%，实际PCE增幅不足0.1%（表格四舍五入为0.0%），较8月0.5%的实际增速放缓；实际可支配收入环比下降0.3%。','fact',('S5',))
claim('C7','9月16日Fed以12–0加息25bp至3.75%–4.00%，10月随后维持。','fact',('S6','S4'))
claim('C8','Gamma原始Yes参考价依次为：降50+bp 0.40%、降25bp 0.65%、不变27.50%、加25bp 70.50%、加50+bp 1.70%；获取时间2026-10-31T17:17:21.213899Z，HTTP Date为17:14:28Z。','price',('S1',))
claim('C9','CLOB五档Yes bid/ask依次为0.003/0.005、0.006/0.007、0.27/0.28、0.70/0.71、0.016/0.018；获取窗口17:17:41.692–41.992Z，书内时间为17:16:54.639–17:17:40.943Z。','price',('S2',))
claim('C10','按保存盘口计算，五个Gamma Yes参考价之和100.75%，bid和99.50%，ask和102.00%；保留原值不强行归一化，不能将其当无摩擦精确概率分布。','inference',basis=['C8','C9'])
claim('C11','加25bp最佳bid/ask显示3010.62/48170.95份，按价格乘份数约2107.43/34201.37美元；不变为27435.55/24428.43份。显示深度可撤单，不等于保证成交。','price',('S2',))
claim('C12','盘口前定性初判以维持为暂定基准、加25bp为实质竞争情景、降息不作基准。10月的等待选择支持暂停，但核心价格仍有压力，无法把异议票数换成概率；缺条件化样本，不给独立数字概率。','inference',basis=['C4','C5','C6'])
claim('C13','盘口后补见9月全票加息，更合理的竞争解释是10月暂歇后恢复收紧；这削弱把10月维持外推至12月的把握。最终将维持与加25bp并列工作情景，加息的证据基础充分，但没有独立模型支持认定70.5%高估或低估。','inference',basis=['C4','C5','C6','C7','C8'])
claim('C14','9月实际消费增速放缓、实际DPI下降，与通胀压力仍在可以同时成立，但单月数据尚未确认持续或全面需求走弱。10月Fed以10–2选择维持，也支持继续等待有政策依据。核心价格与就业的后续组合仅作定性更新提示，尚非已校准、可重复的改判阈值。','inference',basis=['C4','C5','C6'])
claim('C15','BEA列下一次个人收入与支出发布为2026年11月25日8:30 a.m. EST；应核对核心PCE与实际消费，而非只看总价格。之后12月8–9日声明和实际规则结算是最终核对节点。','inference',basis=['C2','C3','C5','C6'])
claim('C16','规则存在元数据时点不一致和延期措辞风险：事件与子合约endDate相差5小时；没有界定“next scheduled meeting”的next相对哪个时点，也没有精确时区/截止秒；日历仅证明2027年1月26–27日在12月会议之后，不能确定它就是默认截止；紧急会改变会前利率时不能直接用今天4.00%上限作差。No change也可能来自无声明默认条款。','inference',basis=['C1','C2','C3','C4'])
claim('C17','加25bp的Gamma lastTradePrice为0.71，同一Yes token的CLOB last_trade_price为0.290；两端都未给独立成交时戳。这两个字段不一致，未用于方向或价格变动解释，差异原因未核实。','price',('S1','S2'))
claim('C18','可否定命题：12月正式声明若相对会议前上限降息或加息至少50bp，即超出维持/加25bp两中心情景，应记为中心情景未覆盖；其余watch仅作定性更新提示，无已校准可重复阈值。无数值概率不计算独立Brier/log loss。','inference',basis=['C2','C13','C14'])
save('claims.json',{'question':'12月Fed合约定价及官方证据的分歧是什么？','as_of':NOW,'claims':claims})

findings=[
 {'title':'当前判断：加息有证据，70.5%尚无独立校准依据','text':'看完市场后，以维持与加息25bp作为并列工作情景。官方材料足以解释为何市场偏向加息，但不足以检验70.5%这个数值是否合理，因此不宣称存在定价优势。9月全票加25bp、10月暂停且仍有加息异议，说明“暂停后恢复收紧”是有根据的路径。','claim_ids':['C4','C5','C7','C8','C13']},
 {'title':'市场参考、独立初判与市场后观点分别保留','text':'市场参考：Gamma加25bp 70.5%、维持27.5%。独立初判：在读取任何Polymarket报价前，已在independent-freeze.json冻结“维持为暂定基准，加25bp为实质竞争情景”，未给数字概率。市场后观点：取得9月官方决议后，降低维持优先排序的把握，改为维持/加25bp并列工作情景；此修订受新增官方上下文支持，也可能受已见市场锚定影响，不能重新包装为独立预测。','claim_ids':['C7','C8','C12','C13']},
 {'title':'通胀约束宽松，但需求并非处处加速','text':'9月核心PCE环比0.3%、同比3.1%，8月核心环比也为0.3%；10月Fed仍强调通胀高、经济强、就业稳定，暂不支持把降息作基准。另一方面，9月名义消费增0.5%而实际消费不足0.1%、实际可支配收入下降0.3%。9月实际消费增速较8月放缓、实际DPI下降，但尚未确认持续或全面需求走弱；下一组数据需要区分价格推动和真实需求。','claim_ids':['C4','C5','C6','C14']},
 {'title':'合约是一次会议的上限调整，异常条款会改变经济语义','text':'按12月会议前后的目标区间上限变化结算，不能误读成今天到年底累计变动。正常25bp网格上的五档为降50+、降25、不变、加25、加50+，在这些条件下互斥并覆盖；非标准变化按规则例子向远离零的25bp档取整，未穷尽的非常规边界不可自行裁定。完整规则逐字保存于sources.json/S1及原始响应。','claim_ids':['C2','C16']},
 {'title':'参考价之和100.75%，双边报价和深度必须一起看','text':'五个Gamma Yes参考价相加100.75%，五个最佳bid之和99.50%、ask之和102.00%。不把原值强行拼成精确概率分布，不从该偏差直接推导套利。加25bp和不变的spread都是0.01美元/份，相当于1个百分点的支付价格；降25bp最佳bid只有20份，足见尾部参考价与可执行规模并非一回事。','claim_ids':['C9','C10','C11']},
 {'title':'真实未来状态已核实，报价采用窗口而非伪同刻','text':'事件和五个子合约均active=true、closed=false，子合约acceptingOrders=true。Gamma获取于17:17:21Z，但HTTP Date为17:14:28Z，子市场updatedAt为17:12:15Z至17:14:16Z；CLOB获取窗口17:17:41.692–41.992Z，订单簿内部时间为17:16:54.639–17:17:40.943Z。它们是同一研究窗口内的异步快照，不是原子同刻行情。另有加25bp的Gamma lastTradePrice=0.71与CLOB last_trade_price=0.290不一致；两端均无独立成交时戳，未用于结论或价格变动解释，原因未核实。','claim_ids':['C1','C8','C9','C17']}
]
market_rows=[]
cn=['降50+bp','降25bp','不变','加25bp','加50+bp']
for label,x in zip(cn,calc['rows']):
 market_rows.append([label,f"{float(x['gamma_yes_reference'])*100:.2f}%",x['yes_best_bid']+' / '+x['yes_best_ask'],x['bid_top_shares']+' / '+x['ask_top_shares'],x['clob_timestamp_utc'][11:23]])
depth_rows=[]
for label,x in zip(cn,calc['rows']):
 depth_rows.append([label,x['bid_depth_within_0_01']['shares'],x['ask_depth_within_0_01']['shares'],f"{float(x['bid_depth_within_0_01']['usd_notional']):.2f}",f"{float(x['ask_depth_within_0_01']['usd_notional']):.2f}"])

tables=[
 {'title':'盘口快照：价格为美元/1美元支付份额，规模为份（Yes侧）','columns':['结果','Gamma参考','CLOB bid / ask','最佳bid份数 / ask份数','书内UTC时间'],'rows':market_rows,'claim_ids':['C8','C9','C11']},
 {'title':'显示深度：bid向下/ask向上各0.01美元内（含边界），金额未计费用','columns':['结果','bid累计份','ask累计份','bid美元名义额','ask美元名义额'],'rows':depth_rows,'claim_ids':['C9','C11'],'note':'计算见calculations.json。远尾bid累计份大但美元金额很小；深度可撤单。未抓No侧订单簿。'},
 {'title':'契约与时间边界','columns':['项目','核实结果'],'rows':[
 ['真实对象','event id 770450；五个market id 3215005–3215009'],
 ['事件状态','active=true；closed=false；五个子合约acceptingOrders=true'],
 ['事件endDate','2026-12-10T04:59:00Z = 12月9日23:59 EST'],
 ['五个子合约endDate','2026-12-09T23:59:00Z = 12月9日18:59 EST'],
 ['官方决策会议','2026-12-08–09；附经济预测；声明发布即可结算'],
 ['比较基准','12月会议前的目标区间上限；当前上限4.00%仅是今日背景'],
 ['默认/延期','原文到“the next scheduled meeting”end date无声明则No change；next相对哪个时点、时区及截止秒均不明。2027-01-26–27仅为12月之后的日历会议，不能确定为默认截止'],
 ['规则来源','Gamma description全文；FOMC正式声明为首要结算来源；规则另指openmarket.htm，未另抓其当前页面']
 ],'claim_ids':['C1','C2','C3','C4','C16']}
]
alts=[
 {'title':'最强反方：暂停是一次观察窗口，加息路径尚未结束','text':'9月以12–0加25bp，10月2人仍要加息；核心PCE连续0.3%且Fed形容就业稳定，支持把10月暂停解释为等待而非方向反转。若下一份核心通胀保持偏强、就业未明显恶化，加25bp的解释会增强；这是定性提示，并非已校准、可重复的改判阈值。这是对盘口前“维持优先”的实质挑战。','claim_ids':['C4','C5','C7','C13','C14']},
 {'title':'加息情景的反方：单月实际消费放缓，委员会也已选择等待','text':'9月实际消费增速较8月放缓、实际DPI下降，核心环比未比8月加速；这些单月数据尚未确认持续或全面需求走弱。10月Fed以10–2维持并表示等待更多信息，是继续等待的直接政策依据。总PCE环比升0.5%不足以单独推出必须12月加息；后续核心价格和就业仅作定性更新提示，尚无校准改判阈值。','claim_ids':['C4','C5','C6','C14']},
 {'title':'规则替代解释：No change不总等于经济政策未变','text':'无声明默认条款可能把No change变成程序性结果；紧急会议若先改变利率，12月相对会前不变也可能与今天利率不同。最终复盘应同时核对政策变化与合约裁决，不用合约标签代替宏观事实。','claim_ids':['C2','C16']}
]
watch=[
 {'signal':'11月25日8:30 EST：BEA十月个人收入与支出','meaning':'检查核心PCE环比是否加速，实际消费与实际收入是否修复；价格与就业组合用于定性更新，不代表已校准、可重复的改判阈值；单次消费放缓不确认持续需求走弱。日期取自本次BEA发布，更新前再核实日历。','claim_ids':['C5','C6','C15']},
 {'signal':'随后BLS就业与CPI正式发布、修订及Fed正式沟通','meaning':'以失业率、就业修订、核心价格广度交叉检验；本次BLS页面403，暂不填数字和未核实的发布日期。若出现就业持续恶化，重新评价降息情景；此为定性提示，尚无已校准、可重复的改判阈值。','claim_ids':['C4','C14']},
 {'signal':'按日历惯例约11月18日前后关注10月会议纪要，实际发布时间另核实','meaning':'日历写通常三周后发布；不把推算日期当已公布预约。核对观望者的条件和收紧支持面是否扩大，不能把两张异议票直接变成概率。该观察也仅是定性更新提示，并非已校准改判阈值。','claim_ids':['C3','C4','C13']},
 {'signal':'12月8–9日正式声明；延期时需澄清next的指代与裁决','meaning':'可否定命题：12月正式声明若相对会前目标上限降息，或加息至少50bp，即落在本报告“维持/加25bp”两中心情景之外，记为中心情景未覆盖实际结果；这不等于此前排除尾部可能。保留正式声明和真实结算证据；无声明时不自行指定fallback会议。其余watch仅作定性更新提示，非已校准可重复阈值。无数值概率，不计算独立Brier/log loss。','claim_ids':['C2','C3','C16','C18']}
]
gaps=[
 'BLS就业与CPI即时页均403；未从搜索摘要补入未核实数字，因此缺直接劳动力与CPI基础数据。官方就业判断仅来自Fed声明。',
 'reference class只定义“相似通胀/就业约束下的常规FOMC会议”，未建立逐次历史条件样本，也无校准反应函数；独立概率留null。定性初判不能转换为概率差或收益优势。',
 '搜索插件在冻结初判前返回媒体与一家机构加息观点；未见盘口百分比，但不能称对所有外部观点完全盲法。9月决议在看价后才取得，最终观点存在锚定可能。',
 'Gamma与CLOB异步且Gamma有缓存迹象；未抓No侧深度、成交历史、费用明细或CME对照，未做执行/滑点模拟。不把网站liquidity和累计volume当可成交深度。加25bp的Gamma lastTradePrice=0.71而同Yes token的CLOB last_trade_price=0.290，均无独立成交时戳；两字段不一致且均未用于方向/价格变动结论，未核实差异成因。',
 '事件/子合约endDate相差5小时；fallback中next相对哪个时点、精确时区/截止秒、非常规变动取整的全部边界、oracle争议处理未由当前描述消除。未另抓规则指向的openmarket.htm页面。',
 '六个关键T0资料记录来自Fed、BEA、Polymarket，来源独立性有限；未扩搜社区，本轮无社区覆盖结论。',
 '报告HTML与Markdown由同一report.json生成，已作静态文本和引用检查；未在浏览器渲染、截图或验证移动设备。本轮已收到协调者转达的独立审查并定向修正，处置见independent-review.md；静态校验不代表完整独立QA，也不证明预测优势。'
]
report={'title':'12月Fed：加息有证据，70.5%仍不是独立结论','question':'Polymarket的2026年12月Fed决议合约正在定价什么，官方证据支持到哪一步？','as_of':NOW,'status':'partial','status_reason':'真实未来合约、完整规则、官方决议/PCE与盘口取得；独立概率、BLS基础数据与规则异常边界仍有缺口。','answer':'市场把加25bp列为首要结果：Gamma参考70.5%，维持27.5%。官方证据支持把加息视为实质情景：9月全票加25bp，10月虽暂停但仍有加息异议，核心PCE仍有压力。独立初判曾暂偏维持；补齐9月资料后的最终观点改为维持与加25bp并列工作情景。没有校准模型，不能判断70.5%是否错价，也不给独立点概率。下一项最明确观察是11月25日的核心PCE、实际消费及随后就业数据。','answer_claim_ids':['C4','C5','C6','C7','C8','C12','C13','C15'],'findings':findings,'tables':tables,'alternatives':alts,'watch':watch,'gaps':gaps,'sources':[{k:s[k] for k in ['id','title','url','published_at']} for s in sources],'independent_analysis':{'record':'independent-freeze.json','frozen_at':freeze['frozen_at'],'numeric_probability':None,'reference_class':freeze['reference_class'],'base_rate':None,'market_blind_scope':'对盘口盲；非对所有外部观点盲','final_vs_initial':'盘口后追加9月决议，降低维持优先排序把握；保留原始初判不改写'},'pricing':{'source':'S1/S2','normalization':'none','quote_timestamp_policy':'原始获取时间、HTTP Date、updatedAt和book timestamp并存；不声称同刻','calculation_file':'calculations.json'},'research_note':'仅为研究建议与案例方法验证，不是买卖建议。未写正式预测账本、作者库或外部平台。'}
save('report.json',report)

# Render every substantive report field from the same frozen object.
def refs(ids):return ' '.join('['+i+']' for i in ids)
def mdtable(t):
    lines=['| '+' | '.join(t['columns'])+' |','| '+' | '.join('---' for _ in t['columns'])+' |']
    lines += ['| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in row)+' |' for row in t['rows']]
    return '\n'.join(lines)
lines=['# '+report['title'],'',f"研究完成截点：{NOW}；状态：部分完成。{report['status_reason']}",'',report['answer']+' '+refs(report['answer_claim_ids']),'']
for f in report['findings']:lines+=['## '+f['title'],'',f['text']+' '+refs(f['claim_ids']),'']
for t in report['tables']:lines+=['## '+t['title'],'',mdtable(t),'',t.get('note','')+' '+refs(t['claim_ids']),'']
lines+=['## 反方与替代解释','']
for a in report['alternatives']:lines+=['**'+a['title']+'**。'+a['text']+' '+refs(a['claim_ids']),'']
lines+=['## 下一观察与改变判断的条件','']
for w in report['watch']:lines+=['- **'+w['signal']+'**：'+w['meaning']+' '+refs(w['claim_ids']),'']
lines+=['## 集中局限','']+['- '+g for g in report['gaps']]+['','## 来源与审计','']
for s in report['sources']:lines += [f"- {s['id']}：[ {s['title']} ]({s['url']})；发布时间：{s['published_at']}。"]
lines += ['',f"盘口前冻结：{freeze['frozen_at']}。完整原句、原始时间和失败记录见 [sources.json](sources.json)；结论见 [claims.json](claims.json)；计算见 [calculations.json](calculations.json)；校验见 [validation.json](validation.json)。",'',report['research_note'],'']
for c in claims:
    targets='；'.join(f"[{s['id']}]({s['url']})" for s in c['sources']) or '依据 '+', '.join(c.get('basis',[]))
    lines += [f"[{c['id']}]: #claim-{c['id'].lower()} \"{c['text']}\"",'']
# Provide explicit reachable claim anchors (Markdown footnote-like reference links alone do not create targets).
lines += ['## 结论索引','']
for c in claims:lines += [f"<a id=\"claim-{c['id'].lower()}\"></a>",f"**{c['id']}**（{c['type']}）：{c['text']}",'']
(ROOT/'report.md').write_text('\n'.join(lines))

esc=html.escape
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+esc(report['title'])+'</title><style>body{font:17px/1.8 system-ui,sans-serif;max-width:1080px;margin:36px auto;padding:0 20px;color:#202020}h1{font-size:30px}h2{font-size:22px;margin-top:36px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #ccc;padding:8px;text-align:left}th{background:#f3f3f3}.scroll{overflow-x:auto}a{color:#1258a0}li{margin:10px 0}small{color:#555}@media print{body{max-width:none;margin:0}table{font-size:11px}a{color:inherit}}</style><body>']
def h(tag,text):parts.append('<'+tag+'>'+esc(text)+'</'+tag+'>')
def hr(ids):return ' '+''.join(f'<a href="#claim-{i.lower()}">[{i}]</a> ' for i in ids)
h('h1',report['title']);h('small',f"研究完成截点：{NOW}；状态：部分完成。{report['status_reason']}");parts.append('<p>'+esc(report['answer'])+hr(report['answer_claim_ids'])+'</p>')
for f in report['findings']:h('h2',f['title']);parts.append('<p>'+esc(f['text'])+hr(f['claim_ids'])+'</p>')
for t in report['tables']:
    h('h2',t['title']);parts.append('<div class="scroll" tabindex="0"><table><thead><tr>'+''.join('<th scope="col">'+esc(c)+'</th>' for c in t['columns'])+'</tr></thead><tbody>')
    for row in t['rows']:parts.append('<tr>'+''.join('<td>'+esc(str(v))+'</td>' for v in row)+'</tr>')
    parts.append('</tbody></table></div><p>'+esc(t.get('note',''))+hr(t['claim_ids'])+'</p>')
h('h2','反方与替代解释')
for a in alts:h('h3',a['title']);parts.append('<p>'+esc(a['text'])+hr(a['claim_ids'])+'</p>')
h('h2','下一观察与改变判断的条件')
for w in watch:h('h3',w['signal']);parts.append('<p>'+esc(w['meaning'])+hr(w['claim_ids'])+'</p>')
h('h2','集中局限');parts.append('<ul>'+''.join('<li>'+esc(g)+'</li>' for g in gaps)+'</ul>');h('h2','来源与审计')
for s in report['sources']:parts.append('<p>'+esc(s['id'])+'：<a href="'+esc(s['url'],quote=True)+'">'+esc(s['title'])+'</a>；发布时间：'+esc(s['published_at'])+'</p>')
h('p',f"盘口前冻结：{freeze['frozen_at']}。完整原句和失败见sources.json；结论claims.json；计算calculations.json；校验validation.json。");h('p',report['research_note'])
parts.append('<details><summary>结论索引与证据</summary>')
for c in claims:
    parts.append('<p id="claim-'+c['id'].lower()+'"><strong>'+esc(c['id'])+'</strong>（'+esc(c['type'])+'）：'+esc(c['text'])+' '+''.join('<a href="'+esc(s['url'],quote=True)+'">'+esc(s['id'])+'</a> ' for s in c['sources'])+esc('依据 '+', '.join(c.get('basis',[])) if c.get('basis') else '')+'</p>')
parts.append('</details></body></html>');(ROOT/'report.html').write_text('\n'.join(parts))
print(json.dumps({'as_of':NOW,'claims':len(claims),'key_sources':len(sources),'files_written':['sources.json','claims.json','report.json','report.md','report.html']},ensure_ascii=False))
