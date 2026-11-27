# Implementation Plan: Đọc số tin entry-level của mỗi vai trò từ cơ cấu cấp bậc toàn quốc

**Branch**: `gh-145-146-so-nguoi-moi` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/145-doc-so-tin-entry/spec.md`

## Summary

Thêm hàm `_national_cells(conn, day, level)` vào `haido_api/stat_market.py`: một câu `SELECT` trên `stat_cells` lấy `role`, `n`, `seniority_mix` của ô `vn` ở một cấp lọc. `StatMarket.newcomer_roles` (#146) gọi hàm này hai lần (`all`, `entry`) trên snapshot do `_latest_readable(conn, "entry")` chọn.

## Technical Context

**Language/Version**: Python 3.13, SQLAlchemy 2, FastAPI

**Primary Dependencies**: Không thêm gói.

**Storage**: Đọc `haido.stat_cells`, `haido.snapshots`, `haido.stat_city_shares`, `haido.stat_sources`. Không đổi schema.

**Testing**: `HAIDO_TEST_DATABASE_URL=… uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q`

**Constraints**: AD-7 (API không tổng hợp trên `job_*`), AD-5 (route không tính).

## Constitution Check

- AD-7: chỉ đọc `stat_*`; test ghi lại SQL và cổng AD-7 kiểm.
- AD-10: nhóm `entry` lấy từ `level_groups` của config.

## Project Structure

```text
haido_api/stat_market.py                     # _national_cells, hằng ENTRY
tests/api/test_fr37_newcomer_roles_stat.py   # test mới (chung với #146)
```

**Structure Decision**: Không thêm module đọc riêng. `stat_market.py` đã giữ mọi phép đọc `stat_*` của API; thêm một hàm cùng kiểu `_cells`.

## Ghi chú 2026-11-13 (#148)

`haido_api/stat_market.py` và `tests/api/test_fr37_newcomer_roles_stat.py` được sửa bởi #148 và #146: thêm bảo vệ entry > n (`RuntimeError`) và các test thứ tự, ô hỏng. Phép đọc của #145 (`_national_cells`) không đổi; không AC nào của #145 đổi.

## Ghi chú 2026-11-15 (gộp main vào #212)

`tests/api/test_fr37_newcomer_roles_stat.py`: lời dựng `create_app` thêm `"learning_path": fake`. `haido_api/stat_market.py` thêm `learning_path` (ném `UnknownCell`, chờ #216), `newcomer_roles` giữ nguyên.

**Cập nhật 2026-11-27 (#230)**: các file sau của issue này được #230 sửa thêm, hành vi không đổi: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `haido_api/stat_market.py`, `tests/api/test_fr37_newcomer_roles_stat.py`. Xem `specs/230-hinh-soi-tin/plan.md`.
