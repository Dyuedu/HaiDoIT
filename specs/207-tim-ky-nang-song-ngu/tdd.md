# TDD: Tìm kỹ năng bằng tiếng Anh và tiếng Việt

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test dùng `web/tests/fixtures/skills.json` (response của API giả, khóa bằng `tests/api/test_ad17_web_fixtures.py`).

Lệnh:

```text
cd web && npx vitest run tests/fr13-tim-ky-nang-song-ngu.test.tsx
```

## Các hành vi

1. `foldText("Học  Máy")` → `"hoc may"`; `foldText("Đà Nẵng")` → `"da nang"`.
2. "học máy", "hoc may", "HỌC MÁY", "machine" → có `machine_learning`.
3. "ml" → có `machine_learning`; "reactjs" → có `react`.
4. Chuỗi rỗng hay toàn khoảng trắng → không kết quả.
5. Tối đa 8 kết quả; khớp đầu tên trước khớp giữa tên.
6. Màn: gõ "học máy", tick Machine Learning → ô tick; hồ sơ lưu có `machine_learning`.
7. Màn: gõ "zzzz" → "Không có kỹ năng nào khớp" trong `role="status"`.

## RED web (2026-11-16)

Lệnh chạy cả sáu file test mới của màn (từ ổ `D:\` viết hoa: chạy từ `/d/...` của Git Bash làm Vitest nạp hai bản `vitest` và mọi file, kể cả test cũ, báo "failed to find the current suite"; đó không phải RED):

```text
cd web && npx vitest run tests/fr19-skill-profile.test.tsx tests/fr18-role-for-title.test.tsx tests/fr22-mo-lo-trinh-tu-ky-nang.test.tsx tests/fr14-luu-tick-trinh-duyet.test.tsx tests/fr13-tim-ky-nang-song-ngu.test.tsx tests/fr18-fr19-us-a2-ac.test.tsx
```

- `fr19-skill-profile`, `fr18-role-for-title`, `fr22-mo-lo-trinh-tu-ky-nang`, `fr13-tim-ky-nang-song-ngu`: không nạp được, `Failed to resolve import` `@/lib/skill-rates`, `@/lib/role-for-title`, `@/lib/skill-profile-view`, `@/lib/vocab` (chưa có).
- `fr14-luu-tick-trinh-duyet`: 6/6 failed, `Unable to find role="list" and name /Kỹ năng theo tỷ lệ tin yêu cầu/` (trang vẫn là trang giữ chỗ của #147).
- `fr18-fr19-us-a2-ac`: 7/8 failed cùng lý do; test khóa tên xanh sẵn.

## GREEN web (2026-11-16)

- Lượt đầu sau khi viết màn: 58 passed, 2 failed (`fr13`): ô tìm kỹ năng bị `disabled` tới khi danh sách kỹ năng về, chữ gõ sớm bị mất. Đây là lỗi thật của màn: bỏ `disabled`, kết quả hiện khi danh sách về. Không sửa test.
- `npm run lint` chặn `setState` đồng bộ trong effect khi đọc hồ sơ. Đổi sang `useSyncExternalStore` với `web/lib/profile-store.ts` (server và lần hydrate đầu dùng hồ sơ rỗng).
- Cổng AD-23 chặn `localStorage.getItem/setItem` trong file test; test gieo và đọc hồ sơ bằng `writeProfile`/`readProfile` của `haido-keys.ts`.
- `npx vitest run` → 21 files, 281 passed; `npx tsc --noEmit`, `npm run lint` sạch; `npm run build` xong (`/ho-so-ky-nang`, `/co-van` động).
- `uv run pytest -q` → 1018 passed, 217 skipped; `tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.
- Chrome headless trên `next start` với API local (nguồn giả), `/ho-so-ky-nang?role=backend&level=entry`:
  - 360×640: không cuộn ngang (360/360), 15 dòng, không ô bấm nào thấp hơn 44px.
  - 1280×900: không cuộn ngang, không ô bấm nào thấp hơn 44px.
  - Tick Java rồi tải lại: Java vẫn tick, dòng đếm "1/6 kỹ năng cốt lõi bạn đã có" (số của API).
  - Chạm Spring Boot: `/co-van?role=backend&level=entry&skill=spring_boot`, tiêu đề "Lộ trình học: Backend".
  - Chức danh "Lập trình viên Java" qua phép 6 thật: "Hải Đồ dùng vai trò Backend cho chức danh này.", URL `?role=backend&level=entry`.
