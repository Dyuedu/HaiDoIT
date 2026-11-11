# Tasks: Gộp tin trùng chéo nguồn thành cụm

**Input**: Design documents from `specs/100-cross-source-clusters/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test phải fail trước khi có thân hàm.

## Phase 1: Setup

- [x] T001 Tạo `specs/100-cross-source-clusters/` và rule `.cursor/rules/sdd-tdd.mdc`

## Phase 2: Foundational

- [x] T002 Thêm `sources.priority` vào `config/rules.toml` và `haido_core/config.py`, tăng `config_version`

## Phase 3: User Story 1 - Đếm một cụm (Priority: P1)

### Tests

- [x] T003 [P] [US1] Test khóa danh tính và gộp cụm trong `tests/domain/test_dat28_cluster.py`
- [x] T004 [US1] Test bước aggregate: hai nguồn cùng công ty và chức danh cho `n = 1` trong `tests/steps/test_dat20_aggregate_step.py`

### Implementation

- [x] T005 [US1] Hàm thuần trong `haido_core/domain/cluster.py`
- [x] T006 [US1] `haido_core/steps/aggregate.py` phát một `CountedPosting` mỗi cụm
- [x] T007 [US1] `posting_urls` trong `haido_core/db/snapshot_store.py`

## Phase 4: User Story 2 - Đại diện (Priority: P1)

### Tests

- [x] T008 [P] [US2] Test thứ tự đại diện trong `tests/domain/test_dat28_cluster.py`
- [x] T009 [P] [US2] `match_postings` trong nguồn và chéo nguồn trong cùng file test

### Implementation

- [x] T010 [US2] `choose_representative` trong `haido_core/domain/cluster.py`
- [x] T011 [US2] `PostingMatcher.match_postings` trong `haido_core/domain/matching.py`
- [x] T012 [US2] Nhãn ô lấy từ đại diện, `last_seen` là max của thành viên

## Phase 5: Polish

- [x] T013 Cập nhật câu chú thích "mỗi tin là một cụm" trong `haido_core/domain/population.py`
- [x] T014 Chạy `uv run pytest tests/domain/test_dat28_cluster.py tests/domain/test_dat20_population.py tests/core/test_ad10_rules_config.py tests/domain/test_ad2_registry.py -q`

## Phase 6: Cập nhật theo #163 (2026-11-11)

- [x] T015 `config/rules.toml` đổi `config_version` và thêm `level_options`, `level_groups`; `haido_core/config.py` kiểm khóa mới (`sources.priority` giữ nguyên)
- [x] T016 `haido_core/steps/aggregate.py` và `haido_core/db/snapshot_store.py` ghi ô và tỷ trọng theo cấp bậc lọc được; thêm test cụm đếm ở cấp của đại diện trong `tests/steps/test_fr33_aggregate_level_step.py`
- [x] T017 Sửa các số đếm hàng và truy vấn trong `tests/steps/test_dat20_aggregate_step.py` cho khớp cột `seniority` mới (lọc `seniority = 'all'` khi so số cũ)
