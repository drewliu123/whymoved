"""SEC EDGAR filings as first-class evidence for US-listed companies.

Filings carry an exact acceptance timestamp. It is the *latest* moment the information was
public: an earnings 8-K is often filed hours after the press release it attaches. So a
filing accepted after the move cannot prove timing, but it names the event precisely.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime, timedelta

from . import __version__
from .net import fetch_json
from .news import Story

# SEC asks automated clients to identify themselves with a contact address. The default is
# the maintainer's; set WHYMOVED_CONTACT to your own email if you run whymoved at volume.
CONTACT = os.environ.get("WHYMOVED_CONTACT", "liuxintian1314520@gmail.com")
HEADERS = {"User-Agent": f"whymoved/{__version__} {CONTACT}"}

FORMS = {"8-K", "8-K/A", "6-K", "10-Q", "10-K", "20-F", "S-1", "S-3", "424B5", "SC 13D", "SC 13G"}

ITEMS = {
    "1.01": "material agreement", "1.02": "agreement terminated", "1.03": "bankruptcy",
    "1.05": "cybersecurity incident", "2.01": "acquisition or disposal completed",
    "2.02": "results of operations (earnings)", "2.03": "new debt obligation",
    "2.05": "restructuring / layoffs", "2.06": "impairment", "3.01": "delisting notice",
    "3.02": "unregistered share sale", "4.01": "auditor change", "4.02": "prior financials unreliable",
    "5.01": "change in control", "5.02": "executive or director change", "5.07": "shareholder vote",
    "7.01": "Regulation FD disclosure", "8.01": "other material event",
}

_CACHE = os.path.join(tempfile.gettempdir(), "whymoved-sec-tickers.json")


def _ticker_map() -> dict[str, int]:
    try:
        if time.time() - os.path.getmtime(_CACHE) < 7 * 86400:
            with open(_CACHE, encoding="utf-8") as f:
                return json.load(f)
    except (OSError, ValueError):
        pass
    data = fetch_json("https://www.sec.gov/files/company_tickers.json", headers=HEADERS, timeout=10, retries=1)
    out = {row["ticker"].upper(): int(row["cik_str"]) for row in data.values()}
    try:
        with open(_CACHE, "w", encoding="utf-8") as f:
            json.dump(out, f)
    except OSError:
        pass
    return out


def describe(form: str, items: str) -> str:
    parts = [ITEMS.get(i.strip(), "") for i in items.split(",") if i.strip() and i.strip() != "9.01"]
    parts = [p for p in parts if p]
    return f"SEC {form}: {'; '.join(parts)}" if parts else f"SEC {form} filing"


def parse_filings(data: dict, cik: int, start: datetime, end: datetime) -> list[Story]:
    recent = (data.get("filings") or {}).get("recent") or {}
    out = []
    for i, form in enumerate(recent.get("form", [])):
        if form not in FORMS:
            continue
        try:
            accepted = datetime.fromisoformat(recent["acceptanceDateTime"][i].replace("Z", "+00:00"))
        except (KeyError, IndexError, ValueError):
            continue
        if not (start <= accepted <= end):
            continue
        acc = recent["accessionNumber"][i].replace("-", "")
        doc = recent["primaryDocument"][i]
        title = describe(form, (recent.get("items") or [""] * (i + 1))[i] or "")
        event = (recent.get("reportDate") or [""] * (i + 1))[i] or ""
        out.append(Story(
            title=f"{title} (event date {event})" if event and form.startswith("8-K") else title,
            source="SEC EDGAR",
            url=f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}",
            published=accepted,
            kind="filing",
        ))
    return out


def sec_filings(symbol: str, start: datetime, end: datetime) -> list[Story]:
    """Filings accepted between `start - 24h` and `end + 2 days`. US tickers only."""
    cik = _ticker_map().get(symbol.upper())
    if not cik:
        return []
    data = fetch_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", headers=HEADERS, timeout=10, retries=1)
    return parse_filings(data, cik, start - timedelta(hours=24), end + timedelta(days=2))
