"""Build this run's evidence bundle from inspected source excerpts, not source code."""
import json
from pathlib import Path
from datetime import datetime, timezone

W = Path(__file__).parent
NOW = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
def save(name, obj):
    (W/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
plan = json.loads((W/'plan.json').read_text())
plan['as_of'] = NOW
save('plan.json', plan)
sources = json.loads((W/'community-candidates.json').read_text())
sources['as_of'] = NOW
for s in sources['candidates']:
    s['id'] = 'L' + s['id'][1:]
    p = s.get('platform', '')
    if p == 'github':
        reason = 'GPU解锁、驱动及软件故障，不回答股价下跌归因'
        relevance = 'irrelevant'
    elif s.get('author', '').lower() == 'nvidia':
        reason = '官方产品宣传或活动内容，未提供股价归因增量'
        relevance = 'context'
    else:
        reason = '仅作为线索保留；本轮未完成原帖或评论定位核实，不支持外部事实或市场整体情绪'
        relevance = 'context'
    s['selection'] = dict(selected=False, reason=reason, relevance=relevance, purpose='保留社区候选及排除依据', priority='background')
sources['source_status']['official'] = {'status':'ok','reason':'NVIDIA IR财报日期公告已读'}
sources['source_status']['market_data'] = {'status':'ok','reason':'两家行情网站日期行交叉核验；底层供应商独立性未知'}
sources['source_status']['news'] = {'status':'ok','reason':'Reuters正文与36氪授权转载正文已读，归因及信用报价保留报道属性'}

def source(sid, url, publisher, tier, quote, locator, published='unknown', kind='document', supports=None, origin=None, origin_basis='原始数据供应商独立性未确认', **extra):
    row = dict(id=sid, url=url, canonical_url=url, publisher=publisher, tier=tier, published_at=published, retrieved_at=NOW, quote=quote, locator=locator, origin_id=origin, origin_basis=origin_basis, supports=supports or ['view'], evidence_kind=kind, access_status='ok', selection=dict(selected=True, reason='直接支持对应价格、归属明确报道或官方安排', relevance='direct', purpose='区分实际表现、媒体解释与官方事实', priority='decisive'))
    row.update(extra)
    sources['candidates'].append(row)

price_url = 'https://cn.investing.com/equities/nvidia-corp-historical-data'
prices = [('2026-10-02',233.95,'+1.34%'),('2026-10-06',239.24,'+0.14%'),('2026-10-29',213.66,'-0.80%'),('2026-10-30',204.64,'-4.22%')]
for n,(date,value,ret) in enumerate(prices,1):
    source('S'+str(n),price_url,'英为财情 Investing.com','T1',f'{date} | {value:.2f} | {ret}',f'历史行情每日表：{date}行，收盘价USD；引文保留原数字，日期规范化为ISO',kind='market_quote',supports=['price'], market_quote=dict(quoted_at=date+'T20:00:00Z',instrument='NASDAQ:NVDA',outcome='普通股每股收盘价格',direction='long',value=value,unit='USD/share',quote_type='close'), quote_time_basis='美国东部夏令时16:00正常收盘对应20:00Z；价格行未给盘后数据，不视为总回报')
source('S5','https://www.statmuse.com/money/ask/nvidia-stock-price-october-chart','StatMuse','T1','2026-10-02 233.95; 2026-10-06 239.24; 2026-10-29 213.66; 2026-10-30 204.64','October 2026每日OHLC表的四个日期行，close列；摘录日期及数字',kind='market_quote',supports=['view'])
reuters = 'https://www.investing.com/news/stock-market-news/nasdaq-futures-tumble-as-amazon-intel-results-deepen-ai-spending-woes-4986163'
source('S6',reuters,'Reuters，经Investing.com刊载','T2','disappointing quarterly results from Intel and Amazon; AI-related companies’ massive spending','2026-10-30收盘稿的财报触发与AI投入担忧段；短句摘录',published='2026-10-30',origin='reuters-20261030-us-stocks-close',origin_basis='页面Reuters署名，转载不是另一个独立原始出处')
source('S7',reuters,'Reuters，经Investing.com刊载','T2','or 2.86%; down 4.2%; shed 7.2%','同一收盘稿：Nasdaq下跌、NVIDIA下跌、broader semiconductor index下跌各段短语；百分比依次对应上述三项',published='2026-10-30',origin='reuters-20261030-us-stocks-close',origin_basis='页面Reuters署名，与S6同一原始报道')
credit = 'https://www.36kr.com/p/4028016585986439'
source('S8',credit,'华尔街见闻Max，经36氪授权转载','T2','资本成本实际上正在下降','2026-10-16文章转述黄仁勋美东10月15日在瑞典活动受访的段落',published='2026-10-16',origin='wallstreetcn-max-coreweave-20261016',origin_basis='36氪标明原来源华尔街见闻Max，作者李丹；仅作为归属明确的管理层观点')
source('S9',credit,'华尔街见闻Max，经36氪授权转载','T2','0.799美元；15.6%','文章援引彭博行情：10月15日盘中，2031年到期、票息9%的CoreWeave债券，每1美元面值价格及到期收益率',published='2026-10-16',origin='wallstreetcn-max-coreweave-20261016',origin_basis='二手信用行情报道，未直取债券终端；不认定为独立的违约概率证据')
official = 'https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Sets-Conference-Call-for-Third-Quarter-Financial-Results/default.aspx'
source('S10',official,'NVIDIA Investor Relations','T0','October 28, 2026; Tuesday, November 17; 2 p.m. PT (5 p.m. ET); ended October 25, 2026.; approximately 1:20 p.m. PT.','公告日期、首段季度结束日与电话会安排、第三段结果发布时间；短片段摘录',published='2026-10-28',supports=['fact'],origin='nvidia-ir-fy2027-q3-calendar',origin_basis='公司原始财报安排公告')
save('sources-before-selection.json', sources)
claims=[]
def claim(cid,text,typ,sids=(),basis=(),**extra):
    row=dict(id=cid,text=text,type=typ,as_of=NOW,sources=[{'source_id':s} for s in sids])
    if basis:row['basis']=list(basis)
    row.update(extra);claims.append(row)
for n,(date,value,ret) in enumerate(prices,1):
    claim('C'+str(n),f'英为财情历史行情表中，NVDA于{date}正常交易收盘价为{value:.2f}美元。','price',['S'+str(n)],price_kind='close')
claim('C5','同一组收盘价格计算：10月30日单日跌4.22%；10月2日至30日跌12.53%；10月6日至30日跌14.46%。阶段变化不是完整自然月收益，也不是盘中高点回撤。','inference',basis=['C1','C2','C3','C4'],calculation_ids=['K1','K2','K3'])
claim('C6','Reuters的10月30日收盘报道把抛售与Intel、Amazon令人失望的季报及AI相关公司的大规模支出担忧联系起来；这是记者归因，未隔离各因素因果贡献。','view',['S6'])
claim('C7','Reuters在同日收盘稿报道Nasdaq跌2.86%、NVIDIA跌约4.2%、半导体指数跌7.2%；两家行情网站的NVDA收盘价与约4.2%的跌幅相符。','view',['S7','S5'])
claim('C8','按NVDA精确计算收益与Reuters报道基准比较，10月30日NVDA比Nasdaq多跌约1.36个百分点，比半导体指数少跌约2.98个百分点；这是当日相对收益，不是风险调整超额收益。','inference',basis=['C5','C7'],calculation_ids=['K4','K5'])
claim('C9','36氪授权转载报道，CoreWeave的2031年到期9%票息债券于10月15日盘中每1美元面值报价0.799美元、收益率15.6%；该信用行情本轮未由交易终端复核。','view',['S9'])
claim('C10','同篇报道引述黄仁勋10月15日称CoreWeave的资本成本实际上正在下降；这是管理层乐观判断，不构成实际融资成本下降或风险解除的证明。','view',['S8'])
claim('C11','NVIDIA于10月28日发布公告，安排11月17日发布FY2027第三季度结果，财季截至10月25日；该安排公告本身不披露当季业绩。','fact',['S10'])
claim('C12','现有同期表现与报道更支持把10月30日下跌理解为行业及AI投资回报担忧中的一次重估：NVDA弱于大盘，却强于半导体基准。尚不能从这些材料确认英伟达出现独立经营恶化，也不能精确分拆跌幅来源；阶段跌幅不能全部归给10月30日新闻。','inference',basis=['C5','C6','C7','C8','C11'])
claim('C13','融资压力的可能机制为：客户借款成本上升压低项目回报和扩张能力，可能影响未来GPU采购与付款，再压低英伟达增长估值；这一链条目前只观察到媒体报道的信用压力，未核实采购取消、延期或英伟达收款恶化。','inference',basis=['C6','C9','C10'])
claim('C14','黄仁勋的乐观表态构成融资风险解释的反方，但与二手报道的高债券收益率存在张力；需要实际新融资条件及采购履约资料区分短期市场压力和持续融资困难。','inference',basis=['C9','C10','C13'])
claim('C15','后续应对照11月17日财报的收入、后续指引、毛利率与收款情况，以及客户融资和采购履约变化：若经营兑现而信用压力缓解，估值调整解释增强；若订单、指引或现金回收转弱，经营传导解释增强。此为可检验情景而非已发生事实。','inference',basis=['C11','C12','C13','C14'])
ledger=dict(schema_version=2,as_of=NOW,historical=False,claims=claims)
save('claims.json',ledger)
calculations=[]
def calc(k,desc,formula,inputs,result,unit,refs):
    calculations.append(dict(id=k,description=desc,formula=formula,inputs=[dict(name=name,value=value,unit=u,claim_ids=ids) for name,value,u,ids in inputs],result=dict(value=result,unit=unit),claim_ids=refs))
daily=(204.64/213.66-1)*100
calc('K1','10月30日NVDA收盘价格收益率','(204.64 / 213.66 - 1) * 100',[('end',204.64,'USD/share',['C4']),('start',213.66,'USD/share',['C3'])],daily,'percent',['C3','C4','C5'])
calc('K2','10月2日至30日NVDA收盘价格变化','(204.64 / 233.95 - 1) * 100',[('end',204.64,'USD/share',['C4']),('start',233.95,'USD/share',['C1'])],(204.64/233.95-1)*100,'percent',['C1','C4','C5'])
calc('K3','10月6日至30日NVDA收盘价格变化','(204.64 / 239.24 - 1) * 100',[('end',204.64,'USD/share',['C4']),('start',239.24,'USD/share',['C2'])],(204.64/239.24-1)*100,'percent',['C2','C4','C5'])
calc('K4','NVDA减Nasdaq当日收益，非风险调整','NVDA_return - Nasdaq_return',[('NVDA',daily,'percent',['C5']),('Nasdaq_reported',-2.86,'percent',['C7'])],daily+2.86,'percentage points',['C5','C7','C8'])
calc('K5','NVDA减半导体指数当日收益，非风险调整','NVDA_return - semiconductor_return',[('NVDA',daily,'percent',['C5']),('semiconductor_reported',-7.2,'percent',['C7'])],daily+7.2,'percentage points',['C5','C7','C8'])
save('calculations.json',calculations)
report=dict(schema_version=2,title='英伟达大跌：行业重估更有证据，融资风险尚待经营数据验证',question=plan['question'],type='asset',task='变化解释',as_of=NOW,
answer=dict(text='截至11月1日，本轮证据更支持行业与AI投入回报担忧中的重估。10月30日NVDA跌4.22%，弱于Nasdaq的-2.86%，但强于半导体基准的-7.2%；不能据此确认公司特有经营恶化，也不能把整段12.53%的跌幅都归给当日新闻。',claim_ids=['C5','C6','C7','C8','C12']),
findings=[
 dict(title='当日跌幅放入行业基准后，归因方向改变',text='10月30日NVDA比Nasdaq多跌1.36个百分点，却比半导体指数少跌2.98个百分点。共同下跌支持行业解释，相对表现不能证明英伟达没有自身问题，更不是风险调整后的异常收益。',claim_ids=['C5','C7','C8','C12'],why_it_matters='只看NVDA的绝对跌幅容易把行业冲击误认作公司独立坏消息。',increment=dict(kind='calculation',baseline='前轮短评给出了NVDA绝对跌幅及Nasdaq比较，尚未计算半导体相对表现',detail='增加同日半导体基准和两组百分点比较，缩小公司独立冲击的可支持范围'),calculation_ids=['K4','K5']),
 dict(title='直接催化有报道依据，长期传导仍缺订单证据',text='Reuters把10月30日科技抛售与Intel、Amazon季报和AI支出回报担忧联系起来。融资压力可能影响客户项目经济性、采购和付款，再影响英伟达未来收入与估值；本轮没有核实采购取消或收款恶化，不能把这一机制写成已发生的经营事实。',claim_ids=['C6','C12','C13'],why_it_matters='区分当日新闻催化、预期折价与已经兑现的经营下滑。',increment=dict(kind='connection',baseline='Reuters仅给行业新闻归因，CoreWeave报道仅给信用市场压力',detail='连接客户融资到GPU采购和英伟达估值，并标出未观测的中间环节')),
 dict(title='管理层乐观与信用市场压力应同时保留',text='媒体报道CoreWeave一只2031年债券10月15日盘中收益率15.6%，黄仁勋同期称其资本成本在下降。前者为未直取终端的二手报价，后者为管理层观点；两者没有共同证明风险已解除，也没有证明融资链将断裂。',claim_ids=['C9','C10','C14'],why_it_matters='用实际融资条件和履约资料检验分歧，比把乐观表态或高收益率单独当结论更有用。',increment=dict(kind='contradiction',baseline='债券压力报道与管理层资本成本下降表态',detail='将相反信号按证据性质配对，不把观点升级为融资交易事实'))],
alternatives=[dict(title='公司自身预期下修仍是竞争解释',text='不能因为NVDA当日强于半导体指数就排除公司风险。现有材料未建立公司独立业绩下修的事件链；11月17日安排公告也不能替代尚未发布的当季结果。',claim_ids=['C8','C11','C12']),dict(title='利率与风险偏好可能叠加，但未定量分拆',text='行业共同下跌也可能包含折现率与风险偏好变化。缺少同口径事件窗口和控制变量时，本轮不分配各因素贡献比例。',claim_ids=['C12','C13'])],
watch=[dict(signal='11月17日财报：实际收入、后续指引、毛利率与应收/经营现金流',meaning='经营兑现且回款正常更支持预期重估；指引或现金回收转弱则支持压力开始进入经营。',claim_ids=['C11','C15']),dict(signal='客户实际新融资条件，以及GPU采购取消、延期与付款履约资料',meaning='信用利差或管理层言论本身不能替代融资成交和订单证据。',claim_ids=['C13','C14','C15'])],
limitations=[dict(text='归因是基于同期表现与记者报道的研究推断，没有识别因果贡献；当日比较不能外推整段窗口。',material=True,claim_ids=['C12']),dict(text='行情网站底层供应商独立性未确认；Nasdaq和半导体收益保留Reuters报道口径；债券报价未直取交易终端。',material=True,claim_ids=['C7','C9']),dict(text='社区原始候选、排名、聚类和状态已保留，但未完成原帖取证的条目均未选入结论。YouTube访问受限，Stocktwits代码解析失败；这些状态不代表平台没有讨论。',material=False,claim_ids=[])],
tables=[dict(title='价格变化与同日基准',columns=['期间/指标','起点','终点','变化'],rows=[['NVDA 10/29至10/30收盘','$213.66','$204.64','-4.22%'],['NVDA 10/02至10/30收盘','$233.95','$204.64','-12.53%'],['NVDA 10/06至10/30收盘','$239.24','$204.64','-14.46%'],['Nasdaq 10/30（Reuters报道）','同日收盘比较','—','-2.86%'],['半导体指数 10/30（Reuters报道）','同日收盘比较','—','-7.20%']],claim_ids=['C1','C2','C3','C4','C5','C7'],note='NVDA为未明确复权口径的正常收盘价格收益，不作总回报断言；两组阶段表现不是自然月回报或盘中最高点回撤。')],calculations=calculations)
save('report.json',report)
print(json.dumps({'as_of':NOW,'sources':len(sources['candidates']),'claims':len(claims),'work':str(W)},ensure_ascii=False))
