# TDD: Nhận định trên trang Insights (#338)

**Lệnh test**: `cd web && npx vitest run`

## Danh sách hành vi cần test

### Market overview takeaways (US1)
1. Có câu gợi ý vai trò cho người chưa chọn hướng (dựa trên `roles_by_entry_share`)
2. Có câu khuyến khích khi tỷ trọng "0 năm" + "không ghi" ≥ 40%
3. Có câu lưu ý khi tỷ trọng "0 năm" + "không ghi" < 40%
4. Có câu gợi ý theo vùng miền khi Hà Nội và TP.HCM chênh lệch

### Newcomer takeaways (US2)
5. Có câu nêu tên hai vai trò dẫn đầu khi ≥ 3 vai trò có shareShown
6. Có câu "đáng chú ý" khi vai trò tổng tin nhỏ nhưng entry share cao

### Skill-roles insight (US3)
7. Insight chứa "nền tảng" khi ≥ 60% vai trò có share > 0.2
8. Insight chứa "chuyên biệt" khi chỉ 1–2 vai trò có share > 0.2
9. Insight là null khi kỹ năng không được nhắc (mentioned = false)

## RED — Đợt 1 (2026-11-21)

Lệnh: `cd web && npx vitest run tests/fr338`

Kết quả: **10 fail, 2 pass** (3 file test, 12 test)

Fail đúng như kỳ vọng:
- 4 fail ở market-overview takeaways: chưa có câu hành động mới
- 3 fail ở newcomer takeaways: `buildNewcomerView` chưa trả field `takeaways`
- 3 fail ở skill-roles insight: `buildSkillRolesView` chưa trả field `insight`

2 pass do kiểm DEC-6 trên takeaways hiện tại (vốn đã không chứa số) và một test market overview
mà regex trùng với takeaway cũ.

## GREEN — Đợt 1 (2026-11-21)

Lệnh: `cd web && npx vitest run --pool vmThreads`

Kết quả: **385 pass, 0 fail** (33 file test)

Sửa:
- `web/lib/market-overview-view.ts`: mở rộng `takeaways()` thêm 3 câu hành động (gợi ý vai trò, kinh nghiệm, vùng miền)
- `web/lib/newcomer-roles-view.ts`: thêm field `takeaways` và hàm `newcomerTakeaways()` (2 câu: top vai trò + vai trò đáng chú ý)
- `web/lib/skill-roles-view.ts`: thêm field `insight` và hàm `skillInsight()` (nền tảng vs chuyên biệt)
- `web/app/components/insights/newcomer-screen.tsx`: hiển thị `takeaways` mới
- `web/app/components/insights/skill-roles-screen.tsx`: hiển thị `insight` mới

Ghi chú: vitest 5.0.5 có bug với pool mặc định (`forks`) + `afterEach` trong setup.ts; dùng `--pool vmThreads` để tránh.
