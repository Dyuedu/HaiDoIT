# Tasks: Màn lộ trình học theo chặng

**Input**: `specs/217-man-lo-trinh/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test chặng, thứ tự, nút, nền tảng, quay về, chưa đủ dữ liệu, trong `web/tests/fr22-lo-trinh-hoc.test.tsx`
- [x] T002 Test đánh dấu đã có, chặng đang học, khung Học tiếp, số của API
- [x] T003 Test ngăn chi tiết: mở, đóng, focus, `?skill=`
- [x] T004 Test chọn vai trò, `not_ready`, lỗi
- [x] T005 Test đường nối và một DOM; envelope sai hợp đồng
- [x] T006 Thay test trang giữ chỗ trong `web/tests/fr22-mo-lo-trinh-tu-ky-nang.test.tsx`

## Phase 2: Implementation

- [x] T007 `web/lib/learning-path.ts`: kiểm envelope
- [x] T008 `web/lib/learning-path-view.ts`, `learningPathHref`
- [x] T009 `path-node.tsx`, `path-graph.tsx`, `skill-panel.tsx`, `learning-path-screen.tsx`, `web/app/co-van/page.tsx`; xóa `path-placeholder.tsx`
- [x] T010 Cập nhật specs #151, #152, #153, #212, #309, #324

## Phase 3: Kiểm tay

- [x] T011 Chrome headless 360, 1024, 1280px trên `next start` với API local (nguồn giả)

## Phase 4: Demo bằng snapshot thật (một phần #216)

- [x] T012 Test `tests/api/test_fr22_learning_path_draft.py`
- [x] T013 `haido_api/draft_path.py`, `haido_api/demo.py`, `deploy/compose.demo.yml`
- [x] T014 Nạp snapshot prod vào `haido_demo`, build lại image, xem màn Backend, Data Engineer, Frontend

## Phase 5: Làm lại theo chủ đề (2026-11-25)

- [x] T015 Test API: chủ đề, chặng chọn một, cổng FR-24, nội dung nháp
- [x] T016 Schema, `topic_stages`, `build_stages`, bản giả, bản nháp, openapi, fixture web
- [x] T017 Test màn: chủ đề, chọn một, màu và chú giải, tên ngắn, lựa chọn thay thế
- [x] T018 `path-graph.tsx`, `path-node.tsx`, `skill-panel.tsx`, `learning-path-screen.tsx`, `learning-path-view.ts`
- [x] T019 Chrome headless 360, 1024, 1280px trên image thật; cập nhật specs các issue bị đụng

## Phase 6: Hướng B — CV Advisor & mở khóa chọn cấp bậc (2026-11-27)

- [x] T020 Mở khóa chọn `level` trên `co-van/page.tsx`, `learning-path-view.ts`, `learning-path-screen.tsx` và cập nhật `web/tests/fr22-lo-trinh-hoc.test.tsx` (test `senior`)
- [x] T021 Thêm `web/lib/advisor-roadmap.ts`, `cv-advisor-form.tsx`, `POST` proxy và `web/tests/advisor-cv-roadmap.test.tsx`

- [x] T-230 Cập nhật 2026-11-27 theo #230: thêm nguồn `posting_check` (và các mục cộng thêm) vào các file của issue này; kiểm bằng `tdd.md` mục "Đợt sửa 2026-11-27"
