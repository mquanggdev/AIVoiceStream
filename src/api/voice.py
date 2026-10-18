"""API cuộc gọi voice. Trả về NDJSON stream: mỗi dòng là một sự kiện (audio, state, transcript...)."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from src.models.schemas import InterruptRequest, TextTurnRequest
from src.voice.pipeline import (
    VoiceDeps,
    default_deps,
    hangup_call,
    mark_interrupted,
    stream_end_call,
    stream_start_call,
    stream_turn,
    touch_call,
)

router = APIRouter(prefix="/voice", tags=["voice"])

MAX_AUDIO_BYTES = 10 * 1024 * 1024  # ~5 phút WAV 16kHz mono

_deps: VoiceDeps | None = None


def get_voice_deps() -> VoiceDeps:
    global _deps
    if _deps is None:
        _deps = default_deps()
    return _deps


def set_voice_deps(deps: VoiceDeps | None) -> None:
    """Dùng trong test để thay STT/TTS/LLM bằng bản giả lập."""
    global _deps
    _deps = deps


async def _ndjson(events: AsyncIterator[dict]) -> AsyncIterator[bytes]:
    async for event in events:
        yield (json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8")


def _stream(events: AsyncIterator[dict]) -> StreamingResponse:
    return StreamingResponse(
        _ndjson(events),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/calls", summary="Bắt đầu cuộc gọi, nhận câu chào")
async def start_call(deps: VoiceDeps = Depends(get_voice_deps)) -> StreamingResponse:
    return _stream(stream_start_call(deps))


@router.post("/turn", summary="Gửi một câu nói của khách (WAV), nhận câu trả lời dạng audio")
async def voice_turn(
    session_id: str = Form(...),
    audio: UploadFile = File(...),
    deps: VoiceDeps = Depends(get_voice_deps),
) -> StreamingResponse:
    data = await audio.read()
    if not data:
        raise HTTPException(status_code=422, detail="File âm thanh rỗng")
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="File âm thanh quá lớn")
    return _stream(stream_turn(deps, session_id, audio=data, mime=audio.content_type or "audio/wav"))


@router.post("/text-turn", summary="Gửi câu dạng text (dev/đánh giá), bỏ qua STT")
async def text_turn(request: TextTurnRequest, deps: VoiceDeps = Depends(get_voice_deps)) -> StreamingResponse:
    return _stream(stream_turn(deps, request.session_id, text=request.text, with_audio=request.with_audio))


@router.post("/interrupt", summary="Báo khách đã ngắt lời agent")
async def interrupt(request: InterruptRequest, deps: VoiceDeps = Depends(get_voice_deps)) -> dict:
    ok = mark_interrupted(deps, request.session_id, request.turn_index, request.played_segments)
    if not ok:
        raise HTTPException(status_code=404, detail="Cuộc gọi không tồn tại")
    return {"ok": True}


@router.post("/calls/{session_id}/end", summary="Kết thúc cuộc gọi, nhận câu tạm biệt")
async def end_call(session_id: str, deps: VoiceDeps = Depends(get_voice_deps)) -> StreamingResponse:
    return _stream(stream_end_call(deps, session_id))


@router.post("/calls/{session_id}/ping", summary="Heartbeat: trình duyệt báo cuộc gọi vẫn mở")
async def ping_call(session_id: str, deps: VoiceDeps = Depends(get_voice_deps)) -> dict:
    return {"active": touch_call(deps, session_id)}


@router.post("/calls/{session_id}/hangup", summary="Khách đóng tab/tải lại trang (navigator.sendBeacon)")
async def hangup(session_id: str, deps: VoiceDeps = Depends(get_voice_deps)) -> dict:
    if not hangup_call(deps, session_id):
        raise HTTPException(status_code=404, detail="Cuộc gọi không tồn tại")
    return {"ok": True}
