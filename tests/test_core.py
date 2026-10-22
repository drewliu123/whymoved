"""Offline tests: no network, no API keys.

Run: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "whymoved", "scripts"))

from whymoved import filings, news, prices  # noqa: E402
from whymoved.analyze import Result, _context, _search_name, ex_asset  # noqa: E402
from whymoved.prices import Bar  # noqa: E402
from whymoved.report import to_dict, to_text  # noqa: E402
from whymoved.symbols import resolve  # noqa: E402
from whymoved.window import change_between, find_window  # noqa: E402

T0 = datetime(2026, 10, 14, 13, 30, tzinfo=timezone.utc)  # 09:30 ET
FIVE = 300


def bars_from(prices_, start=T0, step=FIVE):
    return [Bar(start + timedelta(seconds=i * step), p) for i, p in enumerate(prices_)]


class WindowTest(unittest.TestCase):
    def test_finds_the_spike_not_the_whole_day(self):
        # flat, then a sharp +5% over three bars, then flat
        p = [100, 100.1, 99.9, 100, 101.5, 103.5, 105, 105.1, 104.9, 105]
        w = find_window(bars_from(p), FIVE)
        self.assertAlmostEqual(w.total_pct, 0.05, places=3)
        self.assertGreater(w.pct, 0.035)
        # window starts at the close of the bar before the jump (index 3) and ends by index 6
        self.assertEqual(w.start, T0 + timedelta(seconds=4 * FIVE))
        self.assertLessEqual(w.end, T0 + timedelta(seconds=7 * FIVE))
        self.assertFalse(w.is_gap)

    def test_down_move(self):
        p = [50, 50, 49.9, 47, 45, 45.1, 45]
        w = find_window(bars_from(p), FIVE)
        self.assertLess(w.pct, -0.05)
        self.assertLess(w.total_pct, 0)

    def test_overnight_gap_is_flagged(self):
        prev_close = Bar(T0 - timedelta(hours=17, minutes=35), 100.0)  # 15:55 ET the day before
        today = bars_from([108, 108.2, 108.1, 108.3])
        w = find_window([prev_close] + today, FIVE)
        self.assertTrue(w.is_gap)
        self.assertAlmostEqual(w.pct, 0.08, places=2)

    def test_overshoot_share_above_one(self):
        p = [100, 104, 106, 103, 102]  # up 6%, gives back to +2%
        w = find_window(bars_from(p), FIVE)
        self.assertGreater(w.share, 1.0)

    def test_change_between_uses_close_times(self):
        b = bars_from([100, 110, 121])
        # at T0 + 1 bar, only the first bar has closed
        self.assertAlmostEqual(change_between(b, FIVE, T0 + timedelta(seconds=FIVE), T0 + timedelta(seconds=3 * FIVE)), 0.21)

    def test_needs_two_bars(self):
        with self.assertRaises(ValueError):
            find_window(bars_from([100]), FIVE)


RSS = b"""<?xml version="1.0"?><rss><channel>
<item><title>Nvidia wins huge AI order - Reuters</title><link>https://x/1</link>
  <pubDate>Tue, 14 Oct 2026 13:10:00 GMT</pubDate><source url="https://reuters.com">Reuters</source></item>
<item><title>Nvidia shares jump 6% after AI order - CNBC</title><link>https://x/2</link>
  <pubDate>Tue, 14 Oct 2026 14:40:00 GMT</pubDate><source url="https://cnbc.com">CNBC</source></item>
<item><title>Nvidia stock rises as traders cheer - Benzinga</title><link>https://x/3</link>
  <pubDate>Tue, 14 Oct 2026 13:50:00 GMT</pubDate><source url="https://benzinga.com">Benzinga</source></item>
<item><title>Nvidia stock price today - Fortune</title><link>https://x/4</link>
  <pubDate>Tue, 14 Oct 2026 12:00:00 GMT</pubDate><source url="https://fortune.com">Fortune</source></item>
<item><title>Nvidia shares slump on export worries - Bloomberg</title><link>https://x/5</link>
  <pubDate>Tue, 14 Oct 2026 12:30:00 GMT</pubDate><source url="https://bloomberg.com">Bloomberg</source></item>
<item><title>Nvidia history explained - Blog</title><link>https://x/6</link>
  <pubDate>Fri, 10 Oct 2026 12:00:00 GMT</pubDate><source url="https://blog">Blog</source></item>
</channel></rss>"""


class NewsTest(unittest.TestCase):
    def setUp(self):
        self.asset = resolve("NVDA")
        self.start = datetime(2026, 10, 14, 13, 30, tzinfo=timezone.utc)
        self.end = datetime(2026, 10, 14, 14, 5, tzinfo=timezone.utc)
        s = news.parse_rss(RSS)
        s = news.classify(s, self.start, self.end)
        self.stories = {x.url: x for x in news.score(s, self.asset, "NVIDIA", self.start, move_sign=1)}

    def test_source_suffix_is_stripped(self):
        self.assertEqual(self.stories["https://x/1"].title, "Nvidia wins huge AI order")
        self.assertEqual(self.stories["https://x/1"].source, "Reuters")

    def test_story_before_window_is_candidate(self):
        self.assertEqual(self.stories["https://x/1"].timing, "candidate")

    def test_story_after_window_is_never_a_cause(self):
        self.assertEqual(self.stories["https://x/2"].timing, "after_move")

    def test_story_describing_the_move_during_window_is_a_report(self):
        self.assertEqual(self.stories["https://x/3"].timing, "after_move")

    def test_old_story_is_background(self):
        self.assertEqual(self.stories["https://x/6"].timing, "background")

    def test_noise_and_opposite_direction_are_penalised(self):
        good = self.stories["https://x/1"].score
        self.assertLess(self.stories["https://x/4"].score, good)
        self.assertLess(self.stories["https://x/5"].score, good)

    def test_direction(self):
        self.assertEqual(news.direction("Bitcoin plunges below $80k"), -1)
        self.assertEqual(news.direction("Tesla rallies on deliveries"), 1)
        self.assertEqual(news.direction("Fed holds rates"), 0)

    def test_dedupe_keeps_best(self):
        a = news.Story("Apple unveils new iPhone at event today in Cupertino", "Reuters", "u1", self.start, score=3)
        b = news.Story("Apple unveils new iPhone at event today in Cupertino, analysts react", "Blog", "u2", self.start, score=1)
        self.assertEqual([x.url for x in news.dedupe([b, a])], ["u1"])

    def test_cause_headline_inside_window_stays_a_candidate(self):
        # An earnings beat released as the move starts is the cause, not a report of the move.
        s = news.Story("Nvidia beats estimates, raises guidance", "Reuters", "u", self.start + timedelta(minutes=5))
        recap = news.Story("Nvidia shares jump after earnings", "CNBC", "r", self.start + timedelta(minutes=20))
        news.classify([s, recap], self.start, self.end)
        news.score([s, recap], self.asset, "NVIDIA", self.start, move_sign=1)
        self.assertEqual(s.timing, "candidate")
        self.assertEqual(recap.timing, "after_move")

    def test_story_not_mentioning_the_asset_ranks_below(self):
        other = news.Story("Tesla recalls 2 million vehicles", "Reuters", "t", self.start - timedelta(minutes=30))
        mine = news.Story("Nvidia wins AI order", "Reuters", "n", self.start - timedelta(minutes=30))
        news.classify([other, mine], self.start, self.end)
        news.score([other, mine], self.asset, "NVIDIA", self.start, move_sign=1)
        self.assertIn("does not mention the asset", other.reasons)
        self.assertLess(other.score, mine.score)

    def test_short_tickers_match_case_sensitively(self):
        keys = news.asset_keys(resolve("ON"), "ON Semiconductor Corporation")
        self.assertFalse(news.mentions("Stocks fall on Fed worries", keys))
        self.assertTrue(news.mentions("ON Semi soars after earnings", keys))

    def test_roundups_are_noise(self):
        self.assertTrue(news.NOISE.search("Stocks making the biggest moves after hours: Tesla, Meta"))

    def test_chinese_headlines(self):
        self.assertEqual(news.move_direction("腾讯控股大涨"), 1)
        self.assertEqual(news.direction("茅台业绩不及预期"), -1)
        self.assertTrue(news.PRICE_RECAP.search("腾讯控股涨超3%"))
        keys = news.asset_keys(resolve("腾讯"), "Tencent Holdings Limited")
        self.assertTrue(news.mentions("腾讯发布三季度财报", keys))
        self.assertTrue(news.mentions("Tencent beats estimates", keys))

    def test_filing_after_the_move_is_a_pointer(self):
        f = news.Story("SEC 8-K: results of operations (earnings)", "SEC EDGAR", "f", self.end + timedelta(hours=4), kind="filing")
        news.classify([f], self.start, self.end)
        news.score([f], self.asset, "NVIDIA", self.start, move_sign=1)
        self.assertEqual(f.timing, "after_move")
        self.assertTrue(any("announced earlier" in r for r in f.reasons))

    def test_gather_survives_failed_extra_evidence(self):
        def boom():
            raise RuntimeError("SEC down")
        with mock.patch.object(news, "fetch", return_value=RSS):
            out = news.gather(self.asset, "NVIDIA", self.start, self.end, 1, extra_fn=boom)
        self.assertTrue(out)

    def test_non_google_links_are_left_alone(self):
        self.assertEqual(news.decode_google_url("https://www.reuters.com/x"), "https://www.reuters.com/x")


class FilingsTest(unittest.TestCase):
    def test_parse_filings_window_and_items(self):
        data = {"filings": {"recent": {
            "form": ["8-K", "4", "8-K"],
            "acceptanceDateTime": ["2026-10-22T00:41:42.000Z", "2026-10-21T22:00:00.000Z", "2026-09-01T12:00:00.000Z"],
            "accessionNumber": ["0001628280-26-066738", "x", "y"],
            "primaryDocument": ["tsla-20261021.htm", "a.xml", "b.htm"],
            "items": ["2.02,9.01", "", "8.01"],
            "reportDate": ["2026-10-21", "", ""],
        }}}
        start = datetime(2026, 10, 21, 0, 0, tzinfo=timezone.utc)
        out = filings.parse_filings(data, 1318605, start, start + timedelta(days=2))
        self.assertEqual(len(out), 1)  # form 4 is not evidence, September is out of range
        self.assertIn("results of operations", out[0].title)
        self.assertIn("event date 2026-10-21", out[0].title)
        self.assertTrue(out[0].url.endswith("/1318605/000162828026066738/tsla-20261021.htm"))
        self.assertEqual(out[0].kind, "filing")


class SymbolTest(unittest.TestCase):
    def test_crypto_variants(self):
        for raw in ("btc", "BTC-USD", "BTCUSDT", "$btc", "比特币", "bitcoin"):
            a = resolve(raw)
            self.assertEqual((a.symbol, a.kind), ("BTC", "crypto"), raw)

    def test_stock(self):
        a = resolve("$nvda")
        self.assertEqual((a.symbol, a.kind, a.exchange_tz), ("NVDA", "stock", "America/New_York"))
        self.assertEqual(resolve("英伟达").symbol, "NVDA")
        self.assertEqual(resolve("brk.b").symbol, "BRK-B")

    def test_hong_kong(self):
        for raw in ("700", "0700", "00700", "0700.HK", "hk0700", "腾讯"):
            a = resolve(raw)
            self.assertEqual((a.symbol, a.market, a.exchange_tz), ("0700.HK", "hk", "Asia/Hong_Kong"), raw)
        self.assertEqual(resolve("腾讯").zh_name, "腾讯")

    def test_mainland(self):
        for raw, sym in (("600519", "600519.SS"), ("sh600519", "600519.SS"), ("600519.SH", "600519.SS"),
                         ("000858", "000858.SZ"), ("300750.SZ", "300750.SZ"), ("688256", "688256.SS"), ("茅台", "600519.SS")):
            a = resolve(raw)
            self.assertEqual((a.symbol, a.market), (sym, "cn"), raw)

    def test_company_name_for_search(self):
        self.assertEqual(_search_name("Alibaba Group Holding Limited"), "Alibaba")
        self.assertEqual(_search_name("Kweichow Moutai Co., Ltd."), "Kweichow Moutai")
        self.assertEqual(_search_name("Tesla, Inc."), "Tesla")


class NasdaqFallbackTest(unittest.TestCase):
    def test_eastern_wall_clock_is_converted_to_utc(self):
        # Nasdaq writes 09:30 ET as if it were 09:30 UTC
        fake_ms = int(datetime(2026, 10, 14, 9, 30, tzinfo=timezone.utc).timestamp() * 1000)
        payload = {"data": {"chart": [{"x": fake_ms, "y": 101.0}], "chartPrevClose": 100.0}}
        with mock.patch.object(prices, "fetch_json", return_value=payload):
            bars, sec = prices.nasdaq_today("NVDA")
        self.assertEqual(sec, 60)
        self.assertEqual(bars[1].t, datetime(2026, 10, 14, 13, 30, tzinfo=timezone.utc))
        self.assertEqual(bars[0].close, 100.0)  # synthetic previous close
        self.assertLess(bars[0].t, bars[1].t)


class ReportTest(unittest.TestCase):
    def make(self, ctx_moves, pct_bars):
        w = find_window(bars_from(pct_bars), FIVE)
        r = Result(asset=resolve("NVDA"), name="NVIDIA", period_start=T0, period_end=T0 + timedelta(hours=1), window=w)
        r.benchmarks = [{"symbol": "SPY", "label": "S&P 500", "window_change": m, "period_change": m} for m in ctx_moves]
        r.context = _context(w, r.benchmarks)
        return r

    def test_market_wide_context(self):
        r = self.make([0.045], [100, 100, 105, 105])
        self.assertEqual(r.context, "market_wide")
        self.assertIn("整体行情", to_text(r))

    def test_asset_specific_and_no_news(self):
        r = self.make([0.001], [100, 100, 105, 105])
        self.assertEqual(r.context, "asset_specific")
        text = to_text(r, lang="en")
        self.assertIn("No story published before the move clearly explains it.", text)

    def test_quiet_move_is_called_noise(self):
        r = self.make([0.0], [100, 100.2, 100.3, 100.4])
        self.assertFalse(to_dict(r)["notable"])
        self.assertIn("正常波动", to_text(r))

    def test_benchmark_without_the_asset(self):
        # SMH +1.4% while NVDA (20% of SMH) is +2%: without NVDA the sector is up only ~1.25%.
        self.assertAlmostEqual(ex_asset(0.014, 0.20, 0.02), 0.0125)
        self.assertIsNone(ex_asset(None, 0.2, 0.02))
        w = find_window(bars_from([100, 100, 102, 102]), FIVE)
        raw = [{"symbol": "SMH", "window_change": 0.013}]
        self.assertEqual(_context(w, raw), "market_wide")
        raw[0]["window_change_ex_asset"] = ex_asset(0.013, 0.20, w.pct)
        self.assertEqual(_context(w, raw), "partly_market")

    def test_notable_is_relative_to_the_assets_own_volatility(self):
        r = self.make([0.0], [100, 100, 102, 102])  # +2%
        r.daily_vol = 0.035  # a volatile name: 2% is a normal day
        self.assertFalse(to_dict(r)["notable"])
        r.daily_vol = 0.008  # a sleepy name: 2% is news
        d = to_dict(r)
        self.assertTrue(d["notable"])
        self.assertAlmostEqual(d["move_vs_typical"], 2.5, places=1)
        self.assertIn("2.5×", to_text(r, lang="en"))

    def test_json_shape(self):
        d = to_dict(self.make([0.0], [100, 100, 105, 105]))
        for key in ("asset", "period", "window", "benchmarks", "market_context", "news", "rules", "caveats"):
            self.assertIn(key, d)
        self.assertEqual(set(d["news"]), {"candidates", "after_move", "background"})


if __name__ == "__main__":
    unittest.main()
