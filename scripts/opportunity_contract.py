#!/usr/bin/env python3
"""Versioned research opportunity records; validate evidence links, not alpha."""

import re

STATUSES = {"research_now": "优先研究", "watch": "等待触发", "priced_in": "价格已反映", "no_edge": "未见优势"}
BASES = {"consensus": "调查共识", "price_implied": "价格隐含", "proxy": "研究代理估计"}
THESIS = {"strengthened": "增强", "weakened": "削弱", "unchanged": "未变", "invalidated": "失效"}
RESULTS = {"hit": "已触发", "not_hit": "已检查未触发", "not_checked": "未检查"}
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _choice(value, choices):
    return isinstance(value, str) and value in choices


def validate_opportunity(report, claims):
    """Optional for historical reports; versioned records must be complete."""
    errors = []
    claim_map = {c["id"]: c for c in claims if isinstance(c, dict) and isinstance(c.get("id"), str)}

    def texts(item, fields, path):
        if not isinstance(item, dict):
            errors.append(path + " must be an object")
            return False
        for field in fields:
            if not _text(item.get(field)):
                errors.append(path + "." + field + " must be nonempty text")
        return True

    def refs(item, path, required=True):
        values = item.get("claim_ids")
        if not isinstance(values, list) or (required and not values):
            errors.append(path + ".claim_ids must be a " + ("nonempty " if required else "") + "list")
            return []
        if any(not isinstance(cid, str) or cid not in claim_map for cid in values):
            errors.append(path + ".claim_ids contains unknown references")
        safe = [cid for cid in values if isinstance(cid, str) and cid in claim_map]
        if len(safe) != len(set(safe)):
            errors.append(path + ".claim_ids contains duplicates")
        return [claim_map[cid].get("type") for cid in safe]

    opportunity = report.get("opportunity")
    if "opportunity" in report:
        if not isinstance(opportunity, dict):
            errors.append("opportunity must be an object")
        else:
            if type(opportunity.get("version")) is not int or opportunity["version"] != 1:
                errors.append("opportunity.version must be 1")
            applicability = opportunity.get("applicability")
            if applicability == "not_applicable":
                texts(opportunity, ("reason",), "opportunity")
                if any(key in opportunity for key in ("market_view", "variant", "edge", "catalyst", "payoff", "assessment", "triggers")):
                    errors.append("not_applicable opportunity must not contain trading fields")
            elif applicability != "trading":
                errors.append("opportunity.applicability must be trading or not_applicable")
            else:
                for key in ("market_view", "variant", "edge", "catalyst", "payoff", "assessment"):
                    item = opportunity.get(key)
                    path = "opportunity." + key
                    if not texts(item, ("text", "by") if key == "catalyst" else ("text",), path):
                        continue
                    types = refs(item, path)
                    if key == "market_view":
                        basis = item.get("basis")
                        if not _choice(basis, BASES):
                            errors.append(path + ".basis is invalid")
                        elif basis == "proxy" and "inference" not in types:
                            errors.append(path + " proxy requires an inference claim")
                        elif basis == "consensus" and "consensus" not in types:
                            errors.append(path + " consensus requires a consensus claim")
                        elif basis == "price_implied" and not {"price", "inference"}.issubset(types):
                            errors.append(path + " price_implied requires price and inference claims")
                    if key == "assessment" and not _choice(item.get("status"), STATUSES):
                        errors.append(path + ".status is invalid")
                triggers = opportunity.get("triggers")
                if not isinstance(triggers, list) or not triggers:
                    errors.append("opportunity.triggers must be a nonempty list")
                else:
                    seen = set()
                    for i, trigger in enumerate(triggers):
                        path = "opportunity.triggers[%d]" % i
                        if not texts(trigger, ("signal", "by", "supports_if", "weakens_if", "invalidates_if"), path):
                            continue
                        tid = trigger.get("id")
                        if not isinstance(tid, str) or not ID.fullmatch(tid) or tid in seen:
                            errors.append(path + ".id must be a unique safe identifier")
                        else:
                            seen.add(tid)
                        refs(trigger, path)
    update = report.get("update")
    if isinstance(update, dict) and "opportunity" in update:
        change = update["opportunity"]
        if texts(change, ("reason", "price_move", "remaining_edge"), "update.opportunity"):
            refs(change, "update.opportunity")
            if not isinstance(opportunity, dict) or opportunity.get("applicability") != "trading":
                errors.append("update.opportunity requires a trading opportunity")
            for field in ("previous_status", "current_status"):
                if not _choice(change.get(field), STATUSES):
                    errors.append("update.opportunity." + field + " is invalid")
            assessment = opportunity.get("assessment", {}) if isinstance(opportunity, dict) else {}
            if isinstance(assessment, dict) and change.get("current_status") != assessment.get("status"):
                errors.append("update.opportunity.current_status differs from assessment")
            if not _choice(change.get("thesis_change"), THESIS):
                errors.append("update.opportunity.thesis_change is invalid")
            results = change.get("trigger_results")
            if not isinstance(results, list) or not results:
                errors.append("update.opportunity.trigger_results must be a nonempty list")
            else:
                seen = set()
                for i, row in enumerate(results):
                    path = "update.opportunity.trigger_results[%d]" % i
                    if not texts(row, ("observation",), path):
                        continue
                    tid = row.get("trigger_id")
                    if not isinstance(tid, str) or not ID.fullmatch(tid) or tid in seen:
                        errors.append(path + ".trigger_id must be a unique safe identifier")
                    else:
                        seen.add(tid)
                    status = row.get("status")
                    if not _choice(status, RESULTS):
                        errors.append(path + ".status is invalid")
                    refs(row, path, required=status != "not_checked")
            if "review" in change:
                texts(change["review"], ("direction", "magnitude", "timing", "mechanism", "price_realization"), "update.opportunity.review")
    return errors


def validate_parent_opportunity(parent, report):
    """Bind an update to the actual frozen parent, without reinterpreting triggers."""
    old = parent.get("opportunity")
    update = report.get("update", {})
    change = update.get("opportunity") if isinstance(update, dict) else None
    if not isinstance(old, dict) or old.get("applicability") != "trading":
        return ["update.opportunity requires a trading parent"] if change is not None else []
    current = report.get("opportunity")
    if not isinstance(current, dict) or current.get("applicability") != "trading" or not isinstance(change, dict):
        return ["trading parent requires opportunity and update.opportunity; close a thesis explicitly"]
    errors = []
    if change.get("previous_status") != old["assessment"]["status"]:
        errors.append("update.opportunity.previous_status differs from frozen parent")
    expected = {t["id"] for t in old["triggers"]}
    rows = change.get("trigger_results", [])
    actual = [r.get("trigger_id") for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []
    if len(actual) != len(expected) or any(not isinstance(t, str) for t in actual) or set(t for t in actual if isinstance(t, str)) != expected:
        errors.append("update.opportunity.trigger_results must cover every frozen parent trigger exactly once")
    return errors


def opportunity_blocks(opportunity, appendix=False):
    if opportunity["applicability"] != "trading":
        return
    assessment = opportunity["assessment"]
    if not appendix:
        yield ("p", STATUSES[assessment["status"]] + "：" + assessment["text"], assessment["claim_ids"])
        return
    yield ("h2", "附录：机会判断与触发条件")
    for key, label in (("market_view", "市场押注"), ("variant", "我们的分歧"), ("edge", "证据优势"), ("catalyst", "重估催化"), ("payoff", "剩余空间与做错代价")):
        item = opportunity[key]
        text = label + "：" + item["text"]
        if key == "market_view":
            text += "（依据：" + BASES[item["basis"]] + "）"
        if key == "catalyst":
            text += "；时间/到期：" + item["by"]
        yield ("p", text, item["claim_ids"])
    for trigger in opportunity["triggers"]:
        yield ("h3", trigger["id"] + " · " + trigger["signal"])
        yield ("p", "时间/到期：" + trigger["by"] + "；支持：" + trigger["supports_if"] + "；削弱：" + trigger["weakens_if"] + "；失效：" + trigger["invalidates_if"], trigger["claim_ids"])


def update_blocks(change):
    yield ("p", "机会状态：" + STATUSES[change["previous_status"]] + " → " + STATUSES[change["current_status"]] + "；原判断" + THESIS[change["thesis_change"]] + "：" + change["reason"], change["claim_ids"])
    yield ("p", "期间价格变化：" + change["price_move"] + "；剩余机会：" + change["remaining_edge"], change["claim_ids"])
    for row in change["trigger_results"]:
        yield ("p", row["trigger_id"] + " · " + RESULTS[row["status"]] + "：" + row["observation"], row["claim_ids"])
    if "review" in change:
        for key, label in (("direction", "方向"), ("magnitude", "幅度"), ("timing", "时点"), ("mechanism", "机制兑现"), ("price_realization", "价格兑现")):
            yield ("p", "复盘·" + label + "：" + change["review"][key], change["claim_ids"])
