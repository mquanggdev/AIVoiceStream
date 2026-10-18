"""Truy vấn có cấu trúc trên bảng hàng (SQL). Đây là nguồn DUY NHẤT cho mã căn, giá, diện tích.

Mọi hàm trả về dict đã kèm sẵn dạng đọc (`*_spoken`) và dạng viết ngắn (`*_text`)
để agent dùng nguyên văn, không phải tự tính hay tự đọc số.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload

from src.core.spoken import format_money_text, money_to_words, unit_code_spoken
from src.core.text import normalize
from src.models.entities import Building, SalesPolicy, Subdivision, Unit
from src.retrieval.labels import (
    DIRECTION_KEYWORDS,
    DIRECTION_LABELS,
    FURNISHING_LABELS,
    HANDOVER_LABELS,
    POLICY_TYPE_LABELS,
    PRICE_TYPE_LABELS,
    STATUS_LABELS,
    UNIT_TYPE_LABELS,
    VIEW_KEYWORDS,
    VIEW_LABELS,
)

MAX_RESULTS = 5
UNIT_TYPE_ORDER = ["STUDIO", "1PN", "1PN+1", "2PN", "2PN+1", "3PN", "4PN", "DUPLEX", "PENTHOUSE", "SHOPHOUSE"]


def money_fields(vnd: int | None, prefix: str = "price") -> dict:
    if vnd is None:
        return {f"{prefix}_vnd": None, f"{prefix}_text": None, f"{prefix}_spoken": None}
    return {
        f"{prefix}_vnd": vnd,
        f"{prefix}_text": format_money_text(vnd),
        f"{prefix}_spoken": money_to_words(vnd),
    }


def view_codes_from_text(text: str | None) -> list[str]:
    if not text:
        return []
    value = normalize(text)
    if value in VIEW_LABELS:
        return [value]
    for keyword, code in VIEW_KEYWORDS:
        if keyword in value:
            return [code]
    return []


def direction_code_from_text(text: str | None) -> str | None:
    if not text:
        return None
    raw = text.strip().upper()
    if raw in DIRECTION_LABELS:
        return raw
    value = normalize(text)
    for keyword, code in DIRECTION_KEYWORDS.items():
        if keyword in value:
            return code
    return None


def unit_to_dict(unit: Unit, *, detail: bool = False) -> dict:
    data = {
        "unit_code": unit.unit_code,
        "unit_code_spoken": unit_code_spoken(unit.unit_code),
        "subdivision": unit.subdivision.name,
        "building": unit.building.code,
        "floor": unit.floor_label or unit.floor,
        "unit_type": unit.unit_type,
        "unit_type_label": UNIT_TYPE_LABELS.get(unit.unit_type, unit.unit_type),
        "area_net_m2": unit.area_net_m2,
        "balcony_direction": DIRECTION_LABELS.get(unit.balcony_direction or "", None),
        "views": [VIEW_LABELS.get(v, v) for v in unit.views or []],
        "corner_unit": unit.corner_unit,
        "status": STATUS_LABELS.get(unit.status, unit.status),
        **money_fields(unit.price_vnd),
        "price_type": PRICE_TYPE_LABELS.get(unit.price_type or "", None),
        "price_date": unit.price_date.isoformat() if unit.price_date else None,
    }
    if unit.price_vnd and unit.area_net_m2:
        data["price_per_m2_million"] = round(unit.price_vnd / unit.area_net_m2 / 1_000_000, 1)
    if detail:
        data.update(
            {
                "bedrooms": unit.bedrooms,
                "bathrooms": unit.bathrooms,
                "area_gross_m2": unit.area_gross_m2,
                "door_direction": DIRECTION_LABELS.get(unit.door_direction or "", None),
                "furnishing": FURNISHING_LABELS.get(unit.furnishing or "", unit.furnishing),
                "price_includes_vat": unit.price_includes_vat,
                "price_includes_maintenance_fee": unit.price_includes_maintenance,
                "building_floors": unit.building.num_floors,
                "subdivision_handover": HANDOVER_LABELS.get(unit.subdivision.handover_status, ""),
            }
        )
    return data


def _unit_query():
    return select(Unit).options(joinedload(Unit.subdivision), joinedload(Unit.building))


def get_unit(db: Session, unit_code: str) -> Unit | None:
    return db.scalar(_unit_query().where(Unit.unit_code == unit_code))


def search_units(
    db: Session,
    *,
    subdivision: Subdivision | None = None,
    building: Building | None = None,
    unit_type: str | None = None,
    budget_min: int | None = None,
    budget_max: int | None = None,
    area_min: float | None = None,
    area_max: float | None = None,
    floor_min: int | None = None,
    floor_max: int | None = None,
    view: str | None = None,
    balcony_direction: str | None = None,
    corner_only: bool = False,
    status: str = "available",
    sort: str = "price_asc",
    limit: int = 3,
) -> dict:
    conditions = []
    if subdivision is not None:
        conditions.append(Unit.subdivision_id == subdivision.id)
    if building is not None:
        conditions.append(Unit.building_id == building.id)
    if unit_type:
        conditions.append(Unit.unit_type == unit_type)
    if status and status != "any":
        conditions.append(Unit.status == status)
    if budget_min is not None:
        conditions.append(Unit.price_vnd >= budget_min)
    if budget_max is not None:
        conditions.append(Unit.price_vnd <= budget_max)
    if budget_min is not None or budget_max is not None or sort.startswith("price"):
        conditions.append(Unit.price_vnd.is_not(None))
    if area_min is not None:
        conditions.append(Unit.area_net_m2 >= area_min)
    if area_max is not None:
        conditions.append(Unit.area_net_m2 <= area_max)
    if floor_min is not None:
        conditions.append(Unit.floor >= floor_min)
    if floor_max is not None:
        conditions.append(Unit.floor <= floor_max)
    if balcony_direction:
        conditions.append(Unit.balcony_direction == balcony_direction)
    if corner_only:
        conditions.append(Unit.corner_unit.is_(True))

    order = {
        "price_asc": Unit.price_vnd.asc(),
        "price_desc": Unit.price_vnd.desc(),
        "area_desc": Unit.area_net_m2.desc(),
        "area_asc": Unit.area_net_m2.asc(),
        "floor_desc": Unit.floor.desc(),
        "floor_asc": Unit.floor.asc(),
    }.get(sort, Unit.price_vnd.asc())

    rows = list(db.scalars(_unit_query().where(*conditions).order_by(order, Unit.unit_code)).all())
    view_codes = view_codes_from_text(view)
    if view_codes:
        rows = [u for u in rows if any(code in (u.views or []) for code in view_codes)]

    limit = max(1, min(limit, MAX_RESULTS))
    prices = [u.price_vnd for u in rows if u.price_vnd]
    result = {
        "total_matches": len(rows),
        "returned": min(len(rows), limit),
        "units": [unit_to_dict(u) for u in rows[:limit]],
    }
    if prices:
        result["price_range"] = {"min": money_fields(min(prices), "min"), "max": money_fields(max(prices), "max")}
    return result


def subdivision_stats(db: Session, subdivision: Subdivision) -> list[dict]:
    """Thống kê theo loại căn, tính TỪ BẢNG HÀNG: số căn, số căn đang bán, khoảng diện tích, khoảng giá."""
    rows = db.execute(
        select(
            Unit.unit_type,
            func.count(Unit.id),
            func.sum(case((Unit.status == "available", 1), else_=0)),
            func.min(Unit.area_net_m2),
            func.max(Unit.area_net_m2),
        )
        .where(Unit.subdivision_id == subdivision.id)
        .group_by(Unit.unit_type)
    ).all()
    price_rows = db.execute(
        select(Unit.unit_type, func.min(Unit.price_vnd), func.max(Unit.price_vnd))
        .where(Unit.subdivision_id == subdivision.id, Unit.status == "available", Unit.price_vnd.is_not(None))
        .group_by(Unit.unit_type)
    ).all()
    prices = {row[0]: (row[1], row[2]) for row in price_rows}
    stats = []
    for unit_type, total, available, area_min, area_max in rows:
        entry = {
            "unit_type": unit_type,
            "unit_type_label": UNIT_TYPE_LABELS.get(unit_type, unit_type),
            "total_units": total,
            "available_units": int(available or 0),
            "area_net_m2_range": [round(area_min, 1), round(area_max, 1)],
        }
        if unit_type in prices:
            low, high = prices[unit_type]
            entry["available_price_from"] = money_fields(low, "from")
            entry["available_price_to"] = money_fields(high, "to")
        stats.append(entry)
    stats.sort(key=lambda e: UNIT_TYPE_ORDER.index(e["unit_type"]) if e["unit_type"] in UNIT_TYPE_ORDER else 99)
    return stats


def subdivision_to_dict(db: Session, subdivision: Subdivision, *, detail: bool = True) -> dict:
    data = {
        "slug": subdivision.slug,
        "name": subdivision.name,
        "developer": subdivision.developer,
        "parent_zone": subdivision.parent_zone,
        "design_style": subdivision.design_style,
        "handover_status": HANDOVER_LABELS.get(subdivision.handover_status, subdivision.handover_status),
        "handover_date": subdivision.handover_date,
    }
    if detail:
        buildings = db.scalars(
            select(Building).where(Building.subdivision_id == subdivision.id).order_by(Building.code)
        ).all()
        data.update(
            {
                "handover_standard": FURNISHING_LABELS.get(subdivision.handover_standard or "", None),
                "handover_standard_detail": subdivision.handover_standard_detail,
                "ownership": "sở hữu lâu dài" if subdivision.ownership == "long_term" else subdivision.ownership,
                "location": subdivision.location_text,
                "internal_amenities": subdivision.internal_amenities,
                "external_amenities": subdivision.external_amenities,
                "management_fee_per_m2_vnd": subdivision.management_fee_per_m2_vnd,
                "buildings": [
                    {"code": b.code, "floors": b.num_floors, "units_per_floor": b.units_per_floor} for b in buildings
                ],
                "unit_types": subdivision_stats(db, subdivision),
            }
        )
    return data


def list_subdivisions(
    db: Session,
    *,
    handover_status: str | None = None,
    unit_type: str | None = None,
    budget_max: int | None = None,
) -> list[dict]:
    subs = list(db.scalars(select(Subdivision).order_by(Subdivision.display_order)).all())
    if handover_status:
        subs = [s for s in subs if s.handover_status == handover_status]
    price_query = select(Unit.subdivision_id, func.min(Unit.price_vnd), func.count(Unit.id)).where(
        Unit.status == "available", Unit.price_vnd.is_not(None)
    )
    if unit_type:
        price_query = price_query.where(Unit.unit_type == unit_type)
    if budget_max is not None:
        price_query = price_query.where(Unit.price_vnd <= budget_max)
    cheapest = {row[0]: (row[1], row[2]) for row in db.execute(price_query.group_by(Unit.subdivision_id)).all()}
    out = []
    for sub in subs:
        entry = subdivision_to_dict(db, sub, detail=False)
        if sub.id in cheapest:
            low, count = cheapest[sub.id]
            entry["matching_available_units"] = count
            entry.update(money_fields(low, "cheapest"))
        elif unit_type or budget_max is not None:
            entry["matching_available_units"] = 0
        out.append(entry)
    if unit_type or budget_max is not None:
        out = [e for e in out if e.get("matching_available_units")] or out
    return out


def active_policies(db: Session, subdivision: Subdivision, *, policy_type: str | None = None, today: date | None = None) -> dict:
    today = today or date.today()
    query = select(SalesPolicy).where(SalesPolicy.subdivision_id == subdivision.id)
    if policy_type:
        query = query.where(SalesPolicy.policy_type == policy_type)
    policies = list(db.scalars(query.order_by(SalesPolicy.policy_id)).all())
    active, expired = [], 0
    for policy in policies:
        if (policy.valid_to and policy.valid_to < today) or (policy.valid_from and policy.valid_from > today):
            expired += 1
            continue
        active.append(
            {
                "title": policy.title,
                "type": POLICY_TYPE_LABELS.get(policy.policy_type, policy.policy_type),
                "content": policy.content,
                "discount_percent": policy.discount_percent,
                "valid_to": policy.valid_to.isoformat() if policy.valid_to else None,
            }
        )
    return {"subdivision": subdivision.name, "active_policies": active, "expired_or_not_started_count": expired}

