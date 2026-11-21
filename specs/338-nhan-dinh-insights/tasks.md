# Tasks: Nhận định trên trang Insights

**Input**: Design documents từ `specs/338-nhan-dinh-insights/`

## Phase 1: Tests (RED trước)

- [ ] T001 [US1] Test takeaways mở rộng market-overview: `web/tests/fr338-market-overview-takeaways.test.tsx`
- [ ] T002 [P] [US2] Test newcomer takeaways: `web/tests/fr338-newcomer-takeaways.test.tsx`
- [ ] T003 [P] [US3] Test skill-roles insight: `web/tests/fr338-skill-roles-insight.test.tsx`

## Phase 2: Implementation (GREEN)

- [ ] T004 [US1] Mở rộng `takeaways()` trong `web/lib/market-overview-view.ts` — thêm câu hướng dẫn hành động
- [ ] T005 [P] [US2] Thêm field `takeaways` vào `NewcomerView` và hàm `buildNewcomerView` trong `web/lib/newcomer-roles-view.ts`
- [ ] T006 [P] [US3] Thêm field `insight` vào `SkillRolesView` và hàm `buildSkillRolesView` trong `web/lib/skill-roles-view.ts`

## Phase 3: UI

- [ ] T007 [US2] Hiển thị `takeaways` mới trong `web/app/components/insights/newcomer-screen.tsx`
- [ ] T008 [P] [US3] Hiển thị `insight` mới trong `web/app/components/insights/skill-roles-screen.tsx`

## Dependencies

- T001, T002, T003 chạy song song → RED
- T004, T005, T006 chạy song song (khác file) → GREEN
- T007 sau T005; T008 sau T006
