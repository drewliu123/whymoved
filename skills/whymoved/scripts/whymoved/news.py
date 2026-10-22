"""News around a move window, labelled by *when* each story appeared.

The core rule: a story published after the move finished cannot be its cause.
It may still *name* the cause ("shares jump after X"), so we keep it as a pointer.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from .net import FetchError, fetch
from .symbols import Asset

# How far before the window a story can still count as a candidate cause.
LOOKBACK = timedelta(hours=24)
# Publication timestamps on aggregators lag the real event a little.
TOLERANCE = timedelta(minutes=10)

TIER1 = {
    "reuters", "bloomberg", "the wall street journal", "wsj", "financial times", "cnbc",
    "associated press", "ap news", "barron's", "marketwatch", "the information",
    "coindesk", "the block", "nikkei asia", "bloomberg.com", "reuters.com",
    "sec edgar", "south china morning post", "caixin global",
    "财新网", "财新", "第一财经", "证券时报", "上海证券报", "中国证券报", "21世纪经济报道", "经济观察报",
    "路透中文网", "华尔街日报中文网", "彭博", "香港经济日报", "信报",
}
TIER2 = {
    "yahoo finance", "investing.com", "business insider", "fortune", "forbes", "axios",
    "the verge", "techcrunch", "decrypt", "cointelegraph", "seeking alpha", "benzinga",
    "fox business", "cnn business", "bbc", "the guardian", "new york times", "the new york times",
    "新浪财经", "东方财富网", "华尔街见闻", "界面新闻", "澎湃新闻", "每日经济新闻", "财联社", "格隆汇",
    "智通财经", "36氪", "腾讯新闻", "网易", "凤凰网", "雪球",
}

# Words that describe the price move itself. A headline built on these, published once the
# move was under way, is a report of the move ("Nvidia jumps"), not its cause.
MOVE_UP = {
    "jump", "jumps", "surge", "surges", "soar", "soars", "rally", "rallies", "rise", "rises",
    "gain", "gains", "climb", "climbs", "rebound", "rebounds", "spike", "spikes", "pop", "pops",
    "higher", "advance", "advances", "rockets", "skyrockets",
}
MOVE_DOWN = {
    "fall", "falls", "drop", "drops", "plunge", "plunges", "slump", "slumps", "sink", "sinks",
    "dip", "dips", "tumble", "tumbles", "crash", "crashes", "slide", "slides", "lower",
    "selloff", "sell-off", "slips", "slip", "sheds", "retreat", "retreats", "sinking",
}
# Words that describe news which can *cause* a move. They point in a direction but are
# never, on their own, a sign that the story merely reports the move.
CAUSE_UP = {"beat", "beats", "upgrade", "upgrades", "upgraded", "record", "boost", "boosts", "raises", "approval", "approved"}
CAUSE_DOWN = {
    "miss", "misses", "missed", "downgrade", "downgrades", "downgraded", "cuts", "recall", "recalls",
    "probe", "lawsuit", "halts", "delay", "delays",
}

ZH_MOVE_UP = re.compile(r"大涨|暴涨|飙升|拉升|涨停|走高|上涨|收涨|高开|狂飙|急升|攀升|涨超|涨逾")
ZH_MOVE_DOWN = re.compile(r"大跌|暴跌|跳水|跌停|走低|下跌|收跌|低开|重挫|急跌|下挫|跌超|跌逾|闪崩")
ZH_CAUSE_UP = re.compile(r"超预期|上调|获批|中标|回购|增持|创新高|利好")
ZH_CAUSE_DOWN = re.compile(r"不及预期|下调|减持|立案|处罚|亏损|利空|暴雷|召回")

# Pages that carry no new information about *why* something moved.
NOISE = re.compile(
    r"price (today|prediction|of)|current price|better buy|should you buy|stocks? to buy|"
    r"buy right now|is it too late|top \d+ |\bvs\.? |live updates?|price chart|"
    r"biggest (stock )?moves|stocks making|top movers|(pre-?market|after-hours|midday) movers|stocks that explain|"
    r"股价查询|实时行情|行情走势|收盘播报|盘中播报|个股资金流向|异动股",
    re.I,
)

# Kinds of news that typically move prices: a small prior in their favour.
CATALYST = re.compile(
    r"\b(earnings|results|revenue|guidance|outlook|forecast|quarter|q[1-4]|deliver(y|ies)|eps|"
    r"upgrades?|downgrades?|price target|fda|approval|merger|acquir\w*|acquisition|deal|buyback|"
    r"lawsuit|probe|investigation|recall|tariffs?|sanctions?|ceo|resigns?|layoffs?|etf|sec|hack(ed)?|exploit)\b"
    r"|财报|业绩|营收|净利|指引|评级|目标价|收购|并购|回购|监管|立案|关税|制裁|获批|发布会|减持|增持",
    re.I,
)

# Headlines that restate the price move itself ("TSLA falls 0.7%", "腾讯涨超3%") are reports, not causes.
PRICE_RECAP = re.compile(
    r"\b(rises?|falls?|up|down|gains?|drops?|jumps?|slips?|climbs?|sinks?|soars?|surges?|plunges?|tumbles?)\b[^.]{0,20}?\d+(\.\d+)?\s?%"
    r"|[涨跌升][^。，]{0,6}?\d+(\.\d+)?\s?%",
    re.I,
)

# Extra words that identify an asset in headlines when its ticker and legal name do not.
NEWS_ALIASES = {
    "GOOGL": ["google"], "GOOG": ["google"], "META": ["facebook", "instagram"], "BRK-B": ["berkshire"],
    "BABA": ["alibaba"], "9988.HK": ["alibaba"], "0700.HK": ["tencent"], "TSM": ["tsmc"],
}


@dataclass
class Story:
    title: str
    source: str
    url: str
    published: datetime
    timing: str = ""        # "candidate" | "after_move" | "background"
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)
    kind: str = "news"      # "news" | "filing"


def _query_url(q: str, lang: str) -> str:
    if lang == "zh":
        params = {"q": q, "hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans"}
    else:
        params = {"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"}
    return f"https://news.google.com/rss/search?{urllib.parse.urlencode(params)}"


def google_news_urls(asset: Asset, name: str, start: datetime, end: datetime) -> list[str]:
    """One query in English and, for Hong Kong and mainland stocks, one in Chinese."""
    after = (start - timedelta(days=1)).date().isoformat()
    before = (end + timedelta(days=2)).date().isoformat()
    dates = f"after:{after} before:{before}"
    if asset.kind == "crypto":
        return [_query_url(f'("{name}" OR {asset.symbol}) {dates}', "en")]
    if asset.market == "us":
        return [_query_url(f'("{name}" OR "{asset.symbol}" stock) {dates}', "en")]
    urls = [_query_url(f'"{name}" (stock OR shares) {dates}', "en")]
    zh = asset.zh_name or name
    urls.append(_query_url(f'("{zh}" OR "{asset.code}") (股价 OR 股票 OR 涨 OR 跌) {dates}', "zh"))
    return urls


def google_news_url(asset: Asset, name: str, start: datetime, end: datetime) -> str:
    return google_news_urls(asset, name, start, end)[0]


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


def _sign(up: bool, down: bool) -> int:
    return 0 if up == down else (1 if up else -1)


def move_direction(title: str) -> int:
    """+1 if the headline describes the price going up, -1 down, 0 if unclear."""
    words = set(_norm(title).split())
    return _sign(bool(words & MOVE_UP) or bool(ZH_MOVE_UP.search(title)),
                 bool(words & MOVE_DOWN) or bool(ZH_MOVE_DOWN.search(title)))


def direction(title: str) -> int:
    """+1 if the headline is good news or describes a rise, -1 bad news or a fall, 0 if unclear."""
    words = set(_norm(title).split())
    up = bool(words & (MOVE_UP | CAUSE_UP)) or bool(ZH_MOVE_UP.search(title) or ZH_CAUSE_UP.search(title))
    down = bool(words & (MOVE_DOWN | CAUSE_DOWN)) or bool(ZH_MOVE_DOWN.search(title) or ZH_CAUSE_DOWN.search(title))
    return _sign(up, down)


def asset_keys(asset: Asset, name: str) -> tuple[set[str], set[str], list[str]]:
    """Names (any case), tickers (exact case, so "ON" is not "on") and Chinese substrings
    that mean a headline is about this asset."""
    names = {w.lower() for w in NEWS_ALIASES.get(asset.symbol, [])}
    first = _norm(name).split(" ")[0] if name else ""
    if len(first) >= 3 and first != asset.symbol.lower():
        names.add(first)
    tickers = {asset.symbol, asset.code, asset.code.lstrip("0")} - {""}
    zh = [z for z in {asset.zh_name, asset.code if asset.market == "cn" else ""} if z]
    return names, tickers, zh


def mentions(title: str, keys: tuple[set[str], set[str], list[str]]) -> bool:
    names, tickers, zh = keys
    if names & set(_norm(title).split()) or any(z in title for z in zh):
        return True
    return bool(tickers & set(re.findall(r"[A-Za-z0-9.\-]+", title.replace("$", ""))))


def score(stories: list[Story], asset: Asset, name: str, start: datetime, move_sign: int = 0) -> list[Story]:
    keys = asset_keys(asset, name)
    for s in stories:
        sc = 0.0
        if s.kind == "filing":
            sc += 3.5
            s.reasons.append("official filing")
            if s.timing == "after_move":
                # The filing came later, but the release it attaches may predate the move.
                sc += 1.0
                s.reasons.append("filed after the move; the event it reports may have been announced earlier, check the release time")
        elif mentions(s.title, keys):
            sc += 2.0
            s.reasons.append("mentions the asset")
        else:
            sc -= 1.0
            s.reasons.append("does not mention the asset")
        src = s.source.lower()
        if src in TIER1 and s.kind != "filing":
            sc += 1.5
            s.reasons.append("tier-1 source")
        elif src in TIER2:
            sc += 0.5
        if s.kind == "news" and CATALYST.search(s.title):
            sc += 1.0
            s.reasons.append("catalyst-type news")
        if NOISE.search(s.title):
            sc -= 3.0
            s.reasons.append("no new information")
        if s.kind == "news":
            d = direction(s.title)
            if move_sign and d and d != move_sign:
                sc -= 2.5
                s.reasons.append("headline points the other way")
            if s.timing == "candidate" and (
                PRICE_RECAP.search(s.title) or (s.published >= start and move_sign and move_direction(s.title) == move_sign)
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
        norm = _norm(s.title)
        key = " ".join(norm.split()[:8]) if norm else re.sub(r"\W+", "", s.title)[:16]
        if key not in seen:
            seen[key] = s
    return list(seen.values())


def gather(asset: Asset, name: str, start: datetime, end: datetime, move_sign: int = 0,
           extra: list[Story] | None = None, extra_fn=None) -> list[Story]:
    """Search news and score it. `extra` / `extra_fn()` add other evidence, e.g. SEC filings."""
    urls = google_news_urls(asset, name, start, end)
    with ThreadPoolExecutor(max_workers=len(urls)) as pool:
        results = list(pool.map(_fetch_rss, urls))
    extra = list(extra or [])
    if extra_fn:
        try:
            extra += extra_fn()
        except Exception:  # reported separately by the caller
            pass
    if all(r is None for r in results) and not extra:
        raise FetchError("news search unavailable")
    stories = [s for r in results if r for s in r] + extra
    stories = classify(stories, start, end)
    stories = score(stories, asset, name, start, move_sign)
    return [s for s in dedupe(stories) if s.score > 0]


def _fetch_rss(url: str) -> list[Story] | None:
    try:
        return parse_rss(fetch(url))
    except (FetchError, ET.ParseError):
        return None


# --- Original article links -------------------------------------------------------------
# Google News RSS links are redirects (news.google.com/rss/articles/...). Agents and readers
# want the publisher's URL, so we decode the ones we show. Best-effort: on any failure the
# Google link is kept.

_BATCH = "https://news.google.com/_/DotsSplashUi/data/batchexecute"


def decode_google_url(url: str, timeout: float = 8.0) -> str:
    m = re.search(r"news\.google\.com/(?:rss/)?articles/([^?/]+)", url)
    if not m:
        return url
    aid = m.group(1)
    try:
        page = fetch(f"https://news.google.com/rss/articles/{aid}", timeout=timeout, retries=0).decode("utf-8", "replace")
        sg = re.search(r'data-n-a-sg="([^"]+)"', page)
        ts = re.search(r'data-n-a-ts="([^"]+)"', page)
        if not sg or not ts:
            return url
        inner = (
            '["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],'
            f'"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{aid}",{ts.group(1)},"{sg.group(1)}"]'
        )
        body = urllib.parse.urlencode({"f.req": json.dumps([[["Fbv4je", inner, None, "generic"]]])}).encode()
        raw = fetch(_BATCH, data=body, timeout=timeout, retries=0,
                    headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}).decode("utf-8", "replace")
        for line in raw.splitlines():
            if line.startswith("[["):
                payload = json.loads(json.loads(line)[0][2])
                if isinstance(payload, list) and len(payload) > 1 and str(payload[1]).startswith("http"):
                    return payload[1]
    except (FetchError, ValueError, IndexError, TypeError):
        pass
    return url


def resolve_urls(stories: list[Story], workers: int = 8) -> None:
    todo = [s for s in stories if "news.google.com" in s.url]
    if not todo:
        return
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for s, url in zip(todo, pool.map(lambda x: decode_google_url(x.url), todo)):
            s.url = url
