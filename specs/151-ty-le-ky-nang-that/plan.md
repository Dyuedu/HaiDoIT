# Implementation Plan: Tỷ lệ kỹ năng thật theo vai trò và cấp

**Branch**: `gh-151-ty-le-ky-nang-that` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

`StatMarket.skill_rates` đọc `stat_skill_rates` và `stat_cells`, chọn ô bằng phép 2 theo `n_scanned`, nhóm bằng phép 4, dựng Envelope. Production chuyển nguồn sang `stat`.

## Technical Context

**Language/Version**: Python 3.13, FastAPI, SQLAlchemy 2, Pydantic 2

**Testing**: `uv run pytest tests/api/test_fr19_skill_rates_stat.py tests/deploy/test_gh151_ty_le_ky_nang_doc_snapshot_that.py -q` (cần `HAIDO_TEST_DATABASE_URL` trỏ DB `*_test`); toàn bộ `uv run pytest -q`.

**Constraints**: AD-2 (phép 2 và 4), AD-6, AD-7, AD-17 (cỡ mẫu theo `skill_count`), AD-5.

## Project Structure

```text
haido_api/stat_market.py                                   # skill_rates thật; _display_names, _mid_and_above, _skill_cell_stats, _skill_rate_rows
haido_core/domain/cells.py                                 # phép 2 (#106)
deploy/compose.prod.yml                                    # HAIDO_MARKET_SOURCE_SKILL_RATES: stat
docs/api/envelope-meta.md                                  # mô tả bản thật của skill-rates
tests/api/test_fr19_skill_rates_stat.py                    # mới
tests/api/test_ad17_meta_nguon_stat.py                     # mới (#103)
tests/deploy/test_gh151_ty_le_ky_nang_doc_snapshot_that.py # mới
web/lib/skill-rates.ts, web/lib/skill-profile-view.ts        # đợt 2: rows rỗng khi core_size = 0
web/app/components/skill-profile/skill-profile-screen.tsx   # đợt 2: câu giải thích thay danh sách
web/tests/fr19-skill-profile.test.tsx                       # đợt 2
```

**Structure Decision**: Phép 2 nhận bảng ô qua `lookup` dựng từ hai truy vấn theo khóa (ô của vai trò; `n_scanned` đã ghi); `stat_market.py` không có `select_cell` riêng. Đọc một lần mọi ô của vai trò (tối đa 9 hàng) thay vì một truy vấn mỗi ứng viên.

## Complexity Tracking

- `haido_api/stat_market.py`, `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `haido_core/domain/registry.py`, `haido_core/domain/REGISTRY.md` thuộc nhiều issue cũ: thêm đợt TDD vào `tdd.md` của từng issue có `specs/` (danh sách ở `tdd.md` đợt 2026-11-17 của #151). Không AC cũ nào đổi: `skill-rates` thật là hành vi mới; `learning-path` và `skill-roles` ở `StatMarket` vẫn `UnknownCell`.
- `haido_api/routes/market.py` không sửa (docstring còn ghi "bản thật: #27", lỗi thời, để issue khác).
