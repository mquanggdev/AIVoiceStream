"""Chuẩn hóa số điện thoại khách đọc bằng lời hoặc do STT nhận dạng."""

from __future__ import annotations

import re

from src.core.text import strip_accents

_WORD_DIGITS = {
    "khong": "0", "linh": "0", "le": "0",
    "mot": "1",
    "hai": "2",
    "ba": "3",
    "bon": "4", "tu": "4",
    "nam": "5", "lam": "5",
    "sau": "6",
    "bay": "7", "bai": "7",
    "tam": "8",
    "chin": "9",
}
VALID_MOBILE_RE = re.compile(r"^0(3[2-9]|5[2689]|7[06-9]|8[1-9]|9\d)\d{7}$")


def digits_from_speech(raw: str) -> str:
    """'không chín 12 ba bốn năm 678' → '0912345678'. Bỏ qua từ không phải chữ số."""
    text = strip_accents(raw.lower()).replace("+84", " 0 ")
    out: list[str] = []
    for token in re.findall(r"\d+|[a-z]+", text):
        if token.isdigit():
            out.append(token)
        elif token in _WORD_DIGITS:
            out.append(_WORD_DIGITS[token])
    digits = "".join(out)
    if digits.startswith("84") and len(digits) == 11:
        digits = "0" + digits[2:]
    return digits


def normalize_phone(raw: str) -> tuple[str | None, str | None]:
    """Trả về (số_chuẩn, lỗi). Lỗi là câu ngắn để agent đọc lại cho khách."""
    digits = digits_from_speech(raw)
    if len(digits) == 9 and not digits.startswith("0"):
        digits = "0" + digits
    if len(digits) < 10:
        return None, f"Số điện thoại mới có {len(digits)} chữ số, còn thiếu"
    if len(digits) > 10:
        return None, f"Số điện thoại có {len(digits)} chữ số, bị thừa"
    if not VALID_MOBILE_RE.match(digits):
        return None, "Đầu số điện thoại chưa đúng định dạng di động Việt Nam"
    return digits, None
