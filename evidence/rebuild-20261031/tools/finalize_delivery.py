"""Assemble local delivery from explicit allowlists; never read private ledger bodies."""
import datetime
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path('/Users/frankzhang/Desktop/投研助手')
EVIDENCE = ROOT / 'evidence/rebuild-20261031'
LIVE = EVIDENCE / 'live'
DELIVERY = ROOT / 'delivery'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def source_files():
    files = [ROOT / 'README.md']
    for folder, suffixes in (('.claude-plugin', {'.json'}), ('agents', {'.md'}), ('skills', {'.md'}), ('scripts', {'.py'}), ('tests', {'.py'})):
        files.extend(p for p in (ROOT / folder).rglob('*') if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts)
    assert all(not p.is_symlink() for p in files)
    return sorted(files)

def verify():
    target = EVIDENCE / 'final-e2e'
    target.mkdir(exist_ok=False)
    work = target / 'inputs'
    work.mkdir()
    home = target / 'home'
    env = dict(os.environ, TOUYAN_HOME=str(home), PYTHONDONTWRITEBYTECODE='1')
    steps = []
    def run(label, args):
        argv = [sys.executable, str(ROOT / 'scripts/research_run.py')] + args
        result = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True)
        (target / (label + '.stdout')).write_text(result.stdout, encoding='utf-8')
        (target / (label + '.stderr')).write_text(result.stderr, encoding='utf-8')
        steps.append({'step': label, 'command': argv, 'exit_code': result.returncode})
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)
    base = []
    for field in ('report', 'claims', 'sources', 'plan', 'calculations', 'audit'):
        base.extend(['--' + field, str(LIVE / (field + '.json'))])
    parent = run('archive', ['archive'] + base)
    parent_path = Path(parent['path'])
    before = {p.name: digest(p.read_bytes()) for p in parent_path.iterdir()}
    report = json.loads((LIVE / 'report.json').read_text())
    report['update'] = {'judgment_changed': False, 'reason': '操作回放：同一冻结证据，无新增检索或研究判断。', 'comparability': {'status': 'comparable', 'reason': '同一期间、单位和研究范围；仅验证更新流程。'}}
    dump(work / 'report.json', report)
    update_args = list(base)
    update_args[1] = str(work / 'report.json')
    child = run('update', ['update'] + update_args + ['--parent-run', parent['run_id']])
    loaded = run('show', ['show', child['run_id']])
    listed = run('list', ['list'])
    after = {p.name: digest(p.read_bytes()) for p in parent_path.iterdir()}
    assert before == after
    assert loaded['manifest']['parent_run'] == parent['run_id']
    assert loaded['diff']['claims'] == {'added': [], 'removed': [], 'changed': []}
    assert len(listed) == 2
    dump(target / 'results.json', {'passed': True, 'kind': 'same-evidence operational replay, not fresh research', 'parent_run': parent['run_id'], 'child_run': child['run_id'], 'parent_bytes_unchanged': True, 'commands': steps})
    print(json.dumps({'passed': True, 'commands': len(steps), 'parent': parent['run_id'], 'child': child['run_id']}))

def package():
    DELIVERY.mkdir(exist_ok=False)
    baseline = json.loads((EVIDENCE / 'baseline-manifest.json').read_text())
    protected = {name: {'expected': expected, 'actual': digest((ROOT / name).read_bytes())} for name, expected in baseline['protected_data'].items()}
    assert all(v['expected'] == v['actual'] for v in protected.values())
    reviewed = {'scripts/sources.py': 'af515463667c7d5bc6f904c163acd424adf48c3c0b94990757a4b5e172bb0671', 'scripts/check_claims.py': '13ad8ce4747c33800c640a727fc04038ae276b5bd01844b3483d0ef1907bbb1d', 'scripts/render_report.py': '3bae4155341e63132d391e3fa850a2569174d7d15f202f3c26aa5323cd995994', 'scripts/research_run.py': '078f5598a5943fd3d00fb57e83925dd4bebf37334b732cf898fdce6af7d6ac33', 'scripts/research_plan.py': 'd6bc0f8b8323c49eef07c42d2d3be60f9443b3a7e2233aaaa987a81ba195ef41', 'skills/research/SKILL.md': '3e1a653b6d869b51e5a10c3ef72e62fa82709741877b37d0b27e7eb0aa7e9c4c'}
    assert all(digest((ROOT / name).read_bytes()) == value for name, value in reviewed.items())
    files = source_files()
    manifest = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in files}
    dump(EVIDENCE / 'final-integrity.json', {'protected_data_unchanged': True, 'protected_data': protected, 'reviewed_hashes_match': True, 'source_files': manifest})
    delta = []
    changes = {'added': [], 'modified': [], 'unchanged': [], 'removed': []}
    with zipfile.ZipFile(EVIDENCE / 'baseline.zip') as baseline_zip:
        for name in sorted(set(manifest) | set(baseline['source_files'])):
            original = baseline_zip.read(name).decode('utf-8') if name in baseline['source_files'] else ''
            current = (ROOT / name).read_text(encoding='utf-8') if name in manifest else ''
            state = 'added' if name not in baseline['source_files'] else 'removed' if name not in manifest else 'unchanged' if original == current else 'modified'
            changes[state].append(name)
            if state != 'unchanged':
                delta.extend(difflib.unified_diff(original.splitlines(True), current.splitlines(True), fromfile=('a/' + name if original else '/dev/null'), tofile=('b/' + name if current else '/dev/null')))
    (EVIDENCE / 'full-source.diff').write_text(''.join(delta), encoding='utf-8')
    dump(EVIDENCE / 'source-changes.json', changes)
    def make_zip(name, paths, prefix=''):
        path = DELIVERY / name
        assert not path.exists()
        paths = sorted(set(paths))
        with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_DEFLATED) as output:
            for item in paths:
                assert item.is_file() and not item.is_symlink()
                output.write(item, prefix + str(item.relative_to(ROOT)))
        with zipfile.ZipFile(path) as check:
            assert check.testzip() is None
            assert len(check.namelist()) == len(paths)
            assert not any('/__pycache__/' in n or n.endswith('.pyc') or n.startswith(('data/', 'journal/')) for n in check.namelist())
        return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes()), 'bytes': path.stat().st_size, 'files': len(paths)}
    source_package = make_zip('touyan-0.3.0-source.zip', files)
    evidence_files = [EVIDENCE / name for name in ('DELIVERY.md', 'final-tests.log', 'final-tests.json', 'independent-code-review.md', 'final-integrity.json', 'full-source.diff', 'source-changes.json', 'browser-checks.json', 'browser-mobile.png', 'browser-desktop-dark.png', 'browser-chart.png')]
    evidence_files += [LIVE / name for name in ('report.json', 'claims.json', 'sources.json', 'plan.json', 'calculations.json', 'audit.json', 'old-template.md', 'new-template.md', 'comparison.md', 'browser-final-desktop.png', 'browser-final-mobile.png', 'browser-final-checks.json')]
    evidence_files += list((LIVE / 'final-rendered').glob('*'))
    evidence_files += [p for p in (LIVE / 'logs').rglob('*') if p.is_file()]
    evidence_files += [p for p in (LIVE / 'raw').rglob('*') if p.is_file()]
    run = 'R20261031T184001Z-7bace460dc9c'
    evidence_files += list((LIVE / 'isolated-home/journal/runs' / run).glob('*'))
    evidence_files += [p for p in (EVIDENCE / 'final-e2e').rglob('*') if p.is_file()]
    evidence_files += [p for p in (EVIDENCE / 'regression/final-v2').rglob('*') if p.is_file()]
    evidence_files += [EVIDENCE / 'tools/finalize_delivery.py']
    evidence_package = make_zip('touyan-0.3.0-validation.zip', evidence_files)
    result = {'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'version': '0.3.0', 'source': source_package, 'validation': evidence_package, 'changes': {k: len(v) for k, v in changes.items()}, 'protected_data_unchanged': True, 'installed': False}
    dump(DELIVERY / 'manifest.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    {'verify': verify, 'package': package}[sys.argv[1]]()
