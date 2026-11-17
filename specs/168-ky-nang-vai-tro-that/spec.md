# Feature Specification: Tỷ lệ kỹ năng theo vai trò, số thật

**Feature Branch**: `gh-168-ky-nang-vai-tro-that`

**Created**: 2026-11-17

**Status**: Implemented, đã sửa theo review 2026-11-17, chờ merge.

**Input**: GitHub issue [#168](https://github.com/Dyuedu/HaiDoIT/issues/168) — For one skill, the API returns each role's share of entry-level postings that mention it (rates from #101). Phục vụ story #113. Hình response, bản giả và kiểm `Envelope` do #166 định; bảng `stat_skill_rates` do #101 ghi.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Xếp hạng vai trò theo tỷ lệ tin entry-level nhắc kỹ năng (Priority: P1)

`GET /api/v1/skill-roles?skill=<mã>` với `HAIDO_MARKET_SOURCE_SKILL_ROLES=stat` trả mỗi vai trò của `config/rules.toml` một dòng, tỷ lệ lấy từ `stat_skill_rates` của snapshot đọc được mới nhất, xếp từ cao xuống thấp.

**Why this priority**: AC 1 của #168; nền cho story #113.

**Independent Test**: `tests/api/test_fr09_skill_roles_stat.py` (Postgres thật), `tests/api/test_ad17_meta_nguon_stat.py`.

**Acceptance Scenarios**:

1. **Given** vai trò đủ mẫu có tỷ lệ 0.9, 0.5, 0.5 và 0, **When** gọi, **Then** các dòng `shown` đứng trước, theo tỷ lệ giảm dần rồi mã vai trò; dòng `null_data` đứng sau. (AC 1)
2. **Given** vai trò đủ mẫu mà không tin entry-level nào nhắc kỹ năng, **Then** `share.value = 0`, `display = shown`. (AC 1)
3. **Given** snapshot `published` hoặc `partial` mới nhất có nguồn và có hàng tỷ lệ; snapshot `open`, thiếu nguồn hoặc cũ hơn bị bỏ, **When** gọi, **Then** dùng snapshot đó và ghi trạng thái. (AC 1)
4. **Given** hàng `role = all`, `seniority = all` của kỹ năng có `n_with > 0` (kể cả khi chỉ cấp khác entry nhắc), **Then** `data.mentioned = true`; `n_with = 0` thì `false`. (AC 1, AC 4 của #113)
5. **Given** mỗi dòng, **Then** `share.cell_id = vn.<role>.entry`, `kind = skill_rate`, và `meta.cells[cell_id]` có `n` của `stat_cells`, `seniority_mix`, `n_by_measure.skill_count = n_scanned`. (AC 1)

---

### User Story 2 - Vai trò dưới 30 tin nói "chưa đủ dữ liệu (X/30)" (Priority: P1)

**Why this priority**: AC 2 của #168.

**Independent Test**: `tests/api/test_fr09_skill_roles_stat.py`.

**Acceptance Scenarios**:

1. **Given** vai trò có `n_scanned` dưới 30, **Then** `share.display = null_data`, `value = null`, và X là `meta.cells[cell_id].n_by_measure.skill_count` (ô có `insufficient_by_measure.skill_count = true`). (AC 2)
2. **Given** vai trò có `n` của ô từ 30 trở lên nhưng `n_scanned` dưới 30, **Then** vẫn `null_data` với X là `n_scanned`, không phải `n`. (AC 2)
3. **Given** vai trò không có ô entry ở snapshot, **Then** vẫn có một dòng `null_data`, `n = 0`, `skill_count = 0`. (AC 2)
4. **Given** nhiều dòng `null_data`, **Then** theo X giảm dần rồi mã vai trò. (AC 1, AC 2; `Envelope` kiểm qua `SkillRolesData.check_against_meta`)

---

### User Story 3 - Lỗi và dữ liệu hỏng không thành số giả (Priority: P2)

**Independent Test**: `tests/api/test_fr09_skill_roles_stat.py`, `tests/deploy/test_gh166_*`, `tests/deploy/test_gh309_*`.

**Acceptance Scenarios**:

1. **Given** chưa có snapshot đọc được, **Then** 404 `unknown_cell` không có ngày snapshot.
2. **Given** kỹ năng trong bộ từ vựng nhưng snapshot không có hàng nào của nó, **Then** 404 `unknown_cell` kèm ngày snapshot. Mã ngoài bộ từ vựng vẫn 404 `unknown_skill`, sai định dạng 422. `StatMarket.skill_roles` tự kiểm bộ từ vựng và ném `UnknownSkill` trước khi mở kết nối (không chỉ dựa vào route).
3. **Given** `n_scanned` lớn hơn `n` của ô entry, **Then** lỗi 500 (`RuntimeError` nêu snapshot và vai trò), không trả số.
4. **Given** một vai trò có `n_with > 0` ở cấp entry mà hàng `role = all`, `seniority = all` của kỹ năng có `n_with = 0`, **Then** lỗi 500 (`RuntimeError` nêu kỹ năng và snapshot), không để validator trả 500 không ngữ cảnh.
5. **Given** mọi lần gọi, **Then** SQL chỉ đọc `stat_*` và `snapshots` theo khóa; không `job_*`, không `count(`, `sum(`, `avg(`, `group by` (AD-7).
6. **Given** `deploy/compose.prod.yml`, **Then** `HAIDO_MARKET_SOURCE_SKILL_ROLES = stat`; compose local giữ `fake`.

### Edge Cases

- `mentioned = true` mà mọi dòng hiện đều 0: hợp lệ (tin nhắc ở cấp khác hoặc ở ô bị ẩn).
- Hàng `role = all` ở cấp `entry` không phải dòng của vai trò nào: bị bỏ, và không bao giờ là nguồn của `mentioned`.
- `n_scanned` đúng bằng `min_sample` thì hiện giá trị (`shown`); thiếu 1 thì `null_data`.
- Snapshot mới hơn không có hàng `stat_sources` bị bỏ, dùng snapshot cũ hơn; `sources_failed` của snapshot `partial` chuyển nguyên vào `meta`.
- Kỹ năng không có hàng ở ô entry của một vai trò: `n_scanned` = 0 cho vai trò đó (`null_data`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `StatMarket.skill_roles` đọc một truy vấn `stat_skill_rates` theo `(snapshot_id, skill)`, phạm vi `vn`, nhánh `all`, số năm `any`, cấp `entry` và `all`, cộng `stat_cells` ô entry của mọi vai trò (`_national_cells`).
- **FR-002**: `display` do `suppression_for(SKILL_RATE, n_scanned)` quyết; `value` là `rate` đã ghi, không chia lại.
- **FR-003**: Thứ tự dòng như `FakeMarket.skill_roles`.
- **FR-004**: Production đặt `stat` (đã có từ #166).

## Success Criteria *(mandatory)*

- **SC-001**: `uv run pytest -q` xanh (Postgres thật); cổng AD-7 và AD-17 xanh.

## Assumptions

- X trong "X/30" là `n_scanned` của hàng entry (`skill_count`), theo quyết định của #166.
- Cỡ mẫu theo vai trò đọc từ hàng của chính kỹ năng đang xem; `aggregate` ghi cùng `n_scanned` ở mọi hàng của một ô (#101), nên đủ.
- Bản giả và web không đổi.
- Quyết định của #166 "stat luôn 404 đến #168" là trạng thái chuyển tiếp; nay thay bằng số thật (xem `specs/166-*` đợt 2026-11-17).
