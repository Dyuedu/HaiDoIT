# Tasks: Hình response của màn người mới và dữ liệu giả

**Input**: Design documents from `specs/144-hinh-nguoi-moi/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi viết code.

## Phase 1: Test

- [x] T001 [US1] Test `level_share` dưới ngưỡng ra `null_data` trong `tests/domain/test_ad17_display_policy.py`
- [x] T002 [US1] Test schema `NewcomerRolesData` (kind, cell_id, ô trùng, vai trò lặp, rows rỗng) trong `tests/api/test_fr37_newcomer_roles.py`
- [x] T003 [US1] Test route trả Envelope, có mục ô cho mọi dòng, dưới 30 tin là `null_data`
- [x] T004 [US2] Test dữ liệu giả: đủ vai trò của config, entry = Intern+Fresher+Junior, share = entry/n, đủ bốn trường hợp, thứ tự dòng
- [x] T005 [US1] Thêm route vào `SAMPLE_QUERY`, nguồn `newcomer_roles` vào các lời gọi `create_app` trong `tests/api/test_ad17_routes.py`, `tests/api/test_dat20_stat_market.py`, `tests/steps/test_dat20_api_end_to_end.py`
- [x] T006 [US2] Test fixture web khớp response trong `tests/api/test_ad17_web_fixtures.py` và kiểu TS trong `web/tests/fr37-newcomer-roles-fixture.test.ts`

## Phase 2: Implementation

- [x] T007 Thêm `MeasureKind.LEVEL_SHARE` vào `haido_core/domain/display_policy.py`, vào nhóm tỷ lệ của `haido_core/domain/envelope.py`
- [x] T008 Thêm `NewcomerRoleRow`, `NewcomerRolesData` vào `haido_api/schemas/market.py`
- [x] T009 Thêm `newcomer_roles` vào `MarketReadModel`, `FakeMarket`, `StatMarket` (chưa có số thật), `SOURCE_ENV` và route trong `haido_api/routes/market.py`
- [x] T010 Thêm ô và mục `newcomer_roles` vào `haido_api/fixtures/fake_market.json`
- [x] T011 Viết `web/lib/newcomer-roles.ts`, thêm `level_share` vào `MeasureKind` của `web/lib/city-shares.ts`, sinh `web/tests/fixtures/newcomer-roles.json`
- [x] T012 Sinh lại `docs/api/openapi.json`, cập nhật `docs/api/envelope-meta.md`

## Phase 3: Sau merge

- [ ] T013 Comment hợp đồng lên #144 cho người làm #145, #146, #147
