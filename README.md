# HaiDoIT

Hải Đồ IT — Khung hiển thị và phân tích nhu cầu kỹ năng thị trường CNTT Việt Nam từ tin tuyển dụng.

## Cài đặt ban đầu (Setup)

Cài đặt phụ thuộc cho Python và Web:

```bash
# Cài đặt phụ thuộc Python (bao gồm dev tools: pytest, ruff, alembic)
uv sync

# Cài đặt phụ thuộc Web (Next.js, React, Tailwind)
npm --prefix web ci
```

## Khởi chạy môi trường phát triển (Local Dev)

### 1. Chạy dịch vụ cục bộ qua Docker Compose
Khởi động cụm Postgres 18.6, API FastAPI và Web Next.js:

```bash
docker compose -f deploy/compose.local.yml up -d --wait
```

Dịch vụ sẵn sàng tại:
- Web: http://localhost:3000
- API (OpenAPI docs): http://localhost:8000/docs
- Postgres: 127.0.0.1:5433 (user: `haido`, password: `haido_local`, db: `haido`)

Dừng dịch vụ:
```bash
docker compose -f deploy/compose.local.yml down
```

### 2. Di trú cơ sở dữ liệu (Alembic)
Di trú chạy trên Postgres local (cổng 5433):

**Trên PowerShell (Windows):**
```powershell
$env:HAIDO_DATABASE_URL="postgresql+psycopg://haido:haido_local@localhost:5433/haido"
uv run alembic upgrade head
```

Quay về base trên PowerShell:
```powershell
uv run alembic downgrade base
```

**Trên Bash (Linux/macOS):**
```bash
HAIDO_DATABASE_URL=postgresql+psycopg://haido:haido_local@localhost:5433/haido uv run alembic upgrade head
HAIDO_DATABASE_URL=postgresql+psycopg://haido:haido_local@localhost:5433/haido uv run alembic downgrade base
```

### 3. Chạy từng tầng độc lập cho phát triển hằng ngày

- **API:**
  > **Lưu ý:** Nếu container `api` trong Docker Compose đang chạy, nó sẽ chiếm cổng 8000. Dừng container API trước khi chạy uvicorn tại chỗ: `docker compose -f deploy/compose.local.yml stop api`.
  ```bash
  uv run uvicorn haido_api.main:app --host 127.0.0.1 --port 8000 --reload
  ```

- **Web (giao diện Next.js):**
  > **Lưu ý:** Web đọc `API_BASE_URL` lúc chạy để proxy sang backend (mặc định là `http://localhost:8000`). Nếu API chạy ở cổng khác, đặt biến `API_BASE_URL` trước khi chạy.
  ```bash
  npm --prefix web run dev
  ```

### 4. Chốt snapshot và vòng đời tin (CLI, Story 1.4)

Hai bước chạy tay, mỗi bước là một hàm ở `haido_core/steps/`, không dùng Dagster:

| Lệnh | Việc làm |
|---|---|
| `uv run python -m haido_core.cli ingest --snapshot S` | Mở snapshot S (trạng thái `open`), chép lượt chạy, quan sát và dữ kiện tin (chức danh, công ty, địa điểm, cấp bậc) của S từ bảng của scraper. Chỉ thêm; chạy lại cho S đang `open` không sinh hàng trùng. |
| `uv run python -m haido_core.cli lifecycle --snapshot S` | Tính số lần thấy, ngày thấy đầu và cuối, số lần đăng lại, `absent`, `in_window` bằng `domain.lifecycle.job_lifecycle`, ghi `stat_job_lifecycle` kèm `config_version`. |

Dữ kiện tin lấy từ hàng `jobs` của scraper tại lúc ingest, nên ngày chạy bù chỉ nhận dữ kiện hiện tại cho các tin chưa từng được thấy ở snapshot sau đó.

`S` có dạng `YYYY-MM-DD` theo `Asia/Ho_Chi_Minh`; bỏ trống thì lấy hôm nay. S đã `published` hoặc `partial` thì cả hai lệnh từ chối (mã thoát 1, không ghi gì). `window_days` và danh sách nguồn tự động đọc từ `config/rules.toml`.

Biến môi trường:

- `HAIDO_SCRAPER_DATABASE_URL`: nguồn, bảng của scraper (`jobs`, `job_observations`, `source_runs`). Chỉ `SELECT`, kết nối đặt chỉ-đọc ở phía DB. Dạng `postgresql://...` như `DATABASE_URL` của scraper cũng được.
- `HAIDO_DATABASE_URL`: đích, schema `haido` (tạo bằng `alembic upgrade head`), dạng `postgresql+psycopg://...`.
- `HAIDO_ALLOW_REMOTE_WRITE=1`: bắt buộc nếu đích có host ngoài `localhost`, `127.0.0.1`, `postgres` (ví dụ Supabase). Không đặt cờ thì lệnh từ chối và không ghi.

Nạp từ Supabase chỉ-đọc vào Postgres local (máy dev):

```bash
export HAIDO_SCRAPER_DATABASE_URL='postgresql://postgres.<ref>:<mật khẩu>@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres'
export HAIDO_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido
uv run alembic upgrade head
uv run python -m haido_core.cli ingest --snapshot 2026-11-05
uv run python -m haido_core.cli lifecycle --snapshot 2026-11-05
```

> **Lưu ý:** `pyproject.toml` khai báo `haido = "haido_core.cli:main"` nhưng dự án chưa đóng gói, nên `uv sync` chưa cài lệnh `haido`. Dùng `python -m haido_core.cli` như trên. Trên Windows, dùng `127.0.0.1` thay `localhost` cho Postgres local (cổng 5433 chỉ mở IPv4, `localhost` thử IPv6 trước và chờ rất lâu).
> Story này chưa chạy migration hay ghi gì lên Supabase.

Kiểm thử có marker `postgres` cần Postgres thật. Với Postgres local ở `deploy/compose.local.yml`:

```bash
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test uv run pytest -q
```

Tạo DB test một lần trong Postgres của compose:

```bash
docker compose -f deploy/compose.local.yml exec -T postgres psql -U haido -d haido -c "CREATE DATABASE haido_test"
```

Mỗi test dựng lại schema `haido` và bảng scraper trong DB đó, nên chỉ trỏ vào DB riêng cho test (không dùng DB `haido`; tên DB phải kết thúc bằng `_test`, nếu không test từ chối chạy). Không đặt biến thì test `postgres` bị bỏ qua; trong CI (`CI=true`) thiếu biến thì đỏ.

## Kiểm thử và cổng chất lượng

- Chạy toàn bộ kiểm thử:
  ```bash
  uv run pytest -q
  ```
- Kiểm tra ruff linting:
  ```bash
  uv run ruff check .
  ```
- Kiểm tra các cổng kiến trúc (AD-24):
  ```bash
  python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7
  ```
- Kiểm tra lint & build web:
  ```bash
  npm --prefix web run lint
  npm --prefix web run build
  ```
- Chạy kiểm thử web (Vitest + Testing Library, trong jsdom; không cần API hay Docker). Cần Node `^22.22.2` hoặc `>=24.15.0` (yêu cầu của jsdom 30, ghi ở `engines` của `web/package.json`):
  ```bash
  npm --prefix web run test
  ```
  Chạy một file hoặc lọc theo tên test (tên test chứa mã FR/AD, ví dụ `fr33`):
  ```bash
  npm --prefix web run test -- tests/fr33-map-screen.test.tsx
  npm --prefix web run test -- -t fr36
  ```
