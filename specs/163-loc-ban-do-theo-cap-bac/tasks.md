# Tasks: Lọc bản đồ theo cấp bậc

**Input**: Design documents from `specs/163-loc-ban-do-theo-cap-bac/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Mỗi test phải đỏ vì đúng lý do trước khi có code.

## Phase 1: Setup

- [x] T001 Tạo `specs/163-loc-ban-do-theo-cap-bac/` với sáu file; tra các issue đã đụng tới file sắp sửa (`specs/100-cross-source-clusters`, `specs/205-khoa-ho-so-trinh-duyet`)

## Phase 2: Foundational - config và bảng

### Tests

- [x] T002 [P] Test cấu hình `level_options` và `level_groups` (đủ, thiếu, sai) trong `tests/core/test_ad10_rules_config.py`
- [x] T003 [P] Test migration 0005: cột `seniority`, khóa chính, hàng cũ nhận `all`, một head, trong `tests/db/test_fr33_stat_city_shares_level.py`

### Implementation

- [x] T004 Thêm `level_options`, `level_groups` vào `config/rules.toml` và `haido_core/config.py`, tăng `config_version`
- [x] T005 Viết `haido_core/db/migrations/versions/0005_haido_city_share_level.py`, cập nhật `haido_core/db/tables.py`

## Phase 3: User Story 2 - Số theo cấp (Priority: P1)

### Tests

- [x] T006 [P] [US2] Test hàm thuần: ô và tỷ trọng theo cấp, nhóm cộng từ cấp, tổng bằng 1, n = 0 rơi vào `unknown`, thứ tự cố định, trong `tests/domain/test_fr33_aggregate_level.py`
- [x] T007 [P] [US2] Test bước `aggregate`: hàng theo cấp trong DB, một transaction, chạy lại ra cùng hàng, trong `tests/steps/test_fr33_aggregate_level_step.py`; sửa các số đếm hàng trong `tests/steps/test_dat20_aggregate_step.py`
- [x] T008 [P] [US2] Test API: `level` mặc định, cấp lạ 422, `data.level`, mã ô, `unknown_cell`, mẫu nhỏ theo n của cấp, nguồn giả, trong `tests/api/test_fr33_city_shares_level.py`; sửa stub nguồn trong `tests/api/test_ad17_routes.py`, `tests/api/test_dat20_stat_market.py`, `tests/api/test_ad17_web_fixtures.py`

### Implementation

- [x] T009 [US2] `haido_core/domain/aggregate.py`: `seniority` trên `CellRow` và `ShareRow`, tham số `level_options` và `level_groups`
- [x] T010 [US2] `haido_core/steps/aggregate.py` và `haido_core/db/snapshot_store.py` ghi hàng theo cấp
- [x] T011 [US2] `haido_api/schemas/market.py` (`data.level`), `market_source.py`, `routes/market.py` (`level`), `stat_market.py` đọc theo (role, level)
- [x] T012 [US2] `haido_api/fake_market.py` và `fixtures/fake_market.json` phục vụ `entry` và `all`; sinh lại `web/tests/fixtures/city-shares-*.json` và `docs/api/openapi.json`
- [x] T013 [US2] Cập nhật `docs/api/envelope-meta.md`

## Phase 4: User Story 1 và 3 - Bộ chọn trên web (Priority: P1)

### Tests

- [x] T014 [P] [US1] Test nhãn cấp của `web/lib/labels.ts` khớp config, trong `tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py`
- [x] T015 [P] [US1] [US2] [US3] Test web: mặc định `entry`, đổi cấp đổi cả thanh và bảng, bỏ response muộn, mờ theo cấp, `unknown_cell`, bàn phím, trong `web/tests/fr33-level-filter.test.tsx`; sửa `fr33-map-screen.test.tsx`, `ad17-city-shares-client.test.ts`, helper và fixture

### Implementation

- [x] T016 [US1] `web/lib/labels.ts`: `LEVEL_OPTIONS`, `DEFAULT_LEVEL`, `levelLabel`
- [x] T017 [US2] `web/lib/city-shares.ts`: `level` trong `fetchCityShares`, kiểm `data.level`
- [x] T018 [US1] `web/app/components/map/level-chips.tsx` và gắn vào `map-screen.tsx` (đổi cấp, bỏ response muộn); `web/lib/city-shares-view.ts` ghi nhãn cấp vào tiêu đề

## Phase 5: Polish

- [x] T019 Cập nhật `specs/100-cross-source-clusters/` và `specs/205-khoa-ho-so-trinh-duyet/` (cùng commit)
- [x] T021 Sửa sau review (đợt 7 của `tdd.md`): `stat_market.py` chọn snapshot theo cấp (F1), `config.py` kiểm dạng tên nhóm và mã (F2), `aggregate.py` từ chối thành viên trùng (F3), migration 0005 hạ cấp bỏ cả `stat_cells` theo cấp (F4), test web caption và `aria-describedby` (F5), test dòng chú thích khớp config (F6)
- [x] T020 Chạy toàn bộ: `uv run pytest -q`, hai lần `-m determinism` (`PYTHONHASHSEED=0` và `1`), `uv run ruff check .`, `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11`, `uv run alembic heads`, `npm run lint`, `npm run test`, `npm run build` trong `web/`

## Thay đổi sau merge (2026-11-12, #212)

#212 (hình response lộ trình học) sửa các file dùng chung với issue này, qua hai đợt (đợt 2 là sửa theo review). Hành vi của issue này không đổi.

- `haido_api/market_source.py`, `fake_market.py`, `stat_market.py`, `routes/market.py`: thêm phép `learning_path` và biến chọn nguồn `HAIDO_MARKET_SOURCE_LEARNING_PATH`; `create_app` đòi nguồn cho phép này (do `SOURCE_ENV` ở `routes/market.py`). `main.py` không đổi.
- `haido_api/fixtures/fake_market.json`: mã trong `skill_rates` đổi sang snake_case, thêm và đổi hàng `skill_rates` (đợt 2: `data_engineer/entry` về `vn.data_engineer`, thêm `backend/intern`). Không đụng `cells` hay `newcomer_roles`.
- `docs/api/openapi.json`, `docs/api/envelope-meta.md`: thêm route `learning-path` và ngoại lệ `Ordinal`.
- `tests/api/test_ad17_routes.py`, `test_ad17_web_fixtures.py`, `test_dat20_stat_market.py`, `test_fr33_city_shares_level.py`, `tests/steps/test_dat20_api_end_to_end.py`: thêm nguồn `learning_path` vào các lời gọi `create_app`, thêm route vào `SAMPLE_QUERY` và danh sách yêu cầu của test `display`.
