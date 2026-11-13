# TDD: Màn người mới và lối sang hồ sơ kỹ năng

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test web thay `fetch` bằng fixture `web/tests/fixtures/newcomer-roles.json` (response của API giả, #144), không gọi mạng.

Lệnh:

```text
cd web && npx vitest run tests/fr37-newcomer-list.test.tsx
```

## Các hành vi

1. Mỗi vai trò một dòng, nhãn tiếng Việt, đúng thứ tự API.
2. API gửi thứ tự đảo thì web hiện đúng thứ tự đảo (không sắp xếp lại).
3. Dòng đủ mẫu: "501 tin cho người mới", "57,1%", "n = 877".
4. Dòng dưới ngưỡng: "chưa đủ dữ liệu (12/30)", không có "%".
5. Dòng 0 tin entry-level (`devops`) và không có tin nào (`other`) vẫn ở lại, ghi "0 tin cho người mới".
6. Ngưỡng trong ghi chú lấy từ `meta.thresholds.min_sample` ("12/50").
7. Liên kết của dòng là `/ho-so-ky-nang?role=ai_ml&level=entry`, tên liên kết bắt đầu bằng tên vai trò.
8. Khung "Nguồn và lưu ý" có ngày, nguồn, mọi lưu ý.
9. `unknown_cell`: thông báo, ngày, không "Thử lại", không danh sách.
10. Mạng hỏng: "Không đọc được số liệu", "Thử lại" tải lại được.
11. Tám kiểu envelope sai hợp đồng → `unreadable`; envelope đúng → `ok`.
12. Trang giữ chỗ: tiêu đề có tên vai trò, cấp "Mới vào nghề", "sprint sau", nút quay lại `/insights`.
13. Mã vai trò lạ: không in mã, ghi "Không có vai trò này".
14. Câu giới thiệu và câu trang giữ chỗ không có chữ số (DEC-6).

## RED (2026-11-12)

`npx vitest run tests/fr37-newcomer-list.test.tsx` → 1 file failed, không test nào chạy: `Failed to resolve import "@/app/ho-so-ky-nang/page"` (trang giữ chỗ chưa có; `fetchNewcomerRoles` cũng chưa có). Trước đó một lượt hỏng vì test dùng matcher của `jest-dom` mà repo không cài; đã đổi sang assertion thuần của Vitest như các test web khác, đó không phải RED của hành vi.

## GREEN (2026-11-12)

- Lượt đầu sau khi viết code: 20 passed, 2 failed. Hai test hỏng do chính test (`.textContent` gắn vào promise của `findByRole` khi đổi matcher); sửa test, không sửa code. Test `unknown_cell` thêm ngày snapshot vào body lỗi để kiểm đúng điều tên test nói.
- `npx vitest run tests/fr37-newcomer-list.test.tsx` → 22 passed.
- `npx vitest run` → 13 files, 189 passed.
- `npx tsc --noEmit`, `npm run lint` sạch; `npm run build` xong, `/insights` tĩnh, `/ho-so-ky-nang` động.
- `tools/gates/check_gates.py` → 8 pass (có FR-25/31/47 từ ngữ cấm), 2 skip, 0 fail.
- Chrome headless trên `next start` với API local (nguồn giả):
  - 360px: 17 dòng, không cuộn ngang (360/360), dòng thấp nhất 96px.
  - 1280px: không cuộn ngang, dòng thấp nhất 49px.
  - Bấm dòng đầu: `/ho-so-ky-nang?role=ai_ml&level=entry`, tiêu đề "Hồ sơ kỹ năng: AI/ML".
