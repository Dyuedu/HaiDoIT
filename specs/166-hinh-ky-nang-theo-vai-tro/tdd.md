# TDD: Hình response của một kỹ năng qua các vai trò và dữ liệu giả

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Ghi trung thực về thứ tự làm việc: ở đợt 1, thư mục `specs/166-.../` được viết SAU khi code và test đã xong (CLAUDE.md yêu cầu viết trước code). Mã và test của đợt 1 vẫn theo TDD (test viết trước, chạy đỏ, rồi mới code), nhưng spec, plan, tasks, research và data-model là hồi tố. Đợt 2 (bên dưới) sửa spec cùng lúc với test, trước khi sửa code.

Mỗi test một hành vi. Test Python không mạng, chạy API qua `TestClient` với nguồn giả (riêng test nguồn `stat` chỉ kiểm lời từ chối, không mở database). Test web đọc fixture JSON, không gọi API.

Lệnh:

```text
uv run pytest tests/api tests/steps/test_gh284_aggregate_vai_tro_moi.py -q
cd web && npx vitest run tests/fr09-skill-roles-fixture.test.ts
```

## Các hành vi

Python (`tests/api/test_fr09_skill_roles.py`, mã FR-9 và AD-17):

1. `SkillRoleRow` từ chối `share` sai loại, `cell_id` không phải `vn.<role>.entry`; `skill_rate` dưới ngưỡng không được `low_sample_shown`.
2. `SkillRolesData` từ chối vai trò lặp, `rows` rỗng, `levels` rỗng.
3. `SkillRolesData` từ chối thứ tự sai: tỷ lệ tăng dần, hòa không theo mã, `null_data` đứng trước dòng có tỷ lệ.
4. `mentioned = false` mà có dòng hiện tỷ lệ dương là lỗi; `mentioned = false` với dòng 0 và `null_data` hợp lệ; `mentioned = true` với mọi dòng hiện bằng 0 hợp lệ.
5. Route trả `{data, meta}`, đủ trường, `skill` là mã và tên trong bộ từ vựng, `levels` lấy từ config, `display` khớp `suppression_for` trên n của ô, `meta.cells` đúng các ô entry của dòng.
6. Dữ liệu giả: đủ 17 vai trò, số nhắc không vượt n, mã kỹ năng thuộc bộ từ vựng, `share.value` = số nhắc / n.
7. `python`: có dòng dương, từ hai dòng `null_data` trở lên, một dòng đủ mẫu bằng 0. `figma`: thứ hạng khác `python`, vai trò cao nhất thật (`ui_ux`) bị ẩn. `abap`: `mentioned = false`.
8. `mentioned` tính cả ô bị ẩn.
9. Thứ tự theo máy chủ cho cả ba kỹ năng; hòa theo mã; `null_data` theo n giảm dần rồi mã.
10. 404 `unknown_skill` (không lặp lại mã đã gửi), 404 `unknown_cell` với `java` có ngày snapshot, 422 cho sáu kiểu `skill` sai.
11. DEC-6: mọi chuỗi của `data` ngoài `skill.*` không có chữ số; fixture chỉ có số nguyên.
12. Biến `HAIDO_MARKET_SOURCE_SKILL_ROLES`, thiếu nguồn là lỗi khởi động, `StatMarket` trả 404 `unknown_cell` không có ngày, compose chưa đặt `stat`, nguồn trả sai hợp đồng thành 500, ngưỡng đọc từ fixture.
13. `test_ad17_routes.py`: route có trong `SAMPLE_QUERY` và trong danh sách truy vấn kiểm `display`; `docs/api/openapi.json` khớp code.
14. `test_ad17_web_fixtures.py`: ba fixture web giống hệt response của API giả.

Web (`web/tests/fr09-skill-roles-fixture.test.ts`):

15. Mọi dòng có ô `vn.<role>.entry` trong `meta.cells`, `share` là `skill_rate`.
16. `rowN` tra đúng n (501 cho `ai_ml`), ném lỗi khi thiếu ô.
17. Dòng dưới ngưỡng: `value = null` mà vẫn có n; dòng đủ mẫu bằng 0 hiện 0.
18. `mentioned` đúng ở ba fixture; nhãn `python` đủ mã và tên.
19. `skillRolesUrl`, `fetchSkillRoles`: ok, lỗi `unknown_skill` và `unknown_cell` không thử lại, lỗi khác thử lại, body sai hợp đồng và mạng hỏng là `unreadable`.

## RED

Chạy 2026-11-17, sau khi viết test, trước khi viết code:

- `uv run pytest tests/api tests/steps/test_gh284_aggregate_vai_tro_moi.py -q --continue-on-collection-errors` → 3 failed, 371 passed, 2 errors lúc thu thập:
  - `tests/api/test_ad17_routes.py`: `KeyError: 'skill_roles'` (fixture chưa có mục `skill_roles`);
  - `tests/api/test_fr09_skill_roles.py`: `ImportError: cannot import name 'SkillRoleRow'`;
  - 3 failed là `test_ad17_fixture_web_khop_response_skill_roles[python|figma|abap]` (chưa có file fixture web).
- `cd web && npx vitest run tests/fr09-skill-roles-fixture.test.ts` → 1 file failed: `Failed to resolve import "./fixtures/skill-roles-abap.json"`.

Test của 52 hành vi trong `test_fr09_skill_roles.py` chưa chạy được ở bước này vì lỗi thu thập; chúng chạy đỏ lần đầu ở GREEN phía dưới.

## GREEN

- Sau khi viết code, `uv run pytest tests/api/test_fr09_skill_roles.py -q` → 52 passed. Lần đầu có một test đỏ do so sánh `list` với `tuple` của `level_groups`; sửa test (`list(...)`), không sửa code.
- Sinh lại `docs/api/openapi.json` bằng `HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api -q`; sinh ba fixture web bằng `TestClient(app)` (`json.dumps(..., ensure_ascii=False, indent=2)` cộng dòng trống cuối).
- `uv run pytest tests/api -q` → 517 passed.
- `cd web && npx vitest run tests/fr09-skill-roles-fixture.test.ts` → 12 passed.
- Toàn bộ, Postgres thật (`HAIDO_TEST_DATABASE_URL`, DB `t166_test`, không skip): `uv run pytest -q` → 1510 passed; `uv run ruff check .` sạch; `cd web && npx vitest run` → 22 files, 293 passed; `npx tsc --noEmit` và `npm run lint` sạch.
- `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Kiểm đột biến

Mỗi lần sửa một dòng của code rồi chạy `tests/api/test_fr09_skill_roles.py`, `test_ad17_web_fixtures.py`, `test_ad17_routes.py`, `tests/domain`; trả code về sau mỗi lần. Lần thử đầu của lượt này khôi phục sai (bản sao lưu trỏ nhầm vào một thư mục) nên các đột biến chồng lên nhau; đã hoàn nguyên bằng tay, chạy lại `uv run pytest tests/api -q` → 517 passed, rồi làm lại từng đột biến riêng lẻ bên dưới.

| Đột biến | Kết quả |
|---|---|
| Bỏ khóa tỷ lệ giảm dần ở `FakeMarket.skill_roles` (`-(value)` thành `0.0`) | 14 failed (thứ tự theo máy chủ, schema từ chối thứ tự, fixture web, `display`) |
| `suppression_for`: `n >= min_sample` thành `n > min_sample` | 12 failed (ca `mobile` n = 30 đủ mẫu bằng 0, share = nhắc / n, fixture web) |
| `mentioned` tính từ các dòng hiện thay vì mọi ô | 1 failed (`test_fr09_mentioned_tinh_ca_o_bi_an`) |
| Route bỏ kiểm bộ từ vựng | 1 failed (`...404_unknown_skill`) |
| Schema bỏ luật `mentioned = false` kèm tỷ lệ dương | 2 failed |
| Schema bỏ luật thứ tự dòng có tỷ lệ | 2 failed (`tang_dan`, `hoa_sai_ma`) |
| Bỏ khóa n giảm dần của dòng `null_data` | 7 failed (thứ tự ở ba kỹ năng, fixture web) |
| Bỏ khóa cuối `r.role` của phép sắp xếp (hòa không theo mã) | 15 failed (thứ tự, fixture web, `display`) |

Luật hòa theo mã của dòng `null_data` được `test_fr09_thu_tu_hoa_theo_ma_vai_tro_va_null_data_theo_n_giam_dan` kiểm với hai dòng cùng n = 0 (`devops`, `other`).

---

## Đợt 2 — 2026-11-17: sửa theo review

Lý do: review của người điều phối chốt chín việc (xem "Quyết định" đợt 2 trong `spec.md`): cỡ mẫu của phép đo (`n_by_measure.skill_count`, `n` của ô giữ nguyên), `mentioned` theo mọi cấp, `data.level`, compose prod chọn `stat`, phủ bản giả (`machine_learning`, `sap`, ô `game` quét ít), bộ chốt chống lệch và thứ tự dòng `null_data`, `invalid_query` không thử lại ở web, DEC-6 và mã FR. Spec, plan, tasks, data-model, research và `envelope-meta.md` được cập nhật cùng lúc với test, trước khi sửa code.

Lệnh:

```text
uv run pytest tests/api tests/domain/test_ad17_envelope.py tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py -q
cd web && npx vitest run tests/fr09-skill-roles-fixture.test.ts
```

DB của lượt chạy này: `fx166_test` trên container Postgres local (cổng 5433), tạo riêng cho đợt 2 và xóa cuối đợt. Đợt 1 dùng DB `t166_test`. RED dưới đây chỉ chạy các thư mục nói trên (các test không cần DB chạy ở đó vì có `HAIDO_TEST_DATABASE_URL`; không test nào bị skip).

Hành vi mới hoặc đổi (đánh số tiếp danh sách trên):

20. `Envelope`: `display` của `skill_rate` khớp `suppression_for` trên `n_by_measure.skill_count` (n của ô 43, `skill_count` 12 thì phải ẩn; thiếu khóa thì dùng `n`); `level_share` và `composition_share` vẫn theo `n` của ô dù `skill_count` nhỏ (`tests/domain/test_ad17_envelope.py`).
21. `data` có `check_against_meta` được `Envelope` gọi; lỗi vào thông báo hợp đồng; `data` không có hook không đổi.
22. `data.level` bắt buộc và phải là `entry`; `entry` có trong `level_options` của config và `LEVEL_OPTIONS` của web (#111 nhận được).
23. `mentioned = false` với dòng pha trộn 0 và dương là lỗi (giết đột biến `any` thành `all`).
24. Route: `meta.cells[vn.game.entry]` có `n` 43 và `skill_count` 12; dòng `game` là `null_data`; `n` của ô khớp `newcomer-roles`; Envelope từ chối `shown` khi `skill_count` dưới ngưỡng.
25. Dòng `null_data` theo cỡ mẫu của phép đo giảm dần rồi mã (`ui_ux` 21 trước `game` 12, dù `n` của ô `game` là 43); `Envelope` từ chối đảo hai dòng `null_data`, kể cả hai dòng hòa cỡ mẫu.
26. Fixture: mỗi kỹ năng có đúng các vai trò của config và ô entry cho từng vai trò; số nhắc không vượt `skill_count`; `mentions_all_levels` không nhỏ hơn tổng entry-level.
27. `mentioned` theo AC 4 của #113: `sap` (không tin entry-level nào, có tin ở cấp khác) cho `true`; đổi `mentions_all_levels` đổi `mentioned`.
28. Nhãn song ngữ khác nhau: `machine_learning` = Machine Learning / Học máy.
29. Bộ nạp giả báo `ValueError` nêu kỹ năng và vai trò lệch, hoặc ô entry thiếu, thay cho `KeyError`.
30. DEC-6: mọi chuỗi của `data` ngoài `skill.name_en` và `skill.name_vi` không có chữ số, kể cả `skill.code`.
31. `test_ad17_routes.py`: oracle của `display` dùng `skill_count` cho `skill_rate`, `n` cho loại khác. Các route khác không đổi (hành vi 20 và `test_fr09_cac_route_khac_khong_doi_cach_kiem_display`).
32. Deploy: `compose.prod.yml` đặt `HAIDO_MARKET_SOURCE_SKILL_ROLES = stat`; `compose.local.yml` giữ `fake` (`tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py`, thay `test_fr09_compose_chua_chon_stat_cho_skill_roles`).
33. Web: `rowN` trả `skill_count` (game: 12, không phải 43; thiếu `skill_count` thì `n`); `level` có và bắt buộc; `sap`, `machine_learning` đọc được; 422 `invalid_query` không thử lại; thiếu `level` là `unreadable`.

### RED (đợt 2)

Chạy 2026-11-17, sau khi viết test và fixture web (fixture web sinh ra từ code đợt 2, nên phần web đỏ vì thiếu file), trước khi sửa code:

- `uv run pytest tests/api tests/domain/test_ad17_envelope.py tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py -q` → 33 failed, 541 passed. Lý do: `SkillRolesData` chưa có `level`, hook `check_against_meta`, và `Envelope` chưa đổi cỡ mẫu; fixture còn hình cũ (`skill_roles[mã][vai trò]`, không có `entry` / `mentions_all_levels`, chưa có `sap` và `machine_learning`, `vn.game.entry` còn `skill_count` 43); `compose.prod.yml` chưa đặt `stat`; `test_fr09_dec6_fixture_chi_co_so_dem` đọc hình mới. Gồm `test_ad17_envelope.py` 2 failed (cỡ mẫu `skill_rate`, hook), `tests/deploy/...` 1 failed (prod `stat`), `test_ad17_web_fixtures.py` 2 failed (`sap`, `machine_learning`: 404), `test_fr09_skill_roles.py` 28 failed.
- Ở lượt này, test bảo vệ hành vi không đổi (`test_fr09_cac_route_khac_khong_doi_cach_kiem_display`, `test_fr09_o_entry_co_mot_n_duy_nhat...`, `compose.local` giữ `fake`) xanh ngay vì chúng khóa hành vi cũ; mutation bên dưới chứng minh chúng không rỗng.
- `cd web && npx vitest run tests/fr09-skill-roles-fixture.test.ts` → 1 file failed: `Failed to resolve import "./fixtures/skill-roles-machine_learning.json"` (chưa có fixture mới), nên 17 test của file chưa chạy được ở bước này. Hai test web mới về `rowN` / 422 chạy lần đầu ở GREEN; tính hiệu lực của chúng được chứng minh bằng đột biến.

### GREEN (đợt 2)

- Sửa `envelope.py`, `schemas/market.py`, `fake_market.py`, `fake_market.json`, `routes/market.py`, `compose.prod.yml`, `web/lib/skill-roles.ts`; sinh fixture web (`skill-roles-{python,figma,abap,sap,machine_learning}.json`, `newcomer-roles.json` với `skill_count` của `game`), sinh lại `docs/api/openapi.json` bằng `HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api -q`.
- Lỗi phát hiện khi chuyển xanh: (a) `test_ad17_routes.py` và `test_ad17_web_fixtures.py::newcomer_roles` đỏ vì oracle dùng `n` của ô; sửa oracle và sinh lại `newcomer-roles.json` (chỉ đổi số `skill_count` của ô `vn.game.entry`); (b) hai test mới của tôi sai: test Envelope `shown` xếp dòng sai thứ tự nên lỗi thứ tự che lỗi `display`; thêm test meta có chữ số (`coverage_notes` có "7 nguồn", chuỗi dùng chung), bỏ test đó và ghi vào `spec.md`.
- `uv run pytest tests/api tests/domain tests/deploy -q` → 976 passed.
- Toàn bộ, Postgres thật (DB `fx166_test`, không skip): `uv run pytest -q` → 1538 passed (đợt 1: 1510); `uv run ruff check .` sạch; `cd web && npx vitest run` → 22 files, 298 passed (đợt 1: 293); `npx tsc --noEmit` và `npm run lint` sạch; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

### Kiểm đột biến (đợt 2)

Mỗi lần: commit sạch, sửa một chỗ của code bằng script thay chuỗi, chạy các bộ test liên quan, rồi `git checkout -- <file>` và kiểm `git status --short` rỗng.

Python chạy `uv run pytest -q tests/api tests/domain tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py` (không đặt `HAIDO_TEST_DATABASE_URL`, nên 74 test cần DB skip; gốc: 840 passed). Web chạy `npx vitest run tests/fr09-skill-roles-fixture.test.ts` (gốc: 17 passed). Script ở scratchpad (`mut166r2.py`) kiểm `git status --short` rỗng sau mỗi lần khôi phục.

| Đột biến | Kết quả |
|---|---|
| `sample_n`: `skill_rate` dùng `n` của ô thay cho `skill_count` (`envelope.py`) | 19 failed |
| `mentioned` chỉ theo số nhắc entry-level, bỏ `mentions_all_levels` (`fake_market.py`) | 3 failed |
| Bỏ kiểm thứ tự dòng `null_data` trong `check_against_meta` (`schemas/market.py`) | 1 failed |
| Bỏ chốt lệch config/fixture của bộ nạp giả (`fake_market.py`) | 1 failed |
| `Envelope` không gọi `check_against_meta` (`envelope.py`) | 2 failed |
| Validator `mentioned`: `any` thành `all` (`schemas/market.py`) | 1 failed |
| Đổi chỗ `name_en` / `name_vi` (`fake_market.py`) | 2 failed |
| `rowN` trả `n` của ô (`web/lib/skill-roles.ts`) | 1 failed (`rowN là cỡ mẫu của phép đo...`, web) |
| `invalid_query` thử lại được (`web/lib/skill-roles.ts`) | 1 failed (`unknown_skill, unknown_cell và invalid_query không cho thử lại...`, web) |

Không đột biến nào sống.

Ghi chú về lượt chạy: agent làm đợt 2 bị dừng giữa lúc kiểm đột biến. Nó để lại một đột biến chưa khôi phục ở `fake_market.py` (đổi chỗ hai tên), và một vòng đột biến nền của nó đổi `compose.prod.yml` (`stat` thành `fake`) trong lúc lượt đầu của bảng này đang chạy. Cả hai được trả về bản đã commit bằng `git checkout`. Lượt đầu bị lẫn (đột biến thứ nhất ra 20 failed) nên bị bỏ; bảng trên là lượt chạy lại trên cây sạch, không còn tiến trình nào khác.

## Đợt #309 (2026-11-17): compose.prod đặt `stat` cho mọi nguồn

Lý do: `deploy/compose.prod.yml` thiếu `HAIDO_MARKET_SOURCE_SKILL_RATES` và `HAIDO_MARKET_SOURCE_LEARNING_PATH`, nên prod phục vụ số giả của hai phép này. #309 thêm hai dòng `stat` và test `tests/deploy/test_gh309_prod_khong_doc_du_lieu_gia.py` sinh từ `SOURCE_ENV`. Hành vi và AC của issue này không đổi; test cũ của nó vẫn xanh.

- RED: test mới của #309, `3 failed, 8 passed` (thiếu `skill_rates`, `learning_path`).
- GREEN: `tests/deploy` 75 passed.

## Đợt 2026-11-17 (#151, #106, #103): file dùng chung đổi, AC của issue này không đổi

Lý do: tỷ lệ kỹ năng thật (#151), phép 2 `select_cell` (#106) và ràng buộc lớp đọc (#103) sửa file mà issue này từng đụng:

  - `haido_api/stat_market.py` (thêm `skill_rates` thật, đọc `stat_skill_rates`);
  - `deploy/compose.prod.yml` (thêm `HAIDO_MARKET_SOURCE_SKILL_RATES: stat`);
  - `docs/api/envelope-meta.md` (mô tả bản thật của `skill-rates`);

Hành vi và AC của issue này không đổi: thay đổi chỉ thêm (phương thức `skill_rates` thật, trường `order` có mặc định, một biến môi trường ở prod, một đoạn tài liệu); `city_shares`, `newcomer_roles`, `learning_path`, `skill_roles` của `StatMarket` giữ nguyên. Chi tiết: `specs/151-ty-le-ky-nang-that/plan.md`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #151, #106, #103 nằm ở `specs/151-ty-le-ky-nang-that/tdd.md`, `specs/106-chon-o-quay-ve/tdd.md`, `specs/103-api-doc-ty-le-that/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed; `cd web && npx vitest run` → 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

Cập nhật sau review (đợt 2, 2026-11-17): trong `StatMarket` chỉ `skill_rates` đổi thêm (404 khi ô không có hàng tỷ lệ, `n_scanned` nhất quán, chữ nhãn); hành vi và AC của issue này vẫn không đổi. RED và GREEN: `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `haido_api/stat_market.py`, `tests/api/test_fr09_skill_roles.py`, `tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

Ghi thêm (#168, 2026-11-17): kịch bản 1 của User Story 3 ("stat luôn 404 không ngày") chỉ còn đúng khi chưa có snapshot đọc được; test `test_fr09_stat_chua_co_so_that_nen_la_unknown_cell_khong_co_ngay` được thay bằng `test_fr09_stat_khong_mo_ket_noi_luc_dung_nguon`, còn 404 không ngày kiểm trên Postgres ở `tests/api/test_fr09_skill_roles_stat.py`. AC của issue #166 (hình response, bản giả) không đổi; đây là trạng thái chuyển tiếp mà chính spec ghi "đến #168".

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.
