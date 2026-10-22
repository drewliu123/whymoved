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

from whymoved import news, prices  # noqa: E402
from whymoved.analyze import Result, _context  # noqa: E402
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


class SymbolTest(unittest.TestCase):
    def test_crypto_variants(self):
        for raw in ("btc", "BTC-USD", "BTCUSDT", "$btc", "比特币", "bitcoin"):
            a = resolve(raw)
            self.assertEqual((a.symbol, a.kind), ("BTC", "crypto"), raw)

    def test_stock(self):
        a = resolve("$nvda")
        self.assertEqual((a.symbol, a.kind, a.exchange_tz), ("NVDA", "stock", "America/New_York"))
        self.assertEqual(resolve("英伟达").symbol, "NVDA")


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

    def test_json_shape(self):
        d = to_dict(self.make([0.0], [100, 100, 105, 105]))
        for key in ("asset", "period", "window", "benchmarks", "market_context", "news", "rules", "caveats"):
            self.assertIn(key, d)
        self.assertEqual(set(d["news"]), {"candidates", "after_move", "background"})


if __name__ == "__main__":
    unittest.main()
