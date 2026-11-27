# Implementation Plan: Endpoint tỷ lệ kỹ năng giả theo vai trò và cấp

**Branch**: `gh-111-ho-so-ky-nang` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

## Summary

Mở rộng `GET /api/v1/skill-rates` của bản giả: kiểm `level`, nhận `have`, trả cờ `have` từng dòng và hai số đếm core; bản giả sắp dòng; fixture thêm `entry` và `all` cho mọi vai trò.

## Technical Context

**Language/Version**: Python 3.13, FastAPI, Pydantic 2

**Testing**: `uv run pytest tests/api -q`; sinh lại OpenAPI bằng `HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api -q`.

**Constraints**: AD-17 (Envelope), AD-22 (đếm trên mã kỹ năng chỉ ở API), AD-5 (route không tính).

## Project Structure

```text
haido_api/routes/market.py                       # level: LevelCode, have
haido_api/schemas/market.py                      # SkillRateRow.have, SkillRatesData.core_size/have_core
haido_api/market_source.py                       # chữ ký skill_rates(role, level, have)
haido_api/fake_market.py                         # sắp dòng, have, đếm core
haido_api/stat_market.py                         # chữ ký mới, vẫn UnknownCell
haido_api/fixtures/fake_market.json              # entry + all cho mọi vai trò
docs/api/openapi.json                            # sinh lại
tests/api/test_fr19_skill_rates_vai_tro_cap.py   # mới
tests/api/test_ad17_web_fixtures.py              # fixture web của skill-rates
web/tests/fixtures/skill-rates-*.json            # mới
```

**Structure Decision**: Đếm core đặt ở bản giả (sau này ở bản thật), không ở route, theo AD-5.

## Complexity Tracking

- Các file `haido_api/*` thuộc nhiều issue cũ: thêm đợt TDD cho issue nào có `specs/` (xem `tdd.md` của #152).

**Cập nhật 2026-11-27 (#230)**: các file sau của issue này được #230 sửa thêm, hành vi không đổi: `docs/api/envelope-meta.md`, `docs/api/openapi.json`, `haido_api/fake_market.py`, `haido_api/fixtures/fake_market.json`, `haido_api/main.py`, `haido_api/market_source.py`, `haido_api/routes/market.py`, `haido_api/stat_market.py`, `tests/api/test_ad17_ordinal_allowlist.py`, `tests/api/test_ad17_routes.py`, `tests/api/test_ad17_web_fixtures.py`. Xem `specs/230-hinh-soi-tin/plan.md`.
