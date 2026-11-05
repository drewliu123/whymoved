# -*- coding: utf-8 -*-
from pathlib import Path
p=Path('/Users/frankzhang/Desktop/投研助手/journal/four-type-validation-20261031/theme/work/build_case.py')
s=p.read_text()
def replace(a,b):
 global s
 assert a in s,a
 s=s.replace(a,b)
replace("'分部经营利润与全公司净利润、现金不是同一量度。'","'分部经营利润与全公司净利润、现金不是同一量度。'") if False else None
replace('分部经营利润与全公司净利润、现金不是同一量度。','Fibrebond员工交易/留任等并购相关费用在分部信息中计为Corporate Other expense，摊销与重组亦列Corporate；分部利润未包含这些全经济成本，不等于全公司净利润或现金，Corporate全部费用不能归AI。')
replace('Q2利润率环比改善约192基点但同比仍低约194基点','Q2利润率环比改善约193基点但同比仍低约193基点')
replace('取整表述为+190/-200基点。','公司按披露利润率取整表述为+190/-200基点。Q1销售增20%含有机14、并购5、汇率1个百分点；Q2增18%全为有机。两个增量比率未经范围调整，不能单独证明效率改善。')
replace('已有订单和收入证据，但AI独立盈利归因尚未建立。','已有订单与收入增长披露及分部利润率恢复，与交付爬坡改善相容；未识别同批订单转换，价格、组合及并购基数亦可解释，AI独立盈利归因尚未建立。')
replace('全分部同比桥，非AI项目边际利润率；未剔价格/并购/产品组合','全分部同比桥，非AI项目边际利润率。Q1销售增长20%含有机14、并购5、汇率1个百分点；Q2增长18%全有机，未经范围调整；未剔价格/产品组合，不能独立证明交付效率改善')
replace('订单与交付增长已有实证，利润兑现正在改善但尚未完成。','公司披露订单与收入增长，分部利润率出现恢复，与交付爬坡改善相容；尚未识别同批订单向收入的转换，价格、组合及并购基数也可解释部分变化。')
replace('季度同比用于经营比较，环比用于观察爬坡，不能混同。','季度同比用于经营比较，环比用于观察恢复，不能混同；同名分部不等于已剔除并购/汇率的恒定范围。')
replace('Q2平均利润率较Q1恢复约192基点，但较上年同期仍低约194基点','Q2平均利润率较Q1恢复约193基点，但较上年同期仍低约193基点')
replace('这是交付执行改善的证据，却不足以证明稀缺溢价扩大：','Q1销售增20%含有机14、并购5、汇率1个百分点，Q2增18%全有机；3.05%和16.81%的比率未经范围调整。分部利润率恢复与交付爬坡改善相容，但没有识别同批订单转换，价格、组合及并购基数也可解释部分变化，不能独立证明效率提升或稀缺溢价扩大：')
replace('下一次披露应检验而不能提前确认。','需在Q3和Q4实际数据齐备后，按(Q3经营利润+Q4经营利润)/(Q3销售+Q4销售)>30%检验；单季结果不能判断整个下半年展望兑现。')
replace('并购、利息、摊销等使分部利润不能直接替代股东盈利。','并购、利息、摊销等使分部利润不能直接替代股东盈利。分部信息将Fibrebond员工交易/留任费用等并购相关支出列在Corporate Other expense，摊销与重组也列Corporate；分部利润因此不是包含这些费用的全经济成本后利润。不能把全部Corporate费用归给AI。')
replace('以Q1的3.05%、Q2的16.81%为已实现参照，核对下半年>30%利润率展望。','以未经范围调整的Q1 3.05%、Q2 16.81%为已实现参照。下半年>30%须待Q3/Q4数据齐备后按(Q3经营利润+Q4经营利润)/(Q3销售+Q4销售)核对，不能用单季替代半年；本次仅核实Q3发布日期，不推测Q4发布日期。')
replace('订单→收入已支持；利润恢复有迹象；纯AI增量利润和现金归因未证实','订单与收入增长披露、分部利润率恢复，与交付爬坡改善相容；同批订单转换及纯AI增量利润/现金归因未识别')
replace('共同变化支持，非项目因果识别','共同变化与交付爬坡改善相容；非同批订单转换或项目因果识别')
replace('表格来源：[C2–C5、C9]；季度流量与期末存量分开；利润率按披露取整。','表格来源：[C2–C5、C9–C11]；季度流量与期末存量分开；利润率按披露取整。Q1美洲销售增20%含有机14/并购5/汇率1个百分点，Q2增18%全有机，增量利润比率未经范围调整。分部利润未包含列Corporate的并购相关费用（含Fibrebond员工交易/留任）、摊销和重组，不是全经济成本后利润；不将Corporate全部归AI。')
replace('独立审查与HTML由父任务统一完成；本目录未做浏览器呈现验收。','父任务独立审查提出四项定向修正，本轮已落实并记录independent-review.md；HTML与浏览器呈现验收仍由父任务统一完成。')
# Add original source excerpts without increasing six adopted source documents.
replace("# Excerpts transcribed from chart images explicitly mark that distinction; original PDF remains available.","""S[2]['excerpts'].append(dict(locator='p9 Sales Growth',original='Sales Growth:\\nOrganic 14%\\nAcquisition 5%\\nForex 1%\\nTotal 20%'))
S[4]['excerpts'].append(dict(locator='p8 Sales Growth',original='Sales Growth:\\nOrganic 18%\\nAcquisition 0%\\nForex 0%\\nTotal 18%'))
S[3]['excerpts'].append(dict(locator='p13 acquisition charges / p8 Corporate; see raw/eaton-q2/complete.txt lines440–447',original='Employee transaction and retention award compensation expense related to the acquisition of Fibrebond of $27 million and $39 million in the second quarter and the first six months of 2026, respectively, and $47 million in the second quarter and the first six months of 2025.\\nCharges in 2026 and 2025 were included in Cost of products sold, Selling and administrative expense, Research and development expense, or Other expense (income) - net. In Business Segment Information, the charges were included in Other expense - net.'))
# Excerpts transcribed from chart images explicitly mark that distinction; original PDF remains available.""")
replace("title='同口径经营对照：Electrical Americas'","title='同分部经营对照：Electrical Americas（未作恒定范围调整）'")
replace("title='Electrical Americas同口径已实现数据'","title='Electrical Americas已实现数据（同分部，未作恒定范围调整）'")
replace('不把分部增量当AI利润','不把分部增量当AI利润；Q1销售增20%含有机14/并购5/汇率1个百分点，Q2增18%全有机，未经恒定范围调整')
p.write_text(s,encoding='utf-8')
q=p.parent/'verify_case.py';v=q.read_text();v=v.replace('未执行；用户本轮禁止再委派，父任务统一审查','父任务独立审查四项定向修正已落实；见independent-review.md；未宣称额外独立复审通过');q.write_text(v,encoding='utf-8')
print('Targeted review corrections applied to generators')
