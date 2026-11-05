# -*- coding: utf-8 -*-
import json, subprocess, sys
from pathlib import Path
w=Path('/Users/frankzhang/Desktop/投研助手/journal/work/20261102-warsh')
t=Path('/Users/frankzhang/.claude/plugins/cache/touyan-local/touyan/0.4.1/scripts')
a=json.loads((w/'audit.json').read_text())
commands=[['research_plan.py',str(w/'plan.json')],['sources.py','validate',str(w/'sources.json')],['check_claims.py',str(w/'claims.json'),'--sources',str(w/'sources.json'),'--json'],['analysis_contract.py','check','--plan',str(w/'plan.json'),'--report',str(w/'report.json'),'--claims',str(w/'claims.json'),'--sources',str(w/'sources.json')]]
for i,args in enumerate(commands):
 cmd=[sys.executable,str(t/args[0])]+args[1:]
 r=subprocess.run(cmd,capture_output=True,text=True)
 log=w/('validation-%d.log'%i);log.write_text(r.stdout+r.stderr)
 a['execution'].append(dict(command=cmd,exit_code=r.returncode,log=str(log)))
 print(args[0],r.returncode)
 if r.returncode:
  (w/'audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');sys.exit(r.returncode)
(w/'audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
