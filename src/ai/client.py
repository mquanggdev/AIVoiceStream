"""Client OpenAI-compatible trỏ tới OpenRouter (LLM, STT, TTS, embedding dùng chung một key)."""

from __future__ import annotations

from functools import lru_cache

from openai import AsyncOpenAI

from src.config import get_settings


class AINotConfiguredError(RuntimeError):
    """Chưa có OPENROUTER_API_KEY / LLM_API_KEY."""


@lru_cache
def get_ai_client() -> AsyncOpenAI:
    settings = get_settings()
    if not settings.ai_configured:
        raise AINotConfiguredError("Chưa cấu hình OPENROUTER_API_KEY trong .env")
    return AsyncOpenAI(
        api_key=settings.effective_api_key,
        base_url=settings.effective_base_url,
        timeout=settings.llm_timeout_seconds,
        max_retries=1,
        default_headers={
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        },
    )
