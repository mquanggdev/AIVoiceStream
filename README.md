# Ocean Park Voice Agent

Trợ lý tư vấn căn hộ **Vinhomes Ocean Park** giao tiếp **hoàn toàn bằng giọng nói**, trải nghiệm như một cuộc gọi điện:
khách bấm "Gọi tư vấn", nói tự nhiên, agent trả lời bằng giọng nói, tra đúng mã căn và giá từ bảng hàng,
ghi nhận tên và SĐT khách nói ra để admin xem. Mọi cuộc gọi được lưu (transcript Khách/AI + ghi âm) để đánh giá.

> Bản này được cải tạo từ dự án chatbot C2-App-005. Thiết kế đầy đủ: [docs/voice_agent_design.md](docs/voice_agent_design.md).
> Đặc tả dữ liệu cho tool crawl: [docs/data_spec_v3.md](docs/data_spec_v3.md).

## Kiến trúc

```
Trình duyệt ── micro → VAD (tự nhận ngắt câu) → WAV ──► POST /api/v1/voice/turn
            ◄── NDJSON: từng câu MP3, phát ngay, cho phép ngắt lời ──┘
FastAPI ── STT (OpenRouter) → Agent LLM + tool calling → chuẩn hóa văn nói → TTS (OpenRouter)
        └─ tools: SQL trên bảng hàng (mã căn, giá, diện tích) + hybrid search tài liệu (BM25 + embedding)
SQLite/PostgreSQL ── conversations / messages (kèm ghi âm data/recordings/) / customers / catalog
```

| Thành phần | Vị trí |
|---|---|
| Agent (prompt văn nói, tools, kiểm tra số liệu, vòng lặp LLM) | `src/agent/` |
| Truy xuất: nhận diện tên nghe nhầm, SQL bảng hàng, tìm tài liệu | `src/retrieval/` |
| Giọng nói: STT, TTS, pipeline cuộc gọi, ghi âm | `src/voice/` |
| Đọc số / mã căn / SĐT thành lời, chuẩn hóa SĐT | `src/core/` |
| Import + kiểm tra data v3 | `src/dataset/`, `scripts/validate_data.py`, `scripts/import_data.py` |
| API voice + admin | `src/api/voice.py`, `src/api/admin.py` |
| Giao diện cuộc gọi | `FE/src/components/call-widget.tsx`, `FE/src/lib/voice/` |
| Trang admin (cuộc gọi, nghe lại, khách) | `FE/src/app/admin/` |
| Data demo + script sinh | `cleaned_data/demo_v3/`, `scripts/demo_data/` |
| Đánh giá agent | `eval/run_voice_eval.py` |

## Chạy local

Yêu cầu: Python 3.11+, Node 20+, **key OpenRouter** (một key dùng cho STT, LLM, TTS, embedding).

```bash
cp .env.example .env          # rồi điền OPENROUTER_API_KEY
```

```bash
python -m venv .venv && .venv/Scripts/python -m pip install -e ".[dev]"
```

```bash
.venv/Scripts/python -m uvicorn src.main:app --reload --port 8000
```

```bash
cd FE && npm install && npm run dev -- -p 3001
```

- Website + nút **Gọi tư vấn**: http://localhost:3001 (dùng **Chrome/Edge**, cho phép micro, nên đeo tai nghe)
- Admin: http://localhost:3001/admin/login (tài khoản theo `ADMIN_EMAIL` / `ADMIN_PASSWORD` trong `.env`)
- API docs: http://localhost:8000/docs

Khi khởi động, backend tự tạo bảng và import bộ data trong `DATASET_DIR` (mặc định data demo).

Tùy chọn: tính embedding cho tài liệu (cải thiện câu hỏi định tính; không có thì dùng BM25):

```bash
.venv/Scripts/python scripts/import_data.py --embed-only
```

## Dữ liệu

- **Hiện tại dùng DATA DEMO** (`cleaned_data/demo_v3`): 12 phân khu, 35 tòa, 15.058 căn, 25 chính sách, 95 tài liệu (~17.000 từ).
  Mã căn, giá, trạng thái là **giả lập** để test; admin luôn hiện banner "ĐANG DÙNG DATA DEMO".
- Sinh lại data demo: `python scripts/demo_data/build_demo_data.py`
- **Chuyển sang data thật**: đặt vào `cleaned_data/v3/` theo [đặc tả v3](docs/data_spec_v3.md), rồi:

```bash
.venv/Scripts/python scripts/validate_data.py cleaned_data/v3
```

```bash
.venv/Scripts/python scripts/import_data.py --dataset cleaned_data/v3 --embed
```

  và đổi `DATASET_DIR=cleaned_data/v3` trong `.env`. Không cần sửa code.

## Kiểm thử và đánh giá

```bash
.venv/Scripts/python -m pytest tests -q        # không cần key: STT/TTS/LLM được giả lập
```

```bash
.venv/Scripts/python eval/run_voice_eval.py    # cần key: 21 case sinh từ data → eval/results/voice_report.md
```

Mỗi cuộc gọi trong admin có nút **Xuất JSON đánh giá** (transcript Khách/AI, ghi âm, độ trễ STT/LLM/TTS, tool đã gọi, kết quả kiểm tra số liệu).

## Biến môi trường chính

| Biến | Ý nghĩa | Mặc định |
|---|---|---|
| `OPENROUTER_API_KEY` | Key OpenRouter (bắt buộc để gọi được) | — |
| `LLM_MODEL` | Model agent (cần tool calling) | `openai/gpt-4.1-mini` |
| `STT_MODEL` | Nhận dạng giọng nói | `openai/whisper-large-v3-turbo` |
| `TTS_MODEL`, `TTS_VOICE` | Đọc thành giọng nói | `elevenlabs/eleven-flash-v2.5`, `sarah` |
| `EMBEDDING_MODEL` | Embedding tài liệu | `openai/text-embedding-3-small` |
| `DATASET_DIR` | Bộ data được import | `cleaned_data/demo_v3` |
| `RECORDINGS_DIR` | Nơi lưu ghi âm cuộc gọi | `data/recordings` |

Nếu TTS không đọc được (lỗi model/mạng), trình duyệt tự đọc bằng giọng tiếng Việt có sẵn; khi đó không lưu được file ghi âm phía AI.

## Team

| Member | Role |
|---|---|
| YenPhuong | AI/RAG/Evaluation |
| MinhQuang | FE/BE/Integration |

## License

MIT
