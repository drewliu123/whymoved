from pathlib import Path
from datetime import datetime,timezone
import json
W=Path(__file__).parent;P=Path('/Users/frankzhang/Desktop/投研助手/journal/runs/R20261102T033859Z-9c774311b155')
def load(p):return json.loads(p.read_text())
def save(n,d):(W/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
stamp=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
p=load(P/'plan.json');r=load(P/'report.json');c=load(P/'claims.json');s=load(P/'sources.json')
p['parent_run_id']=P.name;p['task']='停火持续期限的预测市场补充与判断更新';p['prior_judgment']='上一轮未检查预测市场，仅判断无法可靠给出期限；用户指出遗漏，现补同口径期限合约与盘口。';p['decision_needed']='理解市场为不同停火持续期限定价多少，并判断该合约概率能说明什么。';p['budget']={'max_queries':8,'max_followups':1};p['comparison']={'period':'2026年11月1日当前截面，截止11月3日至12月31日的未来期限','unit':'YES买卖报价、买卖中点与合约规则','scope':'Polymarket美国对伊朗合格空袭或地对地导弹打击；并非所有双边敌对行动'}
d=p['research_design'];d['price_relevance']=True;d['rationale']+=' 本次纠正将非资产问题误作无价格相关的取舍；事件合约可提供持续期限基准。保留历史风险机制，新增明确合约定义和当前订单簿，不能将市场价格当独立研究预测。';d['baseline']='上一轮仅凭新闻无法排序停火持续时间；本轮以同口径预测市场期限概率作比较基准。'
t={'id':'T3','observe':'同一合格美方打击定义下，不同截止日期的YES盘口与期限结构','source':'Polymarket Gamma合约规则与CLOB订单簿','by':'当前截面及下一次关键外交军事消息后','outcomes':[{'hypothesis_id':'H1','prediction':'较近数周期限的未打击价格保持较高，但不必支持长期全面和平'},{'hypothesis_id':'H2','prediction':'投票前未打击价格高，之后更长期限未打击价格明显降低'},{'hypothesis_id':'H3','prediction':'更长期限未打击价格也较高，但仍须实际互惠核查事实支持'}]};d['discrimination_tests'].append(t)
p['queries']=[{'question':'哪些合约直接对应停火持续期限？','query':'site.polymarket.com Iran US ceasefire November 2026 strikes by November','source':'WebSearch及Gamma事件API','purpose':'核对事件身份、选项与裁决条件','test_ids':['T3']},{'question':'Kalshi是否有同义合约可作比较？','query':'site.kalshi.com Iran ceasefire November 2026 US strike','source':'WebSearch','purpose':'寻找独立市场；核协议与停火持续不可混同','test_ids':['T3']},{'question':'当前每一期限的实际买卖盘和深度是多少？','query':'Gamma events slug + CLOB book token_id + fee-rate','source':'Polymarket官方公开API','purpose':'补报价时刻、YES映射、买卖价、顶档数量及费率','test_ids':['T3']}]
for x in [p,r,c,s]:x['as_of']=stamp
r['task']=p['task']
for x in c['claims']:x['as_of']=stamp
markets={}
for f in W.glob('us-iran*.json'):
 for e in load(f):
  for m in e['markets']:markets[m['id']]=m
snap={x['id']:x for x in load(W/'market-snapshot.json')}
order=['5447182','6369331','5686980','5190747','5686978','4713483','4713484'];labels=['11月3日（选举日）','11月4日','11月8日','11月15日','11月22日','11月30日','12月31日']
def src(sid,url,quote,locator,kind,supports,origin,market_quote=None):
 x=dict(id=sid,url=url,canonical_url=url,publisher='Polymarket',tier='T0',published_at='unknown',retrieved_at=stamp,quote=quote,locator=locator,origin_id=origin,origin_basis='官方公开Gamma/CLOB API；各期限为同平台同事件系列，不算独立共识',supports=supports,evidence_kind=kind,access_status='ok',selection=dict(selected=True,relevance='direct',priority='decisive',purpose='核对裁决口径与期限报价',reason='原始规则或带token和时间的订单簿，直接补上上一轮缺失的市场基准'))
 if market_quote:x['market_quote']=market_quote
 s['candidates'].append(x)
def add(cid,text,typ,refs=(),basis=(),**extra):
 x=dict(id=cid,text=text,type=typ,as_of=stamp,sources=[{'source_id':v} for v in refs],**extra)
 if basis:x['basis']=list(basis)
 c['claims'].append(x)
rule=markets['5686980']['description'];midrule=markets['5447182']['description']
src('S29','https://gamma-api.polymarket.com/events?slug=us-iran-ceasefire-continues-throughptptpt',rule,'markets[id=5686980].description；所选系列各期限除日期外规则正文hash相同','document',['fact'],'polymarket-ceasefire-series')
src('S30','https://gamma-api.polymarket.com/events?slug=us-iran-ceasefire-continues-through-the-midterms',midrule,'markets[id=5447182].description；特定截止时间11月3日23:59美国东部','document',['fact'],'polymarket-midterms')
add('C13','系列合约YES表示在指定日期23:59伊朗标准时间前未发生美国发起并直接击中伊朗陆地领土及内水的合格空袭或地对地导弹打击。规则排除拦截未落地弹药、网络行动、海军炮击及其他列明行动，且不覆盖全部伊方或以色列行动。','fact',['S29'])
add('C14','选举日合约采用相同合格美方打击定义，但截止为11月3日23:59美国东部时间；不能把它与系列日期合约当作完全相同时间窗口。','fact',['S30'])
rows=[];price_ids=[]
for i,(mid,label) in enumerate(zip(order,labels)):
 v=snap[mid];m=markets[mid];sid='S'+str(31+i);cid='C'+str(15+i);price_ids.append(cid)
 q=dict(quoted_at=v['quoted_at'],instrument='Polymarket market '+mid,outcome='Yes',direction='long',value=v['mid'],unit='USD/share',quote_type='indicative',bid=v['best_bid'],ask=v['best_ask'],token_id=v['token_id'],bid_top_shares=v['bid_top_shares'],ask_top_shares=v['ask_top_shares'])
 excerpt=json.dumps({'question':v['question'],'token_id':v['token_id'],'timestamp':v['book_timestamp'],'best_bid':v['best_bid'],'best_ask':v['best_ask'],'mid':v['mid'],'bid_top_shares':v['bid_top_shares'],'ask_top_shares':v['ask_top_shares'],'gamma_volume24hr':v['volume24hr'],'gamma_updated_at':v['gamma_updated_at']},ensure_ascii=False)
 src(sid,'https://clob.polymarket.com/book?token_id='+v['token_id'],excerpt,'完整原始book-'+mid+'.json；YES token与book.asset_id已逐一验证；Gamma选项及成交量另保留事件JSON','market_quote',['price'],'polymarket-market-'+mid,q)
 add(cid,label+'期限YES买卖价为'+str(v['best_bid'])+'/'+str(v['best_ask'])+'美元，盘口中点'+f"{v['mid']*100:.2f}"+'%；顶档买/卖数量'+str(v['bid_top_shares'])+'/'+str(v['ask_top_shares'])+'份。报价时间'+v['quoted_at']+'。这是中点参考价，不是该中点可成交承诺。','price',[sid],price_kind='indicative')
 rows.append([label,f"{v['mid']*100:.1f}%",f"{v['best_bid']*100:.1f}¢ / {v['best_ask']*100:.1f}¢",'美国东部' if i==0 else '伊朗标准时间'])
add('C22','市场基准已可排序：按合约的美方合格打击定义，短期继续无此类打击是明显主流；11月15日YES为51.5%，月底为34.5%，更长期持续未打击的定价显著较低。这是同一截面的期限结构，不能称为概率较昨日下调，也不能据此证明选举导致复战风险。','inference',basis=['C13','C14']+price_ids)
add('C23','相对于上一轮没有市场基准，本轮应修正为：市场明显偏向选举前维持无合格美方打击，但对维持到月底不乐观；我尚无独立证据可证明市场定价偏高或偏低。双边全面和平、制裁解除与伊方行为仍不能由这些YES价格推出。','inference',basis=['C7','C12','C13','C14','C22'])
add('C24','各期订单簿顶档深度不一。11月底YES最优买卖档只有约401/298份，因此34.5%是有限深度下的中点，较大规模成交可能偏离；整个市场流动性字段不能当成该价位可成交资金量。','inference',basis=['C20'])
s['source_status']['prediction_market']={'status':'ok','reason':'取得两组Gamma原始规则、8个YES订单簿及0基础费率；正文选7期。书面规则与部分Gamma endDate时区不一致，以书面裁决为准。'}
s['source_status']['Kalshi_matching']={'status':'no_results','reason':'定向搜索未取得直接匹配的Kalshi合约；核协议合约不是同义比较。'}
r['title']='美伊停火期限：预测市场偏向选前维持，月底持续概率约三成半'
r['answer']={'text':'补看预测市场后，判断应比上一轮更具体：按Polymarket的“美国不实施合格空袭或导弹打击”定义，维持到选举日的盘口中点为94.5%，到11月8日为72.5%，到11月15日为51.5%，到11月底为34.5%。市场偏向近期维持，对整个月持续较不乐观；这些是市场基准，我尚无充分独立证据判断它偏高或偏低。','claim_ids':['C13','C14','C15','C17','C18','C20','C22','C23']}
r['findings']=[{'title':'上一轮遗漏了直接回答持续时间的市场基准','text':'这个问题虽然没有问资产价格，却问了事件持续期限。上一轮将价格相关性设为false，未检索相关合约，是研究方法遗漏。现在找到同口径多期限合约，使“多久”至少有了可观察的市场概率基准，而不再只能停留在无法排序。','claim_ids':['C7','C12','C22','C23'],'why_it_matters':'把独立证据不足与没有市场定价分开。','increment':{'kind':'judgment_update','baseline':'上一轮只说无法可靠估计剩余寿命，未检查预测市场。','detail':'加入带规则、选项与订单簿时刻的期限概率，形成明确市场比较基准。'}},{'title':'市场把近期延续与长期延续分开定价','text':'选举日YES为94.5%，11月8日72.5%，月中51.5%，月底34.5%，年底25.5%。这说明在合约口径下，近期不发生美方合格打击是主流，而整个月保持如此不是主流。期限越长事件累积风险通常越高；单一截面不能证明风险由选举引起，也不能把不同截止日直接当作精确复战日期。','claim_ids':price_ids+['C22'],'why_it_matters':'可以用市场期限结构回答短期与整月风险的差别，但不能机械宣布某天必战。','increment':{'kind':'new_fact','baseline':'原研究没有期限报价。','detail':'补入7个未来期限的同平台原始报价与裁决时间。'}},{'title':'合约名字叫停火，裁决实际只覆盖一类美方攻击','text':'规则关注美国发起、直接击中伊朗陆地领土及内水的合格空袭或地对地导弹打击；拦截未落地、网络行动、海军炮击等被排除。伊朗攻击、以色列单独行动和全面和平也不是同一问题。11月3日合约按美国东部时间截止，其余系列按伊朗标准时间截止。','claim_ids':['C13','C14'],'why_it_matters':'防止把94.5%读成双边全面和平概率。','increment':{'kind':'connection','baseline':'合约标题使用ceasefire continues。','detail':'将可交易事件的狭义裁决与用户关心的广义停火区分。'}}]
r['alternatives']=[{'title':'研究判断与市场基准分开','text':'上一轮关于互惠履约与冲突成本的机制仍可解释持续条件，但不足以产生一套优于盘口的数值概率。本轮采用市场概率作为比较基准，保留对持续行动和实施条款的核查；不将盘口数字包装成独立预测。','claim_ids':['C9','C10','C12','C23']}]
r['watch']=[{'signal':'同一期限YES价格在新消息后的变化','meaning':'固定相同合约与截止时刻，才能判断市场是否上调或下调停火持续预期；当前只有一个截面，不能声称近期趋势。','claim_ids':['C22']},{'signal':'双方实际打击与互惠措施的核实结果','meaning':'判断合约会否触发，并检查广义停火是否在合约未触发时已恶化。','claim_ids':['C11','C13','C23']}]
r['limitations']=[{'text':'概率取自11月1日22:44左右美国东部时间的YES买卖中点，是同平台有限深度的参考报价；其中11月底顶档约401/298份。它们不等同双边全面和平概率，也不证明研究者能独立预测停火寿命。','material':True,'claim_ids':['C13','C20','C23','C24']}]
r['tables']=[{'title':'不同截止日期的未发生合格美方打击定价','columns':['截止日期（2026年）','YES中点','YES最优买 / 卖','23:59所用时区'],'rows':rows,'claim_ids':price_ids+['C13','C14'],'note':'CLOB快照为2026-11-02 03:44:23—03:44:30 UTC（美国东部11月1日22:44）。各期异步约7秒；中点非可成交价。Gamma部分endDate与书面规则时区不同，表按书面规则。未作跨期相减或条件概率计算。'}]
a=r['analysis'];a['price_relevance']=True;a['baseline']=d['baseline'];a['baseline_claim_ids']=['C7','C12'];a['conclusion']=r['answer']['text'];a['conclusion_claim_ids']=['C22','C23'];a['model_reason']='仅比较原始盘口中点与期限结构，不使用财务模型或未经校准的寿命模型。';a['tests'].append({'id':'T3','outcomes':t['outcomes'],'status':'observed','claim_ids':['C13','C14']+price_ids,'interpretation':'价格显示短期高、远期低，形状与选后风险定价的H2预测相符，但共同的时间累积风险也能产生该结构；价格不能验证选举因果或真实复战。因而不裁定H1/H2/H3的实际机制。','supports':[],'weakens':[],'next_observation':'固定期限合约在新外交军事信息后的价格及实际行动','by':t['by'],'supports_if':'同一截止日价格随可验证履约改善而上升，且行动事实支持持续克制。','weakens_if':'发生合格打击或长期价格与实际履约记录背离。'})
a['market']={'status':'assessed','reason':'已核对当前合约规则、YES token映射与CLOB买卖盘；价格为买卖中点的indicative概率近似。','claim_ids':['C13','C14']+price_ids+['C22','C23','C24'],'model_ids':[],'implied_expectation':'选举日未发生合格美方打击94.5%，11月8日72.5%，11月15日51.5%，11月底34.5%。','research_expectation':'缺乏可校准独立寿命样本，不能报一套优于市场的独立概率；实际行动与双边条款仍需核查。','gap':'本轮补全先前漏掉的市场基准；没有证据证明存在可交易错价，也不能把狭义打击概率外推全面和平。','conditions':'固定同一合约、规则、截止时区、选项与盘口深度；观察后续行动与互惠履约。'}
r['update']={'judgment_changed':True,'reason':'纠正未检索预测市场的遗漏。由无法排序期限情景，更新为已有可核实市场基准：近期延续明显高于月末延续；未新增独立真实概率预测。','comparability':{'status':'mixed','reason':'原研究范围是广义美伊直接冲突；本轮价格只覆盖规则列明的美方合格打击，且增加当前市场截面，不能当作同一概率的历史修订。'}}
save('plan.json',p);save('claims.json',c);save('sources-before-selection.json',s);save('sources.json',s);save('report.json',r)
save('audit.json',{'as_of':stamp,'parent_run':P.name,'queries':p['queries'],'execution':[],'review':{'status':'pending'},'market_snapshot':'market-snapshot.json','raw_evidence':['us-iran-ceasefire-continues-through-the-midterms.json','us-iran-ceasefire-continues-throughptptpt.json','book-*.json','fee-rates.json'],'fees':'8个YES token基础费率API返回0；未估计链上/资金转换成本；中点不作为执行价。','identity':'每个book.asset_id与Gamma outcomes=Yes对应clobTokenIds逐一匹配，使用订单簿timestamp作为quoted_at。','selection':'正文展示选举日与6个系列期限；11月2日冗余近端快照保留原始文件但不入正文。','time_discrepancy':'系列Gamma endDate部分看似UTC或美国东部，书面规则明确伊朗标准时间；全部按description裁决文字呈现。不得混用时间。','structural_diff_interpretation':'新增price主张和market.assessed，price_relevance由false改true；这是补证导致判断改变，不是市场价格相对上轮发生变动。'})
print(stamp)
