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

## Phase 4: Gộp main (đợt 3, 2026-11-15)

- [x] T022 Gộp `origin/main` bằng commit merge, giải chín xung đột giữ cả hai bên
- [x] T023 Thêm `learning_path` vào ba test dựng app của main; sinh lại `openapi.json` và hai fixture web của `data_engineer`
- [x] T024 Test quét 17 vai trò x cấp (`test_fr22_moi_vai_tro_cua_config_nhan_moi_cap_cua_config`)
- [x] T025 Test trước: kỳ vọng "2 trên 13"; rồi đưa `spark`, `airflow`, `pandas` trở lại trong `fake_market.json` và `fake_learning_path.json`

## Đợt 5 (2026-11-16, review #138)

- [x] T026 Test trước (`tests/core/test_fr23_prepared_text.py`): `％`, `²`, `①`, chữ số toàn chiều; "phần trăm" viết hoa, NFD, nhiều dấu cách, NBSP, xuống dòng; "Java 17," và "(HTML5)" vẫn qua
- [x] T027 `haido_core/vocab/prepared_text.py`: chuẩn hóa NFKC trước mọi kiểm tra, "phần trăm" bằng `phần\s+trăm` trên văn bản casefold; cập nhật docstring

## Thay đổi sau merge (2026-11-17, #166)

#166 sửa file dùng chung với issue này (thêm phép thứ năm `skill_roles`; `learning_path` và `skill_rates` giả không đổi). Hành vi và AC của issue này không đổi. Chi tiết: `specs/166-hinh-ky-nang-theo-vai-tro/plan.md`.

## Thay đổi đợt 2 (2026-11-17, #166)

#166 đợt 2 sửa thêm file dùng chung với issue này (`haido_core/domain/envelope.py` (cỡ mẫu của `skill_rate`, hook `check_against_meta`), `haido_api/fake_market.py`, `fixtures/fake_market.json`, `schemas/market.py`, `routes/market.py`). Hành vi và AC của issue này không đổi. Chi tiết: `specs/166-hinh-ky-nang-theo-vai-tro/plan.md`.

## Thay đổi sau merge (2026-11-25, #217)

- [x] `web/lib/learning-path.ts` kiểm envelope chặt hơn; chi tiết ở `specs/217-man-lo-trinh/`.

## Đợt B của #217 (2026-11-25)

- [x] Test chủ đề, chặng chọn một, validator
- [x] Schema, `topic_stages`, `build_stages`, bản giả, fixture web, openapi

- [x] T-230 Cập nhật 2026-11-27 theo #230: thêm nguồn `posting_check` (và các mục cộng thêm) vào các file của issue này; kiểm bằng `tdd.md` mục "Đợt sửa 2026-11-27"
