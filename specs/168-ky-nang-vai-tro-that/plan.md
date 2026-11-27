# Implementation Plan: Tỷ lệ kỹ năng theo vai trò, số thật

**Branch**: `gh-168-ky-nang-vai-tro-that` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

`StatMarket.skill_roles` chọn snapshot đọc được (như `skill_rates`), đọc một truy vấn `stat_skill_rates` của kỹ năng và các ô entry của `stat_cells`, dựng một dòng cho mỗi vai trò của config, xếp như bản giả, dựng `Envelope`. `skill_roles` kiểm mã kỹ năng với bộ từ vựng (`UnknownSkill`) trước khi mở kết nối, và ném `RuntimeError` khi dữ liệu mâu thuẫn (`n_scanned > n`, hoặc `n_with > 0` ở entry khi `all × all` có `n_with = 0`).

## Technical Context

**Language/Version**: Python 3.13, FastAPI, SQLAlchemy 2, Pydantic 2

**Testing**: `uv run pytest tests/api/test_fr09_skill_roles_stat.py tests/api/test_ad17_meta_nguon_stat.py -q` (cần `HAIDO_TEST_DATABASE_URL` trỏ DB `*_test`, host `127.0.0.1`); toàn bộ `uv run pytest -q`.

**Constraints**: AD-5, AD-7 (chỉ `stat_*`), AD-17 (cỡ mẫu `skill_count`).

## Project Structure

```text
haido_api/stat_market.py                                  # skill_roles thật; _skill_role_rows; docstring
deploy/compose.prod.yml                                   # chỉ sửa comment (đã đặt stat từ #166)
docs/api/envelope-meta.md                                 # skill-roles: bản thật; bảng nguồn
tests/api/test_fr09_skill_roles_stat.py                   # mới
tests/api/test_ad17_meta_nguon_stat.py                    # skill-roles vào REAL, seed ô role all
tests/api/test_fr09_skill_roles.py                        # bỏ test "stat luôn 404"; test đếm lần gọi factory; test UnknownSkill không mở kết nối
tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py  # chỉ docstring
```

**Structure Decision**: Không thêm file deploy test mới: `test_gh309_*` đã sinh từ `SOURCE_ENV` kiểm prod `stat` và local `fake` cho mọi nguồn, `test_gh166_*` kiểm riêng biến này; test #168 sẽ lặp lại.

## Complexity Tracking

- `haido_api/stat_market.py`, `deploy/compose.prod.yml`, `docs/api/envelope-meta.md` và các test trên thuộc nhiều issue cũ: thêm đợt vào `tdd.md` của từng issue có `specs/` (liệt kê trong `tdd.md` của issue này). Không AC nào của #166 và #103 sai đi: xem `tdd.md`.

**Cập nhật 2026-11-27 (#230)**: các file sau của issue này được #230 sửa thêm, hành vi không đổi: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `haido_api/stat_market.py`, `tests/api/test_ad17_meta_nguon_stat.py`, `tests/api/test_fr09_skill_roles_stat.py`. Xem `specs/230-hinh-soi-tin/plan.md`.
