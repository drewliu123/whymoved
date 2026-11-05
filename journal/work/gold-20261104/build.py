"""Build plan/sources/claims/report/audit for the 2026-11-04 gold outlook run."""
import csv, json, datetime as dt
from pathlib import Path

W = Path(__file__).resolve().parent
RAW = W / "raw"
AS_OF = "2026-11-04T07:30:00+00:00"
RET = "2026-11-04T07:10:00+00:00"


def yahoo(sym):
    r = json.load(open(RAW / f"y_{sym}.json"))["chart"]["result"][0]
    rows = {dt.datetime.utcfromtimestamp(t).date().isoformat(): x
            for t, x in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if x}
    return rows, r["meta"]


def fred(i):
    return {a: float(b) for a, b in list(csv.reader(open(RAW / f"fred_{i}.csv")))[1:] if b not in (".", "")}


gc, gcm = yahoo("GC=F")
si, sim = yahoo("SI=F")
cl, clm = yahoo("CL=F")
ry = fred("DFII10")
cpi, core = fred("CPIAUCSL"), fred("CPILFESL")
r2 = lambda x: round(x, 2)

G_PEAK, G_APR, G_LOW, G_NOW = r2(gc["2026-01-29"]), r2(gc["2026-04-01"]), r2(gc["2026-10-30"]), r2(gcm["regularMarketPrice"])
S_PEAK, S_NOW = r2(si["2026-01-26"]), r2(sim["regularMarketPrice"])
C_OCT30, C_NOW = r2(cl["2026-10-30"]), r2(clm["regularMarketPrice"])
pct = lambda a, b: round((a / b - 1) * 100, 1)
DD_NOW, DD_LOW, DD_LEG1 = pct(G_NOW, G_PEAK), pct(G_LOW, G_PEAK), pct(G_APR, G_PEAK)
S_DD, C_MOVE = pct(S_NOW, S_PEAK), pct(C_NOW, C_OCT30)
CPI_Y = round((cpi["2026-09-01"] / cpi["2025-09-01"] - 1) * 100, 1)
CORE_Y = round((core["2026-09-01"] / core["2025-09-01"] - 1) * 100, 1)


def corr_window(lo, hi):
    ks = [k for k in sorted(gc) if k in cl and k in ry and lo <= k <= hi]
    g = [gc[ks[i]] / gc[ks[i - 1]] - 1 for i in range(1, len(ks))]
    o = [cl[ks[i]] / cl[ks[i - 1]] - 1 for i in range(1, len(ks))]
    def c(a, b):
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** .5
    return round(c(g, o), 2), len(g)


CORR_PRE, N_PRE = corr_window("2025-11-01", "2026-03-31")
CORR_A, N_A = corr_window("2026-04-01", "2026-07-31")
CORR_B, N_B = corr_window("2026-08-01", "2026-11-04")

YURL = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=1y&interval=1d"


def sel(purpose, priority="decisive", relevance="direct"):
    return {"selected": True, "reason": purpose, "relevance": relevance, "purpose": purpose, "priority": priority}


def quote_src(sid, sym, label, value, unit, when, qtype, outcome, purpose, extra=None):
    s = {"id": sid, "url": YURL % sym, "canonical_url": YURL % sym, "publisher": "Yahoo Finance chart API (exchange data, delayed)",
         "tier": "T1", "published_at": "unknown", "retrieved_at": RET,
         "quote": "%s %s = %s" % (sym, when, value), "locator": "raw/y_%s.json chart.result[0]" % sym,
         "origin_id": "yahoo-%s" % sym.lower(), "origin_basis": "交易所行情经Yahoo转发；非独立第二来源",
         "supports": ["price"], "evidence_kind": "market_quote", "access_status": "ok",
         "market_quote": {"quoted_at": when, "instrument": label, "outcome": outcome, "direction": "level",
                          "value": value, "unit": unit, "quote_type": qtype},
         "selection": sel(purpose)}
    if extra:
        s.update(extra)
    return s


GC_NOW_T = dt.datetime.utcfromtimestamp(gcm["regularMarketTime"]).strftime("%Y-%m-%dT%H:%M:%S+00:00")
SI_NOW_T = dt.datetime.utcfromtimestamp(sim["regularMarketTime"]).strftime("%Y-%m-%dT%H:%M:%S+00:00")
CL_NOW_T = dt.datetime.utcfromtimestamp(clm["regularMarketTime"]).strftime("%Y-%m-%dT%H:%M:%S+00:00")
GCL = "COMEX gold futures continuous front contract (GC=F), USD/oz"
SIL = "COMEX silver futures continuous front contract (SI=F), USD/oz"
CLL = "NYMEX WTI crude futures continuous front contract (CL=F), USD/bbl"
CLOSE_T = lambda d: d + "T17:00:00-05:00" if d < "2026-03-08" or d > "2026-11-01" else d + "T17:00:00-04:00"

FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=%s"
FED_OCT = "https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm"
FED_SEP = "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm"
FED_CAL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
WGC = "https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-q3-2026"
PM_FED = "https://gamma-api.polymarket.com/events?closed=false&limit=50&order=volume24hr&ascending=false&tag_slug=fed"
PM_GOLD = "https://gamma-api.polymarket.com/public-search?q=gold%20price&limit_per_type=10"

cands = [
    quote_src("PX-GC-NOW", "GC=F", GCL, G_NOW, "USD/oz", GC_NOW_T, "indicative", "last price", "当前金价基准"),
    quote_src("PX-GC-PEAK", "GC=F", GCL, G_PEAK, "USD/oz", CLOSE_T("2026-01-29"), "close", "daily close", "一年内收盘高点"),
    quote_src("PX-GC-APR", "GC=F", GCL, G_APR, "USD/oz", CLOSE_T("2026-04-01"), "close", "daily close", "T4第一段下跌终点"),
    quote_src("PX-GC-LOW", "GC=F", GCL, G_LOW, "USD/oz", CLOSE_T("2026-10-30"), "close", "daily close", "一年内收盘低点"),
    quote_src("PX-SI-PEAK", "SI=F", SIL, S_PEAK, "USD/oz", CLOSE_T("2026-01-26"), "close", "daily close", "白银高点"),
    quote_src("PX-SI-NOW", "SI=F", SIL, S_NOW, "USD/oz", SI_NOW_T, "indicative", "last price", "白银当前"),
    quote_src("PX-CL-OCT30", "CL=F", CLL, C_OCT30, "USD/bbl", CLOSE_T("2026-10-30"), "close", "daily close", "油价近期高位"),
    quote_src("PX-CL-NOW", "CL=F", CLL, C_NOW, "USD/bbl", CL_NOW_T, "indicative", "last price", "油价当前"),
    {"id": "FRED-DFII10", "url": FRED % "DFII10", "canonical_url": FRED % "DFII10", "publisher": "FRED / U.S. Treasury",
     "tier": "T0", "published_at": "unknown", "retrieved_at": RET,
     "quote": "2026-01-29,%.2f; 2026-04-01,%.2f; 2026-10-05,%.2f; 2026-11-02,%.2f" % (ry["2026-01-29"], ry["2026-04-01"], ry["2026-10-05"], ry["2026-11-02"]),
     "locator": "DFII10 rows 2026-01-29, 2026-04-01, 2026-10-05, 2026-11-02", "origin_id": "ust-real-yield-curve",
     "origin_basis": "财政部实际收益率曲线原始序列", "supports": ["fact"], "evidence_kind": "document", "access_status": "ok",
     "units": {"unit": "percent", "scope": "10-year TIPS constant maturity"}, "selection": sel("实际利率路径")},
    {"id": "FRED-CPI", "url": FRED % "CPIAUCSL", "canonical_url": FRED % "CPIAUCSL", "publisher": "FRED / BLS",
     "tier": "T0", "published_at": "unknown", "retrieved_at": RET,
     "quote": "CPIAUCSL 2025-09-01,%.3f; 2026-09-01,%.3f | CPILFESL 2025-09-01,%.3f; 2026-09-01,%.3f" % (cpi["2025-09-01"], cpi["2026-09-01"], core["2025-09-01"], core["2026-09-01"]),
     "locator": "CPIAUCSL与CPILFESL 2025-09与2026-09行（季调指数）", "origin_id": "bls-cpi",
     "origin_basis": "BLS原始指数经FRED", "supports": ["fact"], "evidence_kind": "document", "access_status": "ok",
     "selection": sel("通胀来源：能源 vs 核心", "useful")},
    {"id": "FED-SEP", "url": FED_SEP, "canonical_url": FED_SEP, "publisher": "Federal Reserve", "tier": "T0",
     "published_at": "2026-09-16T14:00:00-04:00", "retrieved_at": RET,
     "quote": "The Committee decided to raise the target range for the federal funds rate by 1/4 percentage point to 3-3/4 to 4 percent",
     "locator": "FOMC statement paragraph 1", "origin_id": "fomc-20260916", "origin_basis": "FOMC正式声明",
     "supports": ["fact"], "evidence_kind": "document", "access_status": "ok", "selection": sel("9月加息")},
    {"id": "FED-OCT", "url": FED_OCT, "canonical_url": FED_OCT, "publisher": "Federal Reserve", "tier": "T0",
     "published_at": "2026-10-28T14:00:00-04:00", "retrieved_at": RET,
     "quote": "decided to maintain the target range for the federal funds rate at 3-3/4 to 4 percent ... Voting against the monetary policy action were Lisa D. Cook and Beth M. Hammack, who preferred to raise the target range for the federal funds rate by 1/4 percentage point",
     "locator": "FOMC statement paragraphs 1 and final", "origin_id": "fomc-20261028", "origin_basis": "FOMC正式声明",
     "supports": ["fact"], "evidence_kind": "document", "access_status": "ok", "selection": sel("10月按兵不动但两票主张加息")},
    {"id": "FED-CAL", "url": FED_CAL, "canonical_url": FED_CAL, "publisher": "Federal Reserve", "tier": "T0",
     "published_at": "unknown", "retrieved_at": RET, "quote": "December 8-9* * Meeting associated with a Summary of Economic Projections.",
     "locator": "2026 FOMC Meetings, December row", "origin_id": "fomc-calendar-2026", "origin_basis": "Fed官方日历",
     "supports": ["fact"], "evidence_kind": "document", "access_status": "ok", "selection": sel("下一催化日期")},
    {"id": "WGC-Q3", "url": WGC, "canonical_url": WGC, "publisher": "World Gold Council (Metals Focus data)", "tier": "T0",
     "published_at": "2026-11-03", "retrieved_at": RET,
     "quote": "ETFs and Similar Products 225.7 175.7 62.4 -47.3 211.2 ... Central Bank and Other Institutions 226.3 209.9 57.7 296.3 321.2 8 42 ... Total Bar and Coin 328.6 428.3 476.9 308.6 267.8 -13 -19 ... Jewellery Consumption ... 312.9 12 -17 ... LBMA Gold Price (US$/oz) 3,456.5 4,135.2 4,872.9 4,506.3 4,262.2 -5 23",
     "locator": "Table 1: Quarterly gold supply and demand by sector, tonnes (Q3'25..Q3'26, q/q%, y/y%)",
     "origin_id": "wgc-gdt-q3-2026", "origin_basis": "WGC季度供需统计原始发布", "supports": ["fact"],
     "evidence_kind": "document", "access_status": "ok", "date_nature": "Google News列示11月3日；页面数据截至9月30日",
     "selection": sel("区分官方需求与价格")},
    {"id": "WGC-OUTLOOK", "url": WGC, "canonical_url": WGC, "publisher": "World Gold Council", "tier": "T3",
     "published_at": "2026-11-03", "retrieved_at": RET,
     "quote": "Central bank buying likely to at least match 2025 after surprisingly strong Q3.",
     "locator": "Highlights / Outlook bullet", "origin_id": "wgc-gdt-q3-2026", "origin_basis": "WGC自身展望",
     "supports": ["view"], "evidence_kind": "opinion", "access_status": "ok",
     "selection": sel("官方需求展望", "useful")},
    {"id": "PM-DEC-HIKE", "url": PM_FED, "canonical_url": PM_FED, "publisher": "Polymarket Gamma API", "tier": "T1",
     "published_at": "unknown", "retrieved_at": RET,
     "quote": "Will the Fed increase interest rates by 25 bps after the December 2026 meeting? [\"0.755\", \"0.245\"] bestBid 0.75 bestAsk 0.76 updatedAt 2026-11-04T07:07:57Z",
     "locator": "raw/pm_fed.json event 'Fed Decision in December?'", "origin_id": "polymarket-fed-dec-2026",
     "origin_basis": "平台Gamma参考价（非CLOB订单簿）", "supports": ["price"], "evidence_kind": "market_quote", "access_status": "ok",
     "market_quote": {"quoted_at": "2026-11-04T07:07:57+00:00", "instrument": "Polymarket: Fed Decision in December? / +25bps",
                      "outcome": "Yes", "direction": "level", "value": 0.755, "unit": "USD/share", "quote_type": "indicative"},
     "selection": sel("市场对12月加息的定价")},
    {"id": "PM-GOLD-4300", "url": PM_GOLD, "canonical_url": PM_GOLD, "publisher": "Polymarket Gamma API", "tier": "T1",
     "published_at": "unknown", "retrieved_at": RET,
     "quote": "Will Gold (XAUUSD) hit (HIGH) $4,300 in November? [\"0.235\", \"0.765\"] 0.2 0.27",
     "locator": "public-search 'gold price' event 'What will Gold (XAUUSD) hit in November 2026?'", "origin_id": "polymarket-gold-nov-2026",
     "origin_basis": "平台Gamma参考价（非CLOB订单簿）", "supports": ["price"], "evidence_kind": "market_quote", "access_status": "ok",
     "market_quote": {"quoted_at": RET, "instrument": "Polymarket: Gold (XAUUSD) hit HIGH $4,300 in November 2026",
                      "outcome": "Yes", "direction": "level", "value": 0.235, "unit": "USD/share", "quote_type": "indicative"},
     "selection": sel("月内反弹空间的市场定价", "useful")},
    {"id": "PM-GOLD-4200", "url": PM_GOLD, "canonical_url": PM_GOLD, "publisher": "Polymarket Gamma API", "tier": "T1",
     "published_at": "unknown", "retrieved_at": RET,
     "quote": "Will Gold (XAUUSD) hit (HIGH) $4,200 in November? [\"0.43\", \"0.57\"] 0.4 0.46",
     "locator": "public-search 'gold price' event 'What will Gold (XAUUSD) hit in November 2026?'", "origin_id": "polymarket-gold-nov-2026",
     "origin_basis": "平台Gamma参考价（非CLOB订单簿）", "supports": ["price"], "evidence_kind": "market_quote", "access_status": "ok",
     "market_quote": {"quoted_at": RET, "instrument": "Polymarket: Gold (XAUUSD) hit HIGH $4,200 in November 2026",
                      "outcome": "Yes", "direction": "level", "value": 0.43, "unit": "USD/share", "quote_type": "indicative"},
     "selection": sel("月内反弹空间的市场定价", "useful")},
]
# 只取得标题、未读原文的新闻线索：保留候选但不选中
for sid, title, d in [
    ("N-OIL", "Oil drops 7% as Iran signals openness to peace talks - Reuters", "2026-11-03"),
    ("N-GOLD", "Gold rises as dollar weakens; Democrats score early wins in US midterm elections - Reuters", "2026-11-04"),
    ("N-MS", "Why Is the Gold Price Falling Even as Investors and Central Banks Pile In? - Morningstar", "2026-10-30"),
    ("N-GS", "Goldman Sachs Raises December Brent Oil Price Forecast to $105 - OilPrice.com", "2026-11-02"),
]:
    u = "https://news.google.com/rss/search?q=gold+price+when:7d"
    cands.append({"id": sid, "url": u, "canonical_url": u, "publisher": "Google News RSS headline", "tier": "T2",
                  "published_at": d, "retrieved_at": RET, "quote": title, "locator": "RSS item title",
                  "origin_id": None, "origin_basis": "仅取得聚合器标题，原始媒体家族未确认", "supports": ["view"], "evidence_kind": "opinion", "access_status": "snippet",
                  "selection": {"selected": False, "reason": "仅有标题，原文未取得；只作背景线索", "relevance": "context",
                                "purpose": "地缘/选举背景线索", "priority": "background"}})

sources = {"schema_version": 2, "as_of": AS_OF, "historical": False, "candidates": cands,
           "source_status": {
               "official": {"status": "ok", "reason": "FOMC声明、Fed日历、FRED实际利率与CPI已取得"},
               "market": {"status": "partial", "reason": "Yahoo延迟行情与Polymarket Gamma参考价；未取CLOB订单簿与CME FedWatch"},
               "media": {"status": "partial", "reason": "WebSearch/WebFetch工具报错；仅取得Google News标题，未读原文"},
               "consensus": {"status": "not_run", "reason": "未取得机构金价预测调查"},
               "community": {"status": "not_run", "reason": "本轮未运行Last30Days"}}}

A = AS_OF
def claim(i, t, typ, src=None, basis=None, **kw):
    c = {"id": i, "text": t, "type": typ, "as_of": A, "sources": [{"source_id": s} for s in (src or [])]}
    if basis is not None:
        c["basis"] = basis
    c.update(kw)
    return c

claims = [
    claim("P-GC-NOW", "2026年11月4日06:55 UTC，COMEX金期货主力连续合约报%.1f美元/盎司（延迟行情）。" % G_NOW, "price", ["PX-GC-NOW"], price_kind="indicative"),
    claim("P-GC-PEAK", "2026年1月29日，COMEX金期货收于%.1f美元/盎司，为过去一年收盘高点。" % G_PEAK, "price", ["PX-GC-PEAK"], price_kind="close"),
    claim("P-GC-APR", "2026年4月1日，COMEX金期货收于%.1f美元/盎司。" % G_APR, "price", ["PX-GC-APR"], price_kind="close"),
    claim("P-GC-LOW", "2026年10月30日，COMEX金期货收于%.1f美元/盎司，为过去一年收盘低点。" % G_LOW, "price", ["PX-GC-LOW"], price_kind="close"),
    claim("P-SI-PEAK", "2026年1月26日，COMEX银期货收于%.2f美元/盎司。" % S_PEAK, "price", ["PX-SI-PEAK"], price_kind="close"),
    claim("P-SI-NOW", "2026年11月4日，COMEX银期货报%.2f美元/盎司（延迟行情）。" % S_NOW, "price", ["PX-SI-NOW"], price_kind="indicative"),
    claim("P-CL-OCT30", "2026年10月30日，WTI原油期货收于%.2f美元/桶。" % C_OCT30, "price", ["PX-CL-OCT30"], price_kind="close"),
    claim("P-CL-NOW", "2026年11月4日，WTI原油期货报%.2f美元/桶（延迟行情）。" % C_NOW, "price", ["PX-CL-NOW"], price_kind="indicative"),
    claim("C-REAL", "10年期TIPS实际收益率：1月29日%.2f%%、4月1日%.2f%%、10月5日%.2f%%、11月2日%.2f%%。" % (ry["2026-01-29"], ry["2026-04-01"], ry["2026-10-05"], ry["2026-11-02"]), "fact", ["FRED-DFII10"]),
    claim("C-CPI", "2026年9月美国CPI同比约%.1f%%，核心CPI同比约%.1f%%（季调指数计算）。" % (CPI_Y, CORE_Y), "fact", ["FRED-CPI"]),
    claim("C-FED-SEP", "FOMC于2026年9月16日加息25个基点，目标区间升至3.75%—4.00%。", "fact", ["FED-SEP"]),
    claim("C-FED-OCT", "FOMC于2026年10月28日以10比2维持3.75%—4.00%；Cook与Hammack主张再加息25个基点。", "fact", ["FED-OCT"]),
    claim("C-CAL", "下一次FOMC会议为2026年12月8—9日，并发布经济预测摘要。", "fact", ["FED-CAL"]),
    claim("C-WGC", "WGC数据：2026年Q3央行购金321.2吨、同比增42%；ETF净流入211.2吨；金条金币267.8吨、同比降19%；首饰消费同比降17%；LBMA季度均价4262.2美元，环比降5%。", "fact", ["WGC-Q3"]),
    claim("V-WGC", "WGC预计2026年央行购金至少与2025年持平。", "view", ["WGC-OUTLOOK"]),
    claim("P-PM-DEC", "11月4日07:08 UTC，Polymarket“12月FOMC加息25个基点”Yes参考价0.755（bid 0.75 / ask 0.76）。", "price", ["PM-DEC-HIKE"], price_kind="indicative"),
    claim("P-PM-4300", "11月4日Polymarket“金价11月内触及4300美元”Yes参考价0.235（bid 0.20 / ask 0.27）。", "price", ["PM-GOLD-4300"], price_kind="indicative"),
    claim("P-PM-4200", "11月4日Polymarket“金价11月内触及4200美元”Yes参考价0.43（bid 0.40 / ask 0.46）。", "price", ["PM-GOLD-4200"], price_kind="indicative"),
    # 计算与推断
    claim("C-DD", "金价较1月29日高点回落%.1f%%；10月30日低点时回撤%.1f%%。白银同期从高点回落%.1f%%。" % (DD_NOW, DD_LOW, S_DD), "inference", basis=["P-GC-NOW", "P-GC-PEAK", "P-GC-LOW", "P-SI-PEAK", "P-SI-NOW"]),
    claim("C-LEG1", "第一段下跌（1月29日至4月1日）金价跌%.1f%%，同期实际利率只升%.2f个百分点；这段更像高位投机仓位出清，白银跌幅约为黄金两倍也与此一致。" % (DD_LEG1, ry["2026-04-01"] - ry["2026-01-29"]), "inference", basis=["P-GC-PEAK", "P-GC-APR", "C-REAL", "C-DD"]),
    claim("C-CORR", "按日收益计算，金价与油价的相关系数在2025年11月至2026年3月为%.2f（%d个交易日），4—7月为%.2f（%d日），8月至11月4日为%.2f（%d日）。4月后油价上涨日金价更常下跌。" % (CORR_PRE, N_PRE, CORR_A, N_A, CORR_B, N_B), "inference", basis=["P-GC-NOW", "P-CL-NOW", "C-REAL"]),
    claim("C-MECH", "第二段下跌的主线是利率：油价冲击推高总体CPI（%.1f%%，核心%.1f%%），美联储9月加息且10月仍有两票主张再加，10年期实际利率从约1.9%%升至2.6%%—3.0%%，持有黄金的机会成本显著上升。因此地缘冲突升级目前通过“油价→通胀→加息”路径压制金价，而非提供避险支撑。" % (CPI_Y, CORE_Y), "inference", basis=["C-CPI", "C-FED-SEP", "C-FED-OCT", "C-REAL", "C-CORR"]),
    claim("C-DEMAND", "Q3央行与ETF合计净买入约532吨，而季度均价仍环比下跌，10月继续创年内新低；官方买盘在放大，但目前没有抵消利率压力，更像是限制跌幅的底部力量，而非方向驱动。", "inference", basis=["C-WGC", "V-WGC", "P-GC-LOW"]),
    claim("C-OIL", "油价从10月30日%.2f美元回落至%.2f美元（%.1f%%），同期金价从%.1f美元回升至%.1f美元；两者反向移动与利率主线一致。" % (C_OCT30, C_NOW, C_MOVE, G_LOW, G_NOW), "inference", basis=["P-CL-OCT30", "P-CL-NOW", "P-GC-LOW", "P-GC-NOW", "C-MECH"]),
    claim("C-MARKET", "市场已为12月加息定价约四分之三概率；Polymarket认为金价11月内触及4200美元的概率约43%%、触及4300美元约23%%，即市场预期反弹有限、但不押注继续崩跌。", "inference", basis=["P-PM-DEC", "P-PM-4200", "P-PM-4300", "P-GC-NOW"]),
    claim("C-VIEW", "未来1—3个月（至12月FOMC及1月初）判断：金价大概率在3800—4300美元区间震荡，方向由油价—通胀—美联储链条决定。加息已大体被定价，因此不对称性在于鹰派预期退潮：若油价继续回落、10月CPI降温使12月加息落空，金价有修复空间；若油价重回110美元以上并迫使美联储连续加息，跌破3900美元的风险上升。白银弹性更大，波动方向与金价一致但幅度约两倍。", "inference", basis=["C-MECH", "C-DEMAND", "C-MARKET", "C-OIL", "C-CAL", "C-LEG1"]),
]
json.dump(sources, open(W / "sources.json", "w"), ensure_ascii=False, indent=1)
json.dump({"schema_version": 2, "as_of": AS_OF, "claims": claims}, open(W / "claims.json", "w"), ensure_ascii=False, indent=1)

H = [{"id": "H1", "explanation": "利率主线：油价通胀推动美联储加息与实际利率上升，主导金价",
      "discriminating_observation": "油价上涨日金价下跌；12月决议鹰派时金价走弱"},
     {"id": "H2", "explanation": "避险与官方买盘主线：地缘冲突和央行购金主导金价",
      "discriminating_observation": "冲突升级、央行加码时金价走强，与油价正相关"},
     {"id": "H3", "explanation": "仓位出清主线：高位投机仓位去杠杆，与利率无关",
      "discriminating_observation": "利率未变时金银仍大跌，白银跌幅远大于黄金"}]
tests = [
    {"id": "T1", "observe": "4月以来金价与油价日收益的相关符号", "source": "COMEX/NYMEX日行情与FRED实际利率", "by": "2026-11-04",
     "outcomes": [{"hypothesis_id": "H1", "prediction": "相关为负：油价涨→加息预期升→金价跌"},
                  {"hypothesis_id": "H2", "prediction": "相关为正：冲突升级同时推高油价与避险金价"}]},
    {"id": "T2", "observe": "Q3官方及ETF买入规模与同期价格方向", "source": "WGC Gold Demand Trends Q3 2026", "by": "2026-11-04",
     "outcomes": [{"hypothesis_id": "H1", "prediction": "买盘强但价格仍下跌"},
                  {"hypothesis_id": "H2", "prediction": "买盘强且价格企稳上涨"}]},
    {"id": "T3", "observe": "12月8—9日FOMC决议及点阵图后的金价反应", "source": "Fed声明与金价行情", "by": "2026-12-10",
     "outcomes": [{"hypothesis_id": "H1", "prediction": "加息或鹰派点阵图使金价走弱，意外不加息使金价明显反弹"},
                  {"hypothesis_id": "H2", "prediction": "金价对决议反应有限，主要跟随地缘新闻与央行数据"}]},
    {"id": "T4", "observe": "1月29日至4月1日金价跌幅与同期实际利率变化", "source": "COMEX日行情与FRED DFII10", "by": "2026-11-04",
     "outcomes": [{"hypothesis_id": "H1", "prediction": "跌幅伴随实际利率显著上升"},
                  {"hypothesis_id": "H3", "prediction": "利率基本不变而金银大幅下跌"}]}]
design = {"question_kind": "event_forecast", "method": "reference_class_scenarios",
          "rationale": "用户问黄金等资产的可能走势，按1—3个月窗口（到12月FOMC与1月初）做情景预测。长期条件是去美元化背景下的央行购金；近期环境是伊朗冲突引发油价冲击、通胀回升和美联储重启加息；事前预期用联邦基金利率预测市场与金价触及合约代替；后续用12月FOMC和10月CPI区分利率主线与避险主线。白银与原油作为联动资产附带判断。",
          "baseline": "2026年11月4日金价约4033美元、实际利率2.62%、12月加息定价约75%。",
          "price_relevance": True,
          "mechanism_chain": ["地缘冲突与油价", "总体通胀", "美联储加息预期", "实际利率", "金价"],
          "discrimination_tests": tests}
plan = {"schema_version": 2, "analysis_version": 1, "question": "研究下当前市场的黄金等可能走势", "type": "asset",
        "task": "黄金及联动资产1—3个月走势情景研究", "entity": "黄金（COMEX金期货/XAUUSD），附白银、原油",
        "as_of": AS_OF, "historical": False,
        "decision_needed": "判断未来1—3个月金价更可能的方向与区间、主导驱动是什么、哪些观察会改变判断。",
        "prior_judgment": "首次研究，无既有判断。",
        "comparison": {"period": "2025-11-04至2026-11-04日频，重点2026-04以后", "unit": "USD/oz、百分比、吨", "scope": "COMEX期货连续合约、10年期TIPS、WGC全球需求"},
        "resolution_contract": {"indicator": "COMEX金期货主力连续合约收盘价", "target_period": "2026-11-04至2027-01-08",
                                "source": "交易所行情", "check_at": "2026-12-10与2027-01-08"},
        "budget": {"max_queries": 12, "max_followups": 1},
        "stop_condition": "取得价格、利率、政策与需求的同口径数据并能区分主线，或预算内无法补齐。",
        "research_design": design, "hypotheses": H,
        "queries": [
            {"question": "过去一年金银油价与实际利率路径？", "query": "Yahoo chart GC=F SI=F CL=F; FRED DFII10 DGS10 T10YIE", "source": "行情与FRED", "purpose": "计算回撤与相关", "test_ids": ["T1", "T4"]},
            {"question": "美联储最近决议与下一会议？", "query": "federalreserve.gov press_monetary feed; fomccalendars", "source": "Fed", "purpose": "政策路径", "test_ids": ["T3"]},
            {"question": "Q3官方与投资需求？", "query": "WGC Gold Demand Trends Q3 2026", "source": "WGC", "purpose": "检验买盘与价格方向", "test_ids": ["T2"]},
            {"question": "市场对12月加息和11月金价的定价？", "query": "Polymarket Fed December 2026; gold price November 2026", "source": "Polymarket Gamma", "purpose": "事前预期基准", "test_ids": ["T3"]},
            {"question": "近期地缘与油价新闻背景？", "query": "Google News RSS gold price / oil Brent when:7d", "source": "媒体标题", "purpose": "背景线索", "test_ids": []}]}
json.dump(plan, open(W / "plan.json", "w"), ensure_ascii=False, indent=1)

atests = []
for t in tests:
    base = {"id": t["id"], "outcomes": t["outcomes"], "by": t["by"]}
    if t["id"] == "T1":
        base.update(status="observed", claim_ids=["P-GC-NOW", "P-CL-NOW", "C-CORR"], supports=["H1"], weakens=["H2"],
                    interpretation="4月后金油相关转负（%.2f、%.2f），符合利率主线，不符合避险主线；相关不等于因果，但符号稳定。" % (CORR_A, CORR_B),
                    next_observation="油价大幅波动日的金价方向", supports_if="油价上涨日金价继续下跌", weakens_if="冲突升级日金价与油价同涨")
    elif t["id"] == "T2":
        base.update(status="observed", claim_ids=["C-WGC", "P-GC-LOW", "C-DEMAND"], supports=["H1"], weakens=["H2"],
                    interpretation="央行购金同比增42%、ETF回流，价格仍下跌，说明买盘未成为方向驱动。",
                    next_observation="Q4央行与ETF数据及10—11月月度央行购金", supports_if="买盘维持高位而价格继续跟随利率", weakens_if="买盘加速且金价在利率上行时仍走强")
    elif t["id"] == "T3":
        base.update(status="missing", claim_ids=[], supports=[], weakens=[], gap_reason="12月FOMC尚未举行",
                    interpretation="尚待观察，不能裁定。", next_observation="12月9日决议、点阵图与当日金价",
                    supports_if="决议鹰派时金价下跌或意外不加息时金价急升", weakens_if="金价对决议几乎无反应")
    else:
        base.update(status="observed", claim_ids=["P-GC-PEAK", "P-GC-APR", "C-REAL", "C-LEG1"], supports=["H3"], weakens=["H1"],
                    interpretation="第一段下跌期间实际利率仅小幅上升，利率主线解释不了这一段；仓位出清更合适。这只削弱H1对第一段的解释，不影响其对4月后的解释。",
                    next_observation="CFTC持仓与ETF持仓是否已回到低位", supports_if="持仓已大幅出清", weakens_if="持仓仍拥挤")
    atests.append(base)

analysis = {"version": 1, "question_kind": "event_forecast", "method": "reference_class_scenarios", "price_relevance": True,
            "baseline": design["baseline"], "baseline_claim_ids": ["P-GC-NOW", "C-REAL", "P-PM-DEC"],
            "mechanism_chain": design["mechanism_chain"], "hypotheses": [{"id": h["id"], "explanation": h["explanation"]} for h in H],
            "tests": atests, "conclusion": claims[-1]["text"], "conclusion_claim_ids": ["C-VIEW"],
            "model_status": "not_applicable", "model_reason": "商品无现金流，不适用经营桥或DCF；以情景与市场定价比较代替。", "models": [],
            "market": {"status": "assessed", "reason": "比较预测市场对12月加息与11月金价触及的定价和研究情景。",
                       "claim_ids": ["P-PM-DEC", "P-PM-4200", "P-PM-4300", "P-GC-NOW", "C-MARKET", "C-VIEW"], "model_ids": [],
                       "implied_expectation": "12月加息约75%；11月内触及4200约43%、4300约23%。",
                       "research_expectation": "同意加息为基准，但认为金价对“加息落空”的上行弹性大于对“如期加息”的下行弹性。",
                       "gap": "方向上与市场一致，分歧只在不对称性；未校准触及概率，不构成已验证错价。",
                       "conditions": "10月CPI、油价是否重回110美元、12月点阵图。"}}

report = {
    "schema_version": 2, "title": "黄金：利率压顶、官方托底，方向看油价与12月FOMC",
    "question": "研究下当前市场的黄金等可能走势", "task": plan["task"], "type": "asset", "as_of": AS_OF,
    "answer": {"text": claims[-1]["text"], "claim_ids": ["C-VIEW", "C-DD"]},
    "findings": [
        {"title": "这轮下跌分两段，第二段是利率驱动", "claim_ids": ["C-DD", "C-LEG1", "C-MECH", "C-REAL", "C-FED-SEP", "C-FED-OCT"],
         "text": "金价较1月高点回落约%.0f%%。1—3月的第一段下跌发生在实际利率几乎不变时，更像投机仓位出清；4月以后，油价推高通胀、美联储9月加息，10年期实际利率升到2.6%%—3.0%%，成为主要压力。" % -DD_NOW,
         "why_it_matters": "两段原因不同：仓位出清大体已经完成，接下来的方向主要取决于利率。",
         "increment": {"kind": "connection", "baseline": "常见叙事把下跌归为“泡沫破裂”", "detail": "用实际利率与时间分段区分两种原因"}},
        {"title": "战争升级目前对黄金是利空", "claim_ids": ["C-CORR", "C-OIL"],
         "text": "4月以后金价与油价日收益相关为负（%.2f / %.2f）。11月2—4日油价回落约%.0f%%，金价反而从低点回升约3%%。" % (CORR_A, CORR_B, -C_MOVE),
         "why_it_matters": "这与“地缘冲突利好黄金”的直觉相反：冲突缓和反而可能利好金价。",
         "increment": {"kind": "contradiction", "baseline": "避险资产直觉：冲突升级利好黄金", "detail": "分阶段金油相关系数为负，与直觉相反"}},
        {"title": "央行在买，但没能扭转价格", "claim_ids": ["C-WGC", "C-DEMAND", "V-WGC"],
         "text": "Q3央行购金321吨、同比多42%，ETF也回流211吨，但季度均价环比仍跌5%，10月又创年内新低。",
         "why_it_matters": "官方买盘更像底部支撑，限制大幅下跌，但不足以单独带动上涨。",
         "increment": {"kind": "contradiction", "baseline": "“央行购金必涨”", "detail": "买盘与价格背离"}}],
    "alternatives": [
        {"title": "避险与官方买盘重新主导", "claim_ids": ["C-DEMAND", "V-WGC"],
         "text": "若冲突演变为金融制裁或美元资产信任问题，央行购金加速，金价可能脱离利率上涨。目前相关性数据不支持这一点。"},
        {"title": "仓位仍未出清", "claim_ids": ["C-LEG1", "C-DD"],
         "text": "白银从高点跌约55%，说明投机出清剧烈；若持仓仍拥挤，可能继续抛售。本轮未取CFTC持仓，无法核实。"}],
    "limitations": [
        {"text": "网页搜索工具不可用，媒体只取得标题；伊朗和谈等地缘归因未读原文，只作背景，判断依赖价格与官方数据。", "material": False, "claim_ids": []},
        {"text": "未取得CFTC持仓、CME FedWatch与机构金价预测调查，仓位出清程度与卖方共识是缺口。", "material": True, "claim_ids": []}],
    "watch": [
        {"signal": "10月CPI（11月中旬发布）及油价是否重回110美元", "meaning": "降温则12月加息概率下降，利好金价；反之支持继续下探。", "claim_ids": ["C-CPI", "C-MECH"]},
        {"signal": "12月8—9日FOMC决议与点阵图", "meaning": "检验T3：金价对鹰派/鸽派意外的反应强度决定利率主线是否仍然主导。", "claim_ids": ["C-CAL", "P-PM-DEC"]},
        {"signal": "央行月度购金与Q4 ETF流向", "meaning": "若在利率上行时金价仍走强，说明避险/官方主线开始接管。", "claim_ids": ["C-WGC"]}],
    "tables": [{"title": "关键数据快照", "claim_ids": ["P-GC-NOW", "P-GC-PEAK", "P-GC-LOW", "P-SI-NOW", "P-CL-NOW", "C-REAL", "P-PM-DEC"],
                "columns": ["指标", "数值"],
                "rows": [["金价（11月4日）", G_NOW], ["金价1月29日高点", G_PEAK], ["金价10月30日低点", G_LOW],
                         ["白银（11月4日）", S_NOW], ["WTI原油（11月4日）", C_NOW], ["10年期实际利率%（11月2日）", ry["2026-11-02"]],
                         ["12月加息定价（Polymarket）", 0.755]],
                "note": "期货连续合约延迟行情；Polymarket为Gamma参考价。"}],
    "analysis": analysis,
    "opportunity": {"version": 1, "applicability": "trading",
        "market_view": {"basis": "price_implied", "claim_ids": ["P-PM-DEC", "P-PM-4200", "C-MARKET"],
                        "text": "市场押注美联储12月再加息（约75%），并认为11月金价反弹有限（触及4300约23%）。"},
        "variant": {"claim_ids": ["C-VIEW", "C-OIL"], "text": "方向与市场基本一致；分歧在于加息已大体定价，鹰派落空的上行弹性大于如期加息的下行弹性。"},
        "edge": {"claim_ids": ["C-CORR", "C-MECH"], "text": "优势来自金油负相关的传导识别：油价与CPI可作为金价的领先观察。未校准概率，不构成已验证错价。"},
        "catalyst": {"by": "2026-12-09T14:00:00-05:00", "claim_ids": ["C-CAL", "C-CPI"], "text": "11月中旬10月CPI与12月9日FOMC决议。"},
        "payoff": {"claim_ids": ["C-DD", "C-OIL"], "text": "金价已从高点跌约24%，下行空间受官方买盘限制；若油价重新冲高并迫使连续加息，判断失效，金价可能跌破3900美元。"},
        "assessment": {"status": "watch", "claim_ids": ["C-VIEW", "C-MARKET"], "text": "等待10月CPI与油价方向；在12月FOMC前，这是最能区分情景的观察。"},
        "triggers": [
            {"id": "TR1", "signal": "WTI收盘重回110美元以上", "by": "2026-12-09", "claim_ids": ["P-CL-NOW", "C-MECH"],
             "supports_if": "金价同步下跌，利率主线继续", "weakens_if": "金价随油价上涨", "invalidates_if": "金价在油价与实际利率同升时创新高"},
            {"id": "TR2", "signal": "Polymarket 12月加息Yes跌破0.5", "by": "2026-12-08", "claim_ids": ["P-PM-DEC"],
             "supports_if": "金价同期上涨至4200美元以上", "weakens_if": "金价不涨", "invalidates_if": "加息预期下降但金价跌破3900美元"}]},
}
json.dump(report, open(W / "report.json", "w"), ensure_ascii=False, indent=1)

audit = {"as_of": AS_OF,
         "intent": {"original_question": "研究下当前市场的黄金等可能走势", "relevant_user_context": [], "corrections": [],
                    "task_mode": "forecast", "interpreted_goal": "给出黄金（及白银、原油等联动资产）未来1—3个月的方向/区间判断、驱动与改变判断的条件",
                    "required_answer": ["当前金价与近一年表现", "主导驱动及证据", "1—3个月情景与区间", "市场已定价什么", "改变判断的观察", "白银等联动资产"]},
         "context_review": {"long_term": "央行购金与去美元化", "recent": "伊朗冲突油价冲击、CPI回升、美联储9月加息",
                            "prior_expectations": "Polymarket 12月加息与11月金价触及定价", "new_transmission": "油价→CPI→加息预期→实际利率→金价",
                            "next_test": "10月CPI、12月FOMC", "unresolved": "CFTC持仓、机构预测调查、新闻原文"},
         "queries": plan["queries"],
         "execution": [{"command": "WebSearch x3", "exit_code": 1, "reason": "工具模型错误，未执行"},
                       {"command": "WebFetch gold.org", "exit_code": 1, "reason": "同上；改用curl取得"},
                       {"command": "curl stooq", "exit_code": 0, "reason": "返回JS验证页，未绕过，弃用"},
                       {"command": "curl Yahoo chart / FRED / Fed / WGC / Polymarket Gamma / Google News RSS", "exit_code": 0, "log": "raw/"}],
         "review": {"status": "not_run", "reason": "本轮未调用独立red-team审查；由主研究者自查，判断未经独立复审"}}
json.dump(audit, open(W / "audit.json", "w"), ensure_ascii=False, indent=1)
print("built", G_NOW, G_PEAK, DD_NOW, DD_LEG1, S_DD, C_MOVE, CPI_Y, CORE_Y, CORR_PRE, CORR_A, CORR_B)
