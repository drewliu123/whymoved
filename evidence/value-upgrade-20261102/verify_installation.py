"""Verify the actual installed cache and run its tests, without editing it."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
registry = json.loads((Path.home() / ".claude/plugins/installed_plugins.json").read_text())
entries = registry["plugins"]["touyan@touyan-local"]
entry = next(row for row in entries if row.get("scope") == "user")
assert entry["version"] == "0.5.0", entry["version"]
cache = Path(entry["installPath"])
paths = [ROOT / "README.md"]
for directory in ("scripts", "tests", "agents", "skills", ".claude-plugin"):
    paths.extend(path for path in (ROOT / directory).rglob("*") if path.is_file() and path.suffix in {".py", ".md", ".json"})
checks = {}
for source in paths:
    relative = source.relative_to(ROOT)
    target = cache / relative
    checks[str(relative)] = target.is_file() and hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(target.read_bytes()).digest()
assert checks and all(checks.values()), [name for name, matches in checks.items() if not matches]
with tempfile.TemporaryDirectory(prefix="touyan-value-installed-") as isolated:
    environment = dict(os.environ, TOUYAN_HOME=isolated, PYTHONDONTWRITEBYTECODE="1")
    command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"]
    result = subprocess.run(command, cwd=cache, env=environment, capture_output=True, text=True)
    (HERE / "installed-tests.stdout.log").write_text(result.stdout, encoding="utf-8")
    (HERE / "installed-tests.stderr.log").write_text(result.stderr, encoding="utf-8")
    record = {"registered_version": entry["version"], "install_path": str(cache), "matches": checks,
              "tests": {"command": command, "cwd": str(cache), "exit_code": result.returncode,
                        "stdout": "installed-tests.stdout.log", "stderr": "installed-tests.stderr.log"},
              "final_prompt_sync": json.loads((HERE / "cache-sync.json").read_text()) if (HERE / "cache-sync.json").is_file() else None,
              "reload": "New session required; current session hot reload not claimed"}
    (HERE / "installation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert result.returncode == 0, result.stderr
print(json.dumps({"registered_version": entry["version"], "matched_files": len(checks), "installed_tests_exit_code": result.returncode}, ensure_ascii=False))
