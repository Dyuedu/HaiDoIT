# TDD: Khóa hồ sơ trình duyệt và danh sách kỹ năng mồi

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Mỗi test một hành vi. Test Python không mạng, không database. Test web chạy trong jsdom, dùng `localStorage` thật của jsdom; trường hợp bộ nhớ bị chặn thì stub `Storage.prototype` cho ném lỗi.

Lệnh:

```text
uv run pytest tests/core/test_fr13_skill_seed.py tests/api -q
cd web && npx vitest run tests/ad23-haido-keys.test.ts
```

## Các hành vi

Python:

1. Mã kỹ năng khớp `^[a-z0-9]+(_[a-z0-9]+)*$`, tối đa 40 ký tự; `c++`, `ci/cd`, `Python`, `a__b`, `a,b` bị từ chối.
2. Danh sách mồi có 60–150 kỹ năng, mã không trùng và xếp theo thứ tự, `version` bắt đầu bằng `seed-`.
3. Mỗi kỹ năng có tên tiếng Anh, tên tiếng Việt và nguồn.
4. Không tên hay bí danh nào (sau chuẩn hóa) trỏ tới hai mã.
5. "học máy" và "Machine Learning" ra `machine_learning`; "C#" ra `csharp`; "ReactJS" ra `react`.
6. Không có tên vai trò như `tester`, `fullstack`, `data engineer`.
7. `GET /api/v1/skills` trả `{data: {vocab_version, skills}}` đúng thứ tự file mồi; mỗi dòng có đúng `code`, `name_en`, `name_vi`, `aliases`; không có số.
8. Test AD-17: mọi route `/api/v1` hoặc trả Envelope có số, hoặc nằm trong `NUMBERLESS_ROUTES` và không có số.

Web:

9. Đúng ba khóa `haido:eval`, `haido:profile`, `haido:session`.
10. Định dạng mã kỹ năng giống Python.
11. Chưa có gì thì ra hồ sơ rỗng; ghi rồi đọc ra đúng hồ sơ.
12. Bỏ mã sai, mã trùng, cắt ở 200.
13. JSON hỏng, sai `v`, sai kiểu ra hồ sơ rỗng.
14. Bỏ trường lạ; mã vai trò sai định dạng thành `null`.
15. `clearHaidoData` xóa mọi `haido:*`, kể cả khóa ngoài danh sách, giữ khóa của trang khác.
16. `Storage` ném lỗi thì module không ném ra ngoài.

## RED

- `uv run pytest tests/core/test_fr13_skill_seed.py tests/api -q` → 2 errors lúc thu thập (`ModuleNotFoundError: No module named 'haido_core.vocab.skills'`).
- `uv run pytest tests/api/test_ad17_routes.py -q` → 1 failed, 35 passed: `test_ad17_moi_route_tra_envelope` đỏ vì chưa có `/api/v1/skills`.
- `npx vitest run tests/ad23-haido-keys.test.ts` → 1 file failed: `Failed to resolve import "@/lib/haido-keys"`.

## GREEN

- `uv run pytest tests/core/test_fr13_skill_seed.py tests/api -q` → 51 passed, 22 skipped (skip là test Postgres sẵn có). Lần chạy đầu còn `test_ad17_openapi_da_commit_khop_voi_code` đỏ cho tới khi sinh lại `docs/api/openapi.json` bằng `HAIDO_UPDATE_OPENAPI=1`.
- `npx vitest run tests/ad23-haido-keys.test.ts` → 9 passed. Toàn bộ `npm test` → 115 passed.
- `uv run pytest -q` → 370 passed, 126 skipped.
- `uv run python tools/gates/check_gates.py` → AD-23 PASS, 8 pass, 2 skip, 0 fail.
- `npm run lint`, `npx tsc --noEmit`, `uv run ruff check .` sạch.
- Chạy `uvicorn` trên máy, `curl /api/v1/skills` trả `seed-2026-11-11` và 100 kỹ năng.

## Đợt 2 — 2026-11-11, sửa theo #163 (tham số `level` của city-shares)

Lý do: #163 thêm `level` và `data.level` cho `GET /api/v1/city-shares`, nên ảnh chụp `docs/api/openapi.json` và các stub trong `tests/api/test_ad17_routes.py` đổi. Hành vi của `/api/v1/skills` không đổi.

Lệnh: `uv run pytest tests/api -q`.

### RED

Sau khi thêm `data.level` và tham số `level`: `tests/api/test_ad17_routes.py` 7 failed (3 stub nguồn không nhận `level`, 3 test dựng `CitySharesData` thiếu `level`, 1 `test_ad17_openapi_da_commit_khop_voi_code` vì ảnh chụp cũ).

### GREEN

Sửa stub và dữ liệu thử, sinh lại ảnh chụp bằng `HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api -q`: `tests/api` xanh, mục `/api/v1/skills` trong `openapi.json` không đổi. Các đợt trước giữ nguyên.

## Đợt 3 — 2026-11-12, sau khi thêm lộ trình học (#212)

Lý do: #212 thêm phép `learning_path` vào `create_app`, đổi mã kỹ năng của `skill_rates` giả sang snake_case và (đợt 2 của #212) sửa nội dung `skill_rates`, `envelope.py`, schema OpenAPI.

- Không viết test mới của issue này và không có đợt RED: hành vi của issue không đổi. Bản ghi trước ghi một RED giả định ("sẽ báo...") không kèm số đếm; thay bằng ghi chú này.
- Đã chạy lại các test có sẵn của issue này trên mã sau đợt 2 của #212 (kết quả thật, 2026-11-12):
  - `uv run pytest -q tests/core/test_fr13_skill_seed.py tests/api/test_fr13_skills_route.py tests/api/test_ad17_routes.py` → 54 passed.
  - `npx vitest run tests/ad23-haido-keys.test.ts` → 9 passed.
- GREEN: `uv run pytest -q` (có Postgres) → 862 passed, không skip; hai lượt `-m determinism` (`PYTHONHASHSEED=0` và `1`) → 7 passed mỗi lượt; web `npm run test` → 164 passed.

## Đợt 2026-11-13 — #283 mở rộng từ vựng kỹ năng

Lý do: #283 dùng `skills_seed.json` làm từ vựng quét JD: giữ 100 mã cũ (hồ sơ đã lưu, link đã chia sẻ không hỏng), thêm 125
mã và bí danh tiếng Việt, thêm khóa `composites`, `scan_skip`; `skills.py` có thêm `load_vocabulary()`.

- RED: `test_fr13_danh_sach_moi_du_va_ma_hop_le` đỏ vì trần 150 mã (nay 225); sửa trần thành 400. Các test khác của #205
  (định dạng mã, tên song ngữ, bí danh không trỏ hai mã, "học máy" → `machine_learning`, không có tên vai trò) xanh.
- GREEN: `tests/core/test_fr13_skill_seed.py`, `tests/api/test_fr13_skills_route.py` xanh; `uv run pytest -q` → 887 passed.

## Đợt 2026-11-15 — gộp main vào #212

Lý do: `fake_market.json` `skill_rates` dùng lại `pandas`, `spark`, `airflow` (đều có trong `skills_seed.json` 225 mã của #283). Hành vi của #205 không đổi.

- RED: không có. Hành vi của issue không đổi; test chỉ thêm nguồn `learning_path` vào lời dựng `create_app` (nếu có) hoặc chạy lại trên fixture mới.
- GREEN (chạy lại thật, 2026-11-15): `uv run pytest -q tests/core/test_fr13_skill_seed.py tests/api/test_fr13_skills_route.py tests/api/test_ad17_routes.py` → 69 passed; `npx vitest run tests/fr37-newcomer-roles-fixture.test.ts tests/ad23-haido-keys.test.ts` → 14 passed; toàn bộ `uv run pytest -q` → 1113 passed.

## Đợt 2026-11-16 (#111): file dùng chung đổi, hành vi của issue này không đổi

Lý do: nhánh `gh-111-ho-so-ky-nang` sửa file mà issue này từng đụng: `haido_api/fixtures/fake_market.json` (thêm `skill_rates` cho mọi vai trò, #149), `haido_api/schemas/market.py`, `routes/market.py`, `market_source.py`, `fake_market.py`, `stat_market.py` (chữ ký `skill_rates` nhận `have`, #149), `haido_api/main.py` và `tests/api/test_ad17_routes.py` (route `role-for-title`, #150), `docs/api/*`. Các thay đổi chỉ chạm `skill-rates` và route mới; `city-shares`, `newcomer-roles`, `skills` và khóa trình duyệt không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi.
- GREEN: `uv run pytest -q` → 1018 passed, 217 skipped; `cd web && npx vitest run` → 21 files, 281 passed; `tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.

## Đợt 2026-11-17 (#166): file dùng chung đổi, hành vi của issue này không đổi

Lý do: #166 (hình response `skill-roles`) sửa file mà issue này từng đụng: `haido_core/vocab/skills.py` (thêm `find_seed_skill`, không đổi `SKILL_CODE_PATTERN`, `is_skill_code`, `load_seed_skills`), `haido_api/market_source.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `haido_api/fixtures/fake_market.json`. Thay đổi: định dạng mã kỹ năng và danh sách mồi không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #166 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `t166_test`) → 1510 passed, không skip; `cd web && npx vitest run` → 22 files, 293 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Đợt 2026-11-17 (#166, đợt 2 theo review): file dùng chung đổi lần nữa, AC của issue này không đổi

Lý do: #166 đợt 2 (cỡ mẫu `skill_count` của `skill_rate`, `mentioned` theo mọi cấp, `data.level`, prod chọn nguồn `stat`) sửa thêm `haido_api/fake_market.py`, `fixtures/fake_market.json`, `routes/market.py`. Không đổi hành vi nào của khóa hồ sơ trình duyệt.

- RED: không có, vì không có hành vi nào của issue này đổi. RED của #166 đợt 2 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx166_test`, không skip) → 1538 passed; `cd web && npx vitest run` → 22 files, 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Đợt 2026-11-17 (#151, #106, #103): file dùng chung đổi, AC của issue này không đổi

Lý do: tỷ lệ kỹ năng thật (#151), phép 2 `select_cell` (#106) và ràng buộc lớp đọc (#103) sửa file mà issue này từng đụng:

  - `docs/api/envelope-meta.md` (mô tả bản thật của `skill-rates`);

Hành vi và AC của issue này không đổi: thay đổi chỉ thêm (phương thức `skill_rates` thật, trường `order` có mặc định, một biến môi trường ở prod, một đoạn tài liệu); `city_shares`, `newcomer_roles`, `learning_path`, `skill_roles` của `StatMarket` giữ nguyên. Chi tiết: `specs/151-ty-le-ky-nang-that/plan.md`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #151, #106, #103 nằm ở `specs/151-ty-le-ky-nang-that/tdd.md`, `specs/106-chon-o-quay-ve/tdd.md`, `specs/103-api-doc-ty-le-that/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed; `cd web && npx vitest run` → 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

Cập nhật sau review (đợt 2, 2026-11-17): trong `StatMarket` chỉ `skill_rates` đổi thêm (404 khi ô không có hàng tỷ lệ, `n_scanned` nhất quán, chữ nhãn); hành vi và AC của issue này vẫn không đổi. RED và GREEN: `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`, `docs/api/openapi.json`, `haido_api/fixtures/fake_market.json`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.

## Đợt #278 (2026-11-23): danh sách mồi lớn lên 265 mã, AC của issue này không đổi

Lý do: #278 thêm 40 mã vào `haido_core/vocab/skills_seed.json` (225 → 265, `version` `seed-2026-11-23`) và thêm bộ nạp danh sách loại trừ vào `haido_core/vocab/skills.py`, hai file mà issue này từng đụng. 225 mã cũ còn nguyên; định dạng mã, tên song ngữ, "học máy" → `machine_learning`, "C#" → `csharp`, "ReactJS" → `react` không đổi.

Một test đổi: `tests/core/test_fr13_skill_seed.py::test_fr13_khong_co_ten_vai_tro_trong_danh_sach` không còn cấm `it support` làm bí danh. Quy tắc thật (đợt review 2026-11-23): `it support` là bí danh **chỉ để tra thẻ** của `helpdesk` (thẻ "IT Support", 41 tin) và nằm trong `scan_skip`, nên không bao giờ khớp tên vai trò trong văn bản JD. Các tên `tester`, `fullstack`, `data engineer`, `công nghệ thông tin` vẫn bị cấm hoàn toàn; test mới `test_fr13_ten_vai_tro_duoc_giu_lam_bi_danh_phai_nam_trong_scan_skip` đòi mọi tên vai trò còn là bí danh phải nằm trong `scan_skip`. (Bản đầu của đợt này và comment trong test nói người dùng đã duyệt việc bỏ `it support` khỏi danh sách cấm; điều đó không đúng.)

RED, GREEN và đột biến: `specs/278-ma-ky-nang-thuong-gap/tdd.md`.
