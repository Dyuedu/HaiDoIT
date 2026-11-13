# Tasks: Lọc bản đồ theo số năm kinh nghiệm

**Input**: `specs/280-loc-so-nam-kinh-nghiem/` (spec.md, plan.md, data-model.md)

Test đứng trước code. Mỗi test mới phải đỏ trước khi có code (ghi trong tdd.md).

## Phase 1: Tests (RED)

- [x] T001 `tests/core/test_ad10_rules_config.py`: `years_options` đọc từ config; sai (âm, trùng, không tăng, không phải số nguyên) thì `ConfigError` tiếng Việt
- [x] T002 `tests/domain/test_fr33_aggregate_years.py`: mốc N đếm `years_min ≤ N`; `any` bằng số cũ; `years_unstated`; cấp × số năm; tổng tỷ trọng bằng 1; n = 0 rơi vào `unknown`
- [x] T003 `tests/steps/test_ad4_ingest.py`: `PlannedFact`/`FactVersion` mang `years_min`; đổi `years_min` thì có phiên bản mới
- [x] T004 `tests/steps/test_fr33_aggregate_years_step.py` (Postgres): ingest chép `years_experience_min`, aggregate ghi hàng `years` và `years_unstated`, mã ô và số khớp đếm tay
- [x] T005 `tests/api/test_fr33_city_shares_years.py`: route nhận `years`, 422 khi lạ, `data.years`, `data.years_unstated_cell_id` (ô `...ynone` trong `meta.cells`), mã ô `.y<N>`, mẫu nhỏ theo ô đang chọn; nguồn `stat` chọn snapshot có hàng của (cấp, số năm)
- [x] T006 `tests/deploy/test_gh280_bo_loc_so_nam_khop_config.py`: `YEARS_OPTIONS` của web = `any` + `years_options`, nhãn không rỗng, mặc định `any`
- [x] T007 `web/tests/fr33-years-filter.test.tsx`: lượt gọi đầu có `years=any`; bấm mốc gửi `years`; giữ `level` khi đổi số năm và ngược lại; dòng tin bị bỏ; khung chú thích nêu bộ lọc; response muộn bị bỏ; `data.years` lệch là không đọc được

## Phase 2: Implementation (GREEN)

- [x] T010 `config/rules.toml`, `haido_core/config.py`: `years_options`, `ANY_YEARS`, tăng `config_version`
- [x] T011 `haido_core/db/tables.py`, migration `0006_haido_years_filter`
- [x] T012 `haido_core/db/scraper_source.py`, `haido_core/steps/ingest.py`, `haido_core/db/snapshot_store.py`: chép và lưu `years_min`
- [x] T013 `haido_core/domain/population.py`, `haido_core/domain/aggregate.py`, `haido_core/steps/aggregate.py`: ô và tỷ trọng theo số năm, `years_unstated`
- [x] T014 `haido_api/schemas/market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fake_market.py`, fixture; sinh lại `docs/api/openapi.json`
- [x] T015 `web/lib/labels.ts`, `city-shares.ts`, `city-shares-view.ts`, `years-chips.tsx`, `map-screen.tsx`, `share-bars.tsx`, `share-table.tsx`, `snapshot-caption.tsx`, fixture web
- [x] T008 `tests/db/test_fr33_stat_years.py`: migration 0006 (head, cột, khóa, không có giá trị mặc định, hạ cấp giữ hàng `any`). Viết sau migration, không có lượt RED riêng (xem tdd.md)
- [x] T009 Sửa test cũ của #93, #163, #4 cho cột `years` và tham số `years` (đọc hàng `any`, đếm nhân 6, URL có `years=any`)
- [x] T016 Chạy toàn bộ: `uv run pytest -q`, `uv run ruff check .`, `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7`, `uv run alembic heads`, `npm --prefix web run lint`, `npm --prefix web run test`, `npm --prefix web run build`

## Phase 3: Sau merge

- [x] T020 Lượt đêm đầu tiên sau deploy: log bước kho không lỗi, `GET /api/v1/city-shares?role=all&level=entry&years=1` trả 200 và có `years_unstated_cell_id` trỏ tới một ô của `meta.cells`
