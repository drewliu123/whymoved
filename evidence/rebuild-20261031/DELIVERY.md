# 投研助手 0.3.0 本地源码交付

2026-10-31。源码目录：`/Users/frankzhang/Desktop/投研助手`。本次按用户批准的本地开发例外完成；该目录不是 Git 仓库。源码版本及本地市场版本已统一为 0.3.0，已安装缓存未更新。

## 用户现在获得什么

插件从研究问题出发，选择能区分不同解释的材料，连接原文、计算和判断。报告先回答，再给重要发现、竞争解释和下一项观察。事件、资产、主题、人物机构各有专属方法；普通研究可直接归档，不再被强制预测登记或作者评分打断。

来源层级 T0–T4 用于约束一条材料能支持什么主张。阅读顺序独立按问题相关性、原始细节、时间与比较口径、区分解释的作用决定。候选池、Last30Days 原排名、聚类、状态、原文与选择原因均保留；低热度反证不会因互动量而自动被删除。同一文档的不同片段保留，同一原始出处及其转载不能冒充多份独立证据。

研究产物由同一冻结 report.json 生成 Markdown/HTML，附结论账本、来源、可选计算与图表。图表具有数据表、键盘焦点、悬停读数和交叉线。archive/update 保存输入及 SHA-256 清单，默认不覆盖；更新保留父版本并记录证据变化、判断是否改变和口径可比性。

## 实际示范

打开 `live/final-rendered/report.html`，或同目录 Markdown。

问题是微软含融资租赁的资本开支与现金 PP&E 如何比较实际现金负担。研究将三个不同用途分开：总资本投入看资源取得；当期现金从 CFO 减同期间 cash PP&E 出发，再单列同期间融资租赁本金；未来负担看租赁承诺和到期表。

- FY25Q4 总资本开支 24.2B，现金 PP&E 为 17.079B，差额约 7.121B。扣除披露的新融资租赁 6.5B 后仍约 0.621B，故不能把全部差额写成新增融资租赁。
- FY2025 全年 CFO 136.162B 减现金 PP&E 64.551B 为 71.611B；再减融资租赁融资现金流 2.283B，分析口径余额为 69.328B。已在 CFO 中的租赁经营现金项不重复扣。
- 未开始租赁 92.7B 属未来义务，不进入当年现金支出。季度与全年分别处理，未取得逐项残差调节，不为其虚构成因。

这展示了本版要做的增量：将电话会、现金流表和年报附注连起来，算出差额并暴露尚未解释的部分，使读者能直接使用比较口径。

## 验证结果

| 项目 | 实际执行与结果 | 证据 |
| --- | --- | --- |
| 全量自动测试 | 系统 Python 3.9.6，隔离 HOME/TOUYAN_HOME，105 tests，退出 0；测试运行 10.605 秒，外层计时 10.899 秒 | final-tests.log、final-tests.json |
| 独立代码审查 | 原 F1–F5 五个可复现问题均修复；复核原复现及正向控制通过，当前审查快照无遗留阻塞项；最终源码哈希再次比对 | independent-code-review.md、final-integrity.json |
| 实际检索与严格 v2 研究 | 19 候选、5 个入选原始来源、7 条 claims、3 条发现；sources/plan/claims/report 校验、渲染、归档和读取通过；最终 HTML/Markdown 与归档逐字节一致 | live/logs/final-validation.json、live/isolated-home/journal/runs/R20261031T184001Z-7bace460dc9c/ |
| 算术 | 4 项独立 Decimal 表达式复算通过；未执行任意 formula 字符串 | live/logs/arithmetic-check.json |
| 最终源码 CLI 串联 | 使用实际示范冻结输入，在独立 home 执行 archive → update → show → list，4 命令全部退出 0；父目录文件字节不变，子 run 关联正确，claims 无变化 | final-e2e/results.json、各命令 stdout/stderr |
| 四类既有样本 | 四例兼容渲染退出 0，带旧证据格式标识；新严格归档全部按预期退出 1，拒绝 schema1；asset 两个旧来源缺 retrieved_at，保留未知 | regression/final-v2/results.json |
| 浏览器 | 最终示范桌面 1280 与手机 390 无整页横向溢出；长表内部滚动、证据链接展开、明暗切换正常；截图已人工查看 | live/browser-final-checks.json、live/browser-final-*.png |
| 图表 | 合成测试数据验证键盘左右箭头、悬停、tooltip/crosshair、明暗与表格；配色 validator 通过。合成图表不是研究证据 | browser-checks.json、browser-chart.png |
| 旧数据保护 | 正式 authors.json / memos.jsonl 仅比对字节哈希，与改造前完全一致；四例原 151 个样本文件未改 | final-integrity.json、regression/final-v2/integrity.json |

CLI update 串联使用同一冻结证据，只证明保存、比较及读取流程，不代表新增研究或持续跟踪效果。四例为开发回归，不是留出评测。早期六个误接受 schema1 的隔离归档已经作废，未计入通过、未纳入最终交付包；历史尝试仍留在工作目录供查阅。

## 搜索的实际表现

已真实运行 Last30Days 3.30.0，Python 3.12，raw profile，带 query plan，限定 HN、365 天。引擎退出 0、自报 5.3 秒，返回 13 条候选；研究者判断全部与本题无关，全部不选，原始池与排序保留。该结果说明适配和排除链工作正常，同时说明本题引擎相关召回未成功。

补充检索获得微软三份原文、GeekWire 原创报道、HN 一条原帖。社区观点仅作基准混用的上下文，不支持现金算法或市场共识；媒体重复的微软数字也不算第二个独立事实测量。未使用浏览器 cookies、登录或付费源。

已知 9 个逻辑搜索请求：5 次原生 WebSearch、引擎实际 2 次 HN search、2 次直接 Algolia search。另有原文抓取。runtime 准备至最终归档回放结束约 513.753 秒，未覆盖更早阅读和两次预检索；不作为版本间速度比较，无可用费用记录。中途启动器参数与泛化措辞校验失败保留于 live/logs/outcomes.json，未抹去。

## 与旧模板的比较

live/comparison.md、old-template.md、new-template.md 使用同冻结证据与约 600 汉字正文预算，旧稿 582、新稿 549 汉字。两份都有相同的来源和四项计算；新版将现金算法和用途区别放在开头。

这是同代理非盲模板回放，不是旧插件完整运行或公平模型评测。它能核对信息出现的位置，不能证明理解效果、预测收益或优于专业研究员。研究价值需要持续通过矛盾发现、计算质量、判断更新与重复使用来检验。

## 包内容及运行

- `delivery/touyan-0.3.0-source.zip`：README、插件元数据、agents、skills、scripts、tests。排除真实作者库、预测账本、旧研究、下载原文、缓存、私有配置。
- `delivery/touyan-0.3.0-validation.zip`：本报告、完整源码 diff、新增/修改清单、测试与审查记录、实际示范冻结输入/最终归档、公开原文、浏览器截图及四例最终回归记录。下载原文只作数据，不执行。
- `delivery/manifest.json`：两包 SHA-256、大小、文件数及版本。

插件脚本要求 Python 3.9+，只使用标准库；Last30Days 可选引擎独立要求 Python 3.12+。实际测试入口：

```bash
python3 -m unittest discover -s tests
```

安装和更新步骤见源码 README。交付未执行安装、缓存覆盖、GitHub 写入、push、merge、后台调度或真实账本迁移。没有 Node 应用，未执行 npm build/lint/typecheck，也没有将它们记为通过。严格校验验证结构、时间与支持资格，原文语义、会计解释和研究判断仍由研究审查负责。
