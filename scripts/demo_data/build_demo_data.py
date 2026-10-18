"""Sinh bộ DATA DEMO theo đặc tả docs/data_spec_v3.md.

Chạy:  python scripts/demo_data/build_demo_data.py [--out cleaned_data/demo_v3]

Tất định: cùng phiên bản script luôn sinh ra cùng dữ liệu (seed cố định),
nhờ vậy bộ câu hỏi đánh giá không bị lệch giữa các lần chạy.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from texts_extra import EXTRA  # noqa: E402
from texts_project import PROJECT_DOCS  # noqa: E402
from texts_subdivisions_a import DOCS_A  # noqa: E402
from texts_subdivisions_b import DOCS_B  # noqa: E402

DATASET_VERSION = "demo-v3.0.0"
SEED = "ocean-park-demo-v3"
CRAWLED_AT = "2026-10-12T09:00:00+07:00"
PODIUM_FLOORS = 2  # tầng 1-2 là thương mại/sảnh, căn hộ bắt đầu từ tầng 3
SKIP_FLOOR_LABELS = {13: "12A"}  # tầng thứ 13 được gọi là 12A

TYPE_BEDROOMS = {"STUDIO": 0, "1PN": 1, "1PN+1": 1, "2PN": 2, "2PN+1": 2, "3PN": 3, "4PN": 4}
TYPE_PRICE_FACTOR = {"STUDIO": 1.08, "1PN": 1.04, "1PN+1": 1.02, "2PN": 1.0, "2PN+1": 0.99, "3PN": 0.97, "4PN": 0.96}
VIEW_FACTOR = {
    "ho_ngoc_trai": 1.07,
    "bien_ho": 1.06,
    "vuon_nhat": 1.04,
    "ho_canh_quan": 1.03,
    "cong_vien": 1.03,
    "noi_khu": 1.0,
    "thanh_pho": 0.98,
}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E", "NE": "SW", "SW": "NE", "SE": "NW", "NW": "SE"}


# ── Cấu hình phân khu ─────────────────────────────────────────────────────────
# phase: secondary = đã bàn giao lâu, chỉ còn hàng thứ cấp
#        recent    = vừa bàn giao: phần lớn thứ cấp + một ít quỹ căn CĐT còn lại
#        primary   = đang xây dựng, bán theo bảng giá CĐT
#        primary_early = đang xây dựng, nhiều căn chưa mở bán

SUBDIVISIONS: list[dict] = [
    {
        "slug": "the-sapphire",
        "name": "The Sapphire",
        "aliases": ["Sapphire", "Sa phia", "Sáp phia", "Xa phia", "Sapphire 1", "Sapphire 2", "Sa-phia", "Saphia"],
        "parent_zone": None,
        "developer": "Vinhomes",
        "design_style": "Hiện đại",
        "handover_status": "handed_over",
        "handover_date": "2020-Q2",
        "handover_standard": "basic",
        "handover_standard_detail": "Sàn gỗ công nghiệp, tủ bếp trên dưới, bếp từ, hút mùi, thiết bị vệ sinh cơ bản; chưa gồm điều hòa và đồ rời",
        "ownership": "long_term",
        "location_text": "Cửa ngõ phía Bắc đại đô thị, gần trục Lý Thánh Tông; đi bộ 5–10 phút tới hồ Ngọc Trai",
        "internal_amenities": ["Bể bơi ngoài trời", "Bể bơi trong nhà", "Phòng gym", "Vườn Nhật mini", "Hồ cá koi", "Sân chơi trẻ em", "Sân thể thao đa năng", "Khu BBQ", "Shophouse tầng đế"],
        "external_amenities": ["Hồ Ngọc Trai", "Biển hồ Crystal Lagoon", "Vinschool", "VinUni", "Vinmec", "Vincom Mega Mall", "Xe buýt điện VinBus"],
        "phase": "secondary",
        "base_ppm": 58_000_000,
        "mgmt_fee_per_m2": 12_000,
        "buildings": [("S1.03", 29, 14, 6), ("S1.05", 29, 14, 6), ("S2.12", 30, 14, 6), ("S2.18", 30, 14, 6)],
        "types": {"STUDIO": (26, 33), "1PN": (38, 45), "1PN+1": (42, 48), "2PN": (55, 70), "3PN": (76, 92)},
        "corner_types": ["3PN", "2PN"],
        "mix": ["2PN", "1PN", "STUDIO", "1PN+1", "STUDIO", "2PN", "1PN"],
        "facades": [("SE", "cong_vien"), ("NW", "thanh_pho")],
        "view_upgrades": {"S2.18": (0, 15, "ho_ngoc_trai")},
    },
    {
        "slug": "the-zenpark",
        "name": "The Zenpark",
        "aliases": ["Zenpark", "Zen Park", "The Zen Park", "Dền pác", "Zen pắc", "Dần pác", "Phân khu Nhật", "Zen"],
        "parent_zone": "The Ocean View",
        "developer": "Vinhomes",
        "design_style": "Nhật Bản",
        "handover_status": "handed_over",
        "handover_date": "2021-Q2",
        "handover_standard": "full_built_in",
        "handover_standard_detail": "Sàn gỗ cao cấp, trần thạch cao, điều hòa, tủ bếp kèm bếp từ và hút mùi, thiết bị vệ sinh cao cấp, bình nóng lạnh, khóa điện tử",
        "ownership": "long_term",
        "location_text": "Trung tâm đại đô thị, kế cận đường Lý Thánh Tông 40m; vài phút đi bộ tới hồ Ngọc Trai",
        "internal_amenities": ["Công viên Nhật Bản 1ha", "Vườn thiền", "Hồ cá koi", "Cổng torii", "Bể bơi bốn mùa", "Bể bơi ngoài trời", "Gym trong nhà", "Gym ngoài trời", "Nhà đa năng", "Sân chơi trẻ em"],
        "external_amenities": ["Hồ Ngọc Trai", "Biển hồ Crystal Lagoon", "Vinschool", "Vinmec", "Vincom Mega Mall", "Xe buýt điện VinBus"],
        "phase": "secondary",
        "base_ppm": 68_000_000,
        "mgmt_fee_per_m2": 15_000,
        "buildings": [("R1.01", 30, 16, 6), ("R1.02", 30, 16, 6), ("R1.03", 30, 16, 6), ("R1.05", 30, 16, 6)],
        "types": {"STUDIO": (27, 31), "1PN": (41, 46), "1PN+1": (45, 50), "2PN": (59, 70), "2PN+1": (63, 72), "3PN": (76, 86)},
        "corner_types": ["3PN", "2PN+1"],
        "mix": ["2PN", "1PN", "STUDIO", "1PN+1", "2PN", "STUDIO", "1PN", "2PN+1"],
        "facades": [("SE", "vuon_nhat"), ("NW", "thanh_pho")],
        "view_upgrades": {"R1.01": (0, 12, "ho_ngoc_trai"), "R1.02": (0, 12, "ho_ngoc_trai")},
    },
    {
        "slug": "the-pavilion",
        "name": "The Pavilion",
        "aliases": ["Pavilion", "Pavillion", "Pa vi li ơn", "Pa-vi-li-on", "Pa vi lông", "Pavilông"],
        "parent_zone": "The Ocean View",
        "developer": "Vinhomes",
        "design_style": "Nhiệt đới nghỉ dưỡng",
        "handover_status": "handed_over",
        "handover_date": "2024-Q1",
        "handover_standard": "basic",
        "handover_standard_detail": "Tiêu chuẩn Sapphire+: sàn gỗ, tủ bếp, bếp từ, hút mùi, thiết bị vệ sinh, bình nóng lạnh, khóa điện tử, nhà thông minh cơ bản; chưa gồm điều hòa",
        "ownership": "long_term",
        "location_text": "Cụm The Ocean View, trung tâm đại đô thị; đi bộ 5–7 phút tới hồ Ngọc Trai",
        "internal_amenities": ["Bể bơi ngoài trời", "Đảo yoga", "Quảng trường trung tâm", "Vườn nhiệt đới", "Phòng gym", "Spa", "Sân chơi trẻ em", "Khu BBQ"],
        "external_amenities": ["Hồ Ngọc Trai", "Biển hồ Crystal Lagoon", "Vinschool", "VinUni", "Vinmec", "Vincom Mega Mall"],
        "phase": "secondary",
        "base_ppm": 62_000_000,
        "mgmt_fee_per_m2": 13_000,
        "buildings": [("P1", 30, 15, 6), ("P2", 30, 15, 6)],
        "types": {"STUDIO": (27, 34), "1PN": (36, 46), "2PN": (55, 72), "3PN": (78, 96)},
        "corner_types": ["3PN", "2PN"],
        "mix": ["2PN", "1PN", "STUDIO", "2PN", "1PN", "STUDIO"],
        "facades": [("SE", "ho_canh_quan"), ("NW", "thanh_pho")],
        "view_upgrades": {},
    },
    {
        "slug": "the-bayfront",
        "name": "The Bayfront",
        "aliases": ["Bayfront", "Bay Front", "Bây phron", "Bai phờ ront", "Bây front", "Phân khu Dubai"],
        "parent_zone": None,
        "developer": "Vinhomes",
        "design_style": "Dubai nhiệt đới",
        "handover_status": "under_construction",
        "handover_date": "2027-Q4",
        "handover_standard": "full_built_in",
        "handover_standard_detail": "Dự kiến: sàn gỗ, trần thạch cao, điều hòa, tủ bếp và thiết bị bếp, thiết bị vệ sinh, bình nóng lạnh, khóa điện tử",
        "ownership": "long_term",
        "location_text": "Phía Đông đại đô thị, gần biển hồ Crystal Lagoon; đi bộ 5–10 phút ra bãi cát",
        "internal_amenities": ["Bể bơi bốn mùa", "Bể bơi beach club", "Vườn nhiệt đới", "Phòng gym", "Spa", "Sân chơi trẻ em", "Sảnh phong cách khách sạn"],
        "external_amenities": ["Biển hồ Crystal Lagoon", "Hồ Ngọc Trai", "Vinschool", "VinUni", "Vinmec", "Vincom Mega Mall"],
        "phase": "primary",
        "base_ppm": 76_000_000,
        "mgmt_fee_per_m2": 16_000,
        "buildings": [("BF1", 35, 12, 6), ("BF2", 35, 12, 6), ("BF3", 35, 12, 6)],
        "types": {"1PN+1": (45, 50), "2PN": (60, 70), "2PN+1": (68, 76), "3PN": (85, 100)},
        "corner_types": ["3PN", "2PN+1"],
        "mix": ["2PN", "1PN+1", "2PN", "2PN+1", "1PN+1"],
        "facades": [("E", "bien_ho"), ("W", "noi_khu")],
        "view_upgrades": {},
    },
    {
        "slug": "the-zurich",
        "name": "The Zurich",
        "aliases": ["Zurich", "Zu rích", "Giu rích", "Duy rích", "Zurick", "Zu-rich", "Phân khu Thụy Sỹ", "Phân khu Thụy Sĩ"],
        "parent_zone": "The Metropolitan",
        "developer": "Vinhomes",
        "design_style": "Thụy Sỹ châu Âu",
        "handover_status": "handed_over",
        "handover_date": "2025-08",
        "handover_standard": "full_built_in",
        "handover_standard_detail": "Sàn gỗ, trần thạch cao, điều hòa, tủ bếp và thiết bị bếp, thiết bị vệ sinh cao cấp, bình nóng lạnh, khóa điện tử, nhà thông minh",
        "ownership": "long_term",
        "location_text": "Cụm The Metropolitan; đi bộ 5 phút tới Brighton College và Vinschool",
        "internal_amenities": ["Tháp đồng hồ", "Quảng trường Thụy Sỹ", "Hồ cảnh quan Geneva", "Bể bơi ngoài trời", "Phòng gym", "Spa", "Sân chơi trẻ em", "Vườn BBQ"],
        "external_amenities": ["Brighton College", "Vinschool", "Deway", "Hồ Ngọc Trai", "Vinmec", "Vincom Mega Mall", "Xe buýt điện VinBus"],
        "phase": "secondary",
        "base_ppm": 76_000_000,
        "mgmt_fee_per_m2": 16_000,
        "buildings": [("ZR1", 29, 16, 6), ("ZR2", 29, 16, 6), ("ZR3", 29, 16, 6)],
        "types": {"STUDIO": (27, 34), "1PN": (41, 47), "2PN": (56, 72), "2PN+1": (63, 75), "3PN": (85, 100)},
        "corner_types": ["3PN", "2PN+1"],
        "mix": ["2PN", "1PN", "STUDIO", "2PN", "2PN+1", "STUDIO", "1PN"],
        "facades": [("SE", "ho_canh_quan"), ("NW", "thanh_pho")],
        "view_upgrades": {},
    },
    {
        "slug": "the-beverly",
        "name": "The Beverly",
        "aliases": ["Beverly", "Bê vơ li", "Be ve ly", "Bê-vơ-ly", "Beverly Hills", "Phân khu Mỹ", "Bevely"],
        "parent_zone": "The Metropolitan",
        "developer": "Vinhomes",
        "design_style": "Phong cách Mỹ (American Glory Living)",
        "handover_status": "handed_over",
        "handover_date": "2026-Q3",
        "handover_standard": "full_built_in",
        "handover_standard_detail": "Sàn gỗ, trần thạch cao, điều hòa, tủ bếp và thiết bị bếp, thiết bị vệ sinh, bình nóng lạnh, khóa điện tử",
        "ownership": "long_term",
        "location_text": "Cụm The Metropolitan, phía Tây Bắc gần công viên hồ San Hô",
        "internal_amenities": ["Bể bơi Santa Monica", "Quảng trường Beverly", "Đài phun nước", "Vườn đọc sách", "Gym và xông hơi", "Game room", "Kid corner", "Sân chơi sắc màu"],
        "external_amenities": ["Hồ Ngọc Trai", "Biển hồ Crystal Lagoon", "Vinschool", "Deway", "Vinmec", "Vincom Mega Mall"],
        "phase": "recent",
        "base_ppm": 72_000_000,
        "mgmt_fee_per_m2": 15_000,
        "buildings": [("BE1", 32, 22, 8), ("BE2", 32, 18, 6), ("BE3", 32, 18, 6), ("BE4", 32, 18, 6)],
        "types": {"STUDIO": (28, 35), "1PN": (43, 48), "2PN": (54, 70), "2PN+1": (64, 75), "3PN": (81, 108)},
        "corner_types": ["3PN", "2PN+1"],
        "mix": ["2PN", "STUDIO", "1PN", "2PN", "STUDIO", "2PN+1", "1PN", "STUDIO"],
        "facades": [("SE", "cong_vien"), ("NW", "noi_khu")],
        "view_upgrades": {},
    },
    {
        "slug": "the-london",
        "name": "The London",
        "aliases": ["London", "Luân Đôn", "Lơn đơn", "Lôn đôn", "Lân đân", "Phân khu Anh"],
        "parent_zone": "The Metropolitan",
        "developer": "Vinhomes",
        "design_style": "Cổ điển Anh",
        "handover_status": "handed_over",
        "handover_date": "2026-Q3",
        "handover_standard": "full_built_in",
        "handover_standard_detail": "Sàn gỗ, trần thạch cao, điều hòa, tủ bếp và thiết bị bếp, thiết bị vệ sinh và nhà tắm, chiếu sáng, hệ thống cửa",
        "ownership": "long_term",
        "location_text": "Ba mặt đường Lý Thánh Tông, Hải Đăng 8 và Hải Đăng 5",
        "internal_amenities": ["Bể bơi Santa Monica 700m²", "Phòng gym", "Phòng giải trí", "Phòng karaoke", "Phòng dance", "Phòng trẻ em", "Sân thể thao", "Gym ngoài trời"],
        "external_amenities": ["Hồ Ngọc Trai", "Biển hồ Crystal Lagoon", "Vinschool", "Vinmec", "Vincom Mega Mall", "Cao tốc Hà Nội – Hải Phòng"],
        "phase": "recent",
        "base_ppm": 73_000_000,
        "mgmt_fee_per_m2": 15_000,
        "buildings": [("LD1", 29, 16, 6), ("LD2", 26, 16, 6), ("LD3", 30, 16, 6)],
        "types": {"STUDIO": (27, 36), "1PN": (37, 44), "2PN": (56, 65), "2PN+1": (63, 72), "3PN": (81, 99)},
        "corner_types": ["3PN", "2PN+1"],
        "mix": ["2PN", "1PN", "STUDIO", "2PN", "STUDIO", "2PN+1", "1PN"],
        "facades": [("SE", "noi_khu"), ("NW", "thanh_pho")],
        "view_upgrades": {"LD3": (0, 20, "ho_ngoc_trai")},
    },
    {
        "slug": "the-paris",
        "name": "The Paris",
        "aliases": ["Paris", "Pa ri", "Pa-ri", "Ba ri", "Phân khu Pháp", "Pari"],
        "parent_zone": "The Metropolitan",
        "developer": "Vinhomes",
        "design_style": "Cổ điển Pháp",
        "handover_status": "under_construction",
        "handover_date": "2027-Q1",
        "handover_standard": "full_built_in",
        "handover_standard_detail": "Dự kiến: sàn gỗ, trần thạch cao, điều hòa, tủ bếp kèm bếp từ, hút mùi và lò, thiết bị vệ sinh cao cấp, khóa điện tử",
        "ownership": "long_term",
        "location_text": "Cụm The Metropolitan, gần trục Lý Thánh Tông",
        "internal_amenities": ["Quảng trường tháp Eiffel", "Chòi nghỉ hoàng gia", "Vườn xích đu cổ tích", "Bể bơi ngoài trời", "Phòng gym", "Phòng yoga", "Phòng pilates", "Phòng làm việc chung", "Lounge âm nhạc"],
        "external_amenities": ["Hồ Ngọc Trai", "Biển hồ Crystal Lagoon", "Vinmec", "Vinschool", "Deway", "Vincom Mega Mall"],
        "phase": "primary",
        "base_ppm": 75_000_000,
        "mgmt_fee_per_m2": 16_000,
        "buildings": [("PR1", 30, 16, 6), ("PR3", 30, 16, 6), ("PR5", 30, 16, 6)],
        "types": {"STUDIO": (27, 31), "1PN": (42, 44), "1PN+1": (46, 50), "2PN": (61, 70), "2PN+1": (66, 75), "3PN": (84, 97)},
        "corner_types": ["3PN", "2PN+1"],
        "mix": ["2PN", "1PN", "STUDIO", "1PN+1", "2PN", "STUDIO", "2PN+1"],
        "facades": [("SE", "noi_khu"), ("NW", "thanh_pho")],
        "view_upgrades": {},
    },
    {
        "slug": "the-palma",
        "name": "The Palma",
        "aliases": ["Palma", "Pan ma", "Pal ma", "Lumiere Orient Pearl", "Lumière", "Lu mi e", "Pam ma"],
        "parent_zone": "Lumiere Orient Pearl",
        "developer": "Masterise Homes",
        "design_style": "Modern Luxury",
        "handover_status": "under_construction",
        "handover_date": "2027-Q3",
        "handover_standard": "full_built_in",
        "handover_standard_detail": "Hoàn thiện liền tường cao cấp, thiết bị nhập khẩu: sàn gỗ kỹ thuật, đá ốp lát, điều hòa, bếp nhập khẩu âm tủ, thiết bị vệ sinh cao cấp, khóa thông minh",
        "ownership": "long_term",
        "location_text": "Ba mặt tiền Biển Hồ 1, Biển Hồ 2 và Lý Thánh Tông; vài phút đi bộ tới biển hồ",
        "internal_amenities": ["Sảnh phong cách khách sạn", "Lounge cư dân", "Bể bơi tràn bờ", "Spa", "Gym và yoga", "Vườn trên cao", "Khu vui chơi trẻ em", "Thang máy riêng căn 3PN góc"],
        "external_amenities": ["Biển hồ Crystal Lagoon", "Hồ Ngọc Trai", "Vincom Mega Mall", "Vinmec", "Vinschool"],
        "phase": "primary",
        "base_ppm": 108_000_000,
        "mgmt_fee_per_m2": 30_000,
        "buildings": [("PA1", 32, 10, 5), ("PA2", 32, 10, 5)],
        "types": {"STUDIO": (28, 32), "1PN": (39, 42), "1PN+1": (46, 48), "2PN": (58, 64), "2PN+1": (66, 72), "3PN": (90, 110)},
        "corner_types": ["3PN", "2PN+1"],
        "mix": ["2PN", "1PN", "STUDIO", "1PN+1", "2PN", "1PN"],
        "facades": [("E", "bien_ho"), ("W", "thanh_pho")],
        "view_upgrades": {"PA1": (1, 10, "ho_ngoc_trai"), "PA2": (1, 10, "ho_ngoc_trai")},
    },
    {
        "slug": "masteri-waterfront",
        "name": "Masteri Waterfront",
        "aliases": ["Waterfront", "Masteri Waterfront", "Ma tơ ri", "Mát tơ ri oát tơ phron", "Oát tơ phron", "Masteri Ocean Park"],
        "parent_zone": "Masteri Collection",
        "developer": "Masterise Homes",
        "design_style": "Modern Luxury",
        "handover_status": "handed_over",
        "handover_date": "2024-Q4",
        "handover_standard": "full_built_in",
        "handover_standard_detail": "Sàn gỗ, trần thạch cao, điều hòa, tủ bếp kèm thiết bị bếp nhập khẩu, thiết bị vệ sinh cao cấp, bình nóng lạnh, khóa điện tử",
        "ownership": "long_term",
        "location_text": "Trái tim khu đô thị, tiếp giáp hồ Ngọc Trai, gần biển hồ Crystal Lagoon",
        "internal_amenities": ["Bể bơi ngoài trời", "Bể bơi bốn mùa", "Gym trong nhà", "Gym ngoài trời", "Spa", "Sân chơi trẻ em", "Sân thể thao", "Sảnh lounge 5 sao", "Vườn thượng uyển"],
        "external_amenities": ["Hồ Ngọc Trai", "Biển hồ Crystal Lagoon", "Vinmec", "Vinschool", "Deway", "Vincom Mega Mall"],
        "phase": "secondary",
        "base_ppm": 74_000_000,
        "mgmt_fee_per_m2": 22_000,
        "buildings": [("H1", 33, 14, 6), ("H2", 33, 14, 6), ("H3", 33, 14, 6)],
        "types": {"STUDIO": (25, 34), "1PN": (42, 48), "2PN": (54, 63), "2PN+1": (62, 70), "3PN": (74, 82)},
        "corner_types": ["3PN", "2PN+1"],
        "mix": ["2PN", "1PN", "STUDIO", "2PN", "STUDIO", "2PN+1", "1PN"],
        "facades": [("SE", "noi_khu"), ("NW", "thanh_pho")],
        "view_upgrades": {"H1": (0, 3, "ho_ngoc_trai"), "H2": (0, 3, "ho_ngoc_trai")},
    },
    {
        "slug": "masteri-lakeside",
        "name": "Masteri Lakeside",
        "aliases": ["Lakeside", "Masteri Lakeside", "Lếch sai", "Lake side", "Lết sai", "Mát tơ ri lếch sai"],
        "parent_zone": "Masteri Collection",
        "developer": "Masterise Homes",
        "design_style": "Modern Luxury",
        "handover_status": "under_construction",
        "handover_date": "2026-Q4",
        "handover_standard": "full_built_in",
        "handover_standard_detail": "Sàn gỗ, trần thạch cao, điều hòa, bếp và thiết bị bếp nhập khẩu, thiết bị vệ sinh cao cấp, khóa thông minh",
        "ownership": "long_term",
        "location_text": "Giao điểm đường Lý Thánh Tông và Đại Tây Dương; phía Tây Nam giáp đường Biển Hồ",
        "internal_amenities": ["Bể bơi ngoài trời", "Bể bơi bốn mùa", "Phòng gym", "Spa", "Khu vui chơi trẻ em", "Vườn thư giãn", "Lounge cư dân", "Hồ điều hòa"],
        "external_amenities": ["Hồ Ngọc Trai", "Biển hồ Crystal Lagoon", "Vincom Mega Mall", "Vinmec", "Phố thương mại Biển Hồ"],
        "phase": "primary",
        "base_ppm": 82_000_000,
        "mgmt_fee_per_m2": 22_000,
        "buildings": [("ML1", 30, 14, 6), ("ML2", 30, 14, 6)],
        "types": {"STUDIO": (25, 27), "1PN+1": (45, 47), "2PN": (61, 64), "2PN+1": (64, 67), "3PN": (82, 96)},
        "corner_types": ["3PN", "2PN+1"],
        "mix": ["2PN", "1PN+1", "STUDIO", "2PN", "STUDIO", "2PN+1", "1PN+1"],
        "facades": [("SE", "ho_canh_quan"), ("NW", "thanh_pho")],
        "view_upgrades": {},
    },
    {
        "slug": "the-senique-hanoi",
        "name": "The Senique Hanoi",
        "aliases": ["Senique", "The Senique", "Sê ních", "Xê ních", "Senique Hà Nội", "Sơ ních", "CapitaLand"],
        "parent_zone": None,
        "developer": "CapitaLand Development",
        "design_style": "Modern Luxury Compound",
        "handover_status": "under_construction",
        "handover_date": "2027-Q2",
        "handover_standard": "full_built_in",
        "handover_standard_detail": "Hoàn thiện liền tường cao cấp: sàn gỗ, đá ốp lát, điều hòa, bếp và thiết bị nhập khẩu, thiết bị vệ sinh cao cấp, khóa thông minh",
        "ownership": "long_term",
        "location_text": "Trái tim khu đô thị, mô hình compound khép kín, gần đường Lý Thánh Tông",
        "internal_amenities": ["Bể bơi ngoài trời 50m", "Gym và xông hơi", "Spa", "Khu vui chơi trẻ em", "Vườn cảnh quan", "Sảnh lounge", "Hầm đỗ xe thông minh", "An ninh compound"],
        "external_amenities": ["Hồ Ngọc Trai", "Biển hồ Crystal Lagoon", "Vinmec", "Vincom Mega Mall", "Trường học trong khu"],
        "phase": "primary_early",
        "base_ppm": 96_000_000,
        "mgmt_fee_per_m2": 32_000,
        "buildings": [("SQ1", 37, 12, 6), ("SQ2", 36, 12, 6)],
        "types": {"1PN": (42, 46), "2PN": (54, 81), "3PN": (83, 108), "4PN": (120, 135)},
        "corner_types": ["4PN", "3PN"],
        "mix": ["2PN", "1PN", "2PN", "3PN", "1PN"],
        "facades": [("SE", "ho_canh_quan"), ("NW", "noi_khu")],
        "view_upgrades": {},
    },
]

# Chính sách bán hàng demo (valid_to trước 2026-10-14 = đã hết hạn, dùng để test lọc hiệu lực)
SALES_POLICIES: list[dict] = [
    {"subdivision_slug": "the-sapphire", "policy_type": "other", "title": "Hỗ trợ thủ tục sang tên thứ cấp",
     "content": "Ban quản lý và đối tác pháp lý hỗ trợ miễn phí kiểm tra hồ sơ căn hộ, hướng dẫn thủ tục công chứng và sang tên cho giao dịch mua bán lại trong phân khu. Áp dụng cho giao dịch thực hiện qua kênh tư vấn chính thức.",
     "valid_from": "2026-07-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-sapphire", "policy_type": "discount", "title": "Ưu đãi phí dịch vụ năm 2025",
     "content": "Miễn 6 tháng phí dịch vụ quản lý cho khách hàng nhận chuyển nhượng căn hộ trong năm 2025.",
     "discount_percent": None, "valid_from": "2025-01-01", "valid_to": "2025-12-31"},
    {"subdivision_slug": "the-zenpark", "policy_type": "loan_support", "title": "Gói vay mua nhà thứ cấp liên kết ngân hàng",
     "content": "Ngân hàng đối tác hỗ trợ vay tối đa 70% giá trị căn hộ thứ cấp, thời hạn tối đa 30 năm, lãi suất ưu đãi cố định 12 tháng đầu theo biểu lãi suất của ngân hàng tại thời điểm giải ngân. Hồ sơ được thẩm định trong 5 ngày làm việc.",
     "valid_from": "2026-08-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-zenpark", "policy_type": "gift", "title": "Tặng gói vệ sinh và bảo dưỡng căn hộ",
     "content": "Khách hàng hoàn tất giao dịch mua lại căn hộ qua kênh tư vấn chính thức được tặng gói vệ sinh công nghiệp và bảo dưỡng điều hòa một lần.",
     "valid_from": "2026-09-01", "valid_to": "2026-11-30"},
    {"subdivision_slug": "the-pavilion", "policy_type": "loan_support", "title": "Hỗ trợ vay 70% cho căn hộ thứ cấp",
     "content": "Ngân hàng đối tác cho vay tối đa 70% giá trị căn hộ, thời hạn tối đa 30 năm, ân hạn nợ gốc 6 tháng đầu.",
     "valid_from": "2026-06-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-pavilion", "policy_type": "discount", "title": "Chiết khấu bàn giao quý 1/2024",
     "content": "Chiết khấu 2% cho khách hàng nhận bàn giao đúng hạn trong quý 1 năm 2024.",
     "discount_percent": 2.0, "valid_from": "2024-01-01", "valid_to": "2024-03-31"},
    {"subdivision_slug": "the-bayfront", "policy_type": "payment_schedule", "title": "Lịch thanh toán tiêu chuẩn The Bayfront",
     "content": "Đặt cọc 100.000.000 đồng.\nĐợt 1: ký văn bản thỏa thuận trong 7 ngày kể từ đặt cọc, thanh toán 10% giá trị căn hộ.\nĐợt 2: ký hợp đồng mua bán, thanh toán 10%.\nĐợt 3 đến đợt 6: mỗi 3 tháng thanh toán 7,5%.\nĐợt 7: nhận bàn giao, thanh toán 45% cùng 2% kinh phí bảo trì.\nĐợt 8: nhận sổ hồng, thanh toán 5%.",
     "valid_from": "2026-09-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-bayfront", "policy_type": "discount", "title": "Chiết khấu thanh toán sớm The Bayfront",
     "content": "Khách hàng thanh toán sớm 95% giá trị căn hộ trong vòng 30 ngày kể từ ký hợp đồng mua bán được chiết khấu 9% trên giá bán trước VAT.",
     "discount_percent": 9.0, "valid_from": "2026-09-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-bayfront", "policy_type": "loan_support", "title": "Hỗ trợ lãi suất 0% 18 tháng",
     "content": "Ngân hàng đối tác cho vay tối đa 70% giá trị căn hộ. Chủ đầu tư hỗ trợ lãi suất 0% và ân hạn nợ gốc trong 18 tháng kể từ ngày giải ngân đầu tiên hoặc đến khi bàn giao, tùy thời điểm nào đến trước.",
     "valid_from": "2026-09-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-zurich", "policy_type": "other", "title": "Hỗ trợ chuyển nhượng hợp đồng",
     "content": "Hỗ trợ khách hàng làm thủ tục chuyển nhượng hợp đồng mua bán có xác nhận của chủ đầu tư cho các căn chưa cấp sổ hồng.",
     "valid_from": "2026-01-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-beverly", "policy_type": "discount", "title": "Ưu đãi quỹ căn cuối The Beverly",
     "content": "Áp dụng cho các căn còn lại trong quỹ hàng của chủ đầu tư: chiết khấu 5% trên giá bán trước VAT cho khách hàng thanh toán 70% trong 15 ngày kể từ ký hợp đồng.",
     "discount_percent": 5.0, "valid_from": "2026-09-15", "valid_to": "2026-12-15"},
    {"subdivision_slug": "the-beverly", "policy_type": "gift", "title": "Miễn phí dịch vụ 24 tháng",
     "content": "Miễn phí dịch vụ quản lý 24 tháng cho khách hàng mua căn trong quỹ hàng của chủ đầu tư.",
     "valid_from": "2026-09-15", "valid_to": "2026-12-15"},
    {"subdivision_slug": "the-london", "policy_type": "discount", "title": "Ưu đãi quỹ căn cuối The London",
     "content": "Chiết khấu 4% trên giá bán trước VAT cho các căn còn lại trong quỹ hàng của chủ đầu tư khi thanh toán 70% trong 15 ngày.",
     "discount_percent": 4.0, "valid_from": "2026-09-15", "valid_to": "2026-12-15"},
    {"subdivision_slug": "the-london", "policy_type": "discount", "title": "Chương trình mở bán 2024",
     "content": "Chiết khấu 10% cho khách hàng thanh toán sớm trong đợt mở bán năm 2024.",
     "discount_percent": 10.0, "valid_from": "2024-05-01", "valid_to": "2024-09-30"},
    {"subdivision_slug": "the-paris", "policy_type": "payment_schedule", "title": "Lịch thanh toán The Paris",
     "content": "Đặt cọc 50.000.000 đồng.\nĐợt 1: ký văn bản thỏa thuận, thanh toán 10%.\nĐợt 2: ký hợp đồng mua bán, thanh toán 10%.\nĐợt 3: sau 2 tháng, thanh toán 10%.\nĐợt 4: nhận bàn giao, thanh toán 65% cùng 2% kinh phí bảo trì.\nĐợt 5: nhận sổ hồng, thanh toán 5%.",
     "valid_from": "2026-08-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-paris", "policy_type": "discount", "title": "Chiết khấu thanh toán sớm The Paris",
     "content": "Thanh toán sớm 95% trong 30 ngày kể từ ký hợp đồng được chiết khấu 8% trên giá bán trước VAT.",
     "discount_percent": 8.0, "valid_from": "2026-08-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-paris", "policy_type": "loan_support", "title": "Hỗ trợ lãi suất 0% đến khi bàn giao",
     "content": "Ngân hàng đối tác cho vay tối đa 70%. Chủ đầu tư hỗ trợ lãi suất 0% đến khi bàn giao, tối đa 12 tháng.",
     "valid_from": "2026-08-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-palma", "policy_type": "payment_schedule", "title": "Lịch thanh toán The Palma",
     "content": "Đặt cọc 200.000.000 đồng.\nĐợt 1: ký văn bản thỏa thuận trong 14 ngày, thanh toán 10%.\nĐợt 2: ký hợp đồng mua bán, thanh toán 10%.\nĐợt 3 đến đợt 8: mỗi 3 tháng thanh toán 5%.\nĐợt 9: nhận bàn giao, thanh toán 45% cùng 2% kinh phí bảo trì.\nĐợt 10: nhận sổ hồng, thanh toán 5%.",
     "valid_from": "2026-07-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-palma", "policy_type": "discount", "title": "Chiết khấu thanh toán sớm The Palma",
     "content": "Thanh toán sớm 70% trong 60 ngày kể từ ký hợp đồng được chiết khấu 10% trên giá bán trước VAT.",
     "discount_percent": 10.0, "valid_from": "2026-07-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "masteri-waterfront", "policy_type": "loan_support", "title": "Gói vay căn hộ thứ cấp Masteri",
     "content": "Ngân hàng đối tác hỗ trợ vay tối đa 70% giá trị căn hộ, thời hạn tối đa 30 năm cho giao dịch mua lại tại Masteri Waterfront.",
     "valid_from": "2026-06-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "masteri-lakeside", "policy_type": "payment_schedule", "title": "Lịch thanh toán Masteri Lakeside",
     "content": "Đặt cọc: ký xác nhận đăng ký, 50.000.000 đồng.\nĐợt 1: ký văn bản thỏa thuận trong 7 ngày, thanh toán 10% giá trị căn hộ không gồm VAT, đã gồm tiền đặt cọc.\nĐợt 2: ký hợp đồng mua bán, thanh toán 10%.\nĐợt 3: sau 1 tháng, thanh toán 10%.\nĐợt 4: nhận bàn giao dự kiến quý 4/2026, thanh toán 65% cùng VAT và 2% kinh phí bảo trì.\nĐợt 5: nhận sổ hồng, thanh toán 5%.",
     "valid_from": "2026-07-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "masteri-lakeside", "policy_type": "discount", "title": "Chiết khấu thanh toán sớm Masteri Lakeside",
     "content": "Thanh toán sớm 95% trong 30 ngày kể từ ký hợp đồng được chiết khấu 7% trên giá bán trước VAT.",
     "discount_percent": 7.0, "valid_from": "2026-07-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "masteri-lakeside", "policy_type": "gift", "title": "Ưu đãi mở bán quý 2/2026",
     "content": "Tặng gói nội thất rời trị giá 100 triệu đồng cho khách hàng ký hợp đồng trong quý 2 năm 2026.",
     "valid_from": "2026-04-01", "valid_to": "2026-06-30"},
    {"subdivision_slug": "the-senique-hanoi", "policy_type": "payment_schedule", "title": "Lịch thanh toán The Senique Hanoi",
     "content": "Lần 1: booking, ký quỹ có hoàn lại 200.000.000 đồng.\nLần 2: ký thỏa thuận ký quỹ, thanh toán 5% giá trị căn hộ đã gồm tiền booking.\nLần 3: ký hợp đồng mua bán, thanh toán 10%.\nLần 4 đến lần 7: mỗi 3 tháng thanh toán 7,5%.\nLần 8: nhận bàn giao, thanh toán 50% cùng 2% kinh phí bảo trì.\nLần 9: nhận sổ hồng, thanh toán 5%.",
     "valid_from": "2026-08-01", "valid_to": "2026-12-31"},
    {"subdivision_slug": "the-senique-hanoi", "policy_type": "discount", "title": "Chiết khấu thanh toán sớm The Senique",
     "content": "Thanh toán sớm 50% trong 45 ngày kể từ ký hợp đồng được chiết khấu 6% trên giá bán trước VAT.",
     "discount_percent": 6.0, "valid_from": "2026-08-01", "valid_to": "2026-12-31"},
]

PROJECT = {
    "name": "Vinhomes Ocean Park Gia Lâm",
    "aliases": ["Ocean Park", "Ocean Park 1", "Vin Ocean Park", "Vinhomes Ocean Park", "Ô xin pác"],
    "developer": "Vinhomes",
    "location": "Gia Lâm, Hà Nội",
    "area_ha": 420,
    "description": (
        "Đại đô thị khoảng 420 héc ta phía Đông Hà Nội, mô hình thành phố biển hồ với hồ Ngọc Trai 24,5ha và biển hồ "
        "nước mặn Crystal Lagoon 6,1ha; hệ sinh thái Vinschool, VinUni, Vinmec, Vincom Mega Mall; bàn giao từ 2020."
    ),
    "highlights": [
        {"name": "Hồ Ngọc Trai", "detail": "Hồ nước ngọt trung tâm", "size_ha": 24.5},
        {"name": "Biển hồ Crystal Lagoon", "detail": "Biển hồ nước mặn, bãi cát trắng", "size_ha": 6.1},
        {"name": "Đại học VinUni", "detail": "Đại học tư thục chuẩn quốc tế", "size_ha": None},
        {"name": "Vinschool", "detail": "Trường liên cấp mầm non đến THPT", "size_ha": None},
        {"name": "Vinmec", "detail": "Phòng khám và bệnh viện", "size_ha": None},
        {"name": "Vincom Mega Mall Ocean Park", "detail": "Trung tâm thương mại", "size_ha": None},
    ],
    "transport": [
        {"destination": "Hồ Hoàn Kiếm", "distance_km": 15, "drive_minutes_min": 25, "drive_minutes_max": 40},
        {"destination": "Quận Long Biên", "distance_km": 7, "drive_minutes_min": 12, "drive_minutes_max": 20},
        {"destination": "Cầu Thanh Trì", "distance_km": 6, "drive_minutes_min": 10, "drive_minutes_max": 15},
        {"destination": "Sân bay Nội Bài", "distance_km": 35, "drive_minutes_min": 45, "drive_minutes_max": 60},
        {"destination": "Ecopark", "distance_km": 8, "drive_minutes_min": 12, "drive_minutes_max": 18},
    ],
    "source_url": "demo://ocean-park/project",
    "crawled_at": CRAWLED_AT,
}


# ── Sinh bảng hàng ────────────────────────────────────────────────────────────


def _floor_label(floor: int) -> str:
    return SKIP_FLOOR_LABELS.get(floor, "")


def _floor_factor(floor: int, top_floor: int) -> float:
    if floor <= 5:
        return 0.97
    if floor <= 9:
        return 0.99
    factor = 1 + 0.003 * (floor - 10)
    if floor >= top_floor - 1:
        factor -= 0.01
    return factor


def _layout(sub: dict, units_per_floor: int) -> list[dict]:
    """Mặt bằng một tầng điển hình: vị trí căn → loại căn, diện tích, hướng, view."""
    half = units_per_floor // 2
    corners = {0, half - 1, half, units_per_floor - 1}
    rng = random.Random(f"{SEED}:{sub['slug']}:layout:{units_per_floor}")
    corner_i = mix_i = 0
    layout = []
    for pos in range(units_per_floor):
        is_corner = pos in corners
        if is_corner:
            unit_type = sub["corner_types"][corner_i % len(sub["corner_types"])]
            corner_i += 1
        else:
            unit_type = sub["mix"][mix_i % len(sub["mix"])]
            mix_i += 1
        area_min, area_max = sub["types"][unit_type]
        area = round(rng.uniform(area_min, area_max), 1)
        facade = 0 if pos < half else 1
        balcony, view = sub["facades"][facade]
        layout.append(
            {
                "unit_type": unit_type,
                "area_net_m2": area,
                "facade": facade,
                "balcony_direction": balcony,
                "door_direction": OPPOSITE[balcony],
                "view": view,
                "corner": is_corner,
            }
        )
    return layout


def _status_and_price_type(phase: str, rng: random.Random) -> tuple[str, str]:
    """Trả về (status, price_type); price_type rỗng = không có giá."""
    roll = rng.random()
    if phase == "secondary":
        if roll < 0.72:
            return "sold", ""
        if roll < 0.97:
            return "available", "secondary_asking"
        return "unknown", ""
    if phase == "recent":
        if roll < 0.70:
            return "sold", ""
        if roll < 0.88:
            return "available", "secondary_asking"
        if roll < 0.96:
            return "available", "cdt_list"
        return "unknown", ""
    if phase == "primary":
        if roll < 0.45:
            return "available", "cdt_list"
        if roll < 0.60:
            return "booked", "cdt_list"
        if roll < 0.90:
            return "sold", ""
        return "not_released", ""
    # primary_early
    if roll < 0.30:
        return "available", "cdt_list"
    if roll < 0.40:
        return "booked", "cdt_list"
    if roll < 0.60:
        return "sold", ""
    return "not_released", ""


def _round_price(value: float) -> int:
    return int(round(value / 10_000_000) * 10_000_000)


def build_units(sub: dict) -> tuple[list[dict], list[dict]]:
    buildings, units = [], []
    for code, floors, per_floor, elevators in sub["buildings"]:
        buildings.append(
            {
                "building_code": code,
                "subdivision_slug": sub["slug"],
                "aliases": [f"tòa {code}", f"toà {code}", code.replace(".", " chấm "), code.replace(".", "")],
                "num_floors": floors,
                "units_per_floor": per_floor,
                "num_elevators": elevators,
                "handover_status": sub["handover_status"],
                "handover_date": sub["handover_date"],
                "source_url": f"demo://ocean-park/{sub['slug']}/{code}",
                "crawled_at": CRAWLED_AT,
            }
        )
        layout = _layout(sub, per_floor)
        upgrade = sub["view_upgrades"].get(code)
        for floor in range(PODIUM_FLOORS + 1, floors + 1):
            for pos, spec in enumerate(layout):
                unit_code = f"{code}-{floor:02d}{pos + 1:02d}"
                rng = random.Random(f"{SEED}:{unit_code}")
                views = [spec["view"]]
                if upgrade and spec["facade"] == upgrade[0] and floor >= upgrade[1]:
                    views.insert(0, upgrade[2])
                if spec["corner"]:
                    other_view = sub["facades"][1 - spec["facade"]][1]
                    if other_view not in views:
                        views.append(other_view)
                status, price_type = _status_and_price_type(sub["phase"], rng)

                furnishing = sub["handover_standard"]
                if price_type == "secondary_asking" and rng.random() < 0.35:
                    furnishing = "full_furnished"

                price_vnd: int | None = None
                price_date = ""
                if price_type:
                    best_view = max(VIEW_FACTOR[v] for v in views)
                    value = (
                        sub["base_ppm"]
                        * spec["area_net_m2"]
                        * TYPE_PRICE_FACTOR[spec["unit_type"]]
                        * _floor_factor(floor, floors)
                        * best_view
                        * (1.04 if spec["corner"] else 1.0)
                    )
                    if price_type == "secondary_asking":
                        value *= rng.uniform(0.97, 1.04)
                        if furnishing == "full_furnished":
                            value *= 1.03
                        price_date = (date(2026, 8, 15) + timedelta(days=rng.randint(0, 56))).isoformat()
                    else:
                        price_date = "2026-09-01"
                    price_vnd = _round_price(value)

                unit_type = spec["unit_type"]
                bathrooms = 1 if unit_type in ("STUDIO", "1PN", "1PN+1") else 2
                if unit_type == "2PN" and spec["area_net_m2"] < 60:
                    bathrooms = 1
                if unit_type == "4PN":
                    bathrooms = 3
                units.append(
                    {
                        "unit_code": unit_code,
                        "unit_code_original": "",
                        "subdivision_slug": sub["slug"],
                        "building_code": code,
                        "floor": floor,
                        "floor_label": _floor_label(floor),
                        "unit_type": unit_type,
                        "bedrooms": TYPE_BEDROOMS[unit_type],
                        "bathrooms": bathrooms,
                        "area_gross_m2": round(spec["area_net_m2"] * 1.08, 1),
                        "area_net_m2": spec["area_net_m2"],
                        "door_direction": spec["door_direction"],
                        "balcony_direction": spec["balcony_direction"],
                        "views": "|".join(views),
                        "corner_unit": "true" if spec["corner"] else "false",
                        "furnishing": furnishing,
                        "price_vnd": price_vnd if price_vnd is not None else "",
                        "price_includes_vat": ("true" if price_type == "cdt_list" else "") if price_type else "",
                        "price_includes_maintenance": ("false" if price_type == "cdt_list" else "") if price_type else "",
                        "price_type": price_type,
                        "price_date": price_date,
                        "status": status,
                        "source_url": f"demo://ocean-park/{sub['slug']}/{code}",
                        "crawled_at": CRAWLED_AT,
                    }
                )
    return buildings, units


UNIT_COLUMNS = [
    "unit_code", "unit_code_original", "subdivision_slug", "building_code", "floor", "floor_label", "unit_type",
    "bedrooms", "bathrooms", "area_gross_m2", "area_net_m2", "door_direction", "balcony_direction", "views",
    "corner_unit", "furnishing", "price_vnd", "price_includes_vat", "price_includes_maintenance", "price_type",
    "price_date", "status", "source_url", "crawled_at",
]


def _subdivision_record(sub: dict) -> dict:
    total_units = sum((floors - PODIUM_FLOORS) * per_floor for _, floors, per_floor, _ in sub["buildings"])
    return {
        "subdivision_slug": sub["slug"],
        "name": sub["name"],
        "aliases": sub["aliases"],
        "parent_zone": sub["parent_zone"],
        "developer": sub["developer"],
        "design_style": sub["design_style"],
        "num_buildings": len(sub["buildings"]),
        "total_units": total_units,
        "handover_status": sub["handover_status"],
        "handover_date": sub["handover_date"],
        "handover_standard": sub["handover_standard"],
        "handover_standard_detail": sub["handover_standard_detail"],
        "ownership": sub["ownership"],
        "location_text": sub["location_text"],
        "internal_amenities": sub["internal_amenities"],
        "external_amenities": sub["external_amenities"],
        "price_per_m2_min_vnd": None,
        "price_per_m2_max_vnd": None,
        "management_fee_per_m2_vnd": sub["mgmt_fee_per_m2"],
        "source_url": f"demo://ocean-park/{sub['slug']}",
        "crawled_at": CRAWLED_AT,
    }


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    texts = {**DOCS_A, **DOCS_B}

    subdivisions, buildings, units = [], [], []
    for sub in SUBDIVISIONS:
        if sub["slug"] not in texts:
            raise SystemExit(f"Thiếu nội dung knowledge_docs cho {sub['slug']}")
        sub_buildings, sub_units = build_units(sub)
        buildings += sub_buildings
        units += sub_units
        record = _subdivision_record(sub)
        priced = [u["price_vnd"] / u["area_net_m2"] for u in sub_units if u["price_vnd"] != ""]
        if priced:
            record["price_per_m2_min_vnd"] = int(round(min(priced) / 100_000) * 100_000)
            record["price_per_m2_max_vnd"] = int(round(max(priced) / 100_000) * 100_000)
        subdivisions.append(record)

    policies = []
    for index, policy in enumerate(SALES_POLICIES, start=1):
        policies.append(
            {
                "policy_id": f"{policy['subdivision_slug']}-{index:02d}",
                "subdivision_slug": policy["subdivision_slug"],
                "policy_type": policy["policy_type"],
                "title": policy["title"],
                "content": policy["content"],
                "discount_percent": policy.get("discount_percent"),
                "valid_from": policy["valid_from"],
                "valid_to": policy["valid_to"],
                "source_url": f"demo://ocean-park/{policy['subdivision_slug']}/policies",
                "crawled_at": CRAWLED_AT,
            }
        )

    docs = []
    for index, doc in enumerate(PROJECT_DOCS, start=1):
        docs.append(
            {
                "doc_id": f"project:{doc['topic']}:{index:02d}",
                "subdivision_slug": None,
                "topic": doc["topic"],
                "title": doc["title"],
                "content": doc["content"],
                "source_url": "demo://ocean-park/project",
                "crawled_at": CRAWLED_AT,
            }
        )
    for sub in SUBDIVISIONS:
        for topic, (title, content) in texts[sub["slug"]].items():
            extra = EXTRA.get((sub["slug"], topic))
            if extra:
                content = f"{content}\n\n{extra}"
            docs.append(
                {
                    "doc_id": f"{sub['slug']}:{topic}:01",
                    "subdivision_slug": sub["slug"],
                    "topic": topic,
                    "title": title,
                    "content": content,
                    "source_url": f"demo://ocean-park/{sub['slug']}",
                    "crawled_at": CRAWLED_AT,
                }
            )

    (out_dir / "project.json").write_text(json.dumps(PROJECT, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_jsonl(out_dir / "subdivisions.jsonl", subdivisions)
    _write_jsonl(out_dir / "buildings.jsonl", buildings)
    _write_jsonl(out_dir / "sales_policies.jsonl", policies)
    _write_jsonl(out_dir / "knowledge_docs.jsonl", docs)
    with (out_dir / "units.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=UNIT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(units)

    counts = {
        "subdivisions": len(subdivisions),
        "buildings": len(buildings),
        "units": len(units),
        "units_with_price": sum(1 for u in units if u["price_vnd"] != ""),
        "units_available": sum(1 for u in units if u["status"] == "available"),
        "sales_policies": len(policies),
        "knowledge_docs": len(docs),
        "knowledge_words": sum(len(d["content"].split()) for d in docs),
    }
    manifest = {
        "dataset_version": DATASET_VERSION,
        "is_demo": True,
        "crawled_at": CRAWLED_AT,
        "sources": ["demo://ocean-park (dữ liệu giả lập, dựa trên thông tin công khai và data v2 đã sửa lỗi)"],
        "counts": counts,
        "tool_version": "scripts/demo_data/build_demo_data.py",
        "notes": (
            "DỮ LIỆU DEMO — mã căn, giá, trạng thái và chính sách là giả lập để test hệ thống. "
            "Không dùng để tư vấn thật."
        ),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="cleaned_data/demo_v3")
    args = parser.parse_args()
    counts = build(Path(args.out))
    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
