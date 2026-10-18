# Đặc tả dữ liệu v3 — Ocean Park Voice Agent

> Tài liệu này là "hợp đồng dữ liệu" giữa tool crawl/làm sạch và agent.
> Data đúng đặc tả → agent truy xuất chính xác đến **mã căn** và **giá**.
> Agent sẽ có script `validate_data.py` kiểm tra mọi quy tắc ở mục 5 trước khi import.

## 0. Nguyên tắc chung (bắt buộc)

1. **Một bản ghi = một thực thể.** Không trộn thông tin của phân khu A vào bản ghi phân khu B. Nếu trang nguồn nói về nhiều phân khu, tách ra nhiều bản ghi.
2. **Số là số, không phải chuỗi.** Giá lưu bằng **VND số nguyên** (`3450000000`), diện tích lưu bằng **m² số thực** (`64.5`). Không lưu `"3,45 tỷ"` hay `"64,5m²"`.
3. **Không biết thì để `null`**, không để `""`, `"đang cập nhật"`, `"liên hệ"`, `"đã bán hết"`. Trạng thái (đã bán, chưa công bố giá…) đi vào trường `status` riêng.
4. **Truy vết được.** Mọi bản ghi có `source_url` + `crawled_at` (ISO 8601). Giữ HTML/JSON gốc ở `data/raw/` để đối chiếu.
5. **Không có text quảng cáo**: bỏ các cụm như "Tư vấn ngay", "BẢNG GIÁ GỐC – THỦ TỤC TRỰC TIẾP CĐT", số hotline, emoji, CTA.
6. **Unicode NFC**, bỏ HTML tag, gộp khoảng trắng thừa. Giữ nguyên dấu tiếng Việt.
7. **Không tách danh sách bằng dấu phẩy** khi trong câu có số thập phân kiểu Việt (`24,5ha`). Ưu tiên tách theo thẻ `<li>` hoặc xuống dòng của nguồn.
8. Tôn trọng `robots.txt` và điều khoản của trang nguồn; crawl có delay, không dồn request.

## 1. Cấu trúc thư mục đầu ra

```text
data/
  raw/                      # HTML/JSON gốc, tên file = sha1(url).html — KHÔNG commit nếu nặng
cleaned_data/v3/
  project.json              # 1 object — tổng quan đại đô thị
  subdivisions.jsonl        # mỗi dòng 1 phân khu
  buildings.jsonl           # mỗi dòng 1 tòa
  units.csv                 # bảng hàng — mỗi dòng 1 căn
  sales_policies.jsonl      # mỗi dòng 1 chính sách
  knowledge_docs.jsonl      # văn bản mô tả (tiện ích, vị trí, thiết kế...) để làm RAG
  manifest.json             # metadata của lần crawl
```

`.jsonl` = mỗi dòng là một JSON object hoàn chỉnh, UTF-8, không có dấu phẩy cuối dòng.

## 2. Định danh (ID) — quan trọng nhất cho độ chính xác

| Thực thể | Trường | Quy tắc | Ví dụ |
|---|---|---|---|
| Phân khu | `subdivision_slug` | chữ thường, không dấu, nối bằng `-`, **không** có hậu tố `-vinhomes` | `the-zenpark`, `masteri-waterfront` |
| Tòa | `building_code` | viết HOA, đúng ký hiệu chủ đầu tư dùng | `R1.01`, `S2.18`, `BE1`, `LD2` |
| Căn | `unit_code` | `{building_code}-{tầng 2 chữ số}{số căn 2 chữ số}` | `R1.01-1205` (tòa R1.01, tầng 12, căn 05) |

- `unit_code` phải **duy nhất toàn bộ dataset**.
- Nếu chủ đầu tư dùng mã khác (ví dụ `R101-12A05`), giữ mã gốc ở `unit_code_original`, còn `unit_code` vẫn theo chuẩn trên.
- Tầng đặc biệt (12A, 14A thay cho 13, 14): ghi `floor_label: "12A"`, `floor: 13` (số thứ tự thật).

## 3. Schema từng file

### 3.1 `project.json`

```json
{
  "name": "Vinhomes Ocean Park Gia Lâm",
  "aliases": ["Ocean Park", "Ocean Park 1", "Vin Ocean Park"],
  "developer": "Vinhomes",
  "location": "Gia Lâm, Hà Nội",
  "area_ha": 420,
  "description": "…văn bản sạch 100–300 từ…",
  "highlights": [
    {"name": "Hồ Ngọc Trai", "detail": "Hồ nước ngọt", "size_ha": 24.5},
    {"name": "Biển hồ nước mặn Crystal Lagoon", "size_ha": 6.1}
  ],
  "transport": [
    {"destination": "Hồ Hoàn Kiếm", "distance_km": 15, "drive_minutes_min": 25, "drive_minutes_max": 35}
  ],
  "source_url": "https://…",
  "crawled_at": "2026-10-20T09:00:00+07:00"
}
```

### 3.2 `subdivisions.jsonl`

| Trường | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `subdivision_slug` | string | ✅ | theo mục 2 |
| `name` | string | ✅ | `The Zenpark` |
| `aliases` | string[] | ✅ | **Cách người Việt hay nói/đọc nhầm** — rất quan trọng cho voice: `["Zenpark", "Zen Park", "dần pác", "phân khu Nhật"]` |
| `parent_zone` | string\|null | | `The Ocean View`, `The Metropolitan` |
| `developer` | string | ✅ | `Vinhomes`, `Masterise Homes`, `CapitaLand Development` |
| `design_style` | string\|null | | `Nhật Bản`, `Thụy Sỹ` |
| `num_buildings` | int\|null | | |
| `total_units` | int\|null | | |
| `handover_status` | enum | ✅ | `handed_over` \| `under_construction` \| `not_started` \| `unknown` |
| `handover_date` | string\|null | | `"2026-Q3"` hoặc `"2025-08"` |
| `handover_standard` | enum\|null | | `raw` (thô) \| `basic` (cơ bản) \| `full_built_in` (liền tường) \| `full_furnished` (full nội thất) |
| `handover_standard_detail` | string\|null | | mô tả ngắn các hạng mục bàn giao |
| `ownership` | enum\|null | | `long_term` (lâu dài) \| `50_years` \| `unknown` |
| `location_text` | string\|null | | vị trí **của riêng phân khu này** |
| `internal_amenities` | string[] | | mỗi phần tử là **một tiện ích ngắn** (`"Bể bơi bốn mùa"`), không phải câu văn |
| `external_amenities` | string[] | | như trên |
| `price_per_m2_min_vnd` / `price_per_m2_max_vnd` | int\|null | | nếu nguồn có |
| `management_fee_per_m2_vnd` | int\|null | | phí quản lý VND/m²/tháng |
| `source_url`, `crawled_at` | string | ✅ | |

### 3.3 `buildings.jsonl`

| Trường | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `building_code` | string | ✅ | theo mục 2 |
| `subdivision_slug` | string | ✅ | phải tồn tại trong `subdivisions.jsonl` |
| `aliases` | string[] | | `["tòa R1.01", "rờ một không một"]` |
| `num_floors` | int\|null | | |
| `units_per_floor` | int\|null | | |
| `num_elevators` | int\|null | | |
| `handover_status`, `handover_date` | | | như phân khu, nếu tòa khác phân khu |
| `source_url`, `crawled_at` | string | ✅ | |

### 3.4 `units.csv` — bảng hàng

CSV UTF-8 (có header), dấu phân cách `,`, số thập phân dùng dấu chấm `.`.

| Cột | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `unit_code` | string | ✅ | duy nhất, theo mục 2 |
| `unit_code_original` | string | | mã gốc nếu khác |
| `subdivision_slug` | string | ✅ | |
| `building_code` | string | ✅ | phải tồn tại trong `buildings.jsonl` |
| `floor` | int | ✅ | số thứ tự tầng thật |
| `floor_label` | string | | `12A` nếu có |
| `unit_type` | enum | ✅ | `STUDIO` \| `1PN` \| `1PN+1` \| `2PN` \| `2PN+1` \| `3PN` \| `4PN` \| `DUPLEX` \| `PENTHOUSE` \| `SHOPHOUSE` |
| `bedrooms` / `bathrooms` | int | | |
| `area_gross_m2` | float | | diện tích tim tường |
| `area_net_m2` | float | ✅ | diện tích thông thủy (dùng để tư vấn) |
| `door_direction` | enum | | `N` `NE` `E` `SE` `S` `SW` `W` `NW` |
| `balcony_direction` | enum | | như trên |
| `views` | string | | các view cách nhau bằng `\|`, view đẹp nhất đứng đầu. Từ vựng: `ho_ngoc_trai` `bien_ho` `ho_canh_quan` `vuon_nhat` `cong_vien` `noi_khu` `thanh_pho` |
| `corner_unit` | bool | | `true`/`false` |
| `furnishing` | enum | | `raw` \| `basic` \| `full_built_in` \| `full_furnished` |
| `price_vnd` | int | | **giá tổng, VND số nguyên**; để trống nếu chưa có giá |
| `price_includes_vat` | bool | | |
| `price_includes_maintenance` | bool | | đã gồm 2% phí bảo trì chưa |
| `price_type` | enum | nếu có giá | `cdt_list` (bảng giá CĐT) \| `secondary_asking` (rao bán thứ cấp) \| `secondary_sold` (đã giao dịch) \| `estimate`; để trống khi `price_vnd` trống |
| `price_date` | date | nếu có giá | `2026-10-15` — giá có hiệu lực/ghi nhận ngày nào |
| `status` | enum | ✅ | `available` \| `booked` \| `sold` \| `not_released` \| `unknown` |
| `source_url` | string | ✅ | |
| `crawled_at` | datetime | ✅ | |

> ⚠️ Phân biệt rõ `price_type`. Giá rao trên trang môi giới **không phải** giá chủ đầu tư. Agent sẽ nói khác nhau tùy loại giá ("giá rao bán tham khảo" và "giá niêm yết CĐT").

### 3.5 `sales_policies.jsonl`

| Trường | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `policy_id` | string | ✅ | `masteri-lakeside-payment-2026q3` |
| `subdivision_slug` | string | ✅ | |
| `policy_type` | enum | ✅ | `payment_schedule` \| `discount` \| `loan_support` \| `gift` \| `other` |
| `title` | string | ✅ | |
| `content` | string | ✅ | văn bản sạch; lịch thanh toán thì giữ dạng danh sách từng đợt |
| `discount_percent` | float\|null | | |
| `valid_from` / `valid_to` | date\|null | | **rất quan trọng**, agent không nói chính sách đã hết hạn |
| `source_url`, `crawled_at` | string | ✅ | |

### 3.6 `knowledge_docs.jsonl` — văn bản mô tả cho RAG

Dùng cho câu hỏi định tính (tiện ích ra sao, sống có thoải mái không, thiết kế thế nào). **Không** đưa giá hay mã căn vào đây, vì những thứ đó lấy từ `units.csv`.

| Trường | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `doc_id` | string | ✅ | `the-zenpark:amenities:01` |
| `subdivision_slug` | string\|null | ✅ | `null` = nói về toàn đại đô thị |
| `topic` | enum | ✅ | `overview` \| `location` \| `amenities` \| `design` \| `handover` \| `legal` \| `community` \| `transport` |
| `title` | string | ✅ | |
| `content` | string | ✅ | **80–600 từ**, văn xuôi sạch, chỉ nói về đúng `subdivision_slug` + `topic` |
| `source_url`, `crawled_at` | string | ✅ | |

Tool crawl **không cần tự chunk**. Agent sẽ tự chia nhỏ và embed. Chỉ cần mỗi doc đúng một chủ đề và không lặp lại nội dung doc khác.

### 3.7 `manifest.json`

```json
{
  "dataset_version": "v3.0.0",
  "crawled_at": "2026-10-20T09:00:00+07:00",
  "sources": ["https://…", "https://…"],
  "counts": {"subdivisions": 12, "buildings": 60, "units": 5000, "sales_policies": 10, "knowledge_docs": 80},
  "tool_version": "crawler 0.1.0",
  "notes": "Giá Zurich chưa công bố; Bayfront thiếu dữ liệu tòa."
}
```

## 4. Quy tắc làm sạch (checklist cho tool)

- [ ] Chuẩn hóa giá: `"3,45 tỷ"` → `3450000000`; `"45 triệu/m²"` → `price_per_m2 = 45000000`; `"2.3 tỷ"` và `"2,3 tỷ"` đều → `2300000000`.
- [ ] Chuẩn hóa diện tích: `"64,5m²"`, `"64.5 m2"` → `64.5`.
- [ ] Chuẩn hóa loại căn: `"2 phòng ngủ"`, `"2PN"`, `"2 ngủ"`, `"2BR"` → `2PN`; `"2PN+"`, `"2 ngủ + 1"` → `2PN+1`.
- [ ] Chuẩn hóa hướng: `"Đông Nam"` → `SE`.
- [ ] Bỏ CTA, hotline, emoji, text quảng cáo.
- [ ] Phát hiện lẫn phân khu: nếu `content` của phân khu A nhắc tên phân khu B nhiều hơn A thì đánh dấu để kiểm tra tay.
- [ ] Loại trùng: hai doc có nội dung giống nhau trên 80% thì giữ một.
- [ ] Giá trị "không biết" → `null` (xem nguyên tắc 3).
- [ ] Tiện ích: mỗi phần tử ≤ 8 từ, không chứa dấu chấm câu giữa câu, không phải loại căn hay tên tòa.

## 5. Quy tắc kiểm tra (validator sẽ chạy)

| # | Quy tắc | Mức |
|---|---|---|
| V1 | `unit_code` duy nhất | lỗi |
| V2 | `building_code` của căn tồn tại trong `buildings.jsonl`; `subdivision_slug` khớp với tòa | lỗi |
| V3 | `floor` ≤ `num_floors` của tòa (nếu có) | lỗi |
| V4 | `area_net_m2` hợp lý theo loại căn: STUDIO 20–40, 1PN 30–55, 1PN+1 40–60, 2PN 50–85, 2PN+1 55–90, 3PN 70–130 | cảnh báo |
| V5 | `price_vnd / area_net_m2` nằm trong 20–200 triệu/m² | cảnh báo |
| V6 | Có `price_vnd` thì phải có `price_type` và `price_date` | lỗi |
| V7 | `status = sold` thì không có `price_type = cdt_list` mới hơn 30 ngày | cảnh báo |
| V8 | Mọi bản ghi có `source_url`, `crawled_at` | lỗi |
| V9 | Không trường text nào chứa `"đang cập nhật"`, `"liên hệ"`, `"tư vấn ngay"`, số điện thoại | lỗi |
| V10 | `sales_policies.valid_to` (nếu có) ≥ `valid_from` | lỗi |
| V11 | Mỗi phân khu có ít nhất 1 doc `overview` và 1 doc `amenities` | cảnh báo |

## 6. Mẫu dữ liệu

`units.csv`
```csv
unit_code,unit_code_original,subdivision_slug,building_code,floor,floor_label,unit_type,bedrooms,bathrooms,area_gross_m2,area_net_m2,door_direction,balcony_direction,views,corner_unit,furnishing,price_vnd,price_includes_vat,price_includes_maintenance,price_type,price_date,status,source_url,crawled_at
R1.01-1205,,the-zenpark,R1.01,12,,2PN,2,2,69.8,64.2,NW,SE,ho_ngoc_trai|noi_khu,false,full_built_in,3350000000,true,false,secondary_asking,2026-10-15,available,https://example.com/listing/123,2026-10-20T09:00:00+07:00
R1.01-1206,,the-zenpark,R1.01,12,,STUDIO,0,1,30.1,27.5,NW,SE,noi_khu,false,full_built_in,,,,,,unknown,https://example.com/listing/124,2026-10-20T09:00:00+07:00
```

`subdivisions.jsonl` (1 dòng)
```json
{"subdivision_slug":"the-zenpark","name":"The Zenpark","aliases":["Zenpark","Zen Park","dần pác","phân khu Nhật"],"parent_zone":"The Ocean View","developer":"Vinhomes","design_style":"Nhật Bản","num_buildings":4,"total_units":null,"handover_status":"handed_over","handover_date":"2021-Q2","handover_standard":"full_built_in","handover_standard_detail":"Sàn gỗ, điều hòa, tủ bếp, thiết bị vệ sinh","ownership":"long_term","location_text":"Mặt đường Lý Thánh Tông, gần cổng chính đại đô thị","internal_amenities":["Vườn Nhật","Hồ cá Koi","Bể bơi bốn mùa","Gym trong nhà"],"external_amenities":["Vinschool","Vinmec","Vincom Mega Mall"],"price_per_m2_min_vnd":null,"price_per_m2_max_vnd":null,"source_url":"https://vinhomeoceanpark.com.vn/the-zenpark","crawled_at":"2026-10-20T09:00:00+07:00"}
```

## 7. Mức tối thiểu để demo được

Nếu thời gian gấp, ưu tiên theo thứ tự:
1. `subdivisions.jsonl` đầy đủ, **đặc biệt là `aliases`**
2. `units.csv` cho **2–3 phân khu** (vài trăm căn là đủ demo truy xuất theo mã căn và giá)
3. `knowledge_docs.jsonl` gồm `overview` + `amenities` cho mọi phân khu
4. `buildings.jsonl`, `sales_policies.jsonl`, `project.json`
