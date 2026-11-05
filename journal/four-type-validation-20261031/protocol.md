# 四类代表案例验证协议

启动：2026-10-31T17:14:08Z。每个案例记录实际研究完成截点；盘口单独记录获取时点，不将启动时间之后的报价伪装为启动报价。

## 目标

验证 v2 方法能否产出有用成品，并暴露缺口。本轮是四个开发案例的人工协调验证，不是插件自动化验收、不证明预测优势或泛化表现。

## 案例

- event：选择一个截至研究时仍未结算、官方规则可读取的 Polymarket 政策／宏观合约，解释规则、驱动、盘口及独立判断边界。
- asset：复用 NVDA 已冻结材料回答 10 月跌幅、候选解释、业务变化和下一观察；禁止把旧证据包装成新检索。
- theme：AI 用电如何转为电力设备收入和利润，以官方披露可获取的供应商作例子。
- actor：选择有明确承诺和后续披露的公司管理层，核对资本开支／资本配置表态与行动；优先 Microsoft，资料不足时收窄到能核对的承诺。

## 必须交付

每类 report.md、report.json、claims.json、sources.json、plan.json、validation.json。数字计算另存 calculations.json；网页材料保留可定位原句、日期、URL与获取时间。外部取证失败记录在 sources.json，不以默认值补齐。

report.json 为本轮展示的最小结构：title、question、as_of、status、answer、findings[{title,text,claim_ids}]、tables[{title,columns,rows}]、alternatives[{title,text,claim_ids}]、watch[{signal,meaning,claim_ids}]、gaps、sources[{id,title,url,published_at}]。若有适合图表的数据，另提供 datasets.json。结构只用于本轮，不修改产品 schema。

## 验证

A. 问题回答：是否直接回答、重要性排序明确。
B. 证据：主张—来源真正支持、时期单位正确、事实与推断分开；运行现有 check_claims.py 并保留退出码。
C. 计算：重算收益／增长／差异；缺数据不制造结果。
D. 专属方法：事件规则与概率，资产变化与预期，主题传导与量级，机构条件与实际行动。
E. 反方：至少一个有依据的替代解释与改变判断条件。
F. 交付：文字与HTML同源，引用可用，无内容漂移。

评审用 已满足／部分满足／未满足，不生成未经校准的综合分。由独立审查读取四类成品并挑战证据与主判断。旧版报告与新成品材料／预算并不完全相同，只作描述性比较，不宣称受控效果提升。

## 范围与权限

应用 touyan:research 的证据与研究建议约束；用户已经授权按 v2 验证，因此采用任务专属分析与适合成品，不强制旧固定角度或无意义概率。报告在本目录隔离保存，不写正式 journal/memos.jsonl 和 data/authors.json，不修改插件、不发布外部内容。
