# -*- coding: utf-8 -*-
import json
from pathlib import Path
P=Path('/Users/frankzhang/Desktop/投研助手/journal'); f=P/'tmp-claims.json'; d=json.loads(f.read_text()); c={x['id']:x for x in d['claims']}
c['C23']['text']='研究判断：已核查的四家大型平台有经营盈利基础，资本支出压低部分平台当期自由现金流；AI支出的独立影响及统一现金转换率变化尚未量化，不能据此证明整个NDX的经营质量。未取得10月30日同口径正常化盈利与估值，当前价格吸引力未被证明，也不能据此断言高估。'
c['C7']['type']='fact'; c['C7'].pop('basis',None); c['C7']['sources']=[dict(url='https://www.sec.gov/Archives/edgar/data/1652044/000165204426000080/googexhibit991q32026.htm',publisher='Alphabet',tier='T0',published_at='2026-10-28',quote='Other income (expense), net; year-to-date other income approximately $127.5 billion; quarter other expense approximately $8.2 billion'),dict(url='https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Third-Quarter-Results/',publisher='Amazon',tier='T0',published_at='2026-10-29',quote='Year to date total non-operating income $68.171 billion')]
c['C7']['text']+=' 非经营净收益不全等于应剔除投资收益，也未证明某个forward PE已受这些项目影响；需核实预测盈利是否已调整。'
c['C25']['text']='无概率观察契约：H1按2028年度官方现金流表，Amazon和Alphabet经营现金流减毛额现金购置物业设备均为正，任一家不为正则否，核验2029-04-30；出售激励不加回，租赁本金单列。H3比较2027-12-31生效的同减免费率口径，QQQM费用率仍低于QQQ，否则否，核验2028-01-31；缺少资料或基金终止void。H2正常化每份指数盈利五年复合增长10%因尚无锁定提供者及2026基值，无法裁决，不登记概率或预测。'
c['C9']['text']+=' 这不意味着指数盈利会计重复计算；指数公司财务并非集团合并报表，不能直接抵销供应商收入与客户投资。'
c['C10']['text']+=' 基准是中间外生参数组合，不表示最大概率；指数换股与每份盈利口径变化须另行处理。'
f.write_text(json.dumps(d,ensure_ascii=False,indent=2))
p=P/'tmp-memo.md'; t=p.read_text(); t=t.replace('NDX有值得长期研究的真实盈利基础，但目前只能确认经营质量，不能确认当前价格的安全边际；我的判断是“长期盈利逻辑成立，价格吸引力尚未被证据证明”，并不据此断言高估。','已核查的大型平台有真实经营盈利，但尚不足以证明整个NDX的质量或当前价格安全边际；我的判断是“增长机制值得认可，当前价格吸引力尚未被证据证明”，并不据此断言高估。')
t=t.replace('核心机制是把企业IT预算','已核查业务的核心机制是把企业IT预算')
t=t.replace('我的取舍是：长期盈利基础比“纯叙事”扎实，但新增AI投资的股东回报尚需现金回收证明。','我的取舍是：已核查平台的盈利具有业务基础，但新增AI投资的股东回报尚需现金回收证明。四家公司9月末合计权重19.06%，这不是盈利覆盖率；AI投入独立影响也未量化，不能从这些样本确认全指数质量。[C14][C23]')
t=t.replace('不能把其中一种增长率直接外推十年。','不能把其中一种增长率直接外推十年。非经营收益不全等于证券投资收益；在未核实预测调整前，也不能断言forward P/E受到相同污染或再次剔除。')
t=t.replace('持有产业链两端不自动消除共同需求风险。','持有产业链两端不自动消除共同需求风险。这也不意味着会计重复计算；指数公司财务不是集团合并报表，不能将供应商收入和客户投资直接抵销。')
t=t.replace('2029-03-31','2029-04-30').replace('Amazon与Alphabet各自2028年末TTM经营现金流减现金物业设备支出均为正，按各自可比官方口径','Amazon与Alphabet各自2028年度经营现金流减毛额现金购置物业设备均为正；出售和激励不加回，租赁本金另列')
t=t.replace('| H2 | 同一提供者、同一口径的2031年正常化每份NDX盈利，相对2026年复合增长至少10% | 2032-06-30 | 低于10%则否；无可比数据或无法还原指数盈利口径则void | 留空 |','| H2（未登记） | 2031年正常化每份NDX盈利相对2026年复合增长至少10%，作为研究条件 | 2032-06-30研究窗口 | 尚无预先锁定的提供者、定义及2026基值，当前无法裁决 | 留空 |')
t=t.replace('2027年末QQQM官方总费用率仍低于QQQ','2027-12-31生效、同减免费率口径的QQQM官方总费用率仍低于QQQ')
t=t.replace('H1检验现金回收，H2检验中间盈利假设，H3检验工具费率关系；','只登记H1与H3。H1检验现金设备支出后回收，未涵盖全部租赁负担；H2因契约缺口不登记，H3检验工具费率关系；')
t=t.replace('长期回报的关键分歧是AI投入后每份正常化盈利与现金回收能否增长到足以覆盖起点估值。','长期回报的关键分歧是每份正常化盈利与现金回收能否增长到足以覆盖起点估值。')
t=t.replace('NDX的经营价值有真实基础，','已核查平台有真实经营盈利，尚不足以证明整个指数质量；')
t=t.replace('因此，本研究认可长期盈利逻辑，但对当前价格不给出“有明显吸引力”的肯定评价。','因此，本研究认可长期增长机制的业务基础，但对当前价格不给出“有明显吸引力”的肯定评价。')
p.write_text(t)
m=dict(question=d['question'],type='asset',entity='Nasdaq-100 (NDX), QQQ',as_of=d['as_of'],market_snapshot=[],hypotheses=[dict(id='H1',text='Amazon与Alphabet 2028年度经营现金流减毛额现金购置物业设备均为正；出售和激励不加回，租赁本金另列',verify_by='2029-04-30',measurement_date='2028-12-31',falsify_if='任一家OCF减毛额现金物业设备支出小于或等于零则miss；官方资料缺失无法还原则void，不视为支持',resolution_source='两家公司2028年度官方现金流量表及年度SEC文件',my_prob=None,market_prob=None,authors=[]),dict(id='H3',text='2027-12-31生效且同减免口径的QQQM总费用率低于QQQ',verify_by='2028-01-31',measurement_date='2027-12-31',falsify_if='QQQM费率大于或等于QQQ则miss；基金终止或官方资料缺失则void',resolution_source='Invesco两只基金年末有效招募说明书及费率表',my_prob=None,market_prob=None,authors=[])],probability_status='not_calibrated_null_user_authorized',excluded_hypotheses=[dict(id='H2',reason='尚无可比正常化盈利提供者和锁定2026基值，无法裁决')])
(P/'tmp-memo.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
