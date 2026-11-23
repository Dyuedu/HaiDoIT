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

## Đợt 2026-11-17 (#151, #106, #103): file dùng chung đổi, AC của issue này không đổi

Lý do: tỷ lệ kỹ năng thật (#151), phép 2 `select_cell` (#106) và ràng buộc lớp đọc (#103) sửa file mà issue này từng đụng:

  - `docs/api/envelope-meta.md` (mô tả bản thật của `skill-rates`);

Hành vi và AC của issue này không đổi: thay đổi chỉ thêm (phương thức `skill_rates` thật, trường `order` có mặc định, một biến môi trường ở prod, một đoạn tài liệu); `city_shares`, `newcomer_roles`, `learning_path`, `skill_roles` của `StatMarket` giữ nguyên. Chi tiết: `specs/151-ty-le-ky-nang-that/plan.md`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #151, #106, #103 nằm ở `specs/151-ty-le-ky-nang-that/tdd.md`, `specs/106-chon-o-quay-ve/tdd.md`, `specs/103-api-doc-ty-le-that/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed; `cd web && npx vitest run` → 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

Cập nhật sau review (đợt 2, 2026-11-17): trong `StatMarket` chỉ `skill_rates` đổi thêm (404 khi ô không có hàng tỷ lệ, `n_scanned` nhất quán, chữ nhãn); hành vi và AC của issue này vẫn không đổi. RED và GREEN: `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`, `haido_api/stat_market.py`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`, `docs/api/openapi.json`, `haido_api/fixtures/fake_market.json`, `haido_api/stat_market.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.

## Đợt #278 (2026-11-23): fixture `skills.json` sinh lại, AC của issue này không đổi

Lý do: commit `fecab28` (#149, #150) tạo `web/tests/fixtures/skills.json`; #278 sinh lại file này từ response `GET /api/v1/skills` vì từ vựng lớn lên 265 mã, `vocab_version` `seed-2026-11-23`. Hình dạng không đổi, hành vi `role-for-title` của issue này không đổi.

- RED: `tests/api/test_ad17_web_fixtures.py::test_ad17_fixture_web_khop_response_skills` đỏ khi từ vựng đã đổi mà fixture chưa sinh lại (chạy thật ở đợt đầu của #278).
- GREEN: sau khi sinh lại, test xanh; `cd web && npx vitest run` xanh. Số liệu đầy đủ: `specs/278-ma-ky-nang-thuong-gap/tdd.md`.
