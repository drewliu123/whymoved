"""Start the studied EdgarTools build with the normal local Python 3.12.

The package set lives in the evaluation directory. We deliberately do not
modify the Harness-managed interpreter linked by the original venv.
"""
import os
import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package_dir = root / "research/edgartools-eval-venv/lib/python3.12/site-packages"
if sys.version_info[:2] != (3, 12):
    raise SystemExit("Use the local Python 3.12 interpreter for this evaluation launcher.")
if not (package_dir / "edgar").is_dir():
    raise SystemExit(f"Evaluation packages are missing: {package_dir}")
sys.path.insert(0, str(package_dir))
os.environ.setdefault("EDGAR_LOCAL_DATA_DIR", str(root / "research/edgartools-study/data"))
os.environ.setdefault("EDGAR_CACHE_DIR", str(root / "research/edgartools-study/cache"))
runpy.run_module("edgar.ai", run_name="__main__")
