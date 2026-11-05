# -*- coding: utf-8 -*-
import json
from pathlib import Path
w=Path('/Users/frankzhang/Desktop/投研助手/journal/work/meta-nov-20261102')
def load(p):return json.loads((w/p).read_text())
def save(p,x):(w/p).write_text(json.dumps(x,ensure_ascii=False,indent=2))
r=load('report.json'); c=load('claims.json'); a=load('audit.json')
cm={x['id']:x for x in c['claims']}
cm['C-MECHANISM']['text']='在11月没有新增现金回报改善的情景下，投入压力使研究倾向暂偏下探。广告量价增长提供反弹基础，资本开支超过当季经营现金流及2027积极投入计划构成估值压力；但10月21日披露已伴随至30日11.83%的下跌，尚无同口径新增预期下修证明11月仍会下跌。法律计提及Reality Labs改善也限制单边经营崩塌解释。'
cm['C-MECHANISM']['basis'].append('C-DROP')
cm['C-MARKET']['text']='该两档的持有成本门槛：DOWN600 Yes bid/ask0.74/0.79，含费约79.66%；UP660 Yes bid/ask0.40/0.55，含费约55.99%。600下档距收盘仅2.44%、660上档距7.32%，距离差本身即可造成不同触及率，不能由报价高低识别市场方向倾向。'
cm['C-MARKET']['basis'] += ['E-DOWN600-Yes','E-UP660-Yes']
cm['C-RANK']['text']='研究核查顺序：先看DOWN600 Yes，因为投入压力情景更直接、价差5¢且顶档110份；再看UP660 Yes，价差15¢且顶档20份。该顺序是取证与执行条件的优先级，不代表预期收益排序。600 Yes含费门槛79.66%、660 Yes为55.99%，当前均无已建立的概率优势；10月已下跌11.83%，不能重复当成新增利空。DOWN600 No优先级低：26¢对应整月不下探，缓冲仅2.44%，与能够反弹不同。UP740/760缺尾部概率和新增强催化依据。'
cm['C-DOMINANCE']['text']=cm['C-DOMINANCE']['text'].replace('相同月内触及及调整规则下，','相同月内触及及调整规则、且两边可见低价挂单的共同数量内，')
cm['C-CONCLUSION']['text']='截至11月2日开盘前，在没有新增现金回报改善的情景下，投入压力使研究倾向暂偏下探，同时广告韧性支持反弹可能。10月披露已伴随11.83%跌幅，未证明11月仍有新增下修。优先核查600下探Yes，再核查660上触Yes，依据是机制匹配及价差/深度，并非已证实收益排序；两档均为watch，尚无经成本验证的概率优势。整月不碰600的No与昂贵劣后档位吸引力较低。'
r['answer']['text']='在2026年11月没有新增现金回报改善的情景下，我暂偏向META下探风险，但广告韧性使反弹仍有基础。包含AI扩张的资本开支已超过当季经营现金流；不过10月披露后股价已跌11.83%，持续投入本身不等于11月新增利空。Polymarket先核查600下探Yes，再核查660上触Yes：前者价差更窄、顶档更深，且更贴近压力情景。这是研究顺序，两档当前都处于观察状态。'
f=r['findings']
f[1]['text']=f[1]['text'].replace('这些数字支持偏弱而有反弹可能的判断，既不支持业务崩塌，也不证明利空已经出尽。','这使我保留有条件的下探倾向及反弹情景；持续投入不能自动当作11月新增利空。')
f[2]['text']=f[2]['text'].replace('前者机制更直接，后者允许先跌后涨，但当前证据不能给出超过这些成本的独立胜率。','前者与压力情景更贴近、价差5¢且顶档110份；后者允许先跌后涨，但价差15¢且顶档仅20份。')
f[3]['text']=f[3]['text'].replace('同规则下这些昂贵档位被更便宜档位覆盖，计费后排序仍不变。','在两边低价挂单的共同可买数量内，这些昂贵档位被更便宜档位覆盖，计费后排序仍不变。')
for calc in r['calculations']:
    if calc['id'].startswith('K-UP') or calc['id'].startswith('K-DOWN'):
        calc['description']='按顶档价格测算的单份理论含费成本（100份仅作舍入计算基准，实际数量受深度限制）'
for row in r['tables'][0]['rows']:
    if row[0]=='触及600 / Yes':row[-1]='第一核查：压力情景更直接，价差5¢、顶档110份'
    if row[0]=='触及660 / Yes':row[-1]='第二核查：反弹情景，价差15¢、顶档20份'
rd=r['analysis']; rd['conclusion']=r['answer']['text']
rd['market']['research_expectation']='没有新增现金回报改善时暂偏向下探，但10月已实现跌幅约束后续方向判断；广告韧性保留反弹可能。'
rd['market']['gap']='当前只评估这两档的成本门槛；门槛距离不同，报价高低不能识别市场方向倾向。未校准独立触及概率，未证明超成本差异；可核实增量是路径与相对成本筛选。'
for t in rd['tests']:
    if t['id']=='T1':
        t['next_observation']='11月新增公司收入、投入、现金回报或预算信息，并区分是否只是重述10月披露'
        t['supports_if']='新增收入现金增长无法覆盖新增投入，增强H2；收入现金同步兑现且投入收敛，增强H1'
        t['weakens_if']='核心现金回报改善削弱H2；广告量价与现金同步走弱削弱H1'
    if t['id']=='T2':
        t['next_observation']='取得11月2—10日同窗META及QQQ收益、美国国债收益率变化，配对公司新增盈利或投入修订'
        t['supports_if']='在科技指数及利率压力缓和时META仍相对弱且出现公司成本上修，增强H2；无公司修订但板块共同随利率冲击变化，增强H3'
        t['weakens_if']='板块共变且无公司特有修订削弱H2主导解释；公司特有弱势与成本修订同现而板块稳定则削弱H3'
    if t['id']=='T3':
        t['interpretation']='本轮只完成合约身份、路径规则和成本核对，尚无区分结果。原计划的两个预测可以同时成立，不能把该检验作为H1或H2的裁决；当前两组supports/weakens为空。'
        t['next_observation']='取得匹配11月常规交易时段的首次触及参考类或透明期权分布，分别比较各档含费门槛；下一run重设计真正不同的预测'
        t['supports_if']='只有方法匹配的独立情景概率在成本之外有足够余量才支持对应合约研究升级；单次触及只确认结算事件，不确认经营因果'
        t['weakens_if']='若概率余量被费用/滑点吞噬则削弱对应机会；参考类不能区分时继续不裁定H1/H2'
o=r['opportunity']
o['market_view']['text']='以实际订单簿和费用为代理，只说明两档持有至结算的成本要求：600下探Yes约79.66%、660上触Yes约55.99%。因离现价距离不同，不从高低比较推断投资者方向倾向。'
o['variant']['text']='暂无已建立的概率分歧。研究倾向是有条件的下探情景，增量在区分现金压力与法律计提、反弹与整月不下探；10月已跌后的残余下行不能由旧披露直接推出。'
o['assessment']['text']='先核查600下探Yes、再核查660上触Yes，依据是机制匹配、价差和顶档深度；不是预期收益排序。两档均watch，首个复核窗口11月2—10日。'
r['limitations'][0]['text']='尚缺方法透明的首次触及参考类/期权分布，无法判断独立胜率能否超过含费门槛，因此本轮未确认可成交优势。'
r['title']='META十一月：投入压力仍在，触及合约先核成本'
save('report.json',r);save('claims.json',c)
review={'status':'completed_with_findings_addressed','independent_reviewer':'touyan:red-team','analysis_checks':{'method':'pass','discrimination':'fail_in_original_T3_design; limitation retained; original outcomes frozen, no retrospective rewrite; next observations corrected','models':'pass_for_nonapplicability_and_spot_checked_arithmetic; no independent execution','market':'pass_for_cost_evaluation_only'},'value_checks':{'variant_edge':'original direction proxy failed; replaced with cost-only proxy','catalyst_timing':'pass_with_two_original_checks','price_payoff':'pass','ranking':'pass_as_research_order_only','failure_triggers':'pass_with_specific_observations_added','update_review':'not_applicable_first_run'},'findings':[{'severity':'material','target':'direction','problem':'Old capex disclosures and negative FCF do not alone establish November incremental downside; all capex not identifiable as AI','disposition':'Conditional downside scenario, acknowledged realized decline, capital expenditure wording corrected'},{'severity':'material','target':'market direction proxy','problem':'Different barrier distances confound direction inference','disposition':'Removed directional reading from claims, market and opportunity; cost proxy only'},{'severity':'material','target':'T2/T3 discrimination','problem':'T3 predictions coexist; next observations copied across tests','disposition':'Preserved frozen outcomes, explicitly marked T3 no discrimination; no supports/weakens; tailored observations and next-run redesign'},{'severity':'minor','target':'100-share theoretical fees and dominance','problem':'Top depth often below100; dominance quantity bounded','disposition':'Relabeled theoretical unit cost, retained depth and limited coverage to common visible quantity'},{'severity':'minor','target':'ranking expression','problem':'Research order could be confused with expected return ranking','disposition':'Added spread/depth reasoning in answer and table; no confirmed edge'}],'verification_scope':'Reviewer independently opened Meta IR and BLS; did not re-fetch CLOB/fees or execute code; no claim that revised draft independently re-reviewed.'}
save('review.json',review); a['review']=review
a['execution'] += [{'command':'sources.py validate/select + check_claims corrected','exit_code':0,'log':'evidence/verification-log.json'},{'command':'analysis_contract.py check initial','exit_code':0,'log':'evidence/verification-log.json'},{'command':'render_report.py initial','exit_code':0,'log':'evidence/verification-log.json'},{'command':'package_reports.py','exit_code':0,'reason':'同源Markdown/HTML仅搬移计算和价格评估至附录，不增删主张。'}]
a['remaining_method_gap']='T3 original scenario predictions were not mutually distinguishing; preserved original plan, explicitly no conclusion from T3. A later run must redesign this test instead of rewriting frozen predictions.'
save('audit.json',a)
print('Applied independent-review corrections; original T3 design limitation retained transparently.')
