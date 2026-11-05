Final artifacts and command evidence are in final-v2/. All four latest render checks passed and all four latest archive attempts were rejected as expected with exit 1. There is no valid new archive or no-change update from these legacy samples. Old sandbox runs are superseded/nonconforming.

# Four development regression bundles



开发回归样本（dev sample，非 heldout）。仅将原冻结材料转换为 schema 2 报告；保留原 as_of，无新增检索、事实、引语、计算或研究判断。claims 保留原 schema 1，本次结构校验及开发归档不等于 strict schema 2 claims 验证，也不提供严格历史可得性证明。



This is an offline format/pipeline regression, not heldout validation, new research, strict schema 2 claim proof, or historical reconstruction.

Original answer/finding texts and as_of values are preserved; claims.json is copied byte-for-byte with implicit schema 1. No quotes, origin families, publication instants, retrieval instants, or availability records are invented.

All finding increments are labeled connection with an explicit old-claim baseline and no-new-research disclosure. This expresses existing relationships, not novel research.

Missing theme/actor table references are mapped to actual original claim IDs. The original asset price series is preserved as a scalar table; no chart is authored.

Source candidates come from inline claims joined to original sources.json by exact URL. Original status/time/quote records are retained in provenance. All candidates are unselected, supports=[] and origin_id=null: no new semantic source certification.

historical=false denotes a development replay; original as_of is not replaced with the build time. No availability assertion is supplied. Legacy claims do not qualify for NEW strict archives.

Original source lists appear in every rendered report; source quotes are copied only from existing source fields, never synthesized from claim text.


| case | render | sources2 validation | development archive | no-change update |
| --- | --- | --- | --- | --- |
| event | exit 0 | pass | blocked_legacy_claims_expected | not run |
| asset | exit 0 | blocked | blocked_legacy_claims_expected | not run |
| theme | exit 0 | pass | blocked_legacy_claims_expected | not run |
| actor | exit 0 | pass | blocked_legacy_claims_expected | not run |



All four cases remain render-only: their byte-identical schema 1 claims are not valid NEW archive inputs. Expected archive rejection is recorded with actual commands and stderr. No claim schema is downgraded and no metadata is invented to pass the gate.

Asset also lacks original retrieval instants for S1 and S3. Its render uses render_report API with sources=None and legacy claims, while its source catalog remains a report table. Missing source metadata is recorded as unknown.

The initial archiver accepted legacy inputs and produced six sandbox archive/update runs. Those prior results, commands and runs are superseded/nonconforming, preserved only to expose former gate behavior. They do not count as valid archive or update evidence. See superseded-results.json and superseded-nonconforming-runs.json.

No valid strict no-change update is demonstrated by these legacy bundles. The parent validation can cover safe schema 2 inputs with automated fixture tests; this conversion does not synthesize strict evidence.



## Reproduction and evidence



Run: `python3 -I evidence/rebuild-20261031/regression/build_regression.py --root /Users/frankzhang/Desktop/投研助手`.

The script refreshes only its owned development artifacts. Old sandbox runs remain labeled superseded; strict-gate-home must remain empty because archive attempts should be rejected.

commands.json contains complete command argv, shell representation, environment overrides, exits, and log paths; per-case logs retain stdout/stderr. build.command.json/build.stdout.log/build.stderr.log record the outer transformation invocation.

results.json, integrity.json and before/after original manifests provide outcomes and hashes. legacy-calculations.json is an unmodified old audit artifact, not a new schema 2 calculation document.

Verification covers structure, content preservation, legacy labels, contiguous Markdown tables, real renderer invocation and expected strict archive refusals; it does not add a browser/device visual check or claim a new complete product QA pass.



{
  "original_files": 151,
  "originals_unchanged": true,
  "product_scripts_unchanged": true,
  "scope": "Writes confined to evidence/rebuild-20261031/regression/",
  "archived_development_runs": 0,
  "superseded_nonconforming_runs": 6
}

