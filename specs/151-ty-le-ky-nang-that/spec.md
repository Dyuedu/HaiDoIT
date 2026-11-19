# Feature Specification: Tỷ lệ kỹ năng thật theo vai trò và cấp

**Feature Branch**: `gh-151-ty-le-ky-nang-that`

**Created**: 2026-11-17

**Status**: Implemented, chờ merge. #102 (2026-11-19) đổi nguồn θ của FR-003: từ `config/rules.toml` sang `snapshots.theta_version` và `config/theta.toml`.

**Input**: GitHub issue [#151](https://github.com/Dyuedu/HaiDoIT/issues/151) — Return real skill rates for a role and level. Phục vụ story #111 (US-A2). Đọc #101 (bảng), #103 (ràng buộc lớp đọc), #106 (phép 2).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hồ sơ kỹ năng có số thật cho một vai trò và cấp (Priority: P1)

`GET /api/v1/skill-rates?role=&level=&have=` với `HAIDO_MARKET_SOURCE_SKILL_RATES=stat` trả tỷ lệ từ `stat_skill_rates` của snapshot đã công bố mới nhất, mỗi kỹ năng kèm nhóm `core` hoặc `common`, quay về tập rộng hơn khi ô thiếu mẫu và nói rõ đã dùng tập nào.

**Why this priority**: AC 1 đến 4 của #151; nền cho story #111.

**Independent Test**: `tests/api/test_fr19_skill_rates_stat.py`, `tests/deploy/test_gh151_ty_le_ky_nang_doc_snapshot_that.py`.

**Acceptance Scenarios**:

1. **Given** ô `(vai trò, cấp)` có `n_scanned >= 30`, **When** gọi, **Then** `data.cell_id` là ô đó, mỗi dòng có `rate` (kind `skill_rate`, `display = shown`) và `group` là `core` (rate ≥ θ_core) hoặc `common` (rate ≥ θ_common); kỹ năng `rare` không có dòng; dòng theo tỷ lệ giảm dần rồi mã. (AC 1)
2. **Given** ô thiếu mẫu, **When** gọi, **Then** `data.cell_id` là ô rộng hơn theo phép 2 (`cấp thô → nhóm → all`), `meta.cells[data.cell_id].fallback_label` gọi tên ô được yêu cầu và n, ô đã dùng và n, với n là số tin đọc được kỹ năng (`n_scanned`, không phải `n` của ô; ví dụ "Backend · Fresher chỉ có 26 tin đọc được kỹ năng (dưới 30), …"); ở bước `all` với cấp mới vào nghề thêm tỷ lệ tin Mid trở lên. Khi chính ô được chọn đủ mẫu, `fallback_label` là `null`. (AC 2)
3. **Given** không tập nào đạt 30, **When** gọi, **Then** `data.cell_id` là ô `all`, mọi `rate` là `null_data` (`value = null`), `group = null`, `core_size` và `have_core` là `null`, nhãn nói chưa tập nào đủ 30 và n từng tập. (AC 3)
4. **Given** `HAIDO_MARKET_SOURCE_SKILL_RATES`, **When** đọc `deploy/compose.prod.yml` và `compose.local.yml`, **Then** prod là `stat`, local giữ `fake`. (AC 4)
5. **Given** `have=java,sql`, **When** gọi ô đủ mẫu, **Then** dòng của mã đó có `have = true`; `core_size` là số dòng core, `have_core` là số dòng core có `have`.
6. **Given** `n` của `stat_cells` đủ nhưng `n_scanned < 30`, **When** gọi, **Then** ô đó không được chọn: cỡ mẫu quyết định ô là `n_scanned` (AD-17). `meta.cells[...].n` là `n` của `stat_cells`, `n_by_measure.skill_count` là `n_scanned`.
7. **Given** vai trò ngoài `config/rules.toml` hoặc không có tin nào ở snapshot, **When** gọi, **Then** 404 `unknown_cell` (kèm ngày snapshot nếu có); chưa có snapshot đọc được thì 404 không ngày; `level` lạ vẫn 422.
9. **Given** ô được chọn có trong `stat_cells` nhưng không có hàng `stat_skill_rates` nào cho vai trò đó, **When** gọi, **Then** 404 `unknown_cell` kèm ngày snapshot và câu tiếng Việt nói chưa có tỷ lệ kỹ năng; không trả "có 0 tin" với dòng rỗng. (đợt 2)
10. **Given** ô đủ mẫu mà mọi kỹ năng dưới θ_common, **When** gọi, **Then** 200 với `rows = []`, `core_size = 0`, `have_core = 0` (hợp lệ, không phải lỗi); web hiện một câu giải thích không chứa số và không báo "không đọc được". Ô chưa đủ dữ liệu vẫn không có `rows` rỗng (xem Assumptions). (đợt 2)
11. **Given** các hàng `stat_skill_rates` của một ô có `n_scanned` khác nhau, **When** gọi, **Then** `RuntimeError` nêu ô và các giá trị (vi phạm bảo đảm của #101), không chọn ngầm một giá trị; vẫn chỉ đọc `stat_*`, không GROUP BY, COUNT, AVG, MAX, MIN, HAVING trên bảng nào và không đọc `job_*` (AD-7). (đợt 2)

### Edge Cases

- Snapshot đọc được: `published` hoặc `partial` mới nhất có `stat_sources` và có hàng `stat_skill_rates`; snapshot `open` hoặc thiếu nguồn bị bỏ, lùi về snapshot cũ đầy đủ.
- Ô cuối không có kỹ năng nào được nhắc: liệt kê mọi mã của ô theo mã, tất cả `null_data` (web coi `rows` rỗng là response hỏng).
- Ô đủ mẫu mà mọi kỹ năng là `rare`: `rows` rỗng, `core_size = 0`. Web hiện coi là response không đọc được; chưa gặp ở dữ liệu thật vì θ_common = 0.1, ghi nhận để xử lý nếu xảy ra.
- Nhánh: `stat_cells.branch` luôn `all`; phép 2 hỗ trợ nhánh nhưng route chưa nhận tham số nhánh.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `StatMarket.skill_rates` đọc `stat_skill_rates` và `stat_cells` (phạm vi `vn`, nhánh `all`, số năm `any`) của snapshot đọc được mới nhất; chỉ bảng `stat_*` (AD-7).
- **FR-002**: Ô chọn bằng phép 2 (`CellSelector`) với `CellStats.sample_n = n_scanned`; ngưỡng là `rules.min_sample`.
- **FR-003**: Nhóm bằng phép 4 (`SkillGrouper`) với θ của phiên bản ghi trong snapshot đã chọn (`snapshots.theta_version`, giá trị trong `config/theta.toml`; NULL đọc là `theta-1`), không phải θ hiện hành của `config/rules.toml`. Lúc viết spec này (trước #102) θ lấy từ `config/rules.toml`; phần còn lại không đổi.
- **FR-004**: Mọi `display` do `suppression_for` qua `Envelope` quyết, không có so sánh `n < 30` rời rạc trong `stat_market.py`.
- **FR-005**: Production đặt `HAIDO_MARKET_SOURCE_SKILL_RATES: stat`; bản giả không còn được phục vụ ở prod.

## Success Criteria *(mandatory)*

- **SC-001**: `uv run pytest -q` xanh (Postgres thật); cổng AD-2, AD-7, AD-17 xanh.

## Assumptions

- **Dòng khi không tập nào đủ.** Lấy kỹ năng có `n_with > 0` của ô `all`, xếp theo mã (thứ tự không mang xếp hạng); nếu không có kỹ năng nào thì mọi mã của ô. Chọn vậy để web (`rows` không rỗng) hiện "chưa đủ dữ liệu" từng dòng và vẫn có tên kỹ năng để người dùng tick.
- **Dòng chỉ core và common.** Khác bản giả (có `company_specific`): AC 1 của #151 chỉ nói `core` hoặc `common`; kỹ năng `rare` bị bỏ.
- **Vai trò không có tin** (`n = 0` ở ô cuối): 404 `unknown_cell` như `city-shares`, không phải 200 rỗng.
- **Snapshot không chọn theo vai trò.** Snapshot đọc là snapshot đọc được mới nhất có hàng tỷ lệ kỹ năng nào đó, như các route khác; không chọn riêng cho từng vai trò. Vai trò không có hàng ở snapshot đó là 404 (kịch bản 9).
- **`role=all` không hỗ trợ** (404 `unknown_cell`), như bản giả.
- **Nhóm kỹ năng không thể lỗi `ValueError`**: CHECK của DB giữ `rate` trong [0, 1] và khóa chính giữ mỗi kỹ năng một hàng, nên `group_skills` không gặp đầu vào sai.
- **Tỷ lệ Mid trở lên**: làm tròn nửa lên (không dùng `round` của Python, làm tròn nửa về chẵn); mẫu số là mọi tin trong `seniority_mix` của ô, kể cả `unknown`.
- **`rows` rỗng.** Ô đủ mẫu mà mọi kỹ năng hiếm cho `rows = []` với `core_size = 0` (kịch bản 10). Ô chưa đủ dữ liệu có `core_size = null` và luôn có dòng (bỏ qua việc này thì web coi response hỏng), nên đoạn "kỹ năng có nhắc, rồi mọi mã của ô" vẫn cần và có test (`test_fr19_ac3_o_cuoi_khong_co_ky_nang_nao_duoc_nhac_...`).
- Bản giả không đổi; `fake_market.py` vẫn ánh xạ thẳng fixture. Web không đổi: response thật khớp `isSkillRatesEnvelope` (kiểm ở `tdd.md`).
