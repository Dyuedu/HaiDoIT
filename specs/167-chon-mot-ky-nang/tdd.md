# TDD: Chọn một kỹ năng bằng tiếng Anh hoặc tiếng Việt

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Chạy từ ổ `D:\` viết hoa.

Lệnh:

```text
cd web && npx vitest run tests/fr13-chon-mot-ky-nang.test.tsx
```

## Các hành vi

1. Gõ "học máy" → nút "Học máy (Machine Learning)"; chọn → gọi `skill=machine_learning`, ghi "Kỹ năng: Học máy (Machine Learning)", URL `?skill=machine_learning`, `aria-pressed = true`.
2. Hồ sơ có `python` → nút chọn nhanh Python.
3. Mở `?skill=python` → Python đã chọn, danh sách hiện; `?skill=Khong-Hop-Le` → chưa chọn, không gọi API.
4. Gõ "zzzz" → "Không có kỹ năng nào khớp".
5. ABAP (`mentioned = false`) → "Chưa tin tuyển dụng hiện tại nào nhắc tới ABAP.", không danh sách, không "0%".
6. SAP (`mentioned = true`, mọi dòng 0) → danh sách, không câu "chưa tin nào nhắc".
7. `unknown_skill` → thông báo của API, không "Thử lại".

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
