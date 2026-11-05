from pathlib import Path
import json
from html import escape

root = Path(__file__).parent
out = root / 'reading-sample'
out.mkdir(exist_ok=True)
raw = json.loads((root / 'run-0.1.1/evidence/price-snapshot.json').read_text())
rows = [raw['previous_month_close']] + raw['rows']
w, h = 1100, 1230
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">' + '<title id="title">英伟达研究简报阅读样例</title><desc id="desc">股价日线、三个重点数字、两个业务观察信号和下一步验证条件。数据来自已有研究材料。</desc><rect width="1100" height="1230" fill="#fcfcfb"/><style>text{font-family:"PingFang SC","Heiti SC",sans-serif;fill:#0b0b0b}.muted{fill:#52514e}.small{font-size:15px}.body{font-size:21px}.title{font-size:37px;font-weight:600}.label{font-size:18px}.num{font-size:44px;font-weight:600}</style>']
def text(x,y,s,cls='body'):
    parts.append(f'<text x="{x}" y="{y}" class="{cls}">{escape(s)}</text>')
def line(y):
    parts.append(f'<line x1="55" y1="{y}" x2="1045" y2="{y}" stroke="#deded9"/>')
text(55,44,'投研助手 / 阅读样例 · 2026-10-31 · 基于已采集材料','small muted')
text(55,104,'收入预期仍增长，市场为何回撤？','title')
text(55,148,'优先检验：市场是否开始更重视 AI 投入回报与增长的现金转化。')
text(55,180,'这是研究判断；现有材料对整月跌幅的解释仍不充分。','label muted')
line(207)
for x,label,val,sub in [(55,'10 月累计价格变化','−10.39%','9/30 收盘 → 10/30 收盘'),(400,'月内最高收盘至月末','−14.46%','10/6 收盘 → 10/30 收盘'),(745,'Q3 收入指引中点环比','约 +12.3%','管理层预期，尚待财报兑现')]:
    text(x,245,label,'label muted');text(x,298,val,'num');text(x,330,sub,'small muted')
text(55,385,'NVDA 日收盘价：10 月先涨后跌','body')
text(55,412,'美元 / 价格收益，不含股息','small muted')
x0,x1,y0,y1=105,1005,455,650
for value in [200,220,240]:
    yy=y1-(value-195)/50*(y1-y0)
    parts.append(f'<line x1="{x0}" y1="{yy}" x2="{x1}" y2="{yy}" stroke="#e9e9e4"/>');text(58,yy+5,str(value),'small muted')
coords=[(x0+i/(len(rows)-1)*(x1-x0),y1-(r['close']-195)/50*(y1-y0)) for i,r in enumerate(rows)]
parts.append('<polyline fill="none" stroke="#2a78d6" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in coords)+'"/>')
peak=max(range(len(rows)),key=lambda i:rows[i]['close'])
for i in [0,peak,len(rows)-1]:
    x,y=coords[i];parts.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#2a78d6" stroke="#fcfcfb" stroke-width="2"/>')
    tx=x-85 if i==len(rows)-1 else x+8
    text(tx,y-13,f"{rows[i]['close']:.2f}",'small')
for i,label in [(0,'9/30'),(peak,'10/6'),(len(rows)-1,'10/30')]:text(coords[i][0]-20,680,label,'small muted')
line(709)
text(55,750,'两个最值得追踪的业务信号','body')
text(55,790,'01  收入目标上升，毛利率目标下降','body')
text(95,822,'Q3 收入指引 1,080 亿美元 ±2%；毛利率指引约 74%，Q2 为 75%。','label muted')
text(95,851,'要看新增收入能带来多少利润，以及后续指引能否继续增强。','label muted')
text(55,894,'02  高增长之外，还要检查现金回收','body')
text(95,926,'Q2 经营现金流 240.77 亿美元；应收变动占用现金 223.46 亿美元。','label muted')
text(95,955,'要看下一季现金转化是否改善；这些旧季数字没有确认 10 月订单变化。','label muted')
line(982)
text(55,1021,'下一份财报怎样改变判断？','body')
text(55,1060,'担忧减弱：收入兑现、现金回收改善、后续指引增强。','label')
text(55,1093,'担忧增强：增长伴随应收继续攀升、现金转化持续走弱。','label')
line(1118)
text(55,1150,'来源：FT/LSEG 与 Yahoo 历史行情；NVIDIA FY2027 Q2 官方财报。','small muted')
text(55,1176,'核心缺口：尚缺可靠估值及分析师预期，未完成整月下跌归因。','small muted')
text(55,1202,'表达样例，不是新增研究；逐日数据、来源链接和口径见配套说明。','small muted')
parts.append('</svg>')
(out/'nvda-reading-sample.svg').write_text(''.join(parts))
md=['# 阅读样例：数据与口径','本图是对已归档研究的重新组织，没有新增检索，也没有修改两版原报告。标题下的优先解释为待验证研究判断。','来源：[历史行情](https://markets.ft.markitdigital.com/data/equities/tearsheet/historical?s=NVDA%3ANSQ)、[Yahoo](https://finance.yahoo.com/quote/NVDA/history/)、[官方财报](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027)。','行情来自旧版已保存提取表；官方财务数字来自新版证据账本 C3、C4、C11。月度价格收益从前月末收盘计算，月内回撤从最高收盘计算，均不含股息。没有在价格图上标记新闻为跌幅原因。','\n| 日期 | 收盘价（美元） |\n|---|---:|']
md += [f"| {r['date']} | {r['close']:.2f} |" for r in rows]
(out/'data-and-sources.md').write_text('\n\n'.join(md[:4])+'\n'+'\n'.join(md[4:]))
print(out/'nvda-reading-sample.svg')
