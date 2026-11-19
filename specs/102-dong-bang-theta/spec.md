# Feature Specification: Hiệu chỉnh và đóng băng θ_core, θ_common

**Feature Branch**: `gh-102-dong-bang-theta`

**Created**: 2026-11-19

**Status**: Code xong, RED/GREEN và đột biến đã ghi trong `tdd.md`, gồm đợt sửa theo review (2026-11-19). Chờ review lại và merge.

**Input**: GitHub issue [#102](https://github.com/Dyuedu/HaiDoIT/issues/102) — [DAT.30] Calibrate and freeze θ_core and θ_common. Task phục vụ #121; #101 đọc các giá trị.

## Bối cảnh

Trước issue này θ nằm thẳng trong `config/rules.toml` (`theta_core = 0.3`, `theta_common = 0.1`). `aggregate` không lưu nhóm kỹ năng (migration 0009 chỉ lưu tỷ lệ); API nhóm lúc đọc bằng θ hiện hành của cấu hình. Sửa hai số đó thì mọi snapshot cũ đổi nhóm ngay, không dấu vết, không phiên bản. Đó là "đổi lặng lẽ".

Quyết định đã chốt với người dùng, không mở lại:

- Bản đóng băng đầu tiên là `theta-1` với θ_core 0,3 và θ_common 0,1: là giá trị đang chạy nên không màn hình nào đổi.
- Đóng băng bằng sổ đăng ký (`config/theta.toml`) và theo từng snapshot (mỗi snapshot lưu phiên bản θ nó đã tính bằng).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - θ có phiên bản và snapshot giữ phiên bản của nó (Priority: P1)

**Why this priority**: AC 1. Đây là phần ngăn đổi lặng lẽ.

**Independent Test**: `tests/core/test_gh102_theta_dong_bang.py`, `tests/steps/test_gh102_aggregate_theta_version.py`, `tests/api/test_gh102_stat_market_theta.py`, `tests/db/test_gh102_snapshot_theta_version.py`.

**Acceptance Scenarios**:

1. **Given** `config/theta.toml` có `theta-1`, **When** nạp `config/rules.toml`, **Then** `rules.theta_version = "theta-1"`, `rules.theta_core`/`theta_common` là giá trị của nó và `rules.theta(version)` đọc được θ của bất kỳ phiên bản nào.
2. **Given** một phiên bản đã nằm trong bản ghi cứng `PINNED` của test, **When** ai đó sửa giá trị, xóa nó hay thêm phiên bản mà không thêm vào `PINNED`, **Then** test ghim đỏ.
3. **Given** sổ đăng ký sai (id trùng hoặc có khoảng trắng ở hai đầu, phiên bản hiện hành không có, giá trị ngoài [0, 1], `common > core`, thiếu khóa, khóa lạ trong một mục hay ở cấp cao nhất, `calibrated_on` không phải ngày `YYYY-MM-DD`, mục đầu tiên không phải `theta-1`, rỗng, thiếu file) hoặc `rules.toml` còn `theta_core`/`theta_common`, **When** nạp cấu hình, **Then** `ConfigError` tiếng Việt (thông báo của `rules.toml` nói θ nay nằm ở `config/theta.toml` và chọn bằng `theta_version`). Số nguyên (`theta_core = 1`, `theta_common = 0`) và `core == common` được chấp nhận.
4. **Given** snapshot S đang `open`, **When** chạy `aggregate`, **Then** `snapshots.theta_version` của S là phiên bản hiện hành; phiên bản hiện hành không có trong sổ đăng ký thì `StepError` và không ghi gì. `replace_stats` chỉ cập nhật hàng `snapshot_id = S AND status = 'open'`; S không có hoặc đã `published`/`partial` thì `ValueError` và không đổi `theta_version`.
5. **Given** snapshot ghi `theta-test` (θ_core 0,5, θ_common 0,15) trong khi cấu hình hiện hành là `theta-1`, **When** gọi `skill-rates`, **Then** kỹ năng được nhóm bằng 0,5/0,15 và `meta.thresholds` là `{theta_version: "theta-test", theta_core: 0.5, theta_common: 0.15, ...}`. Ngược lại, snapshot ghi `theta-1` vẫn nhóm theo 0,3/0,1 khi hiện hành đã đổi.
6. **Given** snapshot có `theta_version` NULL (tính trước đóng băng), **When** đọc ở bất kỳ route số liệu thật nào, **Then** nhóm và `meta.thresholds` theo `PRE_FREEZE_THETA_VERSION` (`theta-1`), dù hiện hành là phiên bản khác. Hằng này không phụ thuộc vị trí: bộ đọc bắt buộc `theta-1` là mục đầu tiên của sổ đăng ký.
7. **Given** snapshot ghi phiên bản không có trong sổ đăng ký, **When** gọi bất kỳ route số liệu thật nào, **Then** `RuntimeError` nêu phiên bản và API trả 500.
8. **Given** mọi route (thật và giả), **Then** `meta.thresholds.theta_version` có mặt; bản giả dùng đúng phiên bản hiện hành và giá trị khớp sổ đăng ký.

---

### User Story 2 - Giá trị đã đóng băng được ghi ở chỗ cả nhóm đọc được (Priority: P1)

**Why this priority**: AC 2.

**Independent Test**: kiểm tay `docs/data/theta.md`; `tests/tools/test_gh102_calibrate_theta.py` cho script in bảng.

**Acceptance Scenarios**:

1. **Given** repo ở commit này, **When** mở `docs/data/theta.md`, **Then** thấy θ là ba nhóm, phiên bản hiện hành, quy tắc "thêm chứ không sửa", bằng chứng hiệu chỉnh của `theta-1` và cách tính lại bảng.
2. **Given** snapshot đọc được có `stat_skill_rates`, **When** chạy `tools/theta/calibrate_theta.py`, **Then** in bảng `core,common` theo vai trò (đủ `min_sample` tin quét, cấp `entry`) cho nhiều cặp θ, chỉ chạy câu SELECT trên `snapshots`, `stat_skill_rates` và `stat_sources`, và chọn snapshot cùng điều kiện với API (đọc được, có hàng tỷ lệ, có nguồn).

## Requirements

- **FR-001**: `config/theta.toml` là sổ đăng ký chỉ-thêm các `[[versions]]` (`id`, `theta_core`, `theta_common`, `calibrated_on`, `note`). `config/rules.toml` chọn phiên bản hiện hành bằng `theta_version`, không còn ghi số θ.
- **FR-002**: `RulesConfig` có `theta_version`, `theta_versions`, `theta(version)`; `theta_core`/`theta_common` giữ nguyên là giá trị của phiên bản hiện hành.
- **FR-003**: `snapshots.theta_version` (text, nullable) ghi bởi `aggregate` (chỉ khi S còn `open`); NULL đọc là `PRE_FREEZE_THETA_VERSION` (`theta-1`), luôn là mục đầu tiên của sổ đăng ký.
- **FR-004**: `Thresholds.theta_version` bắt buộc, chuỗi không rỗng, có ở mọi `Envelope.meta`.
- **FR-005**: `StatMarket` dùng θ của phiên bản trong snapshot được chọn cho cả việc nhóm và `meta.thresholds`.

## Giới hạn đã biết

- Ở n từ 30 đến 40, một tỷ lệ gần 0,3 có sai số chuẩn khoảng ±0,07, nên kỹ năng sát ngưỡng vẫn có thể đổi nhóm giữa hai snapshot dù θ không đổi. Đóng băng chỉ loại nguồn đổi nhóm do ngưỡng, không loại nhiễu lấy mẫu.
- Bảng bằng chứng trong `docs/data/theta.md` là số của snapshot 2026-11-19 do người dùng cung cấp; script tính lại cùng dạng bảng nhưng số thay đổi theo snapshot.
- Đóng băng chỉ chặn đổi giá trị của phiên bản cũ qua test ghim; không có ràng buộc DB (cột `theta_version` là text tự do) nên ai ghi tay một id lạ vào snapshot sẽ gây 500 khi đọc.
- Ghi tay `UPDATE snapshots SET theta_version = ...` sang một id khác đã có trong sổ đăng ký sẽ đổi nhóm của snapshot đó mà không ai hay: không có khóa ngoại hay ràng buộc check, và không test nào bắt.
- Sửa một phiên bản cũ trong `config/theta.toml` rồi sửa `PINNED` trong cùng commit thì test vẫn xanh. Test ghim chỉ làm thay đổi hiện trong diff; người review phải từ chối commit đó.
- Không test nào bắt việc quên đổi `theta_version` (vẫn chạy bằng phiên bản cũ) hay quên tăng `config_version` khi thêm phiên bản. Test ghim bắt phiên bản đã ghim bị sửa, bị xóa hay bị bỏ khỏi `PINNED`; test tài liệu bắt `docs/data/theta.md` thiếu một phiên bản. Chi tiết ở `docs/data/theta.md`.
