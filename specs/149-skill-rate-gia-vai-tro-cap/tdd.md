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
