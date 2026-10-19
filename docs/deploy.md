# Deploy: Render (backend) + Vercel (frontend)

```
Trình duyệt ──HTTPS──► Vercel (Next.js, thư mục FE/)
     │
     └──HTTPS──► Render Web Service (Docker, FastAPI) ──► Render PostgreSQL
                                   └──► OpenRouter (STT, LLM, TTS, embedding)
```

Deploy **backend trước** để có URL API, rồi mới deploy frontend.

## 1. Backend trên Render

Repo đã có sẵn [render.yaml](../render.yaml) (Blueprint): 1 web service chạy `Dockerfile` và 1 database PostgreSQL, cùng region Singapore, gói free.

1. Vào https://dashboard.render.com → **New** → **Blueprint** → kết nối GitHub, chọn repo `AIVoiceStream`, nhánh `main`.
2. Render đọc `render.yaml` và hỏi các biến bí mật:

   | Biến | Giá trị |
   |---|---|
   | `OPENROUTER_API_KEY` | Key OpenRouter |
   | `ADMIN_EMAIL` | Email đăng nhập trang admin |
   | `ADMIN_PASSWORD` | Mật khẩu admin, **≥ 12 ký tự**, không dùng mật khẩu mặc định |
   | `CORS_ORIGINS` | Domain Vercel, vd. `https://aivoicestream.vercel.app`. Chưa biết thì điền tạm rồi sửa sau bước 2 |

   `JWT_SECRET_KEY` do Render tự sinh; `DATABASE_URL` tự nối với database.
3. Bấm **Apply**. Lần đầu build khoảng 3–5 phút. Khi khởi động, container sẽ:
   - chạy `alembic upgrade head` để tạo bảng;
   - import data demo (khoảng 6 giây);
   - tạo tài khoản admin;
   - tính embedding tài liệu chạy nền (khoảng $0,0001).
4. Kiểm tra: mở `https://<tên-service>.onrender.com/ready`, phải thấy `{"status":"ready","database":"ok"}`.
   URL API dùng cho frontend là `https://<tên-service>.onrender.com/api/v1`.

## 2. Frontend trên Vercel

1. Vào https://vercel.com/new → import repo `AIVoiceStream`.
2. **Root Directory**: chọn `FE`. Framework tự nhận Next.js, giữ nguyên lệnh build.
3. **Environment Variables**: `NEXT_PUBLIC_API_URL` = `https://<tên-service>.onrender.com/api/v1`.
4. Bấm **Deploy**.
5. Lấy domain Vercel vừa cấp, quay lại Render → service → **Environment** → sửa `CORS_ORIGINS` cho đúng domain đó. Render sẽ tự deploy lại.
   Preview deploy (`aivoicestream-git-…vercel.app`) đã được cho phép qua `CORS_ORIGIN_REGEX`. Nếu đặt tên project Vercel khác `aivoicestream`, sửa regex này.

> `NEXT_PUBLIC_API_URL` được gắn vào code lúc build: đổi giá trị thì phải **Redeploy** trên Vercel.

## 3. Kiểm tra sau deploy

- Mở domain Vercel → **Gọi tư vấn** → cho phép micro → agent chào. Trình duyệt chỉ cho dùng micro trên HTTPS; cả Vercel và Render đều có sẵn HTTPS.
- Mở `/admin`, đăng nhập bằng `ADMIN_EMAIL` / `ADMIN_PASSWORD` → thấy cuộc gọi vừa rồi, bấm nghe lại được ghi âm.
- Gặp lỗi CORS trong console: kiểm tra `CORS_ORIGINS` khớp chính xác domain, có `https://`, không có `/` ở cuối.

## Lưu ý gói free của Render

| Giới hạn | Ảnh hưởng | Cách xử lý |
|---|---|---|
| Web service **ngủ sau 15 phút** không có request | Cuộc gọi đầu tiên sau khi ngủ phải chờ khoảng 50 giây | Mở `/ready` trước khi demo, hoặc nâng gói Starter |
| **Không có ổ đĩa bền** | File ghi âm trên đĩa sẽ mất khi restart | Đã đặt `RECORDINGS_STORAGE=db`: ghi âm lưu trong PostgreSQL |
| PostgreSQL free **hết hạn sau 30 ngày**, dung lượng 1 GB | Mất dữ liệu cuộc gọi khi database hết hạn | Nâng gói database trước khi hết hạn nếu cần giữ dữ liệu |

## Biến môi trường production (tham khảo)

| Biến | Giá trị trên Render |
|---|---|
| `APP_ENV` | `production`: bắt buộc Postgres, JWT secret mạnh, mật khẩu admin mạnh, CORS không chứa localhost |
| `DATABASE_URL` | Lấy từ database. `postgres://…` được tự đổi sang driver `psycopg` |
| `AUTO_CREATE_TABLES` | `false`, bảng được tạo bằng Alembic |
| `RECORDINGS_STORAGE` | `db` |
| `AUTO_EMBED_KNOWLEDGE` | `true` |
| `CORS_ORIGINS`, `CORS_ORIGIN_REGEX` | Domain Vercel |
| `PORT` | Render tự cấp, `Dockerfile` tự đọc |
