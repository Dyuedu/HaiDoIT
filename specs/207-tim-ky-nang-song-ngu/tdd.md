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

## Đợt 2 (2026-11-17, #151): ô đủ mẫu mà mọi kỹ năng hiếm

Lý do: API thật trả `rows = []`, `core_size = 0`, `have_core = 0` khi ô đủ mẫu mà mọi kỹ năng dưới θ_common; `isSkillRatesEnvelope` từng coi `rows` rỗng là hỏng. Sửa `web/lib/skill-rates.ts` (rỗng hợp lệ chỉ khi `core_size === 0`), `web/lib/skill-profile-view.ts` (`emptyText`, không dòng đếm "0/0"), `web/app/components/skill-profile/skill-profile-screen.tsx` (câu thay danh sách). Các AC đang có của issue này không đổi; thêm một trường hợp biên.

- RED: `npx vitest run tests/fr19-skill-profile.test.tsx` → 2 failed, 23 passed (rỗng với `core_size = 0` bị từ chối; màn hiện lỗi thay câu giải thích). Chi tiết ở `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.
- GREEN (chạy thật): `npx vitest run` → 22 files, 302 passed; `npx tsc --noEmit`, `npm run lint` sạch.

## Đợt #324 (2026-11-19): câu chữ trên màn viết lại

Lý do: #324 viết lại chữ hiển thị bằng tiếng Việt dễ hiểu (bỏ nhãn `n = `, "snapshot", "entry-level"; câu thiếu mẫu "Mới có X tin, cần ít nhất 30"; khung nguồn "Đang xem", "Cập nhật", tên nguồn). File của issue này bị đụng: `web/lib/skill-profile-view.ts`, `web/lib/newcomer-roles-view.ts`. Số, thứ tự và ẩn số theo ngưỡng không đổi. Hành vi và AC của issue này không đổi.

- RED và GREEN: `specs/324-cau-chu-de-hieu/tdd.md` (RED 42 failed / 299 passed; GREEN 357 passed, chạy `npx vitest run` từ PowerShell).
