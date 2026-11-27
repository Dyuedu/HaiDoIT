# Implementation Plan: Màn lộ trình học theo chặng

**Branch**: `gh-217-man-lo-trinh` | **Date**: 2026-11-25 | **Spec**: [spec.md](spec.md)

## Summary

Thay trang giữ chỗ `/co-van` (#153) bằng màn lộ trình kiểu roadmap.sh: trục chủ đề ở giữa, cụm kỹ năng so le hai bên, đường nối SVG, ngăn chi tiết bên phải (trên điện thoại ở đáy màn). Số đọc `learning-path` (#212) với `have=`.

## Technical Context

**Language/Version**: TypeScript, Next.js 16, React 19, Tailwind 4, Vitest + Testing Library

**Primary Dependencies**: Không thêm gói (không React Flow, không dagre; xem `research.md`).

**Testing**: `cd web && npx vitest run`; `npx tsc --noEmit`, `npm run lint`, `npm run build`; Chrome headless 360, 1024, 1280px.

**Constraints**: AD-7, AD-17, AD-22, AD-23, DEC-6, FR-20, FR-23, FR-25, #134.

## Project Structure

```text
web/lib/learning-path-view.ts                          # mới: buildLearningPathView, connectorPath
web/lib/learning-path.ts                               # kiểm envelope chặt (#212)
web/lib/skill-profile-view.ts                          # learningPathHref: skill thành tùy chọn (#153)
web/app/co-van/page.tsx                                # thay trang giữ chỗ (#153)
web/app/components/advisor/learning-path-screen.tsx    # mới
web/app/components/advisor/path-graph.tsx              # mới
web/app/components/advisor/path-node.tsx               # mới
web/app/components/advisor/skill-panel.tsx             # mới
web/app/components/advisor/path-placeholder.tsx        # xóa (#153)
web/tests/fr22-lo-trinh-hoc.test.tsx                   # mới
web/tests/helpers/learning-path.ts                     # mới
web/tests/fr22-mo-lo-trinh-tu-ky-nang.test.tsx         # bỏ test trang giữ chỗ, thay bằng màn thật (#153)
```

Phần demo (không sửa file API có sẵn):

```text
haido_api/draft_path.py                                # mới: DraftPathMarket
haido_api/fixtures/draft_learning_path.json            # mới: chủ đề, đồ thị, lời dẫn nháp
haido_api/demo.py                                      # mới: app demo
deploy/compose.demo.yml                                # mới: phủ lên compose.local.yml
tests/api/test_fr22_learning_path_draft.py             # mới (dùng lại _cell, _snapshot của test #151)
```

**Structure Decision**: Một DOM cho cả điện thoại và máy tính, chỉ đổi bằng CSS, để thứ tự đọc luôn là thứ tự API. Các hàng của một bên cao bằng nhau (`auto-rows-fr`) nên đường nối tính bằng tỷ lệ, không đo DOM.

## Demo bằng snapshot thật

1. Postgres của compose.local, tạo database `haido_demo`, chạy `alembic upgrade head` vào đó. Database `haido` không bị đụng.
2. Trên VPS, trong giao dịch chỉ-đọc, `COPY` `snapshots`, `stat_cells`, `stat_city_shares`, `stat_sources`, `stat_skill_rates` của các snapshot `published` hoặc `partial` cần dùng, rồi nạp bằng `psql`. Không lấy `job_*`.
3. Đặt `HAIDO_LOCAL_DB_PASSWORD` bằng mật khẩu Postgres của compose.local (file demo không chứa mật khẩu mặc định), rồi `docker compose -f deploy/compose.local.yml -f deploy/compose.demo.yml up -d --build --wait`

`DraftPathMarket` là lớp riêng, không vào `IMPLEMENTATIONS`, để không biến môi trường nào bật được nó trên prod. Phần dựng chặng dùng chung `build_stages` với `FakeMarket`.

## Đợt 4: chủ đề và chặng chọn một

Sửa hợp đồng #212 (xem `specs/212-hinh-lo-trinh-hoc/plan.md`) và cổng FR-24 (#138: quét `topics[].title` và file nháp). `DraftPathMarket` và `FakeMarket` dùng chung `build_stages`.

## Complexity Tracking


- `learning-path.ts` thuộc #212; `skill-profile-view.ts` thuộc #151, #152, #153, #324; `co-van/page.tsx` và `fr22-mo-lo-trinh-tu-ky-nang.test.tsx` thuộc #153 (và #1, không có `specs/`: ghi trong mô tả PR).
- Commit của `co-van/page.tsx` còn nhắc #154, #206, #207: hành vi của ba issue đó không đổi.

## Thay đổi sau merge (2026-11-25, #216)

Phần ghép của `DraftPathMarket` chuyển vào `haido_api/stat_path.py` và `StatMarket`; nội dung nháp chuyển sang `haido_api/content/learning_path.json`. App demo và màn không đổi.

**Cập nhật 2026-11-27 (#230)**: các file sau của issue này được #230 sửa thêm, hành vi không đổi: `deploy/compose.demo.yml`, `docs/api/envelope-meta.md`, `docs/api/openapi.json`, `haido_api/fake_market.py`, `tests/api/test_fr22_learning_path_draft.py`. Xem `specs/230-hinh-soi-tin/plan.md`.
