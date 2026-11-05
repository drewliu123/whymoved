import os, sys, json, pathlib, subprocess, time, shlex, signal
BASE=pathlib.Path('/Users/frankzhang/Desktop/投研助手/journal/nvda-full-runs-20261031/run-0.1.1/community')
SKILL=pathlib.Path('/Users/frankzhang/.claude/plugins/cache/last30days-skill/last30days/3.30.0/skills/last30days')
PYTHON='/Users/frankzhang/.local/bin/python3.12'
assert sys.version_info >= (3,12)
sys.path.insert(0,str(SKILL/'scripts'))
from lib.env import load_env_file
child_env=dict(os.environ)
for key,value in load_env_file(pathlib.Path('/Users/frankzhang/.config/last30days/.env')).items():
    child_env.setdefault(key,value)
child_env.update({'HOME':str(BASE/'runtime/home'),'XDG_CONFIG_HOME':str(BASE/'runtime/config'),'XDG_CACHE_HOME':str(BASE/'runtime/cache'),'XDG_DATA_HOME':str(BASE/'runtime/data'),'TMPDIR':str(BASE/'runtime/tmp'),'LAST30DAYS_CONFIG_DIR':str(BASE/'runtime/config'),'LAST30DAYS_MEMORY_DIR':'','LAST30DAYS_LIBRARY_CONTEXT':'off','LAST30DAYS_NATIVE_SEARCH':'1','LAST30DAYS_TRUST_PROJECT_CONFIG':'0','PYTHONDONTWRITEBYTECODE':'1','LAST30DAYS_REPORT_CACHE_TTL_SECONDS':'0','FROM_BROWSER':'','LAST30DAYS_FROM_BROWSER':'','LAST30DAYS_X_COOKIE_ACCESS_DENIED':'true'})
phase=sys.argv[1]
if phase=='diagnose':
    args=['--diagnose','--no-browser-cookies']; limit=45
elif phase=='engine':
    args=['NVIDIA NVDA 英伟达','--emit=compact','--save-dir=','--quick','--no-browser-cookies','--no-verify-freshness','--as-of=2026-10-31','--days=30','--plan',sys.argv[2],'--dedicated-subreddits=NVDA','--subreddits=stocks,investing,wallstreetbets,SecurityAnalysis','--search',sys.argv[3]]; limit=165
else: raise ValueError(phase)
cmd=[PYTHON,'-I','-B',str(SKILL/'scripts/last30days.py')]+args
out=BASE/'raw'/phase
meta={'phase':phase,'command':shlex.join(cmd),'environment_overrides':{k:child_env[k] for k in ['HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_DATA_HOME','TMPDIR','LAST30DAYS_CONFIG_DIR','LAST30DAYS_MEMORY_DIR','LAST30DAYS_LIBRARY_CONTEXT','LAST30DAYS_NATIVE_SEARCH','LAST30DAYS_TRUST_PROJECT_CONFIG','PYTHONDONTWRITEBYTECODE','LAST30DAYS_REPORT_CACHE_TTL_SECONDS']},'credential_config_read_only':'/Users/frankzhang/.config/last30days/.env','timeout_seconds':limit,'started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
(out/'command.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
started=time.monotonic()
with (out/'stdout.txt').open('wb') as stdout, (out/'stderr.txt').open('wb') as stderr:
    proc=subprocess.Popen(cmd,stdout=stdout,stderr=stderr,env=child_env,cwd=BASE/'runtime/work',start_new_session=True)
    try:
        rc=proc.wait(timeout=limit); timed_out=False
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid,signal.SIGTERM)
        try: proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGKILL); proc.wait()
        rc=124; timed_out=True
meta.update({'exit_code':rc,'child_returncode':proc.returncode,'timed_out':timed_out,'elapsed_seconds':round(time.monotonic()-started,3),'stdout':str(out/'stdout.txt'),'stderr':str(out/'stderr.txt')})
(out/'result.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print(json.dumps(meta,ensure_ascii=False))
sys.exit(rc)
