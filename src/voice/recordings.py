"""Lưu ghi âm của cuộc gọi theo khóa {session_id}/{turn:03d}_{role}.{ext}.

RECORDINGS_STORAGE=file ghi ra recordings_dir; =db lưu vào bảng recording_blobs (host không có ổ đĩa bền).
"""

from __future__ import annotations

import re
from pathlib import Path

from src.config import get_settings

_SAFE = re.compile(r"[^A-Za-z0-9_-]")

MEDIA_TYPES = {"wav": "audio/wav", "mp3": "audio/mpeg", "webm": "audio/webm", "ogg": "audio/ogg", "m4a": "audio/mp4"}


def recordings_root() -> Path:
    return Path(get_settings().recordings_dir)


def save_recording(session_id: str, turn_index: int, role: str, data: bytes, ext: str) -> str:
    """Lưu ghi âm, trả về khóa tương đối (lưu vào messages.audio_path)."""
    safe_session = _SAFE.sub("", session_id)[:80]
    relative = (Path(safe_session) / f"{turn_index:03d}_{role}.{ext}").as_posix()
    if get_settings().recordings_storage == "db":
        from src.db.session import get_session_factory
        from src.models.entities import RecordingBlob

        with get_session_factory()() as session:
            session.merge(RecordingBlob(path=relative, data=data))
            session.commit()
        return relative
    path = recordings_root() / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return relative


def resolve_recording(relative: str) -> Path | None:
    root = recordings_root().resolve()
    path = (root / relative).resolve()
    if root not in path.parents or not path.exists():
        return None
    return path


def load_recording(relative: str) -> bytes | None:
    """Đọc ghi âm theo khóa, từ DB hoặc file tùy RECORDINGS_STORAGE."""
    if get_settings().recordings_storage == "db":
        from src.db.session import get_session_factory
        from src.models.entities import RecordingBlob

        with get_session_factory()() as session:
            blob = session.get(RecordingBlob, relative)
            return blob.data if blob else None
    path = resolve_recording(relative)
    return path.read_bytes() if path else None


def media_type_for(relative: str) -> str:
    return MEDIA_TYPES.get(relative.rsplit(".", 1)[-1], "application/octet-stream")


def extension_for_mime(mime: str) -> str:
    mime = (mime or "").lower()
    if "wav" in mime:
        return "wav"
    if "webm" in mime:
        return "webm"
    if "ogg" in mime:
        return "ogg"
    if "mp4" in mime or "m4a" in mime:
        return "m4a"
    if "mpeg" in mime or "mp3" in mime:
        return "mp3"
    return "bin"
