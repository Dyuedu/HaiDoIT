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

## Đợt 2 (2026-11-16): quyết định của người dùng và sửa theo review

### Tests (RED)

- [x] T020 `tests/domain/test_dat29_skill_rates.py`: hợp kỹ năng của cụm, hợp chỉ gồm thành viên khớp ô, cụm chưa quét, `{}` khác NULL, `n_scanned` chung của ô và `<= n`
- [x] T021 `tests/steps/test_dat29_aggregate_skill_rates_step.py`: cụm hai nguồn (đại diện NULL, tin kia nhắc Python; cả hai nhắc Python), mẫu số theo cụm đã quét (`backend/all/python = 2/2`), dấu `vocab_version`, từ chối phiên bản lẫn, cũ, NULL; không chặn khi chưa quét hoặc ngoài cửa sổ
- [x] T022 `tests/steps/test_gh283_ingest_classify.py`: từ vựng đổi thì ingest kế tiếp quét lại; dữ kiện NULL cũng quét lại
- [x] T023 `tests/db/test_dat29_stat_skill_rates.py`: cột `n_scanned`, CHECK, chỉ mục, cột `vocab_version`, hạ cấp, `replace_stats` bắt buộc `skill_rates` và kiểm `n_scanned <= n`
- [x] T024 `tests/domain/test_dat29_skill_groups.py`: θ NaN, vô hạn, ngoài [0, 1], biên 0 và 1, `skill_id` trùng

### Code (GREEN)

- [x] T030 `population.py` (`postings_in_window`, `matches_cell`), `skill_rates.py` dùng lại; `n_scanned`, hợp, mẫu số cụm đã quét (D1, D2, R3)
- [x] T031 Migration 0009 sửa tại chỗ: `n_scanned`, CHECK, chỉ mục `(snapshot_id, skill)`, `job_posting_facts.vocab_version`; `tables.py` (D2, D3, R1)
- [x] T032 `snapshot_store.py`: `FactVersion.vocab_version`, `stale_in_window`, `replace_stats` (bắt buộc, kiểm n_scanned) (D3, R4)
- [x] T033 `ingest.py` ghi và so `vocab_version`; `aggregate.py` hợp kỹ năng, kiểm và đóng dấu phiên bản (D1, D3)
- [x] T034 `skill_groups.py` kiểm θ và `skill_id` trùng (R2); `REGISTRY.md` (R5)
- [x] T035 `tools/bench_skill_rates.py` và số đo vào `tdd.md`, SC-001 (R6)
- [x] T036 Điểm mở ở `spec.md` (R8); sửa các đợt 2026-11-16 của #100, #163, #280, #283, #285 (R7); đợt mới của #283 (D3)
- [x] T037 Chạy toàn bộ, ruff, cổng, determinism, đột biến
