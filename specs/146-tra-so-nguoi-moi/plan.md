# Implementation Plan: Trả số tin entry-level, tỷ lệ và n của mỗi vai trò

**Branch**: `gh-145-146-so-nguoi-moi` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/146-tra-so-nguoi-moi/spec.md`

## Summary

Thay bản giữ chỗ `StatMarket.newcomer_roles` (luôn 404) bằng bản thật: chọn snapshot theo `_latest_readable(conn, "entry")`, đọc hai lớp ô bằng `_national_cells` (#145), dựng một dòng cho mỗi vai trò của config, tính `share` qua `suppression_for`, sắp thứ tự như bản giả, dựng `meta` như `city_shares`. Bật nguồn `stat` cho phép này ở `deploy/compose.prod.yml`.

## Technical Context

**Language/Version**: Python 3.13, FastAPI, Pydantic 2, SQLAlchemy 2

**Storage**: Không đổi.

**Testing**: `HAIDO_TEST_DATABASE_URL=… uv run pytest tests/api/test_fr37_newcomer_roles_stat.py tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py -q`

**Constraints**: AD-17 (số ở `Stat` hoặc `meta.cells`), AD-7, AD-22 (web không sắp xếp lại).

## Constitution Check

- AD-17: `display` chỉ do `suppression_for`; số đếm là `n` của ô.
- AD-10: `min_sample`, nhóm `entry`, danh sách vai trò lấy từ config.

## Project Structure

```text
haido_api/stat_market.py                               # StatMarket.newcomer_roles, _cell_meta
deploy/compose.prod.yml                                # HAIDO_MARKET_SOURCE_NEWCOMER_ROLES: stat
docs/api/envelope-meta.md                              # bảng nguồn: newcomer-roles có bản thật
tests/api/test_fr37_newcomer_roles_stat.py             # test mới (chung với #145)
tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py # test mới
specs/144-hinh-nguoi-moi/                              # cạnh biên "stat trả 404" không còn đúng: thêm đợt TDD
```

**Structure Decision**: Không gom phần dựng `meta` chung với `city_shares` thành hàm riêng trong lượt này; hai chỗ giống nhau sáu dòng, gom lại sẽ đụng code của #93, #163, #280 mà không đổi hành vi.
