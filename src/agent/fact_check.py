"""Kiểm tra số liệu trong câu trả lời của agent so với kết quả tool.

- Mã căn không có trong kết quả tool của cuộc gọi → câu bị thay bằng câu an toàn (chặn bịa mã căn).
- Giá không khớp giá nào từng tra hoặc khách đã nói → chỉ ghi nhận `unverified_price` để đánh giá.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

UNIT_CODE_RE = re.compile(r"\b([A-Z]{1,3}\d{0,2}(?:\.\d{2})?-\d{4})\b")
MONEY_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(tỷ|tỉ|triệu)", re.IGNORECASE)
SAFE_SENTENCE = "Dạ thông tin căn này em cần kiểm tra lại trong bảng hàng ạ."
PRICE_TOLERANCE = 0.006  # cho phép làm tròn 2 chữ số thập phân của "x,yz tỷ"


@dataclass
class FactCheckResult:
    text: str
    blocked_codes: list[str] = field(default_factory=list)
    unverified_prices: list[int] = field(default_factory=list)


def extract_money(text: str) -> list[int]:
    values = []
    for number, unit in MONEY_RE.findall(text):
        value = float(number.replace(",", "."))
        multiplier = 1_000_000_000 if unit.lower() in ("tỷ", "tỉ") else 1_000_000
        values.append(round(value * multiplier))
    return values


def _price_known(value: int, known: set[int]) -> bool:
    return any(abs(value - k) <= max(k * PRICE_TOLERANCE, 10_000_000) for k in known)


def check_sentence(sentence: str, known_codes: set[str], known_prices: set[int]) -> FactCheckResult:
    result = FactCheckResult(text=sentence)
    unknown_codes = [code for code in UNIT_CODE_RE.findall(sentence) if code not in known_codes]
    if unknown_codes:
        result.blocked_codes = unknown_codes
        result.text = SAFE_SENTENCE
        return result
    result.unverified_prices = [v for v in extract_money(sentence) if not _price_known(v, known_prices)]
    return result
