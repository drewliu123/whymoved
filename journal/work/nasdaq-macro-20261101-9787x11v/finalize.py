# -*- coding: utf-8 -*-
import json, subprocess
from pathlib import Path
W=Path('/Users/frankzhang/Desktop/投研助手/journal/work/nasdaq-macro-20261101-9787x11v')
T=Path('/Users/frankzhang/.claude/plugins/cache/touyan-local/touyan/0.3.1/scripts')
a=json.loads((W/'audit.json').read_text())
for name,args in [('claims-final',['check_claims.py',str(W/'claims.json'),'--sources',str(W/'sources.json'),'--json']),('render',['render_report.py',str(W/'report.json'),'--claims',str(W/'claims.json'),'--sources',str(W/'sources.json'),'--out-dir',str(W/'output')])]:
 cmd=['python3',str(T/args[0])]+args[1:];p=subprocess.run(cmd,text=True,capture_output=True);(W/(name+'.log')).write_text(p.stdout+p.stderr);a['execution'].append({'command':cmd,'exit_code':p.returncode,'log':name+'.log'});(W/'audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');print(p.stdout,p.stderr)
 if p.returncode:raise SystemExit(p.returncode)
cmd=['python3',str(T/'research_run.py'),'update','--parent-run','R20261102T030116Z-228fb61e7831','--report',str(W/'report.json'),'--claims',str(W/'claims.json'),'--sources',str(W/'sources.json'),'--plan',str(W/'plan.json'),'--audit',str(W/'audit.json')]
p=subprocess.run(cmd,text=True,capture_output=True);(W/'archive-result.json').write_text(p.stdout);(W/'archive-stderr.log').write_text(p.stderr);print(p.stdout,p.stderr);raise SystemExit(p.returncode)
