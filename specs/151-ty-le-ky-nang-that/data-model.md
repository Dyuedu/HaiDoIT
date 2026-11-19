# Data model: tỷ lệ kỹ năng thật (#151)

Không đổi. Không bảng, cột hay revision Alembic nào thay đổi; head vẫn `0009_haido_skill_rates`.

Chỉ đọc, theo khóa, phạm vi `vn`, nhánh `all`, số năm `any` (cột của `specs/101-ty-le-ky-nang/data-model.md`):

- `snapshots`, `stat_sources`: chọn snapshot (`published` hoặc `partial`, có nguồn, có hàng `stat_skill_rates`) và `meta.sources`.
- `stat_cells`: `seniority`, `n`, `seniority_mix` của mọi ô của vai trò. `n` thành `meta.cells[..].n`; `seniority_mix` thành cơ cấu cấp của ô và nguồn của câu "Mid trở lên".
- `stat_skill_rates`: `(seniority, n_scanned)` khác nhau của vai trò (`n_scanned` cùng giá trị ở mọi hàng của ô) và các hàng `(skill, n_with, rate)` của ô được chọn. `n_scanned` thành cỡ mẫu quyết định ô và `n_by_measure.skill_count`.

Nhóm (`core`, `common`, `rare`) tính lúc đọc, không lưu, bằng θ của phiên bản ghi ở `snapshots.theta_version` của snapshot đã chọn (giá trị trong `config/theta.toml`; #102).
