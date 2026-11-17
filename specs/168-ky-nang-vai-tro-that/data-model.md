# Data model: tỷ lệ kỹ năng theo vai trò, số thật (#168)

Không đổi. Không bảng, cột hay revision Alembic nào thay đổi.

Chỉ đọc, theo khóa, phạm vi `vn`, nhánh `all`, số năm `any`:

- `snapshots`, `stat_sources`: chọn snapshot đọc được và `meta.sources`.
- `stat_skill_rates`: hàng của một kỹ năng ở cấp `entry` (mọi vai trò): `role`, `n_scanned` (thành `n_by_measure.skill_count`), `rate`; và hàng `role = all`, `seniority = all`: `n_with` (thành `mentioned = n_with > 0`).
- `stat_cells`: ô `vn.<role>.entry`: `n`, `seniority_mix`.
