# Implementation Plan: MoMo bỏ qua trang chi tiết 404

**Branch**: `gh-296-298-crawler-ben` | **Date**: 2026-11-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/297-momo-bo-qua-404/spec.md`

## Summary

Đưa `try/except requests.RequestException` vào trong vòng tải chi tiết của `crawlers/momo.py`, đếm số trang bỏ qua và số lỗi liền nhau. `BlockedError` vẫn bắt ở ngoài vòng để dừng.

## Technical Context

**Language/Version**: Python 3.13 (image `scraper-browser`)

**Primary Dependencies**: Không thêm gì.

**Storage**: Không đổi.

**Testing**: `cd scraper && python -m pytest tests -q`

**Target Platform**: Lượt đêm `daily.sh`, container `scraper-browser`.

## Constitution Check

- Luật lịch sự: bị từ chối thì dừng, không thử vòng qua.
- Không viết spec vào `_bmad-output/`.

## Project Structure

```text
specs/297-momo-bo-qua-404/          spec, plan, tasks, research, data-model, tdd
scraper/crawlers/momo.py            vòng tải chi tiết
scraper/tests/test_observations.py  thêm install_momo() và ba test
```

## Complexity Tracking

- `scraper/crawlers/momo.py`: git log không có commit gắn số issue, không plan nào trong `specs/` trỏ tới.
- `scraper/tests/test_observations.py` cũng được #296 và #298 sửa trong cùng branch.
