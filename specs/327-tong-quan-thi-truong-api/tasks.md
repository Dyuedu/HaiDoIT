# Tasks: Hình response của toàn cảnh thị trường và dữ liệu giả

**Input**: `specs/327-tong-quan-thi-truong-api/`

## Phase 1: Test

- [x] T001 Viết `tests/api/test_ad22_market_overview.py`: hàm dựng (cấp bậc, vai trò, ẩn số, nơi, mốc số năm, số đếm lệch), route bản giả, fixture web. Chạy, ghi RED.

## Phase 2: Code

- [x] T002 Thêm schema vào `haido_api/schemas/market.py`.
- [x] T003 Viết `haido_api/market_overview.py`.
- [x] T004 Thêm `market_overview` vào `MarketReadModel`, `FakeMarket`, route; mục `market_overview` trong fixture.
- [x] T005 Sinh `web/tests/fixtures/market-overview.json` và `docs/api/openapi.json`; viết mục route trong `docs/api/envelope-meta.md`.
- [x] T006 Chạy `uv run pytest -q`, `uv run ruff check .`; ghi GREEN.
