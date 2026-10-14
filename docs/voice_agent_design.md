# Thiết kế — Ocean Park Voice Agent

> Phiên bản 1.0 · 2026-10-14
> Mục tiêu: biến project chatbot cũ thành **trợ lý tư vấn bằng giọng nói** cho căn hộ Vinhomes Ocean Park, trải nghiệm như **một cuộc gọi điện**.

## 1. Phạm vi

### Có trong phiên bản này
1. **Giao tiếp hoàn toàn bằng giọng nói**: khách nói, agent nói. Khách không phải đọc gì.
2. **Hiểu ngữ nghĩa và truy xuất chính xác**: đúng mã căn, đúng giá, đúng diện tích, lấy thẳng từ dữ liệu có cấu trúc. LLM không được tự bịa số.
3. **Lưu hội thoại để đánh giá**: transcript có nhãn **Khách / AI**, kèm **file ghi âm của cả hai phía**, độ trễ từng khâu và tool đã gọi.
4. **Ghi nhận thông tin khách qua giọng nói**: tên, SĐT, nhu cầu. Agent đọc lại để xác nhận rồi lưu; admin xem được.
5. **Data demo đầy đủ** để test toàn hệ thống trước khi có data thật (xem mục 7).

### Bỏ khỏi project cũ
| Bỏ | Lý do |
|---|---|
| Chặn sau 3 tin (`FREE_MESSAGE_LIMIT`), giới hạn tốc độ | Không hợp cuộc gọi |
| Luật trả lời cứng (fallback rules) | Agent mới xử lý được |
| Phân loại ý định bằng regex, chấm điểm khách bằng regex, tự gán Sales | Thay bằng agent LLM có tool calling |
| Quản lý Sales, phân quyền, giải thưởng, lịch sử mua | Ngoài phạm vi |
| Nhánh pgvector không chạy được, retriever JSON lỗi, `/agent/recommend`, `/agent/customer-score`, `/api/v1/chat` | Thay bằng tầng truy xuất mới |
| Chat widget dạng văn bản | Thay bằng giao diện cuộc gọi |

### Giữ lại
FastAPI, SQLAlchemy, Alembic, đăng nhập admin (JWT), bảng `customers` / `conversations` / `messages` (mở rộng thêm cột), trang public Next.js, trang admin (rút gọn).

## 2. Trải nghiệm phía khách

1. Khách bấm **"Gọi tư vấn"**. Màn hình cuộc gọi hiện: avatar, đồng hồ, trạng thái *Đang nghe / Đang xử lý / Đang nói*, nút **Kết thúc**. **Không hiện phụ đề.**
2. Agent **chào trước** bằng giọng nói.
3. Khách nói tự nhiên, **không cần bấm nút**. Hệ thống tự nhận ra lúc khách ngừng nói (VAD).
4. Câu cần tra dữ liệu: agent nói **câu lót** ("Dạ để em kiểm tra giúp anh chị ạ") rồi mới trả lời.
5. **Ngắt lời**: khách nói chen khi agent đang nói thì agent dừng ngay và chuyển sang nghe.
6. Bấm **Kết thúc**: agent chào tạm biệt, cuộc gọi được lưu.

Khuyến nghị demo bằng **tai nghe** để tránh tiếng vọng.

## 3. Kiến trúc

```
┌──────────────────────── Trình duyệt (Next.js) ─────────────────────────┐
│  Micro ─► AudioWorklet (PCM 16kHz) ─► VAD năng lượng + pre-roll 300ms  │
│                │ utterance.wav                                          │
│                ▼                                                        │
│  POST /voice/turn  ◄── NDJSON stream ──  phát từng câu MP3 theo thứ tự  │
│  (barge-in: dừng phát + POST /voice/interrupt)                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌──────────────────────────── FastAPI ────────────────────────────────────┐
│ 1. Lưu WAV khách ─► STT (OpenRouter /audio/transcriptions, lang=vi)     │
│ 2. Agent: LLM (OpenRouter, tool calling) + lịch sử hội thoại            │
│      tools ─► SQL trên units/buildings/subdivisions/policies            │
│            └► hybrid search (embedding + BM25) trên knowledge chunks    │
│ 3. Chia câu ─► chuẩn hóa văn nói (số, mã căn, SĐT) ─► TTS (OpenRouter   │
│    /audio/speech, MP3) ─► stream về client + ghép thành file AI turn    │
│ 4. Lưu message (role, text, audio, latency, tool calls, interrupted)    │
└──────────────────────────────────────────────────────────────────────────┘
                                 │
                        SQLite (local) / PostgreSQL
                        data/recordings/{session}/…
```

### 3.1 Lựa chọn model (cấu hình bằng `.env`, đổi được)

| Khâu | Mặc định | Biến môi trường | Ghi chú |
|---|---|---|---|
| STT | `openai/gpt-4o-mini-transcribe` | `STT_MODEL` | dự phòng: `openai/whisper-large-v3-turbo`; luôn gửi `language=vi` |
| LLM | `google/gemini-2.5-flash` | `LLM_MODEL` | cần tool calling, độ trễ thấp, tiếng Việt tốt |
| TTS | `google/gemini-3.8-flash-tts` | `TTS_MODEL`, `TTS_VOICE` | MP3; nếu giọng tiếng Việt chưa đạt, đổi sang `elevenlabs/eleven-flash-v2.5` |
| Embedding | `openai/text-embedding-3-small` | `EMBEDDING_MODEL` | tính lúc import data, lưu trong DB |

Tất cả đi qua **một key `OPENROUTER_API_KEY`**. Chất lượng tiếng Việt của STT/TTS phải được nghe thử khi có key; tham số đã tách ra `.env` để đổi model mà không sửa code.

### 3.2 Giao thức `/voice/*`

| Endpoint | Vào | Ra |
|---|---|---|
| `POST /voice/calls` | — | `{session_id}` + stream câu chào (giống `/turn`) |
| `POST /voice/turn` | multipart: `session_id`, `audio` (WAV) | **NDJSON stream** (bảng dưới) |
| `POST /voice/interrupt` | `{session_id, turn_id, played_segments}` | đánh dấu lượt AI bị ngắt |
| `POST /voice/calls/{id}/end` | — | stream câu tạm biệt, chốt cuộc gọi |

Các sự kiện trong stream `/voice/turn`:
```jsonc
{"type":"transcript","turn_id":12,"text":"cho chị hỏi căn hai ngủ ở zenpark"}   // STT xong (client dùng để debug, không hiển thị)
{"type":"state","value":"thinking"}
{"type":"audio","seq":0,"filler":true,"mime":"audio/mpeg","data":"<base64>"}   // câu lót
{"type":"audio","seq":1,"mime":"audio/mpeg","data":"<base64>"}               // từng câu trả lời
{"type":"done","turn_id":13}
{"type":"error","message":"…","fallback_text":"…"}                            // client đọc bằng speechSynthesis
```

### 3.3 Độ trễ mục tiêu

| Khâu | Mục tiêu |
|---|---|
| VAD xác nhận ngừng nói | 700 ms im lặng |
| STT | ≤ 800 ms |
| LLM đến câu đầu tiên (có tool) | ≤ 1.200 ms |
| TTS câu đầu | ≤ 600 ms |
| **Khách ngừng nói → nghe tiếng agent** | **~1,5–3 s** (câu lót che bớt thời gian tra dữ liệu) |

Mỗi khâu được đo và lưu vào `messages.meta` để đánh giá.

## 4. Agent

### 4.1 Vòng lặp
Agent là một LLM có tool calling, không còn chuỗi 4 node regex như bản cũ:

```
lịch sử hội thoại (N lượt gần nhất) + system prompt
   └─► LLM ──(tool call?)──► chạy tool ──► LLM ──► … ──► câu trả lời (stream)
```

- Tối đa 4 vòng tool mỗi lượt.
- Lịch sử: 12 lượt gần nhất kèm **tóm tắt hồ sơ khách** (ngân sách, loại căn, phân khu quan tâm), được cập nhật mỗi lượt.
- Stream token, cắt theo dấu câu, gửi từng câu sang TTS.

### 4.2 Tools

| Tool | Nguồn | Mục đích |
|---|---|---|
| `search_units(subdivision?, unit_type?, budget_min?, budget_max?, min_area?, view?, direction?, status="available", sort?, limit=5)` | SQL `units` | tìm căn theo nhu cầu |
| `get_unit(unit_code)` | SQL `units` | tra chính xác một căn theo mã |
| `get_subdivision(name)` | SQL `subdivisions` + thống kê `units` | tổng quan phân khu, khoảng giá **tính từ bảng hàng** |
| `compare_subdivisions(names[])` | SQL | so sánh 2–3 phân khu |
| `get_sales_policy(subdivision)` | SQL `sales_policies` (lọc theo hiệu lực) | chính sách thanh toán, ưu đãi |
| `search_knowledge(query, subdivision?)` | hybrid search trên `knowledge_chunks` | câu hỏi định tính: tiện ích, vị trí, thiết kế, cộng đồng |
| `save_customer_info(full_name, phone, need_summary?, preferred_time?)` | ghi `customers` | lưu lead **sau khi khách xác nhận** |

Quy tắc chung của tool:
- **Phân giải tên phân khu/tòa bằng `aliases` + so khớp mờ** (bỏ dấu, khoảng cách ký tự), chịu được lỗi nhận dạng giọng nói ("dần pác" → `the-zenpark`). Không chắc chắn thì trả về danh sách gợi ý để agent hỏi lại.
- **Mỗi giá trị số trả về kèm sẵn dạng đọc**, ví dụ `"price_vnd": 3350000000, "price_spoken": "ba tỷ ba trăm năm mươi triệu"`.
- Kết quả kèm `price_type` và `price_date` để agent nói đúng loại giá.

### 4.3 Chống bịa số (độ chính xác)
1. System prompt: **mọi mã căn, giá, diện tích chỉ được lấy từ kết quả tool của cuộc gọi này**.
2. **Bộ kiểm tra sau trả lời**: trích các mã căn, giá, diện tích có trong câu trả lời và đối chiếu với kết quả tool. Không khớp thì ghi `meta.fact_check = "mismatch"` (để đánh giá) và thay câu đó bằng câu an toàn.
3. Không có dữ liệu thì nói thẳng "em chưa có thông tin này", không suy đoán.

### 4.4 Phong cách nói
- Mỗi lượt 1–3 câu, tối đa khoảng 60 từ. Gợi ý 1–2 lựa chọn rồi hỏi lại, không liệt kê dài.
- Không markdown, bullet, emoji, link.
- Xưng "em", gọi "anh/chị".
- **Chuẩn hóa trước TTS** (lớp an toàn cuối):
  - giá `3.350.000.000` → "ba tỷ ba trăm năm mươi triệu"
  - diện tích `64,2m²` → "sáu mươi tư phẩy hai mét vuông"
  - mã căn `R1.01-1205` → "tòa R một chấm không một, tầng mười hai, căn số không năm"
  - SĐT `0912345678` → "không chín một hai, ba bốn năm, sáu bảy tám"

### 4.5 Ghi nhận thông tin khách
1. Agent xin tên và SĐT khi khách muốn được liên hệ, hoặc khi cuộc trò chuyện đã đủ sâu (đã hỏi giá hoặc căn cụ thể).
2. Chuẩn hóa SĐT nói bằng lời: "không chín một hai…", "chín mươi mốt", "+84" → `0912345678`; kiểm tra đúng định dạng di động Việt Nam (10 số, đầu số hợp lệ).
3. **Đọc lại để xác nhận**. Khách đồng ý thì gọi `save_customer_info`; khách sửa thì cập nhật rồi đọc lại.
4. Lưu vào `customers` (khóa theo SĐT, gộp nếu đã có) và gắn với `conversations.customer_id`. Nhu cầu được tóm tắt từ hội thoại.

### 4.6 An toàn
Giữ các quy tắc của bản cũ: không cam kết lợi nhuận đầu tư, không lộ thông tin khách khác, không nói chính sách đã hết hạn, từ chối yêu cầu đổi vai trò. Câu hỏi ngoài phạm vi Ocean Park thì lịch sự kéo về chủ đề.

## 5. Lưu hội thoại để đánh giá

### 5.1 Lưu trữ
- `conversations`: thêm `channel="voice"`, `status` (`active|ended|abandoned`), `ended_at`, `duration_sec`, `data_version` (ví dụ `demo-v3.0.0`), `models` (STT/LLM/TTS đã dùng).
- `messages`: `role` là `customer` hoặc `ai`; `content` (transcript hoặc câu AI nói); `audio_path`; `meta` gồm `turn_index`, `stt_ms`, `llm_first_token_ms`, `tts_ms`, `total_ms`, `tool_calls` (tên + tham số + kết quả rút gọn), `fact_check`, `interrupted`, `played_segments`, `is_filler`.
- File âm thanh: `data/recordings/{session_id}/{turn:03d}_customer.wav` và `{turn:03d}_ai.mp3`. Câu lót lưu riêng, đánh dấu `is_filler`.

### 5.2 Trang admin
- **Danh sách cuộc gọi**: thời gian, thời lượng, số lượt, khách (nếu đã để lại thông tin), độ trễ trung bình, có lượt nào `fact_check=mismatch` không.
- **Chi tiết cuộc gọi**: dòng thời gian từng lượt Khách/AI, có trình phát âm thanh cho từng lượt, độ trễ, tool đã gọi (mở rộng xem tham số và kết quả).
- **Xuất JSON** một cuộc gọi hoặc nhiều cuộc gọi (`GET /api/v1/admin/conversations/{id}/export`) để chấm điểm offline.
- **Danh sách khách**: tên, SĐT, nhu cầu, phân khu quan tâm, link sang cuộc gọi.
- Banner **"ĐANG DÙNG DATA DEMO"** khi `manifest.is_demo = true`.

## 6. Dữ liệu và truy xuất

### 6.1 Mô hình dữ liệu (theo [data_spec_v3.md](data_spec_v3.md))
Các bảng mới hoặc mở rộng: `subdivisions` (thêm `aliases`, `developer`, `handover_*`, `ownership`…), `buildings`, `units`, `sales_policies` (thêm `policy_type`, `valid_from`, `valid_to`), `knowledge_docs`, `knowledge_chunks` (kèm `embedding` lưu JSON), `dataset_versions`.

### 6.2 Pipeline import
```
cleaned_data/<dataset>/  ─► scripts/validate_data.py (11 quy tắc V1–V11)
                         ─► scripts/import_data.py
                               ├─ upsert subdivisions / buildings / units / policies
                               ├─ chunk knowledge_docs (~350 token, overlap 50, cắt theo đoạn)
                               ├─ embed chunk qua OpenRouter (không có key → chỉ BM25)
                               └─ ghi dataset_versions (version, is_demo, counts, imported_at)
```
Biến `DATASET_DIR` chọn bộ data: `cleaned_data/demo_v3` (mặc định) hoặc `cleaned_data/v3` (data thật).

### 6.3 Truy xuất
- **Câu hỏi định lượng** (giá, mã căn, diện tích, còn hàng): **chỉ SQL**, không qua RAG.
- **Câu hỏi định tính**: hybrid search = cosine embedding (trong bộ nhớ, vài trăm chunk) + BM25 tiếng Việt bỏ dấu, gộp bằng RRF và lọc theo phân khu nếu xác định được. Không có embedding thì dùng BM25.

## 7. Data demo (giai đoạn hiện tại)

### 7.1 Mục tiêu
Có một bộ data **đầy đủ, đủ dài, đúng đặc tả v3** để test toàn bộ hệ thống: giọng nói, truy xuất chính xác theo mã căn và giá, câu hỏi định tính, chính sách, lưu thông tin khách. Khi hệ thống đã ổn định thì thay bằng data thật mà **không phải sửa code**.

### 7.2 Nội dung bộ demo `cleaned_data/demo_v3/`

| File | Quy mô | Cách tạo |
|---|---|---|
| `project.json` | 1 bản ghi đầy đủ: tổng quan, các đại tiện ích, kết nối giao thông | viết tay |
| `subdivisions.jsonl` | **12 phân khu**, điền đủ mọi trường, mỗi khu **5–10 aliases** (gồm cách đọc nhầm khi nhận dạng giọng nói) | dựa trên data cũ đã sửa lỗi + viết bổ sung |
| `buildings.jsonl` | **~45 tòa** (2–6 tòa mỗi phân khu), có số tầng, số căn mỗi tầng, thang máy | sinh có quy tắc |
| `units.csv` | **toàn bộ bảng hàng của mọi tòa, hàng nghìn căn**: mã căn, tầng, loại căn, diện tích, hướng, view, căn góc, nội thất, giá, trạng thái | script sinh tất định (seed cố định) |
| `sales_policies.jsonl` | **2–3 chính sách mỗi phân khu** (lịch thanh toán, chiết khấu, hỗ trợ vay, quà tặng), trong đó **có chính sách đã hết hạn** để test lọc theo hiệu lực | viết theo mẫu |
| `knowledge_docs.jsonl` | **6–8 chủ đề mỗi phân khu + ~10 doc cấp đại đô thị**, mỗi doc **150–450 từ** văn xuôi sạch | viết tay |
| `manifest.json` | `"is_demo": true`, `dataset_version: "demo-v3.0.0"` | sinh tự động |

### 7.3 Quy tắc sinh bảng hàng
- Mã căn đúng chuẩn `{tòa}-{tầng:02}{căn:02}`, duy nhất.
- Mỗi tầng có một mặt bằng cố định: vị trí căn xác định loại căn, diện tích, hướng, view và căn góc. Nhờ vậy dữ liệu nhất quán như bảng hàng thật.
- **Giá = đơn giá cơ sở theo phân khu × diện tích × hệ số tầng × hệ số view × hệ số căn góc**, làm tròn đến 10 triệu. Đơn giá cơ sở bám theo khoảng giá tham khảo của từng phân khu trong data cũ (đã sửa các chỗ vô lý).
- `price_type`: phân khu đã bàn giao dùng `secondary_asking`, phân khu đang mở bán dùng `cdt_list`. Có `price_date` cụ thể.
- `status` phân bổ theo tình trạng phân khu (khu đã bàn giao phần lớn là `sold`, khu mới mở bán phần lớn là `available`/`not_released`). Một số căn để trống giá (`price_vnd` null) để test câu "chưa có giá".
- Seed cố định: chạy lại script luôn ra đúng dữ liệu đó, câu hỏi đánh giá không bị lệch.

### 7.4 Ranh giới với data thật
- Data demo **chỉ dùng để test**. Admin luôn thấy banner "ĐANG DÙNG DATA DEMO", và mọi cuộc gọi ghi lại `data_version` để không lẫn kết quả đánh giá giữa hai bộ.
- Agent vẫn nói "giá tham khảo" như với data thật. Không nói "đây là dữ liệu giả" trong cuộc gọi, để test sát thực tế.
- **Chuyển sang data thật**: đặt data thật vào `cleaned_data/v3/`, chạy `validate_data.py` cho đến khi không còn lỗi, chạy `import_data.py --dataset cleaned_data/v3`, đổi `DATASET_DIR`. Không cần sửa code.
- Bộ câu hỏi đánh giá viết cho data demo (mục 8) có đáp án tham chiếu sinh từ data, nên khi đổi data thì sinh lại đáp án tự động.

## 8. Đánh giá

- **Bộ câu hỏi chuẩn** `eval/voice_cases.jsonl`: khoảng 40 câu chia theo nhóm (tra mã căn, lọc theo ngân sách, so sánh phân khu, chính sách, tiện ích, ngoài phạm vi, để lại thông tin, sửa SĐT). Đáp án tham chiếu được sinh từ data.
- **Chế độ chạy text** (bỏ qua STT/TTS) để chấm logic agent nhanh: độ chính xác mã căn/giá, tỷ lệ `fact_check` khớp, đúng tool.
- **Chế độ chạy audio**: phát file WAV mẫu → đo WER của STT và độ trễ từ đầu đến cuối.
- Báo cáo: `eval/results/voice_report.md`.

## 9. Lộ trình triển khai

| Bước | Nội dung | Kết quả kiểm tra |
|---|---|---|
| 1 | Dọn project: bỏ các phần ở mục 1, viết migration mới | test cũ liên quan được gỡ, server chạy |
| 2 | Data demo + validator + import + bảng mới | validator 0 lỗi, import xong, đếm đủ bản ghi |
| 3 | Tầng truy xuất (SQL tools + hybrid search + phân giải alias) | unit test truy xuất |
| 4 | Agent (tool loop, prompt văn nói, chuẩn hóa văn nói, kiểm tra số, lưu thông tin khách) | eval chế độ text |
| 5 | Voice backend (`/voice/*`, STT, TTS, lưu ghi âm) | test API với file WAV |
| 6 | Giao diện cuộc gọi (VAD, phát theo câu, ngắt lời) | thử trên trình duyệt |
| 7 | Admin: cuộc gọi, khách, xuất JSON, banner demo | thử trên trình duyệt |
| 8 | Eval + báo cáo | `voice_report.md` |

Bước 5–6 cần `OPENROUTER_API_KEY` để chạy thật. Các bước còn lại có test chạy không cần key: STT, TTS và LLM được giả lập trong test.
