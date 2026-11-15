# Implementation Plan: TopDev thử lại khi rớt kết nối

**Branch**: `gh-296-298-crawler-ben` | **Date**: 2026-11-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/298-topdev-thu-lai-ket-noi/spec.md`

## Summary

Thêm `get_listing_page()` trong `crawlers/topdev.py`: bọc `client.get` bằng vòng thử lại cho lỗi kết nối và timeout, chờ tăng gấp đôi. `fetch_results_page()` gọi hàm này thay cho `client.get`.

## Technical Context

**Language/Version**: Python 3.13 (image `scraper`)

**Primary Dependencies**: `requests`, không thêm thư viện thử lại.

**Storage**: Không đổi.

**Testing**: `cd scraper && python -m pytest tests -q`

**Target Platform**: Lượt đêm `daily.sh`, container `scraper`.

## Constitution Check

- Luật lịch sự: `BlockedError` không thử lại; thử lại chỉ cho lỗi mạng, có chờ, không dồn request.
- Không viết spec vào `_bmad-output/`.

## Project Structure

```text
specs/298-topdev-thu-lai-ket-noi/   spec, plan, tasks, research, data-model, tdd
scraper/crawlers/topdev.py          thêm get_listing_page(), CONNECT_TRIES, CONNECT_WAIT
scraper/tests/test_observations.py  thêm bốn test TopDev
```

## Complexity Tracking

- `scraper/crawlers/topdev.py`: git log không có commit gắn số issue, không plan nào trong `specs/` trỏ tới.
