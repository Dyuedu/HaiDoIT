# Feature Specification: Trả số tin entry-level, tỷ lệ và n của mỗi vai trò

**Feature Branch**: `gh-145-146-so-nguoi-moi`

**Created**: 2026-11-12

**Status**: Implemented, chờ merge. Cập nhật 2026-11-13 theo #148: thêm cạnh biên entry > n (xem Edge Cases). Không AC nào đổi; phạm vi của AC "Every role is present" được ghi rõ là khi dữ liệu nhất quán (quyết định 2026-11-13).

**Input**: GitHub issue [#146](https://github.com/Dyuedu/HaiDoIT/issues/146) — Return each role's entry-level count, share, and n. Phục vụ story #110 (US-A1). Dùng phép đọc của #145 (`specs/145-doc-so-tin-entry/`), hình response của #144 (`specs/144-hinh-nguoi-moi/`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - API trả số thật cho màn người mới (Priority: P1)

`GET /api/v1/newcomer-roles` với nguồn `stat` trả mỗi vai trò của config một dòng, số lấy từ snapshot đã công bố, cùng hình với bản giả của #144. Production đặt nguồn này là `stat`.

**Why this priority**: Hai AC của #146. Màn người mới (#147) dựng trên bản giả; khi bật `stat` thì số thật đến mà màn hình không đổi.

**Independent Test**: `tests/api/test_fr37_newcomer_roles_stat.py`, `tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py`.

**Acceptance Scenarios**:

1. **Given** snapshot chỉ có hàng của `backend` và `qa`, **When** gọi route, **Then** có đúng một dòng cho mỗi mã trong `roles` của `config/rules.toml`; vai trò vắng (ví dụ `game`) có entry = 0, n = 0, `share` là `null_data`. (AC 1)
2. **Given** `qa` có 35 tin, không tin nào entry-level, **When** gọi, **Then** entry = 0, n = 35, `share.value = 0`, `display = shown`.
3. **Given** `ui_ux` có 12 tin, 3 entry-level, **When** gọi, **Then** entry = 3, n = 12, `share.value = null`, `display = null_data`, `kind = level_share`, `cell_id = vn.ui_ux`.
4. **Given** `min_sample = 10` trong config, **When** gọi với `ui_ux` như trên, **Then** `share` là `shown` và `meta.thresholds.min_sample = 10`.
5. **Given** năm vai trò có số entry-level khác nhau, một vai trò dưới 30 tin, **When** gọi, **Then** dòng có tỷ lệ đứng trước theo entry giảm dần rồi theo mã; dòng `null_data` đứng sau theo cùng quy tắc.
6. **Given** snapshot `partial` với nguồn `zalo`, `itviec` và `topdev` lỗi, **When** gọi, **Then** `meta.snapshot_date` là ngày snapshot, `snapshot_status = partial`, `sources = [itviec, zalo]`, `sources_failed = [topdev]`. (AC 2)
7. **Given** chưa có snapshot đọc được, **When** gọi, **Then** 404 `unknown_cell`.
8. **Given** `deploy/compose.prod.yml`, **When** đọc biến môi trường của `api`, **Then** `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES = stat`; `compose.local.yml` giữ `fake`.

### Edge Cases

- Vai trò mới thêm vào config sau khi snapshot được công bố: có dòng 0 tin cho tới lượt chạy đêm sau.
- Tỷ lệ chia cho n = 0 không xảy ra: n = 0 luôn dưới ngưỡng nên `null_data`, không tính.
- Ô hỏng, entry > n (thêm 2026-11-13, #148): `StatMarket.newcomer_roles` ném `RuntimeError` nêu mã vai trò và cả hai số, không cắt tỷ lệ về 1; route trả 500 `internal_error` và log. **Quyết định ngày 2026-11-13 (người dùng chọn phương án A):** một ô hỏng làm cả danh sách trả 500, giống ca vai trò đủ mẫu vốn đã 500 trước đó vì `Stat` từ chối tỷ lệ lớn hơn 1. AC "Every role is present" áp dụng khi `stat_cells` nhất quán; dữ liệu hỏng là lỗi nội bộ cần lộ ra, không ẩn riêng dòng hỏng. Test: `test_fr37_ad17_o_hong_*` trong `tests/api/test_fr37_newcomer_roles_stat.py`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `StatMarket.newcomer_roles` trả `Envelope[NewcomerRolesData]` cùng hình bản giả (#144); `levels` là thành viên nhóm `entry` của `level_groups`.
- **FR-002**: Mỗi mã trong `roles` của config có một dòng; số lấy theo #145, vắng thì 0.
- **FR-003**: `share` = entry / n, `kind = level_share`, `display` do `suppression_for` quyết với `min_sample` của config.
- **FR-004**: Thứ tự dòng do máy chủ quyết như bản giả.
- **FR-005**: `meta` mang ngày, trạng thái snapshot, `stat_sources`, `sources_failed`, ngưỡng và lưu ý độ phủ, như `city-shares`.
- **FR-006**: Production chọn nguồn `stat` cho phép này.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py -q` xanh.
- **SC-002**: Sau deploy, `GET /api/v1/newcomer-roles` trên prod trả 200 với snapshot mới nhất và 17 dòng.

## Assumptions

- Hình response không đổi so với #144; `docs/api/openapi.json` không cần sinh lại.
