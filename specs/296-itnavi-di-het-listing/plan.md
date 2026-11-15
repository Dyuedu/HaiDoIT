# Implementation Plan: ITnavi đi hết listing

**Branch**: `gh-296-298-crawler-ben` | **Date**: 2026-11-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/296-itnavi-di-het-listing/spec.md`

## Summary

Vòng lặp listing của `crawlers/itnavi.py` đổi điều kiện dừng: trang trống thì dừng; trang trùng hết thì đếm, đủ `STALE_PAGES` trang liên tiếp mới dừng. Khi dừng, đối chiếu số id gặp với tổng in trên trang (`MIN_COVERAGE` 0,9), giống cách `crawlers/topdev.py` đã làm.

## Technical Context

**Language/Version**: Python 3.13 (image scraper)

**Primary Dependencies**: `requests`, `beautifulsoup4`, không thêm gì.

**Storage**: Không đổi. File seen `data/seen/<ngày>/itnavi.json` giữ nguyên định dạng.

**Testing**: `cd scraper && python -m pytest tests -q` (job `scraper` của CI).

**Target Platform**: Lượt đêm `daily.sh` trên VPS, container `scraper`.

**Constraints**: Giữ luật lịch sự: không tăng tốc độ, chỉ thêm tối đa 2 request mỗi đêm.

## Constitution Check

- Lượt chưa xong không được tính "gone": crawler phải nói thật khi chưa đi hết listing.
- Không viết spec vào `_bmad-output/`.

## Project Structure

```text
specs/296-itnavi-di-het-listing/   spec, plan, tasks, research, data-model, tdd
scraper/crawlers/itnavi.py         sửa vòng lặp listing, thêm listed_total()
scraper/tests/test_observations.py thêm test ITnavi
```

## Complexity Tracking

- `scraper/crawlers/itnavi.py` và `scraper/tests/test_observations.py`: git log không có commit nào gắn số issue, `specs/` không có plan nào trỏ tới. Không có spec cũ phải cập nhật.
