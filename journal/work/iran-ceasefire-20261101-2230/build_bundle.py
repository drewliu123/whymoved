import json
from pathlib import Path
from datetime import datetime,timezone
W=Path(__file__).parent
stamp=datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def save(name,obj): (W/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
p=json.loads((W/'plan.json').read_text());p['as_of']=stamp;save('plan.json',p)
sources=[]
def source(sid,url,publisher,tier,date,quote,locator,origin,purpose,supports,selected=True,access='ok'):
 sources.append(dict(id=sid,url=url,canonical_url=url,publisher=publisher,tier=tier,published_at=date,retrieved_at=stamp,quote=quote,locator=locator,origin_id=origin,origin_basis=purpose,supports=supports,evidence_kind='document',access_status=access,selection=dict(selected=selected,reason=purpose,relevance='direct',purpose=purpose,priority='decisive' if selected else 'background')))
source('S1','https://www.whitehouse.gov/releases/2026/06/president-trumps-iran-agreement-is-america-first-in-action/','The White House','T0','2026-06-19','President Donald J. Trump and Vice President JD Vance have secured a historic breakthrough by signing a Memorandum of Understanding with Iran.','正文首段；本地evidence/whitehouse-june.txt:165','whitehouse-june19','核实白宫当时对签署备忘录的公开表述，不据此确认现时履约',['fact'])
source('S2','https://www.whitehouse.gov/releases/2026/06/president-trumps-iran-agreement-is-america-first-in-action/','The White House','T0','2026-06-19','Whether or not the United States can reach an acceptable, verifiable deal with Iran regarding its nuclear program and other issues is yet to be determined','Sen. Lindsey Graham段；evidence/whitehouse-june.txt:183','whitehouse-june19','白宫所载Graham当时观点；揭示停火与可核查最终核协议的区别',['view'])
source('S3','https://ca.marketscreener.com/news/why-has-the-iran-us-ceasefire-memorandum-frayed-ce7f5edcd888f325','Reuters / MarketScreener','T2','2026-07-13','on July 7, the U.S. revoked a license','Reuters解释报道的石油豁免部分；正文同时讨论资金未释放、航行权及核问题','reuters-july13','可读Reuters复盘提供执行次序与争端线索；同一报道只算一个origin',['view'])
source('S4','https://www.aol.co.uk/articles/iranian-negotiators-doha-continue-talks-122402000.html','Reuters / AOL UK','T2','unknown','no final conclusion had been reached','Reuters正文第4段，归属Iranian Foreign Minister Abbas Araqchi；页面Updated 2026-11-01 13:57 UTC','reuters-doha-nov1','最新可读报道引述外长称谈判未有最终结论；非官方协议文本',['view'])
source('S5','https://www.aol.co.uk/articles/iranian-negotiators-doha-continue-talks-122402000.html','Reuters / AOL UK','T2','unknown','before the vote','Reuters正文第2段：报道特朗普暂停追加攻击的承诺覆盖11月3日投票前；页面Updated 2026-11-01 13:57 UTC','reuters-doha-nov1','限定报道中的美方承诺窗口；不能当成双方停火到期条款',['view'])
source('S6','https://gcaptain.com/irans-irgc-navy-says-four-tankers-catch-fire-in-strait-of-hormuz/','Reuters / gCaptain','T2','2026-10-31','All U.S. military unmanned surface vessels in the Middle East are accounted for','正文CENTCOM对无人水面艇说法的回应；Reuters dispatch Oct30。UKMTO通知与伊方四船说法不能合并计数。','reuters-hormuz-oct30','保留海事风险反证；各方声明归属不同，不能由伊方声称四船起火推为已证实四船遇袭',['view'])
source('S7','https://apnews.com/article/422b1799a1a06466279ac265f560e014','AP','T2','2026-10-08','','全文抓取失败；只见搜索标题','ap-oct8','原站与部分转刊均不可读，保留候选但不支持主张',[],False,'failed')
source('S8','https://apnews.com/article/b918f44d8f212d7daf7f2f9a98c91a0b','AP','T2','2026-11-01','','全文抓取失败；只见搜索摘述','ap-nov1','最新AP线索正文无法取得，不用作第二独立事实支持',[],False,'failed')
source('S9','https://www.lemonde.fr/en/international/article/2026/10/30/iran-braces-for-possible-new-conflict-with-us-and-israel-despite-diplomatic-talks_6767460_4.html','Le Monde','T2','2026-10-30','','全文抓取失败','lemonde-oct30','不能凭搜索摘要验证当前备战与谈判细节',[],False,'failed')
sdoc=dict(schema_version=2,as_of=stamp,historical=False,candidates=sources,source_status={'official':{'status':'partial','reason':'取得6月白宫历史原文，未取得当前双边协议与完整履约安排'},'latest_reuters':{'status':'ok','reason':'11月1日AOL转刊可读，声明作归属观点使用'},'independent_AP':{'status':'unreachable','reason':'原站及Local10/CityNews/WBAL转刊未取得全文'},'shipping':{'status':'partial','reason':'取得Reuters转刊，UKMTO通知仍为转述，未取得独立现场确认'},'IAEA_current':{'status':'no_results','reason':'定向搜索只返旧文件，不能说明当前核查未实施'},'community':{'status':'not_run','reason':'等待社区侦察结果写入审计，不用于事实支持'}})
save('sources-before-selection.json',sdoc);save('sources.json',sdoc)
claims=[]
def claim(cid,text,kind,refs=(),basis=()):
 c=dict(id=cid,text=text,type=kind,as_of=stamp,sources=[{'source_id':s} for s in refs])
 if basis:c['basis']=list(basis)
 claims.append(c)
claim('C1','白宫6月19日公告称，美伊已签署谅解备忘录；这是当时的美方公开表述，不能证明当前仍在履约。','fact',['S1'])
claim('C2','白宫该公告所载Graham的判断是：能否达成可接受且可核查的最终核协议仍未确定。','view',['S2'])
claim('C3','路透7月13日复盘将当时安排的恶化与石油豁免撤销、被冻结资金及海峡航行权争端联系起来；这是该报道的解释框架。','view',['S3'])
claim('C4','11月1日路透报道引述伊朗外长称，谈判尚未达成最终结论。','view',['S4'])
claim('C5','11月1日路透报道将特朗普暂停追加攻击的承诺描述为覆盖11月3日投票前；未提供双方以该日为到期日的停火条款。','view',['S5'])
claim('C6','路透10月30日海事报道转述伊方关于油轮起火的声明与UKMTO通知，同时记载CENTCOM反驳另一起无人艇说法；事件数量与归属尚不能合并确认。','view',['S6'])
claim('C7','截至11月1日可取得的材料，不足以可靠估计停火还剩几天或几个月；较有依据的工作判断是选举前后短期克制窗口，仍不能确认可延续数月的双边安排。','inference',basis=['C1','C2','C4','C5'])
claim('C8','11月3日是当前承诺窗口的首个复核点，不是已知双边停火期限；承诺未覆盖之后，不代表11月4日必然复战。','inference',basis=['C5'])
claim('C9','延续数周取决于选后克制继续和谈判渠道保持；延续一至三个月则更需要海峡通行、封锁或制裁安排的互惠落实与核查。它们是条件情景，不是已实现事实或寿命预测。','inference',basis=['C2','C3','C4','C5'])
claim('C10','此前备忘录与未完成核协议并存的经历说明，停止直接打击与解决争议是不同阶段；若一方先履约却拿不到对价，恢复施压的诱因会上升。','inference',basis=['C1','C2','C3'])
claim('C11','应观察选后美伊是否继续克制、是否有双方接受的实施文本，以及船舶实际通行和互惠措施；单次争议事件需要先核实，不能自动判停火全面破裂。','inference',basis=['C4','C5','C6','C9'])
claim('C12','最新协议全文、近30日直接交火时间线、独立航运与核查履约记录尚未核齐，因此本轮不能为未来数周与数月情景排序或赋数值概率。','inference',basis=['C4','C5','C6','C7'])
save('claims.json',dict(schema_version=2,as_of=stamp,claims=claims))
answer='以11月1日可取得的材料看，我更倾向把当前状态理解为选举前后的短期克制窗口，尚不足以按“稳定停火数月”来判断。11月3日是首个复核点；究竟还能持续几天或几周，目前缺少已核实的双边条款与近期交火记录，无法可靠给出期限。'
findings=[dict(title='11月3日是承诺窗口，不能当作战争重启日期',text='11月1日路透报道把特朗普暂停追加攻击的承诺限定在11月3日投票前，同时引述伊朗外长称谈判“尚未达成最终结论”。这支持把选后是否继续克制作为近期检验，而不能推成双方已同意在该日结束停火，更不能推成11月4日必战。',claim_ids=['C4','C5','C8'],why_it_matters='先确认当前安排的性质，才能讨论寿命。',increment=dict(kind='connection',baseline='把报道中的暂停攻击统称为美伊停火。',detail='将单方承诺覆盖窗口与双方协议期限分开。')),
 dict(title='能否延长，关键在互惠措施能否兑现',text='6月白宫已宣布签署备忘录，但同页所载Graham仍称最终可核查核协议未定。路透7月复盘又将安排恶化与石油豁免、资金和航行权争端相联系。我的判断是：双方有意暂停攻击，只能解释眼前克制；要稳定数月，还需让海峡通行、封锁或制裁的交换具有明确次序、可核查结果和争议处理办法。',claim_ids=['C1','C2','C3','C10'],why_it_matters='文本上的停火意愿与持续执行所需激励并不等同。',increment=dict(kind='connection',baseline='6月备忘录的政治承诺。',detail='联系后续执行争端，定位延长克制所需的互惠条件。'))]
analysis=dict(version=1,question_kind='event_forecast',method='reference_class_scenarios',price_relevance=False,baseline=p['research_design']['baseline'],baseline_claim_ids=['C1','C2'],mechanism_chain=p['research_design']['mechanism_chain'],hypotheses=[dict(id=h['id'],explanation=h['explanation']) for h in p['hypotheses']],tests=[],conclusion=answer,conclusion_claim_ids=['C7','C8','C9','C12'],model_status='not_applicable',model_reason='研究停火持续条件，没有可校准的生存样本，不强配财务模型或数值概率。',models=[],market=dict(status='not_applicable',reason='本题判断政治军事安排持续条件，不评估资产或预测市场定价。',claim_ids=[],model_ids=[]))
for t in p['research_design']['discrimination_tests']:
 analysis['tests'].append(dict(id=t['id'],outcomes=t['outcomes'],status='missing',claim_ids=[],supports=[],weakens=[],gap_reason='T1只有最新报道所载声明，未取得当前双方实施文本。' if t['id']=='T1' else '未取得近30天直接打击、独立航运和核查的完整行动记录；不可用缺失判稳定。',interpretation='保留声明线索，无法以合格行动事实裁定竞争解释。',next_observation=t['observe'],by=t['by'],supports_if='选后持续克制支持H1；双方核查互惠落实支持H3。',weakens_if='恢复持续直接打击支持H2，削弱H1与H3。'))
report=dict(schema_version=2,title='美伊停火：先看选后克制能否续接，再谈持续数月',question=p['question'],type=p['type'],task=p['task'],as_of=stamp,answer=dict(text=answer,claim_ids=['C7','C8','C12']),findings=findings,alternatives=[dict(title='短期克制可能延长，但材料尚不足以排序情景',text='若选后仍停止直接打击且谈判持续，克制延续数周有条件成立；若双方持续落实互惠与核查安排，一至三个月稳定才更有依据。若恢复持续直接交火，则当前克制窗口已结束。以上是检验路径，不是概率预测。',claim_ids=['C9','C11','C12'])],watch=[dict(signal='11月3日之后，克制承诺是否续接及双方接受的实施文本',meaning='区分短期政治暂停与有执行安排的停火；尤其核对谁先行动、对价何时交付。',claim_ids=['C8','C9','C11']),dict(signal='实际航运与直接军事行动，而不只是重开海峡的承诺',meaning='连续通行和履约支持稳定情景；已核实持续直接交火支持复战情景。10月30日海事报道各方说法仍有分歧，不能相加成确认损失。',claim_ids=['C6','C11'])],limitations=[dict(text='当前双边实施文本、近30日直接交火和独立履约记录未核齐；因此不报精确天数或概率，也不把未见复战报道当作没有交火。',material=True,claim_ids=['C12'])],tables=[],analysis=analysis)
save('report.json',report)
save('audit.json',dict(as_of=stamp,queries=[dict(query=q['query'],purpose=q['purpose'],test_ids=q['test_ids']) for q in p['queries']],context_review=dict(selected='6月承诺及7月执行争端是机制参考；9月至11月最新谈判与选举承诺决定近期复核点。',missing='当前双边文本、完整直接交火与航运核查；缺失不支持任何H。'),review=dict(status='pending',findings=[],dispositions=[]),execution=[dict(command='analysis_contract.py route event_forecast',exit_code=0),dict(command='research_plan.py plan.json',exit_code=0),dict(command='WebFetch AP/Local10/CityNews/WBAL/LeMonde',status='unreachable',log='工具输出；失败候选未用于支持主张'),dict(command='urllib evidence archival',status='partial',log='evidence/whitehouse-june.html及.txt；MarketScreener直取403，WebFetch可读')],source_notes='Reuters转刊同源不重复计数；更新日期与发布日期分别记录。所有声明按归属观点处理；两项区分检验均missing。'))
print(stamp)
