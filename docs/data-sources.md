# 数据源可达性（本机，2026-11-14）

这份表记录各类数据源在本机的实际可达性，避免后续研究重复撞同一堵墙。状态来自实际请求，不是推测。

| 数据源 | 用途 | 状态 | 备注 |
| --- | --- | --- | --- |
| `data.sec.gov` companyfacts | 10-K/10-Q 年度与季度事实 | ✅ 可用 | 需要 `User-Agent: Touyan research (local test)` |
| `data.sec.gov` submissions |  filings 列表 | ✅ 可用 | 可确认 10-K/8-K 是否已提交 |
| SEC Archives（`www.sec.gov/Archives`） | 10-K/8-K 原文、分部表 | ❌ 403 | Undeclared Automated Tool；不伪造身份绕过 |
| SEC Financial Statement Data Sets | 维度化 XBRL（分部） | ❌ 403 | 同上 |
| Microsoft Investor Relations | 年报、分部表、新闻稿 | ❌ 403 | 自动访问被拒 |
| Applied Materials IR | 新闻稿 | ❌ 403 | 自动访问被拒 |
| Nasdaq historical API | 收盘价 | ✅ 可用 | 需要浏览器 UA；返回复权收盘 |
| FRED `fredgraph.csv` | 指数与宏观序列 | ✅ 可用 | 无需密钥 |
| 美联储官网 FOMC 日历 | 会议日期 | ✅ 可用 | 声明日取会议第二天 |

## 影响

- **微软分部明细**停在 FY2025：FY2026 10-K 已提交，但分部表在 SEC Archives 与 Microsoft IR 均不可得。
- **AMAT FY2026**：2026-11-12 已提交 8-K（可能含 Q4/FY2026 初步业绩），但原文不可得；正式 10-K 预计 2026-12。
- **FOMC** 只依赖 FRED 与美联储日历，不受影响。

## 规则

1. 不伪造 UA 或身份绕过 403；不可得就记录。
2. 事实优先 T0（SEC/Nasdaq/FRED）；T1/T2 只作补充并注明。
3. 每次尝试失败后更新本表，避免重复劳动。
