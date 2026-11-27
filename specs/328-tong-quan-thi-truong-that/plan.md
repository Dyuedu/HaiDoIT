# Implementation Plan: Toàn cảnh thị trường đọc số thật

**Branch**: `gh-327-tong-quan-thi-truong` | **Date**: 2026-11-19 | **Spec**: [spec.md](spec.md)

## File sẽ sửa

| File | Việc |
|---|---|
| `haido_api/stat_market.py` | `StatMarket.market_overview`, `_overview_rows`, `_role_places` |
| `tests/api/test_ad22_market_overview_stat.py` | Test mới trên Postgres |

`deploy/compose.prod.yml` không đổi: route dùng biến `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES`, đã là `stat`.

**Cập nhật 2026-11-27 (#230)**: các file sau của issue này được #230 sửa thêm, hành vi không đổi: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `docs/api/openapi.json`, `haido_api/fake_market.py`, `haido_api/fixtures/fake_market.json`, `haido_api/market_source.py`, `haido_api/routes/market.py`, `haido_api/stat_market.py`, `tests/api/test_ad17_meta_nguon_stat.py`, `tests/api/test_ad17_routes.py`, `tests/api/test_ad22_market_overview_stat.py`. Xem `specs/230-hinh-soi-tin/plan.md`.
