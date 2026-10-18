"""Embedding qua OpenRouter cho knowledge chunks và câu hỏi."""

from __future__ import annotations

import logging

from src.ai.client import AINotConfiguredError, get_ai_client
from src.config import get_settings

logger = logging.getLogger(__name__)

BATCH_SIZE = 64


async def embed_texts(texts: list[str]) -> list[list[float]]:
    client = get_ai_client()
    model = get_settings().embedding_model
    vectors: list[list[float]] = []
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start : start + BATCH_SIZE]
        response = await client.embeddings.create(model=model, input=batch)
        vectors.extend(item.embedding for item in sorted(response.data, key=lambda item: item.index))
    return vectors


async def try_embed_query(text: str) -> list[float] | None:
    """Không có key hoặc lỗi mạng → None (tìm kiếm sẽ dùng BM25)."""
    try:
        return (await embed_texts([text]))[0]
    except AINotConfiguredError:
        return None
    except Exception as exc:  # noqa: BLE001 - embedding lỗi không được làm hỏng cuộc gọi
        logger.warning("query embedding failed: %s", type(exc).__name__)
        return None
