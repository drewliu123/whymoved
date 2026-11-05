# v2来源与结论契约

新研究显式使用schema_version=2，来源集中保存、结论以source_id引用。旧schema1的内嵌sources与R1–R8继续由check_claim(claim, ids)兼容；不把旧记录静默迁移成严格v2。

## sources.json

下面是虚构示例，仅说明字段，不作研究证据。as_of取证完后冻结；想研究过去则historical=true且证明当时可得。

```json
{
  "schema_version": 2,
  "as_of": "2026-10-31T18:00:00Z",
  "historical": false,
  "candidates": [{
    "id": "S1", "url": "https://example.com/disclosure",
    "canonical_url": "https://example.com/disclosure",
    "publisher": "示例公司", "tier": "T0",
    "published_at": "2026-10-30T12:00:00Z",
    "retrieved_at": "2026-10-31T17:59:00Z",
    "quote": "本季度收入为100百万美元。", "locator": "季度业绩表第1行",
    "origin_id": "issuer-quarter-release", "origin_basis": "公司直接披露",
    "supports": ["fact"], "evidence_kind": "document", "access_status": "ok",
    "selection": {"selected": true, "reason": "直接提供被研究收入基数", "relevance": "direct", "purpose": "核对业务兑现", "priority": "decisive"}
  }],
  "source_status": {"official": {"status": "ok"}, "community": {"status": "not_run", "reason": "示例不执行检索"}}
}
```

- id指向具体片段；同一URL可有多个不同定位片段。canonical_url去重不等于原始出处独立性。
- origin_id/origin_basis明确共同原始出处。两家媒体来自同一公告共用origin；未知就空，不能编独立性。
- supports为fact/price/consensus/view的子集；evidence_kind为document/market_quote/survey/opinion。选中且access_status=ok并有quote/locator才有资格支持主张。
- selection由主研究者解释relevance（direct/context/irrelevant）、purpose、priority（decisive/useful/background）、selected及reason。选择脚本保留原候选与审计，不产生语义判断。
- engagement、platform、author、engine_rank/provenance可保留；互动和排名不改变证据层级。
- published_at未知写unknown，retrieved_at必须可解析。事件时间、更新时间与引用日可额外记录，不互相代替。

## claims.json

```json
{
  "schema_version": 2, "as_of": "2026-10-31T18:00:00Z",
  "claims": [
    {"id": "C1", "text": "示例公司披露季度收入100百万美元。", "type": "fact", "as_of": "2026-10-31T18:00:00Z", "sources": [{"source_id": "S1"}]},
    {"id": "C2", "text": "该披露给出后续收入比较的基数。", "type": "inference", "as_of": "2026-10-31T18:00:00Z", "sources": [], "basis": ["C1"]}
  ]
}
```

获取状态access_status与source_status分开：前者ok/snippet/failed；后者使用ok/partial/no_results/not_run/error/rate_limited/auth_failed/payment_required/unreachable/timeout/schema_drift。字段用具体契约枚举，文字描述可说明失败原因。

```bash
python3 "$TY_DIR/scripts/sources.py" validate "$WORK/sources.json"
```

```bash
python3 "$TY_DIR/scripts/check_claims.py" "$WORK/claims.json" --sources "$WORK/sources.json" --json
```

校验入口的退出码：0满足契约，1不满足，2无法读取/解析输入。严格v2检查来源引用、选中状态、原文定位、URL协议、时间、来源资格与推断循环；不能自动证明引文语义和因果。

## 资格与额外字段

| 主张 | 最小支持资格 |
|---|---|
| fact | 一个T0原始片段，或两个已确认独立origin的T0–T2；机构自身“说了什么”的限定事实另见下 |
| price | T0/T1的market_quote，明确选项与报价时刻；不能只凭网页非空URL |
| consensus | 一个T1 survey，或两个已确认独立origin的T1–T2 survey；都需方法/样本/覆盖人群与时间，结论范围仍需人工审查 |
| view | 归属明确的观点，不能把被引者的外部事实当作已证实 |
| inference | basis存在、不自引、不形成多节点环；计算和机制仍由研究者审查 |

price候选附：`market_quote={quoted_at,instrument,outcome,direction,value,unit,quote_type}`；quote_type为indicative/executable/trade/close/derived，claim.price_kind必须一致，executable还需bid/ask，quoted_at是带时区时刻，value有限数值。另记录bid/ask/last/indicative性质、token、深度、费用及异步差异，避免把参考值写成可成交价格。身份和规则也是必要研究输入，字段齐全不代表映射正确。

survey候选附：`survey={population,sample_size,method,fieldwork_start,fieldwork_end}`，sample_size至少2，claim.consensus_scope必须与population完全一致，范围与结论一致，调查在截点之前结束。同一天无法判断先后时用精确时刻。

T3机构自身表态如作为fact，候选需`attribution={speaker,original:true,statement_kind:"attributed_statement"}`，claim需`attributed_to`完全匹配且`fact_scope="attributed_statement"`；只支持“该机构原话如此”，不支持其判断是真的。

来源在claim截点之后获取时，附`availability={available_at,evidence_url,quote,locator}`证明当时已可得。历史任务unknown/只有日期/后续修改页也要可得性凭据。今天读到同名网页不能证明历史内容。严格日期失败不能通过删时间或设unknown绕过。当前研究unknown发布日仅在获取时刻不晚于截点等规则下可接受。

## Last30Days导入

```bash
python3 "$TY_DIR/scripts/sources.py" import-last30days "$WORK/last30days-raw.json" --out "$WORK/community-candidates.json"
```

适配器保留原raw及hash、候选池、原排名和聚类；导入后仍需补原文/locator、分级、用途与选择。默认未选中不是否定质量，而是尚未完成取证。未知输入结构明确失败；摘要/标题不当作原文。不要用导入成功冒充完整社区链通过。
