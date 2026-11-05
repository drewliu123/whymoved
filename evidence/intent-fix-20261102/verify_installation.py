"""Verify registered local version and installed source hashes; run no model."""

import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
command = ["claude", "plugin", "list", "--json"]
result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
if result.returncode:
    raise SystemExit(result.stderr or result.stdout)
plugins = json.loads(result.stdout)
if isinstance(plugins, dict):
    plugins = plugins.get("plugins", [])
entry = next(row for row in plugins if row.get("id") == "touyan@touyan-local" and row.get("scope") == "user")
cache = Path(entry["installPath"])
paths = [ROOT / "README.md"]
for directory in ("scripts", "tests", "agents", "skills", ".claude-plugin"):
    paths.extend(path for path in (ROOT / directory).rglob("*") if path.is_file() and path.suffix in {".py", ".md", ".json"})
checks = {}
for source in paths:
    relative = source.relative_to(ROOT)
    target = cache / relative
    checks[str(relative)] = target.is_file() and hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256(target.read_bytes()).digest()
record = {"registered_version": entry["version"], "install_path": str(cache), "enabled": entry.get("enabled"),
          "expected_version": "0.5.1", "matches": checks,
          "passed": entry["version"] == "0.5.1" and bool(checks) and all(checks.values()),
          "reload": "New session required; no current-session hot reload claimed"}
(HERE / "installation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"version": entry["version"], "path": str(cache), "matched_files": sum(checks.values()), "total_files": len(checks),
                  "mismatches": [name for name, matches in checks.items() if not matches], "passed": record["passed"]}, ensure_ascii=False, indent=2))
raise SystemExit(0 if record["passed"] else 1)
