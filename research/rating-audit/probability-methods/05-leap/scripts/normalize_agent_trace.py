#!/usr/bin/env python3
"""Normalize completed research traces into AgentFuture evidence snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

URL_RE = re.compile(r"https?://[^\s<>()\"']+")
SPACE_RE = re.compile(r"\s+")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_'-]{2,}")
SECRET_VALUE_RE = re.compile(
    r"(?i)\b(?:sk|sk-proj|ak|pk)-[A-Za-z0-9_\-]{16,}\b|"
    r"\b[A-Za-z0-9_\-]{32,}\.[A-Za-z0-9_\-]{16,}\.[A-Za-z0-9_\-]{16,}\b"
)
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|authorization|bearer|password)\b\s*[:=]\s*\S+"
)
SENSITIVE_URL_PARAM_RE = re.compile(
    r"(?i)([?&](?:api[_-]?key|access[_-]?token|auth|key|signature|token|x-amz-signature)=)[^&#\s]+"
)

IMPORTANT_KEY_PARTS = (
    "tool",
    "result",
    "content",
    "message",
    "output",
    "response",
    "summary",
    "observation",
    "url",
    "query",
    "search",
    "evidence",
)
SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "secret",
    "token",
    "authorization",
    "bearer",
    "password",
    ".env",
    "openrouter_api_key",
    "openai_api_key",
)
EVIDENCE_MARKERS = (
    "evidence",
    "sources",
    "source:",
    "证据",
    "来源",
    "总体结论",
    "conclusion",
    "registered office",
    "headquartered",
    "headquarters",
)
OPERATIONAL_LOG_MARKERS = (
    "starting task:",
    "provider_config",
    "tool definitions",
    "'schema':",
    '"schema":',
    "npm notice",
    "runtimewarning",
    "main_agent_turn_",
    "task_tracer.py",
    "orchestrator.py",
    "deepseek_openrouter_client.py",
    "manager.py",
)
OPERATIONAL_PATH_PARTS = (
    "system_prompt",
    "tools[",
    "tool_calls[",
    "base_url",
    "platform",
    "session_start",
    "last_updated",
    "message_count",
    ".reasoning",
    ".reasoning_content",
)
PROMPT_CHUNK_MARKERS = (
    "<system-reminder",
    "<current_date>",
)

YES_WORDS = {"yes", "true"}
NO_WORDS = {"no", "false"}
QUESTION_STOPWORDS = {
    "the",
    "and",
    "for",
    "from",
    "with",
    "that",
    "this",
    "will",
    "would",
    "could",
    "should",
    "have",
    "has",
    "had",
    "been",
    "being",
    "does",
    "did",
    "are",
    "was",
    "were",
    "into",
    "onto",
    "over",
    "under",
    "after",
    "before",
    "about",
    "what",
    "which",
    "when",
    "where",
    "as",
    "of",
}


def _read_input(path: Path) -> list[tuple[str, str]]:
    if path.is_dir():
        items: list[tuple[str, str]] = []
        for child in sorted(path.rglob("*")):
            if not child.is_file():
                continue
            if child.suffix.lower() not in {".json", ".jsonl", ".log", ".txt", ".md"}:
                continue
            try:
                label = child.relative_to(path).as_posix()
                items.append((label, child.read_text(encoding="utf-8", errors="replace")))
            except OSError:
                continue
        return items
    return [(path.name, path.read_text(encoding="utf-8", errors="replace"))]


def _loads_maybe_json(text: str) -> Any | None:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    rows = []
    ok = False
    for line in stripped.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
            ok = True
        except json.JSONDecodeError:
            return None
    return rows if ok else None


def _norm_text(text: str) -> str:
    return SPACE_RE.sub(" ", str(text or "")).strip()


def _is_important_path(path: str) -> bool:
    lowered = path.lower()
    return any(part in lowered for part in IMPORTANT_KEY_PARTS)


def _is_sensitive_path(path: str) -> bool:
    lowered = str(path or "").lower()
    return any(part in lowered for part in SENSITIVE_KEY_PARTS)


def _redact_sensitive(text: str) -> str:
    redacted = SECRET_VALUE_RE.sub("[REDACTED_SECRET]", str(text or ""))
    redacted = SECRET_ASSIGNMENT_RE.sub(lambda m: f"{m.group(1)}=[REDACTED_SECRET]", redacted)
    return SENSITIVE_URL_PARAM_RE.sub(r"\1[REDACTED_SECRET]", redacted)


def _is_sensitive_chunk(path: str, text: str) -> bool:
    if _is_sensitive_path(path):
        return True
    lowered = str(text or "").lower()
    if any(part in lowered for part in SENSITIVE_KEY_PARTS):
        return True
    return bool(SECRET_VALUE_RE.search(text) or SECRET_ASSIGNMENT_RE.search(text))


def _is_operational_log_chunk(text: str) -> bool:
    lowered = str(text or "").lower()
    if not lowered:
        return False
    if any(marker in lowered for marker in PROMPT_CHUNK_MARKERS):
        return True
    if (
        "use your available web/research tools first" in lowered
        and "forecasting task" in lowered
    ):
        return True
    if "benchmark evidence collection stage" in lowered:
        return True
    if (
        "you must call the web_search tool first" in lowered
        and "return a brief answer with sources" in lowered
    ):
        return True
    if (
        ("use web search" in lowered or "must call the web_search" in lowered)
        and ("find whether" in lowered or "answer briefly" in lowered)
    ):
        return True
    if "tool definitions" in lowered or "'schema':" in lowered or '"schema":' in lowered:
        return True
    if '"success": false' in lowered and '"error"' in lowered:
        return True
    if "error: error code:" in lowered:
        return True
    if "invalid token" in lowered or "insufficient_user_quota" in lowered:
        return True
    if "用户额度不足" in lowered:
        return True
    if "duckduckgo search failed" in lowered:
        return True
    if "search-only backend and cannot extract" in lowered:
        return True
    if "npm notice" in lowered or "runtimewarning" in lowered:
        return True
    if "starting task:" in lowered:
        return True
    if any(marker in lowered for marker in OPERATIONAL_LOG_MARKERS):
        return not any(marker in lowered for marker in EVIDENCE_MARKERS)
    return False


def _is_operational_path(path: str) -> bool:
    lowered = str(path or "").lower()
    return any(part in lowered for part in OPERATIONAL_PATH_PARTS)


def _collect_json_strings(value: Any, *, path: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            key_s = str(key)
            next_path = f"{path}.{key_s}" if path else key_s
            yield from _collect_json_strings(child, path=next_path)
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            yield from _collect_json_strings(child, path=f"{path}[{idx}]")
    elif isinstance(value, str):
        text = _norm_text(value)
        if not text:
            return
        if len(text) >= 80 or URL_RE.search(text) or _is_important_path(path):
            yield path or "json", text
    elif value is not None and _is_important_path(path):
        yield path, _norm_text(value)


def _collect_text_chunks(text: str, *, label: str, max_chars: int) -> Iterable[tuple[str, str]]:
    normalized = text.replace("\r\n", "\n")
    blocks = [block.strip() for block in re.split(r"\n{2,}", normalized) if block.strip()]
    if not blocks:
        blocks = [normalized.strip()]

    chunk_id = 0
    for block in blocks:
        block = block.strip()
        if len(block) < 80 and not URL_RE.search(block):
            continue
        start = 0
        while start < len(block):
            chunk = block[start : start + max_chars].strip()
            if chunk:
                chunk_id += 1
                yield f"{label}#chunk{chunk_id}", _norm_text(chunk)
            if start + max_chars >= len(block):
                break
            start += max_chars


def _parse_options(args: argparse.Namespace) -> list[str] | None:
    options: list[str] = []
    if args.options_json:
        loaded = json.loads(args.options_json)
        if not isinstance(loaded, list):
            raise SystemExit("--options-json must be a JSON list")
        options.extend(str(item) for item in loaded)
    options.extend(args.option or [])
    cleaned = [str(opt).strip() for opt in options if str(opt).strip()]
    return cleaned or None


def _infer_question_family(options: list[str] | None, output_type: str) -> str:
    if output_type == "continuous" or not options:
        return "continuous_numeric"
    return "nominal_classification"


def _first_url(text: str) -> str | None:
    match = URL_RE.search(text)
    if not match:
        return None
    return match.group(0).rstrip(".,;]")


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _option_key(option: str) -> str:
    text = str(option or "").strip()
    if ":" in text:
        text = text.split(":", 1)[0]
    return text.strip().lower()


def _is_yes_no_options(options: list[str] | None) -> bool:
    if not options or len(options) != 2:
        return False
    keys = {_option_key(opt) for opt in options}
    return bool(keys & YES_WORDS) and bool(keys & NO_WORDS)


def _yes_option(options: list[str] | None) -> str:
    for opt in options or []:
        if _option_key(opt) in YES_WORDS:
            return opt
    return "Yes"


def _no_option(options: list[str] | None) -> str:
    for opt in options or []:
        if _option_key(opt) in NO_WORDS:
            return opt
    return "No"


def _question_tokens(question: str) -> set[str]:
    lowered = re.sub(r"\bas\s+of\s+\d{4}[-/]\d{1,2}[-/]\d{1,2},?", " ", question.lower())
    return {
        token
        for token in WORD_RE.findall(lowered)
        if token not in QUESTION_STOPWORDS and not token.isdigit()
    }


def _binary_yes_no_signal(
    *,
    text: str,
    question: str,
    options: list[str] | None,
) -> tuple[list[str], list[str]]:
    """Infer a conservative Yes/No support label from search snippets.

    This is intentionally lexical. It only fires when the snippet repeats
    several content words from the yes/no proposition, leaving ambiguous
    evidence for the downstream LLM likelihood stage.
    """
    if not _is_yes_no_options(options):
        return [], []
    tokens = _question_tokens(question)
    if not tokens:
        return [], []
    text_l = text.lower()
    overlap = {tok for tok in tokens if tok in text_l}
    if len(overlap) < min(3, len(tokens)):
        return [], []
    negated = re.search(r"\b(?:not|no longer|isn't|is not|are not|was not|were not)\b", text_l)
    if negated:
        return [], [_no_option(options)]
    return [_yes_option(options)], []


def _literal_option_signal(text: str, options: list[str] | None) -> tuple[list[str], list[str]]:
    if not options:
        return [], []
    if _is_yes_no_options(options):
        return [], []
    text_l = text.lower()
    matched = []
    for option in options:
        option_l = str(option or "").strip().lower()
        if option_l and option_l in text_l:
            matched.append(option)
            continue
        if ":" in option_l:
            core = option_l.split(":", 1)[1].strip()
            if core and len(core) >= 5 and core in text_l:
                matched.append(option)
    return matched[:1], []


def _build_evidence(
    *,
    agent: str,
    source_label: str,
    path: str,
    text: str,
    round_idx: int,
    question: str,
    options: list[str] | None,
) -> dict[str, Any]:
    url = _first_url(text)
    query_or_url = url or f"{path}#{round_idx}"
    supports, opposes = _literal_option_signal(text, options)
    if not supports and not opposes:
        supports, opposes = _binary_yes_no_signal(text=text, question=question, options=options)
    has_external_snippet = bool(url) or "source: web search" in text.lower()
    has_signal = has_external_snippet or bool(supports) or bool(opposes)
    comparison_text = ""
    if supports:
        comparison_text = f"Search snippet supports option: {supports[0]}"
    elif opposes:
        comparison_text = f"Search snippet opposes option: {opposes[0]}"
    elif has_signal:
        comparison_text = "External search snippet relevant to the target question."
    return {
        "source_tool": f"{agent}_trace",
        "query_or_url": query_or_url,
        "content": text,
        "round_idx": round_idx,
        "description": f"{agent} trace evidence from {source_label}",
        "variable": "",
        "supports": supports,
        "opposes": opposes,
        "source_tier": "C" if has_signal else "unknown",
        "strength": "medium" if supports or opposes else ("weak" if has_signal else "none"),
        "reliability": "medium" if has_signal else "unknown",
        "date_hint": "unknown",
        "why_relevant": "Extracted from a completed agent research trace.",
        "observation_type": "qualitative" if has_signal else "none",
        "support_shape": "class_support" if supports else ("class_reject" if opposes else ("comparative" if has_signal else "none")),
        "measurement_scope": "direct_target" if supports or opposes else ("proxy_signal" if has_signal else "context_only"),
        "target_match": "direct" if supports or opposes else ("related" if has_signal else "unknown"),
        "market_role": "unknown",
        "representativeness": "unknown",
        "sample_role": "unknown",
        "independence_key": url or f"{agent}:{source_label}:{round_idx}",
        "point_value": None,
        "lower_bound": None,
        "upper_bound": None,
        "trend": "unknown",
        "comparison_text": comparison_text,
        "unit": "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, help="Name of the agent that produced the completed trace.")
    parser.add_argument("--input", required=True, help="Trace file, JSON log, text log, or directory.")
    parser.add_argument("--output", required=True, help="Output evidence snapshot JSON path.")
    parser.add_argument("--task-id", default="agentos_task")
    parser.add_argument("--question", required=True)
    parser.add_argument("--freeze-time", default="")
    parser.add_argument("--option", action="append", default=[])
    parser.add_argument("--options-json", default="")
    parser.add_argument("--output-type", default="", choices=["", "single_choice", "multi_choice", "ordinal", "continuous"])
    parser.add_argument("--metadata-json", default="{}")
    parser.add_argument("--max-items", type=int, default=40)
    parser.add_argument("--max-chars", type=int, default=6000)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    options = _parse_options(args)
    output_type = args.output_type or ("single_choice" if options else "continuous")
    metadata = json.loads(args.metadata_json)
    if not isinstance(metadata, dict):
        raise SystemExit("--metadata-json must be a JSON object")

    candidates: list[tuple[str, str, str]] = []
    for label, text in _read_input(input_path):
        loaded = _loads_maybe_json(text)
        if loaded is None:
            candidates.extend(_collect_text_chunks(text, label=label, max_chars=args.max_chars))
        else:
            for path, chunk in _collect_json_strings(loaded):
                for chunk_label, chunk_text in _collect_text_chunks(chunk, label=f"{label}:{path}", max_chars=args.max_chars):
                    candidates.append((chunk_label, path, chunk_text))

    evidence = []
    seen = set()
    for idx, item in enumerate(candidates, 1):
        if len(item) == 2:
            source_label, text = item
            path = source_label
        else:
            source_label, path, text = item
        text = _norm_text(text)
        if not text:
            continue
        text = _redact_sensitive(text)
        if _is_sensitive_chunk(path, text) or _is_operational_path(path) or _is_operational_log_chunk(text):
            continue
        fp = _stable_hash(text)
        if fp in seen:
            continue
        seen.add(fp)
        evidence.append(
            _build_evidence(
                agent=args.agent,
                source_label=source_label,
                path=path,
                text=text,
                round_idx=len(evidence) + 1,
                question=args.question,
                options=options,
            )
        )
        if len(evidence) >= args.max_items:
            break

    hash_payload = {
        "question": args.question,
        "options": options,
        "freeze_time": args.freeze_time or None,
        "evidence": [
            {
                "source_tool": ev["source_tool"],
                "query_or_url": ev["query_or_url"],
                "content": ev["content"],
                "round_idx": ev["round_idx"],
                "supports": ev["supports"],
                "opposes": ev["opposes"],
                "source_tier": ev["source_tier"],
                "strength": ev["strength"],
                "reliability": ev["reliability"],
                "observation_type": ev["observation_type"],
                "support_shape": ev["support_shape"],
                "measurement_scope": ev["measurement_scope"],
                "target_match": ev["target_match"],
                "comparison_text": ev["comparison_text"],
            }
            for ev in evidence
        ],
    }
    evidence_bundle_hash = _stable_hash(hash_payload)

    metadata.update(
        {
            "task_id": args.task_id,
            "agent_cli": args.agent,
            "source_trace": input_path.name,
            "output_type": output_type,
            "evidence_bundle_hash": evidence_bundle_hash,
            "stage_isolation": "evidence_locked_finalization",
        }
    )

    snapshot = {
        "task_id": args.task_id,
        "question": args.question,
        "freeze_time": args.freeze_time or None,
        "metadata": metadata,
        "question_family": _infer_question_family(options, output_type),
        "options": options,
        "evidence": evidence,
        "frame": None,
        "evidence_count": len(evidence),
        "evidence_bundle_hash": evidence_bundle_hash,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "snapshot": str(output_path),
        "evidence_count": len(evidence),
        "evidence_bundle_hash": evidence_bundle_hash,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
