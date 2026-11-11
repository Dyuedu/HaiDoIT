# Tasks: Hình response của lộ trình học và dữ liệu giả

**Input**: `specs/212-hinh-lo-trinh-hoc/`. Test viết trước, chạy đỏ, ghi `tdd.md`.

## Phase 1: Test

- [x] T001 [US1] Test schema và validator (`tests/api/test_fr22_learning_path.py`)
- [x] T002 [US1] Test route: hình, thứ tự FR-22, `have` (cờ, đếm, `current_stage`, `have_ignored`, trùng, rỗng, 422), `not_ready`, quay về ô
- [x] T003 [US2] Test dữ liệu giả: mã thuộc danh sách mồi, snake_case, lời dẫn không số, tỷ lệ bằng `skill-rates`, vai trò sẵn sàng và `not_ready`
- [x] T004 [US1] Test tất định (`@pytest.mark.determinism`), route có trong `SAMPLE_QUERY`, nguồn chọn riêng
- [x] T005 [US2] Fixture web khớp response (`test_ad17_web_fixtures.py`, `web/tests/fr22-learning-path-fixture.test.ts`)

## Phase 2: Implementation

- [x] T006 `haido_api/schemas/learning_path.py`
- [x] T007 `haido_api/learning_path.py` (áp `have`)
- [x] T008 `fake_learning_path.json`, đổi mã `skill_rates` sang snake_case, thêm hàng cho đủ lộ trình
- [x] T009 `market_source.py`, `fake_market.py`, `stat_market.py` (UnknownCell), `routes/market.py`
- [x] T010 `web/lib/learning-path.ts`, fixture web
- [x] T011 Sinh lại `openapi.json`, cập nhật `envelope-meta.md`, docstring `SkillRateRow.skill`
- [x] T012 Cập nhật `create_app` ở các test cũ; `specs/144`, `specs/163`, `specs/205`

## Phase 2b: Sửa theo review (đợt 2, 2026-11-12)

Test trước, chạy đỏ, ghi `tdd.md` đợt 2.

- [x] T014 [F3] Test `Ordinal` (`tests/domain/test_ad17_ordinal.py`) và danh sách trường (`tests/api/test_ad17_ordinal_allowlist.py`); sửa `envelope.py`, docstring, hai dòng trống
- [x] T015 [F1, F2] Test quét vai trò × cấp, `cell_id` ở trong vai trò, null_data của data_engineer, quay về của backend intern; sửa `fake_market.py`, `fake_market.json`
- [x] T016 [F4, F5, F11] Test nhóm và lộ trình, `foundation_for` bắc cầu, đồ thị (`test_fr22_learning_path_graph.py`, `..._review.py`); sửa `learning_path.py`, `schemas/learning_path.py`
- [x] T017 [F7, F12] Test lời dẫn và tiêu đề tài nguyên (`test_fr23_prepared_text.py`, `test_fr23_blurbs.py`); thêm `haido_core/vocab/prepared_text.py`, viết lại lời dẫn, đổi link
- [x] T018 [F8] Test web (`learningPathUrl` bỏ trùng và mã sai, `retryable` của 422); sửa `web/lib/learning-path.ts`
- [x] T019 [F6, F10] Fixture web `learning-path-backend.intern`, `-data_engineer-have`, `-ai_ml`; `test_ad17_web_fixtures.py`
- [x] T020 [F9] Test 201 mã thô, `have` lặp, mô tả OpenAPI; sinh lại `openapi.json`
- [x] T021 [F13, F14, F15] Cập nhật `spec.md`, `envelope-meta.md`, `specs/144`, `specs/163`, `specs/205`

## Phase 3: Sau merge

- [ ] T013 Comment hợp đồng lên #212 cho người làm #213, #216, #217, #218, #220, #221
