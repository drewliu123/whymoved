import hashlib
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parent
home = root.parent.parent
plugin = Path('/Users/frankzhang/.claude/plugins/cache/touyan-local/touyan')
execution = json.loads((root / 'execution.json').read_text())
execution['commands'].extend([
    {'command': 'Polymarket supplemental search NVIDIA revenue earnings', 'exit_code': 2, 'result': 'SSL EOF occurred in violation of protocol；不视为不存在匹配市场'},
    {'command': 'ego-browser nodejs -e save Zacks (initial)', 'exit_code': 1, 'result': 'shell unmatched quote；未执行保存，已用heredoc修复'},
    {'command': 'ego-browser nodejs heredoc save Zacks and finish taskSpace(10)', 'exit_code': 0, 'result': '保存5631字符正文，时间2026-10-31T05:09:20.343Z；TaskSpace已finish'},
    {'command': 'forecast.py finalize forecast.json --claims claims.json', 'exit_code': 0, 'result': 'H1=0.82；H2=0.6767；所引证据哈希写入'},
])

def run(label, cmd):
    r = subprocess.run(cmd, text=True, capture_output=True)
    log = root / (label + '.log')
    log.write_text('$ ' + shlex.join(cmd) + '\n' + r.stdout + r.stderr + '\nexit_code=' + str(r.returncode) + '\n')
    execution['commands'].append(dict(command=shlex.join(cmd), exit_code=r.returncode, log=log.name))
    print(label, 'exit_code=' + str(r.returncode), r.stdout.strip())
    if r.returncode:
        execution['research_validation'] = 'failed'
        (root / 'execution.json').write_text(json.dumps(execution, ensure_ascii=False, indent=2) + '\n')
        raise SystemExit(r.returncode)
    return r.stdout

for version in ['0.1.1', '0.2.0']:
    run('claims-' + version, [sys.executable, str(plugin / version / 'scripts/check_claims.py'), str(root / 'claims.json'), '--json'])
run('forecast-check', [sys.executable, str(plugin / '0.2.0/scripts/forecast.py'), 'check', str(root / 'forecast.json'), '--claims', str(root / 'claims.json')])
ledger = json.loads((root / 'claims.json').read_text())
ids = {c['id'] for c in ledger['claims']}
for name in ['memo-0.1.1.md', 'memo-0.2.0.md', 'comparison.md']:
    refs = set(re.findall(r'\bC\d+\b', (root / name).read_text()))
    if refs - ids:
        raise SystemExit('Unknown references: ' + str(refs - ids))
forecasts = json.loads((root / 'forecast.json').read_text())
memo = json.loads((root / 'memo-0.2.0.json').read_text())
assert {h['id'] for h in memo['hypotheses']} == {f['hypothesis_id'] for f in forecasts['forecasts']}
for h in memo['hypotheses']:
    fc = next(f for f in forecasts['forecasts'] if f['hypothesis_id'] == h['id'])
    assert h['my_prob'] == fc['final_prob']

journal = home / 'journal/memos.jsonl'
before_bytes = journal.read_bytes() if journal.exists() else b''
before = [json.loads(s) for s in before_bytes.splitlines() if s.strip()]
output = run('journal-add', [sys.executable, str(plugin / '0.2.0/scripts/journal.py'), 'add', str(root / 'memo-0.2.0.json'), '--claims', str(root / 'claims.json'), '--report', str(root / 'memo-0.2.0.md'), '--plan', str(root / 'plan.json'), '--forecast', str(root / 'forecast.json')])
after = [json.loads(s) for s in journal.read_bytes().splitlines() if s.strip()]
assert len(after) == len(before) + 1 and after[:-1] == before, 'Existing journal records changed'
mid = after[-1]['memo_id']
archive = home / 'journal' / mid
for src, dest in [('claims.json','claims.json'),('forecast.json','forecast.json'),('plan.json','plan.json'),('memo-0.2.0.json','memo.json'),('memo-0.2.0.md','memo.md')]:
    assert (root / src).read_bytes() == (archive / dest).read_bytes(), 'Archive copy differs'
execution.update(research_validation='passed', plugin_unit_tests='not_run: research execution only, no plugin code changed', memo_id=mid, archive=str(archive), prior_journal_rows=len(before), current_journal_rows=len(after), existing_journal_records_unchanged=True)
execution['integrity'] = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in ['claims.json','forecast.json','forecast-input-H2.json','memo-0.1.1.md','memo-0.2.0.md']}
(root / 'execution.json').write_text(json.dumps(execution, ensure_ascii=False, indent=2) + '\n')
with (root / 'comparison.md').open('a') as f:
    f.write('\n正式归档：' + mid + '（journal/' + mid + '/）。原有' + str(len(before)) + '条备忘录完整保留；只追加1条新版备忘录、2条假设。两版18条证据校验、概率复算及归档均退出0，日志在本目录。\n')
print('Archive verified:', mid, 'prior records preserved:', len(before))
