# Data model: phép 2 (#106)

Không đổi. Không bảng, cột hay revision Alembic nào thay đổi. `haido_core/domain/cells.py` không đọc DB: người gọi đưa `lookup`. Nguồn dữ liệu của bản chạy thật là `stat_cells` và `stat_skill_rates` (xem `specs/151-ty-le-ky-nang-that/data-model.md`).
