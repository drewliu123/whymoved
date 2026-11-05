from pathlib import Path
from datetime import datetime,timezone
import json, math
W=Path(__file__).parent
P=Path('/Users/frankzhang/Desktop/投研助手/journal/runs/R20261102T035050Z-ffc04249819e')
def load(p):return json.loads(p.read_text())
def save(n,x):(W/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
stamp=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
p,r,c,s=[load(P/(n+'.json')) for n in ['plan','report','claims','sources']]
for x in [p,r,c,s]:x['as_of']=stamp
p.update(parent_run_id=P.name,task='检验停火期限的前端风险定价与潜在信号',prior_judgment=r['answer']['text'],decision_needed='34.5%的月底未打击价格是否便宜，选后哪一段期限最值得检验？',budget={'max_queries':8,'max_followups':1})
p['comparison']={'period':'旧快照2026-11-02T03:44Z，月底合约复核05:06:48Z；报道截至11月1日','unit':'同规则YES价格、分段条件风险；研究判断不登记数值概率','scope':'美国发起并落地伊朗陆地或内水的合格空袭/导弹打击；并非全面和平'}
d=p['research_design'];d['baseline']='上一轮已取得期限价格，但未判断定价矛盾；本轮检验风险是否集中在选后最初数日及其行动依据。';d['rationale']+=' 本轮把长期核问题与短期是否启动打击分开；检验选举约束消失是否足以解释即时军事行动。先前社区线索在本轮两小时内仍沿用，不重复广泛检索。'
t4={'id':'T4','observe':'美方是否已有执行决定，还是保留谈判与非空袭施压选择','source':'最新Reuters具名官员表态与谈判报道','by':'11月3日至8日','outcomes':[{'hypothesis_id':'H1','prediction':'未决定新增打击并保留谈判，选后可能明确延长克制窗口'},{'hypothesis_id':'H2','prediction':'出现执行决定或明确最后通牒，选后迅速落实打击'},{'hypothesis_id':'H3','prediction':'双方公布并实施互惠步骤及核查条款'}]}
t5={'id':'T5','observe':'新增军事准备及触发事件是否被核实','source':'CENTCOM/DoD原始行动披露及独立现场报道','by':'11月3日至8日','outcomes':[{'hypothesis_id':'H1','prediction':'新施压主要仍是封锁与制裁，克制承诺续接'},{'hypothesis_id':'H2','prediction':'出现具体打击准备、已执行授权或美方伤亡等新触发事件'}]}
d['discrimination_tests'] += [t4,t5]
p['queries']=[{'question':'期限风险是否只是累计而非前端集中？','query':'沿用已冻结Gamma全规则和7期CLOB，并复核Nov30 book','source':'Polymarket公开API','purpose':'核对共同规则、不同创建日期、计算同一截面条件价格比；保留非联合分布限制','test_ids':['T3']},{'question':'当前谈判和选前承诺有什么实际改变？','query':'US Iran November 1 2 2026 Doha talks Trump deal Reuters','source':'Reuters/AOL/ThePrint/Investing','purpose':'继续核对双边条款与执行；未取得完整行动记录仍missing','test_ids':['T1','T2','T4']},{'question':'军事准备和立即重启打击有何事实？','query':'Axios October 7 29 2026 Cooper CENTCOM Iran blockade post-midterms','source':'Axios/CENTCOM及Reuters历史报道','purpose':'区分兵力存在、政治意愿和实际执行准备；与长期库存压力区分','test_ids':['T5']}]
p['resolution_contract']['definition']='用户问题仍为停火持续时间；价格比较严格限定美方合格打击；本轮重点选后数日与11月底。'
# Preserve inherited claims with their original timestamps; append new observations.
def src(sid,url,quote,locator,publisher,tier,supports,origin,published='unknown',mq=None):
 x=dict(id=sid,url=url,canonical_url=url,publisher=publisher,tier=tier,published_at=published,retrieved_at=stamp,quote=quote,locator=locator,origin_id=origin,origin_basis='原始API或同一Reuters报道的明确归属；转载不算独立来源',supports=supports,evidence_kind='market_quote' if mq else 'document',access_status='ok',selection=dict(selected=True,relevance='direct',priority='decisive',purpose='检验前端风险及即时打击决定',reason='增加可核查报价或竞争解释所需的具体表态'))
 if mq:x['market_quote']=mq
 s['candidates'].append(x)
def add(cid,text,typ,refs=(),basis=(),**kw):
 x=dict(id=cid,text=text,type=typ,as_of=stamp,sources=[{'source_id':v} for v in refs],**kw)
 if basis:x['basis']=list(basis)
 c['claims'].append(x)
token='1759128163540908136861900527987306673081148337830189221001436012323578054934'
qt='2026-11-02T05:06:48.510000+00:00'
mq=dict(quoted_at=qt,instrument='Polymarket market 4713483',outcome='Yes',direction='long',value=.345,unit='USD/share',quote_type='indicative',bid=.34,ask=.35,token_id=token,bid_top_shares=1083.93,ask_top_shares=514.65)
src('S38','https://clob.polymarket.com/book?token_id='+token,json.dumps({'timestamp':1793596008510,'asset_id':token,'highest_bid':.34,'bid_size':1083.93,'lowest_ask':.35,'ask_size':514.65}),'WebFetch公开JSON提取；本轮未下载完整订单簿，不补造原始book','Polymarket','T0',['price'],'polymarket-market-4713483',mq=mq)
src('S39','https://theprint.in/world/iran-qatari-mediators-hold-third-day-of-talks-to-end-us-iran-war/3087694/','Trump has not decided whether to launch new strikes against Iran, but would prefer to resolve the conflict diplomatically.','Reuters 11月1日转刊中归属Rubio在10月31日的表态；WebFetch再次定向提取；与AOL同一报道族','Reuters / ThePrint','T2',['fact','view'],'reuters-nov1','2026-11-01')
src('S40','https://www.investing.com/news/commodities-news/iran-sees-only-unacceptable-ideas-in-latest-mediation-to-end-war-official-says-4979005','unacceptable ideas and not an offer','Reuters 10月28日，Andrew Mills与Parisa Hafezi；匿名伊方谈判人士评价Qatar建议。正文核问题/港口封锁和石油销售限制先后次序段','Reuters / Investing.com','T2',['view'],'reuters-oct28','2026-10-28')
src('S41','https://wdsm710.com/2026/09/02/trump-aides-fearing-a-midterm-rout-push-to-keep-iran-war-quiet-for-now/','will consider; far from a given','Reuters 9月2日历史报道正文第2段；短引分隔表示两处摘录；仅用于条件性与历史激励，未采用库存数字','Reuters / WDSM','T2',['view'],'reuters-sep2','2026-09-02')
add('C25','2026-11-02 05:06:48.510 UTC，11月底YES买卖价仍为34/35美分，中点34.5%；顶档买/卖1083.93/514.65份。与03:44截面的中点相同，仅复核该一期，不构成期限曲线的同步刷新。','price',['S38'],price_kind='indicative')
add('C26','11月1日Reuters报道记载Rubio在10月31日称，特朗普尚未决定是否发动新打击，并倾向外交解决。这核实的是报道中的具名表态，并不证明私下未有决定。','fact',['S39'])
add('C27','10月28日Reuters引述匿名伊方人士称Qatar建议不可接受；报道描述美方要求尽早谈核问题，伊方要求先解除港口封锁和石油销售限制。分歧属于谈判顺序，未报告已完成互惠执行。','view',['S40'])
add('C28','9月2日Reuters曾将选后扩大行动描述为will consider并称far from a given；该历史报道表明选举约束与军事决策曾被区别讨论，不能作为11月部署或命令证据。','view',['S41'])
add('C29','以03:44截面的同规则伊朗时间系列作条件价格比：1-0.725/0.935=22.46%（11月4日至8日4天），1-0.515/0.725=28.97%（8日至15日7天），1-0.405/0.515=21.36%（15日至22日7天），1-0.345/0.405=14.81%（22日至30日8天），1-0.255/0.345=26.09%（11月底至12月底31天）。按1-(后一期/前一期)^(1/天数)换算日均风险依次约6.16%、4.77%、3.37%、1.98%、0.97%。这是把价格当嵌套生存概率时的解释性计算，不是市场提供的联合概率或独立真实概率。合约创建日不同，沿用其当前开放未裁决状态，假设不存在不同的历史触发争议；订单簿异步7秒。','inference',basis=['C13','C16','C17','C18','C19','C20','C21'])
add('C30','曲线的前端风险集中超出单纯期限变长：若11月4日至30日26天采用恒定日均风险、且保留两端价格0.935/0.345，则11月8日价格约0.802，而实际中点0.725。差约7.7美分是恒定风险基准的形状差，不是公允价值或套利幅度。11月4日至8日条件风险用买卖价组合约21.5%-23.4%，不是执行套利价。','inference',basis=['C29','C16','C17','C20'])
add('C31','暂定方向偏向选后最初数日继续谈判与拖延，优先检验11月8日的高前端风险，而非直接把月底35美分判为明显便宜。理由是具名美方表态仍保留外交和未决打击决定，而价格把初期日均风险定得更高；该表态早于本轮、可能已反映在价格中，因此这里只形成偏向，不构成已证明的交易优势。月底累计打击概率约65.5%只需一次合格有限打击兑现，谈判分歧使这一风险仍有依据。未取得新增部署和授权证据是本轮缺口，不是支持拖延的负面证据。','inference',basis=['C26','C27','C29','C30','C13','C25'])
add('C32','最有区分力的新消息是选后不打击承诺明确延长至11月8日之后、并获可核查执行；这会直接压缩前端风险。继续谈判、仍无最终核协议或继续海上封锁本身较难区分立即空袭与继续拖延。新最后通牒配合执行准备、核实美军伤亡及随后的美方报复决定会削弱拖延判断。即便前端风险下降，月底合约仍保留更长尾部风险，不能等幅外推。','inference',basis=['C13','C26','C27','C29','C31'])
add('C33','11月8日YES旧快照可买报价为73美分，因此若持有到期且不计其他成本，需要真实未打击概率高于73%才有正期望；月底对应门槛为35%。中点不能代替这个门槛，跨过日期带来的条件概率上升也不是免费收益，因为期间可能发生使YES归零的打击。','inference',basis=['C17','C25','C13'])
answer='我的暂定判断是：选后最初几天更可能延续边谈边施压，最值得检验的是11月8日这段风险是否被高估；月底35美分暂不构成明显错价。市场在押的不只是“越久越危险”，而是把风险集中在选后初期。若到11月4日仍无合格美方打击，价格比隐含随后四天打击风险约22.5%；相比之下11月22日至30日八天约14.8%。最新美方具名表态仍是未决定新打击、倾向外交，这让我偏向短端延续，但尚不足以证明价格便宜。'
r.update(title='美伊停火：更值得检验的是选后四天的风险定价',task=p['task'],answer={'text':answer,'claim_ids':['C26','C29','C31','C25']})
r['findings']=[{'title':'市场把最初几天定得比月底更危险','text':'同口径价格折算的日均打击风险，从11月4日至8日约6.2%，降到11月22日至30日约2.0%。若按整段恒定风险匹配11月4日和30日两端，11月8日应约80.2%，实际为72.5%。这7.7美分差额揭示应检验的前端风险集中，不能直接叫作低估或套利。','claim_ids':['C29','C30'],'why_it_matters':'把研究焦点从期限越长概率越低，收窄到选后初期为何特别危险。','increment':{'kind':'calculation','baseline':'上一轮只列期限概率，未区分累计风险与分段风险。','detail':'由同规则期限计算条件价格比与日均风险，并给出恒定风险形状基准。'}},{'title':'我偏向短期拖延，因为政治约束消失与执行决定之间仍有一步','text':'Reuters 11月1日报道的Rubio表态是尚未决定新打击、倾向外交；10月28日报道的核心分歧仍是核问题和解除封锁的先后。我的解释是，选举结束会移除一项克制激励，却不自动决定打击的收益、目标和时点。继续封锁、谈判与不发动合格空袭可以并存。这个解释使短端延续更值得关注，但公开表态可能已经入价，本轮没有证明它是市场漏看的信息。','claim_ids':['C26','C27','C31','C13'],'why_it_matters':'形成有依据的暂定方向，同时区分判断与可兑现优势。','increment':{'kind':'judgment_update','baseline':'上一轮未对报价形成独立方向。','detail':'偏向选后短期拖延，检验对象优先放在前端风险集中。'}},{'title':'月底35美分便宜与否，取决于一次有限打击','text':'11月底YES在05:06 UTC复核仍为34/35美分。YES只要发生一次规则内美方打击便会失败；无法达成核协议、互惠顺序僵持提供了反复施压或军事升级的理由。因而“全面战争代价高”不足以推导月底YES便宜，也不足以替它估出更高公允概率。更直接的证据应是选后克制承诺续接及实际执行。','claim_ids':['C25','C13','C27','C31','C32'],'why_it_matters':'避免把全面战争成本误用于一次打击合约。','increment':{'kind':'connection','baseline':'上一轮指出口径狭窄，但未解释其定价影响。','detail':'把一次有限打击的结算门槛接回月底是否便宜。'}}]
r['alternatives']=[{'title':'最强反方：谈判也是打击前的最后窗口','text':'伊方仍拒绝建议，双方顺序诉求未解决；因此即便美方公开保留外交，选后仍可能很快进行一次有限打击。最新准备与授权证据本轮未能补齐，不能据此判定不存在准备。若出现明确最后通牒及可验证执行准备，应撤回前端拖延倾向。','claim_ids':['C26','C27','C13','C31','C32']}]
r['watch']=[{'signal':'选后明确延长不打击承诺，尤其跨过11月8日','meaning':'这是比“仍在谈”更有价值的新信息：直接压缩前端打击窗口。须核对双方表态、执行及固定合约的可成交报价。','claim_ids':['C32','C33']},{'signal':'新最后通牒配合可验证准备，或核实美军伤亡后宣布报复','meaning':'前者把可选军事工具变成接近执行的决定，后者提供新增触发器；两者会削弱短期拖延倾向。仅有旧部署或空泛威胁不足以代替。','claim_ids':['C31','C32']},{'signal':'11月8日73美分、月底35美分的买入门槛','meaning':'这分别要求高于73%和35%的真实未打击概率才可能有正期望，尚未计成本。现在识别了优先核查的定价矛盾，未验证可直接交易的优势；时间流逝本身不创造免费收益。','claim_ids':['C33']}]
r['limitations']=[{'text':'完整期限曲线沿用03:44 UTC截面，05:06仅复核11月底。条件价格比假设当前开放合约无不同历史裁决争议，不等于联合概率；政治表态已公开，部署和授权的当前事实仍缺，方向判断不等于已发现交易优势。','material':True,'claim_ids':['C25','C29','C31']}]
r['tables']=[{'title':'风险集中在哪一段','columns':['条件区间（伊朗时间23:59）','天数','区间打击隐含风险','等效日均风险'],'rows':[['11月4日→8日',4,'22.5%','6.2%'],['11月8日→15日',7,'29.0%','4.8%'],['11月15日→22日',7,'21.4%','3.4%'],['11月22日→30日',8,'14.8%','2.0%'],['11月30日→12月31日',31,'26.1%','1.0%']],'claim_ids':['C29'],'note':'每段以到前一个截止日仍未发生合格打击为条件，使用03:44 UTC同截面中点的比例作解释性计算。不是相应区间的直接可交易合约，也不假定区间独立。未混入选举日美国东部时区合约。'}]
a=r['analysis'];a.update(baseline=d['baseline'],baseline_claim_ids=['C20','C22','C23'],conclusion=answer,conclusion_claim_ids=['C29','C31'],model_reason='固定价格比和日均风险算术，不使用财务模型；计算输入与公式列claims并另保存calculations.json。')
a['tests'][2]['interpretation']='规则和报价可形成嵌套期限的条件价格比，显示前端风险集中；不是选举因果或真实行动证据。各创建日不同且未完成逐案历史争议核对，比例只作解释性基准。'
a['tests'] += [dict(id='T4',outcomes=t4['outcomes'],status='observed',claim_ids=['C26','C27'],interpretation='具名未决表态与外交偏好符合H1的暂定解释，削弱把选后打击视为既定决定的读法；不消除H2的条件性有限打击，也未验证H3执行。',supports=['H1'],weakens=[],next_observation='选后是否续接具体克制期限或变成执行决定',by=t4['by'],supports_if='具体克制承诺跨过11月8日并获执行',weakens_if='最后通牒配合可验证执行准备'),dict(id='T5',outcomes=t5['outcomes'],status='missing',claim_ids=[],supports=[],weakens=[],gap_reason='Axios正文403；官方部署与授权原文未取得；历史报道不能作为当前新增准备。',interpretation='没有取得证据不代表没有准备，不能裁定任一解释。',next_observation=t5['observe'],by=t5['by'],supports_if='核实新增执行准备及目标指向支持H2',weakens_if='明确延长克制并执行削弱立即打击读法')]
a['market']=dict(status='assessed',reason='用已冻结完整期限报价计算条件价格比，另复核月底报价；规则相同，创建日期不同及历史争议假设明确。',claim_ids=['C13','C16','C17','C18','C19','C20','C21','C25','C29','C30','C31','C33'],model_ids=[],implied_expectation='若到11月4日仍未打击，随后4天风险约22.5%，等效日均6.2%，高于月底前最后8天约2.0%。',research_expectation='偏向选后最初数日继续拖延，暂不把月底35美分视为明显错价。',gap='前端风险集中与美方公开未决表态存在可检验张力；公开信息可能已入价，未建立已验证交易优势。',conditions='关注明确续接克制期限与执行准备；执行价门槛而非中点；一旦有限合格打击YES即失败。')
r['update']=dict(judgment_changed=True,reason='由价格摘录推进到前端风险形状计算和短期拖延的暂定方向；没有登记独立公允概率。',comparability=dict(status='mixed',reason='同一合约范围及03:44旧曲线可比，新增05:06单期复核；研究新增计算和判断，不把异步截面拼成同步新曲线。'))
s['source_status']['current_orderbook_refresh']={'status':'partial','reason':'urllib两组Gamma均403；WebFetch成功取得11月底时间戳与顶档；七期期限刷新失败，其余沿用旧截面。'}
s['source_status']['military_preparation']={'status':'partial','reason':'候选和失败原样留military-evidence.json；当前部署/授权仍missing，不以此支持H1。'}
save('plan.json',p);save('report.json',r);save('claims.json',c);save('sources.json',s);save('sources-before-selection.json',s)
vals=[.935,.725,.515,.405,.345,.255];days=[4,7,7,8,31]
save('calculations.json',{'type':'fixed_arithmetic','inputs':{'prices':vals,'interval_days':days,'claims':['C16','C17','C18','C19','C20','C21']},'formula_interval':'1 - later_price / earlier_price','formula_daily':'1 - (later_price / earlier_price) ** (1 / days)','outputs':[{'interval_risk':1-b/a,'daily_risk':1-(b/a)**(1/n)} for a,b,n in zip(vals,vals[1:],days)],'constant_risk_Nov8':.935*(.345/.935)**(4/26),'not_fair_value':True})
save('audit.json',{'as_of':stamp,'parent_run':P.name,'queries':p['queries'],'execution':[],'review':{'status':'pending'},'plan_timing':'竞争解释及军事T4/T5初始口径在取证委托中已有；本地结构化plan在本轮首批取证后补记，不宣称事前冻结。','community_reuse':'沿用上一轮两小时前的候选，未重跑引擎；本轮没有把社区叙事入账成外部事实。','failed':['Axios 10月28日HTTP403','urllib Gamma两组HTTP403','military-evidence.json记录的代理失败'],'price_refresh':'05:06只复核月底；未刷新七期；不伪造新完整原始订单簿。','conditional_ratio':'已检查系列规则全文一致；创建日不同，未逐案排除历史裁决争议，比例解释依赖当前无争议嵌套假设；非联合风险中性分布。','reference_class':'沿用2026年同一冲突机制；9月报道只用于区分选择与决定，不外推库存或胜率。','new_evidence_paths':['military-evidence.json','calculations.json'],'freshness':'当前来源获取晚于05:04，最终as_of随冻结前移，不作为05:04前已取得证据。'})
print('Frozen',stamp,'claims',len(c['claims']),'sources',len(s['candidates']))
