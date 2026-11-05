#!/usr/bin/env python3
"""Local acceptance runner. Synthetic cases are explicit, not research findings."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
from test_analysis_contract import bundle, priced_bundle
import research_run


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run(command, label, expected=0):
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    (HERE / (label + ".stdout.log")).write_text(result.stdout, encoding="utf-8")
    (HERE / (label + ".stderr.log")).write_text(result.stderr, encoding="utf-8")
    record = {"command": command, "exit_code": result.returncode, "expected_exit_code": expected,
              "stdout": label + ".stdout.log", "stderr": label + ".stderr.log"}
    records.append(record)
    if result.returncode != expected:
        raise RuntimeError("unexpected exit code: " + label + "\n" + result.stderr)
    return result


records = []
cases = []
run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], "tests")
run(["claude", "plugin", "validate", ".", "--json"], "plugin-validate")
run(["claude", "plugin", "validate", ".claude-plugin/plugin.json", "--json"], "plugin-contents-validate")
for obj_type, kind in (("asset", "valuation"), ("theme", "theme_transmission"),
                       ("event_pricing", "event_forecast"), ("actor", "commitment_check")):
    data = priced_bundle() if obj_type == "asset" else bundle(kind)
    data[0]["type"] = data[3]["type"] = obj_type
    data[0]["title"] = "虚构验收示范（非市场研究） · " + obj_type
    directory = HERE / "cases" / obj_type
    for name, doc in zip(("report", "claims", "sources", "plan"), data):
        save(directory / (name + ".json"), doc)
    args = []
    for name in ("report", "claims", "sources", "plan"):
        args += ["--" + name, str(directory / (name + ".json"))]
    run([sys.executable, "scripts/analysis_contract.py", "check"] + args, obj_type + "-check")
    home = directory / "isolated-home"
    result = research_run.archive_run(*(directory / (name + ".json") for name in ("report", "claims", "sources", "plan")), home=home)
    loaded = research_run.load_run(result["run_id"], home)
    assert loaded["report"]["analysis"] == data[0]["analysis"]
    data[0]["update"] = {"judgment_changed": False, "reason": "验收只修改下一观察，不虚构新发现", "comparability": {"status": "comparable", "reason": "同一虚构输入与口径"}}
    data[0]["analysis"]["tests"][0]["next_observation"] = "下一期同口径交付与现金流"
    save(directory / "report.json", data[0])
    updated = research_run.archive_run(*(directory / (name + ".json") for name in ("report", "claims", "sources", "plan")), home=home, parent_run=result["run_id"])
    assert updated["diff"]["analysis_changed"]
    research_run.load_run(updated["run_id"], home)
    cases.append({"object_type": obj_type, "question_kind": kind, "run_id": result["run_id"], "update_run_id": updated["run_id"],
                  "report_html": str(Path(result["path"]) / "report.html"), "report_md": str(Path(result["path"]) / "report.md"),
                  "model_status": loaded["report"]["analysis"]["model_status"], "market_status": loaded["report"]["analysis"]["market"]["status"], "synthetic": True})
    if obj_type == "asset":
        model = data[0]["analysis"]["models"][0]
        save(directory / "model-spec.json", model["spec"])
        run([sys.executable, "scripts/analysis_models.py", str(directory / "model-spec.json")], "model-cli")
        data[0]["analysis"]["models"][0]["result"]["outputs"]["implied_growth"]["value"] = .99
        save(directory / "report.json", data[0])
        run([sys.executable, "scripts/analysis_contract.py", "check"] + args, "tampered-result-rejected", expected=1)
        save(directory / "report.json", loaded["report"])
    else:
        save(directory / "report.json", loaded["report"])

# Read actual old archives in place; compare every file hash to prove no rewrite.
old_root = ROOT / "journal" / "runs"
before = {str(p.relative_to(old_root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in old_root.rglob("*") if p.is_file()}
old_runs = research_run.list_runs(ROOT)
after = {str(p.relative_to(old_root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in old_root.rglob("*") if p.is_file()}
assert before == after
save(HERE / "acceptance.json", {"result": "pass", "records": records, "cases": cases, "old_runs_read": old_runs,
    "old_archive_files_unchanged": before == after, "not_run": ["live web research", "forecast accuracy or alpha evaluation", "new interactive session reload"],
    "notes": "Four object types use explicit synthetic fixtures. Existing NVDA archives were loaded only, not re-researched or rewritten."})
print(json.dumps({"passed": True, "cases": len(cases), "old_runs_read": len(old_runs), "evidence": str(HERE / "acceptance.json")}, ensure_ascii=False))
