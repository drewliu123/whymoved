# EdgarTools 正式取证接入验证

日期：2026-11-02。投研助手源码版本：0.6.0。第三方库：EdgarTools 5.62.1（MIT）。

## 实现

- `scripts/sec_data.py`：Python 3.9+ 标准库入口、参数验证、运行时发现、超时、有限 JSON、退出码与新文件输出。
- `scripts/sec_worker.py`：独立 Python 3.11+ 取 SEC 文件，提供 filings/document/statements；doctor 不访问 SEC。
- 主研究 Skill 与 fact-collector 已明确按需求选择 SEC 入口，并接入现有 sources/claims 流程；Financial Datasets 行情入口保留。
- `TOUYAN_HOME/data/sec-runtime.json` 只保存解释器和独立依赖目录；不包含联系身份。测试身份只经临时进程环境传入。

## 实际取数

指定 NVIDIA 10-Q：`0001045810-26-000075`，报告期末 `2026-07-26`，申报日 `2026-08-26`。

原始索引：https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/0001045810-26-000075-index.html

主文件：https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm

SEC SGML header 解析出的接受时间：`2026-08-26 16:36:00`，按 America/New_York 转为 `2026-08-26T20:36:00Z`。接受时间行是解析器规范化后的 header 内容，获取包明确标识 normalized，不冒充原始字节引文。

- `1-document.json`：完整 MD&A，37,895 字符，未截断。UTF-8 SHA256=`cd14ab0a1188e10d6173830e3f6b49038ed0f10ac0883f74567d02b28a6fa9f2`，与上轮完整文本一致，末尾已核对。
- `2-statements.json`：同一文件的利润表、资产负债表、现金流量表；`standard=False, presentation=False` 保留原始概念和实例符号，附单位定义、期间和 1,000 个数值事实的上下文。缺失 NaN 转 null，严格 JSON 序列化通过。
- 单季收入：96,221,000,000；同财年累计收入：177,837,000,000。现金流表只提供 YTD，经营现金流为74,421,000,000；适配器没有把它改名为单季，也没有自行差分。
- `3-filings.json`：10-Q bounded 列表，保留未完整扫描的标记，不宣称全历史。
- `4-before-cutoff.json`：截点20:35:59Z，文件被排除，status=no_results、data=null。
- `5-at-cutoff.json`：截点恰好20:36:00Z，同一文件通过，取得完整 MD&A。
- `6-eightk-filings.json`：8-K 列表及主/附件文件名；该最新8-K仅有主文件，没有EX-99.1，因此没有把未取得的业绩附件说成已实测。

## 既有证据链

`verify_live.py` 对上述捕获数据执行固定真实值断言，生成经过人工选段的 `sources.json` 和 `claims.json`。quote 从完整 MD&A 直接截取，包含期间和“百万美元”单位头；选中该收入证据是本次研究选择，不是自动将所有解析数据提升为事实的规则。

运行：

```bash
python3 evidence/sec-integration-20261102/verify_live.py
python3 scripts/check_claims.py evidence/sec-integration-20261102/claims.json --sources evidence/sec-integration-20261102/sources.json --json
```

实际结果：来源结构通过；一条真实收入事实的严格v2主张校验通过。没有为纯适配器验证伪造完整研究报告或研究归档。

## 离线回归与独立审查

- 完整回归：192项全部通过，最终日志 `tests-final.log`。
- SEC专项覆盖：身份/配置缺失不取数、worker协议损坏/非有限值/非0退出/超时、无shell调用、输出拒覆盖、精确accession、完整文本、NaN/null/零/维度/单位与Q2/YTD、缺表partial、限流/403/500、附件精确选择、历史边界、Eastern冬夏时与DST歧义、先筛再limit及未扫完历史列表partial。
- 独立审查指出的两处问题均已修复：运行时JSON示例补schema_version；历史扫描未尽即使已凑够条数仍为partial。

## 安装与使用

执行 `claude plugin update touyan@touyan-local` 更新已安装版本，当前会话不会因此自动重载；最终结果以 `installation-status.json` 为准。

日常 SEC 获取仍需启动 Agent 的进程环境设置自己的 `EDGAR_IDENTITY`。本次没有将先前“仅测试”授权的姓名邮箱存为长期默认值，也没有把个人联系信息写入插件源码。其余运行时路径已配置并经 doctor 核对。

当前验证覆盖本次指定文件及列举契约；其他表单、其他公司的分类差异和 SEC 访问失败按返回状态处理。原文与数值的经济含义仍由研究者核对。
