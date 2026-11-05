"""Add this run's official-source findings to its own generated evidence files."""
import json
from pathlib import Path
from datetime import datetime,timezone
W=Path(__file__).parent
now=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def load(n):return json.loads((W/n).read_text())
def save(n,d):(W/n).write_text(json.dumps(d,ensure_ascii=False,indent=2))
s=load('sources-before-selection.json');l=load('claims.json');r=load('report.json');p=load('plan.json')
for d in (s,l,r,p):d['as_of']=now
for c in l['claims']:c['as_of']=now

def add(sid,url,publisher,quote,loc,published,origin):
 s['candidates'].append(dict(id=sid,url=url,canonical_url=url,publisher=publisher,tier='T0',published_at=published,retrieved_at=now,quote=quote,locator=loc,origin_id=origin,origin_basis='发行人或指数编制者原始页面；仅用于对应披露和指数数据',supports=['fact','view'],evidence_kind='document',access_status='ok',selection=dict(selected=True,reason='新增官方证据，检验客户支出与行业相对表现',relevance='direct',purpose='核对归因机制与反方',priority='decisive'),retrieval_note='retrieved_at为主研究者收到并冻结已读取工具输出的时刻，不冒称HTTP响应时刻'))
add('S11','https://indexes.nasdaq.com/Index/Overview/sox?trk=test','Nasdaq Indexes','DATA AS OF 10/30/2026 10,688.80 -829.40 -7.20%','PHLX Semiconductor/SOX标题下的数据行；未明确列出具体时区时刻或close字段','unknown','nasdaq-sox-20261030')
add('S12','https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Third-Quarter-Results/default.aspx','Amazon Investor Relations','Operating cash flow -- trailing twelve months (TTM): 168,300; Free cash flow -- TTM (1): -42,357; Purchases of property and equipment, net of proceeds from sales and incentives -- TTM: 210,657. This increase primarily reflects investments in artificial intelligence.','Supplemental Financial Information，TTM截至2026-09-30列，单位USD millions；数字摘录与原句。不是Q3单季','2026-10-29','amazon-2026-q3-release')
add('S13','https://www.intc.com/news-events/press-releases/detail/1786/intel-reports-third-quarter-2026-financial-results','Intel Investor Relations','Revenue, gross margin and earnings per share exceeded guidance','CFO David Zinsner引语，Q3 2026业绩新闻稿；guidance指公司自身指引','2026-10-29T20:01:00Z','intel-2026-q3-release')
add('S14','https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027','NVIDIA Newsroom','Revenue is expected to be $108.0 billion, plus or minus 2%. NVIDIA is not assuming any Data Center compute revenue from China in its outlook.','FY2027 Q2公告Outlook首条，Q3展望；2026-08-26，窗口外背景，不冒充10月新消息','2026-08-26','nvidia-fy2027-q2-release')
add('S15','https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Third-Quarter-Results/default.aspx','Amazon Investor Relations','数据摘录（非逐字句子）：TTM经营现金流2026/2025为168,300/130,691；净PP&E购买210,657/115,903；FCF -42,357/14,788，单位USD millions。','Supplemental Financial Information，同口径TTM截至2026-09-30和2025-09-30两列','2026-10-29','amazon-2026-q3-release')

def c(cid,text,typ,sids=(),basis=(),**extra):
 x=dict(id=cid,text=text,type=typ,as_of=now,sources=[dict(source_id=x) for x in sids]);x.update(extra)
 if basis:x['basis']=list(basis)
 l['claims'].append(x)
c('C16','Nasdaq官方SOX页面所示10月30日变化为-7.20%，指数10688.80；该数据行未注明具体时刻和close，不能冒充有收盘时戳的终端记录。','fact',['S11'])
c('C17','Amazon披露截至2026年9月30日过去12个月经营现金流1683.00亿美元、净PP&E购买2106.57亿美元、自由现金流负423.57亿美元；公司称净资本购买增加主要反映AI投资。同期上一年FCF正147.88亿美元。该数据是TTM，不是Q3一季。','fact',['S12','S15'])
c('C18','Intel在10月29日官方稿中称Q3收入、毛利率和EPS超过自身指引；这不等于超过分析师预期，也不能把媒体失望评价写成低于公司指引。','fact',['S13'])
c('C19','NVIDIA于8月26日官方Q2财报给Q3收入指引1080亿美元±2%，不假设来自中国的数据中心计算收入。这是窗口外基准，不能证明10月实际交付或11月即将公布结果一定达标。','fact',['S14'])
c('C20','Amazon官方数据具体支持AI资本支出对客户现金流的压力；但经营现金流仍为正且同比增加，自由现金流转负不能单独证明客户融资危机或削减英伟达采购。Intel超过自身指引说明需要区分公司指引与市场预期。','inference',basis=['C6','C17','C18','C19'])
c('C21','按Amazon公司同口径TTM数据，1683.00亿经营现金流减2106.57亿净PP&E购买等于负423.57亿自由现金流；资本支出超过经营现金流423.57亿美元，不能将全年跨度金额当作一个季度。','inference',basis=['C17'],calculation_ids=['K6'])
# Strengthen existing inference bases, retaining reported-vs-observed distinctions.
for x in l['claims']:
 if x['id']=='C12':x['basis']+=['C16','C20']
 if x['id']=='C13':x['basis']+=['C17','C20']
 if x['id']=='C7':
  x['text']='Reuters在10月30日收盘稿报道Nasdaq跌2.86%、NVIDIA跌约4.2%、半导体指数跌7.2%；官方SOX日期数据另支持-7.20%，但未给具体收盘时戳。'
  x['sources']=[dict(source_id='S7')]
 if x['id']=='C8':x['basis']+=['C16']
k=dict(id='K6',description='Amazon TTM经营现金流减净资本购买对账',formula='168300 - 210657 = -42357',inputs=[dict(name='TTM operating cash flow',value=168300,unit='USD million',claim_ids=['C17']),dict(name='TTM net PP&E purchases',value=210657,unit='USD million',claim_ids=['C17'])],result=dict(value=168300-210657,unit='USD million'),claim_ids=['C17','C21'])
r['calculations'].append(k)
r['answer']['text']='截至11月1日，本轮证据更支持行业与AI投入回报担忧中的重估。10月30日NVDA跌4.22%，弱于Nasdaq报道的-2.86%，但强于半导体基准约-7.2%。Amazon官方现金流提供客户AI资本支出压力的具体依据；仍未核实它已导致英伟达采购或回款恶化，也不能把整段12.53%的跌幅全归给当日新闻。'
r['answer']['claim_ids']+=['C16','C17','C20']
r['findings'][0]['claim_ids']+=['C16']
r['findings'].insert(1,dict(title='客户资金压力已有官方数字，采购转弱仍未证实',text='Amazon披露TTM经营现金流1683.00亿美元，净PP&E购买2106.57亿美元，两者相减为负423.57亿美元自由现金流；公司将资本购买增加主要归于AI。经营现金流为正且同比增长，说明现金流压力来自支出规模，不等于主营业务已不产生现金。资本支出大既支撑芯片需求，也提高持续融资与回报要求，不能直接推出取消GPU订单。',claim_ids=['C17','C20','C21'],why_it_matters='把抽象的AI烧钱叙事落实到客户现金流，并标出向英伟达经营传导的证据缺口。',increment=dict(kind='calculation',baseline='前轮主要依赖Reuters归因和CoreWeave债券压力报道',detail='加入Amazon公司官方TTM现金流对账，区分经营造血与资本支出'),calculation_ids=['K6']))
r['findings'][2]['text']+=' Intel官方称Q3超过自身指引，故“市场失望”需保留媒体归因标签，不能写成未达到公司原指引。'
r['findings'][2]['claim_ids']+=['C18','C20']
r['alternatives'][0]['text']+=' 8月26日的Q3收入指引1080亿美元±2%只作为待核对的旧基准，不能替代最新市场预期。'
r['alternatives'][0]['claim_ids']+=['C18','C19']
r['watch'][0]['meaning']+=' 可对照8月26日1080亿美元±2%的原指引，但它不是最新分析师预期。'
r['watch'][0]['claim_ids']+=['C19']
r['limitations'][1]['text']='行情网站底层供应商独立性未确认；Nasdaq综合指数收益保留Reuters报道口径；SOX官方日期行未列精确收盘时戳；债券报价未直取交易终端。'
r['limitations'][1]['claim_ids']+=['C16']
r['limitations'].append(dict(text='本轮未获取同期分析师一致预期或10月2日至30日完整行业基准序列，不能量化财报预期差，不能把单日相对表现外推整段阶段回撤。',material=True,claim_ids=['C12','C18','C19']))
r['tables'][0]['rows'][-1]=['半导体指数 10/30（Reuters+Nasdaq日期数据）','同日比较','未列精确收盘时戳','-7.20%']
r['tables'][0]['claim_ids']+=['C16']
r['tables'].append(dict(title='Amazon TTM现金流对账',columns=['截至9月30日的过去12个月','2026年，亿美元','2025年，亿美元'],rows=[['经营现金流',1683.00,1306.91],['净PP&E购买',2106.57,1159.03],['自由现金流',-423.57,147.88]],claim_ids=['C17','C21'],note='公司定义的自由现金流口径；PP&E为物业设备净购买，不是资产余额，不能当作Q3单季支出。'))
for name,obj in [('sources-before-selection.json',s),('claims.json',l),('report.json',r),('plan.json',p),('calculations.json',r['calculations'])]:save(name,obj)
save('official-supplement.json',dict(captured_at=now,source_ids=['S11','S12','S13','S14','S15'],query_count=3,agent_webfetch_count=5,main_verification_urls=[x['url'] for x in s['candidates'] if x['id'] in ['S12','S13']],note='主研究者收取并冻结工具输出时刻，非HTTP时戳；官方原句与数值摘录见来源账本'))
print('Enriched bundle:',len(l['claims']),'claims;',len(s['candidates']),'sources; as_of',now)
