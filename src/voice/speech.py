"""STT / TTS qua OpenRouter, có bản giả lập cho test và cache cho câu cố định."""

from __future__ import annotations

import hashlib
import io
import logging
import re
import wave
from pathlib import Path
from typing import Protocol

from src.ai.client import get_ai_client
from src.config import get_settings

logger = logging.getLogger(__name__)


class SpeechToText(Protocol):
    name: str

    async def transcribe(self, audio: bytes, filename: str, mime: str) -> str: ...


class TextToSpeech(Protocol):
    name: str
    mime: str

    async def synthesize(self, text: str) -> bytes: ...


class OpenRouterSTT:
    last_cost_usd: float | None = None

    def __init__(self, model: str | None = None, language: str | None = None):
        settings = get_settings()
        self.name = model or settings.stt_model
        self.language = language or settings.stt_language

    async def transcribe(self, audio: bytes, filename: str, mime: str) -> str:
        client = get_ai_client()
        result = await client.audio.transcriptions.create(
            model=self.name,
            file=(filename, audio, mime),
            language=self.language,
        )
        usage = getattr(result, "usage", None)
        self.last_cost_usd = getattr(usage, "cost", None) if usage is not None else None
        return (getattr(result, "text", "") or "").strip()


class OpenRouterTTS:
    """TTS qua OpenRouter. Một số model (Gemini TTS) chỉ trả PCM thô → bọc thành WAV để trình duyệt phát được."""

    def __init__(self, model: str | None = None, voice: str | None = None, audio_format: str | None = None):
        settings = get_settings()
        self.name = model or settings.tts_model
        self.voice = voice or settings.tts_voice
        fmt = (audio_format or settings.tts_format).lower()
        if fmt == "auto":
            fmt = "pcm" if self.name.startswith("google/") else "mp3"
        self.format = fmt
        self.mime = "audio/wav" if fmt == "pcm" else "audio/mpeg"

    async def synthesize(self, text: str) -> bytes:
        client = get_ai_client()
        response = await client.audio.speech.create(
            model=self.name,
            voice=self.voice,
            input=text,
            response_format=self.format,
        )
        if self.format != "pcm":
            return response.content
        content_type = response.response.headers.get("content-type", "")
        match = re.search(r"rate=(\d+)", content_type)
        return pcm_to_wav(response.content, int(match.group(1)) if match else PCM_DEFAULT_RATE)


PCM_DEFAULT_RATE = 24_000

# Đơn giá TTS ước tính (USD / 1000 ký tự), đo thực tế qua OpenRouter ngày 2026-10-18.
# OpenRouter không trả chi phí TTS trong response nên dùng ước tính này để theo dõi.
TTS_USD_PER_1K_CHARS = {
    "elevenlabs/eleven-flash-v2.5": 0.020,
    "google/gemini-3.8-flash-tts": 0.0146,
}


def estimate_tts_cost(model: str, chars: int) -> float | None:
    rate = TTS_USD_PER_1K_CHARS.get(model)
    return round(rate * chars / 1000, 7) if rate is not None else None


def pcm_to_wav(pcm: bytes, sample_rate: int = PCM_DEFAULT_RATE) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm)
    return buffer.getvalue()


def concat_audio(parts: list[bytes], mime: str) -> bytes:
    """Ghép nhiều đoạn audio của một lượt AI thành một file. MP3 nối thẳng được; WAV phải ghép PCM rồi bọc lại."""
    if mime != "audio/wav":
        return b"".join(parts)
    frames: list[bytes] = []
    params = None
    for part in parts:
        try:
            with wave.open(io.BytesIO(part), "rb") as handle:
                params = params or handle.getparams()
                frames.append(handle.readframes(handle.getnframes()))
        except wave.Error:
            continue
    if params is None:
        return b""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setparams(params)
        handle.writeframes(b"".join(frames))
    return buffer.getvalue()


def extension_for_audio_mime(mime: str) -> str:
    return "wav" if mime == "audio/wav" else "mp3"


class CachedTTS:
    """Bọc một TTS: cache ra đĩa các câu cố định (chào, câu lót, tạm biệt) để phát ngay."""

    def __init__(self, inner: TextToSpeech, cache_dir: str | Path = "data/tts_cache"):
        self.inner = inner
        self.name = inner.name
        self.mime = inner.mime
        self.cache_dir = Path(cache_dir)

    def _path(self, text: str) -> Path:
        voice = getattr(self.inner, "voice", "")
        fmt = getattr(self.inner, "format", "")
        digest = hashlib.sha1(f"{self.inner.name}|{voice}|{fmt}|{text}".encode()).hexdigest()
        return self.cache_dir / f"{digest}.{extension_for_audio_mime(self.mime)}"

    async def synthesize(self, text: str) -> bytes:
        return await self.inner.synthesize(text)

    async def synthesize_cached(self, text: str) -> bytes:
        path = self._path(text)
        if path.exists():
            return path.read_bytes()
        audio = await self.inner.synthesize(text)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(audio)
        return audio


class FakeSTT:
    """STT giả lập: trả lần lượt các câu định sẵn (test không cần key)."""

    name = "fake-stt"

    def __init__(self, transcripts: list[str] | None = None):
        self.transcripts = list(transcripts or [])

    async def transcribe(self, audio: bytes, filename: str, mime: str) -> str:
        return self.transcripts.pop(0) if self.transcripts else ""


class FakeTTS:
    name = "fake-tts"
    mime = "audio/mpeg"

    def __init__(self) -> None:
        self.texts: list[str] = []

    async def synthesize(self, text: str) -> bytes:
        self.texts.append(text)
        return b"ID3" + hashlib.md5(text.encode()).digest()
