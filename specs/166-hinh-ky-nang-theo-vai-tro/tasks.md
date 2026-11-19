# Tasks: Hình response của một kỹ năng qua các vai trò và dữ liệu giả

**Input**: Design documents from `specs/166-hinh-ky-nang-theo-vai-tro/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi viết code.

## Phase 1: Test

- [x] T001 [US1] Test schema `SkillRoleRow`, `SkillRolesData` (loại, `cell_id`, vai trò lặp, rỗng, thứ tự, `mentioned`) trong `tests/api/test_fr09_skill_roles.py`
- [x] T002 [US1] Test route: hình, nhãn kỹ năng, `display` khớp `suppression_for`, `meta.cells`, 404 `unknown_skill`, 404 `unknown_cell`, 422
- [x] T003 [US2] Test dữ liệu giả: đủ 17 vai trò, số nhắc không vượt n, share = nhắc / n, các trường hợp của `python`, xếp hạng `figma`, `abap` không ai nhắc, `mentioned` tính cả ô bị ẩn, thứ tự, DEC-6
- [x] T004 [US3] Test nguồn: biến môi trường, thiếu nguồn là lỗi khởi động, `StatMarket` từ chối, compose không đặt `stat`
- [x] T005 [US1] Thêm route vào `SAMPLE_QUERY` và danh sách yêu cầu kiểm `display` trong `tests/api/test_ad17_routes.py`; thêm nguồn `skill_roles` vào các lời gọi `create_app` ở sáu file test khác
- [x] T006 [US2] Test fixture web khớp response trong `tests/api/test_ad17_web_fixtures.py` và kiểu TS trong `web/tests/fr09-skill-roles-fixture.test.ts`

## Phase 2: Implementation

- [x] T007 `find_seed_skill` trong `haido_core/vocab/skills.py`
- [x] T008 `SkillLabel`, `SkillRoleRow`, `SkillRolesData` trong `haido_api/schemas/market.py`
- [x] T009 `UnknownSkill`, phép `skill_roles` trong `haido_api/market_source.py`, handler trong `haido_api/errors.py`
- [x] T010 `SOURCE_ENV` và route `/skill-roles` trong `haido_api/routes/market.py`
- [x] T011 Mục `skill_roles` trong `haido_api/fixtures/fake_market.json`, `FakeMarket.skill_roles`, `StatMarket.skill_roles`
- [x] T012 `web/lib/skill-roles.ts`, sinh ba fixture web
- [x] T013 Sinh lại `docs/api/openapi.json`, cập nhật `docs/api/envelope-meta.md`

## Phase 3: Sau merge

- [ ] T014 Comment hợp đồng lên #166 cho người làm #168, #169, #170
- [x] T015 (#168, xong ở `specs/168-ky-nang-vai-tro-that/`) `StatMarket.skill_roles` đọc `stat_skill_rates`: `n_scanned` thành `n_by_measure.skill_count` của `meta.cells[vn.<role>.entry]` (`n` giữ là số tin của ô); `mentioned = n_with > 0` của hàng ô `vn.all` (mọi vai trò, mọi cấp); thứ tự dòng `null_data` theo `skill_count` (Envelope kiểm)

## Phase 4: Đợt 2 theo review (2026-11-17)

**Tests**: viết trước, chạy đỏ rồi mới sửa code (xem `tdd.md`).

- [x] T016 [US1] Test Envelope: cỡ mẫu `skill_rate` theo `skill_count`, loại khác theo `n`, hook `check_against_meta` (`tests/domain/test_ad17_envelope.py`)
- [x] T017 [US1] Test `data.level`, `mentioned = false` với dòng pha trộn, thứ tự dòng `null_data` theo cỡ mẫu của phép đo (`tests/api/test_fr09_skill_roles.py`)
- [x] T018 [US2] Test fixture: `mentions_all_levels`, ca `sap`, ca `game` (43 và 12), nhãn song ngữ `machine_learning`, chốt chống lệch, bộ nạp báo lỗi rõ, DEC-6 trên `data`
- [x] T019 [US3] Test deploy: prod `stat`, local `fake` (`tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py`), thay test compose cũ
- [x] T020 [US2] Test web: `rowN` theo `skill_count`, `level`, 422 không thử lại, hai fixture mới
- [x] T021 `haido_core/domain/envelope.py`: `SKILL_COUNT`, `sample_n`, hook `check_against_meta`
- [x] T022 `haido_api/schemas/market.py` (`level`, `check_against_meta`, docstring `mentioned`), `fake_market.py` (cấu trúc mới, `_check_skill_roles`), `fake_market.json`, `compose.prod.yml`
- [x] T023 `web/lib/skill-roles.ts`, sinh lại fixture web và `newcomer-roles.json`, sinh lại `openapi.json`, cập nhật `envelope-meta.md`
