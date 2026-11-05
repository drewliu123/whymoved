from pathlib import Path
R=Path('/Users/frankzhang/Desktop/投研助手/journal/four-type-validation-20261031/actor')
p=R/'work/build_case.py'
s=p.read_text()
changes=[
("FY26 Q4为410、358、56亿美元。","FY26 Q4为410、358、56亿美元。FY26 Q2 CFO明确预计下一季capex环比下降。"),
("'S3-L299','S4-L263'","'S3-L299','S3-L353','S4-L263'"),
("所读六次电话会未提供新增AI投资批次的数值ROI、现金回收期或增量NOPAT/投入资本配对表。',['S5','S6']","本轮六份电话会未提供可计算新增AI资本回报的资本—增量利润/现金配对数据，其他公开披露未穷尽；S1中CFO称good ROI today，S6中CFO称高质量模型带来良好利润率，这些正向自述也应保留，披露粒度不足不等于回报差。',['S1','S5','S6']"),
("['S5-L576','S5-L580','S6-L259'","['S1-L515','S5-L576','S5-L580','S6-L409','S6-L259'"),
("扩张投入的方向已有真实执行与部分新增产能支持；但兑现应分层：投入已执行，部分产能已形成，商业化已有信号，新增AI投资回报尚无法闭环。","扩张投入的方向已有支出执行支持；据管理层披露部分新增产能已形成，商业化已有信号，但具体新增AI批次可售GPU容量/利用率未核实。本轮六份电话会缺可计算新增AI资本回报的配对数据，其他公开披露未穷尽。"),
("前一段属管理层说明的租赁分类口径变化，后一段属交付延期；但FY27 Q1开支低于指引也意味着执行时间并未完全兑现。","据管理层解释，前一段属租赁分类口径变化，后一段属交付延期；该解释未经独立经济归因验证，也未排除需求同时变化。FY27 Q1开支低于指引意味着原金额安排未完全兑现。"),
("且披露没有AI专属资本和可归属利润。","且本轮六份电话会没有AI专属资本和可归属利润的配对数据；未穷尽其他公开披露，也不据此判定回报差。"),
("若延期未恢复或单位经济恶化，应下调兑现判断。","同口径FY27 Q2实际capex若≤500亿美元，超过500亿美元的金额指引即未兑现；延期容量若再移至2027年7月以后或取消，则FY27 H2交付安排未兑现；无披露仅算未核实。单位经济恶化应下调回报判断。"),
("'description':'日历年2026指引修订差额'","'description':'日历年2026指引差额（原因标签据管理层解释）'"),
("'qualification':'guidance changes not realized savings; periods identical but scope changes at first revision'","'qualification':'Arithmetic guidance differences only; classification/delivery cause labels follow management explanations, not independently verified economic attribution; demand may also change. Not realized savings; first revision changes scope.'"),
("扩大投入已经落实到实际支出和部分上线产能，商业化也出现可观察进展；但新增AI资本的回报尚未被公开披露闭环证明。最新季度开支低于指引体现交付时间仍有缺口，日历年指引下调还混合了租赁分类变化，不能直接解释成需求收缩。","扩大投入已有实际支出支持；据管理层披露，部分产能已上线、商业化已有进展，具体新增AI批次可售GPU容量/利用率未核实。本轮六份电话会未提供可计算新增AI资本回报的配对数据，其他公开披露未穷尽，披露不足不等于回报差。最新季度开支低于指引；据管理层解释，日历年指引下调分别涉及分类变化和交付延期，该解释未经独立验证，也不能排除需求同时变化。"),
("连续季度新增GW容量和数据中心说明部分产能确已形成；Azure/Foundry有变现信号。","据管理层连续披露的新增GW容量和数据中心，部分产能已形成；具体新增AI批次可售GPU容量/利用率未核实，Azure/Foundry有变现信号。"),
("10月改1700亿美元则归因交付延后。","10月改1700亿美元据管理层解释归因于交付延后。两次修订的原因均为管理层解释，本轮未独立验证经济归因，也未排除需求同时变化。"),
("7月的下调有明确租赁分类说明，10月有明确第三方延迟说明；需求弱化不是当前证据支持最强的单一解释。但交付延期本身会推后产能，若后续承诺容量仍未上线且订单/价格走弱，就应将解释转向需求或执行能力问题。","据管理层解释，7月下调涉及租赁分类，10月涉及第三方延迟；这些原因标签未经独立验证，不能排除同期需求变化。交付延期本身也推后产能，若后续承诺容量仍未上线且订单/价格走弱，应提高需求或执行能力问题的权重。"),
("最新电话会直接承认原有CPU容量、GPU效率和token定价贡献。它支持商业化改善，也削弱“当季增长全部由新增AI资本创造”的归因。若价格恢复正常后仍有可归属的利用率、毛利和现金改善，才加强回报兑现判断。","最新电话会直接承认原有CPU容量、GPU效率和token定价贡献。最强正向反方也应保留：CFO在S1-L515称good ROI today，在S6-L409称高质量模型及较高token定价带来良好利润率；本轮配对数据不足不等于回报差。这些表述支持商业化与回报潜力，却无法把当季增长全部归于新增AI资本。后续可归属利用率、毛利和现金改善会加强回报兑现判断。"),
("若继续延期而供给缺口不收敛，下调执行兑现；若如期上线并被使用，提高产能兑现判断。Q2及H2尚未完成。","同口径FY27 Q2实际capex若≤500亿美元，则超过500亿美元金额指引未兑现；延期容量若再移至2027年7月以后或取消，则FY27 H2交付安排未兑现。无披露仅算未核实；如期上线并被使用则提高产能兑现判断。Q2及H2尚未完成。"),
("未取得新增AI批次资本、可归属增量利润/现金、租赁完整支付和电力/芯片细项，不能计算AI ROI、ROIC或回收期；数据中心数量不能换算AI可售容量。","本轮六份电话会未取得新增AI批次资本与可归属增量利润/现金的配对数据，其他公开披露未穷尽；租赁完整支付和电力/芯片细项也不足，不能据此计算AI ROI、ROIC或回收期。具体新增AI批次可售GPU容量/利用率未核实；披露粒度不足不等于回报差。"),
("自审完成但未另做独立审查；这是单个人工协调开发案例，不证明预测能力、自动化或泛化效果。","已按协调方转达的独立审查六项意见定向修正，处理记录见independent-review.md；未扩展检索，也未声称因此完成全面独立事实审计。这是人工协调开发案例，不证明预测能力、自动化或泛化效果。"),
("'status':'部分形成；未把计划Fairwater算成完成'","'status':'据管理层披露部分形成；新增AI批次可售GPU容量/利用率未核实；未把计划Fairwater算成完成'"),
("'status':'未闭环证明'","'status':'本轮六份电话会无可计算配对数据；其他公开披露未穷尽；不等于回报差'"),
("新增数据中心/GW支持部分产能形成，却没有披露对应AI可售GPU容量。","据管理层披露新增数据中心/GW支持部分产能形成，但具体新增AI批次可售GPU容量/利用率未核实。"),
("数据中心/GW不等于AI可售GPU容量。","据管理层披露的数据中心/GW不等于具体新增AI批次可售GPU容量，后者及利用率未核实。")]
for old,new in changes:
    if old not in s:raise ValueError('missing target '+old[:90])
    s=s.replace(old,new)
p.write_text(s)
p=R/'work/validate_case.py';s=p.read_text()
s=s.replace('no image export, no independent review; this is human-coordinated content validation','no image export; coordinator-relayed independent review corrections recorded, not a full independent audit; this is human-coordinated content validation')
s=s.replace("'self_challenge':{'independent':False,", "'independent_review_followup':{'status':'six coordinator-relayed corrections addressed','record':'independent-review.md','new_retrieval':False},'self_challenge':{'independent':False,")
p.write_text(s)
print('Applied six review themes; preserved 27 claim IDs and six sources.')
