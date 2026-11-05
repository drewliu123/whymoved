# -*- coding: utf-8 -*-
from pathlib import Path
import hashlib,json
w=Path('/Users/frankzhang/Desktop/投研助手/journal/work/meta-nov-20261102')
d=Path('/Users/frankzhang/Desktop/投研助手/delivery/meta-nov-20261102')
d.mkdir(parents=True,exist_ok=True)
for ext,start,end,appendix,rename in [
    ('md','## 分析判断\n','### 11月2日开盘前盘口与研究排序','## 附录：机会判断与触发条件','## 附录：价格评估与计算明细\n'),
    ('html','<h2>分析判断</h2>','<div class="table-wrap"><table><caption>11月2日开盘前盘口与研究排序','<h2>附录：机会判断与触发条件</h2>','<h2>附录：价格评估与计算明细</h2>')]:
    s=(w/f'output/report.{ext}').read_text()
    a=s.index(start); b=s.index(end,a)
    block=s[a:b].replace(start,rename,1)
    s=s[:a]+s[b:]
    pos=s.index(appendix)
    s=s[:pos]+block+'\n'+s[pos:]
    (d/f'META-2026-11-research.{ext}').write_text(s)
manifest={'frozen_report_sha256':hashlib.sha256((w/'report.json').read_bytes()).hexdigest(),'transformation':'Only move price-assessment and calculation-detail sections into appendix, identically in Markdown and HTML. No claim or number added or removed.','files':[str(d/'META-2026-11-research.md'),str(d/'META-2026-11-research.html')]}
(d/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps(manifest,ensure_ascii=False))
