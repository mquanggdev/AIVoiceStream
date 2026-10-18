"""Kiểm tra một bộ data theo các quy tắc V1–V11 của docs/data_spec_v3.md."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date

from src.dataset.loader import Dataset

UNIT_TYPES = {"STUDIO", "1PN", "1PN+1", "2PN", "2PN+1", "3PN", "4PN", "DUPLEX", "PENTHOUSE", "SHOPHOUSE"}
STATUSES = {"available", "booked", "sold", "not_released", "unknown"}
PRICE_TYPES = {"cdt_list", "secondary_asking", "secondary_sold", "estimate"}
DIRECTIONS = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"}
HANDOVER_STATUSES = {"handed_over", "under_construction", "not_started", "unknown"}
AREA_RANGES = {
    "STUDIO": (20, 40), "1PN": (30, 55), "1PN+1": (40, 60), "2PN": (50, 85),
    "2PN+1": (55, 90), "3PN": (70, 130), "4PN": (100, 180),
}
FORBIDDEN_TEXT = re.compile(r"đang cập nhật|liên hệ|tư vấn ngay|hotline|(?<!\d)0\d{9}(?!\d)", re.IGNORECASE)
UNIT_CODE_RE = re.compile(r"^[A-Z0-9.]+-\d{4}$")


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, rule: str, message: str) -> None:
        self.errors.append(f"[{rule}] {message}")

    def warn(self, rule: str, message: str) -> None:
        self.warnings.append(f"[{rule}] {message}")


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(str(value)[:10])


def _as_int(value) -> int | None:
    if value in (None, ""):
        return None
    return int(float(value))


def validate_dataset(ds: Dataset, *, max_messages_per_rule: int = 20) -> ValidationReport:
    report = ValidationReport()
    seen_messages: Counter = Counter()

    def error(rule: str, message: str) -> None:
        seen_messages[rule] += 1
        if seen_messages[rule] <= max_messages_per_rule:
            report.error(rule, message)

    def warn(rule: str, message: str) -> None:
        seen_messages[rule] += 1
        if seen_messages[rule] <= max_messages_per_rule:
            report.warn(rule, message)

    sub_slugs = {s.get("subdivision_slug") for s in ds.subdivisions}
    if len(sub_slugs) != len(ds.subdivisions):
        error("ID", "subdivision_slug bị trùng")
    for sub in ds.subdivisions:
        slug = sub.get("subdivision_slug", "?")
        if not sub.get("name"):
            error("S1", f"{slug}: thiếu name")
        if not sub.get("aliases"):
            warn("S2", f"{slug}: chưa có aliases (agent voice sẽ khó nhận diện tên đọc sai)")
        if sub.get("handover_status") not in HANDOVER_STATUSES:
            error("S3", f"{slug}: handover_status không hợp lệ: {sub.get('handover_status')}")
        for key in ("internal_amenities", "external_amenities"):
            for item in sub.get(key) or []:
                if len(str(item).split()) > 8:
                    warn("S4", f"{slug}: tiện ích quá dài (>8 từ), có thể là câu văn: {item!r}")

    buildings = {}
    for building in ds.buildings:
        code = building.get("building_code")
        if code in buildings:
            error("ID", f"building_code bị trùng: {code}")
        buildings[code] = building
        if building.get("subdivision_slug") not in sub_slugs:
            error("V2", f"tòa {code}: subdivision_slug không tồn tại")

    unit_codes: Counter = Counter()
    for row in ds.units:
        code = row.get("unit_code", "")
        unit_codes[code] += 1
        if not UNIT_CODE_RE.match(code):
            error("ID", f"unit_code sai định dạng: {code!r}")
        building = buildings.get(row.get("building_code"))
        if building is None:
            error("V2", f"{code}: building_code {row.get('building_code')} không tồn tại")
        elif building.get("subdivision_slug") != row.get("subdivision_slug"):
            error("V2", f"{code}: subdivision_slug không khớp với tòa")
        floor = _as_int(row.get("floor"))
        if floor is None:
            error("V3", f"{code}: thiếu floor")
        elif building and building.get("num_floors") and floor > int(building["num_floors"]):
            error("V3", f"{code}: tầng {floor} > số tầng của tòa ({building['num_floors']})")
        unit_type = row.get("unit_type")
        if unit_type not in UNIT_TYPES:
            error("U1", f"{code}: unit_type không hợp lệ: {unit_type}")
        if row.get("status") not in STATUSES:
            error("U2", f"{code}: status không hợp lệ: {row.get('status')}")
        for key in ("door_direction", "balcony_direction"):
            if row.get(key) and row[key] not in DIRECTIONS:
                error("U3", f"{code}: {key} không hợp lệ: {row[key]}")
        try:
            area = float(row.get("area_net_m2") or 0)
        except ValueError:
            area = 0
        if area <= 0:
            error("U4", f"{code}: thiếu area_net_m2")
        elif unit_type in AREA_RANGES:
            low, high = AREA_RANGES[unit_type]
            if not low <= area <= high:
                warn("V4", f"{code}: diện tích {area} m² bất thường với {unit_type}")
        price = _as_int(row.get("price_vnd"))
        if price is not None:
            if row.get("price_type") not in PRICE_TYPES or not row.get("price_date"):
                error("V6", f"{code}: có giá nhưng thiếu price_type/price_date hợp lệ")
            if area > 0:
                per_m2 = price / area
                if not 20_000_000 <= per_m2 <= 200_000_000:
                    warn("V5", f"{code}: đơn giá {per_m2 / 1e6:.1f} triệu/m² bất thường")
            if row.get("status") == "sold" and row.get("price_type") == "cdt_list":
                price_date = _parse_date(row.get("price_date"))
                if price_date and (date.today() - price_date).days < 30:
                    warn("V7", f"{code}: căn đã bán nhưng có giá niêm yết CĐT mới")
        if not row.get("source_url") or not row.get("crawled_at"):
            error("V8", f"{code}: thiếu source_url/crawled_at")
    for code, count in unit_codes.items():
        if count > 1:
            error("V1", f"unit_code trùng {count} lần: {code}")

    for policy in ds.sales_policies:
        pid = policy.get("policy_id", "?")
        if policy.get("subdivision_slug") not in sub_slugs:
            error("V2", f"chính sách {pid}: subdivision_slug không tồn tại")
        valid_from, valid_to = _parse_date(policy.get("valid_from")), _parse_date(policy.get("valid_to"))
        if valid_from and valid_to and valid_to < valid_from:
            error("V10", f"chính sách {pid}: valid_to trước valid_from")

    docs_by_sub: dict[str | None, set[str]] = {}
    for doc in ds.knowledge_docs:
        did = doc.get("doc_id", "?")
        slug = doc.get("subdivision_slug")
        if slug is not None and slug not in sub_slugs:
            error("V2", f"doc {did}: subdivision_slug không tồn tại")
        docs_by_sub.setdefault(slug, set()).add(doc.get("topic"))
        if len(str(doc.get("content", "")).split()) < 40:
            warn("D1", f"doc {did}: nội dung quá ngắn")

    records = [("subdivision", s.get("subdivision_slug"), s) for s in ds.subdivisions]
    records += [("building", b.get("building_code"), b) for b in ds.buildings]
    records += [("policy", p.get("policy_id"), p) for p in ds.sales_policies]
    records += [("doc", d.get("doc_id"), d) for d in ds.knowledge_docs]
    for kind, rid, record in records:
        if not record.get("source_url") or not record.get("crawled_at"):
            error("V8", f"{kind} {rid}: thiếu source_url/crawled_at")
        for key, value in record.items():
            texts = value if isinstance(value, list) else [value]
            for text in texts:
                if isinstance(text, str) and key not in ("source_url", "crawled_at") and FORBIDDEN_TEXT.search(text):
                    error("V9", f"{kind} {rid}.{key}: chứa text cấm ({FORBIDDEN_TEXT.search(text).group(0)!r})")

    for slug in sub_slugs:
        topics = docs_by_sub.get(slug, set())
        for topic in ("overview", "amenities"):
            if topic not in topics:
                warn("V11", f"{slug}: thiếu doc {topic}")

    for rule, count in seen_messages.items():
        if count > max_messages_per_rule:
            report.warnings.append(f"[{rule}] … và {count - max_messages_per_rule} thông báo khác cùng loại")
    return report
