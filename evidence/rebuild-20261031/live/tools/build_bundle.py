import json, html, re, shutil
from pathlib import Path
from datetime import datetime, timezone
R=Path('/Users/frankzhang/Desktop/投研助手/evidence/rebuild-20261031/live')
F=R/'raw/fetched'
def load(p): return json.loads(p.read_text())
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def body(n): return (F/n/'body.txt').read_text()
def locate(n,start,end=None):
    lines=body(n).splitlines(); a=next(i for i,l in enumerate(lines) if start in l)
    b=next(i for i,l in enumerate(lines[a:],a) if end in l) if end else a
    return '\n'.join(lines[a:b+1]),f'raw/fetched/{n}/body.txt:L{a+1}-L{b+1}'
def sel(reason,rel='direct',priority='decisive',selected=True,purpose='Resolve cash-burden accounting mechanism'):
    return dict(selected=selected,relevance=rel,priority=priority,reason=reason,purpose=purpose)
D=load(R/'raw/imported-sources.json')
for c in D['candidates']:
    c['selection']=sel('Actual engine-returned Microsoft story is unrelated to capex, leases, or cash burden; engagement does not repair relevance.',rel='irrelevant',priority='background',selected=False)
# Preserve official original excerpts and table axes; never replace with search summaries.
qcall,lcall=locate('official-call','Capital expenditures were $24.2 billion')
qcash,lcash=locate('official-release','Additions','(44,477)') if False else ('','')
lines=body('official-release').splitlines(); cashidx=lines.index('(17,079)')
qcash='\n'.join(lines[cashidx-3:cashidx+7]); lcash=f'raw/fetched/official-release/body.txt:L{cashidx-2}-L{cashidx+7}; CASH FLOWS STATEMENTS, in millions, first column Three Months Ended June 30 2025; header saved in response.bin'
qannual,lannual=locate('official-annual','Supplemental cash flow information related to leases was as follows:','| 3,128')
qannual2,lannual2=locate('official-annual','As of June 30, 2025, purchases of property and equipment remaining') if False else locate('official-annual','purchases of property and equipment remaining in accounts payable')
qfuture,lfuture=locate('official-annual','we had additional leases, primarily for datacenters, that had not yet commenced')
# Supplement annual source with precise cash-flow rows and period headers.
ann=body('official-annual').splitlines(); ci=next(i for i,l in enumerate(ann) if l=='| 136,162'); pi=next(i for i,l in enumerate(ann) if l=='| (64,551)')
annualcfo='\n'.join(ann[ci-2:ci+7]); annualppe='\n'.join(ann[pi-2:pi+7])
qmedia,lmedia=locate('geekwire','The company reported $24.2 billion')
community=load(F/'hn-comment-original/body.json'); commtext=html.unescape(re.sub('<[^>]+>',' ',community['text'])); owncomment=commtext[commtext.index('Maybe I’m not getting it.'):]
now=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def source(sid,n,tier,quote,locator,reason,origin,published='2025-07-30',supports=None,kind='document',url=None):
    meta=load(F/n/'fetch.json')
    return dict(id=sid,url=url or meta['url'],publisher='Microsoft' if tier=='T0' else 'Todd Bishop / GeekWire' if n=='geekwire' else '_aavaa_ / Hacker News',tier=tier,published_at=published,retrieved_at=meta['retrieved_at'],quote=quote,locator=locator,origin_id=origin,origin_basis='Microsoft original financial disclosure; repeated numbers in media remain the Microsoft fact family' if tier=='T0' else 'Original bylined GeekWire reporting, independently edited publication; reported Microsoft figures are not a second independent measurement' if n=='geekwire' else 'Original public comment by _aavaa_; verified both on HN HTML permalink and official Firebase item API',supports=supports or ['fact','view'],evidence_kind=kind,access_status='ok',selection=sel(reason),provenance={'fetch_record':str((F/n/'fetch.json').relative_to(R))})
D['candidates'] += [
 source('S14','official-call','T0',qcall,lcall,'Direct same-quarter definitions and lease commencement disclosure','msft-fy25-disclosures'),
 source('S15','official-release','T0',qcash,lcash,'Exact quarterly cash PP&E figure and period axes','msft-fy25-disclosures'),
 source('S16','official-annual','T0',qannual+'\n[...]\n'+annualcfo+'\n[...]\n'+annualppe+'\n[...]\n'+qannual2+'\n[...]\n'+qfuture,lannual+f'; annual CFO L{ci-1}-L{ci+7}; annual PP&E L{pi-1}-L{pi+7}; '+lannual2+'; '+lfuture,'Annual cash-flow classifications, payment timing context and future commitments; annual numbers never mixed with Q4','msft-fy25-disclosures',published='unknown'),
 source('S17','geekwire','T2',qmedia,lmedia,'Original independent media publication provides reporting context; it does not establish an independent cash reconciliation','geekwire-todd-bishop-20250730',supports=['view']),
 source('S18','hn-comment-original','T4',owncomment,'raw/fetched/hn-discussion-original/body.txt:L13; official Firebase item 50304674 text final paragraph; timestamp from Unix time field','Actually fetched community original questions an analyst-versus-company expectation comparison; context only, no adoption of quoted amounts or representativeness','hn-_aavaa_-50304674',published=datetime.fromtimestamp(community['time'],timezone.utc).isoformat().replace('+00:00','Z'),supports=['view'],kind='opinion',url='https://news.ycombinator.com/item?id=50304674')]
# Carry all fetched but unused media as a candidate, with an explicit choice.
tech=source('S19','techradar','T2','','','Fetched but GeekWire directly covers the chosen quarter; do not add redundant reporting or search-derived facts','techradar-original',published='unknown',supports=['view'])
tech['selection']=sel('Fetched original but not required for the selected quarter and narrow mechanism; retained as unused candidate.',rel='context',priority='background',selected=False)
D['candidates'].append(tech)
D['as_of']=now; D['historical']=False
D['source_status'].update({
 'official_web':{'status':'ok','detail':'3 originals fetched HTTP 200; annual publication date left unknown; current retrieval supports use at as_of'},
 'independent_media':{'status':'ok','detail':'GeekWire and TechRadar originals fetched HTTP 200; initial GeekWire WebFetch returned 403, cookie-free urllib retry succeeded'},
 'community_supplement':{'status':'partial','detail':'2 direct Algolia searches; one relevant context comment fetched on official HN HTML and Firebase; engine returned zero semantically relevant candidates'},
 **{p:{'status':'not_run','detail':'Not selected: cookie-free HN-only validation, no authentication/setup/paid lane'} for p in ('reddit','x','youtube','polymarket','github')},
 'native_web_search':{'status':'ok','detail':'5 actual host search calls; search excerpts not used as source quotes'}})
D['retrieval']['supplement_method']='5 host web searches and 2 direct Algolia queries; supplementary community comment is NOT an engine hit'
D['retrieval']['retrieval_window']='Engine 365 days, range_from=2025-10-31 to range_to=2026-10-31. Accounting case uses FY25Q4 originals outside that window, deliberately fetched separately.'
write(R/'sources.annotated.json',D)
question='Microsoft 含融资租赁的资本开支与现金 PP&E，应如何比较实际现金负担？'
task='用 FY25Q4 历史案例验证真实检索、语义筛选、证据绑定、渲染和隔离归档；只研究会计机制。'
plan=dict(schema_version=2,question=question,task=task,entity='Microsoft / MSFT',type='asset',historical=False,as_of=now,decision_needed='确定投入规模、当期现金支出和未来租赁义务的比较口径',prior_judgment='待核实：headline capex 与 cash PP&E 不同，二者差额未必等于新融资租赁。',stop_condition='官方原文、独立媒体原文、社区原文均有实际抓取；数字和分类可定位，未解决差额明确保留。',comparison={'period':'FY25Q4 quarter ended 2025-06-30; separate explicitly labelled FY2025 annual illustration','unit':'USD billion unless source original says USD million','scope':'Consolidated Microsoft; gross investment, cash PP&E, and lease principal/interest classification; not all capex is AI'},hypotheses=[{'explanation':'两种 capex 口径仅由新融资租赁解释','discriminating_observation':'计算季度总投入减现金 PP&E，和披露的新融资租赁比较。'},{'explanation':'还包含现金支付与确认时点差异，且租赁本金另列融资现金流','discriminating_observation':'核对年报租赁现金流分类、PP&E 应付款和季度定义。'}],queries=[{'question':'季度定义与金额是什么？','query':'Microsoft FY25 Q4 24.2 billion capital expenditures finance leases 6.5 17.1 cash','source':'host web then official original GET','purpose':'定义和现金金额'},{'question':'独立报道怎样描述投入？','query':'Microsoft July 30 2025 24.2 capital expenditures finance leases cash 17.1 Reuters CNBC','source':'host web then GeekWire original GET','purpose':'媒体叙事口径'},{'question':'社区讨论是否能帮助发现比较陷阱？','query':'Microsoft capex; Microsoft leases (engine actual executed); finance leases comments; Microsoft capex stories (direct Algolia)','source':'Last30Days 3.30.0 HN; supplementary Algolia and HN originals','purpose':'社区原文与误比较线索'}],budget={'max_queries':9,'max_followups':2})
write(R/'plan.json',plan)
def claim(cid,text,typ,ids=None,**kw):
    return dict(id=cid,text=text,type=typ,as_of=now,sources=[{'source_id':sid} for sid in (ids or [])],**kw)
claims=[
 claim('C1','FY25Q4 管理层披露资本开支 24.2B，其中融资租赁 6.5B，租赁开始时确认全部价值；现金 PP&E 约 17.1B。','fact',['S14']),
 claim('C2','FY25Q4 现金流表 additions to property and equipment 为 17,079 百万美元，即 17.079B。','fact',['S15']),
 claim('C3','用披露值相减，总资本开支减现金 PP&E 约 7.121B，再减披露的 6.5B 新融资租赁，仍约 0.621B；原文未逐项调节这个季度残差。','inference',basis=['C1','C2'],calculation_ids=['K1','K2']),
 claim('C4','FY2025 年报列融资租赁经营现金流 1.372B、融资现金流 2.283B；全年 CFO 136.162B、现金 PP&E 64.551B。年末 PP&E 应付款 6.9B，未开始租赁 92.7B。','fact',['S16']),
 claim('C5','当期现金压力以 CFO 减现金 PP&E 为起点；比较融资租赁后的股东剩余现金时再减同一期间融资租赁本金。该经营现金流口径已含租赁经营现金支付，不能再把该项重复扣除；新租赁开始确认金额另列为投入和未来义务线索。FY2025 示例为 71.611B 与扣本金后 69.328B。','inference',basis=['C1','C2','C4'],calculation_ids=['K3','K4']),
 claim('C6','GeekWire 原创报道把 FY25Q4 的 24.2B 称为资本投入，并讨论长期资产和服务器的用途；媒体 headline 的投入规模仍须与现金流口径分开。','view',['S17']),
 claim('C7','HN 用户 _aavaa_ 在原帖质疑，把低于外部分析师预计的支出直接称为 miss 是否合适。这里只记录该用户个人质疑；评论转引数字未在本案例核验。','view',['S18']),
]
write(R/'claims.json',dict(schema_version=2,as_of=now,claims=claims))
def calc(cid,description,formula,inputs,result,refs):
    return dict(id=cid,description=description,formula=formula,inputs=[dict(name=n,value=v,unit='USD billion',claim_ids=[c]) for n,v,c in inputs],result={'value':result,'unit':'USD billion'},claim_ids=refs)
calculations=[
 calc('K1','Q4 reported headline less cash PP&E; approximate because headline rounded','24.2 - 17.079',[('headline_capex',24.2,'C1'),('cash_ppe',17.079,'C2')],7.121,['C1','C2']),
 calc('K2','Unreconciled Q4 remainder after reported new finance leases; not an identified accounting item','(24.2 - 17.079) - 6.5',[('headline_capex',24.2,'C1'),('cash_ppe',17.079,'C2'),('new_finance_leases',6.5,'C1')],0.621,['C1','C2']),
 calc('K3','Annual cash FCF starting point; FY2025 only','136.162 - 64.551',[('CFO_FY2025',136.162,'C4'),('cash_ppe_FY2025',64.551,'C4')],71.611,['C4']),
 calc('K4','Annual financing-lease-principal-adjusted residual cash; analytical metric, not issuer-labelled FCF','136.162 - 64.551 - 2.283',[('CFO_FY2025',136.162,'C4'),('cash_ppe_FY2025',64.551,'C4'),('finance_lease_financing_cash_FY2025',2.283,'C4')],69.328,['C4'])]
write(R/'calculations.json',dict(schema_version=2,as_of=now,calculations=calculations))
report=dict(schema_version=2,title='微软资本开支：把投入确认、当期现金与未来租赁义务分开',question=question,task=task,type='asset',as_of=now,
 answer={'text':'研究现金负担应并列三个视角：总资本投入看资源取得；当期现金以 CFO 减 cash PP&E 为起点，再单列同期间融资租赁本金；未来负担看已签约租赁及到期表。FY25Q4 的 24.2B 含新融资租赁，现金 PP&E 是 17.079B；约 7.121B 差额不能全称为新融资租赁，更不能当作当期现金支出。','claim_ids':['C1','C2','C3','C5']},
 findings=[
 {'title':'24.2B 是投入确认口径，17.079B 是现金 PP&E','text':'电话会解释融资租赁在开始时确认全部价值。GeekWire 也以 24.2B 描述投资规模；做现金压力或跨公司比较时，须回到现金流表，统一期间、单位及租赁处理。','why_it_matters':'用 headline capex 直接扣 CFO 会把新租赁的确认与当期支付混用。','claim_ids':['C1','C2','C6'],'increment':{'kind':'connection','baseline':'媒体 headline 投入规模','detail':'与现金流原表和租赁开始确认机制关联。'}},
 {'title':'差额约 7.121B，仍有约 0.621B 未调节','text':'24.2 − 17.079 ≈ 7.121；再扣 6.5 后约 0.621。因 24.2 和 6.5 已四舍五入，这些差值也是近似数。年报披露 PP&E 应付款，只能提示支付时点可能影响桥接，不能证明本季度残差的具体组成。','why_it_matters':'保留未解释残差，避免把一个算术差额包装成新增融资租赁事实。','claim_ids':['C1','C2','C3','C4'],'calculation_ids':['K1','K2'],'increment':{'kind':'calculation','baseline':'差额全是新融资租赁的假设','detail':'原披露值计算后不相等，拒绝伪调节。'}},
 {'title':'当期现金还要看融资租赁本金；未来义务另列','text':'FY2025 全年示例：CFO 136.162 − cash PP&E 64.551 = 71.611B；再扣年报的融资租赁融资现金流 2.283 = 69.328B。这是分析口径，且全部采用全年数据。已含在 CFO 的 1.372B 融资租赁经营现金流不要再扣。未开始租赁 92.7B 是未来义务线索，不能计作这一年的现金支出。','why_it_matters':'同时避免漏计租赁本金和重复扣经营现金项。社区原帖也提醒比较基准必须写清，单条评论不构成共识。','claim_ids':['C4','C5','C7'],'calculation_ids':['K3','K4'],'increment':{'kind':'calculation','baseline':'仅看 CFO 减 cash PP&E','detail':'增加同期间租赁本金后的剩余现金展示，同时隔离未来义务。'}}],
 alternatives=[{'title':'若问题改为扩建规模或设备需求','text':'可以先看含新融资租赁的资本投入，同时附现金口径；投入用途不可全部称为 AI。','claim_ids':['C1','C6']}],
 watch=[{'signal':'同一期间租赁本金、PP&E 应付款变化和明确的资本开支调节表','meaning':'能否解释确认与支付差异；未取到 Q4 独立租赁本金，不能给出 Q4 扣租赁后的现金余额。','claim_ids':['C3','C4','C5']}],
 limitations=[
 {'text':'只完成一个会计机制案例。FY25Q4 为历史财报，as_of 是本次抓取后冻结的当前时点；不声称还原 2025 年当日信息集，也不提供最新买卖建议。','material':True,'claim_ids':['C1','C2']},
 {'text':'引擎扩大到 365 天并返回 13 候选，但语义筛选全部不相关；社区原帖来自另行 Algolia 检索与官方 HN 抓取。仅一条上下文观点，无社区代表性、完整平台召回或全链路相关性成功证明。','material':True,'claim_ids':['C7']},
 {'text':'独立媒体是原创编辑出版物，但重复的微软数字仍属于同一事实源；没有把媒体转述当作独立现金调节验证。','material':True,'claim_ids':['C6']},
 {'text':'验证器检查结构、时间和引用，公式字段不会被执行；本次另用 Decimal 独立复算四个值。未验证资本投入回报率、所有承诺的现金到期分布或季度残差成因。','material':True,'claim_ids':['C3','C5']}],
 tables=[{'title':'统一期间与口径（USD billion）','columns':['期间','项目','值','含义'],'rows':[['FY25Q4','含融资租赁资本开支',24.2,'确认投入'],['FY25Q4','现金 PP&E',17.079,'投资现金流支出'],['FY25Q4','新融资租赁',6.5,'开始时确认；不等于当期本金'],['FY2025全年','融资租赁融资现金流',2.283,'年度本金现金压力'],['FY2025全年','扣本金后分析现金余额',69.328,'分析口径，非季度值']],'claim_ids':['C1','C2','C4','C5'],'note':'季度与全年清楚标记，不作跨期间相加。'}],calculations=calculations)
write(R/'report.json',report)
shutil.copyfile(R.parent/'last30days-diagnose.json',R/'raw/parent-diagnose.json')
write(R/'raw/searches.json',{'native_web_queries':['Microsoft FY25 Q4 24.2 billion capital expenditures finance leases 6.5 17.1 cash','Microsoft capex finance leases cash flow Hacker News','Microsoft July 30 2025 24.2 capital expenditures finance leases cash 17.1 Reuters CNBC','Microsoft FY25 Q4 earnings call transcript cash paid property equipment finance leases 6.5 Microsoft.com','"site:news.ycombinator.com" "Microsoft" "leases" capex'],'search_call_count':9,'breakdown':{'native_web':5,'engine_actual_hn_queries':2,'direct_algolia_supplement':2},'requested_engine_subqueries':3,'actual_engine_subqueries':2,'note':'Engine normalized to 2 subqueries. Count is logical search request count, not hidden provider retries, result pages or enrichment requests. 2 host WebFetch calls: official success, GeekWire 403; then 10 urllib GET requests including original retrieval and supplementary searches, all HTTP 200.','diagnostic_scope':'parent diagnostic copied; no fresh diagnose or login-backed doctor needed because run restricts to HN','native_results_use':'Only locate URLs; all accepted quotes separately fetched.'})
print(json.dumps({'as_of':now,'candidates':len(D['candidates']),'claims':len(claims),'selected_requested':5},indent=2))
