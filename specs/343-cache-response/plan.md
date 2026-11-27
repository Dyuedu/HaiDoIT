# Implementation Plan: Cache response của API thị trường, xóa theo snapshot

**Branch**: `gh-343-cache-response` | **Date**: 2026-11-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/343-cache-response/spec.md`

## Summary

Thêm một middleware ASGI thuần giữ response 200 của `GET /api/v1/*` trong RAM. Mỗi request hỏi `version()` của các nguồn; dấu đổi thì xóa cache. Request có `title` hoặc `have` không đi qua cache. Bật bằng `HAIDO_RESPONSE_CACHE=on`, prod bật. Đo lại bằng kịch bản của #342.

## Technical Context

**Language/Version**: Python 3.13, FastAPI 0.162, Starlette, anyio

**Primary Dependencies**: Không thêm.

**Storage**: Không đổi schema. Đọc thêm bảng `haido.snapshots` (một query mỗi request khi cache bật).

**Testing**: `uv run pytest tests/api/test_gh343_cache_response.py` (2 test cần `HAIDO_TEST_DATABASE_URL`).

## Constitution Check

- AC "snapshot đọc được mới nhất" của các route giữ nguyên: kiểm version ở mỗi request.
- Không giữ dữ liệu người dùng gõ (#150 không ghi chức danh; #205 hồ sơ ở trình duyệt).
- AD-7: `version()` chỉ đọc `snapshots`, không đọc `job_*`.
- Mặc định tắt trong mã, prod bật trong compose, như `SOURCE_ENV` (#309).

## Project Structure

```text
haido_api/
├── response_cache.py      # Mới: ResponseStore (LRU theo version), ResponseCache (middleware)
├── main.py                # create_app(response_cache=, cache_max_entries=), đọc HAIDO_RESPONSE_CACHE
├── market_source.py       # Protocol thêm version()
├── fake_market.py         # version() = "fake"
└── stat_market.py         # version() đọc bảng snapshots

deploy/
├── compose.prod.yml       # HAIDO_RESPONSE_CACHE: "on"
└── compose.loadtest.yml   # HAIDO_RESPONSE_CACHE: ${HAIDO_RESPONSE_CACHE:-on}

tests/api/
└── test_gh343_cache_response.py   # Mới

specs/343-cache-response/
└── ket-qua-do.md          # Mới: đo lại
```

Spec cũ cập nhật vì file của chúng bị đụng (ghi một đợt trong `tdd.md`, AC không đổi): #309 (`compose.prod.yml`, `market_source.py`, `fake_market.py`, `stat_market.py`), #342 (`compose.loadtest.yml`), #150 (`main.py`), #205 (`main.py`), #328 (`stat_market.py`, `fake_market.py`, `market_source.py`).

## Complexity Tracking

Không có vi phạm.

**Cập nhật 2026-11-27 (#230)**: các file sau của issue này được #230 sửa thêm, hành vi không đổi: `deploy/compose.loadtest.yml`, `deploy/compose.prod.yml`, `haido_api/fake_market.py`, `haido_api/main.py`, `haido_api/market_source.py`, `haido_api/stat_market.py`. Xem `specs/230-hinh-soi-tin/plan.md`.
