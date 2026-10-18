"""Điều phối cuộc gọi: chào → (khách nói → STT → agent → TTS từng câu)* → tạm biệt.

Mỗi hàm `stream_*` là async generator trả về các sự kiện dict; route sẽ gửi chúng dạng NDJSON.
Mọi lượt đều được lưu vào DB (Khách/AI) kèm file ghi âm và số đo độ trễ.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time
import uuid
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.agent.llm import ChatModel, OpenRouterChatModel
from src.agent.prompts import GREETING_TEXT, NOT_HEARD_TEXT, goodbye_text
from src.agent.runner import DoneEvent, FillerEvent, SentenceEvent, ToolCallEvent, build_history, run_agent_turn
from src.agent.tools import ToolContext
from src.config import get_settings
from src.core.spoken import to_spoken
from src.dataset.importer import current_dataset
from src.models.entities import Conversation, Message
from src.voice.recordings import extension_for_mime, save_recording
from src.voice.speech import (
    CachedTTS,
    OpenRouterSTT,
    OpenRouterTTS,
    SpeechToText,
    TextToSpeech,
    concat_audio,
    estimate_tts_cost,
    extension_for_audio_mime,
)

logger = logging.getLogger("voice.pipeline")


@dataclass
class VoiceDeps:
    stt: SpeechToText
    tts: CachedTTS
    model_factory: Callable[[], ChatModel]
    session_factory: Callable[[], Session]


_locks: dict[str, asyncio.Lock] = {}
_pending_interrupts: dict[tuple[str, int], int] = {}


def default_deps() -> VoiceDeps:
    from src.db.session import get_session_factory

    return VoiceDeps(
        stt=OpenRouterSTT(),
        tts=CachedTTS(OpenRouterTTS()),
        model_factory=OpenRouterChatModel,
        session_factory=get_session_factory(),
    )


def _now() -> datetime:
    return datetime.now(UTC)


def _lock(session_id: str) -> asyncio.Lock:
    return _locks.setdefault(session_id, asyncio.Lock())


def _audio_event(seq: int, audio: bytes, mime: str, *, filler: bool = False) -> dict:
    return {
        "type": "audio",
        "seq": seq,
        "filler": filler,
        "mime": mime,
        "data": base64.b64encode(audio).decode("ascii"),
    }


@dataclass
class _SpeechJob:
    seq: int
    text: str
    spoken: str
    task: asyncio.Task
    filler: bool = False
    started: float = field(default_factory=time.perf_counter)


async def _tts_or_none(tts: TextToSpeech | CachedTTS, text: str, cached: bool) -> bytes | None:
    try:
        if cached and isinstance(tts, CachedTTS):
            return await tts.synthesize_cached(text)
        return await tts.synthesize(text)
    except Exception as exc:  # noqa: BLE001 - TTS lỗi → client đọc bằng giọng trình duyệt
        logger.warning("TTS failed: %s", type(exc).__name__)
        return None


async def _speak_fixed(
    deps: VoiceDeps, db: Session, conversation: Conversation, turn_index: int, text: str, meta: dict
) -> AsyncIterator[dict]:
    """Phát một câu cố định (chào/tạm biệt/không nghe rõ) và lưu thành lượt AI."""
    spoken = to_spoken(text)
    started = time.perf_counter()
    audio = await _tts_or_none(deps.tts, spoken, cached=True)
    tts_ms = round((time.perf_counter() - started) * 1000)
    audio_path = None
    if audio:
        audio_path = save_recording(
            conversation.session_id, turn_index, "ai", audio, extension_for_audio_mime(deps.tts.mime)
        )
        yield _audio_event(0, audio, deps.tts.mime)
    else:
        yield {"type": "speak_text", "seq": 0, "text": spoken}
    db.add(
        Message(
            conversation_id=conversation.id,
            turn_index=turn_index,
            role="ai",
            content=text,
            audio_path=audio_path,
            meta={**meta, "spoken": spoken, "tts_ms": tts_ms, "tts_failed": audio is None, "tts_cached": True},
        )
    )
    conversation.last_activity_at = _now()
    db.commit()


async def stream_start_call(deps: VoiceDeps) -> AsyncIterator[dict]:
    settings = get_settings()
    with deps.session_factory() as db:
        dataset = current_dataset(db)
        conversation = Conversation(
            session_id=uuid.uuid4().hex,
            channel="voice",
            status="active",
            data_version=dataset.version if dataset else None,
            models={
                "stt": deps.stt.name,
                "llm": settings.llm_model,
                "tts": deps.tts.name,
                "tts_voice": getattr(deps.tts.inner, "voice", None),
            },
            state={},
            turn_count=0,
        )
        db.add(conversation)
        db.commit()
        yield {"type": "call", "session_id": conversation.session_id, "is_demo_data": bool(dataset and dataset.is_demo)}
        yield {"type": "state", "value": "speaking"}
        async for event in _speak_fixed(deps, db, conversation, 0, GREETING_TEXT, {"kind": "greeting"}):
            yield event
        yield {"type": "done", "turn_index": 0}


def _load_active(db: Session, session_id: str) -> Conversation | None:
    return db.scalar(select(Conversation).where(Conversation.session_id == session_id))


async def stream_turn(
    deps: VoiceDeps,
    session_id: str,
    *,
    audio: bytes | None = None,
    mime: str = "audio/wav",
    text: str | None = None,
    with_audio: bool = True,
) -> AsyncIterator[dict]:
    """Một lượt: khách nói (audio hoặc text) → agent → các câu trả lời (audio)."""
    async with _lock(session_id):
        with deps.session_factory() as db:
            conversation = _load_active(db, session_id)
            if conversation is None or conversation.status != "active":
                yield {"type": "error", "message": "Cuộc gọi không tồn tại hoặc đã kết thúc"}
                return
            async for event in _run_turn(deps, db, conversation, audio=audio, mime=mime, text=text, with_audio=with_audio):
                yield event


async def _run_turn(
    deps: VoiceDeps,
    db: Session,
    conversation: Conversation,
    *,
    audio: bytes | None,
    mime: str,
    text: str | None,
    with_audio: bool,
) -> AsyncIterator[dict]:
    turn_started = time.perf_counter()
    turn_index = conversation.turn_count + 1
    conversation.turn_count = turn_index
    conversation.last_activity_at = _now()

    # 1. Lời khách: lưu ghi âm + STT
    customer_audio_path = None
    stt_ms = 0
    stt_error = None
    if audio is not None:
        customer_audio_path = save_recording(
            conversation.session_id, turn_index, "customer", audio, extension_for_mime(mime)
        )
        stt_started = time.perf_counter()
        try:
            deps.stt.last_cost_usd = None
            text = await deps.stt.transcribe(audio, f"turn.{extension_for_mime(mime)}", mime)
        except Exception as exc:  # noqa: BLE001
            logger.warning("STT failed: %s", exc)
            stt_error = f"{type(exc).__name__}"
            text = ""
        stt_ms = round((time.perf_counter() - stt_started) * 1000)
    text = (text or "").strip()

    db.add(
        Message(
            conversation_id=conversation.id,
            turn_index=turn_index,
            role="customer",
            content=text,
            audio_path=customer_audio_path,
            meta={"stt_model": deps.stt.name if audio is not None else None, "stt_ms": stt_ms, "stt_error": stt_error,
                  "input": "audio" if audio is not None else "text", "audio_bytes": len(audio) if audio else 0,
                  "stt_cost_usd": getattr(deps.stt, "last_cost_usd", None) if audio is not None else None},
        )
    )
    db.commit()
    yield {"type": "transcript", "turn_index": turn_index, "text": text}

    if not text:
        yield {"type": "state", "value": "speaking"}
        async for event in _speak_fixed(deps, db, conversation, turn_index, NOT_HEARD_TEXT, {"kind": "not_heard"}):
            yield event
        yield {"type": "done", "turn_index": turn_index}
        return

    yield {"type": "state", "value": "thinking"}

    # 2. Agent + TTS song song theo từng câu
    history = build_history(
        list(
            db.scalars(
                select(Message)
                .where(Message.conversation_id == conversation.id, Message.turn_index < turn_index)
                .order_by(Message.id)
            ).all()
        ),
        get_settings().agent_history_turns,
    )
    state = dict(conversation.state or {})
    ctx = ToolContext(db=db, conversation=conversation, state=state)
    model = deps.model_factory()

    queue: asyncio.Queue = asyncio.Queue()
    seq_counter = 0

    async def produce() -> None:
        nonlocal seq_counter
        try:
            async for event in run_agent_turn(ctx, model, text, history):
                if isinstance(event, (SentenceEvent, FillerEvent)):
                    is_filler = isinstance(event, FillerEvent)
                    task = asyncio.create_task(
                        _tts_or_none(deps.tts, event.spoken, cached=is_filler) if with_audio else _none()
                    )
                    await queue.put(_SpeechJob(seq_counter, event.text, event.spoken, task, filler=is_filler))
                    seq_counter += 1
                else:
                    await queue.put(event)
        finally:
            await queue.put(None)

    producer = asyncio.create_task(produce())
    ai_audio_parts: list[bytes] = []
    filler_job: _SpeechJob | None = None
    filler_audio: bytes | None = None
    tts_timings: list[int] = []
    tts_failed = 0
    tts_chars = 0
    played_seq = -1
    done_event: DoneEvent | None = None
    first_audio_ms: int | None = None
    interrupted = False
    try:
        while True:
            item = await queue.get()
            if item is None:
                break
            if isinstance(item, _SpeechJob):
                audio_bytes = await item.task
                if audio_bytes and not (item.filler and isinstance(deps.tts, CachedTTS)):
                    tts_chars += len(item.spoken)
                tts_timings.append(round((time.perf_counter() - item.started) * 1000))
                if first_audio_ms is None:
                    first_audio_ms = round((time.perf_counter() - turn_started) * 1000)
                    yield {"type": "state", "value": "speaking"}
                if item.filler:
                    filler_job, filler_audio = item, audio_bytes
                elif audio_bytes:
                    ai_audio_parts.append(audio_bytes)
                if audio_bytes:
                    yield _audio_event(item.seq, audio_bytes, deps.tts.mime, filler=item.filler)
                else:
                    if with_audio:
                        tts_failed += 1
                    yield {"type": "speak_text", "seq": item.seq, "filler": item.filler, "text": item.spoken}
                played_seq = item.seq
            elif isinstance(item, ToolCallEvent):
                yield {"type": "tool", "name": item.name, "arguments": item.arguments}
            elif isinstance(item, DoneEvent):
                done_event = item
    except (asyncio.CancelledError, GeneratorExit):
        interrupted = True
        producer.cancel()
        raise
    finally:
        if not producer.done():
            producer.cancel()
        _save_ai_turn(
            db,
            conversation,
            turn_index,
            state,
            done_event,
            ai_audio_parts,
            filler_job,
            filler_audio,
            deps.tts.mime,
            meta_extra={
                "stt_ms": stt_ms,
                "tts_model": deps.tts.name,
                "tts_ms": tts_timings,
                "tts_failed": tts_failed,
                "tts_chars": tts_chars,
                "tts_cost_usd_est": estimate_tts_cost(deps.tts.name, tts_chars) if with_audio else None,
                "first_audio_ms": first_audio_ms,
                "turn_total_ms": round((time.perf_counter() - turn_started) * 1000),
                "interrupted": interrupted,
                "played_segments": played_seq + 1,
            },
        )
    yield {"type": "done", "turn_index": turn_index}


async def _none() -> None:
    return None


def _save_ai_turn(
    db: Session,
    conversation: Conversation,
    turn_index: int,
    state: dict,
    done_event: DoneEvent | None,
    audio_parts: list[bytes],
    filler_job: _SpeechJob | None,
    filler_audio: bytes | None,
    audio_mime: str,
    meta_extra: dict,
) -> None:
    session_id = conversation.session_id
    if filler_job is not None:
        ext = extension_for_audio_mime(audio_mime)
        filler_path = save_recording(session_id, turn_index, "ai_filler", filler_audio, ext) if filler_audio else None
        db.add(
            Message(
                conversation_id=conversation.id,
                turn_index=turn_index,
                role="ai",
                content=filler_job.text,
                audio_path=filler_path,
                meta={"is_filler": True, "spoken": filler_job.spoken},
            )
        )
    text = done_event.text if done_event else ""
    meta = dict(done_event.meta) if done_event else {"error": "turn_incomplete"}
    meta.update(meta_extra)
    pending = _pending_interrupts.pop((session_id, turn_index), None)
    if pending is not None:
        meta["interrupted"] = True
        meta["played_segments"] = pending
    merged = concat_audio(audio_parts, audio_mime) if audio_parts else b""
    audio_path = (
        save_recording(session_id, turn_index, "ai", merged, extension_for_audio_mime(audio_mime)) if merged else None
    )
    db.add(
        Message(
            conversation_id=conversation.id,
            turn_index=turn_index,
            role="ai",
            content=text,
            audio_path=audio_path,
            meta=meta,
        )
    )
    conversation.state = state
    conversation.last_activity_at = _now()
    db.commit()


def mark_interrupted(deps: VoiceDeps, session_id: str, turn_index: int, played_segments: int) -> bool:
    with deps.session_factory() as db:
        conversation = _load_active(db, session_id)
        if conversation is None:
            return False
        message = db.scalar(
            select(Message)
            .where(
                Message.conversation_id == conversation.id,
                Message.turn_index == turn_index,
                Message.role == "ai",
            )
            .order_by(Message.id.desc())
        )
        if message is None or (message.meta or {}).get("is_filler"):
            _pending_interrupts[(session_id, turn_index)] = played_segments
            return True
        message.meta = {**(message.meta or {}), "interrupted": True, "played_segments": played_segments}
        db.commit()
        return True


async def stream_end_call(deps: VoiceDeps, session_id: str) -> AsyncIterator[dict]:
    async with _lock(session_id):
        with deps.session_factory() as db:
            conversation = _load_active(db, session_id)
            if conversation is None:
                yield {"type": "error", "message": "Cuộc gọi không tồn tại"}
                return
            if conversation.status == "active":
                turn_index = conversation.turn_count + 1
                conversation.turn_count = turn_index
                yield {"type": "state", "value": "speaking"}
                async for event in _speak_fixed(deps, db, conversation, turn_index, goodbye_text(), {"kind": "goodbye"}):
                    yield event
                finish_call(db, conversation, "ended")
            yield {"type": "done", "ended": True}


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def finish_call(db: Session, conversation: Conversation, status: str, *, ended_at: datetime | None = None) -> None:
    """Chốt cuộc gọi. status: ended (khách bấm kết thúc) | closed (khách đóng/tải lại trang) | abandoned (mất kết nối)."""
    ended = ended_at or _now()
    conversation.status = status
    conversation.ended_at = ended
    conversation.duration_sec = max(0.0, round((ended - _aware(conversation.started_at)).total_seconds(), 1))
    db.commit()


def touch_call(deps: VoiceDeps, session_id: str) -> bool:
    """Heartbeat từ trình duyệt: cuộc gọi vẫn mở (khách có thể đang im lặng)."""
    with deps.session_factory() as db:
        conversation = _load_active(db, session_id)
        if conversation is None or conversation.status != "active":
            return False
        conversation.last_activity_at = _now()
        db.commit()
        return True


def hangup_call(deps: VoiceDeps, session_id: str) -> bool:
    """Khách đóng tab / F5 (sendBeacon): chốt ngay, không phát câu tạm biệt vì không còn ai nghe.

    Không chờ khóa của lượt đang chạy — lượt đó vẫn tự lưu khi stream bị hủy.
    """
    with deps.session_factory() as db:
        conversation = _load_active(db, session_id)
        if conversation is None:
            return False
        if conversation.status == "active":
            finish_call(db, conversation, "closed")
        return True


def sweep_stale_calls(db: Session, timeout_seconds: float) -> int:
    """Đóng các cuộc gọi không còn heartbeat/lượt nói quá `timeout_seconds` (mất mạng, sập trình duyệt...)."""
    cutoff = _now() - timedelta(seconds=timeout_seconds)
    closed = 0
    for conversation in db.scalars(select(Conversation).where(Conversation.status == "active")).all():
        last = _aware(conversation.last_activity_at)
        if last < cutoff:
            # thời lượng tính đến lần hoạt động cuối, không tính thời gian treo
            finish_call(db, conversation, "abandoned", ended_at=last)
            closed += 1
    return closed
