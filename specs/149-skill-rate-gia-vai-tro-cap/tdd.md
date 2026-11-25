# TDD: Endpoint tỷ lệ kỹ năng giả theo vai trò và cấp

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh:

```text
uv run pytest tests/api/test_fr19_skill_rates_vai_tro_cap.py -q
```

## Các hành vi

1. Mọi vai trò × `entry`, `all` → 200, `data.role`/`data.level` đúng giá trị gửi.
2. `level=khong_co` → 422 `invalid_query`.
3. Backend · Intern, UI/UX · Entry, DevOps · Entry: ô rộng hơn, `fallback_label` có, n ≥ 30.
4. Data Engineer · Entry: mọi `rate` `null_data`, `group` `null`, `core_size`/`have_core` `null`.
5. Dòng có tỷ lệ trước, giảm dần, hòa theo mã; nhóm khớp θ.
6. `have=java,sql,git,khong_co_trong_o`: cờ `have` đúng; `core_size`, `have_core` đúng.
7. `have` sai định dạng, quá 200 mã → 422.

## RED (2026-11-16)

`uv run pytest tests/api/test_fr19_skill_rates_vai_tro_cap.py -q` → 61 failed, 5 passed. Lý do:

- 53 test: 404 `unknown_cell`, vì fixture chỉ có `skill_rates` cho `ai_ml`, `backend`, `data_engineer`, `java_backend` ở vài cấp.
- `level=khong_co` ra 404 thay vì 422: route nhận mọi chuỗi snake_case.
- 4 test `have` sai ra 200: route chưa đọc `have`.
- `KeyError: 'have'`, `KeyError: 'core_size'`: schema chưa có hai trường này.
- 5 test xanh sẵn là các ô fixture đã có (`ai_ml`, `backend`, `data_engineer` ở `entry`; Backend · Intern quay về; `backend` · `lead` 404).

## GREEN (2026-11-16)

- Lượt đầu sau khi sửa: response 500 `invalid_response`, vì Envelope (AD-17) cấm số trần `core_size`, `have_core`. Đổi hai trường sang `Ordinal | None` như `path_size`, thêm vào `tests/api/test_ad17_ordinal_allowlist.py` và quy tắc 1 của `docs/api/envelope-meta.md`.
- Ba test cũ đỏ do thay đổi chủ ý, đã sửa test kèm chú thích:
  - `test_ad17_khong_co_o_tra_404`: `level=khong_ton_tai` giờ là 422; đổi sang `ai_ml` · `senior`.
  - `test_ad17_instance_sua_bang_model_copy_van_bi_kiem_lai`: stub nhận thêm `have`.
  - `test_ad17_cap_khac_cua_vai_tro_san_sang_la_404_nhu_skill_rates` (#212) và `test_fr22_ai_ml_entry_not_ready_nhung_co_skill_rates_de_mo_ho_so` (#212): `all` và `qa` · `entry` giờ có ô; đổi sang `lead` và `qa` · `senior`.
- `uv run pytest tests/api/test_fr19_skill_rates_vai_tro_cap.py -q` → 66 passed.
- `HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api -q` sinh lại `docs/api/openapi.json`; `uv run pytest tests/api -q` → 364 passed, 74 skipped.

## Đợt 2026-11-17 (#166): file dùng chung đổi, hành vi của issue này không đổi

Lý do: #166 (hình response `skill-roles`) sửa file mà issue này từng đụng: `haido_api/market_source.py`, `fake_market.py`, `stat_market.py`, `routes/market.py`, `schemas/market.py`, `fixtures/fake_market.json`, `docs/api/*`, `tests/api/test_ad17_routes.py`, `test_ad17_web_fixtures.py` (mục `skill_rates` và hàng `skill-rates` không đổi). Thay đổi: thêm phép `skill_roles`, route `skill-roles`, mã lỗi `unknown_skill`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #166 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `t166_test`) → 1510 passed, không skip; `cd web && npx vitest run` → 22 files, 293 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Đợt 2026-11-17 (#166, đợt 2 theo review): file dùng chung đổi lần nữa, AC của issue này không đổi

Lý do: #166 đợt 2 (cỡ mẫu `skill_count` của `skill_rate`, `mentioned` theo mọi cấp, `data.level`, prod chọn nguồn `stat`) sửa thêm `haido_core/domain/envelope.py`, `haido_api/fake_market.py`, `fixtures/fake_market.json`, `schemas/market.py`, `routes/market.py`. `skill-rates` giờ kiểm `display` của `skill_rate` theo `n_by_measure.skill_count` (thiếu khóa thì `n`). Ở bản giả chỉ ô `vn.game.entry` có `skill_count` (12) khác `n` (43): `GET /skill-rates?role=game&level=entry` ẩn mọi tỷ lệ (`null_data`). Không AC nào của #149 nêu `game` ở cấp `entry`; các test của #149 không đổi kỳ vọng. Phiên bản thật của `skill-rates` (#151) phải ghi `skill_count = n_scanned` vào `meta.cells`.

- RED: không có, vì không có hành vi nào của issue này đổi. RED của #166 đợt 2 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx166_test`, không skip) → 1538 passed; `cd web && npx vitest run` → 22 files, 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Đợt 2026-11-17 (#151, #106, #103): file dùng chung đổi, AC của issue này không đổi

Lý do: tỷ lệ kỹ năng thật (#151), phép 2 `select_cell` (#106) và ràng buộc lớp đọc (#103) sửa file mà issue này từng đụng:

  - `haido_api/stat_market.py` (thêm `skill_rates` thật, đọc `stat_skill_rates`);
  - `docs/api/envelope-meta.md` (mô tả bản thật của `skill-rates`);

Hành vi và AC của issue này không đổi: thay đổi chỉ thêm (phương thức `skill_rates` thật, trường `order` có mặc định, một biến môi trường ở prod, một đoạn tài liệu); `city_shares`, `newcomer_roles`, `learning_path`, `skill_roles` của `StatMarket` giữ nguyên. Chi tiết: `specs/151-ty-le-ky-nang-that/plan.md`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #151, #106, #103 nằm ở `specs/151-ty-le-ky-nang-that/tdd.md`, `specs/106-chon-o-quay-ve/tdd.md`, `specs/103-api-doc-ty-le-that/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed; `cd web && npx vitest run` → 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

Cập nhật sau review (đợt 2, 2026-11-17): trong `StatMarket` chỉ `skill_rates` đổi thêm (404 khi ô không có hàng tỷ lệ, `n_scanned` nhất quán, chữ nhãn); hành vi và AC của issue này vẫn không đổi. RED và GREEN: `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`, `haido_api/stat_market.py`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`, `docs/api/openapi.json`, `haido_api/fixtures/fake_market.json`, `haido_api/stat_market.py`, `haido_core/domain/envelope.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.

## Đợt #278 (2026-11-23): từ vựng lớn lên, AC của issue này không đổi

Lý do: #278 sinh lại `web/tests/fixtures/skills.json` (fixture của `GET /api/v1/skills`, thêm trong commit của #149/#150) theo từ vựng 265 mã, `vocab_version` `seed-2026-11-23`. Hình dạng response không đổi; tỷ lệ kỹ năng của issue này không đổi.

RED, GREEN và đột biến: `specs/278-ma-ky-nang-thuong-gap/tdd.md`.

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: sửa file mà issue này từng đụng (trong số `fake_market.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `tools/gates/check_gates.py`, `web/lib/learning-path.ts`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: sửa file mà issue này từng đụng (trong số `stat_market.py`, `check_gates.py`, `envelope-meta.md`, `compose.prod.yml`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.
