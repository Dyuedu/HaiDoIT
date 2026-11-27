# Implementation Plan: Production không bao giờ phục vụ fixture giả của thị trường

**Branch**: `gh-309-prod-khong-doc-du-lieu-gia` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

Đặt `stat` cho hai biến còn thiếu trong compose.prod và thêm test đọc `SOURCE_ENV` để mọi phép sau này phải có dòng `stat`.

## Technical Context

Python 3.13, pytest, PyYAML (đã có trong test deploy của #146, #166). Không đổi mã API, không đổi DB.

## File sẽ sửa

| File | Việc |
|---|---|
| `deploy/compose.prod.yml` | Thêm `HAIDO_MARKET_SOURCE_SKILL_RATES: stat`, `HAIDO_MARKET_SOURCE_LEARNING_PATH: stat` |
| `tests/deploy/test_gh309_prod_khong_doc_du_lieu_gia.py` | Test mới (FR-001, FR-002, FR-003) |
| `docs/api/envelope-meta.md` | Bảng nguồn: prod đặt `stat` cho mọi phép; sửa dòng `skill_roles` đã cũ ("chưa compose nào đặt") |

## Issue cũ có file bị đụng

- `deploy/compose.prod.yml`: #1, #162 (chưa có `specs/`), #262, #273, #146, #166 (có `specs/`, thêm đợt tdd).
- `docs/api/envelope-meta.md`: nhiều issue; chỉ bảng nguồn đổi, không đổi hình response.

**Cập nhật 2026-11-27 (#230)**: các file sau của issue này được #230 sửa thêm, hành vi không đổi: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`. Xem `specs/230-hinh-soi-tin/plan.md`.
