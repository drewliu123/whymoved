import json
from pathlib import Path
P=Path('/Users/frankzhang/Desktop/投研助手/journal'); A='2026-10-31T15:15:05Z'
cs=[]
def add(i,text,typ='fact',url=None,pub=None,date='unknown',basis=None,quote=None):
 c=dict(id=i,text=text,type=typ,as_of=A,sources=[])
 if url:c['sources']=[dict(url=url,publisher=pub,tier='T4' if typ=='view' else 'T0',published_at=date,quote=quote or text)]
 if basis:c['basis']=basis
 cs.append(c)
add('C1','研究截面为2026-10-31；Nasdaq交易日历显示10月30日为正常交易日，因此最新已完成交易日为2026-10-30。',url='https://www.nasdaq.com/market-activity/stock-market-holiday-schedule',pub='Nasdaq')
add('C2','Nasdaq历史页标注DATA AS OF 10/30/2026，显示NDX 28,384.85；但同时显示前收也是28,384.85、涨跌-1,000.42及0.00%，彼此不一致，且没有可读历史收盘行。该数只能作为页面展示值，不作已核实正式收盘价或收益率依据。','price','https://indexes.nasdaq.com/Index/History/NDX','Nasdaq')
e=json.loads((P/'tmp-company-evidence.json').read_text())['evidence']
texts=[('C3','微软截至2026-09-30季度收入922.79亿美元、经营利润459.15亿美元、Azure收入331.65亿美元同比增长48%；经营现金流580.00亿美元、现金购置物业设备393.67亿美元。现金capex不包含全部融资租赁新增资产。'),('C4','Alphabet 2026Q3收入1,275.77亿美元、经营利润405.76亿美元；Services收入963亿美元同比增长11%，Cloud收入307亿美元同比增长103%且含TPU硬件销售；经营现金流422.90亿美元、资本开支513.55亿美元、自由现金流-90.65亿美元，过去十二个月自由现金流197.47亿美元。'),('C5','Amazon 2026Q3 AWS收入459.84亿美元同比增长39.3%，AWS经营利润177.73亿美元，公司经营利润280.76亿美元；过去十二个月经营现金流1,683.00亿美元、扣出售及激励后的物业设备支出2,106.57亿美元、自由现金流-423.57亿美元；2026现金资本开支约2,200亿美元为管理层指引。'),('C6','Meta 2026Q3收入646.01亿美元，其中广告630.61亿美元；经营利润129.88亿美元含98.9亿美元诉讼费用；经营现金流327.86亿美元，含融资租赁本金支付的资本开支349.06亿美元，自由现金流-21.20亿美元；全年资本开支1,350–1,450亿美元为指引。')]
for (i,t),s in zip(texts,e):add(i,t,url=s['url'],pub=s['publisher'],date=s['published_at'],quote=s['quote'])
add('C7','Alphabet季度证券投资损失与年内累计巨额非经营收入方向不同；2026年前九个月损益表Other income net为1,275亿美元左右，Amazon同期非经营净收益681.71亿美元。不能把GAAP盈利增速直接视为可持续经营盈利增速。','inference',basis=['C4','C5'])
add('C8','云计算、企业软件订阅、搜索及社交广告已经产生经营盈利，AI增长可通过算力销售、云消费、软件收费和广告转化兑现；但四家公司收入与现金开支不同步，不能从云收入增长推导指数自由现金流同比例增长。','inference',basis=['C3','C4','C5','C6'])
add('C9','共同风险机制：指数内算力供应商的收入可能对应云厂商的资本开支，同一笔产业支出在指数内部兼具收入和投资；终端付费不足会同时影响供应商订单与平台投资回报。折旧、能源约束、竞争降价、监管和利率变化均须作为压力情景，而非已经发生的损失。','inference',basis=['C3','C4','C5','C6'])
add('C10','十年价格回报敏感性采用 r=(1+g)*(退出PE/起点PE)^(1/10)-1，盈利必须采用同口径正常化每份盈利，既不混用forward/TTM也不把收入增速代入。起点PE25/30/35/40为假设网格而非当前估值。乐观g15%退出32倍，年化价格回报17.87%/15.75%/13.97%/12.46%；基准g10%退出25倍为10.00%/8.01%/6.36%/4.95%；悲观g4%退出20倍为1.71%/-0.13%/-1.66%/-2.96%。不含分红、基金费、税和汇率；概率均留空。','inference',basis=['C8','C9'])
add('C11','若要求十年价格年回报8%、退出25倍，同口径起点PE25/30/35/40要求每份盈利年增8.00%/9.99%/11.70%/13.20%。这是反推条件，不是对实际市场预期或概率的观测。','inference',basis=['C10'])
add('C12','r/investing相关帖子中cloud7100评论质疑在广泛股票敞口之外继续增加大型科技集中风险；r/stocks另一个帖子里Picks6x担心巨额AI开支能否盈利，CornerOne238则质疑增加芯片支出时抛售芯片股。仅两个帖子，评论时间和截面互动量未独立核实，不能概括投资者总体情绪。','view','https://www.reddit.com/r/investing/comments/1xi4res/does_anyone_put_all_their_money_is_the_nasdaq_100/','Reddit',quote='I don’t think anyone has thought “Gee, S&P500 doesn’t have enough big tech stocks in 2026.”')
cs[-1]['sources'].append(dict(url='https://www.reddit.com/r/stocks/comments/1xjqpj8/stock_market_rocked_as_investors_dump_tech_shares/',publisher='Reddit',tier='T4',published_at='2026-10-30',quote="It's like investors hate not knowing if insane spending is going to be profitable or not."))
(P/'tmp-claims.json').write_text(json.dumps(dict(question='NDX中长期投资价值，QQQ工具参照',as_of=A,claims=cs),ensure_ascii=False,indent=2))
