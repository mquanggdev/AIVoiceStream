"""Chuẩn hóa văn bản tiếng Việt cho tìm kiếm và so khớp."""

from __future__ import annotations

import re
import unicodedata

_NON_WORD = re.compile(r"[^a-z0-9\s]")
_SPACES = re.compile(r"\s+")

# Từ dừng tiếng Việt (đã bỏ dấu) thường gặp trong câu hỏi, không mang nghĩa tìm kiếm
STOPWORDS = {
    "a", "ah", "ak", "anh", "chi", "em", "minh", "toi", "ban", "cho", "hoi", "voi", "la", "va", "cua", "co", "khong",
    "nao", "gi", "the", "thi", "ma", "nhe", "nha", "a", "u", "o", "oi", "da", "vang", "duoc", "can", "muon", "biet",
    "xin", "giup", "hay", "nhung", "cac", "mot", "nay", "do", "kia", "ve", "tai", "o", "tren", "duoi", "trong", "ngoai",
    "bao", "nhieu", "khoang", "lam", "rat", "qua", "nhu", "sao", "the", "nhi", "dau", "nua", "roi", "se", "dang",
}


def strip_accents(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize(value: str) -> str:
    """Chữ thường, bỏ dấu, bỏ ký tự đặc biệt, gộp khoảng trắng."""
    value = strip_accents(value or "").lower()
    value = _NON_WORD.sub(" ", value)
    return _SPACES.sub(" ", value).strip()


def tokens(value: str, *, drop_stopwords: bool = True) -> list[str]:
    words = normalize(value).split()
    if drop_stopwords:
        words = [word for word in words if word not in STOPWORDS]
    return words


def compact(value: str) -> str:
    """Bỏ dấu và bỏ hết khoảng trắng — dùng so khớp tên bị STT tách chữ ("zen park" ~ "zenpark")."""
    return normalize(value).replace(" ", "")
