# Event 独立审查意见处置

本记录基于协调者转达的独立审查意见，仅定向修订已有材料；没有新检索。原研究截点与盘口快照不变，pre-market-analysis.json、independent-freeze.json不改写。此记录说明已收到意见及其处置，不代替审查者对修订后的再次验收。

1. **fallback指代未明**：修订C2/C3/C16、契约表、集中局限及同源Markdown/HTML。规则原文“the next scheduled meeting”没有说明next相对哪个时点，时区/截止秒也未明确。2027年1月26–27日只证明是12月之后的日历会议，不能确定为默认截止。没有自行指定fallback日期；未向平台或oracle核实。
2. **单月消费放缓不等于持续需求走弱**：修订C6/C14、发现与替代解释为9月实际消费增速较8月放缓、实际DPI下降，尚未确认持续或广泛需求走弱。补入10月Fed以10–2维持、等待更多信息，作为继续等待的直接政策依据。冻结初判仅为历史记录，保留原文，不以修订覆盖当时判断。
3. **定性更新与可否定命题**：watch明确为定性更新提示，没有已校准、可重复的改判阈值，不编造数值阈值。新增C18：12月正式声明若相对会议前目标上限降息或加息至少50bp，即落在维持/加25bp两中心情景之外，记为中心情景未覆盖实际结果；这不是声称已排除尾部可能。没有独立数值概率，不计算独立Brier/log loss；未来事件尚未评分。
4. **成交价字段冲突**：仅检查已保存原始响应。加25bp子合约3215008，Gamma lastTradePrice=0.71；同一Yes token的CLOB last_trade_price="0.290"。两端均无独立成交时戳，updatedAt和订单簿timestamp不能当成交时间。新增C17，在sources.json保存字段并同步报告局限；两字段均未用于方向判断或价格变动解释。未核实差异来自接口语义、缓存、旧成交或其他原因，不选择任何一方作真值。

所有修改由compose.py同源生成report.json、claims.json、sources.json、report.md、report.html。重跑既有check_claims.py并更新check_claims.log、validation.json、validation-static.log；最终退出码以这些文件为准。BLS 403、无独立校准概率、规则边界、未作浏览器视觉检查等剩余局限继续保留；本次修订不把partial提升为pass。
