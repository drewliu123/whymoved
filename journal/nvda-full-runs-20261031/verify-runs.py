import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parent
plugin = Path('/Users/frankzhang/.claude/plugins/cache/touyan-local/touyan')
formal_home = root.parent.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if '--baseline' in sys.argv:
    files = [formal_home / 'data/authors.json', formal_home / 'journal/memos.jsonl']
    baseline = {str(p): sha(p) for p in files if p.is_file()}
    (root / 'formal-data-baseline.json').write_text(json.dumps(baseline, indent=2) + '\n')
    print('Saved formal data hashes; research agents write separate run homes.')
    raise SystemExit(0)

result = {'runs': {}, 'formal_data_unchanged': None}
for version in ['0.1.1', '0.2.0']:
    home = root / ('run-' + version)
    env = dict(os.environ, TOUYAN_HOME=str(home))
    required = ['plan.json', 'claims.json', 'memo.json', 'memo.md', 'execution.json']
    if version == '0.2.0':
        required.append('forecast.json')
    status = {'missing': [n for n in required if not (home / n).is_file()], 'checks': []}
    result['runs'][version] = status
    if status['missing']:
        continue
    ledger = json.loads((home / 'claims.json').read_text())
    memo = json.loads((home / 'memo.json').read_text())
    text = (home / 'memo.md').read_text()
    ids = {c['id'] for c in ledger.get('claims', [])}
    status.update(claim_count=len(ids), hypothesis_count=len(memo.get('hypotheses', [])), report_characters=len(text), unresolved_claim_refs=sorted(set(re.findall(r'\bC\d+\b', text)) - ids), markdown_links=len(re.findall(r'\[[^\]]+\]\(https?://', text)))
    commands = [[sys.executable, str(plugin / version / 'scripts/check_claims.py'), str(home / 'claims.json'), '--json']]
    if version == '0.2.0':
        commands.append([sys.executable, str(plugin / version / 'scripts/forecast.py'), 'check', str(home / 'forecast.json'), '--claims', str(home / 'claims.json')])
    for command in commands:
        r = subprocess.run(command, text=True, capture_output=True, env=env)
        status['checks'].append({'command': command, 'exit_code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
    path = home / 'journal/memos.jsonl'
    rows = [json.loads(s) for s in path.read_text().splitlines() if s.strip()] if path.exists() else []
    status['registered_memos'] = [r.get('memo_id') for r in rows]
    status['archive_matches'] = []
    for row in rows:
        archive = home / 'journal' / row.get('archive', row['memo_id'])
        status['archive_matches'].append({name: (archive / name).is_file() and (home / name).read_bytes() == (archive / name).read_bytes() for name in ['memo.json', 'memo.md', 'claims.json', 'plan.json']})
    if version == '0.2.0':
        fc = json.loads((home / 'forecast.json').read_text())
        finals = {f['hypothesis_id']: f for f in fc.get('forecasts', [])}
        status['all_hypotheses_have_forecast'] = all(h['id'] in finals for h in memo.get('hypotheses', []))
        status['all_probabilities_match'] = all(h.get('my_prob') == finals.get(h['id'], {}).get('final_prob') for h in memo.get('hypotheses', []))
baseline = json.loads((root / 'formal-data-baseline.json').read_text())
result['formal_data_unchanged'] = all(Path(p).is_file() and sha(Path(p)) == h for p, h in baseline.items())
(root / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False, indent=2))
