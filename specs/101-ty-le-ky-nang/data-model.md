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
| n_with | integer | số cụm đã quét nhắc kỹ năng; `>= 0` và `<= n_scanned` |
| n_scanned | integer | số cụm đã quét của ô (mẫu số), cùng giá trị ở mọi hàng của ô; `<= n` của `stat_cells` (kiểm ở `replace_stats`, DB không kiểm chéo bảng). Là `n_with_value` của AD-17 |
| rate | double precision | `n_with / n_scanned`, 0 khi `n_scanned = 0`; `0 <= rate <= 1` |
| vocab_version | text | phiên bản từ vựng của dữ kiện đã đọc, ví dụ `seed-2026-11-11` |

CHECK: `n_with >= 0`, `n_with <= n_scanned` (`ck_stat_skill_rates_n_with_scanned`), `0 <= rate <= 1`. Chỉ mục phụ `ix_stat_skill_rates_snapshot_skill` trên `(snapshot_id, skill)` cho #168 đọc một kỹ năng qua các vai trò.

Khóa ngoại `(snapshot_id, role, branch, seniority, years, scope)` → khóa chính của `stat_cells`. `replace_stats` xóa bảng này trước `stat_cells`. Không có cột nhóm (core, common, rare): tính lúc đọc từ θ.

## `haido.job_posting_facts` (cùng migration 0009)

Thêm cột `vocab_version` text, nullable: phiên bản từ vựng đã dùng để quét `skills` lúc ingest. NULL ở dữ kiện cũ; ingest coi NULL là khác phiên bản hiện hành và quét lại các tin trong cửa sổ (thêm phiên bản dữ kiện mới, bảng vẫn chỉ-thêm).

0009 chưa push và chưa áp dụng ở đâu, nên được sửa tại chỗ (đợt 2, 2026-11-16) thay vì thêm 0010.

Hạ cấp bỏ bảng `stat_skill_rates` (kéo theo chỉ mục) rồi bỏ cột `job_posting_facts.vocab_version`. `stat_cells`, `stat_city_shares`, `stat_sources`: không đổi.

Số hàng: số ô `(vai trò, cấp)` × số mã từ vựng. 18 vai trò × 9 cấp × 225 = 36.450 hàng mỗi snapshot.
