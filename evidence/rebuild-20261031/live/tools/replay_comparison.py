import json,re,hashlib,zipfile
from pathlib import Path
from datetime import datetime,timezone
R=Path('/Users/frankzhang/Desktop/投研助手/evidence/rebuild-20261031/live')
old='''投研助手 · asset · Microsoft · 截面 2026-10-31

一句话：FY25Q4 含融资租赁资本开支 24.2B，现金 PP&E 17.079B，比较现金压力时要统一口径。[C1][C2]

**定价与对标**
本题研究会计机制，股价、交叉定价、历史频率与调查预期均未取证，不填入数字。投入基准是季度 24.2B，现金基准是同季 17.079B，二者不能直接互换。[C1][C2]

**发生了什么**
2025-07-30 电话会披露资本开支包含 6.5B 融资租赁，在开始时确认全部价值；财报现金流表列 PP&E 支出 17,079 百万美元。[C1][C2]

**市场在想什么**
GeekWire 报道 24.2B 投入规模。HN 用户 _aavaa_ 质疑把低于分析师预计的支出称为 miss；只记录该人观点，评论所引金额未核实。[C6][C7]

**分歧与推断**
24.2−17.079≈7.121B，不等于 6.5B 新租赁，约 0.621B 无逐项调节解释。PP&E 应付款可能影响支付时点，但未证明残差组成。[C3][C4]

**值得研究的假设**
若比较当期现金，以 CFO 减现金 PP&E 再减同期间融资租赁本金。FY2025 全年 136.162−64.551=71.611B，扣本金 2.283B 后为 69.328B；已进 CFO 的 1.372B 不重复扣。[C4][C5]

**反方**
若研究设备投入与扩建规模，含租赁口径仍有用途，不能因其非当期现金就删掉。[C1][C6]

**证据缺口**
未取到 Q4 独立租赁本金；未开始租赁 92.7B 属未来义务线索。引擎 13 条均不相关，另抓一条 HN 原帖，不能据此概括社区。[C4][C7]

本备忘录是研究材料，不构成投资建议。
'''
new='''微软资本开支与现金负担 · 同证据压缩回放

先回答：比较现金压力应分开投入确认、当期支付和未来义务。先算 CFO 减现金 PP&E，再单列同期间融资租赁本金；不能用含新租赁的总 capex 直接代替现金支出。季度和全年必须各算各的。[C1][C2][C4][C5]

**投入规模不能替代现金压力**
FY25Q4 总资本开支 24.2B，包含开始时确认全部价值的新融资租赁 6.5B；现金流表 PP&E 为 17.079B。GeekWire 以 24.2B 报道投入规模，读媒体数字前要确认比较目标。全部资本开支也不能都称为 AI 投入。[C1][C2][C6]

**差额仍有未解释部分**
24.2−17.079≈7.121B，再扣 6.5B 仍约 0.621B。前两项管理层数字已经四舍五入，差值也是近似。年报有 PP&E 应付款，提示支付时点可能影响桥接，但不能据此给季度残差命名。[C1][C2][C3][C4]

**现金比较要补本金，避免重复扣**
全年 CFO 136.162−现金 PP&E 64.551=71.611B；再减全年融资租赁本金现金流 2.283B，得到分析口径 69.328B。已在 CFO 中的租赁经营现金项 1.372B 不再重复扣。未开始租赁 92.7B 列入未来义务，不能作为当年现金支出。[C4][C5]

**下一步只补能改变判断的证据**
需要同季度融资租赁本金和明确的 capex 调节表，才能给出 Q4 扣租赁后的现金余额。若目的改为衡量扩建规模，可先看含租赁投入，再附现金口径。[C1][C3][C5]

**边界**
HN 用户质疑分析师与公司预期混用，仅代表本人。引擎 13 条均未采用，原帖来自补充抓取；不把它当调查或验证转引数字。没有核验投资回报率，也没有推导最新股票建议。[C7]
'''
old=old.replace('本备忘录是研究材料，不构成投资建议。','比较边界：同为美元并不代表相同经济口径，现金流量、取得资产和签约未来付款义务需要分别展示。把媒体转引的资本投入规模与另一家公司现金采购直接并排，会混入不同租赁安排与付款时点。财报所示年末应付款只能提示问题，未完成季度期初期末调节前，不应把它分配给这一季度的残差。[C1][C2][C4][C6]\n\n研究建议：为下一次比较建立同期间表，分别列经营现金流、现金购置资产、租赁本金和未来义务；有缺项就标注缺项，不用年度金额填季度空白，也不把新确认的租赁全部作为当天现金流出。两种口径回答不同问题，应该先声明研究目的再使用对应金额。[C1][C4][C5]\n\n本备忘录是研究材料，不构成投资建议。')
new+='\n比较对象的期间、币种和租赁口径应同时一致。读到一个较低的现金采购数字，只能说明该口径当期支付较低，不能据此断言公司减少相同比例的资源取得或未来支付。下一轮若获得季度租赁本金与资本开支逐项调节，可以再更新现金压力判断；在此之前保留无法解释的部分。[C1][C2][C3][C4][C5]\n'
(R/'old-template.md').write_text(old)
(R/'new-template.md').write_text(new)
# Equal-budget comparison treats Chinese character count as explicit content budget,
# excludes headings/template metadata, Markdown markers, digits and citation IDs.
def chinese(s): return len(re.findall('[一-鿿]',s))
counts={'old_chinese_characters':chinese(old),'new_chinese_characters':chinese(new)}
files={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ('claims.json','sources.json','report.json')}
out=json.loads((R/'logs/outcomes.json').read_text())
cmds=json.loads((R/'logs/commands.json').read_text())
out.pop('all_validation_commands_exit_zero',None)
out['final_validation_commands_exit_zero']=all([next(x for x in reversed(cmds) if x['step']==n)['exit_code']==0 for n in ('select','sources-validate','plan-validate','claims-validate','render','archive','archive-show')])
out['earlier_failed_attempts']=[{'step':x['step'],'exit_code':x['exit_code'],'stderr':x['stderr'],'stdout':x['stdout']} for x in cmds if x['exit_code']]
out['earlier_failure_notes']=['First local validation harness incorrectly retained -c as script argv[0], raising FileNotFoundError before product script ran; fixed local harness only. Original select.stderr was overwritten by second attempt before unique retry log naming; command and traceback retained in transcript and this note.','Initial claims validator rejected negative phrase 不能代表市场共识 due to literal 共识 matcher. C7 rewritten as one-person attribution without breadth language; report retains representativeness limitation.']
(R/'logs/outcomes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
meta={'method':'Same agent nonblind replay, identical frozen sources/claims; no additional retrieval, not an old plugin complete run and not a model evaluation','budget':'Both approximately 600 Chinese characters, measured with U+4E00-U+9FFF count; citation IDs, Latin text, digits, punctuation excluded',**counts,'frozen_hashes':files,'verified_selected_sources':5,'claims':7,'fact_claims':3,'view_claims':2,'inference_claims':2,'arithmetic_checks':4,'both_present':{'cash_vs_investment_definition':True,'unreconciled_residual':True,'annual_cash_lease_principal_example':True,'community_attribution_limit':True},'quality_score':None,'quality_inference':'Presentation inspection only; no superiority, alpha, model accuracy, time-saving or scoring claim.'}
(R/'logs/comparison-metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
comparison=f'''# 同一证据的模板回放比较

这是同一代理写的非盲回放，不是旧插件完整运行，也不是模型评测。旧版模板直接来自 baseline.zip 的 skills/research/references/memo-template.md；新版压缩回放保持已渲染报告的回答、三条发现、下一观察与限制结构。两份正文共享冻结的 claims.json 和 sources.json，无额外检索。

预算约 600 汉字。旧稿 {counts['old_chinese_characters']} 个汉字，新稿 {counts['new_chinese_characters']} 个汉字；按 Unicode 中日韩统一表意字符计数，不含英文、数字、标点及引用编号。完整机器报告和证据附录不纳入这次正文比较。

| 可核实观察 | 旧模板回放 | 新模板回放 |
|---|---|---|
| 首段回答 | 先列两个投入数并提示统一口径；具体现金算法在“值得研究的假设” | 首段直接写 CFO 减现金 PP&E 再单列同期融资租赁本金 |
| 验证事实和原文 | 相同：5 个已取原文来源、3 条 fact、2 条 view、2 条 inference | 相同冻结证据 |
| 算术 | 相同：约 7.121B、残差约 0.621B、全年 71.611B 与 69.328B | 相同 4 项独立 Decimal 复算 |
| 与本题有关的内容 | 现金算法完整；定价/对标栏说明未取证，保留模板顺序 | 先给现金算法，再解释差额与未来义务 |
| 社区与失败边界 | 写明 13 条未采用，原帖为补充抓取 | 写明相同边界 |

这只能证明上述内容的位置和是否出现，不能证明读者理解、投资收益、召回完整性或新版优于旧版。没有读者盲评、随机化或独立模型评分。

已知执行成本：9 个逻辑搜索请求＝5 次原生 WebSearch＋引擎实际 2 条 HN 搜索＋2 条直接 Algolia 搜索。请求的引擎计划有 3 条，实际被引擎限制为 2 条。引擎自报 5.3 秒；从检索前 runtime 准备到 archive/show/渲染一致性检查是 {out['elapsed_wall_seconds_from_retrieval_start']} 秒，未含更早的技能阅读与 2 次预检索，亦未含本比较写作；不能作为两版速度对比。隐藏供应商重试不计作已知请求。

渲染、严格来源/结论/计划检查、归档和读取最终退出码均 0。中途失败记录和修复原因在 logs/outcomes.json；渲染器仅检查公式结构，本次另行复算，未证明季度残差原因。
'''
(R/'comparison.md').write_text(comparison)
# Preserve sanitized execution contract without credentials or real-ledger paths.
engine={'runtime':'/Users/frankzhang/.local/bin/python3.12','skill_dir':'/Users/frankzhang/.claude/plugins/cache/last30days-skill/last30days/3.30.0/skills/last30days','engine_argv':['Microsoft capex finance leases cash PP&E cash burden','--research-only','--emit=json','--json-profile=raw','--plan',str(R/'raw/engine-plan.json'),'--search','hackernews','--days=365','--save-dir='],'env_mode':'env -i, retain PATH and HOME only for runtime; TMPDIR live/tmp','overrides':{'LAST30DAYS_CONFIG_DIR':str(R/'runtime-state'),'LAST30DAYS_SKIP_KEYCHAIN':'1','LAST30DAYS_NATIVE_SEARCH':'1','SETUP_COMPLETE':'true','FROM_BROWSER':'off'},'save_resolver_argv':['--resolve-save-dir','--save-dir='],'saved_directory':'','exit_code':0,'isolation_note':'Runtime-only environment overrides, no installed/global config written. Engine was invoked without -I because it imports sibling lib; all locally written Python readers use -I and separate tools directory. No browser/cookie/paid provider was used.'}
(R/'logs/engine-command.json').write_text(json.dumps(engine,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(meta,ensure_ascii=False,indent=2))
