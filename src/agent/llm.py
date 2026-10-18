"""Lớp gọi LLM dạng stream có tool calling. Có bản giả lập cho test (không cần key)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Protocol

from src.ai.client import get_ai_client
from src.config import get_settings


@dataclass
class ToolCallDelta:
    index: int
    id: str | None = None
    name: str | None = None
    arguments: str = ""


@dataclass
class StreamChunk:
    content: str | None = None
    tool_calls: list[ToolCallDelta] = field(default_factory=list)
    finish_reason: str | None = None
    cost_usd: float | None = None  # OpenRouter trả ở chunk cuối khi bật include_usage
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class ChatModel(Protocol):
    name: str

    def stream(self, messages: list[dict], tools: list[dict] | None) -> AsyncIterator[StreamChunk]: ...


class OpenRouterChatModel:
    def __init__(self, model: str | None = None, temperature: float | None = None, max_tokens: int = 500):
        settings = get_settings()
        self.name = model or settings.llm_model
        self.temperature = settings.llm_temperature if temperature is None else temperature
        self.max_tokens = max_tokens

    async def stream(self, messages: list[dict], tools: list[dict] | None) -> AsyncIterator[StreamChunk]:
        client = get_ai_client()
        kwargs = {
            "model": self.name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        response = await client.chat.completions.create(**kwargs)
        async for chunk in response:
            usage = getattr(chunk, "usage", None)
            if usage is not None:
                yield StreamChunk(
                    cost_usd=getattr(usage, "cost", None),
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                )
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            delta = choice.delta
            calls = [
                ToolCallDelta(
                    index=tc.index if tc.index is not None else i,
                    id=tc.id,
                    name=tc.function.name if tc.function else None,
                    arguments=(tc.function.arguments or "") if tc.function else "",
                )
                for i, tc in enumerate(delta.tool_calls or [])
            ]
            yield StreamChunk(content=delta.content, tool_calls=calls, finish_reason=choice.finish_reason)


@dataclass
class ScriptedStep:
    """Một lần gọi LLM giả lập: hoặc trả text, hoặc gọi tool."""

    text: str = ""
    tool_calls: list[tuple[str, dict]] = field(default_factory=list)


class ScriptedChatModel:
    """LLM giả lập cho test: trả lần lượt từng bước đã định sẵn."""

    name = "scripted"

    def __init__(self, steps: list[ScriptedStep]):
        self.steps = list(steps)
        self.calls: list[list[dict]] = []

    async def stream(self, messages: list[dict], tools: list[dict] | None) -> AsyncIterator[StreamChunk]:
        import json

        self.calls.append(messages)
        step = self.steps.pop(0) if self.steps else ScriptedStep(text="Dạ vâng ạ.")
        if step.text:
            for piece in step.text.split(" "):
                yield StreamChunk(content=piece + " ")
        for index, (name, args) in enumerate(step.tool_calls):
            yield StreamChunk(
                tool_calls=[ToolCallDelta(index=index, id=f"call_{index}", name=name, arguments=json.dumps(args))]
            )
        yield StreamChunk(finish_reason="tool_calls" if step.tool_calls else "stop")
