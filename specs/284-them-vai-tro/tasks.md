# Tasks: Thêm bảy vai trò vào danh sách vai trò

**Input**: `specs/284-them-vai-tro/` (spec.md, plan.md, data-model.md)

Test đứng trước code. Mỗi test mới phải đỏ trước khi có code (ghi trong tdd.md).

## Phase 1: Tests (RED)

- [x] T001 `tests/deploy/test_gh284_vai_tro_moi.py`: `roles` có 17 mã đúng thứ tự; mỗi nhãn của bộ phân loại có mã riêng; `report_as` rỗng; bản giả có `city_shares` và dòng `newcomer_roles` cho mỗi mã mới, `newcomer_roles` theo đúng thứ tự `roles`
- [x] T002 `tests/steps/test_gh284_aggregate_vai_tro_moi.py` (Postgres): tin của mỗi vai trò mới vào ô của mã đó, không vào `other`; chức danh chung vẫn vào `other`; API nguồn `stat` trả 200 cho `role=fullstack&level=entry&years=1`
- [x] T003 `web/tests/fr33-role-chips-new-roles.test.tsx`: nhóm "Vai trò" có 18 nút theo thứ tự, nhãn tiếng Việt, `flex-wrap`, Tab đi qua đủ; bấm "Fullstack" gửi `role=fullstack`
- [x] T004 Test có sẵn đỏ theo: `tests/deploy/test_gh162_ban_do_doc_snapshot_that.py` (chip web khác config)

## Phase 2: Implementation (GREEN)

- [x] T010 `config/rules.toml`: `roles`, `[labels.role]`, `config_version`
- [x] T011 `config/classify.toml`: `[report_as]` rỗng
- [x] T012 `web/lib/labels.ts`: `ROLE_OPTIONS`
- [x] T013 `haido_api/fixtures/fake_market.json`; sinh lại `web/tests/fixtures/newcomer-roles.json`
- [x] T014 Sửa test cũ có kỳ vọng `report_as` hoặc số vai trò; ghi trong tdd.md
- [x] T015 Chạy toàn bộ: pytest, determinism, ruff, cổng, vitest, lint, tsc, build; chạy lại snapshot 12/11 trên bản sao, đo `other`; xem trang ở 360px
- [x] T016 Cập nhật spec của #144, #163, #280, #283

## Phase 3: Sau merge

- [ ] T020 Lượt đêm đầu tiên sau deploy: `city-shares?role=fullstack` trả 200 với snapshot mới
