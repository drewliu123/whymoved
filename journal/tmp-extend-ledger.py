# -*- coding: utf-8 -*-
import json
from pathlib import Path
P=Path('/Users/frankzhang/Desktop/投研助手/journal'); d=json.loads((P/'tmp-claims.json').read_text()); a=d['as_of']; cs=d['claims']; cs[-1]['text']=cs[-1]['text'].replace('广泛股票敞口','其他股票指数敞口')
def add(i,text,url=None,pub='Nasdaq',basis=None,date='unknown',typ='fact'):
 c=dict(id=i,text=text,type='inference' if basis else typ,as_of=a,sources=[])
 if url:c['sources']=[dict(url=url,publisher=pub,tier='T0',published_at=date)]
 if basis:c['basis']=basis
 cs.append(c)
f='https://indexes.nasdaq.com/docs/FS_NDX.pdf'; q='https://www.invesco.com/content/dam/invesco/us/en/product-documents/etf/fact-sheet/qqq-invesco-qqq-etf-fact-sheet.pdf'; m='https://indexes.nasdaqomx.com/docs/Methodology_NDX_Effective_May_1_2026.pdf'; v='https://www.invesco.com/us-rest/contentdetail?contentId=3bb2c37291215710VgnVCM1000006e36b50aRCRD&dnsName=us'
add('C13','Nasdaq-100选取100家大型Nasdaq上市非金融公司，采用修正市值加权；2026-05-01生效方法规定季度再平衡，年度重构于12月第三个周五后首个交易日开盘生效。未独立核实其后是否又有方法修订。',m)
add('C14','Nasdaq官方factsheet截至2026-09-30：NVDA8.36%、AAPL7.38%、MSFT5.78%、MU5.04%、AMD4.19%、AMZN4.08%、META3.27%、GOOGL3.07%、GOOG2.86%、TSLA2.83%；Technology68.01%、Consumer Discretionary15.14%。这是9月末权重，不是10月30日。',f)
add('C15','上述十大证券权重合计46.86%，Alphabet两股类合计5.93%；十条证券对应九家公司。NVDA、MU、AMD合计17.59%仅是这三家权重，不是全部半导体行业权重。权重不等同于盈利贡献权重。',basis=['C14'])
add('C16','NDX是价格回报版本，XNDX是总回报版本，XNDXNNR为净总回报版本。基金含分红回报不能直接与NDX价格回报比较。',f)
add('C17','Invesco文件说明Nasdaq Composite Total Return覆盖Nasdaq市场境内外普通股；其范围与100家大型非金融公司的NDX不同。该官方PDF URL文件名含QQQ，但本次取得正文标题与ticker为QQQM，按正文身份归属。',q,'Invesco')
add('C18','Invesco官网列示QQQ总费用率0.18%；2025-12-22官方说明费用由0.20%降至0.18%，并介绍open-ended ETF结构转换。完整转换生效记录本次未取得，因此不沿用旧UIT限制描述。','https://www.invesco.com/qqq-etf/en/performance.html','Invesco')
cs[-1]['sources'].append(dict(url='https://www.invesco.com/qqq-etf/en/market-outlook/whats-new-about-qqq.html',publisher='Invesco',tier='T0',published_at='2025-12-22'))
add('C19','QQQM官方截至2026-09-30资料列示总费用率0.15%；按两只基金公示费率差0.03个百分点计算，每10,000美元资产每年费用差约3美元，实际取决于净值路径。',v,'Invesco')
add('C20','官方PDF实际正文QQQM截至2026-09-30列示P/E29.48、P/B9.91、ROE34.54%；仅写P/E ratio，未取得forward/TTM、亏损公司处理及加权方法定义。该P/E不是已核实10月30日NDX估值，也不能与未核实的历史远期PE直接比较。',q,'Invesco')
add('C21','QQQM截至2026-09-30同表：一年NAV总回报23.79%、市场价格回报23.85%、指数24.00%；五年年化NAV16.40%、市场价格16.36%、指数16.56%。另一官方正文注明基准XNDX，市场回报采用美东16时买卖报价中点。',v,'Invesco')
add('C22','上述QQQM NAV相对指数一年差-0.21个百分点，五年年化差-0.16个百分点。这是已实现跟踪差异，不是跟踪误差的波动率，也不是QQQ本身的跟踪记录。NAV、交易价格、总回报须分别比较。',basis=['C16','C21'])
add('C23','当前研究判断：NDX拥有可验证的经营盈利基础，但AI投入正压低部分平台现金转换率；在未取得10月30日同口径正常化盈利与估值前，不能确认当前价格存在安全边际，也不能仅凭科技集中度断言当前估值过高。质量逻辑成立，价格吸引力尚未被证据证明。',basis=['C3','C4','C5','C6','C9','C14','C20'])
add('C24','反方检验：投入期自由现金流下降可能是在建设未来盈利资产，不自动意味着毁损价值；若新增经营现金流持续覆盖新增支出且每份正常化盈利增长，现金流担忧应被下调。反之，延长折旧年限或投资收益抬高EPS不能替代终端客户付费和现金回收。',basis=['C3','C4','C5','C6','C7'])
add('C25','研究观察契约而非统计预测：H1截至2028年末Amazon和Alphabet公布的2028年末TTM经营现金流减现金购置设备口径FCF均为正；任一家不为正则否。H2在同一提供者披露可比2026与2031正常化每份指数盈利时，2031相对2026复合增长至少10%；若口径或样本不可比则void。H3两基金2027年末官方QQQM费用率仍低于QQQ；若相等或反转则否。三项概率留空；不能把本文估值情景变成已校准概率。',basis=['C4','C5','C10','C18','C19'])
add('C26','QQQ与QQQM都是指数实施工具，费用降低净回报；现金分红是总回报的一部分，除息时不能把现金到账视为额外创造收益。价格偏离NAV、交易价差及税费影响实际结果，基金费用不是跟踪差异的唯一来源。固定回报测算不应重复扣除已在净值中计提的管理费。',basis=['C16','C18','C19','C21','C22'])
(P/'tmp-claims.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
