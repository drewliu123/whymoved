# 相对估值示例：微软与大型科技同行的市盈率折价

这是第一个基于**真实收盘价**的相对估值示例。问题：**微软相对 Apple、Alphabet、Amazon 的市盈率折价，是低估还是口径差异？**

数据来源：

- 收盘价：Nasdaq 官方历史行情，2026-11-13 收盘（明确报价日与收盘时刻）；
- 盈利与股数：各公司最近一个完整财年的 SEC 10-K 事实（净利润与稀释加权股数）。

| 公司 | 收盘价（美元/股） | 最近财年 | EPS（美元） | P/E |
| --- | --- | --- | --- | --- |
| MSFT | 523.88 | FY2026-06 | 17.95 | **29.2x** |
| AAPL | 356.27 | FY2026-09 | 8.98 | 39.7x |
| GOOGL | 295.77 | FY2025-12 | 10.81 | 27.4x |
| AMZN | 266.66 | FY2025-12 | 7.17 | 37.2x |

同行中位 37.2x，微软 29.2x，折价约 **21.5%**；但 Alphabet 也只有 27.4x，说明同组内本身分层。按同行中位倍数，微软 EPS 隐含每股约 **667 美元**，区间约 579–690 美元——这是倍数参照，不是目标价。

**结论**：折价事实成立，「低估」不成立。四家财年终点不同（MSFT 6 月、AAPL 9 月、GOOGL/AMZN 12 月），增长与资本开支结构也不同；把「低于同行」直接读成错误定价，会忽略分母的时间差与业务差异。

## 这个示例演示什么

- **真实价格证据**：每个收盘价都是 T0 交易所报价，带报价日、收盘时刻、相对前一日的方向，以及 `claim.price_kind=close`。
- **可比公司模型**：`relative_valuation` 用同行 P/E 分布给出隐含每股价值区间、现价隐含倍数与在同行中的分位（约 33%）。
- **口径陷阱**：财年不一致、P/E 未做 TTM 对齐、同行只有三家；这些都写进限制与判断，而不是藏在脚注。
- **不是目标价**：估值汇总只给方法区间，一页纸也保留「不跨方法加权」的边界。

## 命令

```bash
python3 scripts/analysis_contract.py check \
  --plan examples/mega-cap-peers/research/work/plan.json \
  --report examples/mega-cap-peers/research/work/report.json \
  --claims examples/mega-cap-peers/research/work/claims.json \
  --sources examples/mega-cap-peers/research/work/sources.json

python3 scripts/memo_pack.py examples/mega-cap-peers/research/work/report.json \
  --claims examples/mega-cap-peers/research/work/claims.json \
  --sources examples/mega-cap-peers/research/work/sources.json
```

## 边界

- 财年终点不同，P/E 未做 TTM 对齐；盈利增长会改变分母。
- 未调整增长、资本开支、回购与净现金差异；折价与低估之间不能画等号。
- 同行只有三家大型平台公司，不能代表全市场或行业。
- 收盘价是 2026-11-13 的快照；行情变化后结论需要重算。
