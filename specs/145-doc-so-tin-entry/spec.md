# Feature Specification: Đọc số tin entry-level của mỗi vai trò từ cơ cấu cấp bậc toàn quốc

**Feature Branch**: `gh-145-146-so-nguoi-moi`

**Created**: 2026-11-12

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#145](https://github.com/Dyuedu/HaiDoIT/issues/145) — Read entry-level counts per role from the national level mix. Phục vụ story #110 (US-A1). Làm cùng nhánh với #146 (`specs/146-tra-so-nguoi-moi/`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Số tin entry-level lấy từ ô đã công bố (Priority: P1)

Bước trả số của màn người mới (#146) cần số tin entry-level và n của mỗi vai trò. Hai số này đã có sẵn trong `stat_cells` do `aggregate` ghi (#163): ô toàn quốc ở nhóm cấp `entry` có `n` = Intern + Fresher + Junior và `seniority_mix` của ba cấp đó; ô toàn quốc ở `all` có n của vai trò. Phép đọc chỉ lấy hai ô đó.

**Why this priority**: Cả hai AC của #145. Nếu API tự cộng lại từ bảng tin thì vi phạm AD-7, và số có thể lệch với số đã công bố trên bản đồ.

**Independent Test**: `tests/api/test_fr37_newcomer_roles_stat.py` (ba test đầu).

**Acceptance Scenarios**:

1. **Given** snapshot đã công bố, ô `vn` của `backend` ở `entry` có n = 20 với mix `{intern: 4, fresher: 6, junior: 10}` và ô `vn` ở `all` có n = 50, **When** gọi `GET /api/v1/newcomer-roles` với nguồn `stat`, **Then** `meta.cells["vn.backend.entry"].n = 20`, mix giữ nguyên, `meta.cells["vn.backend"].n = 50`, tỷ lệ 0,4.
2. **Given** cùng snapshot, có thêm ô thành phố cấp `entry` với n khác, **When** đọc, **Then** chỉ ô `vn` được dùng.
3. **Given** một yêu cầu, **When** ghi lại mọi câu SQL engine chạy, **Then** không câu nào nhắc tới `job_*`, bảng `public.*` của scraper, hay `sum(`/`count(`.
4. **Given** snapshot cũ đã công bố và snapshot mới hơn còn `open`, **When** đọc, **Then** số lấy từ snapshot đã công bố.

### Edge Cases

- Vai trò không có hàng ở snapshot (chưa có tin nào trong cửa sổ): đọc ra 0 tin, n = 0 (xử lý ở #146).
- Hàng `role = all` không được đọc vào danh sách vai trò.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Số tin entry-level của vai trò R là `stat_cells.n` của hàng (`snapshot`, `role = R`, `branch = all`, `seniority = entry`, `years = any`, `scope = vn`).
- **FR-002**: n của vai trò là `stat_cells.n` của hàng cùng khóa với `seniority = all`.
- **FR-003**: Phép đọc không cộng, không đếm, không đọc bảng tin hay bảng scraper (AD-7; cổng AD-7 và test ghi SQL).
- **FR-004**: Snapshot đọc là `published` hoặc `partial` mới nhất có hàng cấp `entry` và có `stat_sources`, cùng quy tắc với bản đồ (`_latest_readable`).
- **FR-005**: Tên nhóm `entry` và các cấp thành viên lấy từ `level_groups` của `config/rules.toml`.

### Key Entities

- **Ô toàn quốc theo cấp**: hàng `stat_cells` với `scope = vn`; `n` và `seniority_mix` do `aggregate` ghi.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` xanh (Postgres).
- **SC-002**: Cổng AD-7 PASS.
- **SC-003**: Trên bản sao local của prod (snapshot 12/11), số đọc ra khớp số `city-shares?level=entry` của cùng vai trò (ví dụ `it_infra` 132, `backend` 56).

## Assumptions

- Ô `entry` luôn có cho mọi vai trò × snapshot từ migration 0005 (#163); `aggregate` ghi hàng `vn` cho mọi vai trò và mọi cấp lọc kể cả khi n = 0.
