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
  python tools/gates/check_gates.py --require AD-1 AD-17 AD-25
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
