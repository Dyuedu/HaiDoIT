# Tasks: Tỷ lệ kỹ năng theo ô, nhóm kỹ năng theo θ

**Input**: `specs/101-ty-le-ky-nang/`

Test đứng trước code. Mỗi test mới phải đỏ trước khi có code (ghi trong tdd.md).

## Phase 1: Tests (RED)

- [x] T001 `tests/domain/test_dat29_skill_groups.py`: ranh giới đúng θ, rỗng, một và lô, thứ tự, θ theo từng lần gọi, đầu vào sai
- [x] T002 `tests/domain/test_dat29_skill_rates.py`: dày, n = 0, đếm cụm, cửa sổ, vai trò, cấp và nhóm, chỉ vn và any, mã lạ, n lệch
- [x] T003 `tests/db/test_dat29_stat_skill_rates.py` (Postgres): migration 0009, cột, khóa, khóa ngoại tới `stat_cells`, ràng buộc, hạ cấp
- [x] T004 `tests/steps/test_dat29_aggregate_skill_rates_step.py`: dày, khóa ô, `rate = n_with / n`, cửa sổ, cụm, nguồn bị loại, chạy lại, đã chốt, lỗi giữa chừng

## Phase 2: Implementation (GREEN)

- [x] T010 `skill_groups.py` (phép 4)
- [x] T011 `skill_rates.py`, `CountedPosting.skills`
- [x] T012 `tables.py`, migration 0009, `snapshot_store.replace_stats`
- [x] T013 `steps/aggregate.py`, `cli.py`
- [x] T014 Đổi test cũ kiểm head sang 0009 và thêm bảng vào danh sách bảng
- [x] T015 Chạy toàn bộ, ruff, cổng, determinism (`PYTHONHASHSEED` 0 và 1); đo thời gian trên bản sao dữ liệu thật
- [x] T016 Cập nhật spec của #100, #163, #280, #283, #285 (`plan.md`, `tasks.md`, đợt TDD mới)
