# Tasks: Khóa hồ sơ trình duyệt và danh sách kỹ năng mồi

**Input**: Design documents from `specs/205-khoa-ho-so-trinh-duyet/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi viết code.

## Phase 1: User Story 2 - Danh sách mồi (Priority: P1)

- [x] T001 [US2] Test định dạng mã, tên song ngữ, nguồn, thứ tự và bí danh không trùng trong `tests/core/test_fr13_skill_seed.py`
- [x] T002 [US2] Test "học máy" ra `machine_learning`, "C#" ra `csharp`, "ReactJS" ra `react`; không có tên vai trò
- [x] T003 [US2] Test `GET /api/v1/skills` trả `{data: {vocab_version, skills}}`, không chứa số, trong `tests/api/test_fr13_skills_route.py`
- [x] T004 [US2] Cho test AD-17 nhận route không có số qua `NUMBERLESS_ROUTES` trong `tests/api/test_ad17_routes.py`

## Phase 2: User Story 1 - Khóa đóng (Priority: P1)

- [x] T005 [US1] Test danh sách khóa, định dạng mã, đọc/ghi hồ sơ, chuẩn hóa, xóa theo tiền tố, bộ nhớ bị chặn trong `web/tests/ad23-haido-keys.test.ts`

## Phase 3: Implementation

- [x] T006 Soạn `haido_core/vocab/skills_seed.json` từ tag của bộ tin nền
- [x] T007 Viết `haido_core/vocab/skills.py`
- [x] T008 Viết `haido_api/schemas/skills.py`, `haido_api/routes/skills.py`, gắn router trong `haido_api/main.py`, sinh lại `docs/api/openapi.json`
- [x] T009 Viết `web/lib/haido-keys.ts`

## Phase 4: Sau merge

- [ ] T010 Kiểm `https://haidoit.io.vn/api/v1/skills` sau lần deploy
- [ ] T011 Comment hợp đồng (bảng khóa, định dạng mã) lên #205 cho người làm #206–#211, #111, #121–#124

## Phase 4: Cập nhật theo #163 (2026-11-11)

- [x] T015 Sinh lại `docs/api/openapi.json` (`HAIDO_UPDATE_OPENAPI=1`) sau khi `city-shares` thêm `level`; `/api/v1/skills` giữ nguyên trong ảnh chụp
- [x] T016 Sửa `tests/api/test_ad17_routes.py`: stub nguồn nhận `level`, `_all_fixture_requests` duyệt thêm cấp bậc

## Thay đổi sau merge (2026-11-12, #212)

#212 (hình response lộ trình học) sửa các file dùng chung với issue này, qua hai đợt (đợt 2 là sửa theo review). Hành vi của issue này không đổi.

- `haido_api/market_source.py`, `fake_market.py`, `stat_market.py`, `routes/market.py`: thêm phép `learning_path` và biến chọn nguồn `HAIDO_MARKET_SOURCE_LEARNING_PATH`; `create_app` đòi nguồn cho phép này (do `SOURCE_ENV` ở `routes/market.py`). `main.py` không đổi.
- `haido_api/fixtures/fake_market.json`: mã trong `skill_rates` đổi sang snake_case, thêm và đổi hàng `skill_rates` (đợt 2: `data_engineer/entry` về `vn.data_engineer`, thêm `backend/intern`). Không đụng `cells` hay `newcomer_roles`.
- `docs/api/openapi.json`, `docs/api/envelope-meta.md`: thêm route `learning-path` và ngoại lệ `Ordinal`.
- `tests/api/test_ad17_routes.py`, `test_ad17_web_fixtures.py`, `test_dat20_stat_market.py`, `test_fr33_city_shares_level.py`, `tests/steps/test_dat20_api_end_to_end.py`: thêm nguồn `learning_path` vào các lời gọi `create_app`, thêm route vào `SAMPLE_QUERY` và danh sách yêu cầu của test `display`.
