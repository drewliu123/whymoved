# Polymarket中国10月CPI：28¢的0\.9%\-1\.0%档值得优先核查

Polymarket的October Inflation China \- Annual应如何按规则及当前价格评估各选项？

研究截点 2026\-11\-02T07:54:08\.603270\+00:00 · event\_pricing · 结算规则、盘口与概率价格差研究

## 判断

按这份Polymarket合约，当前最值得优先核查的是0\.9%\-1\.0%档28¢的YES：前轮0\.9%基准落在这一档，含费胜率门槛约29\.0%。0\.7%\-0\.8%是盘口最热门档，YES卖价50¢、含费门槛约51\.25%。现有材料尚不能把0\.9%点预测转换成可靠分档胜率，因此判断是优先研究第三档，暂未验证正期望。 [C22] [C23]

优先研究：第三档28¢优先研究：与0\.9%基准一致且门槛低于第二档，但没有概率误差校准，不称已验证错价。 [C23] [C25]

## 先看结算档位：0\.8与0\.9差一个结算结果

合约为October Inflation China \- Annual，2026年10月全国CPI同比，以国家统计局10月CPI月报Growth Rate Y/Y \(%\)的一位小数官方数字结算。五档为≤0\.6%、0\.7%\-0\.8%、0\.9%\-1\.0%、1\.1%\-1\.2%、≥1\.3%；0\.8归第二档，0\.9归第三档，1\.0仍归第三档，1\.1归第四档。若到下个月数据计划发布日期仍未发布指定月份数据，按最后可得月份结算。规则未另写随后修订的处理，不能自行追加规则。 [C20]

为什么重要：0\.9%的点预测只定位第三档，不能证明第三档胜率；应直接预测官方公布值落在哪档。

## 28¢与50¢对应不同的胜率门槛

市场最热的0\.7%\-0\.8%档YES卖价50¢，而0\.9%\-1\.0%档YES卖价28¢。按合约经济类taker费率，后者每份等价成本约29\.008¢，必须认为该档胜率高于约29\.0%才有正期望；0\.7%\-0\.8%档50¢买入的门槛约51\.25%。这些是成本门槛，不是研究胜率。各档更新时间不同，不能将盘口相加宣称套利。 [C22]

为什么重要：最可能的档位也可能价格过高，较低胜率的档位也可能存在价格优势。

## 顶档深度限制实际成本

0\.9%\-1\.0% YES的28¢顶档仅118\.43份，下一档37¢共61\.03份；28¢档名义金额约33\.16美元。若继续吃到37¢，该部分含费等价成本约38\.17¢。按当前可见盘口买100份需28美元，立即卖出时80份按21¢、20份按17¢，共收回20\.20美元，价格损失7\.80美元，另计费用；若最后不落该区间，持有至结算的YES价值为零。 [C24]

为什么重要：买入超过顶档会显著提高成本；结算前价差也影响退出。

## 有研究分歧，尚无经验证的概率优势

研究优先看0\.9%\-1\.0%档28¢的YES，而非直接将0\.9%的点预测视为高胜率。它与前轮0\.9%基准一致，但现有0\.7%\-1\.1%只是情景范围，没有校准概率，不能据此断言该档胜率超过29%。当前属于有分歧可研究，未证实正期望；需要验证食品走弱是否足以把结果压到0\.7%\-0\.8%或更低。 [C23]

为什么重要：下一项研究应估计≤0\.8%与0\.9%\-1\.0%的概率，而非重复CPI点预测。

## 分析判断

传导关系：10月分项价格 → 官方CPI一位小数同比 → 五档结算映射 → 可成交价格及费用 → 预期收益门槛

模型不适用：四种固定公司经营或估值模型不适合本题；费用与盈亏平衡手工公式由脚本计算存档，不宣称校准概率模型。

### 价格要求什么，研究判断有什么不同

隐含预期：第二档50¢最热门，第三档28¢；含费门槛分别51\.25%、29\.008%，仅是报价对应成本门槛。 [P0Yes] [P0No] [P1Yes] [P1No] [P2Yes] [P2No] [P3Yes] [P3No] [P4Yes] [C22] [C23] [C24] [C25]

研究假设：前轮点预测0\.9%落第三档，但未形成可校准分档概率。 [P0Yes] [P0No] [P1Yes] [P1No] [P2Yes] [P2No] [P3Yes] [P3No] [P4Yes] [C22] [C23] [C24] [C25]

差异：有方向分歧，不能量化为已验证概率价差。 [P0Yes] [P0No] [P1Yes] [P1No] [P2Yes] [P2No] [P3Yes] [P3No] [P4Yes] [C22] [C23] [C24] [C25]

改变判断的条件：研究价格条件：0\.9%\-1\.0% YES在28¢附近时，仅当独立判断该档胜率超过29\.0%且有额外误差余量才具正期望；若成本升至37¢，门槛升至约38\.17%。食品全月数据证实走弱到足以使公布同比≤0\.8%，将削弱这条候选；若不能建立分档概率优势，维持观察。 [P0Yes] [P0No] [P1Yes] [P1No] [P2Yes] [P2No] [P3Yes] [P3No] [P4Yes] [C22] [C23] [C24] [C25]

### 盘口快照与YES含费盈亏平衡门槛

| 官方公布值档位 | YES最佳买价$ | YES最佳卖价$ | 卖价顶档份数 | 含费门槛% |
| --- | --- | --- | --- | --- |
| ≤0\.6% | 0\.2 | 0\.269 | 100 | 27\.883 |
| 0\.7% to 0\.8% | 0\.44 | 0\.5 | 64 | 51\.25 |
| 0\.9% to 1\.0% | 0\.21 | 0\.28 | 118\.43 | 29\.008 |
| 1\.1% to 1\.2% | 0\.015 | 0\.08 | 69\.96 | 8\.368 |
| 1\.3%\+ | 无 | 0\.001 | 890\.42 | 0\.105 |

[P0Yes] [P0No] [P1Yes] [P1No] [P2Yes] [P2No] [P3Yes] [P3No] [P4Yes] [C21] [C22]

抓取于2026\-11\-02T07:50:23\.527860\+00:00；各档盘口自身更新时间不同；最优报价不保证后续成交，门槛按USDC等价成本估算。

## 其他解释

### 食品下行解释市场偏向较低档位

前轮已有月初猪菜价格下跌线索，可能使0\.7%\-0\.8%或≤0\.6%成为合理结果；尚无完整全月权重贡献来判断其幅度。 [C9] [C11] [C23]

## 接下来观察什么

### 发布前补齐全月食品价格、能源和服务贡献及历史预测误差；重新核查第三档价格。

研究价格条件：0\.9%\-1\.0% YES在28¢附近时，仅当独立判断该档胜率超过29\.0%且有额外误差余量才具正期望；若成本升至37¢，门槛升至约38\.17%。食品全月数据证实走弱到足以使公布同比≤0\.8%，将削弱这条候选；若不能建立分档概率优势，维持观察。 [C25]

## 附录：机会判断与触发条件

市场押注：该事件盘口最热第二档YES50¢，第三档YES28¢；对应含费成本门槛51\.25%与29\.008%，不同于客观事件概率。（依据：价格隐含） [P0Yes] [P0No] [P1Yes] [P1No] [P2Yes] [P2No] [P3Yes] [P3No] [P4Yes] [C22]

我们的分歧：前轮0\.9%基准指向第三档，与第二档更热门形成待检验分歧。 [C8] [C22] [C23]

证据优势：新增优势是精确规则、价格与深度核对；现有宏观证据尚不足以证明独立概率优势。 [C20] [C23] [C24]

重估催化：官方2026年10月CPI发布，计划11月9日9:30北京时间；此前全月分项材料也可调整概率。；时间/到期：2026\-11\-09T09:30:00\+08:00 [C1] [C20] [C23]

剩余空间与做错代价：0\.9%\-1\.0% YES的28¢顶档仅118\.43份，下一档37¢共61\.03份；28¢档名义金额约33\.16美元。若继续吃到37¢，该部分含费等价成本约38\.17¢。按当前可见盘口买100份需28美元，立即卖出时80份按21¢、20份按17¢，共收回20\.20美元，价格损失7\.80美元，另计费用；若最后不落该区间，持有至结算的YES价值为零。 [C24]

### TR1 · 第三档可成交价格及独立概率判断是否满足含费门槛。

时间/到期：2026\-11\-09T09:30:00\+08:00；支持：28¢附近仍可成交，且独立分档概率可靠超过29%并有误差余量。；削弱：卖价升到37¢，需要约38\.17%胜率才能覆盖成本。；失效：全月证据支持≤0\.8%，或最终公布值不在0\.9%\-1\.0%。 [C25]

## 附录：相对原文与旧判断的增量

先看结算档位：0\.8与0\.9差一个结算结果；基线：前轮只有CPI数值预测。；增加的判断：加入官方公布精度、五档边界及延迟发布兜底规则。 [C20]

28¢与50¢对应不同的胜率门槛；基线：单看网页显示百分比或点预测。；增加的判断：用真实卖价与费用计算盈亏平衡门槛。 [C22]

顶档深度限制实际成本；基线：只看28¢标题价。；增加的判断：列出可见数量、下一档价格及错误情景损失。 [C24]

有研究分歧，尚无经验证的概率优势；基线：前轮0\.9%中心与0\.7%\-1\.1%情景。；增加的判断：明确点预测与可成交期望收益的差别，排序第三档优先。 [C23]

## 附录：分析底稿与可复算模型

方法：reference\_class\_scenarios；比较基准：Polymarket 2026年10月中国CPI五档合约与2026\-11\-02取得的盘口；前轮CPI点预测0\.9%。 [C8] [C20] [P0Yes] [P0No] [P1Yes] [P1No] [P2Yes] [P2No] [P3Yes] [P3No] [P4Yes]

### 候选解释

| 编号 | 解释 |
| --- | --- |
| H1 | 0\.9%\-1\.0%档28¢可能低估贴近0\.9%的发布结果。 |
| H2 | 食品走弱令0\.7%\-0\.8%甚至更低的区间更合理，28¢不构成错价。 |



### 区分性检验 T1

### 不同解释的事前预测

| 解释 | 预期观察 |
| --- | --- |
| H1 | 基数与全月贡献支持0\.9%\-1\.0%，概率高于含费门槛。 |
| H2 | 食品拖累支撑≤0\.8%，第三档概率不足含费门槛。 |



观察缺失：没有完整全月分项贡献与历史预测误差，不能把情景范围升级为校准分档概率。；尚不能裁定第三档是否正期望。 

支持：；削弱：

下一观察：全月数据与校准误差，或最终官方公布。；时间/触发：2026\-11\-09T09:30:00\+08:00；支持条件：独立证据使第三档概率可靠地超过含费门槛。；削弱条件：可靠预测指向≤0\.8%或第三档概率低于含费成本。

### 区分性检验 T2

### 不同解释的事前预测

| 解释 | 预期观察 |
| --- | --- |
| H1 | 第三档28¢可成交，概率门槛显著低于第二档。 |
| H2 | 第三档成本因价差滑点升高，或28¢可用深度不足以支持候选。 |



观察结果：第三档28¢确有118\.43份可见卖单，下一档37¢；识别研究价格而未证明概率优势。 [P0Yes] [P0No] [P1Yes] [P1No] [P2Yes] [P2No] [P3Yes] [P3No] [P4Yes]

支持：；削弱：

下一观察：下一次盘口更新及全月预测证据。；时间/触发：2026\-11\-02T07:54:08\.603270\+00:00；支持条件：28¢附近可执行且分档概率超过成本。；削弱条件：价格提高到37¢而预测概率未相应提高。

固定模型的数值已重算；来源含义、假设合理性与因果解释仍需研究审查。敏感性结果不是统计置信区间。

## 来源与结论审计

\[C1\] 国家统计局2026年日程表计划于11月9日星期一9:30发布居民消费价格月度报告，非PMI月度指标对应上月；日期为初步计划，可能调整。（fact；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S1

\[C2\] 国家统计局2026年10月14日发布的公告对应2026年9月，CPI同比上涨0\.9%，环比上涨0\.2%。（fact；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S2

\[C5\] Trading Economics日历列示2026年10月CPI同比模型预测为0\.9%，Consensus列未填写数值。（view；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S3

\[C6\] 2025年10月全国CPI环比上涨0\.2%。（fact；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S4

\[C7\] 以9月同比0\.9%和去年10月环比0\.2%为基数，假设2026年10月环比0\.2%，按\(1\+0\.009\)\*\(1\+0\.002\)/\(1\+0\.002\)\-1计算，10月同比为0\.9%；假设环比0\.0%或0\.4%，对应同比约0\.699%或1\.101%。这是滚动近似，发布值舍入、权重换基及链式指数口径会带来误差。（inference；2026\-11\-02T07:54:08\.603270\+00:00）

依据：C2, C6；来源：

\[C8\] 截至2026年11月2日，本轮对2026年10月全国CPI同比的中心预测为\+0\.9%，主要情景区间为\+0\.7%至\+1\.1%。依据为上一期0\.9%、同比滚动基数及TE同月0\.9%外部模型；尚未获得完整10月CPI分项贡献，因此是基准情景预测，没有已验证的独立预测优势。区间对应环比0\.0%至0\.4%的假设，并非经过回测校准的统计置信区间。（inference；2026\-11\-02T07:54:08\.603270\+00:00）

依据：C2, C5, C6, C7；来源：

\[C9\] 西南证券10月15日研报报告，截至10月13日，10月初猪肉环比下降2\.2%、28种蔬菜环比下降5\.9%；这是机构引述的局部批发高频，不是全月CPI食品分项。（view；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：F3

\[C10\] 发改委10月15日公告汽柴油不作调整；10月29日公告实际每吨上调汽油345元、柴油335元，自10月29日24时起生效。（fact；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：F1, F2

\[C11\] 月初猪菜价格走弱给中心0\.9%带来下行风险；月末成品油上调作用于10月的时间短，不能据此假设整月能源价格同步大涨。维持中心0\.9%及0\.7%\-1\.1%情景区间，食品零售传导和全月月均缺失限制进一步细化；没有理由仅凭月末油价把预测抬高到1\.1%以上。（inference；2026\-11\-02T07:54:08\.603270\+00:00）

依据：C8, C9, C10；来源：

\[C20\] 合约为October Inflation China \- Annual，2026年10月全国CPI同比，以国家统计局10月CPI月报Growth Rate Y/Y \(%\)的一位小数官方数字结算。五档为≤0\.6%、0\.7%\-0\.8%、0\.9%\-1\.0%、1\.1%\-1\.2%、≥1\.3%；0\.8归第二档，0\.9归第三档，1\.0仍归第三档，1\.1归第四档。若到下个月数据计划发布日期仍未发布指定月份数据，按最后可得月份结算。规则未另写随后修订的处理，不能自行追加规则。（fact；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S20

\[C21\] 该合约feeSchedule列示rate=0\.05、exponent=1、takerOnly=true、rebateRate=0\.25；官方费用公式fee=C×feeRate×p×\(1\-p\)，maker不收手续费。每份0\.28美元的taker费用USDC等价0\.01008，故不计额外滑点的等价成本0\.29008美元。（fact；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S21, S22

\[P0Yes\] ≤0\.6% Yes买入所需可见最佳卖价0\.269美元/份，顶档可见100份；盘口时间2026\-11\-02T07:41:41\.491000\+00:00。（price；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S5734060Yes

\[P0No\] ≤0\.6% No买入所需可见最佳卖价0\.8美元/份，顶档可见20份；盘口时间2026\-11\-02T07:41:41\.491000\+00:00。（price；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S5734060No

\[P1Yes\] 0\.7% to 0\.8% Yes买入所需可见最佳卖价0\.5美元/份，顶档可见64份；盘口时间2026\-11\-02T07:47:19\.779000\+00:00。（price；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S5734061Yes

\[P1No\] 0\.7% to 0\.8% No买入所需可见最佳卖价0\.56美元/份，顶档可见172份；盘口时间2026\-11\-02T07:47:19\.779000\+00:00。（price；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S5734061No

\[P2Yes\] 0\.9% to 1\.0% Yes买入所需可见最佳卖价0\.28美元/份，顶档可见118\.43份；盘口时间2026\-11\-02T07:50:09\.464000\+00:00。（price；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S5734062Yes

\[P2No\] 0\.9% to 1\.0% No买入所需可见最佳卖价0\.79美元/份，顶档可见80份；盘口时间2026\-11\-02T07:50:09\.464000\+00:00。（price；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S5734062No

\[P3Yes\] 1\.1% to 1\.2% Yes买入所需可见最佳卖价0\.08美元/份，顶档可见69\.96份；盘口时间2026\-11\-02T07:49:42\.760000\+00:00。（price；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S5734063Yes

\[P3No\] 1\.1% to 1\.2% No买入所需可见最佳卖价0\.985美元/份，顶档可见98\.98份；盘口时间2026\-11\-02T07:49:42\.760000\+00:00。（price；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S5734063No

\[P4Yes\] 1\.3%\+ Yes买入所需可见最佳卖价0\.001美元/份，顶档可见890\.42份；盘口时间2026\-11\-02T07:50:09\.396000\+00:00。该档缺买盘，按单边指示报价处理。（price；2026\-11\-02T07:54:08\.603270\+00:00）

依据：；来源：S5734064Yes

\[C22\] 市场最热的0\.7%\-0\.8%档YES卖价50¢，而0\.9%\-1\.0%档YES卖价28¢。按合约经济类taker费率，后者每份等价成本约29\.008¢，必须认为该档胜率高于约29\.0%才有正期望；0\.7%\-0\.8%档50¢买入的门槛约51\.25%。这些是成本门槛，不是研究胜率。各档更新时间不同，不能将盘口相加宣称套利。（inference；2026\-11\-02T07:54:08\.603270\+00:00）

依据：C20, C21, P0Yes, P0No, P1Yes, P1No, P2Yes, P2No, P3Yes, P3No, P4Yes；来源：

\[C23\] 研究优先看0\.9%\-1\.0%档28¢的YES，而非直接将0\.9%的点预测视为高胜率。它与前轮0\.9%基准一致，但现有0\.7%\-1\.1%只是情景范围，没有校准概率，不能据此断言该档胜率超过29%。当前属于有分歧可研究，未证实正期望；需要验证食品走弱是否足以把结果压到0\.7%\-0\.8%或更低。（inference；2026\-11\-02T07:54:08\.603270\+00:00）

依据：C8, C11, C20, C22；来源：

\[C24\] 0\.9%\-1\.0% YES的28¢顶档仅118\.43份，下一档37¢共61\.03份；28¢档名义金额约33\.16美元。若继续吃到37¢，该部分含费等价成本约38\.17¢。按当前可见盘口买100份需28美元，立即卖出时80份按21¢、20份按17¢，共收回20\.20美元，价格损失7\.80美元，另计费用；若最后不落该区间，持有至结算的YES价值为零。（inference；2026\-11\-02T07:54:08\.603270\+00:00）

依据：P2Yes, C21, C20；来源：

\[C25\] 研究价格条件：0\.9%\-1\.0% YES在28¢附近时，仅当独立判断该档胜率超过29\.0%且有额外误差余量才具正期望；若成本升至37¢，门槛升至约38\.17%。食品全月数据证实走弱到足以使公布同比≤0\.8%，将削弱这条候选；若不能建立分档概率优势，维持观察。（inference；2026\-11\-02T07:54:08\.603270\+00:00）

依据：C23, C24, C22, C11；来源：

S1 · 国家统计局 · T0 · published\_at：2025\-12\-25T00:00:00\+08:00 · retrieved\_at：2026\-11\-02T07:44:18\.568812\+00:00 · quote：居民消费价格指数月度报告；11月：9/一，9:30。本表公布的发布内容（除采购经理指数外）均为指标上月、上季、上年或累计数据。发布日期为初步计划，届时可能有所调整。 · locator：2026年国家统计局主要统计信息发布日程表，居民消费价格指数月度报告11月栏及附注 · origin\_id：nbs\-2026\-release\-calendar · origin\_basis：国家统计局直接发布 · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "核对日期与数据口径", "reason": "直接规定10月参考期的计划发布日期", "relevance": "direct", "selected": true\}

[https://www\.stats\.gov\.cn/xw/tjxw/tzgg/202512/t20251224\_1962137\.html](https://www.stats.gov.cn/xw/tjxw/tzgg/202512/t20251224_1962137.html)

S2 · 国家统计局 · T0 · published\_at：2026\-10\-14T09:30:00\+08:00 · retrieved\_at：2026\-11\-02T07:44:18\.568812\+00:00 · quote：2026年9月份居民消费价格同比上涨0\.9%；全国居民消费价格同比上涨0\.9%。全国居民消费价格环比上涨0\.2%。 · locator：标题及正文前两段 · origin\_id：nbs\-2026\-september\-cpi · origin\_basis：国家统计局直接发布 · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "核对日期与数据口径", "reason": "直接核对最近已公布数据的参考月与同比", "relevance": "direct", "selected": true\}

[https://www\.stats\.gov\.cn/sj/zxfbhjd/202610/t20261014\_1965477\.html](https://www.stats.gov.cn/sj/zxfbhjd/202610/t20261014_1965477.html)

S3 · Trading Economics · T3 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:44:18\.568812\+00:00 · quote：Date 2026\-11\-09; Reference Oct; Actual \[blank\]; Previous 0\.9%; Consensus \[blank\]; TEForecast 0\.9%\. · locator：HTML calendar row data\-id=400850; columns: Date, reference, actual, previous, consensus, TEForecast · origin\_id：te\-china\-oct2026\-model · origin\_basis：Trading Economics网页自有模型预测；原始HTML本轮保存 · evidence\_kind：opinion · access\_status：ok · supports：\["view"\] · selection：\{"priority": "decisive", "purpose": "外部预测基准", "reason": "与目标2026年10月完全匹配的外部模型预测，明确不是调查共识。", "relevance": "direct", "selected": true\}

[https://tradingeconomics\.com/china/inflation\-cpi](https://tradingeconomics.com/china/inflation-cpi)

S4 · 国家统计局 · T0 · published\_at：2025\-11\-09T09:30:00\+08:00 · retrieved\_at：2026\-11\-02T07:44:18\.568812\+00:00 · quote：10月份，全国居民消费价格环比上涨0\.2%。 · locator：2025年10月份居民消费价格同比上涨0\.2%，正文环比段 · origin\_id：nbs\-oct2025\-cpi · origin\_basis：国家统计局原始公告，WebFetch读取 · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "同比环比连接计算", "reason": "同比滚动预测所需去年同月环比基数。", "relevance": "direct", "selected": true\}

[https://www\.stats\.gov\.cn/sj/zxfbhjd/202511/t20251109\_1961826\.html](https://www.stats.gov.cn/sj/zxfbhjd/202511/t20251109_1961826.html)

S20 · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：This is a market about the variation of consumer prices in China over a 12\-month period ending October 2026 as reported by the National Bureau of Statistics \(NBS\) of China\.<br><br>This market will resolve according to the number the Consumer Price Index \(CPI\) increased by during the 12\-month period ending October 2026 \(% change from the same month in the previous year\) according to the monthly NBS report\.<br><br>The resolution source for this market will be the NBS Consumer Price Index monthly report released for October 2026 \(https://www\.stats\.gov\.cn/english/PressRelease/\), currently scheduled to be released in November 2026\. Resolution of this market will take place upon release of the aforementioned data\. If no data for the specified month is released by the date the next month's data is scheduled to be released, this market will resolve based on data from the last available month\.<br><br>You can find the relevant figure by locating the report for October 2026 on the Press Releases page \(see: https://www\.stats\.gov\.cn/english/PressRelease/\), locating the table named "Consumer Price Index in October 2026", and finding the consumer price index figure in the column labeled "Growth Rate Y/Y \(%\)"\.<br><br>Note: the resolution source for this market will be the official monthly NBS CPI news release which reports inflation during 12\-month periods to only one decimal point \(e\.g\. 1\.9%\)\. Thus, this is the level of precision that will be used when resolving the market\. For the full release schedule, see: https://www\.stats\.gov\.cn/english/PressRelease/ReleaseCalendar/ · locator：event\.description · origin\_id：polymarket\-china\-oct2026\-S20 · origin\_basis：Polymarket官方公开API · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\}

[https://gamma\-api\.polymarket\.com/events/slug/october\-inflation\-china\-annual](https://gamma-api.polymarket.com/events/slug/october-inflation-china-annual)

S21 · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：\{"exponent": 1, "rate": 0\.05, "takerOnly": true, "rebateRate": 0\.25\} · locator：markets\[0\]\.feeSchedule · origin\_id：polymarket\-china\-oct2026\-S21 · origin\_basis：Polymarket官方公开API · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\}

[https://gamma\-api\.polymarket\.com/events/slug/october\-inflation\-china\-annual](https://gamma-api.polymarket.com/events/slug/october-inflation-china-annual)

S22 · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：fee = C × feeRate × p × \(1 \- p\)\. Economics: 0\.05\. Makers are never charged fees\. Taker fees are calculated in USDC\. · locator：fee formula and economics table · origin\_id：polymarket\-china\-oct2026\-S22 · origin\_basis：Polymarket官方公开API · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\}

[https://docs\.polymarket\.com/trading/fees](https://docs.polymarket.com/trading/fees)

S5734060Yes · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：\{"bids": \[\{"price": "0\.2", "size": "20"\}, \{"price": "0\.199", "size": "20"\}, \{"price": "0\.15", "size": "13\.33"\}, \{"price": "0\.131", "size": "20\.01"\}\], "asks": \[\{"price": "0\.269", "size": "100"\}, \{"price": "0\.27", "size": "40"\}, \{"price": "0\.356", "size": "14\.82"\}, \{"price": "0\.357", "size": "47\.03"\}\], "timestamp": "1793605301491"\} · locator：CLOB best ask after sorting asks ascending; token 52183944893309575584469195876785440459503726691144855603239839746827009154742 · origin\_id：polymarket\-china\-oct2026\-S5734060Yes · origin\_basis：Polymarket官方公开API · evidence\_kind：market\_quote · access\_status：ok · supports：\["price"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\} · market\_quote：\{"ask": 0\.269, "bid": 0\.2, "direction": "buy", "instrument": "52183944893309575584469195876785440459503726691144855603239839746827009154742", "outcome": "Yes", "quote\_type": "executable", "quoted\_at": "2026\-11\-02T07:41:41\.491000\+00:00", "unit": "USD/share", "value": 0\.269\}

[https://clob\.polymarket\.com/book?token\_id=52183944893309575584469195876785440459503726691144855603239839746827009154742](https://clob.polymarket.com/book?token_id=52183944893309575584469195876785440459503726691144855603239839746827009154742)

S5734060No · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：\{"bids": \[\{"price": "0\.731", "size": "100"\}, \{"price": "0\.73", "size": "40"\}, \{"price": "0\.644", "size": "14\.82"\}, \{"price": "0\.643", "size": "47\.03"\}\], "asks": \[\{"price": "0\.8", "size": "20"\}, \{"price": "0\.801", "size": "20"\}, \{"price": "0\.85", "size": "13\.33"\}, \{"price": "0\.869", "size": "20\.01"\}\], "timestamp": "1793605301491"\} · locator：CLOB best ask after sorting asks ascending; token 108209989187998892927955357620122640696691348982806268943421311483976413566435 · origin\_id：polymarket\-china\-oct2026\-S5734060No · origin\_basis：Polymarket官方公开API · evidence\_kind：market\_quote · access\_status：ok · supports：\["price"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\} · market\_quote：\{"ask": 0\.8, "bid": 0\.731, "direction": "buy", "instrument": "108209989187998892927955357620122640696691348982806268943421311483976413566435", "outcome": "No", "quote\_type": "executable", "quoted\_at": "2026\-11\-02T07:41:41\.491000\+00:00", "unit": "USD/share", "value": 0\.8\}

[https://clob\.polymarket\.com/book?token\_id=108209989187998892927955357620122640696691348982806268943421311483976413566435](https://clob.polymarket.com/book?token_id=108209989187998892927955357620122640696691348982806268943421311483976413566435)

S5734061Yes · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：\{"bids": \[\{"price": "0\.44", "size": "172"\}, \{"price": "0\.41", "size": "20"\}, \{"price": "0\.4", "size": "5"\}, \{"price": "0\.33", "size": "234"\}\], "asks": \[\{"price": "0\.5", "size": "64"\}, \{"price": "0\.51", "size": "141\.34"\}, \{"price": "0\.52", "size": "15\.87"\}, \{"price": "0\.57", "size": "350"\}\], "timestamp": "1793605639779"\} · locator：CLOB best ask after sorting asks ascending; token 114171842186484275952326049592166610493642657152927370258739004220505470044692 · origin\_id：polymarket\-china\-oct2026\-S5734061Yes · origin\_basis：Polymarket官方公开API · evidence\_kind：market\_quote · access\_status：ok · supports：\["price"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\} · market\_quote：\{"ask": 0\.5, "bid": 0\.44, "direction": "buy", "instrument": "114171842186484275952326049592166610493642657152927370258739004220505470044692", "outcome": "Yes", "quote\_type": "executable", "quoted\_at": "2026\-11\-02T07:47:19\.779000\+00:00", "unit": "USD/share", "value": 0\.5\}

[https://clob\.polymarket\.com/book?token\_id=114171842186484275952326049592166610493642657152927370258739004220505470044692](https://clob.polymarket.com/book?token_id=114171842186484275952326049592166610493642657152927370258739004220505470044692)

S5734061No · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：\{"bids": \[\{"price": "0\.5", "size": "64"\}, \{"price": "0\.49", "size": "141\.34"\}, \{"price": "0\.48", "size": "15\.87"\}, \{"price": "0\.43", "size": "350"\}\], "asks": \[\{"price": "0\.56", "size": "172"\}, \{"price": "0\.59", "size": "20"\}, \{"price": "0\.6", "size": "5"\}, \{"price": "0\.67", "size": "234"\}\], "timestamp": "1793605639779"\} · locator：CLOB best ask after sorting asks ascending; token 109529943778586143059052037585386197051793239973444200675367716646347193445431 · origin\_id：polymarket\-china\-oct2026\-S5734061No · origin\_basis：Polymarket官方公开API · evidence\_kind：market\_quote · access\_status：ok · supports：\["price"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\} · market\_quote：\{"ask": 0\.56, "bid": 0\.5, "direction": "buy", "instrument": "109529943778586143059052037585386197051793239973444200675367716646347193445431", "outcome": "No", "quote\_type": "executable", "quoted\_at": "2026\-11\-02T07:47:19\.779000\+00:00", "unit": "USD/share", "value": 0\.56\}

[https://clob\.polymarket\.com/book?token\_id=109529943778586143059052037585386197051793239973444200675367716646347193445431](https://clob.polymarket.com/book?token_id=109529943778586143059052037585386197051793239973444200675367716646347193445431)

S5734062Yes · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：\{"bids": \[\{"price": "0\.21", "size": "80"\}, \{"price": "0\.17", "size": "216\.76"\}, \{"price": "0\.15", "size": "216\.32"\}, \{"price": "0\.1", "size": "573"\}\], "asks": \[\{"price": "0\.28", "size": "118\.43"\}, \{"price": "0\.37", "size": "61\.03"\}, \{"price": "0\.4", "size": "5"\}, \{"price": "0\.41", "size": "40"\}\], "timestamp": "1793605809464"\} · locator：CLOB best ask after sorting asks ascending; token 26887471990263045174666955224465910846695842248672249681094749371722644067548 · origin\_id：polymarket\-china\-oct2026\-S5734062Yes · origin\_basis：Polymarket官方公开API · evidence\_kind：market\_quote · access\_status：ok · supports：\["price"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\} · market\_quote：\{"ask": 0\.28, "bid": 0\.21, "direction": "buy", "instrument": "26887471990263045174666955224465910846695842248672249681094749371722644067548", "outcome": "Yes", "quote\_type": "executable", "quoted\_at": "2026\-11\-02T07:50:09\.464000\+00:00", "unit": "USD/share", "value": 0\.28\}

[https://clob\.polymarket\.com/book?token\_id=26887471990263045174666955224465910846695842248672249681094749371722644067548](https://clob.polymarket.com/book?token_id=26887471990263045174666955224465910846695842248672249681094749371722644067548)

S5734062No · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：\{"bids": \[\{"price": "0\.72", "size": "118\.43"\}, \{"price": "0\.63", "size": "61\.03"\}, \{"price": "0\.6", "size": "5"\}, \{"price": "0\.59", "size": "40"\}\], "asks": \[\{"price": "0\.79", "size": "80"\}, \{"price": "0\.83", "size": "216\.76"\}, \{"price": "0\.85", "size": "216\.32"\}, \{"price": "0\.9", "size": "573"\}\], "timestamp": "1793605809464"\} · locator：CLOB best ask after sorting asks ascending; token 20505240443959035398948663697700527654147215345529617205666034820832601721703 · origin\_id：polymarket\-china\-oct2026\-S5734062No · origin\_basis：Polymarket官方公开API · evidence\_kind：market\_quote · access\_status：ok · supports：\["price"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\} · market\_quote：\{"ask": 0\.79, "bid": 0\.72, "direction": "buy", "instrument": "20505240443959035398948663697700527654147215345529617205666034820832601721703", "outcome": "No", "quote\_type": "executable", "quoted\_at": "2026\-11\-02T07:50:09\.464000\+00:00", "unit": "USD/share", "value": 0\.79\}

[https://clob\.polymarket\.com/book?token\_id=20505240443959035398948663697700527654147215345529617205666034820832601721703](https://clob.polymarket.com/book?token_id=20505240443959035398948663697700527654147215345529617205666034820832601721703)

S5734063Yes · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：\{"bids": \[\{"price": "0\.015", "size": "98\.98"\}, \{"price": "0\.011", "size": "6\.44"\}, \{"price": "0\.01", "size": "160"\}, \{"price": "0\.009", "size": "100"\}\], "asks": \[\{"price": "0\.08", "size": "69\.96"\}, \{"price": "0\.094", "size": "14\.17"\}, \{"price": "0\.099", "size": "21"\}, \{"price": "0\.208", "size": "30"\}\], "timestamp": "1793605782760"\} · locator：CLOB best ask after sorting asks ascending; token 86933156776420864149302496693737629941007343057217584904829522768776921083933 · origin\_id：polymarket\-china\-oct2026\-S5734063Yes · origin\_basis：Polymarket官方公开API · evidence\_kind：market\_quote · access\_status：ok · supports：\["price"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\} · market\_quote：\{"ask": 0\.08, "bid": 0\.015, "direction": "buy", "instrument": "86933156776420864149302496693737629941007343057217584904829522768776921083933", "outcome": "Yes", "quote\_type": "executable", "quoted\_at": "2026\-11\-02T07:49:42\.760000\+00:00", "unit": "USD/share", "value": 0\.08\}

[https://clob\.polymarket\.com/book?token\_id=86933156776420864149302496693737629941007343057217584904829522768776921083933](https://clob.polymarket.com/book?token_id=86933156776420864149302496693737629941007343057217584904829522768776921083933)

S5734063No · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：\{"bids": \[\{"price": "0\.92", "size": "69\.96"\}, \{"price": "0\.906", "size": "14\.17"\}, \{"price": "0\.901", "size": "21"\}, \{"price": "0\.792", "size": "30"\}\], "asks": \[\{"price": "0\.985", "size": "98\.98"\}, \{"price": "0\.989", "size": "6\.44"\}, \{"price": "0\.99", "size": "160"\}, \{"price": "0\.991", "size": "100"\}\], "timestamp": "1793605782760"\} · locator：CLOB best ask after sorting asks ascending; token 57129428845494974286065369097486690887399583289017837615497895047905457446913 · origin\_id：polymarket\-china\-oct2026\-S5734063No · origin\_basis：Polymarket官方公开API · evidence\_kind：market\_quote · access\_status：ok · supports：\["price"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "直接核对目标合约规则或该选项可执行盘口。", "relevance": "direct", "selected": true\} · market\_quote：\{"ask": 0\.985, "bid": 0\.92, "direction": "buy", "instrument": "57129428845494974286065369097486690887399583289017837615497895047905457446913", "outcome": "No", "quote\_type": "executable", "quoted\_at": "2026\-11\-02T07:49:42\.760000\+00:00", "unit": "USD/share", "value": 0\.985\}

[https://clob\.polymarket\.com/book?token\_id=57129428845494974286065369097486690887399583289017837615497895047905457446913](https://clob.polymarket.com/book?token_id=57129428845494974286065369097486690887399583289017837615497895047905457446913)

S5734064Yes · Polymarket · T0 · published\_at：unknown · retrieved\_at：2026\-11\-02T07:50:23\.527860\+00:00 · quote：\{"bids": \[\], "asks": \[\{"price": "0\.001", "size": "890\.42"\}, \{"price": "0\.011", "size": "50\.99"\}, \{"price": "0\.012", "size": "155\.98"\}, \{"price": "0\.1", "size": "21"\}\], "timestamp": "1793605809396"\} · locator：CLOB best ask after sorting asks ascending; token 74947865945028394568190892672118545784871288967278080780974446091981724679176 · origin\_id：polymarket\-china\-oct2026\-S5734064Yes · origin\_basis：Polymarket官方公开API · evidence\_kind：market\_quote · access\_status：ok · supports：\["price"\] · selection：\{"priority": "decisive", "purpose": "结算映射及价格判断", "reason": "可见单边卖单，无买价，不声明完整双边可成交报价。", "relevance": "direct", "selected": true\} · market\_quote：\{"ask": 0\.001, "bid": null, "direction": "buy", "instrument": "74947865945028394568190892672118545784871288967278080780974446091981724679176", "outcome": "Yes", "quote\_type": "indicative", "quoted\_at": "2026\-11\-02T07:50:09\.396000\+00:00", "unit": "USD/share", "value": 0\.001\}

[https://clob\.polymarket\.com/book?token\_id=74947865945028394568190892672118545784871288967278080780974446091981724679176](https://clob.polymarket.com/book?token_id=74947865945028394568190892672118545784871288967278080780974446091981724679176)

F2 · 国家发展改革委 · T0 · published\_at：2026\-10\-29 · retrieved\_at：2026\-11\-02T07:43:59\.196827\+00:00 · quote：每吨分别应上调440元、420元；调控后实际上调345元、335元；自10月29日24时起。 · locator：调价金额与生效时点段落（分段摘录） · origin\_id：ndrc\-20261029 · origin\_basis：直接官方公告 · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "useful", "purpose": "T1汽油\+345元/吨、柴油\+335元/吨，月末生效", "reason": "T1汽油\+345元/吨、柴油\+335元/吨，月末生效", "relevance": "direct", "selected": true\}

[https://www\.ndrc\.gov\.cn/xwdt/xwfb/202610/t20261029\_1408449\_ext\.html](https://www.ndrc.gov.cn/xwdt/xwfb/202610/t20261029_1408449_ext.html)

F1 · 国家发展改革委 · T0 · published\_at：2026\-10\-15 · retrieved\_at：2026\-11\-02T07:43:59\.196827\+00:00 · quote：根据国际市场油价变化情况，本次汽、柴油价格不作调整。 · locator：公告正文 · origin\_id：ndrc\-20261015 · origin\_basis：直接官方公告 · evidence\_kind：document · access\_status：ok · supports：\["fact"\] · selection：\{"priority": "useful", "purpose": "T1国内油价中旬不变", "reason": "T1国内油价中旬不变", "relevance": "direct", "selected": true\}

[https://www\.ndrc\.gov\.cn/xwdt/xwfb/202610/t20261015\_1408170\_ext\.html](https://www.ndrc.gov.cn/xwdt/xwfb/202610/t20261015_1408170_ext.html)

F3 · 新浪财经转载西南证券叶凡 · T3 · published\_at：2026\-10\-15 · retrieved\_at：2026\-11\-02T07:43:59\.196827\+00:00 · quote：截至2026 年10 月13 日，同比方面，10 月初28 种重点监测蔬菜价格同比下降17\.1%，7 种重点监测水果价格同比下降6\.1%。鸡蛋价格同比涨幅收窄至31\.7%，猪肉价格同比下降11\.5%；环比方面，28 种重点监测蔬菜价格环比由上升转为下降5\.9%，7种重点监测水果价格环比下降0\.3%，降幅收窄。鸡蛋价格环比由上升转为下降9\.6%，猪肉价格环比由上升转为下降2\.2%。 · locator：截至10月13日高频段；以GB18030解码原网页 · origin\_id：swsc\-yefan\-20261015 · origin\_basis：同一西南证券叶凡研报；底层数字原始出处未取得 · evidence\_kind：opinion · access\_status：ok · supports：\["view"\] · selection：\{"priority": "useful", "purpose": "T1猪菜月初下跌线索，非全月；原始序列未回溯", "reason": "T1猪菜月初下跌线索，非全月；原始序列未回溯", "relevance": "direct", "selected": true\}

[https://stock\.finance\.sina\.com\.cn/stock/go\.php/vReport\_Show/kind/macro/rptid/845398391207/index\.phtml](https://stock.finance.sina.com.cn/stock/go.php/vReport_Show/kind/macro/rptid/845398391207/index.phtml)

来源状态：\{"community": \{"reason": "纯官方数值及发布时间查询，无需社区材料。", "status": "not\_run"\}, "expectations": \{"reason": "取得TE月度模型0\.9%；日历调查共识栏为空，不代表全市场共识。", "status": "partial"\}, "named\_october\_numeric\_forecasts": \{"reason": "五次搜索内未取得目标期具名数字，不代表不存在", "status": "no\_results"\}, "national\_food\_monthly": \{"reason": "仅取得具名研报月初数据及媒体转引月末单日数据，原始日序列未取得", "status": "partial"\}, "october\_services": \{"reason": "只有机构方向预测，无10月实际高频", "status": "partial"\}, "official": \{"reason": "两份官方网页经WebFetch读取。", "status": "ok"\}, "official\_oil": \{"status": "ok"\}, "original\_survey": \{"reason": "未取得目标期调查，预算用尽", "status": "not\_run"\}, "polymarket": \{"reason": "已保存event\.json、10份订单簿与token映射、feeSchedule。", "status": "ok"\}\}
