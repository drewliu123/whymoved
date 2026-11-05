# NVDA 独立审查与处置

独立只读审查覆盖冻结输入、关键计算、账本及主判断。未重新联网核对原站，也未验证全月价格因果。

| 审查发现 | 处置 | 证据 |
|---|---|---|
| 从舍入毛利率反推Q2毛利额，精度与GAAP口径不理想 | 改用直接披露72.142十亿美元，Q3中点示例79.92，相比增10.78% | inputs/newsroom.txt GAAP gross profit；calculations.json |
| 账本保留旧包raw路径 | 映射到本例inputs副本 | claims.json sources.local_evidence；input-manifest.json |
| 旧获取晚于as_of注释与本次截点矛盾；媒体更新时间性质丢失 | 注明归档获取在本次截点前；Reuters日期标为更新时间、首次发布时间未确认 | claims.json；sources.json |
| 现金回收分析不能代替整月跌因解释 | 首段先回答实际跌幅；现金作为核查线索；补板块共同重估竞争解释；保持partial | report.json answer/alternatives/gaps |

复跑生成器与现有check_claims退出0，11条通过。这只证明当前字段规则满足，不证明整月归因完成。
