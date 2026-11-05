# 英伟达财报前研究 · 0.1.1 基线

问题：截至研究截面，英伟达（NVDA）下一次财报前的市场预期是什么，关键分歧和证伪条件有哪些？

证据冻结：2026-10-31T05:12:10.269507Z。行情及盘口保留各自实际时间；这不是同一秒的价格快照。本文件按0.1.1技能生成，与新版共用18条证据；没有独立再检索一次。

一句话：Zacks当季收入预期只比公司指引中值高约0.92%，仍在公司指引范围内；公司指引、分析师预期、预测市场报价和股票涨跌分别回答不同问题，不能互相替代。[C7][C11][C16]

## 定价与对标

- [公司官方行情页](https://investor.nvidia.com/stock-info/stock-quote-and-chart/default.aspx)标注10月30日4:00 PM股价204.64美元，前收213.66美元，跌9.02美元/-4.22%；页面注明延迟20分钟，时间标记未明确时区。本次没有取得可靠的单日下跌归因。[C4]
- [公司Q3 FY2027指引](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2027/)为总收入1080亿美元±2%，即1058.4亿至1101.6亿美元；non-GAAP毛利率74.0%±50基点。[C2][C7][C12]
- [Zacks 10月30日汇总](https://www.zacks.com/stock/news/3019405/nvidia-corporation-nvda-is-attracting-investor-attention-here-is-what-you-should-know)为当季收入1089.9亿美元、EPS 2.49美元，EPS估计30天上调1%。只代表该来源口径；未取得样本人数和完整EPS调整定义。[C5]
- Zacks称过去四季均超过其收入及EPS估计；这是四次观察，不能单独确定本季超预期概率。[C6][C18]
- [毛利率预测市场](https://polymarket.com/event/nvidia-nvda-q3-adjusted-gross-margin-non-gaap-20261008120136000)的73%至75%合约在05:03:57Z显示77.5%；05:04:28Z订单簿为73¢买价/20.1份、82¢卖价/20份。显示值不是可直接成交价，历史挂单也不保证现在仍在。[C9][C11]
- [数据中心收入阈值市场](https://polymarket.com/event/will-nvidia-nvda-q3-data-center-revenue-be-above-20261008120135000)显示>950亿美元70%、>1000亿美元88%，嵌套阈值出现逆序，且买卖价差很大。不能据此拟合收入分布。[C8][C11]

## 发生了什么

- 8月26日，公司公布Q2 FY2027总收入962.21亿美元、数据中心收入890亿美元、non-GAAP毛利率75.0%。[C1]
- 同次财报给出Q3上述指引，且不假设中国Data Center compute收入；不能将这个限定扩大为所有中国收入为零。[C2]
- [10月28日官方公告](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Sets-Conference-Call-for-Third-Quarter-Financial-Results/default.aspx)确定11月17日约13:20 PT公布截至10月25日的Q3 FY2027结果，14:00 PT召开电话会。[C3]

## 社区在讨论什么

以下是有限样本中的个人观点，互动量是抓取或归档值，不是精确冻结时刻的热度，也不能推导多空比例。

- [u/soukstah](https://www.reddit.com/r/stocks/comments/1wuxwtu/just_sold_last_nvda_googl_and_msft/)质疑下游AI软件收入能否覆盖投入所需回报，帖子约844分/566评论。[C13]
- [u/KeyTrainingk](https://www.reddit.com/r/NVDA_Stock/comments/1x0vnke/nvidia_is_doing_almost_everything_right_so_whats/)看好业务，但不认为盈利增长自动意味着股票便宜，约40分/93评论。[C14]
- [u/Wonderful-Sail-1126](https://www.reddit.com/r/stocks/comments/1x7niv5/nvidia_blackwell_rental_prices_hits_record_high/)认为不同模型路线都需要硬件，借租价叙事判断需求韧性，约237分/165评论；相关租价没有在本次被核实为基本面事实。[C15]

## 分歧与推断

- 第一层门槛是收入兑现：超过1080亿美元公司中值，仍可能低于1089.9亿美元的Zacks预期；指引范围覆盖该预期两侧。[C7][C18；依据C2、C5、C6]
- 第二层是盈利质量：73.5%至74.5%的公司毛利率指引落在73%含至75%不含的合约区间内，但指引不能证明最终结果。[C12；依据C2、C10]
- 第三层是股价：本季增长兑现仍不足以证明股票便宜或财报后上涨；当前缺少足够的估值和期权预期门槛证据。[C16；依据C2、C4、C5、C14]

## 值得研究的假设

| 编号 | 假设 | 验证时间点 | 证伪条件 |
|---|---|---|---|
| H1 | Q3 FY2027首次官方non-GAAP毛利率满足73%≤x<75% | 计划11月17日财报；材料最晚截止12月31日23:59 ET | x<73%或x≥75%；按合约规则，缺指标或截止未公布也判NO。区间取中点、采用最精确数字、不计后续修订。[C3][C10][C12] |
| H2 | Q3 FY2027首次官方总收入严格超过1089.9亿美元 | 计划11月17日财报；观察截止12月31日23:59 ET | 收入≤1089.9亿美元；本次比较约定截止未公布或缺指标为NO。[C3][C5][C18] |

旧版没有强制问题契约及概率算法。本基线保留上述可验证观察，不凭主观印象填写一个概率；没有将77.5%显示值称为预测准确率。

## 反方

即使当季增长兑现，客户回报与后续增长也可能不足以支撑估值。这是需要进一步取证的研究风险，社区质疑不能证明融资或需求已经恶化。反过来，客户回报改善和交付收款持续兑现，会削弱该风险判断；单季财报不能完整裁决长期回报。[C17；依据C5、C13、C14、C15]

## 证据缺口

未取得带时点及到期日的期权隐含财报波幅、空头持仓、标准forward PE、Zacks样本人数和EPS完整调整口径，也未取得可核实的一线媒体最新反方原文。Reddit仅保留5个线程，部分请求超时；X无可用后端，补搜没有核实到可引用URL。一次补充预测市场搜索因SSL错误退出2，不能据此证明相同事件合约不存在。

本备忘录是研究材料，不构成投资建议。全部[C编号]对应共同claims.json；脚本校验来源结构，不证明网页内容真实、完整或预测正确。
