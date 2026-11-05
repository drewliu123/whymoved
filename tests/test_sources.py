"""Offline source import/selection regression tests; no network or credentials."""
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
from sources import canonicalize_url, import_last30days, select_sources, validate_sources

AS_OF = "2026-10-31T12:00:00Z"


def candidate(cid="S1", **changes):
    source = {"id": cid, "url": "https://example.com/" + cid, "publisher": "Publisher",
              "tier": "T2", "published_at": "2026-10-30", "retrieved_at": AS_OF,
              "quote": "Verbatim source statement", "locator": "paragraph 2",
              "origin_id": "family-" + cid, "origin_basis": "Original reporting identified in byline",
              "supports": ["fact"], "evidence_kind": "document", "access_status": "ok",
              "selection": {"selected": True, "reason": "Direct evidence", "relevance": "direct",
                            "purpose": "Verify reported fact", "priority": "useful"}}
    source.update(changes)
    return source


def document(*candidates, **changes):
    doc = {"schema_version": 2, "as_of": AS_OF, "historical": False,
           "candidates": list(candidates) or [candidate()], "source_status": {"web": {"status": "ok"}}}
    doc.update(changes)
    return doc


def raw_report():
    # Shape mirrors 3.30.0 scripts/lib/schema.py Report/SourceItem/Candidate.
    item = {"item_id": "r1", "source": "reddit", "title": "Original post", "body": "Low heat useful post",
            "url": "https://reddit.com/r/test/comments/1", "author": "alice", "published_at": "2026-10-30",
            "engagement": {"score": 2}, "snippet": "Collected excerpt"}
    unranked = {"item_id": "r2", "source": "reddit", "title": "Contrary post", "body": "Contrary view",
                "url": "https://reddit.com/r/test/comments/2", "published_at": None}
    row = {"candidate_id": "C1", "item_id": "r1", "source": "reddit", "title": "Engine title",
           "url": item["url"], "snippet": "Engine snippet", "native_ranks": {"q1": 4},
           "final_score": 99, "cluster_id": "cl1", "source_items": [item]}
    return {"topic": "test", "range_from": "2026-10-01", "range_to": "2026-10-31", "generated_at": AS_OF,
            "ranked_candidates": [row], "items_by_source": {"reddit": [item, unranked]},
            "clusters": [{"cluster_id": "cl1", "candidate_ids": ["C1"]}],
            "source_status": {"reddit": {"state": "partial", "attempted": True, "items_returned": 2,
                                          "detail": "One lane timed out"},
                              "x": {"state": "skipped-unconfigured", "attempted": False},
                              "web": {"state": "no-results", "attempted": True}},
            "errors_by_source": {"reddit": "lane timeout"}}


class SourcesTest(unittest.TestCase):
    def test_semantic_priority_beats_engagement_and_raw_rank(self):
        low = candidate("low", engagement={"likes": 1}, provenance={"engine_rank": 20})
        low["selection"]["priority"] = "decisive"
        hot = candidate("hot", engagement={"likes": 1000000}, provenance={"engine_rank": 1})
        hot["selection"].update(selected=False, relevance="irrelevant", reason="Different event")
        result = select_sources(document(hot, low))
        self.assertEqual(result["selection_summary"]["selected"], ["low"])
        self.assertEqual(result["candidates"][0]["id"], "low")

    def test_rank_is_only_semantic_tie_break_and_input_is_unchanged(self):
        doc = document(candidate("later", provenance={"engine_rank": 5}), candidate("earlier", provenance={"engine_rank": 2}))
        before = copy.deepcopy(doc)
        result = select_sources(doc)
        self.assertEqual(result["selection_summary"]["selected"], ["earlier", "later"])
        self.assertEqual(doc, before)
        self.assertNotIn("engagement", result["candidates"][0])

    def test_normalized_url_dedup_and_confirmed_retransmission(self):
        first = candidate("S1", url="https://example.com/story?utm_source=x#top", origin_id="wire")
        same = candidate("S2", url="https://EXAMPLE.com:443/story", origin_id="wire")
        retransmission = {"confirmed": True, "statement_id": "earnings-quote", "basis": "Explicit wire attribution"}
        first["retransmission"] = retransmission
        reprint = candidate("S3", url="https://another.com/reprint", origin_id="wire", retransmission=retransmission)
        contrary = candidate("S4", origin_id="wire", quote="Different analysis")
        result = select_sources(document(first, same, reprint, contrary))
        self.assertEqual(result["selection_summary"]["selected"], ["S1", "S4"])
        self.assertEqual(result["candidates"][1]["selection"]["duplicate_of"], "S1")
        self.assertEqual(select_sources(result), result)

    def test_distinct_fragments_same_url_survive_but_exact_fragment_deduplicates(self):
        a = candidate("a", url="https://example.com/earnings", quote="Revenue rose", locator="table 1", origin_id="report")
        b = candidate("b", url="https://example.com/earnings", quote="Margins fell", locator="table 2", origin_id="report")
        duplicate = candidate("c", url="https://example.com/earnings?utm_source=x", quote=" Revenue  rose ", locator="table 1", origin_id="report")
        result = select_sources(document(a, b, duplicate))
        self.assertEqual(result["selection_summary"]["selected"], ["a", "b"])
        self.assertEqual(result["candidates"][2]["selection"]["duplicate_of"], "a")

    def test_same_topic_or_unknown_origin_never_deduplicated(self):
        a, b = candidate("a", origin_id=None), candidate("b", origin_id=None)
        for source in (a, b):
            source["cluster_id"] = "same-topic"
            source["retransmission"] = {"confirmed": True, "statement_id": "same", "basis": "Unresolved origin"}
        self.assertEqual(select_sources(document(a, b))["selection_summary"]["selected"], ["a", "b"])

    def test_unknown_dates_allowed_but_invalid_dates_and_naive_times_fail(self):
        self.assertEqual(validate_sources(document(candidate(published_at="unknown"))), [])
        for value in ("2026-02-30", "garbage", "2026-10-30T12:00:00", 123):
            self.assertTrue(validate_sources(document(candidate(published_at=value))), value)
        self.assertTrue(validate_sources(document(candidate(retrieved_at="2026-10-30"))))
        self.assertTrue(validate_sources(document(as_of="2026-10-31T13:00:00+01:00")))

    def test_post_cutoff_candidates_retained_only_when_explicitly_unselected(self):
        for published in ("2026-11-01", "2026-10-31T12:01:00Z"):
            source = candidate(published_at=published, retrieved_at="2026-11-02T00:00:00Z")
            self.assertTrue(validate_sources(document(source)))
            source["selection"].update(selected=False, reason="Published after historical cutoff")
            doc = document(source, historical=True)
            self.assertEqual(validate_sources(doc), [])
            selected = select_sources(doc)
            self.assertEqual(len(selected["candidates"]), 1)
            self.assertEqual(selected["selection_summary"]["selected"], [])
            self.assertEqual(selected["candidates"][0]["published_at"], published)
            source["selection"]["selected"] = None
            self.assertTrue(validate_sources(doc))

    def test_malicious_urls_rejected(self):
        for url in ("javascript:alert(1)", "file:///etc/passwd", "https://user:token@example.com/a",
                    "https://localhost/a", "http://127.0.0.1/", "http://169.254.169.254/a", "http://[::1]/",
                    "http://127.1/", "http://2130706433/", "http://0x7f.0x0.0x0.0x1/",
                    "https://example.com/\nsecret", "https://example.com/a%0d%0aX", "https://example.com\\@evil.com/"):
            with self.subTest(url=url):
                self.assertTrue(validate_sources(document(candidate(url=url))))
        self.assertEqual(canonicalize_url("https://Example.com:443/a?b=2&utm_source=x&a=1#top"),
                         "https://example.com/a?a=1&b=2")

    def test_malformed_types_return_errors_not_tracebacks(self):
        for field in ("tier", "supports", "evidence_kind", "access_status", "published_at", "origin_id"):
            self.assertTrue(validate_sources(document(candidate(**{field: {"malformed": []}}))), field)
        bad = candidate()
        bad["selection"]["relevance"] = []
        self.assertTrue(validate_sources(document(bad)))
        self.assertTrue(validate_sources(document(source_status={"web": {"status": []}})))
        self.assertTrue(validate_sources([]))

    def test_full_raw_pool_rank_clusters_errors_retained(self):
        raw = raw_report()
        imported = import_last30days(raw, "/offline/raw.json")
        self.assertEqual(validate_sources(imported), [])
        self.assertEqual(len(imported["candidates"]), 2)
        source, extra = imported["candidates"]
        self.assertEqual(source["quote"], "Low heat useful post")
        self.assertEqual(source["tier"], "T4")
        self.assertIsNone(source["origin_id"])
        self.assertEqual(source["provenance"]["engine_rank"], 1)
        self.assertEqual(source["provenance"]["raw_candidate"]["native_ranks"], {"q1": 4})
        self.assertFalse(source["selection"]["selected"])
        self.assertEqual(extra["published_at"], "unknown")
        self.assertTrue(extra["provenance"]["unranked"])
        self.assertNotIn("engagement", extra)
        self.assertEqual(imported["retrieval"]["raw_report"], raw)
        self.assertEqual(len(imported["retrieval"]["raw_sha256"]), 64)
        self.assertEqual(imported["source_status"]["reddit"]["status"], "partial")
        self.assertEqual(imported["source_status"]["x"]["status"], "not_run")
        self.assertEqual(imported["source_status"]["web"]["status"], "no_results")
        self.assertEqual(select_sources(imported)["selection_summary"]["selected"], [])

    def test_agent_14_summary_never_original_quote(self):
        raw = {"schema_version": "1.4", "query": "test", "generated_at": AS_OF, "clusters": [],
               "source_status": {"web": "ok"},
               "results": [{"candidate_id": "C1", "source": "web", "url": "https://example.com/a",
                            "title": "A headline", "summary": "Model summary", "relevance_score": 0.99}]}
        result = import_last30days(raw)
        source = result["candidates"][0]
        self.assertEqual(source["quote"], "")
        self.assertEqual(source["locator"], "")
        self.assertEqual(source["access_status"], "snippet")
        self.assertFalse(source["selection"]["selected"])
        self.assertEqual(source["supports"], [])

    def test_unknown_raw_shape_fails_instead_of_empty_success(self):
        for raw in ({}, {"results": []}, {"schema_version": "99", "results": []},
                    dict(raw_report(), source_status={"reddit": "new-state"}),
                    dict(raw_report(), ranked_candidates=[{"url": "https://example.com/a"}])):
            with self.assertRaisesRegex(ValueError, "compatibility error"):
                import_last30days(raw)

    def test_raw_malformed_source_and_item_ids_fail_compatibly(self):
        for field, value in (("source", []), ("source", {}), ("item_id", []), ("item_id", {})):
            raw = raw_report()
            raw["ranked_candidates"][0][field] = value
            with self.assertRaisesRegex(ValueError, "compatibility error"):
                import_last30days(raw)
        raw = raw_report()
        raw["ranked_candidates"][0]["source_items"][0]["source"] = ["reddit"]
        with self.assertRaisesRegex(ValueError, "compatibility error"):
            import_last30days(raw)

    def test_cli_import_select_validate_in_isolated_home(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, out, selected = root / "raw.json", root / "sources.json", root / "selected.json"
            raw.write_text(json.dumps(raw_report()), encoding="utf-8")
            env = {**os.environ, "HOME": temp, "TOUYAN_HOME": temp, "PYTHONDONTWRITEBYTECODE": "1"}
            def cli(*args):
                return subprocess.run([sys.executable, str(SCRIPTS / "sources.py"), *map(str, args)],
                                      env=env, capture_output=True, text=True)
            self.assertEqual(cli("import-last30days", raw, "--out", out).returncode, 0)
            self.assertEqual(cli("validate", out).returncode, 0)
            self.assertEqual(cli("select", out, "--out", selected).returncode, 0)
            self.assertTrue(selected.exists())
            raw.write_text('{}', encoding="utf-8")
            self.assertEqual(cli("import-last30days", raw, "--out", out).returncode, 2)


if __name__ == "__main__":
    unittest.main()
