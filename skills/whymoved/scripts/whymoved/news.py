"""News around a move window, labelled by *when* each story appeared.

The core rule: a story published after the move finished cannot be its cause.
It may still *name* the cause ("shares jump after X"), so we keep it as a pointer.
"""

from __future__ import annotations

import re
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from .net import fetch
from .symbols import Asset

# How far before the window a story can still count as a candidate cause.
LOOKBACK = timedelta(hours=24)
# Publication timestamps on aggregators lag the real event a little.
TOLERANCE = timedelta(minutes=10)

TIER1 = {
    "reuters", "bloomberg", "the wall street journal", "wsj", "financial times", "cnbc",
    "associated press", "ap news", "barron's", "marketwatch", "the information",
    "coindesk", "the block", "nikkei asia", "bloomberg.com", "reuters.com",
}
TIER2 = {
    "yahoo finance", "investing.com", "business insider", "fortune", "forbes", "axios",
    "the verge", "techcrunch", "decrypt", "cointelegraph", "seeking alpha", "benzinga",
    "fox business", "cnn business", "bbc", "the guardian", "new york times", "the new york times",
}


UP_WORDS = {
    "jump", "jumps", "surge", "surges", "soar", "soars", "rally", "rallies", "rise", "rises",
    "gain", "gains", "climb", "climbs", "rebound", "rebounds", "spike", "spikes", "pop", "pops",
    "higher", "record", "beat", "beats", "upgrade", "upgraded", "boost", "boosts",
}
DOWN_WORDS = {
    "fall", "falls", "drop", "drops", "plunge", "plunges", "slump", "slumps", "sink", "sinks",
    "dip", "dips", "tumble", "tumbles", "crash", "crashes", "slide", "slides", "lower", "miss",
    "misses", "downgrade", "downgraded", "selloff", "sell-off", "slips", "slip", "sheds",
}
# Pages that carry no new information about *why* something moved.
NOISE = re.compile(
    r"price (today|prediction|of)|current price|better buy|should you buy|stocks? to buy|"
    r"buy right now|is it too late|top \d+ |\bvs\.? |live updates?|price chart",
    re.I,
)


# Headlines that restate the price move itself ("TSLA falls 0.7%", "Bitcoin jumps") are reports, not causes.
PRICE_RECAP = re.compile(r"\b(rises?|falls?|up|down|gains?|drops?|jumps?|slips?|climbs?|sinks?)\b[^.]{0,20}?\d+(\.\d+)?\s?%", re.I)


@dataclass
class Story:
    title: str
    source: str
    url: str
    published: datetime
    timing: str = ""        # "candidate" | "after_move" | "background"
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)


def google_news_url(asset: Asset, name: str, start: datetime, end: datetime) -> str:
    after = (start - timedelta(days=1)).date().isoformat()
    before = (end + timedelta(days=2)).date().isoformat()
    if asset.kind == "crypto":
        q = f'("{name}" OR {asset.symbol}) after:{after} before:{before}'
    else:
        q = f'("{name}" OR "{asset.symbol}" stock) after:{after} before:{before}'
    params = urllib.parse.urlencode({"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"})
    return f"https://news.google.com/rss/search?{params}"


def parse_rss(xml_bytes: bytes) -> list[Story]:
    root = ET.fromstring(xml_bytes)
    out: list[Story] = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = item.findtext("pubDate")
        src_el = item.find("source")
        source = (src_el.text or "").strip() if src_el is not None else ""
        if not title or not pub:
            continue
        # Google News appends " - Source" to titles.
        if source and title.endswith(f" - {source}"):
            title = title[: -len(source) - 3].strip()
        try:
            published = parsedate_to_datetime(pub).astimezone(timezone.utc)
        except (TypeError, ValueError):
            continue
        out.append(Story(title=title, source=source, url=link, published=published))
    return out


def classify(stories: list[Story], start: datetime, end: datetime) -> list[Story]:
    for s in stories:
        if s.published > end + TOLERANCE:
            s.timing = "after_move"
        elif s.published >= start - LOOKBACK:
            s.timing = "candidate"
        else:
            s.timing = "background"
    return stories


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def direction(title: str) -> int:
    """+1 if the headline describes a rise, -1 a fall, 0 if unclear."""
    words = set(_norm(title).split())
    up, down = bool(words & UP_WORDS), bool(words & DOWN_WORDS)
    return 0 if up == down else (1 if up else -1)


def score(stories: list[Story], asset: Asset, name: str, start: datetime, move_sign: int = 0) -> list[Story]:
    keys = {asset.symbol.lower()}
    first_word = _norm(name).split(" ")[0] if name else ""
    if len(first_word) >= 3:
        keys.add(first_word)
    for s in stories:
        t = _norm(s.title)
        words = set(t.split())
        sc = 0.0
        if keys & words:
            sc += 2.0
            s.reasons.append("mentions the asset")
        src = s.source.lower()
        if src in TIER1:
            sc += 1.5
            s.reasons.append("tier-1 source")
        elif src in TIER2:
            sc += 0.5
        if NOISE.search(s.title):
            sc -= 3.0
            s.reasons.append("no new information")
        d = direction(s.title)
        if move_sign and d and d != move_sign:
            sc -= 2.5
            s.reasons.append("headline points the other way")
        if s.timing == "candidate" and (
            PRICE_RECAP.search(s.title) or (s.published >= start and move_sign and d == move_sign)
        ):
            # Published once the move was under way and describes it: a report of the move.
            s.timing = "after_move"
            s.reasons.append("describes the move itself")
        if s.timing == "candidate":
            # Closer to the start of the move is more likely to be the trigger.
            hours = abs((s.published - start).total_seconds()) / 3600
            sc += max(0.0, 2.0 - hours / 6)
        s.score = round(sc, 2)
    return stories


def dedupe(stories: list[Story]) -> list[Story]:
    """Drop near-identical headlines syndicated across outlets; keep the best-scored one."""
    seen: dict[str, Story] = {}
    for s in sorted(stories, key=lambda x: -x.score):
        key = " ".join(_norm(s.title).split()[:8])
        if key not in seen:
            seen[key] = s
    return list(seen.values())


def gather(asset: Asset, name: str, start: datetime, end: datetime, move_sign: int = 0) -> list[Story]:
    url = google_news_url(asset, name, start, end)
    stories = parse_rss(fetch(url))
    stories = classify(stories, start, end)
    stories = score(stories, asset, name, start, move_sign)
    return [s for s in dedupe(stories) if s.score > 0]
