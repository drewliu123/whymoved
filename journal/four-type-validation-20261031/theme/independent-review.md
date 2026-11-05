# Theme 独立审查定向修正记录

父任务独立审查提出四项修正；本案例执行修正，未新增检索或来源。证据截点仍为2026-10-31T17:25:57Z，不将修改时间当成新证据时间。

| 项目 | 修正与核对 | 状态 |
| --- | --- | --- |
| 因果识别 | answer、current_judgment、C16及机制连线收紧为订单与收入增长披露、分部利润率恢复，与交付爬坡改善相容；没有识别同批订单转换，价格、组合、并购基数可解释部分变化。 | 已落实 |
| 增量利润比较范围 | Q1 Americas销售增20%含有机14、并购5、汇率1个百分点；Q2增18%全有机。C11、正文、表注、calculations及datasets声明未经恒定范围调整，3.05%→16.81%不能单独证明交付效率改善。原文位于Q1 presentation p9、Q2 presentation p8。 | 已落实 |
| Corporate成本边界 | Q2 complete p13及p8显示Fibrebond员工交易/留任等并购费用计Corporate Other expense，摊销与重组也列Corporate。C10、正文和表注说明分部利润未包括这些全经济成本；不能将全部Corporate归AI。 | 已落实 |
| 基点及半年验收 | K4实际+192.6221bp、K5实际−192.5354bp，均展示约193bp，公司取整+190/−200bp保留。watch及正文要求待Q3/Q4数据齐备后按(Q3OP+Q4OP)/(Q3sales+Q4sales)>30%检验下半年展望；单季不能验收半年，未虚构Q4官方发布日期。 | 已落实 |

修正由冻结report.json重新生成report.md；运行现有check_claims.py的23条校验及JSON引用、来源哈希、Markdown同源检查。最终结果以validation.json及logs/check_claims.log为准。本记录说明审查意见已处理，不代替父任务最终独立复审或HTML验收。
