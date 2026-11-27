# Tasks: Hiệu chỉnh và đóng băng θ_core, θ_common

**Input**: Design documents from `specs/102-dong-bang-theta/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi sửa code.

## Phase 1: Tests

- [x] T001 [US1] Test bộ đọc sổ đăng ký, các ca `ConfigError`, và test ghim `PINNED`, trong `tests/core/test_gh102_theta_dong_bang.py`
- [x] T002 [US1] Test migration 0010: cột `snapshots.theta_version` text nullable, trong `tests/db/test_gh102_snapshot_theta_version.py`
- [x] T003 [US1] Test `aggregate` ghi `theta_version`, từ chối phiên bản lạ, trong `tests/steps/test_gh102_aggregate_theta_version.py`
- [x] T004 [US1] Test `StatMarket` nhóm và ghi `meta.thresholds` theo θ của snapshot; NULL là `theta-1`; phiên bản lạ là `RuntimeError`/500; mọi route, trong `tests/api/test_gh102_stat_market_theta.py`
- [x] T005 [US1] Test `meta.thresholds.theta_version` ở mọi route bản giả và `Thresholds`, trong `tests/api/test_gh102_theta_version_fake.py`
- [x] T006 [US2] Test script `tools/theta/calibrate_theta.py`, trong `tests/tools/test_gh102_calibrate_theta.py`
- [x] T007 Cập nhật test cũ có `thresholds`/`theta_*` (xem plan), chạy, ghi RED vào `tdd.md`

## Phase 2: Implementation

- [x] T008 `config/theta.toml`, `config/rules.toml`, `haido_core/config.py`
- [x] T009 Migration 0010, `haido_core/db/tables.py`, `snapshot_store.replace_stats`, `steps/aggregate.py`
- [x] T010 `Thresholds.theta_version`, `fake_market.json`, `stat_market.py`
- [x] T011 Sinh lại fixture web, `web/lib/city-shares.ts`, `envelopes.ts`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`
- [x] T012 `docs/data/theta.md`, `tools/theta/calibrate_theta.py`
- [x] T013 Chạy GREEN, ghi `tdd.md`; chạy kiểm đột biến
- [x] T014 Cập nhật `specs/` của các issue cũ đã đụng tới cùng file (xem `tdd.md`)

## Phase 3: Sửa theo review (2026-11-19)

- [x] T015 [US1] Test trước: `replace_stats` chỉ ghi snapshot `open` (`tests/db/test_gh102_snapshot_theta_version.py`)
- [x] T016 [US2] Test trước: script bỏ snapshot thiếu `stat_sources`, `n_scanned == min_sample` được tính, bắt SQL chỉ SELECT ba bảng (`tests/tools/test_gh102_calibrate_theta.py`)
- [x] T017 [US1] Test trước: bộ đọc từ chối khóa `theta_core`/`theta_common` cũ, mục đầu khác `theta-1`, thiếu `theta-1`, id có khoảng trắng, `calibrated_on` sai, khóa lạ; cận dưới; ca chấp nhận; tách test ghim (`tests/core/test_gh102_theta_dong_bang.py`)
- [x] T018 [US1] Test: NULL đọc là `theta-1` ở cả bốn route khi hiện hành đổi; 500 trả thông báo chung (`tests/api/test_gh102_stat_market_theta.py`)
- [x] T019 [US2] Test tài liệu: mọi id đã ghim có trong `docs/data/theta.md`, bảng "Phiên bản hiện hành" đánh dấu `rules.theta_version` (`tests/core/test_gh102_theta_dong_bang.py`)
- [x] T020 Code: `snapshot_store.replace_stats`, `haido_core/config.py`, `haido_api/stat_market.py`, `tools/theta/calibrate_theta.py`
- [x] T021 Tài liệu: `docs/data/theta.md` (quy tắc 2, giới hạn, luật bộ đọc), sửa FR-9 của #101, FR-003 và data-model của #151, các mục "Đợt #102" của #100, #163, #280, #283, #284, #285, #296, #302
- [x] T022 Ghi RED, GREEN, đột biến vào `tdd.md`

- [x] T-230 Cập nhật 2026-11-27 theo #230: thêm nguồn `posting_check` (và các mục cộng thêm) vào các file của issue này; kiểm bằng `tdd.md` mục "Đợt sửa 2026-11-27"
