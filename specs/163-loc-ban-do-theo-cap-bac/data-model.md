# Data model: Số theo cấp bậc của bản đồ

## Config (`config/rules.toml`, `config_version` tăng từ `2026-11-10.3` lên `2026-11-11.1`)

| Khóa | Ý nghĩa |
|---|---|
| `level_options` | Mã cấp lọc theo thứ tự hiển thị, không gồm `all`: `entry`, `intern`, `fresher`, `junior`, `mid`, `senior`, `lead`, `unknown`. Mỗi mã là một nhóm trong `level_groups` hoặc một mã trong `labels.level`; mọi mã của `labels.level` phải có mặt |
| `[level_groups]` | Nhóm cấp. Tên nhóm và mã trong `level_options` chỉ gồm `a-z0-9_`. Bản đầu: `entry = ["intern", "fresher", "junior"]` (#134). Thành viên là mã của `labels.level`, không gồm `unknown`, không trùng nhau giữa các nhóm, tên nhóm không trùng mã cấp và không phải `all` |

`haido_core/config.py` thêm `ALL_LEVELS = "all"`, và `RulesConfig.level_options`, `RulesConfig.level_groups`. `min_sample`, `theta_core`, `theta_common`, `coverage_notes` không đổi (#260).

## Bảng `haido.stat_city_shares` (đổi)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| snapshot_id | date | khóa, FK `snapshots` |
| role | text | khóa |
| **seniority** | text, not null | **mới**, khóa. `all` hoặc mã cấp lọc. Hàng cũ nhận `all` |
| city | text | khóa |
| share | float8 | 0–1 |

Khóa chính: `(snapshot_id, role, seniority, city)` (trước đây không có `seniority`).

## Bảng `haido.stat_cells` (không đổi schema)

Cột `seniority` đã nằm trong khóa chính từ 0003 và mới chỉ chứa `all`. Từ nay chứa `all` và từng mã cấp lọc. `seniority_mix` của ô cấp `L` chỉ gồm các cấp thành viên của `L` có tin, cộng lại bằng `n`.

## Revision Alembic

`0005_haido_city_share_level`, `down_revision = "0004_haido_stat_sources"`.

- `upgrade`: thêm cột `seniority` (`server_default 'all'` để lấp hàng cũ), đổi khóa chính sang `(snapshot_id, role, seniority, city)`, bỏ `server_default`.
- `downgrade`: xóa hàng có `seniority <> 'all'`, trả khóa chính cũ, bỏ cột.

Một head: `0005_haido_city_share_level`.

## Số hàng mỗi snapshot

Với R vai trò (cả `all`) và L cấp lọc (cả `all`): `stat_cells` có `R × L × 6` hàng, `stat_city_shares` có `R × L × 5`. Bản đầu R = 11, L = 9: 594 và 495.

## Mã ô trong envelope

| Cấp | `cell_id` | Ví dụ |
|---|---|---|
| `all` | `<scope>.<role>` (như cũ) | `ha_noi.backend`, `vn.backend` |
| khác | `<scope>.<role>.<level>` | `ha_noi.backend.entry`, `vn.backend.entry` |

## `data.level` (API, mới)

`CitySharesData.level: str` là cấp đã dùng (`all` khi không gửi `level`). Không có bảng hay cột nào mới cho trường này.
