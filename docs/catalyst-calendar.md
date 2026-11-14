# 催化剂日历：未来 3 个月哪些时点可能放大波动

**窗口**：2026-11-14 → 2027-02-28（美股大盘与已覆盖的 19 个研究对象）
**用途**：事件风险 awareness，不是方向预测，也不是买卖建议。
**数据截点**：2026-11-14；价格与 EPS 预期来自 Nasdaq，宏观日期来自美联储与 BEA 官方日历。

## 一、已确认日期（可核对）

| 日期 | 事件 | 当前预期/共识 | 为什么可能放大波动 | 关联报告 |
| --- | --- | --- | --- | --- |
| **2026-11-17（盘后）** | 英伟达 FY2027 Q3 财报 | 共识 EPS **$2.49**（Nasdaq；营收预期未提供） | AI 算力基准；DSO、毛利率、数据中心指引会传导到设备（AMAT/LRCX/KLAC）与云厂商 | [nvda-growth-quality](../examples/nvda-growth-quality/README.md)、[ai-capex-value-chain](../examples/ai-capex-value-chain/README.md) |
| **2026-12-02 08:30 ET** | BEA：10 月个人收入与支出（含 PCE） | 本机无可信 consensus；看核心 PCE 环比与同比 | 影响降息路径与久期资产；对高估值成长（NVDA/LLY/TSLA）与银行（JPM）同时有估值传导 | [jpm-nim-provisions](../examples/jpm-nim-provisions/README.md) |
| **2026-12-08/09** | FOMC 会议（声明 12-09） | 本机无法取得市场隐含概率；看声明、点阵图与发布会 | 全市场贴现率；但本项目 23 次样本显示「FOMC 后方向」不稳定 | [sp500-fomc-event](../examples/sp500-fomc-event/README.md) |
| **2026-12-17** | 耐克 FY2027 Q2 财报 | 共识 EPS **$0.34**（Nasdaq；时间未定） | 毛利率、存货天数与全年指引；消费与关税敏感 | [nke-turnaround](../examples/nke-turnaround/README.md) |
| **2026-12-23 08:30 ET** | BEA：Q3 GDP 第三次估算 | 本机无可信 consensus | 增长与通胀组合；对利率与周期股有传导，但通常低于 PCE/CPI | — |

## 二、预计窗口（日期未确认，需在接近时复核）

| 窗口 | 事件 | 当前预期状态 | 波动潜力 | 关联报告 |
| --- | --- | --- | --- | --- |
| 2026-12 上旬 | 11 月非农就业（BLS，通常首个周五） | BLS 日历 403，无法确认具体日期；consensus 不可得 | 中高：利率路径 | — |
| 2026-12 中旬 | 11 月 CPI（BLS，通常中旬） | 同上；consensus 不可得 | 高：通胀与降息定价 | — |
| 2027-01 下旬 | 微软、苹果、特斯拉、JPM、LRCX、KLAC 财报 | 日期未在 Nasdaq 日历确认；consensus 尚未可取 | 高：指数权重与 AI/消费/银行/设备四条线 | msft-cashflow、aapl-quality、tsla-price-cut-quality、jpm-nim-provisions |
| 2027-02 上旬 | 礼来、埃克森、亚马逊、谷歌、Meta、AMAT 财报 | 日期未确认；consensus 尚未可取 | 高：医药/能源/云/设备 | lly-growth-quality、xom-capital-allocation、hyperscaler-capex-margins、ai-capex-transmission |

## 三、预测打分点（与本项目 5 条预测对齐）

| 预测 | 到期 | 事件 |
| --- | --- | --- |
| P3 JPM FY2026 ROE <15.5% | 2027-01-31 | JPM 4Q26/FY2026 财报 |
| P2 礼来 FY2026 存货天数 <420 | 2027-02-28 | 礼来 FY2026 10-K |
| P4 英伟达 FY2027 DSO ≤65 | 2027-02-28 | 英伟达 FY2027 10-K |
| P5 埃克森 FY2026 回购 <180 亿 | 2027-02-28 | 埃克森 FY2026 10-K |
| P1 微软 FY2027 capex/收入 <33% | 2027-07-31 | 微软 FY2027 10-K |

完整的共识假设、期限与失效条件见 [预测协议](prediction-protocol.md) 与 [预测日志](../predictions/2026-11.json)。

## 四、传导与拥挤

- **NVDA → 设备 → 云**：一个事件同时影响 AMAT/LRCX/KLAC 与 MSFT/GOOGL/AMZN/META 的 AI 叙事；持有多个 AI 名字时，事件风险不是分散的，而是同一链条的重复暴露。
- **FOMC/PCE → 所有估值**：高 P/E 名字（TSLA 363x、NVDA 33x、LLY 63x）对贴现率更敏感；银行（JPM）则同时受净息差与信用成本影响。
- **NKE 与消费**：单一公司事件，但毛利率/库存指引会影响消费板块情绪。
- **财报密集周**：2027-01 下旬与 2027-02 上旬是重叠窗口，多个高权重名字可能在同一周放大指数波动。

## 五、当前预期的诚实边界

- **只有 NVDA 与 NKE 有可核对的 EPS consensus**（Nasdaq 提供）；其他公司财报日期尚未进入日历，consensus 不可得。
- **宏观 consensus 不可得**：BLS 日历 403，Nasdaq 经济日历无 consensus 字段且与美联储官方日期冲突（曾把 FOMC 标为 12-10）；本表以美联储/BEA 官方日期为准。
- **没有市场隐含概率/期权定价**：无法量化「市场预期几次降息」或「财报隐含波动」。
- 波动潜力是编辑判断，不是统计估计；日期未确认的条目必须接近时复核。

## 六、接下来怎么用

1. **11-17 前**：只关注 NVDA 一个事件；检查 DSO、毛利率、数据中心指引，以及对本项目 P4 的含义。
2. **12-02 与 12-08/09**：先看 PCE，再看 FOMC；不要用 FOMC 做方向交易，本项目样本显示无稳定效应。
3. **12-17**：NKE 看毛利率与存货天数，验证「企稳≠修复」。
4. **2027-01/02**：按预测打分点逐条记录，不用后见之明改预测。

## 来源

- 美联储 2026 年 FOMC 日历（federalreserve.gov，2026-11-14 取）。
- BEA 发布日程（bea.gov/news/schedule，2026-11-14 取）。
- Nasdaq earnings calendar 与 quote info（2026-11-14 取；NVDA/NKE EPS consensus）。
- 价格：Nasdaq 2026-11-13 收盘。
