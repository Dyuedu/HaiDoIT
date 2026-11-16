# TDD: Chức danh gõ vào thành một vai trò

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh:

```text
uv run pytest tests/api/test_fr18_role_for_title.py -q
cd web && npx vitest run tests/fr18-role-for-title.test.tsx
```

## Các hành vi

1. "Java Backend Developer", "Lập trình viên Java" → `matched`, `backend`; "Tester" → `qa`; "Machine learning engineer" → `ai_ml`.
2. "Kế toán", "Nhân viên bán hàng" → `not_it`, `role = null`.
3. "Developer", "Kỹ sư phần mềm" → `generic`, `role = null`.
4. Chức danh rỗng, toàn khoảng trắng, 121 ký tự, thiếu tham số → 422 `invalid_query`.
5. Response không có số; route nằm trong `NUMBERLESS_ROUTES`.
6. Màn: gõ chức danh khớp → ghi "Backend", ô Vai trò là Backend, tải `skill-rates?role=backend`.
7. Màn: đổi ô Vai trò → tải số của vai trò mới.
8. Màn: `not_it`/`generic` → câu báo không khớp, danh sách vai trò bấm được, không chữ số nào trong vùng kết quả.
9. Màn: ô trống thì bấm tìm không gọi API.

## RED API (2026-11-16)

`uv run pytest tests/api/test_fr18_role_for_title.py -q` → 15 failed: mọi test nhận 404 `not_found` ("Không có đường dẫn này"), vì route `/api/v1/role-for-title` chưa có.

## GREEN API (2026-11-16)

- Thêm `haido_api/schemas/roles.py`, `haido_api/routes/roles.py`, `include_router` trong `haido_api/main.py`.
- `test_ad17_moi_route_tra_envelope` gọi route không số mà không có tham số; thêm `NUMBERLESS_SAMPLE` (truy vấn mẫu của từng route không số) trong `tests/api/test_ad17_routes.py`. Test Ordinal quét thêm `roles.router`.
- `uv run pytest tests/api/test_fr18_role_for_title.py -q` → 15 passed; `uv run pytest tests/api -q` → 379 passed, 74 skipped; `tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.

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

## Đợt 2026-11-16 (CI của PR #304): thứ tự import

Lý do: job `Python - ruff and pytest` đỏ ở `ruff check` (I001, thứ tự import của `haido_api/routes/roles.py`); lượt kiểm ở máy trước đó không chạy ruff. Không đổi hành vi.

- RED: `uv run ruff check .` → 1 error (I001, `haido_api/routes/roles.py`).
- GREEN: `uv run ruff check --fix` rồi `uv run ruff check .` → All checks passed; `uv run pytest tests/api -q` → 385 passed, 74 skipped; `tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.

## Đợt 2026-11-17 (#166): file dùng chung đổi, hành vi của issue này không đổi

Lý do: #166 (hình response `skill-roles`) sửa file mà issue này từng đụng: `haido_api/fake_market.py`, `market_source.py`, `routes/market.py`, `schemas/market.py`, `fixtures/fake_market.json`, `docs/api/*`, `tests/api/test_ad17_routes.py`. Thay đổi: thêm phép `skill_roles`; `role-for-title` không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #166 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `t166_test`) → 1510 passed, không skip; `cd web && npx vitest run` → 22 files, 293 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.
