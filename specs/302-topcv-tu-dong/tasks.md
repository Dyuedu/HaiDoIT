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

## Phase 3: Triển khai

- [ ] T010 Chép `scraper/` lên `/opt/haidoit/scraper` (không phải git repo), build `scraper-browser`, chạy thử `pipeline.py crawl --sources topcv --limit 5`
- [ ] T011 Merge sau khi image đã build, vì merge đẩy `daily.sh` mới lên VPS
- [ ] T012 Đêm đầu: log có `[topcv] OK`, `topcv listed=… complete=True`
