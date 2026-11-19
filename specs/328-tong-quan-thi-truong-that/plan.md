# Implementation Plan: Toàn cảnh thị trường đọc số thật

**Branch**: `gh-327-tong-quan-thi-truong` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

## File sẽ sửa

| File | Việc |
|---|---|
| `haido_api/stat_market.py` | `StatMarket.market_overview`, `_overview_rows`, `_role_places` |
| `tests/api/test_ad22_market_overview_stat.py` | Test mới trên Postgres |

`deploy/compose.prod.yml` không đổi: route dùng biến `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES`, đã là `stat`.
