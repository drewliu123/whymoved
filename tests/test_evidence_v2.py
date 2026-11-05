"""Strict v2 evidence tests and explicit legacy API regressions."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from check_claims import check_claim, validate_ledger
from test_sources import AS_OF, candidate, document


def claim(cid="C1", ctype="fact", sources=None, **changes):
    result = {"id": cid, "text": "Reported result", "type": ctype, "as_of": AS_OF,
              "sources": [{"source_id": "S1"}] if sources is None else sources}
    result.update(changes)
    return result


def ledger(*claims):
    return {"schema_version": 2, "as_of": AS_OF, "claims": list(claims) or [claim()]}


class StrictEvidenceTest(unittest.TestCase):
    def test_official_fact_and_independent_fact_families(self):
        self.assertTrue(validate_ledger(ledger(), document(candidate(tier="T0")))["passed"])
        refs = [{"source_id": "S1"}, {"source_id": "S2"}]
        doc = document(candidate(), candidate("S2", publisher="Other"))
        self.assertTrue(validate_ledger(ledger(claim(sources=refs)), doc)["passed"])
        for family in ("family-S1", None):
            doc["candidates"][1]["origin_id"] = family
            result = validate_ledger(ledger(claim(sources=refs)), doc)
            self.assertFalse(result["passed"])
            self.assertIn("R2", " ".join(result["failures"]["C1"]))

    def test_reprints_one_family_even_if_publishers_differ(self):
        doc = document(candidate(origin_id="Reuters-wire"), candidate("S2", publisher="Different newspaper", origin_id="Reuters-wire"))
        result = validate_ledger(ledger(claim(sources=[{"source_id": "S1"}, {"source_id": "S2"}])), doc)
        self.assertFalse(result["passed"])

    def test_same_document_fragments_cannot_fake_independent_families(self):
        refs = [{"source_id": "S1"}, {"source_id": "S2"}]
        doc = document(candidate(url="https://example.com/a"), candidate("S2", url="https://example.com/a",
                       origin_id="alleged-other-family", quote="Different financial number", locator="table 2"))
        self.assertFalse(validate_ledger(ledger(claim(sources=refs)), doc)["passed"])

    def test_canonical_override_cannot_split_actual_document_origin(self):
        refs = [{"source_id": "S1"}, {"source_id": "S2"}]
        a = candidate(url="https://example.com/report?utm_source=a", canonical_url="https://example.com/alias-a")
        b = candidate("S2", url="https://example.com/report?utm_source=b", canonical_url="https://example.com/alias-b")
        self.assertFalse(validate_ledger(ledger(claim(sources=refs)), document(a, b))["passed"])
        # Alias bridges union transitively, independent of reference order.
        c = candidate("S3", url="https://example.com/alias-b", canonical_url="https://example.com/alias-c")
        for sources in ((a, b, c), (c, b, a)):
            refs = [{"source_id": source["id"]} for source in sources]
            self.assertFalse(validate_ledger(ledger(claim(sources=refs)), document(*sources))["passed"])

    def test_optional_basis_is_typed_on_every_strict_claim(self):
        for basis in ([{}], [None], [1], "C2", {}):
            self.assertFalse(validate_ledger(ledger(claim(basis=basis)), document(candidate(tier="T0")))["passed"])
        self.assertTrue(validate_ledger(ledger(claim(basis=[])), document(candidate(tier="T0")))["passed"])
        inline = {"tier": "T0", "publisher": "BLS", "url": "https://example.com/a", "published_at": "unknown"}
        self.assertTrue(validate_ledger({"claims": [claim(sources=[inline], basis=[{}])]})["passed"])

    def test_t3_forecast_cannot_be_underlying_fact(self):
        source = candidate(tier="T3", evidence_kind="opinion")
        self.assertFalse(validate_ledger(ledger(), document(source))["passed"])
        source["attribution"] = {"speaker": "Institution analyst", "original": True,
                                 "statement_kind": "attributed_statement"}
        attributed = claim(text="Institution analyst stated this forecast", attributed_to="Institution analyst",
                           fact_scope="attributed_statement")
        self.assertTrue(validate_ledger(ledger(attributed), document(source))["passed"])
        source["attribution"]["original"] = False
        self.assertFalse(validate_ledger(ledger(attributed), document(source))["passed"])

    def test_t4_view_only_and_support_semantics_required(self):
        source = candidate(tier="T4", supports=["view"], evidence_kind="opinion")
        self.assertTrue(validate_ledger(ledger(claim(ctype="view")), document(source))["passed"])
        self.assertFalse(validate_ledger(ledger(), document(source))["passed"])
        source = candidate(tier="T0", supports=["view"])
        self.assertFalse(validate_ledger(ledger(), document(source))["passed"])

    def test_selected_access_quote_locator_and_reference_resolution(self):
        for change in ({"access_status": "snippet"}, {"quote": ""}, {"locator": ""},
                       {"selection": {"selected": False, "reason": "not relevant", "relevance": "context",
                                      "purpose": "review", "priority": "background"}}):
            self.assertFalse(validate_ledger(ledger(), document(candidate(tier="T0", **change)))["passed"])
        self.assertFalse(validate_ledger(ledger(claim(sources=[{"source_id": "missing"}])), document())["passed"])
        injected = claim(sources=[{"source_id": "S1", "tier": "T0", "quote": "forged"}])
        self.assertFalse(validate_ledger(ledger(injected), document(candidate(tier="T0")))["passed"])

    def test_price_requires_market_kind_metadata_and_matching_indicative_type(self):
        price_claim = claim(ctype="price", price_kind="indicative")
        source = candidate(tier="T0", supports=["price"])
        self.assertFalse(validate_ledger(ledger(price_claim), document(source))["passed"])
        source.update(evidence_kind="market_quote", market_quote={"quoted_at": AS_OF, "instrument": "event-id",
                      "outcome": "Yes", "direction": "long", "value": 0.6, "unit": "probability", "quote_type": "indicative",
                      "token_id": "token1", "snapshot_id": "snapshot1"})
        self.assertTrue(validate_ledger(ledger(price_claim), document(source))["passed"])
        self.assertFalse(validate_ledger(ledger(claim(ctype="price", price_kind="executable")), document(source))["passed"])
        for field in ("quoted_at", "outcome", "direction", "instrument", "unit", "quote_type", "value"):
            broken = copy.deepcopy(source)
            del broken["market_quote"][field]
            self.assertFalse(validate_ledger(ledger(price_claim), document(broken))["passed"], field)
        source["market_quote"]["quoted_at"] = "2026-10-31T13:00:00Z"
        self.assertFalse(validate_ledger(ledger(price_claim), document(source))["passed"])

    def test_executable_quote_needs_real_bid_ask(self):
        source = candidate(tier="T0", supports=["price"], evidence_kind="market_quote",
                           market_quote={"quoted_at": AS_OF, "instrument": "ABC", "outcome": "ABC share",
                                         "direction": "buy", "value": 50, "unit": "USD", "quote_type": "executable"})
        c = claim(ctype="price", price_kind="executable")
        self.assertFalse(validate_ledger(ledger(c), document(source))["passed"])
        source["market_quote"].update(bid=49, ask=50)
        self.assertTrue(validate_ledger(ledger(c), document(source))["passed"])
        source["market_quote"]["bid"] = 51
        self.assertFalse(validate_ledger(ledger(c), document(source))["passed"])

    def test_price_and_consensus_reject_ineligible_piggyback_sources(self):
        price = candidate(tier="T0", supports=["price"], evidence_kind="market_quote",
                          market_quote={"quoted_at": AS_OF, "instrument": "ABC", "outcome": "ABC share",
                                        "direction": "buy", "value": 50, "unit": "USD", "quote_type": "indicative"})
        refs = [{"source_id": "S1"}, {"source_id": "S2"}]
        piggyback = candidate("S2", tier="T2", supports=["price"], evidence_kind="market_quote")
        c = claim(ctype="price", sources=refs, price_kind="indicative")
        result = validate_ledger(ledger(c), document(price, piggyback))
        self.assertFalse(result["passed"])
        self.assertIn("every referenced price source", str(result["failures"]))
        survey = candidate(tier="T1", supports=["consensus"], evidence_kind="survey",
                           survey={"population": "surveyed economists", "sample_size": 30, "method": "poll",
                                   "fieldwork_start": "2026-10-25", "fieldwork_end": "2026-10-30"})
        for tier in ("T0", "T3", "T4"):
            piggyback = candidate("S2", tier=tier, supports=["consensus"], evidence_kind="survey")
            c = claim(ctype="consensus", sources=refs, consensus_scope="surveyed economists")
            result = validate_ledger(ledger(c), document(survey, piggyback))
            self.assertFalse(result["passed"], tier)
            self.assertIn("every referenced consensus source", str(result["failures"]))

    def test_market_quote_huge_numbers_fail_safely(self):
        source = candidate(tier="T0", supports=["price"], evidence_kind="market_quote",
                           market_quote={"quoted_at": AS_OF, "instrument": "ABC", "outcome": "ABC share",
                                         "direction": "buy", "value": 50, "unit": "USD", "quote_type": "executable",
                                         "bid": 49, "ask": 50})
        c = claim(ctype="price", price_kind="executable")
        for field in ("value", "bid", "ask"):
            broken = copy.deepcopy(source)
            broken["market_quote"][field] = 10 ** 1000
            result = validate_ledger(ledger(c), document(broken))
            self.assertFalse(result["passed"], field)
            self.assertIn("R3", str(result["failures"]))

    def test_consensus_is_scoped_survey_not_publisher_name(self):
        c = claim(ctype="consensus", consensus_scope="30 surveyed economists", text="多数受访经济学家预期不变")
        source = candidate(tier="T1", publisher="Reuters", supports=["consensus"])
        self.assertFalse(validate_ledger(ledger(c), document(source))["passed"])
        source.update(evidence_kind="survey", survey={"population": "30 surveyed economists", "sample_size": 30,
                      "method": "Reuters poll", "fieldwork_start": "2026-10-25", "fieldwork_end": "2026-10-30"})
        self.assertTrue(validate_ledger(ledger(c), document(source))["passed"])
        universal = dict(c, consensus_scope="whole market")
        self.assertFalse(validate_ledger(ledger(universal), document(source))["passed"])
        source["survey"]["fieldwork_end"] = "2026-10-31"
        self.assertFalse(validate_ledger(ledger(c), document(source))["passed"])
        source["survey"]["fieldwork_end"] = "2026-10-31T11:00:00Z"
        self.assertTrue(validate_ledger(ledger(c), document(source))["passed"])

    def test_unknown_invalid_precision_and_historical_availability(self):
        source = candidate(tier="T0", published_at="unknown")
        self.assertTrue(validate_ledger(ledger(), document(source))["passed"])
        for value in ("2026-02-30", "2026-10-30 nonsense", "2026-10-30T03:00:00"):
            self.assertFalse(validate_ledger(ledger(), document(dict(source, published_at=value)))["passed"])
        source["retrieved_at"] = "2026-11-01T00:00:00Z"
        doc = document(source, historical=True)
        self.assertFalse(validate_ledger(ledger(), doc)["passed"])
        source["availability"] = {"available_at": "2026-10-30T18:00:00Z", "evidence_url": "https://archive.org/snapshot",
                                  "quote": "Archived content", "locator": "capture metadata"}
        self.assertTrue(validate_ledger(ledger(), doc)["passed"])
        source["availability"]["available_at"] = "2026-10-30"
        self.assertFalse(validate_ledger(ledger(), doc)["passed"])

    def test_date_precision_same_day_later_retrieval_cannot_bypass(self):
        source = candidate(tier="T0", published_at="2026-10-31", retrieved_at="2026-11-01T00:00:00Z")
        result = validate_ledger(ledger(), document(source, historical=True))
        self.assertFalse(result["passed"])
        self.assertIn("date precision", " ".join(result["failures"]["C1"]))
        source["published_at"] = "2026-10-31T12:01:00Z"
        self.assertFalse(validate_ledger(ledger(), document(source))["passed"])

    def test_post_cutoff_excluded_candidate_does_not_invalidate_other_evidence(self):
        excluded = candidate("S2", tier="T0", published_at="2026-11-01", retrieved_at="2026-11-02T00:00:00Z")
        excluded["selection"].update(selected=False, reason="Published after historical cutoff")
        doc = document(candidate(tier="T0"), excluded, historical=True)
        self.assertTrue(validate_ledger(ledger(), doc)["passed"])
        result = validate_ledger(ledger(claim(sources=[{"source_id": "S2"}])), doc)
        self.assertFalse(result["passed"])
        self.assertIn("not selected", str(result["failures"]["C1"]))
        self.assertIn("published after", str(result["failures"]["C1"]))
        excluded["selection"]["selected"] = True
        self.assertFalse(validate_ledger(ledger(claim(sources=[{"source_id": "S2"}])), doc)["passed"])

    def test_multi_node_cycle_all_members_and_duplicate_ids_rejected(self):
        claims = [claim("A", "inference", [], basis=["B"]), claim("B", "inference", [], basis=["C"]),
                  claim("C", "inference", [], basis=["A"])]
        result = validate_ledger(ledger(*claims), document())
        self.assertEqual(set(result["failures"]), {"A", "B", "C"})
        self.assertTrue(all(any("cycle" in error for error in errors) for errors in result["failures"].values()))
        result = validate_ledger(ledger(claim(), claim(text="other")), document(candidate(tier="T0")))
        self.assertIn("duplicate", str(result["failures"]))
        source_doc = document(candidate(tier="T0"), candidate(tier="T0"))
        self.assertFalse(validate_ledger(ledger(), source_doc)["passed"])

    def test_overlapping_cycles_mark_every_member(self):
        claims = [claim("A", "inference", [], basis=["B", "C"]),
                  claim("B", "inference", [], basis=["A"]),
                  claim("C", "inference", [], basis=["B"])]
        result = validate_ledger(ledger(*claims), document())
        self.assertEqual(set(result["failures"]), {"A", "B", "C"})
        self.assertTrue(all(any("cycle" in error for error in errors) for errors in result["failures"].values()))

    def test_history_unknown_needs_proof_even_when_retrieved_before_cutoff(self):
        source = candidate(tier="T0", published_at="unknown", retrieved_at="2026-10-31T11:00:00Z")
        self.assertFalse(validate_ledger(ledger(), document(source, historical=True))["passed"])
        self.assertTrue(validate_ledger(ledger(), document(source, historical=False))["passed"])

    def test_t3_cannot_piggyback_on_valid_t0_fact(self):
        refs = [{"source_id": "S1"}, {"source_id": "S2"}]
        doc = document(candidate(tier="T0"), candidate("S2", tier="T3"))
        self.assertFalse(validate_ledger(ledger(claim(sources=refs)), doc)["passed"])

    def test_inference_cannot_use_future_basis_and_self_cycle_rejected(self):
        future = claim("C1")
        early = claim("C2", "inference", [], basis=["C1"], as_of="2026-10-30T12:00:00Z")
        self.assertFalse(validate_ledger(ledger(future, early), document(candidate(tier="T0")))["passed"])
        self_cycle = claim("C1", "inference", [], basis=["C1"])
        self.assertIn("cycle", str(validate_ledger(ledger(self_cycle), document())["failures"]))

    def test_fact_cannot_piggyback_on_market_quote_metadata(self):
        source = candidate(tier="T0", evidence_kind="market_quote", supports=["fact"])
        self.assertFalse(validate_ledger(ledger(), document(source))["passed"])

    def test_acyclic_inference_and_missing_basis(self):
        claims = [claim(), claim("C2", "inference", [], basis=["C1"]), claim("C3", "inference", [], basis=["C1", "C2"])]
        self.assertTrue(validate_ledger(ledger(*claims), document(candidate(tier="T0")))["passed"])
        claims[2]["basis"] = ["missing"]
        self.assertFalse(validate_ledger(ledger(*claims), document(candidate(tier="T0")))["passed"])

    def test_bad_inputs_fail_without_exception(self):
        for malformed in (None, [], {"claims": None}, {"schema_version": 99, "claims": []},
                          ledger({"id": [], "type": [], "as_of": {}, "sources": [None]}),
                          ledger(claim(ctype="inference", sources=[], basis=[{}]))):
            with self.subTest(malformed=malformed):
                self.assertFalse(validate_ledger(malformed, document())["passed"])
        for changes in ({"supports": [[]]}, {"tier": []}, {"evidence_kind": {}}, {"selection": []}):
            self.assertFalse(validate_ledger(ledger(), document(candidate(**changes)))["passed"])
        self.assertFalse(validate_ledger(dict(ledger(), claims=[]), document())["passed"])

    def test_version_cannot_silently_downgrade(self):
        # A valid legacy inline source cannot bypass strict resolution.
        inline = {"tier": "T0", "publisher": "BLS", "url": "https://example.com/a", "published_at": "unknown"}
        c = claim(sources=[inline])
        self.assertFalse(validate_ledger(ledger(c), document())["passed"])
        self.assertTrue(validate_ledger({"claims": [c]})["passed"])
        self.assertEqual(check_claim(c, {"C1"}), [])

    def test_cli_sources_resolution_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lp, sp = root / "claims.json", root / "sources.json"
            lp.write_text(json.dumps(ledger()), encoding="utf-8")
            sp.write_text(json.dumps(document(candidate(tier="T0"))), encoding="utf-8")
            env = {**os.environ, "HOME": temp, "TOUYAN_HOME": temp, "PYTHONDONTWRITEBYTECODE": "1"}
            cmd = [sys.executable, str(SCRIPTS / "check_claims.py"), str(lp), "--sources", str(sp), "--json"]
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["passed"])
            sp.write_text('{}', encoding="utf-8")
            self.assertEqual(subprocess.run(cmd, env=env, capture_output=True).returncode, 1)
            sp.write_text('{broken', encoding="utf-8")
            self.assertEqual(subprocess.run(cmd, env=env, capture_output=True).returncode, 2)


if __name__ == "__main__":
    unittest.main()
