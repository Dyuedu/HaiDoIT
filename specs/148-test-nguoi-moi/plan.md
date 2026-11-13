# Implementation Plan: Test danh sách người mới

**Branch**: `gh-148-test-nguoi-moi` | **Date**: 2026-11-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification từ `specs/148-test-nguoi-moi/spec.md`

## Summary

Thêm test cho các chỗ hở G1–G5 của review PR #291. Chỉ một đoạn code sản phẩm đổi: bảo vệ entry > n trong `StatMarket.newcomer_roles` (G5). Còn lại là test.

## Technical Context

**Language/Version**: Python 3.12 (FastAPI, SQLAlchemy), TypeScript (Next.js, Vitest, Testing Library)

**Storage**: Postgres test (127.0.0.1:5433; đợt 2 dùng DB riêng `fx148_test`); không đổi schema

**Testing**: pytest (`HAIDO_TEST_DATABASE_URL=...`), `cd web && npx vitest run`

**Project Type**: web (API + web)

## File sẽ sửa

```text
haido_api/stat_market.py                       # G5: RuntimeError khi entry > n
tests/api/test_fr37_newcomer_roles_stat.py     # G1, G2 (API), G5; đợt 2: F2 (n riêng), F4 (biên 30/29), F5 (rowcount)
web/tests/fr37-newcomer-list.test.tsx          # G1, G2, G3, G4 (web); đợt 2: F1 (mọi dòng), F3 (DEC-6 rộng)
specs/148-test-nguoi-moi/*                     # spec, plan, tasks, research, data-model, tdd
specs/144-hinh-nguoi-moi, 145-doc-so-tin-entry, 146-tra-so-nguoi-moi,
specs/147-man-nguoi-moi, 163-loc-ban-do-theo-cap-bac, 280-loc-so-nam-kinh-nghiem
                                               # ghi chú ngày 2026-11-13 và đợt TDD mới
```

## Specs của issue khác bị chạm

- `haido_api/stat_market.py`: #144, #145, #146, #163, #280 (có `specs/`). Đợt 2 không đổi file này.
- `tests/api/test_fr37_newcomer_roles_stat.py`: #145, #146.
- `web/tests/fr37-newcomer-list.test.tsx`: #147.
- Đợt 2 chỉ sửa hai file test trên và `specs/148-test-nguoi-moi/`; không chạm file code sản phẩm mới nên không cần đợt mới ở spec của issue khác.

## Issue cũ cần ghi trong mô tả PR

`git log --format='%h %s' -- haido_api/stat_market.py` có các issue chưa có thư mục `specs/`, nên phải ghi tên trong mô tả PR (đợt 1 đã ghi sai là không có):

- #93 (`190f2e9`, tỷ trọng thành phố, bước publish, nguồn stat)
- #162, #259, #263 (`5a4d9e9`, bản đồ đọc snapshot thật, nguồn theo tin được đếm, loại LinkedIn)

Hai file test không có issue cũ nào thiếu `specs/`.

## Rủi ro

- Test DEC-6 quá rộng sẽ bắt số trong khung "Nguồn và lưu ý"; đã loại khung đó (điểm mở 1 ở spec).
- Bảo vệ entry > n chỉ chạy trong `StatMarket`; `FakeMarket` không đọc DB nên không cần.
