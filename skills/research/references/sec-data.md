# SEC 数据：EdgarTools 只读取证入口

本地入口：`scripts/sec_data.py`。插件入口保持 Python 3.9+ 标准库，通过独立 Python 3.11+ 运行 EdgarTools 5.62.1。首批覆盖美股 SEC 公告列表、精确 accession 的主文件/章节及财务报表；原有 Financial Datasets 财务和行情入口继续保留，见[financial-data.md](financial-data.md)。SEC 入口不提供股价、卖方一致预期或后台监控。

## 运行时与身份

运行时配置位于 `TOUYAN_HOME/data/sec-runtime.json`，TOUYAN_HOME 默认值沿用插件的数据根。配置仅保存 `python`、`site_packages` 路径，不保存身份。示例中的路径须替换为实际独立解释器和依赖目录；配置文件不是安装器，不能以写好配置宣称运行库可用。

```json
{
  "schema_version": 1,
  "python": "/absolute/path/to/python3.12",
  "site_packages": "/absolute/path/to/site-packages"
}
```

`EDGAR_IDENTITY` 只从调用进程环境读取，由用户在自己的运行环境提供真实联系身份。不得从配置、历史测试记录或其他文件补身份，不硬编码或复用测试邮箱，不把身份写进获取包、日志或共享文档。不要为运行命令向对话索取身份或凭据。入口不自动安装依赖或更新客户端插件。

先运行 `doctor` 检查当前配置与运行时。缺身份或缺运行时返回 `not_run`，不能记为已经完成 SEC 获取。doctor 的诊断结果也不证明联网取数成功或财务数值正确。

## 调用

以下命令从插件源码根目录执行。Agent 应使用插件根下的绝对脚本路径，将获取包保存在本轮独立 WORK 目录；accession 必须使用实际列表返回的精确值。

```bash
python3 scripts/sec_data.py doctor
python3 scripts/sec_data.py filings NVDA --form 10-Q --limit 5
python3 scripts/sec_data.py filings NVDA --form 10-Q --limit 5 --as-of 2026-10-31T20:00:00Z --timeout 60 --out '<NEW_JSON>'
python3 scripts/sec_data.py document --accession '<NUMBER>' --section full_text --out '<NEW_JSON>'
python3 scripts/sec_data.py document --accession '<NUMBER>' --section mda --as-of 2026-10-31T20:00:00Z
python3 scripts/sec_data.py document --accession '<NUMBER>' --item 'Part I, Item 2'
python3 scripts/sec_data.py statements --accession '<NUMBER>' --statement all --as-of 2026-10-31T20:00:00Z --timeout 60 --out '<NEW_JSON>'
```

`document --section` 可选 `full_text|mda|risk_factors|business`；`--item` 指定报告 item，只能与默认的 `full_text` 搭配，不与其他命名章节同时使用。`--attachment` 指定该披露内的精确附件文件名，例如 `ex991.htm`，不能与 `--item` 或非默认章节组合。`statements --statement` 可选 `all|income|balance|cashflow`。获取操作均支持 `--out NEW_JSON`（拒绝覆盖）、`--timeout secs` 与 `--as-of RFC3339`。同一示例中的 NEW_JSON 是待创建文件的占位符；每次保存使用不同路径。缺少的章节、无报表或解析失败须按实际状态记录，不能用其他章节或其他 accession 静默替代。

## 截点与文件身份

先用 `filings` 确认公司、form、精确 accession 和 SEC 原文 URL，再用该 accession 读取正文和报表，避免多次 latest 调用取到不同披露。保留 `filing_date`、`acceptance_datetime`、`period_of_report`：申报日、SEC 接受时刻、报告期分别记录，不能互相代替。接受时间从文件 SGML 头读取，其无时区时间按 `America/New_York` 转 UTC；不使用可能存在偏移的 submissions 时间标签。包内保留解析后的接受时间行并显式标注 normalized，不能把规范化行冒充下载原字节。列表受 `--scan-limit`（默认 50、最多 100）约束；历史查询未扫描完时即使凑够条数也为 `partial`，不能保证未扫描部分不改变排序。

历史研究每次获取都传同一带时区 `--as-of`。列表按真实 `acceptance_datetime` 筛选；接受时间未知的文件不得视为通过。精确 accession 的 `document` 与 `statements` 也检查截点，拒绝未来文件和接受时间未知的文件。不能以日期早于截点、报告期更早或今天取得的最新 CompanyFacts 证明当时可得。被排除的未来/未知时间记录是取证限制，不等于没有相关披露。补不到真实接受时间时保留缺口，不删时间、不设 unknown 绕过。

## 获取包与完整性

统一输出获取包包含 `provider: edgartools`、`status`、`data`、`provenance`、`completeness`。它不是 sources v2 文档，也不直接创建 sources/claims。核对包内版本、参数、获取时间、精确 accession、SEC URL、三类日期及完整性信息后，再进入现有证据流程。

正文路径使用 Python 解析接口，保留完整主文件文本或所选完整章节，不经过 MCP 的 6000 字符截断输出。精确附件用 `--attachment` 读取，候选文件名和类型可从 `provenance.attachments` 核对。读取时可以分块定位，但不得把工具界面预览当全文。`full_text` 指主文件正文，不等于所有附件全文；8-K 的 EX-99.1 等附件须另行核对实际原文件，不能声称本入口已完整覆盖附件。章节不存在、解析失败或数据缺失时检查 `status` 和 `completeness`，不得因有一段文本就宣称完整。

报表以 `standard=False, presentation=False` 导出，保留原始概念与实例符号，不执行展示符号翻转。保留原始期间列、起止日期、YTD/quarter 属性、数值、单位、concept 与分部/合并范围及文件出处；`numeric_facts` 保留实例原值字符串、数值、unit_ref、decimals、上下文和维度，`units` 与 `reporting_periods` 提供对应定义。金额没有再次缩放，Decimals 表示精度而非再乘单位的指令。已知表格缺失 NaN 转 JSON null，零保留为零。不把累计值改名为单季，不自行推导单季值，不把缺失值填零。对比和模型输入前核对财年、财季、期间长度、是否累计、币种、缩放和分部范围；需要差分推导时由主研究者另记计算及输入 basis，不能冒充原始披露。解析后的表不是独立信息源，也不能用展示标签取代 concept 和原始期间证据。

读取 JSON 状态和完整性后才裁定获取结果：`not_run` 表示未执行，`partial` 表示仅部分取得；错误或超时按具体失败原因记录。不得把 `partial`、错误、空缺章节或缺失报表标为 `ok`。即使获取包为 `ok`，仍需审查具体字段、原文和口径，不能直接宣布证据或模型通过。source_status 使用现有证据契约的枚举，具体失败原因保留在说明中。

## 从 SEC 材料形成证据

fact-collector 按[evidence.md](evidence.md)建立候选，主研究者统一 S 编号。拟作为 T0 时，必须核对实际 SEC 原文件，并保存支持该主张的原文件 `quote` 与可复核 `locator`（如 Part/Item、表名、行、期间列或明确段落），同时保留精确 accession 和 SEC URL。ticker、标题、库生成的财务摘要、列表元数据或成功状态都不能代替原文引文。

另取 SEC 接受记录/提交头等可复核的时间依据，保存时间证据 URL、原文和定位；历史可得性按现有 `availability={available_at,evidence_url,quote,locator}` 契约填写。时间依据须独立于正文内容或报告期推测；获取包中单一时间字段不替代依据核查。主文件与独立时间依据可以来自同一 SEC 披露，但只证明材料与时间，不构成两个独立事实来源。

同一公告的 SEC 原文、EdgarTools 解析表、Financial Datasets 转述及媒体转载共用原始出处家族，不能双计为独立来源。EdgarTools 是解析器，不能被计为第二个 origin。修订文件保留各自 accession 和版本关系；比较修订不自动证明独立信息源。

## 验证边界

本次通过正式入口实测 NVDA 精确 10-Q 的完整 MD&A、三张报表、10-Q/8-K 列表和接受时间截点，并将原文收入片段转入既有 sources/claims 校验链。完整原文、原始表、断言及离线回归记录见 `evidence/sec-integration-20261102/`。个别附件类型、各公司自定义分类与其他表单仍按实际结果核查。插件安装状态见该目录交付记录；源码修改不会自动更新已加载会话。
