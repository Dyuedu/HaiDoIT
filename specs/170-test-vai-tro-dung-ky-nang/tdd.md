# TDD: Test "vai trò nào dùng kỹ năng" theo AC của #113

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Chạy từ ổ `D:\` viết hoa.

Lệnh:

```text
cd web && npx vitest run tests/fr09-fr13-us-a4-ac.test.tsx
```

## Các hành vi

Năm AC của #113, theo bảng trong `spec.md`, cộng test khóa tên.

## RED (2026-11-17)

```text
cd web && npx vitest run tests/fr09-vai-tro-dung-ky-nang.test.tsx tests/fr13-chon-mot-ky-nang.test.tsx tests/fr09-fr13-us-a4-ac.test.tsx
```

- 25 failed, 1 passed: `fr09-vai-tro-dung-ky-nang` 10/10, `fr13-chon-mot-ky-nang` 10/10, `fr09-fr13-us-a4-ac` 5/6. Mọi test đỏ cùng lý do `Unable to find role="region" and name "Kỹ năng của bạn dùng ở vai trò nào"`: `/insights` chưa có mục này. Test khóa tên xanh sẵn.

## GREEN (2026-11-17)

- Ba file test mới: 26 passed ngay lượt đầu sau khi viết màn.
- `npx vitest run` toàn bộ: 2 test cũ của `fr37-newcomer-list.test.tsx` đỏ vì mục mới thêm một lần gọi `/api/v1/skills` và một vùng `role="status"` trên cùng trang; thu phạm vi hai test về mục người mới (xem `specs/147-man-nguoi-moi/tdd.md`). Sau đó 25 files, 328 passed.
- `npx tsc --noEmit`, `npm run lint` sạch. `npm run build` xong (`/insights` vẫn tĩnh). Next 16.4.4 in cảnh báo GHSA-mfr8-8qww-v76h (moderate, `'use cache'` qua `unstable_cache`, sửa ở 16.4.6) và lần đầu dừng để nhắc nâng cấp; web không dùng hai API đó. Nâng cấp để việc riêng.
- `tools/gates/check_gates.py` → 10 pass, 0 fail; `uv run ruff check .` sạch; `uv run pytest tests/api -q` → 463 passed, 98 skipped.
- Chrome headless trên `next start` với API local (nguồn giả), `/insights?skill=python`:
  - 360×640: không cuộn ngang (360/360), 17 dòng, không ô bấm nào trong mục thấp hơn 44px; 1280×900: như vậy.
  - Dòng đầu "AI/ML · 77,6% tin AI/ML mới vào nghề nhắc tới Python · n = 501", liên kết `/ho-so-ky-nang?role=ai_ml&level=entry`.
  - Gõ "học máy", chọn Học máy: URL `?skill=machine_learning`, dòng đầu "65,9% tin AI/ML mới vào nghề nhắc tới Học máy".
  - `?skill=abap`: "Kỹ năng: ABAP", "Chưa tin tuyển dụng hiện tại nào nhắc tới ABAP.", không dòng nào.
- Production (`haidoit.io.vn`) còn trả 404 `unknown_cell` cho `skill-roles` tới khi #168 có số thật; màn hiện thông báo đó.

## Đợt #168 (2026-11-19): câu chữ AC 3 của #113 đổi, hành vi không đổi

Lý do: AC 3 của #113 nay ghi "fewer than 30 entry-level postings that could be read for skills". Màn lấy X bằng `rowN` (`skill_count`, thiếu thì `n`); test AC3 của issue này dùng `data_engineer` có `n` bằng `skill_count` nên không phân biệt hai số, còn chỗ phân biệt (`vn.game.entry`, 43 và 12) đã có ở `web/tests/fr09-skill-roles-fixture.test.ts` (#166). Không sửa test. Nguồn `stat` thật của `skill-roles`: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #324 (2026-11-19): câu chữ trên màn viết lại

Lý do: #324 viết lại chữ hiển thị bằng tiếng Việt dễ hiểu (bỏ nhãn `n = `, "snapshot", "entry-level"; câu thiếu mẫu "Mới có X tin, cần ít nhất 30"; khung nguồn "Đang xem", "Cập nhật", tên nguồn). File của issue này bị đụng: `web/lib/skill-roles-view.ts`, `web/app/components/insights/skill-roles-list.tsx`. Số, thứ tự và ẩn số theo ngưỡng không đổi. Câu trong scenario của `spec.md` đã sửa theo câu mới; ý của AC giữ nguyên (người dùng đồng ý 2026-11-19).

- RED và GREEN: `specs/324-cau-chu-de-hieu/tdd.md` (RED 42 failed / 299 passed; GREEN 357 passed, chạy `npx vitest run` từ PowerShell).

## Đợt #329 (2026-11-19): /insights thêm toàn cảnh ở đầu trang, AC của issue này không đổi

Lý do: #329 thêm mục toàn cảnh thị trường lên đầu `/insights` (`web/app/insights/page.tsx`). Mock `fetch` trong test của mục này (`web/tests/fr37-newcomer-list.test.tsx`, `web/tests/helpers/skill-roles.ts`) trả "đang tải" mãi cho `/api/v1/market-overview`, để test vẫn chỉ kiểm mục của issue này. Hành vi và AC không đổi.

- RED và GREEN: `specs/329-man-tong-quan/tdd.md` (`npx vitest run` → 366 passed).
