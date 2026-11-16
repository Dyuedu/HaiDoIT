# Data model: Cổng tất định cho thứ tự lộ trình

Không đổi. Không thêm bảng, cột hay revision Alembic; `alembic heads` giữ nguyên. Phép 8 là hàm thuần trên các dataclass đã có ở `haido_core/domain/registry.py` (`PathRequest`, `PathSkill`, `GraphEdge`, `SkillBand`), không đọc cơ sở dữ liệu.

Dữ liệu duy nhất đổi là sổ hoãn `tools/gates/deferred.json`: mục `FR-22` đổi hạn từ 2026-11-22 sang 2026-12-13 và chỉ còn nói về AC2.
