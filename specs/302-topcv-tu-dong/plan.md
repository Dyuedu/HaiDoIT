# Implementation Plan: TopCV chạy trong lượt đêm trên VPS

**Branch**: `gh-302-topcv-tu-dong` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/302-topcv-tu-dong/spec.md`

## Summary

Áp bản người dùng đề xuất, sửa các lỗi tìm thấy khi rà:
- `topcv.py`: cờ CLI, profile và hàng đợi dưới `data/state/`, cờ Chrome cho container, bỏ fallback URL cũ.
- `pipeline.py`: bọc `xvfb-run`, truyền cờ cho nguồn `nodriver`.
- Image `scraper-browser`: thêm Chrome Stable, Xvfb, `nodriver==0.50.99`.
- `daily.sh`: thêm `topcv`.

## Technical Context

**Language/Version**: Python 3.13, image `scraper-browser` (python:3.13-slim).

**Primary Dependencies**: `nodriver==0.50.99` (bản đang chạy tay), Google Chrome Stable từ kho apt của Google (không ghim được), `xvfb`, `xauth`.

**Storage**: SQLite `data/state/topcv_jobs.db` trong volume `scraper_data`. Không đổi Postgres.

**Testing**: `cd scraper && python -m pytest tests -q`; `uv run pytest tests/deploy -q`.

**Target Platform**: `daily.sh` trên VPS, x86_64, RAM 3,8 GB.

## Constitution Check

- Bỏ quyết định 03/11 theo yêu cầu người dùng ngày 16/11. Ghi trong issue #302, README của scraper, `docs/permissions/`.
- Các nguồn dùng `PoliteClient` giữ nguyên luật dừng khi bị chặn.
- Không viết spec vào `_bmad-output/`.

## Project Structure

```text
specs/302-topcv-tu-dong/                     spec, plan, tasks, research, data-model, tdd
scraper/crawlers/topcv.py                    cờ CLI, PROFILE_DIR, cờ Chrome, xoá Singleton*, bỏ fallback
scraper/pipeline.py                          topcv has_limit + timeout, xvfb-run, truyền cờ nodriver
scraper/Dockerfile.browser                   Chrome Stable, xvfb, xauth, nodriver==0.50.99
scraper/README.md                            ngoại lệ TopCV
deploy/compose.scraper.yml                   shm_size 1g
deploy/daily.sh                              --sources momo,itviec,topcv
deploy/topcv-manual.sh                       bỏ TOPCV_DB
docs/permissions/topcv.md, README.md         trạng thái công tắc
scraper/tests/test_observations.py           test main(), PROFILE_DIR, pipeline
tests/deploy/test_gh302_topcv_tu_dong.py     test daily.sh, Dockerfile, compose, script tay
scraper/ingest.py                            AUTO_SOURCES thêm topcv (17/11)
config/rules.toml                            [sources].auto thêm topcv, config_version 2026-11-17.1 (17/11)
tests/core/test_ad10_rules_config.py         AUTO có topcv; linkedin thay topcv làm nguồn ngoài danh sách (17/11)
tests/steps/test_ad4_ingest.py               ví dụ nguồn chạy tay đổi sang linkedin (17/11)
scraper/crawlers/topcv.py                    trang rỗng để lại thử sau, không dừng listing (18/11, #318)
```

## Complexity Tracking

- `deploy/compose.scraper.yml`, `deploy/daily.sh`: thuộc #90 (không có `specs/`) và #273. Thay đổi không đụng hành vi của #273 (image kho, `.warehouse-tag`); test của #273 chạy lại xanh, ghi ở `specs/273-image-kho-trong-deploy/tdd.md`.
- `scraper/tests/test_observations.py`: #296–#298 chỉ được thêm test mới, test của họ không đổi và vẫn xanh.
- `topcv.py`, `pipeline.py`, `Dockerfile.browser`, `topcv-manual.sh`: git log không có số issue.

**Cập nhật 2026-11-27 (#230)**: các file sau của issue này được #230 sửa thêm, hành vi không đổi: `config/rules.toml`, `tests/core/test_ad10_rules_config.py`. Xem `specs/230-hinh-soi-tin/plan.md`.
