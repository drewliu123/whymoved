#!/usr/bin/env python3
"""Industry transmission maps: nodes, mechanisms, lags and the bottleneck (Python 3.9+).

`theme_transmission` research asks where a demand or cost shock stops travelling
into orders, margins and cash. This module gives that chain a structure instead
of a paragraph:

    {"schema_version": 1, "theme": "AI 用电需求传导", "as_of": "...",
     "nodes": [{"id": "DEMAND", "label": "AI 训练用电需求", "kind": "demand",
                "observables": ["数据中心新签订单"], "claim_ids": ["C1"]}],
     "edges": [{"from": "DEMAND", "to": "GRID", "mechanism": "并网排队",
                "lag": "6-18个月", "claim_ids": ["C2"]}],
     "bottleneck": {"node": "GRID", "reason": "并网容量审批", "claim_ids": ["C3"]}}

It validates the graph, finds the paths that reach the bottleneck, reports the
transmission distance of every node and warns about nodes that never reach the
bottleneck, cycles, and nodes with no attached evidence. It does not decide which
mechanism is true; that remains the researcher's judgment.
"""

import argparse
import json
import re
from collections import deque
import sys
from pathlib import Path

SCHEMA_VERSION = 1
KINDS = ("demand", "capex", "capacity", "price", "margin", "policy", "cash", "other")
SAFE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def validate_document(document, claims=None):
    """Validate nodes, edges and the bottleneck; returns T-prefixed errors."""
    if not isinstance(document, dict):
        return ["T1 document must be an object"]
    errors = []
    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append("T1 schema_version must be %d" % SCHEMA_VERSION)
    if not _text(document.get("theme")):
        errors.append("T1 theme must be nonempty text")
    claim_ids = None
    if claims is not None:
        claim_ids = {claim["id"] for claim in claims if isinstance(claim, dict) and _text(claim.get("id"))}
    nodes = document.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return errors + ["T1 nodes must be a nonempty list"]
    ids = set()
    for index, node in enumerate(nodes):
        path = "T1 nodes[%d]" % index
        if not isinstance(node, dict):
            errors.append(path + " must be an object")
            continue
        extra = set(node) - {"id", "label", "kind", "observables", "claim_ids"}
        if extra:
            errors.append(path + " has unknown fields: " + ", ".join(sorted(map(str, extra))))
        identifier = node.get("id")
        if not isinstance(identifier, str) or not SAFE_ID.fullmatch(identifier):
            errors.append(path + ".id must be a safe identifier")
        elif identifier in ids:
            errors.append(path + ".id duplicates another node")
        else:
            ids.add(identifier)
        if not _text(node.get("label")):
            errors.append(path + ".label must be nonempty text")
        if "kind" in node and (not isinstance(node["kind"], str) or node["kind"] not in KINDS):
            errors.append(path + ".kind must be one of " + ", ".join(KINDS))
        observables = node.get("observables")
        if not isinstance(observables, list) or not observables or any(not _text(item) for item in observables):
            errors.append(path + ".observables must list at least one checkable observation")
        errors.extend(_claim_refs(node, path, claim_ids))
    edges = document.get("edges")
    if not isinstance(edges, list) or not edges:
        return errors + ["T1 edges must be a nonempty list"]
    seen_edges = set()
    for index, edge in enumerate(edges):
        path = "T1 edges[%d]" % index
        if not isinstance(edge, dict):
            errors.append(path + " must be an object")
            continue
        extra = set(edge) - {"from", "to", "mechanism", "lag", "claim_ids"}
        if extra:
            errors.append(path + " has unknown fields: " + ", ".join(sorted(map(str, extra))))
        for field in ("from", "to"):
            if not isinstance(edge.get(field), str) or edge[field] not in ids:
                errors.append(path + "." + field + " must reference a declared node")
        if edge.get("from") == edge.get("to"):
            errors.append(path + " cannot be a self-loop")
        if not _text(edge.get("mechanism")):
            errors.append(path + ".mechanism must be nonempty text")
        if not _text(edge.get("lag")):
            errors.append(path + ".lag must describe a time window or condition")
        key = (edge.get("from"), edge.get("to"))
        if key in seen_edges:
            errors.append(path + " duplicates another edge")
        seen_edges.add(key)
        errors.extend(_claim_refs(edge, path, claim_ids))
    bottleneck = document.get("bottleneck")
    if not isinstance(bottleneck, dict):
        return errors + ["T1 bottleneck must be an object"]
    extra = set(bottleneck) - {"node", "reason", "claim_ids"}
    if extra:
        errors.append("T1 bottleneck has unknown fields: " + ", ".join(sorted(map(str, extra))))
    if not isinstance(bottleneck.get("node"), str) or bottleneck["node"] not in ids:
        errors.append("T1 bottleneck.node must reference a declared node")
    if not _text(bottleneck.get("reason")):
        errors.append("T1 bottleneck.reason must be nonempty text")
    errors.extend(_claim_refs(bottleneck, "T1 bottleneck", claim_ids))
    return errors


def _claim_refs(item, path, claim_ids):
    if "claim_ids" not in item:
        return []
    refs = item.get("claim_ids")
    if not isinstance(refs, list) or any(not _text(cid) for cid in refs):
        return [path + ".claim_ids must be a list of claim ids"]
    errors = []
    if not refs:
        errors.append(path + ".claim_ids must not be empty when present")
    if claim_ids is not None:
        missing = [cid for cid in refs if cid not in claim_ids]
        if missing:
            errors.append(path + ".claim_ids references unknown claims: " + ", ".join(missing))
    if len(set(refs)) != len(refs):
        errors.append(path + ".claim_ids contains duplicates")
    return errors


def analyse(document):
    """Return paths to the bottleneck, transmission distances and warnings."""
    nodes = {node["id"]: node for node in document["nodes"]}
    edges = [(edge["from"], edge["to"]) for edge in document["edges"]]
    target = document["bottleneck"]["node"]
    outgoing = {}
    for source, sink in edges:
        outgoing.setdefault(source, []).append(sink)
    incoming = {}
    for source, sink in edges:
        incoming.setdefault(sink, []).append(source)
    distances, paths = {}, []
    parents = {target: None}
    order = deque([target])
    while order:
        node = order.popleft()
        for source in incoming.get(node, []):
            if source not in parents:
                parents[source] = node
                order.append(source)
    for node in nodes:
        if node not in parents:
            continue
        path, current = [], node
        while current is not None:
            path.append(current)
            current = parents[current]
        distances[node] = len(path) - 1
        if not incoming.get(node):
            paths.append(path)
    if not paths and target in parents:
        paths.append([target])
    downstream, order = set(), deque([target])
    while order:
        node = order.popleft()
        if node in downstream:
            continue
        downstream.add(node)
        for sink in outgoing.get(node, []):
            order.append(sink)
    directions = {}
    for node in nodes:
        if node == target:
            directions[node] = "bottleneck"
        elif node in parents:
            directions[node] = "upstream"
        elif node in downstream:
            directions[node] = "downstream"
        else:
            directions[node] = "unrelated"
    warnings = []
    unrelated = sorted(node for node, direction in directions.items() if direction == "unrelated")
    if unrelated:
        warnings.append("这些节点与瓶颈没有任何路径连接，可能只是背景: " + ", ".join(unrelated))
    cycles = _cycles(nodes, outgoing)
    if cycles:
        warnings.append("存在环路，传导方向不唯一: " + "；".join(" -> ".join(cycle) for cycle in cycles))
    unevidenced = sorted(identifier for identifier, node in nodes.items() if not node.get("claim_ids"))
    if unevidenced:
        warnings.append("这些节点没有挂claim_ids，尚无可核对证据: " + ", ".join(unevidenced))

    return {"passed": True, "theme": document.get("theme", ""), "as_of": document.get("as_of", ""),
            "bottleneck": {"node": target, "label": nodes[target]["label"],
                           "reason": document["bottleneck"]["reason"]},
            "distances": {node: distances[node] for node in sorted(distances)},
            "directions": {node: directions[node] for node in sorted(directions)},
            "paths": sorted(paths, key=lambda path: (len(path), path)),
            "warnings": warnings,
            "notes": ["路径按边的方向从远端走到瓶颈；距离是跳数，不是时间。",
                      "lag是研究者给出的时间窗口，工具不做换算。",
                      "环路只提示不判错：价格与需求可能真的互相反馈。"]}


def _cycles(nodes, outgoing):
    """Return simple cycles up to length 4 to keep the warning readable."""
    found = []
    for start in sorted(nodes):
        stack = [(start, [start])]
        while stack:
            node, path = stack.pop()
            for sink in outgoing.get(node, []):
                if sink == start and len(path) > 1:
                    cycle = path + [start]
                    canonical = min(tuple(cycle[:-1][index:] + cycle[:-1][:index]) for index in range(len(cycle) - 1))
                    if list(canonical) not in found:
                        found.append(list(canonical))
                elif sink not in path and len(path) < 4:
                    stack.append((sink, path + [sink]))
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--claims", type=Path, help="optional claims.json to verify claim_ids")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.document.read_text(encoding="utf-8"))
        claims = json.loads(args.claims.read_text(encoding="utf-8")).get("claims") if args.claims else None
    except (OSError, ValueError) as exc:
        print(json.dumps({"passed": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2
    errors = validate_document(document, claims)
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    result = analyse(document)
    text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(json.dumps({"passed": True, "written": str(args.out)}, ensure_ascii=False))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
