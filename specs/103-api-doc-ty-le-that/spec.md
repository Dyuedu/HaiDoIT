# Feature Specification: API đọc tỷ lệ kỹ năng thật

**Feature Branch**: `gh-151-ty-le-ky-nang-that`

**Created**: 2026-11-17

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#103](https://github.com/Dyuedu/HaiDoIT/issues/103) — The API reads real skill rates. Phục vụ #111, #119, #121. Phần đọc `stat_skill_rates` nằm ở `specs/151-ty-le-ky-nang-that/`; issue này khóa hai ràng buộc của lớp đọc.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mọi response có số đều có meta, API không tổng hợp bảng tin (Priority: P1)

Người dùng không bao giờ thấy một con số không kèm ngày snapshot, nguồn, cỡ mẫu và nhãn quay về; và con số đó đến từ bảng `stat_*` do bước `aggregate` ghi, không từ một câu `GROUP BY` chạy trong request.

**Why this priority**: AC 1, 2 của #103 (FR-19, AD-7, AD-17).

**Independent Test**: `tests/api/test_ad17_meta_nguon_stat.py`, `tests/api/test_fr19_skill_rates_stat.py` (test AD-7), cổng AD-7.

**Acceptance Scenarios**:

1. **Given** nguồn `stat` cho mọi phép và một snapshot có số, **When** gọi `city-shares`, `skill-rates`, `newcomer-roles`, `skill-roles`, **Then** body là `{data, meta}` với `meta.snapshot_date` và `meta.cells` không rỗng. (AC 1)
2. **Given** nguồn `stat` cho `learning-path` (chưa có số thật; `skill-roles` có số thật từ #168 và nằm ở kịch bản 1), **When** gọi, **Then** trả lỗi chuẩn `{error}`, không có `data` và không có số. (AC 1)
3. **Given** một lần gọi `skill-rates` qua `StatMarket`, **When** ghi lại mọi câu SQL, **Then** chỉ đọc `stat_skill_rates` và `stat_cells`, không nhắc `job_*`, và không có `group by`, `avg(`, `count(`, `sum(`, `percentile`. (AC 2)
4. **Given** mã nguồn `haido_api/`, **When** chạy cổng AD-7, **Then** PASS. (AC 2)

### Edge Cases

- Mọi route có số với nguồn giả đã được `tests/api/test_ad17_routes.py::test_ad17_moi_route_tra_envelope` kiểm; test mới thêm nguồn `stat`.
- `SELECT DISTINCT seniority, n_scanned` trên `stat_skill_rates` để lấy `n_scanned` đã ghi là tra theo khóa trên bảng `stat_*`, không tổng hợp (AD-7 cấm `job_*`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Mọi route trả số dưới `/api/v1` trả `Envelope` (`data` + `meta`) ở cả hai nguồn `fake` và `stat`.
- **FR-002**: Mã `haido_api/` chỉ đọc bảng `stat_*` và `snapshots`; không đọc, không tổng hợp `job_*` (AD-7).

## Success Criteria *(mandatory)*

- **SC-001**: `uv run pytest tests/api/test_ad17_meta_nguon_stat.py tests/api/test_fr19_skill_rates_stat.py -q` xanh; `check_gates.py --require AD-7` PASS.

## Assumptions

- Hai AC của #103 không đòi code mới ngoài `StatMarket.skill_rates` của #151; issue này thêm test khóa chúng. Kiểm tra bằng test chứ không bằng đọc mã.
