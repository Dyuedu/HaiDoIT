# Data model: tỷ lệ kỹ năng (#101)

## `haido.stat_skill_rates` (migration `0009_haido_skill_rates`, nối sau `0008_haido_fact_city`)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| snapshot_id | date, khóa | khóa ngoại tới `stat_cells` |
| role | text, khóa | |
| branch | text, khóa | `all` |
| seniority | text, khóa | `all`, nhóm, hoặc cấp thô |
| years | text, khóa | `any` |
| scope | text, khóa | `vn` |
| skill | text, khóa | mã trong từ vựng |
| n_with | integer | số cụm nhắc kỹ năng; `>= 0` |
| rate | double precision | `n_with / n` của ô, 0 khi n = 0; `0 <= rate <= 1` |
| vocab_version | text | phiên bản từ vựng, ví dụ `seed-2026-11-11` |

Khóa ngoại `(snapshot_id, role, branch, seniority, years, scope)` → khóa chính của `stat_cells`. `replace_stats` xóa bảng này trước `stat_cells`. Không có cột nhóm (core, common, rare): tính lúc đọc từ θ.

Hạ cấp bỏ bảng. `stat_cells`, `stat_city_shares`, `stat_sources`: không đổi.

Số hàng: số ô `(vai trò, cấp)` × số mã từ vựng. 18 vai trò × 9 cấp × 225 = 36.450 hàng mỗi snapshot.
