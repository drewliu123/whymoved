# -*- coding: utf-8 -*-
import json, hashlib, datetime, pathlib
P=pathlib.Path('/Users/frankzhang/Desktop/投研助手/journal/four-type-validation-20261031/theme')
ASOF='2026-10-31T17:25:57Z'
BASE='https://www.eaton.com'
IR=BASE+'/us/en-us/company/investor-relations/financial-presentations-webcasts.html'
D=BASE+'/content/dam/eaton/company/investor-relations/quarterly-earnings/filings/'
def write(n,x):
 (P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def source(i,title,url,date,file,quotes,period):
 f=P/file
 return dict(id=i,title=title,url=url,retrieval_url=url.replace('https://www.eaton.com','https://origin-edge.eaton.com'),publisher='Eaton',tier='T0',published_at=date,event_period=period,retrieved_at=datetime.datetime.fromtimestamp(f.stat().st_mtime,datetime.timezone.utc).isoformat().replace('+00:00','Z'),status='success',local_file=file,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),version='本次截点获取的官网版本，未独立核对SEC归档版本',excerpts=[dict(locator=a,original=b) for a,b in quotes])
S=[source('S1','Eaton financial presentations and webcasts',IR,'unknown','raw/eaton-ir/browser-extract.json',[
 ('Third quarter 2026','Eaton will announce third quarter 2026 earnings on Tuesday, November 3, 2026, before the opening of the New York Stock Exchange.'),
 ('Forward-looking statement','Factors that could cause actual results to differ materially from those in the forward-looking statements include: unanticipated changes in the markets for the Company’s business segments, unanticipated downturns in business relationships with customers or their purchases from us, competitive pressures on sales and pricing, unexpected increases in the cost of material and other production costs that cannot be recouped in product pricing, introduction of competing technologies')], '截至获取时页面列示Q2/Q1 2026；Q3待发布'),
source('S2','Fourth quarter 2025 earnings complete',D+'2025/q4/4Q-2025-earnings-complete.pdf','2026-02-03','raw/eaton-q4/complete.pdf',[
 ('p3 Business Segment Results','Sales for the Electrical Americas segment were a record $3.5 billion, up 21% from the fourth quarter of 2024.'),
 ('p8 Business Segment Information（列顺序2025Q4/2024Q4/2025FY/2024FY）','Electrical Americas $ 1,046 $ 918 $ 3,972 $ 3,455'),
 ('p10 Non-GAAP financial information','Operating cash flow $ 1,965 $ 1,597\nCapital expenditures for property, plant and equipment (392) (255)\nFree cash flow $ 1,573 $ 1,342'),
 ('p8 Net sales rows; also raw complete.txt lines220–226','Electrical Americas $ 2,905 $ 13,276 $ 11,436\nElectrical Global 1,728 1,569 6,815 6,248\nAerospace 1,111 971 4,249 3,744\nVehicle 586 647 2,505 2,790\neMobility 125 147 604 662\nTotal net sales $ 7,055 $ 6,240 $ 27,448 $ 24,878')], '2025Q4/FY2025；PDF多列抽取顺序需结合原表，2025Q4美洲销售3506'),
source('S3','First quarter 2026 analyst presentation',D+'2026/q1/q1-2026-analyst-presentation.pdf','2026-05-05','raw/eaton-q1-presentation/analyst.pdf',[
 ('p3 Highlights','In Q1, Electrical Americas data center orders are up approximately 240% and revenue up approximately 50% versus 1Q25 demonstrating continued strong momentum in this rapid growth market.'),
 ('p9 Electrical Americas Segment','Sales\n1Q ‘26\n1Q ‘25 V ‘25\n$3,600\n$3,010\n20%\nOperating Profit\n922\n904\n2%\nOperating Margin\n25.6%\n30.0%\n(440) bps'),
 ('p9 bullets','• Orders up 42% on rolling 12-month basis, including\ndata centers, up ~240% in the quarter\n• Book-to-bill ratio 1.2 on rolling 12-month basis\n• Backlog up $4.4B or 44% year-over-year'),
 ('p5 chart; visual verified raw/eaton-q1-presentation/page-5.png','Total backlog ($B) / Rolling 12 Month Organic Order Growth: 4Q25 $13.2 / 16%; 1Q26 $14.5 / 42%'),
 ('p6 portfolio headings','Power Generation & Grid Connection; Gray Space Power Conditioning, Isolation, & Stability; White Space Power Conditioning, Delivery, & Stability; Software & Services; Cooling'),
 ('p7 Beam Rubin DSX Platform','Faster deployment amid power constraints\nSolving for grid limitations and engineering build requirements\nto keep up with AI growth cycles\nPre-engineered, modular power and cooling')], '2026Q1；同比2025Q1'),
source('S4','Second quarter 2026 earnings complete',D+'2026/q2/q2-20265-earnings-complete.pdf','2026-07-31','raw/eaton-q2/complete.pdf',[
 ('p8 Business Segment Information；2026Q2/2025Q2/2026H1/2025H1','Electrical Americas $ 1,088 $ 987 $ 2,010 $ 1,891'),
 ('p8 sales row; original multi-column order in raw text','Electrical Americas $ 3,350 $ 7,551 $ 6,360'),
 ('p3 Business Segment Results','The twelve-month rolling average of orders in the second quarter was up 41% organically. Total backlog at the end of June remained strong and was up 33% over June 2025.'),
 ('p10 Non-GAAP reconciliation','Operating cash flow $ 1,127 $ 918\nCapital expenditures for property, plant and equipment (253) (202)\nFree cash flow $ 874 $ 716'),
 ('p3 Electrical Global','The sales increase consisted of 18% growth in organic sales, 25% contribution from Boyd Thermal in its first full quarter post-acquisition, and 1% growth from foreign exchange.'),
 ('p7 Net income / adjusted earnings','Net income attributable to Eaton ordinary shareholders $ 821 $ 982 $ 1,687 $ 1,945\nExcluding acquisition and divestiture charges, after-tax 190 54 278 61\nExcluding restructuring program charges, after-tax 19 18 49 33\nExcluding intangible asset amortization expense, after-tax 198 101 308 185\nAdjusted earnings $ 1,228 $ 1,155 $ 2,322 $ 2,225'),
 ('p11 Fibrebond','Fibrebond is a U.S. based designer and builder of pre-integrated modular power enclosures for data center, industrial, utility and communications customers. Fibrebond is reported within the Electrical Americas business segment.'),
 ('p12 Boyd Thermal','On March 12, 2026, Eaton acquired Boyd Thermal for $9.55 billion, net of cash acquired.')], '2026Q2/H1；同比2025Q2/H1；URL中20265为官网真实文件名'),
source('S5','Second quarter 2026 analyst presentation',D+'2026/q2/q2-2026-analyst-presentation.pdf','2026-07-31','raw/eaton-q2-presentation/analyst.pdf',[
 ('p3 Highlights','In Q2, Electrical Sector data center orders are up approximately 85% and revenue up approximately 65% versus 2Q25 demonstrating continued strong momentum in this rapid growth market.'),
 ('p8 Electrical Americas Segment','Sales\n2Q ‘26\n2Q ‘25 V ‘25\n$3,951\n$3,350\n18%\nOperating Profit\n1,088\n987\n10%\nOperating Margin\n27.5%\n29.5%\n(200) bps'),
 ('p8 bullets','• Book-to-bill ratio 1.3 on rolling 12-month basis\n• Backlog up $3.8B or 33% year-over-year'),
 ('p6 chart; visual verified raw/eaton-q2-presentation/page-6.png','Total backlog ($B): 4Q25 $13.2; 2Q26 $15.2. Segment margin: 1Q26 25.6%; 2Q26 27.5%; 2H26 >30%.'),
 ('p12 exposure; visual verified raw/eaton-q2-presentation/page-12.png','Data Centers & Distributed IT — 21% of 2025 Eaton Sales'),
 ('p13 guidance','Electrical Americas: Organic Growth Guidance 14 – 16%; Operating Margin Guidance 28.8 – 29.2%')], '2026Q2；专项口径Electrical Sector；敞口分母2025全公司销售'),
source('S6','Eaton expands modular electrical enclosures capacity, Arkansas',BASE+'/us/en-us/company/news-insights/news-releases/2026/eaton-expands-manufacturing-for-modular-electrical-enclosures.html','2026-09-02','raw/eaton-capacity/browser-extract.json',[
 ('opening paragraph','CLEVELAND – Intelligent power management company Eaton (NYSE:ETN) today announced a more than $242 million investment to expand its U.S. manufacturing footprint with a new facility in North Little Rock, Arkansas.'),
 ('opening paragraph','The company expects to double its U.S. manufacturing capacity of customized electrical enclosures from the Fibrebond business to help meet growing demand across data center, utility, industrial and digital communications markets.'),
 ('Highlights','New Arkansas facility builds on Fibrebond’s over 40 years in Minden, Louisiana, where production capacity has doubled over the past three years and Eaton continues to invest')], '2026-09-02扩产宣布；非已投产')]
S[2]['excerpts'].append(dict(locator='p9 Sales Growth',original='Sales Growth:\nOrganic 14%\nAcquisition 5%\nForex 1%\nTotal 20%'))
S[4]['excerpts'].append(dict(locator='p8 Sales Growth',original='Sales Growth:\nOrganic 18%\nAcquisition 0%\nForex 0%\nTotal 18%'))
S[3]['excerpts'].append(dict(locator='p13 acquisition charges / p8 Corporate; see raw/eaton-q2/complete.txt lines440–447',original='Employee transaction and retention award compensation expense related to the acquisition of Fibrebond of $27 million and $39 million in the second quarter and the first six months of 2026, respectively, and $47 million in the second quarter and the first six months of 2025.\nCharges in 2026 and 2025 were included in Cost of products sold, Selling and administrative expense, Research and development expense, or Other expense (income) - net. In Business Segment Information, the charges were included in Other expense - net.'))
# Excerpts transcribed from chart images explicitly mark that distinction; original PDF remains available.
for s in S:
 for e in s['excerpts']:
  e['extraction']='chart transcription (labels/numbers; not a prose quotation)' if 'chart' in e['locator'] or 'exposure' in e['locator'] else 'verbatim excerpt/text-layer; multi-column rows retain extraction order'
smap={s['id']:s for s in S}
C=[]
def claim(i,text,ss=None,basis=None):
 c=dict(id=i,text=text,type='inference' if basis else 'fact',as_of=ASOF,sources=[{k:smap[s][k] for k in ['url','publisher','tier','published_at']}|{'source_id':s} for s in (ss or [])])
 if basis:c['basis']=basis
 C.append(c)
claim('C1','截至截点，Eaton官网列示Q3 2026将于11月3日发布；本研究最新已实现季度为2026Q2，不能将Q3指引当实际。',['S1','S4'])
claim('C2','Electrical Americas 2025Q4销售3506百万美元、分部经营利润1046百万美元；滚动12个月有机订单同比增16%，backlog为13.2十亿美元。',['S2','S3'])
claim('C3','Electrical Americas 2026Q1销售3600百万美元、经营利润922百万美元，同比分别20%和2%（公司取整）；销售增长含有机14、并购5、汇率1个百分点；利润率25.6%，上年30.0%；滚动订单增42%，backlog14.5十亿美元，同比增44%。',['S3'])
claim('C4','Electrical Americas 2026Q2销售3951百万美元、经营利润1088百万美元；销售同比增18%全有机，未经恒定范围调整；利润率27.5%，上年29.5%；滚动有机订单同比增41%，backlog15.2十亿美元、同比增33%，滚动book-to-bill 1.3。',['S4','S5'])
claim('C5','2026Q1 Electrical Americas数据中心当季订单约增240%、收入约增50%；2026Q2披露改为Electrical Sector数据中心当季订单约增85%、收入约增65%；后者未在该条注明有机口径。',['S3','S5'])
claim('C6','两季数据中心专项口径不同，240%到85%不能被解释为同一业务订单减速，50%到65%也不能直接写成同一业务收入加速。',basis=['C5'])
claim('C7','Eaton披露Data Centers & Distributed IT占2025全公司销售21%；2025公司销售27448百万美元。该分类包括Distributed IT，不等于纯AI数据中心。',['S2','S5'])
claim('C8','以披露分类和全年销售相乘，2025 Data Centers & Distributed IT销售量级约5764百万美元；这是历史敞口近似，不是AI收入、市场TAM或市占率。',basis=['C7'])
claim('C9','2026Q2全公司经营现金1127百万美元、capex253百万美元、FCF874百万美元；2025Q2分别918、202、716。2025Q4分别1965、392、1573，现金口径均为全公司。',['S2','S4'])
claim('C10','2026Q2全公司GAAP归属净利润821百万美元，上年982；调整后盈利1228，上年1155。Fibrebond员工交易/留任等并购相关费用在分部信息中计为Corporate Other expense，摊销与重组亦列Corporate；分部利润未包含这些全经济成本，不等于全公司净利润或现金，Corporate全部费用不能归AI。',['S4'])
claim('C11','按原表重算，Electrical Americas 2026Q1同比增量利润/增量收入约3.05%，2026Q2约16.81%；Q2利润率环比改善约193基点但同比仍低约193基点，公司按披露利润率取整表述为+190/-200基点。Q1销售增20%含有机14、并购5、汇率1个百分点；Q2增18%全为有机。两个增量比率未经范围调整，不能单独证明效率改善。',basis=['C3','C4'])
claim('C12','美洲backlog从2025Q4的13.2十亿美元升至2026Q2的15.2，增长约15.15%；期末存量相当于Q2季度销售约3.85倍，不能当作3.85个季度的交付保证。',basis=['C2','C4'])
claim('C13','Eaton的官方产品范围从Grid Connection、Gray Space、White Space延伸至软件服务和冷却；Fibrebond提供预集成模块化电力围护结构，计入Electrical Americas。',['S3','S4'])
claim('C14','2026年9月Eaton宣布超过242百万美元投入Arkansas新厂，拟将Fibrebond美国定制电气围护结构产能翻倍；Minden产能此前三年已翻倍。公告未给新厂投产日期，且服务数据中心、公用事业等多个市场。',['S6'])
claim('C15','Q2 Electrical Global销售增长44%中，有机18%、Boyd Thermal并购贡献25%、汇率1%；不能把该分部全部增长归为AI新增需求。',['S4'])
claim('C16','最值得验证的是Electrical Americas中数据中心相关配电/预集成供电设备的backlog转交付，再转增量经营利润与现金；已有订单与收入增长披露及分部利润率恢复，与交付爬坡改善相容；未识别同批订单转换，价格、组合及并购基数亦可解释，AI独立盈利归因尚未建立。',basis=['C3','C4','C5','C9','C11','C13'])
claim('C17','用电增长先要形成获电/建设安排和设备规格，才可能成为设备采购；订单积累后还需制造、安装/验收与回款。运行TWh不能直接乘设备单价推导收入；投运延迟对订单、交付、收入、现金可发生在不同时间。',basis=['C5','C9','C13','C14'])
claim('C18','扩产同时支持交付并削弱永久稀缺假设：若产能释放快于有效采购，价格与利用率可能承压；现有分部数字不能识别扩产成本、价格、产品组合各自贡献。',basis=['C3','C4','C14'])
claim('C19','本次核对的六个官方来源未提供AI专属收入基数、增量毛利率/成本桥、取消延期条款及项目回款结构，不能计算可辩护的AI增量利润点估计或给出取消率。',basis=['C3','C4','C5','C7','C9','C13','C14'])
claim('C20','Q2材料将Electrical Americas下半年利润率>30%展示为展望，全年28.8–29.2%为指引，均未在本截点实现。',['S5'])
claim('C21','若后续订单/积压仍强而增量利润率与现金兑现继续改善，交付爬坡解释增强；若订单延期、margin恢复停滞或现金落后，应下调利润兑现判断。',basis=['C4','C9','C11','C14','C20'])
claim('C22','竞争和替代的证据限于Eaton披露的竞争定价/技术风险、模块化和液冷路线变化；没有直接竞品订单、价格、成本曲线，不能断言Eaton具永久定价权或排名全行业最优。',basis=['C13','C14','C15'])
# explicit fact source of competitive risk for inference basis
claim('C23','Eaton官网风险提示包括competitive pressures on sales and pricing及introduction of competing technologies。',['S1'])
next(c for c in C if c['id']=='C22')['basis'].append('C23')
write('claims.json',dict(question='AI数据中心用电增长如何转成电力设备供应商收入与利润，哪个环节最值得验证？',as_of=ASOF,claims=C))
failures=[dict(url=BASE+'/il/en-gb/company/news-insights/news-releases/2026/eaton-reports-record-second-quarter-2026-results.html',method='WebFetch',status='failed',error='timeout of 60000ms exceeded',fallback='origin-edge官方镜像+原始PDF成功'),dict(url=BASE+'/my/en-us/company/news-insights/news-releases/2026/eaton-reports-record-first-quarter-2026-results.html',method='WebFetch',status='failed',error='timeout of 60000ms exceeded',fallback='origin-edge+PDF'),dict(url=BASE+'/us/en-us/company/news-insights/news-releases/2026/eaton-reports-record-second-quarter-2026-results.html',method='WebFetch/curl',status='failed',error='WebFetch timeout; curl HTTP/2 INTERNAL_ERROR exit92; Q1/Q4主站curl亦同',fallback='curl --http1.1 origin-edge成功'),dict(url=D+'2026/q1/q1-2026-analyst-presentation.pdf',method='WebFetch PDF',status='failed',error='返回压缩二进制，未能提取正文',fallback='本地系统PDFKit成功'),dict(method='pdfinfo/pdftotext/Read PDF',status='failed',error='poppler工具不存在(exit127)；Python -I环境无pypdf/fitz/pdfplumber',fallback='系统PDFKit提取+关键页栅格核对；未安装包')]
write('sources.json',dict(as_of=ASOF,cutoff_verification='S1实际读取确认Q3待发布；最新季度S4/S5，最新采用的运营公告S6。非全公司全文件穷尽审计。',sources=S,failed_attempts=failures,not_used=[dict(url='https://www.se.com/ww/en/about-us/investor-relations/financial-results/',reason='选样预查；最终收窄Eaton，未将搜索摘要或Schneider数字作为事实证据'),dict(local_file='raw/eaton-q1/complete.pdf',reason='与S3相同季度辅助下载，正文数字均用S3或S4；不增加独立来源数')],independence='六份官方文档/页面，发布方均为Eaton；是公司披露案例，非六个独立验证者。IEA未采用，避免旧用电预测冒充最新。'))
calcs=[]
def calc(i,formula,inputs,result,unit,meaning):calcs.append(dict(id=i,formula=formula,inputs=inputs,result=result,unit=unit,interpretation=meaning))
calc('K1','27448 * 0.21',{'sales_musd':27448,'reported_share':.21,'source_ids':['S2','S5']},27448*.21,'USD million','披露百分比取整，结果应展示约5.8十亿美元；非AI敞口')
for period,r,r0,p,p0 in [('2026Q1',3600,3010,922,904),('2026Q2',3951,3350,1088,987)]:
 calc('K_'+period,'delta_profit / delta_revenue',dict(revenue=r,prior_revenue=r0,profit=p,prior_profit=p0,unit='USD million',source_ids=['S3'] if period=='2026Q1' else ['S4','S5']),dict(delta_revenue=r-r0,delta_profit=p-p0,incremental_margin_pct=(p-p0)/(r-r0)*100,revenue_growth_pct=(r/r0-1)*100,profit_growth_pct=(p/p0-1)*100,margin_pct=p/r*100,prior_margin_pct=p0/r0*100),'percent / USD million','全分部同比桥，非AI项目边际利润率。Q1销售增长20%含有机14、并购5、汇率1个百分点；Q2增长18%全有机，未经范围调整；未剔价格/产品组合，不能独立证明交付效率改善')
calc('K4','(1088/3951 - 922/3600)*10000',{'source_ids':['S3','S5']},(1088/3951-922/3600)*10000,'basis points','Q2环比，原表金额取整可能造成尾差')
calc('K5','(1088/3951 - 987/3350)*10000',{'source_ids':['S5']},(1088/3951-987/3350)*10000,'basis points','Q2同比')
calc('K6','15.2 / 3.951',{'backlog_busd':15.2,'quarterly_sales_busd':3.951,'source_ids':['S5']},15.2/3.951,'times quarterly sales','存量/单季流量；不是交付年限，不是backlog转化率')
calc('K7','15.2 / 13.2 - 1',{'source_ids':['S3','S5']},(15.2/13.2-1)*100,'percent','2025Q4至2026Q2期末积压增长')
calc('K8','OCF-capex=FCF',{'source_ids':['S2','S4']},[dict(period=t,ocf=o,capex=k,fcf=o-k) for t,o,k in [('2025Q4',1965,392),('2025Q2',918,202),('2026Q2',1127,253)]],'USD million','公司定义FCF；未扣并购价款；非主题/分部自由现金')
calc('K9','821 / 982 - 1',{'source_ids':['S4']},(821/982-1)*100,'percent','Q2公司GAAP净利同比；非分部利润')
write('calculations.json',dict(as_of=ASOF,status='observed_calculations_complete_theme_profit_not_identifiable',calculations=calcs,sensitivity=dict(status='symbolic_only_no_subjective_scenarios',variables={'B':'同口径AI设备已签订单金额（未知）','d':'取消/削减比例（未知）','c':'本期可交付并满足收入确认的比例（未知）','m':'这些交付的增量贡献率，未扣F（未知）','F':'增量启动/固定成本及折旧（未知）','delta_NWC':'主题新增营运资本占用（未知）','K':'主题增量资本开支（未知）'},formulas=['ΔR = B × (1-d) × c （同口径、同批订单；不将全部积压视为本期）','ΔOP = ΔR × m - F','盈亏阈值：B × (1-d) × c × m > F','当m>0且B(1-d)>0时：c > F / [B(1-d)m]','每提高1个百分点交付率：ΔOP变化 = 0.01 × B × (1-d) × m，须固定其他输入','ΔFCF ≈ ΔOP - 现金税 + 非现金折旧摊销 - ΔNWC - K，仍需利息及公司分摊桥'],not_permitted='不得把分部25.6%/27.5%平均利润率直接当AI新增贡献率；不得以约5.8B总敞口乘AI增长率得主题利润。')))
rows=[['2025Q4',3506,1046,'29.8%', '16%',13.2],['2026Q1',3600,922,'25.6%','42%',14.5],['2026Q2',3951,1088,'27.5%','41%',15.2]]
tables=[dict(title='同分部经营对照：Electrical Americas（未作恒定范围调整）',columns=['期间','收入（百万美元）','分部经营利润（百万美元）','经营利润率','滚动12个月有机订单同比','期末backlog（十亿美元）'],rows=rows),dict(title='数据中心专项披露：只能各自同比',columns=['期间','覆盖范围','当季订单同比','当季收入同比','限制'],rows=[['2026Q1','Electrical Americas','约240%','约50%','非AI单独；未披露绝对额'],['2026Q2','Electrical Sector','约85%','约65%','覆盖扩大；非同口径趋势；未注明有机']]),dict(title='现金兑现：全公司，不能归因AI',columns=['期间','OCF（百万美元）','capex（百万美元）','FCF（百万美元）','FCF定义'],rows=[['2025Q4',1965,392,1573,'OCF−PP&E capex'],['2025Q2',918,202,716,'OCF−PP&E capex'],['2026Q2',1127,253,874,'OCF−PP&E capex']])]
answer='当前更值得验证的是Eaton Electrical Americas的数据中心配电与预集成供电设备：公司披露订单与收入增长，分部利润率出现恢复，与交付爬坡改善相容；尚未识别同批订单向收入的转换，价格、组合及并购基数也可解释部分变化。核心问题已从“AI会不会用更多电”推进到“新增产能能否把backlog按可接受成本转成收入、经营利润和现金”。本案例支持该环节优先研究，不足以判定全行业最优或计算纯AI增量利润。'
findings=[
 dict(title='研究边界与可证伪命题',text='地区以美洲电气分部为主，期间取2025Q4、2026Q1、2026Q2；季度同比用于经营比较，环比用于观察恢复，不能混同；同名分部不等于已剔除并购/汇率的恒定范围。命题：截至下一次及随后季度披露，强数据中心采购应体现为美洲交付增长，并伴随经营利润率及增量利润率恢复；若只有积压堆高而利润/现金不兑现，主题到盈利的链条仍未成立。实际证据截点为2026-10-31 17:25:57 UTC。官网显示Q3要到11月3日公布；最新实现季度为7月31日发布的Q2，9月2日扩产公告提供更晚的运营证据。',claim_ids=['C1','C16','C21']),
 dict(title='从用电到设备收入：中间有四道门',text='分析路径：AI计算负荷/机架功率需求 → 可实施项目与供电接入/建设安排 → 按冗余、配电与热管理规格采购 → 订单与backlog → 产能、部件、人员与工程协同交付/验收 → 合同要求下确认收入 → 扣交付成本后的利润 → 应收回款减营运资本和capex后的现金。产品关联由grid-to-chip、Fibrebond和液冷披露支持；负荷到下单的转化率、并网时滞、收入确认条款及取消率是待验证推断。用电TWh是运行流量，设备更多跟新增/改造装机容量及架构有关；利用率变化未必触发等比例设备采购。电网瓶颈可能让设备提前下单，也可能推迟验收与回款，不能只画一条同步向上的箭头。',claim_ids=['C13','C17','C19']),
 dict(title='为什么优先看配电交付和集成能力',text='Eaton已将数据中心订单增长连接到可观察的Electrical Americas分部，Fibrebond也明确计入该分部。模块化围护结构将电力设备预集成，价值可能来自更快交付、工程整合和可靠性；这些仍需项目价格、交期与贡献率证实。它比抽象用电预测更接近采购与利润验证点；本研究未取得变压器、开关设备、UPS等产品单项利润和产能数据，不能进一步排名某个单品最赚钱。',claim_ids=['C5','C13','C16','C19']),
 dict(title='量级已重要，AI敞口仍不可辨识',text='2025 Data Centers & Distributed IT占Eaton销售21%，乘全年27448百万美元约为5764百万美元，展示为约58亿美元。它是广义终端市场历史收入量级，包括非AI数据中心和分布式IT，并非AI纯度、TAM或市场份额。美洲期末backlog从132亿升至145亿、152亿美元，半年约增15.15%；152亿相当于Q2分部单季销售的3.85倍，只说明存量重要，不能据此宣称能锁定3.85个季度收入。订单是期间流入，backlog是存量，取消、交付和统计范围变更均可能影响二者。',claim_ids=['C7','C8','C12']),
 dict(title='利润断点最有信息价值',text='2026Q1美洲销售同比增加590百万美元，分部利润只增加18百万美元，增量比率3.05%；Q2销售增601、利润增101，增量比率升至16.81%。Q2平均利润率较Q1恢复约193基点，但较上年同期仍低约193基点（公司取整+190/-200基点）。Q1销售增20%含有机14、并购5、汇率1个百分点，Q2增18%全有机；3.05%和16.81%的比率未经范围调整。分部利润率恢复与交付爬坡改善相容，但没有识别同批订单转换，价格、组合及并购基数也可解释部分变化，不能独立证明效率提升或稀缺溢价扩大：增量利润率仍低于平均利润率，价格、产品组合、扩产启动和效率没有分拆桥。公司将下半年>30%列作展望，需在Q3和Q4实际数据齐备后，按(Q3经营利润+Q4经营利润)/(Q3销售+Q4销售)>30%检验；单季结果不能判断整个下半年展望兑现。',claim_ids=['C3','C4','C11','C20']),
 dict(title='现金与全公司利润再加一道校验',text='Q2全公司OCF1127、capex253、FCF874百万美元，上年同期分别918、202、716，现金随经营改善，但没有主题/分部现金表。Q4与Q2存在季节差异，不能拿Q4高现金推导Q2恶化。Q2全公司GAAP净利从982降至821百万美元，调整后盈利却从1155增至1228；并购、利息、摊销等使分部利润不能直接替代股东盈利。分部信息将Fibrebond员工交易/留任费用等并购相关支出列在Corporate Other expense，摊销与重组也列Corporate；分部利润因此不是包含这些费用的全经济成本后利润。不能把全部Corporate费用归给AI。该FCF定义未扣收购价款，也不是AI投资净回报。',claim_ids=['C9','C10']),
 dict(title='量化应停在输入边界',text='主题利润只给敏感性条件：同一批AI订单B，取消/削减比例d，本期收入确认交付率c，新增贡献率m、增量固定/启动成本及折旧F，则ΔR=B(1−d)c，ΔOP=ΔR×m−F；盈利要求B(1−d)cm>F。现金还需扣现金税、营运资本和资本开支并加回非现金项。缺B、d、c、m、F及现金桥，点估计不成立。分部平均利润率不能代替m；21%广义历史敞口不能代替纯AI基数。calculations.json保留公式和可重算已实现同比桥。',claim_ids=['C11','C19'])]
alternatives=[dict(title='强订单可能是长交期锁产能，而非当期利润保证',text='这是待检验替代解释：订单和积压可以先于项目通电，客户为交期提前采购甚至多源预订；本次未取得取消/重复预订数据，不能认定已发生。若后续交付迟缓、延期上升而backlog不降，应降低收入与现金兑现速度判断。',claim_ids=['C12','C17','C19']),dict(title='扩产兑现会消除部分稀缺，竞争也可能压价',text='9月2日超过242百万美元的新厂投资计划拟使Fibrebond美国产能翻倍，原Minden产能此前三年已翻倍；属于实质供给反证，但公告不披露新厂投产日期。产能兑现可提收入，也可能增加启动成本或在需求放缓时压低利用率。官网还明确提示价格竞争与替代技术风险。没有竞品订单、价格和成本证据，不能宣称永久稀缺或Eaton份额必升；模块化、液冷和供电架构变化可改变价值在不同产品间的归属，未必降低整体支出。',claim_ids=['C14','C18','C22','C23']),dict(title='行业主题与并购/其他终端市场增长混在一起',text='Q2 Electrical Global的44%销售增幅有25个百分点来自Boyd Thermal并购贡献，有机18%、汇率1%；不能全部归于AI。Q1/Q2数据中心专项披露又跨Americas/Sector口径，不能连成一条增长曲线。若未来仍只提供混合口径和分部总利润，应维持“重要敞口、无法归因纯AI利润”的判断。',claim_ids=['C6','C15','C19'])]
watch=[dict(signal='11月3日Q3及随后季度：同口径数据中心订单、销售与取消/延期说明',meaning='确认Electrical Americas与Sector拆分、有机与并购拆分；否则不解释专项增速的季度变化。',claim_ids=['C1','C5','C6']),dict(signal='美洲分部交付/收入、backlog金额和book-to-bill',meaning='收入提高且积压有序兑现支持交付爬坡；仅积压增高仍可能是供给或项目阻滞。滚动比率不作季度转化率。',claim_ids=['C4','C12','C17']),dict(signal='美洲经营利润率、同比Δ利润/Δ收入与扩产成本桥',meaning='以未经范围调整的Q1 3.05%、Q2 16.81%为已实现参照。下半年>30%须待Q3/Q4数据齐备后按(Q3经营利润+Q4经营利润)/(Q3销售+Q4销售)核对，不能用单季替代半年；本次仅核实Q3发布日期，不推测Q4发布日期。收入增而利润率长期停滞将削弱价值捕获判断。',claim_ids=['C11','C20','C21']),dict(signal='全公司OCF、capex、FCF及营运资本解释；争取分部/主题现金数据',meaning='现金与利润共同改善才增强兑现证据；公司现金改善不能单独证明AI回款。',claim_ids=['C9','C19','C21']),dict(signal='Fibrebond新厂开工、投产、利用率和新增订单覆盖；竞品交期与报价',meaning='区分计划与实际产能；若供给释放伴随降价/利用率下滑，应下调稀缺利润假设。现有公告没有投产时间。',claim_ids=['C14','C18','C22'])]
gaps=['纯AI的订单/收入绝对额、产品和地区拆分缺失；广义21%敞口不能代替。','未取得订单取消、延期、客户集中度、项目验收与收入确认合同条款；不能估算backlog兑现日期。','没有价格/量/组合/扩产成本利润桥，也无主题营运资本和现金分拆；主题增量利润与FCF不作点估计。','六个来源均为同一公司，缺竞品官方期间数据和客户侧项目核对；不作行业赢家排序。','Eaton Q3尚未发布；官方入口核实最新已实现季度，不等于穷尽全部监管/投资者会议文件。','WebFetch地区网页和主站多次失败、PDF工具缺失；origin-edge与本地PDFKit补齐核心证据，失败详情保留。','父任务独立审查提出四项定向修正，本轮已落实并记录independent-review.md；HTML与浏览器呈现验收仍由父任务统一完成。']
report=dict(title='AI用电到电力设备利润：Eaton的订单已来，交付兑现更值得验证',question='AI数据中心用电增长如何转成电力设备供应商收入与利润，哪个环节最值得验证？',as_of=ASOF,status='partial',answer=answer,findings=findings,tables=tables,alternatives=alternatives,watch=watch,gaps=gaps,sources=[{k:s[k] for k in ['id','title','url','published_at']} for s in S],method='theme / v2；官方六文档；研究建议',current_judgment='订单与收入增长披露、分部利润率恢复，与交付爬坡改善相容；同批订单转换及纯AI增量利润/现金归因未识别',mechanism_edges=[dict(from_stage=a,to_stage=b,status=t,claim_ids=ids) for a,b,t,ids in [('AI负荷/设备功率','项目获电与采购','待检验，缺项目匹配',['C17','C19']),('数据中心采购','专项订单与收入','披露支持，口径有断点',['C5']),('美洲订单/backlog','美洲收入与分部利润','共同变化与交付爬坡改善相容；非同批订单转换或项目因果识别',['C3','C4','C11']),('分部利润','主题现金','未识别',['C9','C19'])]])
report['tables'][0]['note']='Q1美洲销售增20%含有机14/并购5/汇率1个百分点；Q2增18%全有机，增量利润比率未经恒定范围调整。分部利润未包含列Corporate的并购相关费用（含Fibrebond员工交易/留任）、摊销和重组，不是全经济成本后利润；不能把Corporate全部归AI。'
write('report.json',report)
# Markdown is generated only from frozen report fields; parent will use the same JSON for HTML.
parts=['# '+report['title'],'','问题：'+report['question'],'','截点：'+ASOF+'｜状态：部分完成（主题盈利归因缺输入；核心案例已交付）','',answer]
for f in findings:
 parts+=['','## '+f['title'],'',f['text']+' '+' '.join('['+x+']' for x in f['claim_ids'])]
for t in tables:
 parts+=['','## '+t['title'],'','| '+' | '.join(t['columns'])+' |','| '+' | '.join(['---']*len(t['columns']))+' |']
 parts+=['| '+' | '.join(str(v) for v in r)+' |' for r in t['rows']]
parts+=['','表格来源：[C2–C5、C9–C11]；季度流量与期末存量分开；利润率按披露取整。Q1美洲销售增20%含有机14/并购5/汇率1个百分点，Q2增18%全有机，增量利润比率未经范围调整。分部利润未包含列Corporate的并购相关费用（含Fibrebond员工交易/留任）、摊销和重组，不是全经济成本后利润；不将Corporate全部归AI。']
for f in alternatives:
 parts+=['','## 反方：'+f['title'],'',f['text']+' '+' '.join('['+x+']' for x in f['claim_ids'])]
parts+=['','## 下一观察','']
parts += ['- **'+w['signal']+'**：'+w['meaning']+' '+' '.join('['+x+']' for x in w['claim_ids']) for w in watch]
parts+=['','## 证据缺口','']+['- '+g for g in gaps]
parts+=['','## 官方来源','']+['- ['+s['id']+' · '+s['title']+']('+s['url']+')，发布：'+s['published_at'] for s in S]
parts+=['','原句、文件定位、下载哈希与失败取证见 sources.json；主张映射见 claims.json；计算见 calculations.json。本报告提供研究判断，不提供买卖建议。','']
(P/'report.md').write_text('\n'.join(parts),encoding='utf-8')
write('datasets.json',dict(as_of=ASOF,datasets=[dict(id='ea_trend',title='Electrical Americas已实现数据（同分部，未作恒定范围调整）',period_type='quarter / quarter end',rows=[dict(period=r[0],sales_musd=r[1],segment_profit_musd=r[2],margin_pct=float(r[3][:-1]),rolling_12m_organic_orders_yoy_pct=float(r[4][:-1]),backlog_busd=r[5],source_ids=ss) for r,ss in zip(rows,[['S2','S3'],['S3'],['S4','S5']])],render_note='各指标分图，金额单位明确；不使用双轴；不把分部增量当AI利润；Q1销售增20%含有机14/并购5/汇率1个百分点，Q2增18%全有机，未经恒定范围调整'),dict(id='company_cash',title='Eaton现金季度对照',rows=[dict(period=t,ocf_musd=o,capex_musd=k,fcf_musd=o-k,source_id=s) for t,o,k,s in [('2025Q4',1965,392,'S2'),('2025Q2',918,202,'S4'),('2026Q2',1127,253,'S4')]],render_note='Q2同比单独比较，Q4只是季节性参照，不连成平滑增长线')],excluded_from_trend=['Q1 Americas vs Q2 Electrical Sector数据中心增速，覆盖不同','Q2材料中2H26 >30%为展望，不画为已实现']))
write('plan.json',dict(question=report['question'],type='theme',method_reference='../protocol.md; ../../plans/touyan-end-to-end-plan-v2-20261031.md#theme',as_of=ASOF,status='completed_with_gaps',scope='只写本theme目录；只读官方来源，不委派、不发布、不修改插件、不登记正式账本/作者库',hypothesis='数据中心采购形成显著订单；主题兑现应在交付爬坡后表现为利润与现金，而非只看积压',comparison='2025Q4/2026Q1/2026Q2美洲分部；Q2同比利润/现金；专项数据中心披露不跨口径连线',queries=['site.eaton.com 2026 third quarter earnings October 2026 data center orders Electrical Americas','site.se.com 2026 third quarter revenues October 2026 data center','site.eaton.com 2026 capacity data center billion'],steps=[dict(task=t,status='done') for t in ['读取协议、v2和证据格式','核实最新官方季度与时间','取得两至三期经营/现金和专项敞口','对照利润与现金、竞争扩产及敏感性边界','生成冻结JSON/Markdown和趋势数据']],stop_rule='核心可靠材料足够即成品；不为缺失利润输入持续扩搜；保留partial',source_budget='6份采用官方文档/页面，均Eaton；无社区',implementation_notes='Swift PDFKit为本地提取工具；下载数据独立raw子目录；Python全部-I；不运行下载代码；HTML父任务统一消费report.json'))
print('Wrote report.md/report.json/claims.json/sources.json/plan.json/calculations.json/datasets.json')
