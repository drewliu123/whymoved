"""Industry transmission maps: graph validation, direction, paths and warnings."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import transmission

AS_OF = "2026-11-14"


def node(identifier, label=None, kind="demand", observables=None, claims=None):
    data = {"id": identifier, "label": label or identifier, "kind": kind,
            "observables": observables or ["可观察指标"]}
    if claims is not None:
        data["claim_ids"] = claims
    return data


def edge(source, sink, mechanism="机制", lag="1-2个季度", claims=None):
    data = {"from": source, "to": sink, "mechanism": mechanism, "lag": lag}
    if claims is not None:
        data["claim_ids"] = claims
    return data


def document(**overrides):
    data = {"schema_version": 1, "theme": "AI用电传导", "as_of": AS_OF,
            "nodes": [node("DEMAND", "AI训练用电", claims=["C1"]),
                      node("GRID", "并网容量", kind="capacity", claims=["C2"]),
                      node("EQUIP", "变压器交付", kind="capex", claims=["C3"]),
                      node("MARGIN", "设备商毛利", kind="margin", claims=["C4"])],
            "edges": [edge("DEMAND", "GRID", claims=["C2"]),
                      edge("GRID", "EQUIP", claims=["C3"]),
                      edge("EQUIP", "MARGIN", claims=["C4"])],
            "bottleneck": {"node": "GRID", "reason": "并网审批", "claim_ids": ["C2"]}}
    data.update(overrides)
    return data


def claims(*ids):
    return {"claims": [{"id": identifier, "text": "x", "type": "fact"} for identifier in ids]}


class ValidationTests(unittest.TestCase):
    def errors(self, doc, ledger=None):
        return transmission.validate_document(doc, ledger.get("claims") if ledger else None)

    def test_valid_document(self):
        self.assertEqual(self.errors(document(), claims("C1", "C2", "C3", "C4")), [])

    def test_top_level_failures(self):
        for patch in ({"schema_version": 2}, {"theme": ""}, {"nodes": []}, {"edges": []},
                      {"bottleneck": None}, {"nodes": "nope"}, {"edges": "nope"}):
            doc = document()
            doc.update(patch)
            self.assertTrue(self.errors(doc), patch)
        self.assertTrue(self.errors("nope"))

    def test_node_failures(self):
        cases = [
            lambda n: n.pop("id"),
            lambda n: n.update(id="1bad"),
            lambda n: n.update(label=""),
            lambda n: n.update(kind="unclear"),
            lambda n: n.update(observables=[]),
            lambda n: n.update(observables=[""]),
            lambda n: n.update(extra=1),
            lambda n: n.update(claim_ids=[]),
            lambda n: n.update(claim_ids=["C404"]),
            lambda n: n.update(claim_ids=["C1", "C1"]),
        ]
        for mutate in cases:
            doc = document()
            mutate(doc["nodes"][0])
            self.assertTrue(self.errors(doc, claims("C1", "C2", "C3", "C4")), mutate)

    def test_duplicate_node_ids(self):
        doc = document()
        doc["nodes"].append(node("DEMAND", "重复"))
        self.assertTrue(self.errors(doc))

    def test_edge_failures(self):
        cases = [
            lambda e: e.update(**{"from": "NOPE"}),
            lambda e: e.update(to="NOPE"),
            lambda e: e.update(mechanism=""),
            lambda e: e.update(lag=""),
            lambda e: e.update(extra=1),
            lambda e: e.update(claim_ids=["C404"]),
        ]
        for mutate in cases:
            doc = document()
            mutate(doc["edges"][0])
            self.assertTrue(self.errors(doc, claims("C1", "C2", "C3", "C4")), mutate)
        doc = document()
        doc["edges"].append(dict(doc["edges"][0]))
        self.assertTrue(any("duplicates" in error for error in self.errors(doc)))
        doc = document()
        doc["edges"].append(edge("GRID", "GRID"))
        self.assertTrue(any("self-loop" in error for error in self.errors(doc)))

    def test_bottleneck_failures(self):
        for patch in ({"node": "NOPE"}, {"reason": ""}, {"extra": 1}):
            doc = document()
            doc["bottleneck"].update(patch)
            self.assertTrue(self.errors(doc), patch)

    def test_claim_references_only_checked_when_ledger_given(self):
        doc = document()
        doc["nodes"][0]["claim_ids"] = ["C404"]
        self.assertEqual(self.errors(doc), [], "shape only without a ledger")
        self.assertTrue(self.errors(doc, claims("C1", "C2")))


class AnalyseTests(unittest.TestCase):
    def test_directions_distances_and_paths(self):
        result = transmission.analyse(document())
        self.assertEqual(result["bottleneck"]["node"], "GRID")
        self.assertEqual(result["directions"], {"DEMAND": "upstream", "EQUIP": "downstream",
                                                "GRID": "bottleneck", "MARGIN": "downstream"})
        self.assertEqual(result["distances"], {"DEMAND": 1, "GRID": 0})
        self.assertEqual(result["paths"], [["DEMAND", "GRID"]])

    def test_multiple_roots_and_longer_chain(self):
        doc = document()
        doc["nodes"].append(node("PRICE", "电价", kind="price", claims=["C5"]))
        doc["edges"].append(edge("PRICE", "GRID", claims=["C5"]))
        result = transmission.analyse(doc)
        self.assertEqual(result["distances"]["PRICE"], 1)
        self.assertEqual(len(result["paths"]), 2)
        doc = document()
        doc["nodes"].append(node("POLICY", "审批政策", kind="policy", claims=["C6"]))
        doc["edges"].append(edge("POLICY", "DEMAND", claims=["C6"]))
        result = transmission.analyse(doc)
        self.assertEqual(result["distances"]["POLICY"], 2)
        self.assertEqual(result["paths"], [["POLICY", "DEMAND", "GRID"]])

    def test_unrelated_node_warning(self):
        doc = document()
        doc["nodes"].append(node("ISOLATED", "无关节点", claims=["C7"]))
        result = transmission.analyse(doc)
        self.assertEqual(result["directions"]["ISOLATED"], "unrelated")
        self.assertTrue(any("没有任何路径连接" in warning for warning in result["warnings"]))
        self.assertTrue(any("ISOLATED" in warning for warning in result["warnings"]))

    def test_cycle_warning_and_termination(self):
        doc = document()
        doc["edges"].append(edge("EQUIP", "DEMAND"))
        result = transmission.analyse(doc)
        self.assertTrue(any("环路" in warning for warning in result["warnings"]))

    def test_unevidenced_nodes_warn(self):
        doc = document()
        doc["nodes"][0].pop("claim_ids")
        result = transmission.analyse(doc)
        self.assertTrue(any("没有挂claim_ids" in warning for warning in result["warnings"]))
        self.assertTrue(any("DEMAND" in warning for warning in result["warnings"]))


class CliTests(unittest.TestCase):
    def invoke(self, payload, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp).resolve() / "transmission.json"
            path.write_text(json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload,
                            encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPTS / "transmission.py"), str(path), *extra],
                                  capture_output=True, text=True)

    def test_valid_cli(self):
        process = self.invoke(document())
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        payload = json.loads(process.stdout)
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["bottleneck"]["node"], "GRID")

    def test_cli_with_claims_and_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            doc_path = root / "transmission.json"
            doc_path.write_text(json.dumps(document()), encoding="utf-8")
            ledger_path = root / "claims.json"
            ledger_path.write_text(json.dumps(claims("C1", "C2", "C3", "C4")), encoding="utf-8")
            target = root / "result.json"
            process = subprocess.run([sys.executable, str(SCRIPTS / "transmission.py"), str(doc_path),
                                      "--claims", str(ledger_path), "--out", str(target)],
                                     capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertTrue(target.exists())

    def test_failures(self):
        self.assertEqual(self.invoke(document(theme="")).returncode, 1)
        self.assertEqual(self.invoke("{").returncode, 2)


if __name__ == "__main__":
    unittest.main()
