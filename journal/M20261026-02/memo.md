投研助手 · event_pricing · How many dissent at the October Fed meeting · 截面 2026-10-26T06:59Z

一句话：逐人研究得到的反对票分布（0 票 22%、1 票 17%、2 票 34%、3 票 24%）与盘口基本一致，没有找到可靠的错价。结果主要取决于两个人：Hammack 是否反对，决定是 0 票还是至少 1 票；Kashkari 是否跟着反对，决定是 2 票还是 3 票。起草时得出的“盘口高估 2 票”，在反方审查后撤回。

**定价与对标**
- 市场定价：[Polymarket](https://polymarket.com/event/how-many-dissent-at-the-october-fed-meeting) 2 票 27.5%、0 票 26.5%、3 票 22%、1 票 14.5%、4 票及以上 4.4%（合计 94.9%）；0 票一个月内下跌 18 个百分点 [D1]
- 交叉定价：[Kalshi 票数](https://api.elections.kalshi.com/trade-api/v2/events?series_ticker=KXFOMCDISSENTCOUNT&with_nested_markets=true&status=open)：2 票 0.30、0 票 0.22、1 票 0.21、3 票 0.20 [D2]；[Kalshi 逐人](https://api.elections.kalshi.com/trade-api/v2/events?series_ticker=KXFEDDISSENT&with_nested_markets=true&status=open)最后成交价：Hammack 0.74、Logan 0.43、Kashkari 0.36 [D3]，买卖价快照：Logan 0.60/0.61、Kashkari 0.13/0.39 [D3b]
- 历史基准：2026 年的反对票数：1 月 2 票、3 月 1 票、4 月 4 票、6 月 0 票、7 月 3 票、9 月 0 票 [D5、D6、D7]
- 结算口径：只计对利率决定的反对票，以会后声明为准（[Gamma](https://gamma-api.polymarket.com/events?slug=how-many-dissent-at-the-october-fed-meeting)）[D14]

**发生了什么**
- 2026 年票委：理事 Warsh、Barr、Bowman、Cook、Jefferson、Powell、Waller；纽约联储 Williams；轮值主席 Hammack、Kashkari、Logan、Paulson（[Fed](https://www.federalreserve.gov/monetarypolicy/fomc.htm)）[D4]
- 4/29 Hammack、Kashkari、Logan 支持维持利率，但反对声明中的宽松措辞（[声明](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260429a.htm)）[D6]
- 7/29 以 9 比 3 维持利率，上述三人主张加息 25bp（[声明](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm)）[D5]
- 9/16 以 12 比 0 加息 25bp；纪要显示与会者全部支持这次加息，并认为年底前很可能还要再加一次（[纪要](https://www.federalreserve.gov/monetarypolicy/fomcminutes20260916.htm)）[D7、D15]
- 9/29 Williams 说没有紧迫性；10/8 Waller 说加息不必连续进行（[Williams](https://www.newyorkfed.org/newsevents/speeches/2026/wil260929)、[Waller](https://www.federalreserve.gov/newsevents/speech/waller20261008a.htm)）[D11]
- 10/1 Logan 估计还需要再加 50bp 或更多，没有说明是哪次会议（[讲话](https://www.dallasfed.org/news/speeches/logan/2026/lkl261001)）[D9]
- 10/12 Hammack 表示倾向小幅调整，而不是等待之后再做更大的纠正；没有点名 10 月（[讲话](https://www.clevelandfed.org/collections/speeches/2026/sp-20261012-trimming-the-sails-communicating-my-reaction-function)）[D8]
- Kashkari 能找到的最后一次表态是 7 月“渐进收紧”的反对理由；9/30 的活动没有文字稿（[声明](https://www.minneapolisfed.org/article/2026/statement-on-my-fomc-dissent)）[D10]
- Barr、Paulson 认为还可能需要收紧，但都没给出时点 [D12]
- 先例：2025 年 Bowman、Waller 7 月投了反对票，9 月诉求被满足后都投了赞成票 [D16]

**市场在想什么**
- Bloomberg 视频标题称 Bowman 认为不急于进一步行动（只有标题）[D13]
- 社区层：community-scout 在登记前没有返回，本备忘录没有社区信号（见证据缺口）

**分歧与推断**
- 三人在 2026 年唯一一次利率反对中同时反对，4 月又同时就声明措辞反对。同时反对的样本只有 2 次，说明他们有共同的驱动因素，但估计不了相关系数 [I1，依据 D5、D6、D7]
- 用 Kalshi 逐人中间价、按三人完全同向计算，得到 21/15/31/27，与两家平台的票数盘口大体一致。也就是说，盘口已经反映了“三人高度相关、但概率各不相同” [I5，依据 D1、D2、D3、D3b]
- 证据支持市场把 Logan 排在 Kashkari 前面：Logan 仍要求再加至少 50bp，而 Kashkari 主张的渐进收紧在 9 月已经得到满足 [I6，依据 D9、D10、D15、D16]
- 按修正后的逐人概率（Hammack 0.70、Logan 0.60、Kashkari 0.25）、在保持各人概率不变的前提下计算，结果为 0 票 19%–26%、1 票 12%–21%、2 票 32%–36%、3 票 22%–26%，各档与盘口的差距都不超过 7 个百分点 [I3]
- 如果鹰派像 4 月那样只反对措辞，这种反对不计入结算，结果仍是 0 票 [I4，依据 D6、D14]

**值得研究的假设**
| 编号 | 假设 | 本助手 / 市场 | 验证时间点 | 证伪条件 |
|---|---|---|---|---|
| H1 | Hammack 对利率决定投反对票 | 0.70 / 0.74 | 2026-10-28 | 声明中她投了赞成；会前信号：Kalshi 中间价跌破 0.50 |
| H2 | Kashkari 对利率决定投反对票 | 0.25 / 0.26 | 2026-10-28 | 声明中他投了反对；会前信号：Kalshi 中间价升破 0.40 |
| H3 | 恰好 2 票反对 | 0.34 / 0.29 | 2026-10-28 | 声明中的反对票不是 2 票 |
| H4 | 0 票反对 | 0.22 / 0.28 | 2026-10-28 | 声明中有任何一张对利率决定的反对票 |

另有一个结构性观察，不登记概率：如果 Kashkari 反对，Hammack 和 Logan 应该也都反对。10/28 的声明可以直接验证这一点。

**反方**（来自 red-team）
- 起草时我用了“阵营共用一枚硬币”的模型，它会把三人的概率拉成同一个平均值，导致“2 票只有 8%–16%”的结论与我自己给的逐人概率矛盾。改用保持各人概率不变的方法后，这个结论撤回。
- 起草时我认为“两组盘口不一致”，用的是过期成交价。改用中间价后，两组盘口基本自洽。
- 6 次会议的一致性里，有 4 次是全员一致，对“三人特有的相关性”没有信息量。
- 逐人概率可能偏高：6 月同样是维持利率，三人却没有反对。可见只要前瞻指引够鹰，他们可以接受等待；9 月纪要已经暗示年底前还会再加一次。
- Kalshi 逐人合约是否也计入“措辞反对”，没有核实。如果口径不同，两组价格不能直接对比。

**证据缺口**
- Kashkari 在 9 月加息后没有可核实的原话；Bowman 只有视频标题。
- Reuters、WSJ、FT 无法访问；Bloomberg、CNBC 的正文返回 403。
- 社区层（community-scout）在登记前没有返回。
- 没有利率期货对 10 月加息的定价。如果 10 月意外加息，鹰派就不会反对，但这一档的概率账本里没有。
- 没有找到“鹰派诉求刚被满足、紧接着下一次会议又反对”的先例。

本备忘录是研究材料，不构成投资建议。
