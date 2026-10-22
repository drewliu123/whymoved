"""End-to-end runs of analyze() on recorded-style data. No network.

Run: python3 -m unittest discover -s tests
"""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "whymoved", "scripts"))

from whymoved import news, prices  # noqa: E402
from whymoved.analyze import analyze  # noqa: E402
from whymoved.cli import default_lang  # noqa: E402
from whymoved.net import FetchError  # noqa: E402
from whymoved.prices import Bar  # noqa: E402
from whymoved.report import to_dict, to_text  # noqa: E402

ET = ZoneInfo("America/New_York")
FIVE = 300


def session(day, start_hm, end_hm, price_at):
    """5-minute bars from start_hm to end_hm (ET, exclusive); price_at(local_time) -> close."""
    t = datetime(*day, *start_hm, tzinfo=ET)
    end = datetime(*day, *end_hm, tzinfo=ET)
    out = []
    while t < end:
        out.append(Bar(t.astimezone(timezone.utc), price_at(t)))
        t += timedelta(seconds=FIVE)
    return out


def earnings_day_bars():
    """Flat Tuesday at 100, earnings after the close push it to 108, Wednesday holds ~108.5."""
    def tue(t):
        hm = (t.hour, t.minute)
        if hm < (16, 5):
            return 100.0 + (0.05 if t.minute % 10 else -0.05)
        return {(16, 5): 103.0, (16, 10): 106.0}.get(hm, 108.0)

    def wed(t):
        return 108.5 + (0.05 if t.minute % 10 else -0.05)

    return session((2026, 10, 13), (4, 0), (20, 0), tue) + session((2026, 10, 14), (4, 0), (20, 0), wed)


def flat(sym_price):
    return session((2026, 10, 13), (4, 0), (20, 0), lambda t: sym_price) + session(
        (2026, 10, 14), (4, 0), (20, 0), lambda t: sym_price
    )


def fake_yahoo(symbol, start, end):
    if symbol == "NVDA":
        return earnings_day_bars(), FIVE, "NVIDIA Corporation"
    return flat({"SPY": 600.0, "QQQ": 520.0, "SMH": 300.0}[symbol]), FIVE, symbol


def rss(*items):
    body = "".join(
        f"<item><title>{t} - {src}</title><link>https://x/{i}</link><pubDate>{pub}</pubDate>"
        f'<source url="https://s">{src}</source></item>'
        for i, (t, src, pub) in enumerate(items)
    )
    return f'<?xml version="1.0"?><rss><channel>{body}</channel></rss>'.encode()


EARNINGS_NEWS = rss(
    # The cause: lands inside the window, and says "beats", "record" and "up 94%".
    ("Nvidia beats estimates on record data center sales; revenue up 94%", "Reuters", "Tue, 13 Oct 2026 20:06:00 GMT"),
    # The report: published after the move and describes it.
    ("Nvidia stock soars 8% after blowout quarter", "CNBC", "Tue, 13 Oct 2026 20:45:00 GMT"),
    # Commentary from the morning: before the window, but not a trigger.
    ("Why I'm Not Worried About Nvidia's Valuation", "The Motley Fool", "Tue, 13 Oct 2026 14:00:00 GMT"),
    ("Could Nvidia Stock Double Again?", "Yahoo Finance", "Tue, 13 Oct 2026 15:00:00 GMT"),
)

NOW = datetime(2026, 10, 15, 2, 0, tzinfo=timezone.utc)


class EarningsAfterCloseTest(unittest.TestCase):
    def run_case(self, feed=EARNINGS_NEWS):
        with mock.patch.object(prices, "yahoo", side_effect=fake_yahoo), mock.patch.object(news, "fetch", return_value=feed):
            return analyze("NVDA", when="2026-10-14", now=NOW)

    def test_window_is_the_after_hours_spike_not_the_whole_night(self):
        r = self.run_case()
        start, end = r.window.start.astimezone(ET), r.window.end.astimezone(ET)
        self.assertEqual((start.hour, start.minute), (16, 5))
        self.assertLessEqual((end.hour, end.minute), (16, 20))
        self.assertFalse(r.window.is_gap)
        self.assertGreaterEqual(r.window.share, 0.7)

    def test_earnings_headline_inside_window_is_the_top_candidate(self):
        r = self.run_case()
        d = to_dict(r)
        top = d["news"]["candidates"][0]
        self.assertEqual(top["source"], "Reuters")
        self.assertIn("names a concrete event", top["why_ranked"])
        self.assertEqual([s["source"] for s in d["news"]["after_move"]], ["CNBC"])

    def test_commentary_ranks_below_the_cause(self):
        d = to_dict(self.run_case())
        sources = [s["source"] for s in d["news"]["candidates"]]
        self.assertNotIn("The Motley Fool", sources[:1])
        self.assertNotIn("Yahoo Finance", sources[:1])

    def test_market_flat_means_asset_specific(self):
        r = self.run_case()
        self.assertEqual(r.context, "asset_specific")
        self.assertEqual([b["symbol"] for b in r.benchmarks], ["SPY", "QQQ", "SMH"])

    def test_regular_session_change_is_reported(self):
        r = self.run_case()
        self.assertAlmostEqual(r.regular_change, 0.085, delta=0.002)
        self.assertIsNotNone(to_dict(r)["period"]["regular_session_change"])

    def test_broken_news_feed_degrades_to_a_warning(self):
        r = self.run_case(feed=b"<html>rate limited</html")
        self.assertEqual(r.stories, [])
        self.assertTrue(any("news search failed" in w for w in r.warnings))
        self.assertIn("No story published before the move", to_text(r, lang="en"))

    def test_unknown_ticker_is_a_clean_error(self):
        with mock.patch.object(prices, "yahoo", side_effect=FetchError("404")), mock.patch.object(
            prices, "nasdaq_today", side_effect=FetchError("404")
        ):
            with self.assertRaises(FetchError) as ctx:
                analyze("NOTATICKER", now=NOW)
        self.assertIn("valid US stock or ETF ticker", str(ctx.exception))


class LangTest(unittest.TestCase):
    def test_chinese_input_gets_chinese(self):
        self.assertEqual(default_lang("英伟达"), "zh")

    def test_locale_decides_for_latin_input(self):
        with mock.patch.dict(os.environ, {"LC_ALL": "", "LC_MESSAGES": "", "LANG": "zh_CN.UTF-8"}):
            self.assertEqual(default_lang("NVDA"), "zh")
        with mock.patch.dict(os.environ, {"LC_ALL": "", "LC_MESSAGES": "", "LANG": "en_US.UTF-8"}):
            self.assertEqual(default_lang("NVDA"), "en")
        with mock.patch.dict(os.environ, {"LC_ALL": "", "LC_MESSAGES": "", "LANG": ""}):
            self.assertEqual(default_lang("NVDA"), "en")


if __name__ == "__main__":
    unittest.main()
