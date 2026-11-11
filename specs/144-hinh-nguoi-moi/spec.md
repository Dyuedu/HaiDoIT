# Feature Specification: Hình response của màn người mới và dữ liệu giả

**Feature Branch**: `gh-144-hinh-nguoi-moi`

**Created**: 2026-11-11

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#144](https://github.com/Dyuedu/HaiDoIT/issues/144) — Agree the newcomer-view response shape and add fake data. Phục vụ story #110 (US-A1: thấy vai trò nào còn nhận người mới).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Một hình response cho cả màn hình và bước đếm (Priority: P1)

Người làm màn người mới (#147) và người làm bước đọc/trả số thật (#145, #146) dựng trên cùng một hình: `GET /api/v1/newcomer-roles` trả mỗi vai trò một dòng, có số tin entry-level, tỷ lệ trong số tin của vai trò, và n.

**Why this priority**: AC thứ nhất của #144. Nếu hai bên tự đoán hình thì màn hình chạy trên dữ liệu giả nhưng vỡ khi nối số thật.

**Independent Test**: `tests/api/test_fr37_newcomer_roles.py` kiểm schema và route; `tests/api/test_ad17_routes.py` kiểm route mới trả Envelope.

**Acceptance Scenarios**:

1. **Given** API chạy với nguồn giả, **When** gọi `GET /api/v1/newcomer-roles`, **Then** body là `Envelope[NewcomerRolesData]`; mỗi dòng có `role`, `total_cell_id`, `entry_cell_id`, `share`.
2. **Given** một dòng, **When** tra `meta.cells[entry_cell_id].n` và `meta.cells[total_cell_id].n`, **Then** ra số tin entry-level và n của vai trò; `share.cell_id` là `total_cell_id`.
3. **Given** `share` có `kind` khác `level_share`, `share.cell_id` khác `total_cell_id`, hai ô trùng nhau, hoặc vai trò lặp, **When** dựng `NewcomerRolesData`, **Then** lỗi.
4. **Given** vai trò có n < 30, **When** API trả, **Then** `share.display = null_data`, `share.value = null`; số tin entry-level và n vẫn có ở `meta.cells`.
5. **Given** `level_share` dưới ngưỡng, **When** gọi `suppression_for`, **Then** ra `null_data` (không hiện mờ như tỷ trọng thành phố).

---

### User Story 2 - Dữ liệu giả có sẵn cho màn hình (Priority: P1)

Màn người mới đọc được dữ liệu giả đúng hình ngay hôm nay, qua proxy `/api` khi API chạy nguồn `fake`, và qua fixture khi chạy test web.

**Why this priority**: AC thứ hai của #144. #147 phải dựng được từ ngày đầu, trước khi #145, #146 có số thật.

**Independent Test**: `tests/api/test_fr37_newcomer_roles.py` kiểm nội dung dữ liệu giả; `tests/api/test_ad17_web_fixtures.py` so fixture web với response; `web/tests/fr37-newcomer-roles-fixture.test.ts` kiểm fixture khớp kiểu TypeScript.

**Acceptance Scenarios**:

1. **Given** dữ liệu giả, **When** so tập vai trò với `roles` của `config/rules.toml`, **Then** đúng bằng nhau.
2. **Given** mỗi dòng, **When** cộng `intern`, `fresher`, `junior` trong `seniority_mix` của ô vai trò, **Then** bằng n của ô entry-level, và không vượt n của vai trò; dòng có số thì `share.value` bằng số entry-level chia n.
3. **Given** dữ liệu giả, **When** liệt kê trường hợp, **Then** có vai trò đủ mẫu, vai trò dưới 30 tin, vai trò đủ mẫu có 0 tin entry-level, và vai trò không có tin nào.
4. **Given** response, **When** đọc thứ tự dòng, **Then** dòng có tỷ lệ đứng trước, xếp theo số entry-level giảm dần rồi theo mã; dòng `null_data` đứng sau theo cùng quy tắc.
5. **Given** `web/tests/fixtures/newcomer-roles.json`, **When** so với response của API giả, **Then** giống hệt.

---

### Edge Cases

- Vai trò không có tin nào (n = 0): vẫn có dòng, `share` là `null_data`, ô entry-level có n = 0 và `seniority_mix` rỗng.
- Vai trò đủ mẫu nhưng 0 tin entry-level: `share.value = 0`, `display = shown`; màn hình hiện 0 và giữ vai trò trong danh sách.
- Nguồn `stat` chưa cài phép này: `StatMarket.newcomer_roles` trả 404 `unknown_cell` cho tới #145, #146. Prod để phép này ở `fake` (mặc định).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `GET /api/v1/newcomer-roles` không nhận tham số và trả `Envelope[NewcomerRolesData]`.
- **FR-002**: `NewcomerRolesData` có `levels` (các cấp bậc tính là entry-level: `intern`, `fresher`, `junior`) và `rows`, mỗi vai trò một dòng.
- **FR-003**: Số tin entry-level là `meta.cells[entry_cell_id].n`; n của vai trò là `meta.cells[total_cell_id].n`. Không có số nào đứng ngoài `Stat` hay `meta` (AD-17).
- **FR-004**: `share` là `Stat` có `kind = level_share` và `cell_id = total_cell_id`. `suppression_for` cho `level_share` dưới ngưỡng ra `null_data`.
- **FR-005**: Thứ tự dòng do máy chủ quyết như Scenario 2.4; web không tự sắp xếp hay tính toán (AD-22).
- **FR-006**: Phép có biến chọn nguồn riêng `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES`, mặc định `fake`.

### Key Entities

- **Dòng vai trò người mới**: `role`, `total_cell_id`, `entry_cell_id`, `share`.
- **Ô entry-level**: `vn.<role>.entry`, n bằng tổng Intern/Fresher/Junior trong `seniority_mix` của ô `vn.<role>`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run pytest tests/api tests/domain -q` xanh.
- **SC-002**: `cd web && npm test` xanh, có `tests/fr37-newcomer-roles-fixture.test.ts`.
- **SC-003**: `docs/api/openapi.json` và `docs/api/envelope-meta.md` mô tả route mới.

## Assumptions

- Entry-level là Intern, Fresher, Junior, theo FR-37 ("tỷ lệ tin Intern/Fresher/Junior trong từng vai trò") và theo ô `vn.backend.entry` đã có trong bản giả.
- Tên route `newcomer-roles` theo tên màn hình của #110. Mã vai trò lấy từ `config/rules.toml`.
