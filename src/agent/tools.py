"""Tool của agent: schema (OpenAI function calling) + thực thi trên DB."""

from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.phone import normalize_phone
from src.core.spoken import phone_spoken
from src.models.entities import Conversation, Customer
from src.retrieval import catalog
from src.retrieval.knowledge import search_knowledge
from src.retrieval.resolver import normalize_unit_code, resolve_building, resolve_subdivision

logger = logging.getLogger(__name__)

UNIT_TYPE_ENUM = ["STUDIO", "1PN", "1PN+1", "2PN", "2PN+1", "3PN", "4PN"]


@dataclass
class ToolContext:
    db: Session
    conversation: Conversation
    state: dict
    today: date = field(default_factory=date.today)
    # thu thập trong lượt hiện tại — dùng cho kiểm tra số liệu và ngữ cảnh lượt sau
    turn_facts: list[dict] = field(default_factory=list)

    def remember_units(self, units: list[dict]) -> None:
        codes = set(self.state.setdefault("known_unit_codes", []))
        prices = set(self.state.setdefault("known_prices", []))
        for unit in units:
            codes.add(unit["unit_code"])
            if unit.get("price_vnd"):
                prices.add(unit["price_vnd"])
        self.state["known_unit_codes"] = sorted(codes)[-300:]
        self.state["known_prices"] = sorted(prices)[-300:]

    def remember_prices(self, values: list[int | None]) -> None:
        prices = set(self.state.setdefault("known_prices", []))
        prices.update(v for v in values if v)
        self.state["known_prices"] = sorted(prices)[-300:]


def _fn(name: str, description: str, properties: dict, required: list[str] | None = None) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required or []},
        },
    }


TOOL_SCHEMAS: list[dict] = [
    _fn(
        "search_units",
        "Tìm căn hộ trong bảng hàng theo nhu cầu. Mặc định chỉ trả căn đang mở bán, sắp xếp giá tăng dần.",
        {
            "subdivision": {"type": "string", "description": "Tên phân khu đúng như khách nói, ví dụ 'Zenpark'"},
            "building": {"type": "string", "description": "Mã tòa, ví dụ 'R1.01'"},
            "unit_type": {"type": "string", "enum": UNIT_TYPE_ENUM},
            "budget_min_vnd": {"type": "integer", "description": "Ngân sách tối thiểu, VND"},
            "budget_max_vnd": {"type": "integer", "description": "Ngân sách tối đa, VND. 3 tỷ = 3000000000"},
            "area_min_m2": {"type": "number"},
            "area_max_m2": {"type": "number"},
            "floor_min": {"type": "integer"},
            "floor_max": {"type": "integer"},
            "view": {"type": "string", "description": "Ví dụ 'hồ Ngọc Trai', 'biển hồ', 'vườn Nhật', 'công viên'"},
            "balcony_direction": {"type": "string", "description": "Hướng ban công, ví dụ 'Đông Nam'"},
            "corner_only": {"type": "boolean", "description": "Chỉ căn góc"},
            "include_unavailable": {"type": "boolean", "description": "true nếu khách muốn xem cả căn đã bán/đặt"},
            "sort": {"type": "string", "enum": ["price_asc", "price_desc", "area_desc", "floor_desc"]},
            "limit": {"type": "integer", "minimum": 1, "maximum": 5},
        },
    ),
    _fn(
        "get_unit",
        "Tra chính xác một căn theo mã căn (giá, diện tích, hướng, view, trạng thái).",
        {"unit_code": {"type": "string", "description": "Mã căn, ví dụ 'R1.01-1205'"}},
        ["unit_code"],
    ),
    _fn(
        "get_subdivision",
        "Thông tin một phân khu: chủ đầu tư, bàn giao, tiêu chuẩn, tiện ích, các tòa, thống kê loại căn và khoảng giá căn đang bán.",
        {"name": {"type": "string", "description": "Tên phân khu như khách nói"}},
        ["name"],
    ),
    _fn(
        "list_subdivisions",
        "Danh sách phân khu, có thể lọc theo tình trạng bàn giao, loại căn, ngân sách; kèm giá căn rẻ nhất đang bán phù hợp.",
        {
            "handover_status": {"type": "string", "enum": ["handed_over", "under_construction"]},
            "unit_type": {"type": "string", "enum": UNIT_TYPE_ENUM},
            "budget_max_vnd": {"type": "integer"},
        },
    ),
    _fn(
        "compare_subdivisions",
        "So sánh 2 đến 3 phân khu.",
        {"names": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3}},
        ["names"],
    ),
    _fn(
        "get_sales_policy",
        "Chính sách bán hàng ĐANG HIỆU LỰC của một phân khu (lịch thanh toán, chiết khấu, hỗ trợ vay, quà tặng).",
        {
            "subdivision": {"type": "string"},
            "policy_type": {"type": "string", "enum": ["payment_schedule", "discount", "loan_support", "gift", "other"]},
        },
        ["subdivision"],
    ),
    _fn(
        "search_knowledge",
        "Tìm thông tin mô tả: tiện ích, trường học, vị trí, giao thông, thiết kế, pháp lý, quy trình mua, chi phí, cộng đồng.",
        {
            "query": {"type": "string", "description": "Câu hỏi ngắn gọn"},
            "subdivision": {"type": "string", "description": "Tên phân khu nếu câu hỏi về một khu cụ thể"},
        },
        ["query"],
    ),
    _fn(
        "save_customer_info",
        "Lưu tên và số điện thoại khách để chuyên viên liên hệ. CHỈ gọi sau khi đã đọc lại và khách xác nhận đúng.",
        {
            "full_name": {"type": "string"},
            "phone": {"type": "string", "description": "Số điện thoại dạng chữ số, ví dụ 0912345678"},
            "need_summary": {"type": "string", "description": "Tóm tắt nhu cầu khách trong 1-2 câu"},
            "interested_subdivision": {"type": "string"},
            "unit_type": {"type": "string", "enum": UNIT_TYPE_ENUM},
            "budget_max_vnd": {"type": "integer"},
            "preferred_contact_time": {"type": "string"},
        },
        ["full_name", "phone"],
    ),
]


def _subdivision_or_candidates(ctx: ToolContext, name: str | None) -> tuple[Any, dict | None]:
    if not name:
        return None, None
    sub, matches = resolve_subdivision(ctx.db, name)
    if sub is not None:
        return sub, None
    if matches:
        return None, {
            "ambiguous": True,
            "message": "Tên phân khu chưa rõ, hãy hỏi lại khách muốn nói khu nào",
            "candidates": [m.name for m in matches],
        }
    return None, {"not_found": True, "message": f"Không tìm thấy phân khu '{name}' trong dữ liệu"}


async def tool_search_units(ctx: ToolContext, **args) -> dict:
    sub, problem = _subdivision_or_candidates(ctx, args.get("subdivision"))
    if problem:
        return problem
    building = resolve_building(ctx.db, args.get("building")) if args.get("building") else None
    if args.get("building") and building is None:
        return {"not_found": True, "message": f"Không có tòa '{args['building']}' trong dữ liệu"}
    direction = catalog.direction_code_from_text(args.get("balcony_direction"))
    result = catalog.search_units(
        ctx.db,
        subdivision=sub,
        building=building,
        unit_type=args.get("unit_type"),
        budget_min=args.get("budget_min_vnd"),
        budget_max=args.get("budget_max_vnd"),
        area_min=args.get("area_min_m2"),
        area_max=args.get("area_max_m2"),
        floor_min=args.get("floor_min"),
        floor_max=args.get("floor_max"),
        view=args.get("view"),
        balcony_direction=direction,
        corner_only=bool(args.get("corner_only")),
        status="any" if args.get("include_unavailable") else "available",
        sort=args.get("sort") or "price_asc",
        limit=args.get("limit") or 3,
    )
    if result["total_matches"] == 0 and args.get("budget_max_vnd"):
        relaxed = catalog.search_units(
            ctx.db, subdivision=sub, building=building, unit_type=args.get("unit_type"), limit=2
        )
        result["note"] = "Không có căn trong ngân sách; đây là các căn rẻ nhất đang bán cùng điều kiện"
        result["closest_options"] = relaxed["units"]
        ctx.remember_units(relaxed["units"])
    ctx.remember_units(result["units"])
    if "price_range" in result:
        ctx.remember_prices([result["price_range"]["min"]["min_vnd"], result["price_range"]["max"]["max_vnd"]])
    return result


async def tool_get_unit(ctx: ToolContext, unit_code: str) -> dict:
    code = normalize_unit_code(ctx.db, unit_code) or unit_code.strip().upper()
    unit = catalog.get_unit(ctx.db, code)
    if unit is None:
        return {"not_found": True, "message": f"Không có căn mã '{unit_code}' trong bảng hàng"}
    data = catalog.unit_to_dict(unit, detail=True)
    ctx.remember_units([data])
    return data


async def tool_get_subdivision(ctx: ToolContext, name: str) -> dict:
    sub, problem = _subdivision_or_candidates(ctx, name)
    if problem:
        return problem
    data = catalog.subdivision_to_dict(ctx.db, sub)
    prices = []
    for entry in data.get("unit_types", []):
        prices += [entry.get("available_price_from", {}).get("from_vnd"), entry.get("available_price_to", {}).get("to_vnd")]
    ctx.remember_prices(prices)
    _remember_profile(ctx, interested_subdivision=sub.name)
    return data


async def tool_list_subdivisions(ctx: ToolContext, **args) -> dict:
    items = catalog.list_subdivisions(
        ctx.db,
        handover_status=args.get("handover_status"),
        unit_type=args.get("unit_type"),
        budget_max=args.get("budget_max_vnd"),
    )
    ctx.remember_prices([item.get("cheapest_vnd") for item in items])
    return {"subdivisions": items}


async def tool_compare_subdivisions(ctx: ToolContext, names: list[str]) -> dict:
    out = []
    for name in names[:3]:
        sub, problem = _subdivision_or_candidates(ctx, name)
        if problem:
            out.append({"input": name, **problem})
            continue
        data = catalog.subdivision_to_dict(ctx.db, sub)
        data.pop("buildings", None)
        out.append(data)
        for entry in data.get("unit_types", []):
            ctx.remember_prices(
                [entry.get("available_price_from", {}).get("from_vnd"), entry.get("available_price_to", {}).get("to_vnd")]
            )
    return {"comparison": out}


async def tool_get_sales_policy(ctx: ToolContext, subdivision: str, policy_type: str | None = None) -> dict:
    sub, problem = _subdivision_or_candidates(ctx, subdivision)
    if problem:
        return problem
    return catalog.active_policies(ctx.db, sub, policy_type=policy_type, today=ctx.today)


async def tool_search_knowledge(ctx: ToolContext, query: str, subdivision: str | None = None) -> dict:
    sub_id = None
    if subdivision:
        sub, problem = _subdivision_or_candidates(ctx, subdivision)
        if problem and problem.get("ambiguous"):
            return problem
        sub_id = sub.id if sub else None
    results = await search_knowledge(ctx.db, query, subdivision_id=sub_id, top_k=3)
    for item in results:
        item["content"] = item["content"][:900]
        item.pop("score", None)
    return {"results": results} if results else {"not_found": True, "message": "Không có tài liệu phù hợp"}


async def tool_save_customer_info(ctx: ToolContext, full_name: str, phone: str, **args) -> dict:
    normalized, error = normalize_phone(phone)
    if error:
        return {"saved": False, "error": error, "heard": phone}
    db = ctx.db
    customer = db.scalar(select(Customer).where(Customer.phone == normalized))
    if customer is None:
        customer = Customer(phone=normalized, source="voice")
        db.add(customer)
    customer.full_name = full_name.strip() or customer.full_name
    if args.get("need_summary"):
        customer.need_summary = args["need_summary"].strip()
    if args.get("interested_subdivision"):
        sub, _ = resolve_subdivision(db, args["interested_subdivision"])
        customer.interested_subdivision = sub.name if sub else args["interested_subdivision"]
    if args.get("unit_type"):
        customer.preferred_unit_type = args["unit_type"]
    if args.get("budget_max_vnd"):
        customer.budget_max_vnd = int(args["budget_max_vnd"])
    if args.get("preferred_contact_time"):
        customer.preferred_contact_time = args["preferred_contact_time"]
    db.flush()
    ctx.conversation.customer_id = customer.id
    ctx.state["customer"] = {"saved": True, "full_name": customer.full_name, "phone": normalized, "id": customer.id}
    db.commit()
    return {"saved": True, "full_name": customer.full_name, "phone": normalized, "phone_spoken": phone_spoken(normalized)}


def _remember_profile(ctx: ToolContext, **values) -> None:
    profile = ctx.state.setdefault("profile", {})
    for key, value in values.items():
        if value:
            profile[key] = value


TOOL_HANDLERS: dict[str, Callable[..., Awaitable[dict]]] = {
    "search_units": tool_search_units,
    "get_unit": tool_get_unit,
    "get_subdivision": tool_get_subdivision,
    "list_subdivisions": tool_list_subdivisions,
    "compare_subdivisions": tool_compare_subdivisions,
    "get_sales_policy": tool_get_sales_policy,
    "search_knowledge": tool_search_knowledge,
    "save_customer_info": tool_save_customer_info,
}


async def execute_tool(ctx: ToolContext, name: str, raw_arguments: str | dict) -> dict:
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return {"error": f"Tool không tồn tại: {name}"}
    try:
        args = raw_arguments if isinstance(raw_arguments, dict) else json.loads(raw_arguments or "{}")
    except json.JSONDecodeError:
        return {"error": "Tham số tool không phải JSON hợp lệ"}
    args = {k: v for k, v in args.items() if v not in (None, "")}
    _remember_profile(
        ctx,
        unit_type=args.get("unit_type"),
        budget_max_vnd=args.get("budget_max_vnd"),
    )
    try:
        result = await handler(ctx, **args)
    except TypeError as exc:
        logger.warning("tool %s bad args %s: %s", name, args, exc)
        return {"error": f"Tham số không hợp lệ cho {name}"}
    except Exception:
        logger.exception("tool %s failed", name)
        ctx.db.rollback()
        return {"error": "Lỗi khi tra dữ liệu, hãy xin lỗi khách và đề nghị Sales hỗ trợ"}
    ctx.turn_facts.append({"tool": name, "args": args, "result": result})
    return result
