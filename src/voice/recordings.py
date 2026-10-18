"""Lưu file ghi âm của cuộc gọi: data/recordings/{session_id}/{turn:03d}_{role}.{ext}."""

from __future__ import annotations

import re
from pathlib import Path

from src.config import get_settings

_SAFE = re.compile(r"[^A-Za-z0-9_-]")


def recordings_root() -> Path:
    return Path(get_settings().recordings_dir)


def save_recording(session_id: str, turn_index: int, role: str, data: bytes, ext: str) -> str:
    """Ghi file, trả về đường dẫn tương đối so với recordings_root (lưu vào DB)."""
    safe_session = _SAFE.sub("", session_id)[:80]
    relative = Path(safe_session) / f"{turn_index:03d}_{role}.{ext}"
    path = recordings_root() / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return relative.as_posix()


def resolve_recording(relative: str) -> Path | None:
    root = recordings_root().resolve()
    path = (root / relative).resolve()
    if root not in path.parents or not path.exists():
        return None
    return path


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
