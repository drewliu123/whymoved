"""Offline adapter contract tests; no provider calls or real credentials."""
import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.request import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from financial_data import NoRedirect, fetch_data, request_params


class Response(io.BytesIO):
    status = 200


class FakeClient:
    def __init__(self, payload=None, error=None, raw=None):
        self.raw = raw if raw is not None else json.dumps(payload).encode()
        self.error = error
        self.requests = []

    def open(self, req, timeout):
        self.requests.append(req)
        if self.error:
            raise self.error
        return Response(self.raw)


class FinancialDataTest(unittest.TestCase):
    def call(self, client, **kwargs):
        with patch.dict(os.environ, {"FINANCIAL_DATASETS_API_KEY": "unit-test-placeholder"}):
            return fetch_data("income", "aapl", opener=client, **kwargs)

    def test_preserves_units_period_filing_id_and_raw_payload(self):
        row = {"ticker": "AAPL", "currency": "USD", "period": "annual",
               "accession_number": "filing-id", "report_period": "2025-09-30", "revenue": 123}
        payload = {"income_statements": [row]}
        result = self.call(FakeClient(payload))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["data"], [row])
        self.assertEqual(result["raw_response"], payload)
        self.assertEqual(len(result["response_sha256"]), 64)
        self.assertNotIn("unit-test-placeholder", json.dumps(result))

    def test_period_filters_reach_api(self):
        client = FakeClient({"income_statements": []})
        result = self.call(client, period="quarterly", limit=8, report_period_lte="2025-12-31")
        self.assertIn("report_period_lte=2025-12-31", client.requests[0].full_url)
        self.assertEqual(result["params"]["ticker"], "AAPL")
        self.assertEqual(result["status"], "no_results")

    def test_no_key_does_not_make_network_request(self):
        client = FakeClient()
        with patch.dict(os.environ, {}, clear=True):
            result = fetch_data("income", "AAPL", opener=client)
        self.assertEqual(result["status"], "not_run")
        self.assertEqual(client.requests, [])

    def test_public_probe_never_sends_configured_key(self):
        client = FakeClient({"income_statements": []})
        self.call(client, public_probe=True)
        self.assertFalse(any(k.lower() == "x-api-key" for k in client.requests[0].headers))

    def test_http_errors_are_not_empty_success_and_do_not_leak_body(self):
        for code, status in [(401, "auth_failed"), (402, "payment_required"),
                             (403, "auth_failed"), (429, "rate_limited"), (500, "error")]:
            with self.subTest(code=code):
                error = HTTPError("https://api.financialdatasets.ai/", code, "Failure", {},
                                  io.BytesIO(b"unit-test-placeholder"))
                client = FakeClient(error=error)
                result = self.call(client)
                self.assertEqual(result["status"], status)
                self.assertIsNone(result["data"])
                self.assertNotIn("unit-test-placeholder", json.dumps(result))
                self.assertEqual(len(client.requests), 1)

    def test_json_and_shape_failures(self):
        clients = [FakeClient(raw=b"<html>unavailable</html>"),
                   FakeClient({"other": []}), FakeClient({"income_statements": {}}),
                   FakeClient({"income_statements": [None]}),
                   FakeClient({"income_statements": [], "error": "bad request"}),
                   FakeClient(raw=b'{"income_statements": [NaN]}'),
                   FakeClient(raw=b'{"income_statements": [{"revenue": 1e999}]}')]
        for client in clients:
            with self.subTest(raw=client.raw):
                result = self.call(client)
                self.assertEqual(result["status"], "schema_drift")
                self.assertIsNone(result["data"])

    def test_next_page_is_explicitly_partial(self):
        client = FakeClient({"income_statements": [{"revenue": 10}],
                             "next_page_url": "https://other.example/next"})
        result = self.call(client)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(len(client.requests), 1)

    def test_timeout_and_connection_errors(self):
        for error, status in [(TimeoutError(), "timeout"),
                              (URLError(TimeoutError()), "timeout"),
                              (URLError("DNS failure"), "unreachable")]:
            self.assertEqual(self.call(FakeClient(error=error))["status"], status)

    def test_snapshot_and_combined_financials_contract(self):
        for operation, payload in [
            ("snapshot", {"snapshot": {"ticker": "AAPL", "price": 10, "currency": "USD"}}),
            ("financials", {"financials": {"income_statements": [{"revenue": 10}],
                                          "balance_sheets": [], "cash_flow_statements": []}}),
            ("balance", {"balance_sheets": [{"total_assets": 10}]}),
            ("cashflow", {"cash_flow_statements": [{"free_cash_flow": 10}]})]:
            with self.subTest(operation=operation):
                result = fetch_data(operation, "AAPL", opener=FakeClient(payload), public_probe=True)
                self.assertEqual(result["status"], "ok")

    def test_invalid_input_fails_before_network(self):
        for params in [dict(ticker="AAPL&secret=x"), dict(limit=0), dict(limit=True),
                       dict(report_period_gte="2025-02-30"),
                       dict(report_period_gte="2025-02-02", report_period_lte="2025-01-01")]:
            with self.subTest(params=params), self.assertRaises(ValueError):
                request_params("income", **dict({"ticker": "AAPL"}, **params))
        with self.assertRaises(ValueError):
            fetch_data("income", "AAPL", timeout=float("nan"))
        with self.assertRaises(ValueError):
            request_params("snapshot", "AAPL", report_period_lte="2025-01-01")

    def test_redirects_do_not_forward_credentials(self):
        request = Request("https://api.financialdatasets.ai/", headers={"X-API-KEY": "placeholder"})
        self.assertIsNone(NoRedirect().redirect_request(request, None, 302, "Found", {},
                                                       "https://other.example/"))


if __name__ == "__main__":
    unittest.main()
