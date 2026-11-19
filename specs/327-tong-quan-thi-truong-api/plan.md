# Implementation Plan: Hình response của toàn cảnh thị trường và dữ liệu giả

**Branch**: `gh-327-tong-quan-thi-truong` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

## Summary

Thêm `GET /api/v1/market-overview`. Một hàm thuần chia số đếm thành tỷ trọng và tỷ lệ đã ẩn theo ngưỡng; bản giả gom số đếm từ `fake_market.json`.

## Technical Context

Python 3.13, FastAPI, Pydantic. Không đổi DB.

## File sẽ sửa

| File | Việc |
|---|---|
| `haido_api/schemas/market.py` | Thêm `OverviewShare`, `OverviewRole`, `MarketOverviewData` |
| `haido_api/market_overview.py` | Mới: `OverviewCounts`, `year_buckets`, `build_market_overview` |
| `haido_api/market_source.py` | Thêm `market_overview` vào `MarketReadModel` |
| `haido_api/fake_market.py` | `FakeMarket.market_overview` |
| `haido_api/fixtures/fake_market.json` | Mục `market_overview`: Hà Nội/TP.HCM của tám vai trò, mốc số năm |
| `haido_api/routes/market.py` | Route `/market-overview`, nguồn của `newcomer_roles` |
| `docs/api/envelope-meta.md`, `docs/api/openapi.json` | Mô tả route, sinh lại OpenAPI |
| `web/tests/fixtures/market-overview.json` | Response của bản giả |
| `tests/api/test_ad22_market_overview.py` | Test mới |
| `tests/api/test_ad17_routes.py` | Thêm route vào `SAMPLE_QUERY` |

## Issue cũ có file bị đụng

- `haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`: chỉ thêm, không đổi hành vi cũ. Các issue có `specs/` từng đụng (#146, #151, #163, #166, #168, #212, #280, #309) được thêm đợt tdd.
