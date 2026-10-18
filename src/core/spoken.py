"""Chuyển văn bản viết thành văn nói tiếng Việt trước khi đưa vào TTS.

Ví dụ:
  "Căn R1.01-1205 giá 3,35 tỷ, 64,2 m²"  →
  "Căn tòa R một chấm không một, tầng mười hai, căn số không năm giá ba tỷ ba trăm năm mươi triệu,
   sáu mươi tư phẩy hai mét vuông"
"""

from __future__ import annotations

import re

DIGITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
LETTERS = {
    "A": "a", "B": "bê", "C": "xê", "D": "đê", "E": "e", "F": "ép", "G": "gờ", "H": "hát", "I": "i", "J": "giây",
    "K": "ca", "L": "lờ", "M": "em", "N": "en", "O": "o", "P": "pê", "Q": "quy", "R": "rờ", "S": "ét", "T": "tê",
    "U": "u", "V": "vê", "W": "vê kép", "X": "ích", "Y": "i dài", "Z": "dét",
}
UNIT_TYPES_SPOKEN = {
    "STUDIO": "studio",
    "1PN+1": "một phòng ngủ cộng một",
    "2PN+1": "hai phòng ngủ cộng một",
    "1PN": "một phòng ngủ",
    "2PN": "hai phòng ngủ",
    "3PN": "ba phòng ngủ",
    "4PN": "bốn phòng ngủ",
    "DUPLEX": "căn duplex",
    "PENTHOUSE": "căn penthouse",
    "SHOPHOUSE": "shophouse",
}
DIRECTIONS_SPOKEN = {
    "N": "Bắc", "S": "Nam", "E": "Đông", "W": "Tây",
    "NE": "Đông Bắc", "NW": "Tây Bắc", "SE": "Đông Nam", "SW": "Tây Nam",
}


# ── Đọc số ────────────────────────────────────────────────────────────────────


def _read_triple(n: int, full: bool) -> str:
    """Đọc số 0–999. `full=True` khi đứng sau một nhóm lớn hơn (cần 'không trăm', 'lẻ')."""
    hundreds, rest = divmod(n, 100)
    tens, units = divmod(rest, 10)
    words: list[str] = []
    if hundreds or full:
        words += [DIGITS[hundreds], "trăm"]
    if tens == 0:
        if units:
            if hundreds or full:
                words.append("lẻ")
            words.append(DIGITS[units])
    elif tens == 1:
        words.append("mười")
        if units == 5:
            words.append("lăm")
        elif units:
            words.append(DIGITS[units])
    else:
        words += [DIGITS[tens], "mươi"]
        if units == 1:
            words.append("mốt")
        elif units == 4:
            words.append("tư")
        elif units == 5:
            words.append("lăm")
        elif units:
            words.append(DIGITS[units])
    return " ".join(words)


def read_int(n: int) -> str:
    if n == 0:
        return "không"
    if n < 0:
        return "âm " + read_int(-n)
    if n >= 1_000_000_000:
        billions, rest = divmod(n, 1_000_000_000)
        head = read_int(billions) + " tỷ"
        return head if rest == 0 else f"{head} {_read_below_billion(rest, full=True)}"
    return _read_below_billion(n, full=False)


def _read_below_billion(n: int, full: bool) -> str:
    groups = [(1_000_000, "triệu"), (1_000, "nghìn"), (1, "")]
    words: list[str] = []
    started = full
    for size, name in groups:
        value, n = divmod(n, size)
        if value == 0:
            continue
        words.append(_read_triple(value, full=started))
        if name:
            words.append(name)
        started = True
    return " ".join(words)


def read_digits(value: str) -> str:
    return " ".join(DIGITS[int(ch)] for ch in value if ch.isdigit())


def read_decimal(value: str) -> str:
    """'64,2' / '64.2' → 'sáu mươi tư phẩy hai'; '2,05' → 'hai phẩy không năm'."""
    value = value.replace(".", ",")
    if "," not in value:
        return read_int(int(value))
    whole, frac = value.split(",", 1)
    frac = frac.rstrip("0")
    if not frac:
        return read_int(int(whole or "0"))
    frac_words = read_digits(frac) if frac.startswith("0") or len(frac) > 2 else read_int(int(frac))
    return f"{read_int(int(whole or '0'))} phẩy {frac_words}"


def money_to_words(vnd: int) -> str:
    """3_350_000_000 → 'ba tỷ ba trăm năm mươi triệu'. Làm tròn đến triệu."""
    millions = round(vnd / 1_000_000)
    billions, rest_millions = divmod(millions, 1000)
    parts: list[str] = []
    if billions:
        parts.append(f"{read_int(billions)} tỷ")
    if rest_millions:
        parts.append(f"{_read_triple(rest_millions, full=False)} triệu")
    if not parts:
        return f"{read_int(vnd)} đồng"
    return " ".join(parts)


def format_money_text(vnd: int) -> str:
    """Dạng viết ngắn gọn cho LLM: 3_350_000_000 → '3,35 tỷ'; 980_000_000 → '980 triệu'."""
    if vnd >= 1_000_000_000:
        text = f"{vnd / 1_000_000_000:.2f}".rstrip("0").rstrip(".")
        return text.replace(".", ",") + " tỷ"
    return f"{round(vnd / 1_000_000)} triệu"


def spell_code(code: str) -> str:
    """'R1.01' → 'rờ một chấm không một'; 'BE1' → 'bê e một'."""
    words: list[str] = []
    for part in re.findall(r"[A-Za-z]|\d+|\.", code):
        if part == ".":
            words.append("chấm")
        elif part.isdigit():
            words.append(read_digits(part) if len(part) > 1 and part.startswith("0") else read_int(int(part)))
        else:
            words.append(LETTERS.get(part.upper(), part))
    return " ".join(words)


def unit_code_spoken(unit_code: str) -> str:
    """'R1.01-1205' → 'tòa rờ một chấm không một, tầng mười hai, căn số không năm'."""
    match = re.fullmatch(r"(.+)-(\d{2})(\d{2})", unit_code)
    if not match:
        return spell_code(unit_code)
    building, floor, number = match.groups()
    return f"tòa {spell_code(building)}, tầng {read_int(int(floor))}, căn số {read_digits(number)}"


def phone_spoken(phone: str) -> str:
    """'0912345678' → 'không chín một hai, ba bốn năm, sáu bảy tám'."""
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        groups = [digits[:4], digits[4:7], digits[7:]]
    else:
        groups = [digits[i : i + 3] for i in range(0, len(digits), 3)]
    return ", ".join(read_digits(group) for group in groups)


# ── Chuẩn hóa toàn câu ───────────────────────────────────────────────────────

UNIT_CODE_RE = re.compile(r"(?:\b(?:tòa|toà)\s+)?\b([A-Z]{1,3}\d{0,2}(?:\.\d{2})?-\d{4})\b", re.IGNORECASE)
FLOOR_LABEL_RE = re.compile(r"\b(\d{1,2})A\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+84|0)(?:[\s.\-]?\d){9}(?!\d)")
MONEY_BILLION_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:tỷ|tỉ)\b", re.IGNORECASE)
MONEY_MILLION_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:triệu|tr)\b", re.IGNORECASE)
MONEY_FULL_RE = re.compile(r"(\d{1,3}(?:\.\d{3}){2,})\s*(?:đồng|vnđ|vnd|đ)?", re.IGNORECASE)
AREA_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:m²|m2|mét vuông)", re.IGNORECASE)
PERCENT_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*%")
QUARTER_RE = re.compile(r"\b(?:quý|Q)\s*([1-4])\s*[/\-]\s*(\d{4})\b", re.IGNORECASE)
MONTH_YEAR_RE = re.compile(r"\btháng\s*(\d{1,2})\s*[/\-]\s*(\d{4})\b", re.IGNORECASE)
UNIT_TYPE_RE = re.compile(r"\b(STUDIO|[1-4]PN\+1|[1-4]PN\+?|DUPLEX|PENTHOUSE|SHOPHOUSE)(?![\w+])", re.IGNORECASE)
DECIMAL_RE = re.compile(r"\b\d+[.,]\d+\b")
INT_RE = re.compile(r"\b\d+\b")
MARKDOWN_RE = re.compile(r"(\*\*|__|`|#+\s|^\s*[-*•]\s+)", re.MULTILINE)
CITATION_RE = re.compile(r"\[C\d+\]")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
ABBREVIATIONS = {
    r"\bCĐT\b": "chủ đầu tư",
    r"\bHĐMB\b": "hợp đồng mua bán",
    r"\bPN\b": "phòng ngủ",
    r"\bVAT\b": "thuế VAT",
    r"\bTP\.?\s?HCM\b": "thành phố Hồ Chí Minh",
}


def _number_value(raw: str) -> float:
    return float(raw.replace(",", "."))


def _unit_type_words(match: re.Match) -> str:
    raw = match.group(1).upper()
    if raw.endswith("+") and not raw.endswith("+1"):
        raw = raw + "1"
    return UNIT_TYPES_SPOKEN.get(raw, raw)


def to_spoken(text: str) -> str:
    """Áp dụng toàn bộ quy tắc chuẩn hóa văn nói. Idempotent với câu đã là chữ."""
    text = LINK_RE.sub(r"\1", text)
    text = CITATION_RE.sub("", text)
    text = MARKDOWN_RE.sub("", text)
    for pattern, replacement in ABBREVIATIONS.items():
        text = re.sub(pattern, replacement, text)

    text = UNIT_CODE_RE.sub(lambda m: unit_code_spoken(m.group(1).upper()), text)
    text = FLOOR_LABEL_RE.sub(lambda m: f"{read_int(int(m.group(1)))} A", text)
    text = PHONE_RE.sub(lambda m: phone_spoken(m.group(0).replace("+84", "0")), text)
    text = MONEY_FULL_RE.sub(lambda m: money_to_words(int(m.group(1).replace(".", ""))), text)
    text = MONEY_BILLION_RE.sub(lambda m: money_to_words(round(_number_value(m.group(1)) * 1_000_000_000)), text)
    text = MONEY_MILLION_RE.sub(lambda m: f"{read_decimal(m.group(1))} triệu", text)
    text = AREA_RE.sub(lambda m: f"{read_decimal(m.group(1))} mét vuông", text)
    text = PERCENT_RE.sub(lambda m: f"{read_decimal(m.group(1))} phần trăm", text)
    text = QUARTER_RE.sub(lambda m: f"quý {read_int(int(m.group(1)))} năm {read_int(int(m.group(2)))}", text)
    text = MONTH_YEAR_RE.sub(lambda m: f"tháng {read_int(int(m.group(1)))} năm {read_int(int(m.group(2)))}", text)
    text = UNIT_TYPE_RE.sub(_unit_type_words, text)
    text = DECIMAL_RE.sub(lambda m: read_decimal(m.group(0)), text)
    text = INT_RE.sub(lambda m: read_int(int(m.group(0))) if len(m.group(0)) < 13 else read_digits(m.group(0)), text)
    return re.sub(r"\s+", " ", text).strip()
