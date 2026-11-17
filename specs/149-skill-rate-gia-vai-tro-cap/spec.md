# Feature Specification: Endpoint tỷ lệ kỹ năng giả theo vai trò và cấp

**Feature Branch**: `gh-111-ho-so-ky-nang`

**Created**: 2026-11-16

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#149](https://github.com/Dyuedu/HaiDoIT/issues/149) — Extend the fake skill-rate endpoint to role and level. Phục vụ story #111 (US-A2). Bản thật là #151 (GiapPhanQuang).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Màn hồ sơ kỹ năng có số giả cho mọi vai trò (Priority: P1)

Màn hồ sơ kỹ năng (#152) gọi `GET /api/v1/skill-rates?role=&level=&have=` trước khi có tỷ lệ thật. Bản giả trả số cho mọi vai trò của `config/rules.toml` ở cấp `entry` (cấp mặc định, #134) và `all`, gọi tên ô rộng hơn khi ô đã chọn dưới 30 tin, và tự đếm kỹ năng core người dùng đã có.

**Why this priority**: AC 1, 2 của #149. Không có nó thì #152 không có gì để hiện cho hầu hết vai trò mà danh sách người mới (#147) dẫn tới.

**Independent Test**: `tests/api/test_fr19_skill_rates_vai_tro_cap.py`.

**Acceptance Scenarios**:

1. **Given** mỗi vai trò của `config/rules.toml`, **When** gọi `skill-rates` với `level=entry` và `level=all`, **Then** trả 200 và `data.role`, `data.level` là giá trị đã gửi. (AC 1)
2. **Given** `level=khong_co`, **When** gọi, **Then** trả 422 `invalid_query`; cấp hợp lệ mà fixture không có ô thì vẫn 404 `unknown_cell`. (AC 1)
3. **Given** ô đã chọn dưới 30 tin mà ô rộng hơn đủ 30 (Backend · Intern, UI/UX · Entry, DevOps · Entry), **When** gọi, **Then** `data.cell_id` là ô rộng hơn, `meta.cells[cell_id].fallback_label` gọi tên ô đó, và `meta.cells[cell_id].n` ≥ 30. (AC 2)
4. **Given** không ô nào đủ 30 (Data Engineer · Entry), **When** gọi, **Then** `fallback_label` nói cả hai chưa đủ, mọi `rate` là `null_data`, `group` là `null`.
5. **Given** ô đủ mẫu, **When** gọi, **Then** dòng có tỷ lệ đứng trước, tỷ lệ giảm dần, hòa thì theo mã; nhóm khớp θ của `meta.thresholds` (core ≥ θ_core, common ≥ θ_common, còn lại company_specific).
6. **Given** `have=java,sql,git,khong_co_trong_o`, **When** gọi Backend · Entry, **Then** dòng `java`, `sql`, `git` có `have = true`, dòng khác `false`; `data.core_size` là số dòng core, `data.have_core` là số dòng core có `have`.
7. **Given** ô `null_data`, **When** gọi, **Then** `core_size` và `have_core` là `null`.
8. **Given** `have` sai định dạng hoặc quá 200 mã, **When** gọi, **Then** 422, như `learning-path`.

### Edge Cases

- `role` không có trong `config/rules.toml` (`java_backend` cũ của fixture) giữ nguyên hành vi: có ô thì trả, không có thì 404.
- `learning-path` đọc chung `skill_rates` của fixture; thứ tự và nhóm của lộ trình không đổi.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `level` của `skill-rates` là một trong `all` + `level_options` (như `city-shares`, `learning-path`).
- **FR-002**: `have` theo đúng luật của `learning-path` (AD-22): mã snake_case, tối đa 200, loại trùng.
- **FR-003**: `SkillRateRow.have: bool`; `SkillRatesData.core_size`, `have_core: int | null`. Web không đếm (AD-22).
- **FR-004**: Máy chủ quyết thứ tự dòng; web không sắp xếp lại.
- **FR-005**: Fixture có `skill_rates[role].entry` và `.all` cho mọi vai trò của `config/rules.toml`.

## Success Criteria *(mandatory)*

- **SC-001**: `uv run pytest tests/api -q` xanh; `docs/api/openapi.json` sinh lại.

## Assumptions

- Bản thật (#151) theo cùng hình. `StatMarket.skill_rates` hiện vẫn ném `UnknownCell`; chỉ đổi chữ ký để nhận `have`. *(2026-11-17, #151: `StatMarket.skill_rates` đã đọc `stat_skill_rates`; bản thật chỉ trả dòng `core` và `common`, xem `specs/151-ty-le-ky-nang-that/spec.md`. Bản giả và các scenario ở trên không đổi.)*
- Câu `fallback_label` của bản giả viết tay; phép 2 (#106) sinh câu thật cho bản `stat` (2026-11-17).
