"""SEC retrieval contracts. Synthetic providers, no SEC calls or contact details."""
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sec_data import PINNED_VERSION, envelope, fetch_data, main, parse_as_of, validate_request
from sec_worker import acceptance_utc, at_cutoff, clean, execute, table_data

ACCESSION = "0001045810-26-000075"
IDENTITY = "Synthetic Tester synthetic@example.invalid"


def request(operation="document", **kwargs):
    values = {"document": dict(accession=ACCESSION, section="mda", item=None, attachment=None),
              "statements": dict(accession=ACCESSION, statement="all"),
              "filings": dict(identifier="NVDA", form="10-Q", limit=2, scan_limit=5),
              "doctor": {}}[operation]
    return dict(operation=operation, **dict(values, **kwargs))


class Frame:
    columns = ["concept", "2026-07-26 (Q2)", "2026-07-26 (YTD)", "dimension", "unit", "missing", "zero"]
    def to_dict(self, orient):
        return [{"concept": "us-gaap_Revenues", "2026-07-26 (Q2)": 96221000000,
                 "2026-07-26 (YTD)": 177837000000, "dimension": False, "unit": "usd",
                 "missing": float("nan"), "zero": 0.0}]


class Statement:
    def to_dataframe(self, **kwargs):
        if kwargs != dict(standard=False, presentation=False, include_unit=True, include_point_in_time=True):
            raise AssertionError("must request raw signs, units, period type and non-standardized concepts")
        return Frame()


class Filing:
    accession_no = ACCESSION
    company = "NVIDIA CORP"
    cik = 1045810
    form = "10-Q"
    filing_date = "2026-08-26"
    period_of_report = "2026-07-26"
    url = "https://www.sec.gov/Archives/edgar/data/1045810/" + ACCESSION + "-index.html"
    text_url = "https://www.sec.gov/Archives/edgar/data/1045810/" + ACCESSION + ".txt"
    header = SimpleNamespace(acceptance_datetime=datetime(2026, 8, 26, 16, 30),
                             text="ACCEPTANCE-DATETIME: 2026-08-26 16:30:00")
    document = SimpleNamespace(document="nvda.htm", url="https://www.sec.gov/nvda.htm", content="<html>raw instance</html>")
    def obj(self):
        return self
    def __getitem__(self, item):
        return "Revenue growth.\n" + "Detailed analysis.\n" * 700 + "END OF SECTION"
    def text(self):
        return "FULL PRIMARY DOCUMENT\n" + "data\n" * 2000
    income_statement = Statement()
    balance_sheet = Statement()
    cash_flow_statement = Statement()
    def xbrl(self):
        return SimpleNamespace(facts=SimpleNamespace(get_facts=lambda: [
            {"concept": "us-gaap:Revenues", "value": "96221000000", "numeric_value": 96221000000,
             "context_ref": "quarter", "unit_ref": "usd", "period_start": "2026-04-27", "period_end": "2026-07-26", "dimension": None},
            {"numeric_value": None, "value": "a text block"}]),
            units={"usd": {"measure": "iso4217:USD"}}, reporting_periods=[{"key": "duration_2026-04-27_2026-07-26"}])


class Provider:
    __version__ = PINNED_VERSION
    def __init__(self, filing=None):
        self.filing = filing or Filing()
        self.requests = 0
    def set_identity(self, identity):
        self.identity = identity
    def find(self, accession):
        self.requests += 1
        return self.filing


class SECWorkerTest(unittest.TestCase):
    def run_worker(self, req=None, provider=None):
        with patch.dict(os.environ, {"EDGAR_IDENTITY": IDENTITY}):
            return execute(req or request(), provider or Provider())

    def test_document_is_full_text_with_exact_provenance_and_hash(self):
        result = self.run_worker()
        self.assertEqual(result["status"], "ok")
        self.assertGreater(result["data"]["characters"], 6000)
        self.assertTrue(result["data"]["text"].endswith("END OF SECTION"))
        self.assertEqual(result["data"]["locator"], "Part I, Item 2")
        self.assertEqual(result["provenance"]["acceptance_datetime"], "2026-08-26T20:30:00Z")
        self.assertEqual(result["provenance"]["origin_id"], "sec:" + ACCESSION)
        self.assertEqual(len(result["data"]["sha256"]), 64)
        self.assertNotIn(IDENTITY, json.dumps(result))

    def test_as_of_boundary_and_equivalent_timezones(self):
        for cutoff, expected in [("2026-08-26T20:29:59Z", "no_results"),
                                 ("2026-08-26T20:30:00Z", "ok"),
                                 ("2026-08-26T16:30:00-04:00", "ok")]:
            result = self.run_worker(request(as_of=cutoff))
            self.assertEqual(result["status"], expected)
            if expected == "no_results":
                self.assertIsNone(result["data"])

    def test_missing_accepted_is_not_filing_date_at_midnight(self):
        filing = Filing()
        filing.header = SimpleNamespace(acceptance_datetime=None, text="no acceptance header")
        result = self.run_worker(request(as_of="2026-09-01T00:00:00Z"), Provider(filing))
        self.assertEqual(result["status"], "partial")
        self.assertIsNone(result["data"])
        self.assertEqual(result["reason"], "acceptance_datetime_unknown")

    def test_eastern_ambiguous_time_not_invented(self):
        self.assertIsNone(acceptance_utc(datetime(2026, 11, 1, 1, 30)))
        self.assertIsNone(acceptance_utc(datetime(2026, 3, 8, 2, 30)))
        self.assertEqual(acceptance_utc(datetime(2026, 1, 2, 16)), "2026-01-02T21:00:00Z")

    def test_missing_identity_no_provider_access(self):
        provider = Provider()
        with patch.dict(os.environ, {}, clear=True):
            result = execute(request(), provider)
        self.assertEqual(result["status"], "not_run")
        self.assertEqual(provider.requests, 0)

    def test_statements_keep_raw_quarter_ytd_numeric_contexts_and_units(self):
        result = self.run_worker(request("statements"))
        self.assertEqual(result["status"], "ok")
        data = result["data"]
        row = data["statements"]["income"]["rows"][0]
        self.assertEqual(row["2026-07-26 (Q2)"], 96221000000)
        self.assertEqual(row["2026-07-26 (YTD)"], 177837000000)
        self.assertFalse(row["dimension"])
        self.assertIsNone(row["missing"])
        self.assertEqual(row["zero"], 0)
        self.assertEqual(data["numeric_facts"][0]["context_ref"], "quarter")
        self.assertEqual(len(data["numeric_facts"]), 1)
        self.assertEqual(data["derivations"], [])
        json.dumps(result, allow_nan=False)

    def test_partial_statement_not_whole_success(self):
        filing = Filing()
        filing.balance_sheet = None
        result = self.run_worker(request("statements"), Provider(filing))
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["data"]["errors"][0]["statement"], "balance")

    def test_truncated_text_flagged_partial(self):
        filing = Filing()
        filing.text = lambda: "partial ... (truncated)"
        result = self.run_worker(request(section="full_text"), Provider(filing))
        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["completeness"]["truncated"])

    def test_version_drift_and_failure_do_not_leak_identity(self):
        provider = Provider()
        provider.__version__ = "999.0"
        self.assertEqual(self.run_worker(provider=provider)["status"], "schema_drift")
        provider = Provider()
        provider.find = Mock(side_effect=RuntimeError(IDENTITY))
        result = self.run_worker(provider=provider)
        self.assertEqual(result["status"], "error")
        self.assertNotIn(IDENTITY, json.dumps(result))

    def test_filings_filter_before_limit(self):
        newer, older = Filing(), Filing()
        older.accession_no = "0001045810-26-000001"
        older.header = SimpleNamespace(acceptance_datetime=datetime(2026, 5, 1, 16), text="")
        company = SimpleNamespace(name="NVIDIA CORP", cik=1045810, get_filings=lambda **kw: [newer, older])
        provider = Provider()
        provider.Company = lambda ident: company
        result = self.run_worker(request("filings", limit=1, as_of="2026-06-01T00:00:00Z"), provider)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"]["filings"][0]["accession_number"], older.accession_no)
        self.assertEqual(result["data"]["excluded_after_cutoff"], [ACCESSION])

    def test_historical_scan_bound_is_partial_even_when_limit_filled(self):
        first, second = Filing(), Filing()
        second.accession_no = "0001045810-26-000076"
        second.header = SimpleNamespace(acceptance_datetime=datetime(2026, 8, 26, 17), text="")
        company = SimpleNamespace(name="NVIDIA CORP", cik=1045810, get_filings=lambda **kw: [first, second])
        provider = Provider()
        provider.Company = lambda ident: company
        result = self.run_worker(request("filings", limit=1, scan_limit=1, as_of="2026-09-01T00:00:00Z"), provider)
        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["completeness"]["truncated"])

    def test_http_rejection_statuses_are_specific(self):
        for code, expected in [(429, "rate_limited"), (403, "auth_failed"), (500, "error")]:
            exc = RuntimeError(IDENTITY)
            exc.response = SimpleNamespace(status_code=code)
            provider = Provider()
            provider.find = Mock(side_effect=exc)
            result = self.run_worker(provider=provider)
            self.assertEqual(result["status"], expected)
            self.assertIsNone(result["data"])
            self.assertNotIn(IDENTITY, json.dumps(result))

    def test_attachment_and_missing_section_are_not_silently_substituted(self):
        filing = Filing()
        filing.attachments = {"ex991.htm": SimpleNamespace(document="ex991.htm", document_type="EX-99.1",
                                                           url="https://www.sec.gov/ex991.htm", text=lambda: "Earnings release.")}
        result = self.run_worker(request(section="full_text", attachment="ex991.htm"), Provider(filing))
        self.assertEqual(result["data"]["text"], "Earnings release.")
        self.assertEqual(result["data"]["locator"], "attachment:ex991.htm")
        result = self.run_worker(request(section="business"))
        self.assertEqual(result["status"], "no_results")
        self.assertIsNone(result["data"])

    def test_clean_retains_decimal_precision_zero_and_sign(self):
        from decimal import Decimal
        value = clean({"nan": math.nan, "zero": 0, "negative": -4.434e9, "decimal": Decimal("2.4700")})
        self.assertIsNone(value["nan"])
        self.assertEqual(value["zero"], 0)
        self.assertEqual(value["negative"], -4434000000)
        self.assertEqual(value["decimal"], "2.4700")


class SECDispatcherTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        (self.home / "data").mkdir()
        (self.home / "data/sec-runtime.json").write_text(json.dumps({"schema_version": 1, "python": sys.executable}))

    def dispatch(self, runner, req=None):
        with patch.dict(os.environ, {"EDGAR_IDENTITY": IDENTITY}):
            return fetch_data(req or request(), home=self.home, runner=runner)

    def test_unconfigured_identity_does_not_launch_worker(self):
        runner = Mock()
        with patch.dict(os.environ, {}, clear=True):
            result = fetch_data(request(), home=self.home, runner=runner)
        self.assertEqual(result["status"], "not_run")
        runner.assert_not_called()

    def test_protocol_nonfinite_logs_bad_exit_and_empty_rejected(self):
        for stdout, code in [("not-json", 0), ("", 1),
                             ('{"provider":"edgartools","operation":"document","status":"ok","value":NaN}', 0),
                             (json.dumps(envelope(request())), 1)]:
            runner = Mock(return_value=SimpleNamespace(stdout=stdout, stderr=IDENTITY, returncode=code))
            result = self.dispatch(runner)
            self.assertEqual(result["status"], "schema_drift")
            self.assertNotIn(IDENTITY, json.dumps(result))

    def test_timeout_and_no_shell(self):
        runner = Mock(side_effect=subprocess.TimeoutExpired("worker", 1))
        self.assertEqual(self.dispatch(runner)["status"], "timeout")
        self.assertIsInstance(runner.call_args[0][0], list)
        self.assertNotIn("shell", runner.call_args[1])

    def test_valid_protocol_preserved(self):
        payload = dict(envelope(request()), status="ok", data={"text": "actual"})
        runner = Mock(return_value=SimpleNamespace(stdout=json.dumps(payload), returncode=0))
        self.assertEqual(self.dispatch(runner), payload)

    def test_invalid_inputs_rejected_before_worker(self):
        bad = [request(accession="https://evil.invalid/"), request(as_of="2026-08-26"),
               request(as_of="2026-08-26T00:00:00"), request(item="Item 7", section="mda"),
               request(attachment="../../secret"), request("filings", limit=True),
               request("filings", scan_limit=1), request("statements", statement="ttm")]
        runner = Mock()
        for req in bad:
            with self.assertRaises(ValueError):
                self.dispatch(runner, req)
        runner.assert_not_called()

    def test_existing_output_refused_before_retrieval(self):
        out = self.home / "existing.json"
        out.write_text("original")
        with patch("sec_data.fetch_data") as fetch, patch("sys.stderr", io.StringIO()):
            with self.assertRaises(SystemExit):
                main(["doctor", "--out", str(out)])
        fetch.assert_not_called()
        self.assertEqual(out.read_text(), "original")


if __name__ == "__main__":
    unittest.main()
