#!/usr/bin/env python3
"""Update only touyan-local and verify installed source hashes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
records = []

def run(command, label, cwd=ROOT):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    (HERE / (label + '.stdout.log')).write_text(result.stdout, encoding='utf-8')
    (HERE / (label + '.stderr.log')).write_text(result.stderr, encoding='utf-8')
    records.append({'command': command, 'exit_code': result.returncode,
                    'stdout': label + '.stdout.log', 'stderr': label + '.stderr.log'})
    if result.returncode:
        raise RuntimeError(label + ': ' + result.stderr)
    return result

run(['claude', 'plugin', 'marketplace', 'update', 'touyan-local', '--json'], 'marketplace-update')
run(['claude', 'plugin', 'update', 'touyan@touyan-local', '--json'], 'plugin-update')
registry = json.loads((Path.home() / '.claude/plugins/installed_plugins.json').read_text())
entries = registry['plugins']['touyan@touyan-local']
entry = next(e for e in entries if e.get('version') == '0.4.0')
installed = Path(entry['installPath'])
paths = ['.claude-plugin/plugin.json', 'README.md']
for folder in ('scripts', 'skills', 'agents', 'tests'):
    paths.extend(str(p.relative_to(ROOT)) for p in (ROOT / folder).rglob('*')
                 if p.is_file() and p.suffix in {'.py', '.md', '.json'})
checks = []
for relative in sorted(paths):
    digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
    actual = hashlib.sha256((installed / relative).read_bytes()).hexdigest()
    if digest != actual:
        raise RuntimeError('installed content mismatch: ' + relative)
    checks.append({'path': relative, 'sha256': digest, 'matches': True})
run(['claude', 'plugin', 'validate', str(installed / '.claude-plugin/plugin.json'), '--json'], 'installed-plugin-validate')
run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], 'installed-tests', cwd=installed)
result = {'result': 'pass', 'plugin': 'touyan@touyan-local', 'version': entry['version'],
          'installed_path': str(installed), 'records': records, 'files': checks,
          'activation': 'Restart or start a new session to load the updated plugin; current-session hot reload not verified.'}
(HERE / 'installation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'passed': True, 'version': entry['version'], 'files_matched': len(checks),
                  'installed_path': str(installed)}, ensure_ascii=False))
