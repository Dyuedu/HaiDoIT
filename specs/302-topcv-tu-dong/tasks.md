# Tasks: TopCV chạy trong lượt đêm trên VPS

**Input**: Design documents from `specs/302-topcv-tu-dong/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi sửa code.

## Phase 1: Tests

- [x] T001 [US1] Test trang 1 bị chặn: file seen không có URL cũ, trong `scraper/tests/test_observations.py`
- [x] T002 [US2] Test `DB_PATH`, `PROFILE_DIR` mặc định dưới `data/state`
- [x] T003 [US3] Test `--skip-details`, `--limit` của `topcv.py`
- [x] T004 [US3] Test `pipeline.py` truyền cờ, bọc `xvfb-run`, timeout 6 giờ; không bọc khi có `DISPLAY` hoặc với momo/itviec
- [x] T005 [US4] Test `daily.sh`, `Dockerfile.browser`, `compose.scraper.yml`, `topcv-manual.sh` trong `tests/deploy/test_gh302_topcv_tu_dong.py`

## Phase 2: Implementation

- [x] T006 Sửa `scraper/crawlers/topcv.py`
- [x] T007 Sửa `scraper/pipeline.py`
- [x] T008 Sửa `scraper/Dockerfile.browser`, `deploy/compose.scraper.yml`, `deploy/daily.sh`, `deploy/topcv-manual.sh`
- [x] T009 Sửa `scraper/README.md`, `docs/permissions/topcv.md`, `docs/permissions/README.md`

## Phase 4: Sửa sau lượt thử 16/11

- [x] T013 [US5] Test `listed_total`, tải lại trang rỗng, so với tổng trên tiêu đề, trong `scraper/tests/test_observations.py`
- [x] T014 Thêm `EMPTY_PAGE_TRIES`, `MIN_COVERAGE`, `listed_total()` và tham số `problems` trong `scraper/crawlers/topcv.py`
- [x] T015 Chạy lại `--sources topcv --skip-details` trên VPS: `complete=True`, số tin gần tổng trên tiêu đề

## Phase 5: Ingest bỏ sót TopCV (2026-11-17)

- [x] T016 [US6] Test `topcv` trong `ingest.AUTO_SOURCES` (`scraper/tests/test_observations.py`) và trong `auto_sources` (`tests/core/test_ad10_rules_config.py`)
- [x] T017 Đổi ví dụ nguồn chạy tay trong `tests/steps/test_ad4_ingest.py` từ `topcv` sang `linkedin`
- [x] T018 Thêm `topcv` vào `scraper/ingest.py` và `config/rules.toml`, tăng `config_version`
- [ ] T019 Đêm đầu sau merge: ingest có dòng `topcv listed=… complete=True`, kho ghi 8 lượt chạy

## Phase 3: Triển khai

- [x] T010 Chép `scraper/` lên `/opt/haidoit/scraper` (không phải git repo), build `scraper-browser`, chạy thử `pipeline.py crawl --sources topcv --limit 5`
- [x] T011 Merge sau khi image đã build, vì merge đẩy `daily.sh` mới lên VPS
- [x] T012 Đêm đầu (17/11): log có `[topcv] OK in 6978s`, `seen: 2399 jobs, listing_complete=True`; nhưng ingest bỏ qua TopCV, xem Phase 5
