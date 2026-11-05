# SEC / NVIDIA 免费公开数据实测

- 开始 UTC：2026-11-02T02:26:43.541728+00:00
- 结束 UTC：2026-11-02T02:26:56.155196+00:00
- 与 2026-11-01 UTC 日历日差：1；距该日 UTC 零点秒数：95203.541728
- Python：3.9.6；curl 8.7.1 (x86_64-apple-darwin25.0) libcurl/8.7.1 (SecureTransport) LibreSSL/3.3.6 zlib/1.2.12 nghttp2/1.68.1
- 命令：`python3 -I /Users/frankzhang/Desktop/投研助手/evidence/free-sources-20261101/sec/scripts/validate_sec.py /Users/frankzhang/Desktop/投研助手/evidence/free-sources-20261101/sec`
- 脚本退出码：0
- User-Agent：`InvestmentResearchSourceValidation`（无虚构邮箱）
- 无 key、只读、不交易；串行，每项最多一次，30 秒总超时，不重试、不跟随重定向、不绕过 403/限流。

| 请求 | HTTP | curl退出码 | 耗时秒 | 字节 | 物理行数 |
|---|---:|---:|---:|---:|---:|
| submissions | 200 | 0 | 1.845591 | 159761 | 1 |
| companyfacts | 200 | 0 | 8.851676 | 4092966 | 1 |
| filing_document | 403 | 0 | 1.804872 | 4818 | 53 |

脚本退出 0 仅表示两个必测 API 成功；可选申报文档访问失败（403）。curl 退出 0 表示传输完成，不表示 HTTP 成功。

submissions 统计：`{"entity_name": "NVIDIA CORP", "recent_filing_records": 1000, "earliest_filing_date": "2020-09-17", "latest_filing_date": "2026-10-13", "historical_file_references": 1, "scope": "Dates/count cover filings.recent only; historical referenced JSON files not fetched."}`

companyfacts 统计：`{"entity_name": "NVIDIA CORP", "namespace_count": 6, "concept_count": 644, "fact_unit_records": 27281, "filed_dates": {"earliest": "2009-08-20", "latest": "2026-08-26"}, "period_end_dates": {"earliest": "2007-01-28", "latest": "2026-08-21"}, "period_start_dates": {"earliest": "2007-01-29", "latest": "2026-04-27"}, "count_definition": "Sum of all entries in facts[namespace][concept].units[unit]; entries can repeat economic facts across filings/contexts, not unique economic observations."}`

## 两条近期申报

- 2026-10-13 4/A；accession 0002152188-26-000007；报告日期 2026-09-09
  - [xslF345X06/wk-form4a_1791925767.xml](https://www.sec.gov/Archives/edgar/data/1045810/000215218826000007/xslF345X06/wk-form4a_1791925767.xml)
  - 链接生成依据：CIK 去前导零 + accessionNumber 去连字符 + primaryDocument，置于官方 SEC Archives 路径；并非 API 直接返回的完整 URL。
  - 文档验证：{"http_status": 403, "exit_code": 0, "body_path": "/Users/frankzhang/Desktop/投研助手/evidence/free-sources-20261101/sec/raw/20261102T022643541728Z-filing_document/response.body"}

- 2026-10-09 4；accession 0001197647-26-000011；报告日期 2026-10-07
  - [xslF345X06/wk-form4_1791579847.xml](https://www.sec.gov/Archives/edgar/data/1045810/000119764726000011/xslF345X06/wk-form4_1791579847.xml)
  - 链接生成依据：CIK 去前导零 + accessionNumber 去连字符 + primaryDocument，置于官方 SEC Archives 路径；并非 API 直接返回的完整 URL。
  - 文档验证："未请求"

## 边界与证据

- edgartools 未安装、SDK 未测，仅实测底层 SEC 公开 API。
- 原始响应和响应头分别存于 raw 中各自全新独立子目录；自写脚本在 scripts。
- 物理行数不代表 JSON 记录数；统计口径以 result.json 为准。
- 如请求被拒绝，记录实际 HTTP 和退出码，不将环境访问失败认定为产品缺陷。
- 详细命令、版本、HTTP、耗时、响应哈希和绝对路径见 result.json。
