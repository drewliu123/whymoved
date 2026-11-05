import json, subprocess
from pathlib import Path
W=Path('/Users/frankzhang/Desktop/投研助手/journal/work/nasdaq-20261101-wak14q8o')
T=Path('/Users/frankzhang/.claude/plugins/cache/touyan-local/touyan/0.3.1/scripts')
a=json.loads((W/'audit.json').read_text())
# Outputs of each completed command are retained with their real exit codes.
commands=[('final-claims',['check_claims.py',str(W/'claims.json'),'--sources',str(W/'sources.json'),'--json']),('final-render',['render_report.py',str(W/'report.json'),'--claims',str(W/'claims.json'),'--sources',str(W/'sources.json'),'--out-dir',str(W/'output'),'--overwrite'])]
for name,args in commands:
 cmd=['python3',str(T/args[0])]+args[1:];p=subprocess.run(cmd,text=True,capture_output=True);(W/(name+'.log')).write_text(p.stdout+p.stderr);a['execution'].append({'command':cmd,'exit_code':p.returncode,'log':name+'.log'});(W/'audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n');print(p.stdout,p.stderr)
 if p.returncode:raise SystemExit(p.returncode)
cmd=['python3',str(T/'research_run.py'),'archive','--report',str(W/'report.json'),'--claims',str(W/'claims.json'),'--sources',str(W/'sources.json'),'--plan',str(W/'plan.json'),'--audit',str(W/'audit.json')]
p=subprocess.run(cmd,text=True,capture_output=True);(W/'archive-result.json').write_text(p.stdout);(W/'archive-stderr.log').write_text(p.stderr);print(p.stdout,p.stderr);raise SystemExit(p.returncode)
