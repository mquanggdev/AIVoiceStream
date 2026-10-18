"""Vòng lặp agent cho một lượt nói: LLM ⇄ tools, stream từng câu để đọc ngay bằng TTS."""

from __future__ import annotations

import json
import logging
import re
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from src.agent.fact_check import check_sentence, extract_money
from src.agent.llm import ChatModel
from src.agent.prompts import FALLBACK_ERROR_TEXT, FILLER_TEXTS, SAVE_FILLER_TEXT, build_system_prompt
from src.agent.tools import TOOL_SCHEMAS, ToolContext, execute_tool
from src.config import get_settings
from src.core.spoken import to_spoken

logger = logging.getLogger("agent.runner")

_SENTENCE_END = re.compile(r"(?<=[.!?…])\s+|\n+")
MIN_SENTENCE_CHARS = 18
MIN_FIRST_SENTENCE_CHARS = 6  # câu đầu ngắn ("Dạ có ạ.") được phát ngay để khách nghe phản hồi sớm
MAX_BUFFER_CHARS = 220
TOOL_RESULT_MAX_CHARS = 7000


@dataclass
class SentenceEvent:
    text: str  # dạng viết (lưu DB, kiểm tra số)
    spoken: str  # dạng đọc (gửi TTS)
    index: int
    blocked_codes: list[str] = field(default_factory=list)
    unverified_prices: list[int] = field(default_factory=list)


@dataclass
class FillerEvent:
    text: str
    spoken: str


@dataclass
class ToolCallEvent:
    name: str
    arguments: dict
    result_preview: str


@dataclass
class DoneEvent:
    text: str
    meta: dict


class SentenceSplitter:
    def __init__(self, first: bool = True) -> None:
        self.buffer = ""
        self.first = first

    def feed(self, piece: str) -> list[str]:
        self.buffer += piece
        out: list[str] = []
        while True:
            match = _SENTENCE_END.search(self.buffer)
            if not match:
                break
            candidate = self.buffer[: match.start()].strip()
            min_chars = MIN_FIRST_SENTENCE_CHARS if self.first else MIN_SENTENCE_CHARS
            if len(candidate) < min_chars:
                # câu quá ngắn ("Dạ.") → gộp với câu sau cho TTS tự nhiên hơn
                next_match = _SENTENCE_END.search(self.buffer, match.end())
                if not next_match:
                    break
                candidate = self.buffer[: next_match.start()].strip()
                self.buffer = self.buffer[next_match.end() :]
            else:
                self.buffer = self.buffer[match.end() :]
            if candidate:
                out.append(candidate)
                self.first = False
        if len(self.buffer) > MAX_BUFFER_CHARS:
            cut = self.buffer.rfind(",", 0, MAX_BUFFER_CHARS)
            if cut > MIN_SENTENCE_CHARS:
                out.append(self.buffer[: cut + 1].strip())
                self.buffer = self.buffer[cut + 1 :]
        return out

    def flush(self) -> list[str]:
        rest, self.buffer = self.buffer.strip(), ""
        return [rest] if rest else []


def _compact_result(name: str, result: dict) -> dict | str:
    """Rút gọn kết quả tool để làm ngữ cảnh cho lượt sau."""
    if name == "search_units":
        keep = ("unit_code", "unit_type", "area_net_m2", "floor", "price_text", "price_type", "status", "views")
        units = result.get("units", []) + result.get("closest_options", [])
        return {
            "total_matches": result.get("total_matches"),
            "units": [{k: u.get(k) for k in keep} for u in units],
        }
    if name == "get_unit":
        keep = ("unit_code", "subdivision", "unit_type", "area_net_m2", "floor", "price_text", "price_type", "status",
                "views", "balcony_direction")
        return {k: result.get(k) for k in keep}
    text = json.dumps(result, ensure_ascii=False)
    return text[:1200]


def build_history(messages: list, max_turns: int) -> list[dict]:
    """messages: các Message ORM của cuộc gọi (đã sắp theo id), bỏ câu lót."""
    history = []
    for message in messages:
        if (message.meta or {}).get("is_filler") or (message.meta or {}).get("is_greeting_audio_only"):
            continue
        role = "user" if message.role == "customer" else "assistant"
        content = message.content
        if role == "assistant" and (message.meta or {}).get("interrupted"):
            content += " (khách đã ngắt lời giữa chừng)"
        if content.strip():
            history.append({"role": role, "content": content})
    return history[-max_turns * 2 :]


async def run_agent_turn(
    ctx: ToolContext,
    model: ChatModel,
    user_text: str,
    history: list[dict],
) -> AsyncIterator[SentenceEvent | FillerEvent | ToolCallEvent | DoneEvent]:
    settings = get_settings()
    started = time.perf_counter()
    ctx.remember_prices(extract_money(user_text))
    messages: list[dict] = [{"role": "system", "content": build_system_prompt(ctx.state, ctx.today)}]
    messages += history
    messages.append({"role": "user", "content": user_text})

    sentences: list[SentenceEvent] = []
    tool_log: list[dict] = []
    filler_sent = False
    first_sentence_ms: float | None = None
    error: str | None = None
    llm_rounds = 0
    llm_cost = 0.0
    llm_tokens = [0, 0]

    def make_sentence(text: str) -> SentenceEvent:
        nonlocal first_sentence_ms
        known_codes = set(ctx.state.get("known_unit_codes", []))
        known_prices = set(ctx.state.get("known_prices", []))
        checked = check_sentence(text, known_codes, known_prices)
        if first_sentence_ms is None:
            first_sentence_ms = (time.perf_counter() - started) * 1000
        event = SentenceEvent(
            text=checked.text,
            spoken=to_spoken(checked.text),
            index=len(sentences),
            blocked_codes=checked.blocked_codes,
            unverified_prices=checked.unverified_prices,
        )
        sentences.append(event)
        return event

    try:
        for round_index in range(settings.agent_max_tool_rounds + 1):
            llm_rounds += 1
            allow_tools = round_index < settings.agent_max_tool_rounds
            splitter = SentenceSplitter(first=not sentences)
            round_text = ""
            calls: dict[int, dict] = {}
            async for chunk in model.stream(messages, TOOL_SCHEMAS if allow_tools else None):
                if chunk.cost_usd is not None or chunk.prompt_tokens is not None:
                    llm_cost += chunk.cost_usd or 0.0
                    llm_tokens[0] += chunk.prompt_tokens or 0
                    llm_tokens[1] += chunk.completion_tokens or 0
                if chunk.content:
                    round_text += chunk.content
                    for sentence in splitter.feed(chunk.content):
                        yield make_sentence(sentence)
                for delta in chunk.tool_calls:
                    call = calls.setdefault(delta.index, {"id": None, "name": "", "arguments": ""})
                    if delta.id:
                        call["id"] = delta.id
                    if delta.name:
                        call["name"] = delta.name
                    call["arguments"] += delta.arguments or ""
            for sentence in splitter.flush():
                yield make_sentence(sentence)

            if not calls:
                break

            if not sentences and not filler_sent:
                if all(call["name"] == "save_customer_info" for call in calls.values()):
                    filler = SAVE_FILLER_TEXT
                else:
                    filler = FILLER_TEXTS[ctx.conversation.turn_count % len(FILLER_TEXTS)]
                filler_sent = True
                yield FillerEvent(text=filler, spoken=to_spoken(filler))

            ordered = [calls[i] for i in sorted(calls)]
            for i, call in enumerate(ordered):
                call["id"] = call["id"] or f"call_{round_index}_{i}"
            messages.append(
                {
                    "role": "assistant",
                    "content": round_text or None,
                    "tool_calls": [
                        {
                            "id": call["id"],
                            "type": "function",
                            "function": {"name": call["name"], "arguments": call["arguments"] or "{}"},
                        }
                        for call in ordered
                    ],
                }
            )
            for call in ordered:
                tool_started = time.perf_counter()
                result = await execute_tool(ctx, call["name"], call["arguments"])
                payload = json.dumps(result, ensure_ascii=False)
                tool_log.append(
                    {
                        "name": call["name"],
                        "arguments": call["arguments"],
                        "ms": round((time.perf_counter() - tool_started) * 1000),
                        "result_preview": payload[:600],
                    }
                )
                yield ToolCallEvent(name=call["name"], arguments=_safe_json(call["arguments"]), result_preview=payload[:300])
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": payload[:TOOL_RESULT_MAX_CHARS]})
    except Exception as exc:  # noqa: BLE001 - lỗi LLM không được làm rơi cuộc gọi
        logger.exception("agent turn failed")
        error = f"{type(exc).__name__}: {exc}"[:300]
        if not sentences:
            yield make_sentence(FALLBACK_ERROR_TEXT)

    if not sentences:
        yield make_sentence("Dạ em chưa có thông tin này, anh chị muốn em nhờ chuyên viên kiểm tra giúp không ạ?")

    if ctx.turn_facts:
        ctx.state["recent_facts"] = [
            {"tool": fact["tool"], "args": fact["args"], "result": _compact_result(fact["tool"], fact["result"])}
            for fact in ctx.turn_facts
        ]

    full_text = " ".join(event.text for event in sentences)
    meta = {
        "llm_model": model.name,
        "llm_rounds": llm_rounds,
        "llm_cost_usd": round(llm_cost, 7),
        "llm_tokens": {"prompt": llm_tokens[0], "completion": llm_tokens[1]},
        "llm_first_sentence_ms": round(first_sentence_ms or 0),
        "agent_total_ms": round((time.perf_counter() - started) * 1000),
        "tool_calls": tool_log,
        "filler_used": filler_sent,
        "fact_check": "mismatch" if any(e.blocked_codes for e in sentences) else "ok",
        "blocked_codes": sorted({c for e in sentences for c in e.blocked_codes}),
        "unverified_prices": sorted({p for e in sentences for p in e.unverified_prices}),
        "spoken": " ".join(event.spoken for event in sentences),
    }
    if error:
        meta["error"] = error
    yield DoneEvent(text=full_text, meta=meta)


def _safe_json(raw: str) -> dict:
    try:
        value = json.loads(raw or "{}")
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        return {}
