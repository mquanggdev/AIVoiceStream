"""Nhận diện tên phân khu / tòa / mã căn từ câu nói (chịu lỗi nhận dạng giọng nói).

Ví dụ: "dần pác" → the-zenpark, "zen park" → the-zenpark, "r 1 01" → R1.01, "R1011205" → R1.01-1205.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.text import compact, normalize
from src.models.entities import Building, DatasetVersion, Subdivision

FUZZY_THRESHOLD = 0.78
_GENERIC_PREFIXES = ("phan khu ", "khu ", "du an ", "the ", "toa ", "can ho ")


@dataclass(frozen=True)
class Match:
    slug: str
    name: str
    score: float
    matched: str


@dataclass(frozen=True)
class _Alias:
    slug: str
    name: str
    alias: str
    key: str  # compact form


def _strip_generic(value: str) -> str:
    value = normalize(value)
    changed = True
    while changed:
        changed = False
        for prefix in _GENERIC_PREFIXES:
            if value.startswith(prefix) and len(value) > len(prefix) + 2:
                value = value[len(prefix) :]
                changed = True
    return value


@lru_cache(maxsize=4)
def _subdivision_aliases(version_id: int, rows: tuple[tuple[str, str, tuple[str, ...]], ...]) -> tuple[_Alias, ...]:
    aliases: list[_Alias] = []
    for slug, name, alias_list in rows:
        candidates = {name, slug.replace("-", " "), *alias_list}
        for candidate in candidates:
            for form in {normalize(candidate), _strip_generic(candidate)}:
                key = form.replace(" ", "")
                if len(key) >= 3:
                    aliases.append(_Alias(slug, name, candidate, key))
    return tuple(aliases)


def _load_aliases(db: Session) -> tuple[_Alias, ...]:
    version_id = db.scalar(select(DatasetVersion.id).where(DatasetVersion.is_active.is_(True))) or 0
    rows = tuple(
        (s.slug, s.name, tuple(s.aliases or []))
        for s in db.scalars(select(Subdivision).order_by(Subdivision.display_order)).all()
    )
    return _subdivision_aliases(version_id, rows)


def resolve_subdivisions(db: Session, text: str, *, limit: int = 3) -> list[Match]:
    """Trả về các phân khu có thể đang được nhắc tới, điểm cao nhất trước."""
    if not text or not text.strip():
        return []
    query_compact = compact(text)
    query_words = normalize(text).split()
    best: dict[str, Match] = {}

    for alias in _load_aliases(db):
        score = 0.0
        if alias.key in query_compact:
            # alias dài khớp nguyên văn đáng tin hơn alias ngắn
            score = 0.9 + min(len(alias.key), 12) / 120
        else:
            windows = {
                "".join(query_words[i : i + n])
                for n in (1, 2, 3)
                for i in range(0, max(len(query_words) - n + 1, 0))
            }
            for window in windows:
                if abs(len(window) - len(alias.key)) > 4:
                    continue
                ratio = SequenceMatcher(None, window, alias.key).ratio()
                if ratio > score:
                    score = ratio
            if score < FUZZY_THRESHOLD:
                continue
            score *= 0.9  # khớp mờ thấp hơn khớp chính xác
        current = best.get(alias.slug)
        if current is None or score > current.score:
            best[alias.slug] = Match(alias.slug, alias.name, round(score, 3), alias.alias)
    return sorted(best.values(), key=lambda m: m.score, reverse=True)[:limit]


def resolve_subdivision(db: Session, text: str | None) -> tuple[Subdivision | None, list[Match]]:
    """Một phân khu chắc chắn nhất + danh sách ứng viên (để agent hỏi lại khi mơ hồ)."""
    if not text:
        return None, []
    matches = resolve_subdivisions(db, text)
    if not matches:
        return None, []
    top = matches[0]
    ambiguous = len(matches) > 1 and matches[1].score >= top.score - 0.03 and top.score < 0.95
    if ambiguous:
        return None, matches
    return db.scalar(select(Subdivision).where(Subdivision.slug == top.slug)), matches


def _code_key(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def resolve_building(db: Session, text: str | None) -> Building | None:
    if not text:
        return None
    key = _code_key(text.replace("toà", "").replace("tòa", ""))
    if not key:
        return None
    for building in db.scalars(select(Building)).all():
        if _code_key(building.code) == key:
            return building
    return None


def normalize_unit_code(db: Session, text: str) -> str | None:
    """Đưa mã căn khách/LLM đọc về dạng chuẩn `{tòa}-{tầng}{căn}` nếu tòa tồn tại."""
    raw = text.strip().upper().replace("TÒA", "").replace("CĂN", "")
    match = re.search(r"([A-Z]{1,3}\s*\d{0,2}(?:[.\s]?\d{2})?)\s*[-\s]?\s*(\d{4})\b", raw)
    if not match:
        return None
    building_part, number = match.groups()
    building = resolve_building(db, building_part)
    if building is None:
        return None
    return f"{building.code}-{number}"
