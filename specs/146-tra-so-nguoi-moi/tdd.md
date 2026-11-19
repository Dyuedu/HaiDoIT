# TDD: Trả số tin entry-level, tỷ lệ và n của mỗi vai trò

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test API dùng Postgres thật (`haido_test`), dựng thẳng hàng `stat_*`. Test deploy đọc file compose.

Lệnh:

```text
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test uv run pytest tests/api/test_fr37_newcomer_roles_stat.py tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py -q
```

## Các hành vi

1. `test_fr37_moi_vai_tro_cua_config_deu_co_dong`: đủ 17 mã của config; `game` vắng là 0/0, `null_data`.
2. `test_fr37_vai_tro_du_mau_khong_co_tin_entry_hien_0`: `qa` 0/35, `share = 0`, `shown`.
3. `test_fr37_vai_tro_duoi_30_tin_khong_co_ty_le_nhung_van_co_so`: `ui_ux` 3/12, `null_data`, value `null`, `level_share` của `vn.ui_ux`.
4. `test_fr37_nguong_mau_lay_tu_config`: `min_sample = 10` đổi `ui_ux` sang `shown`.
5. `test_fr37_thu_tu_dong_co_ty_le_truoc_roi_so_entry_giam_dan`: `qa`, `backend`, `devops`, `mobile`, rồi `ui_ux`, rồi phần còn lại theo mã.
6. `test_fr37_envelope_co_ngay_snapshot_nguon_va_nguon_loi`: ngày, `partial`, nguồn A–Z, nguồn lỗi.
7. `test_fr37_chua_co_snapshot_doc_duoc_la_404`: 404 `unknown_cell`.
8. `test_gh146_compose_prod_chon_nguon_stat_cho_newcomer_roles`.
9. `test_gh146_compose_local_giu_nguon_gia_cho_newcomer_roles`.

## RED (2026-11-12)

- `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → 9 failed, 1 passed. Sáu test 1–6 của issue này (cùng ba test của #145) đỏ vì `StatMarket.newcomer_roles` còn là bản giữ chỗ, luôn ném `UnknownCell` → 404 (`assert 404 == 200`). Test 7 xanh ngay vì bản giữ chỗ cũng trả 404; giữ lại để khóa hành vi khi chưa có snapshot.
- `uv run pytest tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py -q` → 1 failed, 1 passed: `compose.prod.yml` chưa có biến (`assert None == 'stat'`). Test 9 xanh ngay (local vốn không đặt biến).

## GREEN (2026-11-12)

- Hai file test trên → 12 passed.
- `uv run pytest -q` (Postgres) → 959 passed.
- `uv run ruff check .` sạch; `tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.
- Trên DB local `haido` (bản sao prod, snapshot 12/11): 17 dòng; 16 vai trò có tỷ lệ, đứng đầu là `it_infra` 132/485 (27,2%), `ba_po_pm` 128/791, `qa` 77/292; `data_scientist` 5/28 là `null_data` và đứng cuối.

## Đợt 2026-11-13 (#148): ô hỏng entry > n

Lý do sửa: review PR #291 chỉ ra phép chia `entry_n / total_n` không có bảo vệ. Một ô hỏng làm cả danh sách 17 dòng không đọc được ở web.

- RED: `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → 3 failed, 12 passed. Hai test đỏ vì `ValidationError` của `Stat` thay vì `RuntimeError` và code `invalid_response` thay vì `internal_error`; một test `DID NOT RAISE` (vai trò dưới ngưỡng, entry 20 > n 12).
- GREEN: cùng lệnh → 15 passed. `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py tests/deploy/test_gh146_nguoi_moi_doc_snapshot_that.py -q` → 17 passed. `uv run pytest -q` → 964 passed.
- Chi tiết và đột biến: `specs/148-test-nguoi-moi/tdd.md`.

## Đợt 2026-11-15 — gộp main vào #212 (thêm nguồn `learning_path`)

Lý do: nhánh #212 thêm `"learning_path": fake` vào lời dựng `create_app` ở `tests/api/test_fr37_newcomer_roles_stat.py` (file dùng chung của #146); `StatMarket.newcomer_roles` và bảo vệ entry > n giữ nguyên.

- RED: không có. Hành vi của issue không đổi; test chỉ thêm nguồn `learning_path` vào lời dựng `create_app` (nếu có) hoặc chạy lại trên fixture mới.
- GREEN (chạy lại thật, 2026-11-15): `uv run pytest -q tests/api/test_fr37_newcomer_roles_stat.py tests/api/test_fr37_newcomer_roles.py tests/api/test_ad17_web_fixtures.py` → 42 passed; toàn bộ `uv run pytest -q` → 1113 passed.

## Đợt 2026-11-16 (#111): file dùng chung đổi, hành vi của issue này không đổi

Lý do: nhánh `gh-111-ho-so-ky-nang` sửa file mà issue này từng đụng: `haido_api/fixtures/fake_market.json` (thêm `skill_rates` cho mọi vai trò, #149), `haido_api/schemas/market.py`, `routes/market.py`, `market_source.py`, `fake_market.py`, `stat_market.py` (chữ ký `skill_rates` nhận `have`, #149), `haido_api/main.py` và `tests/api/test_ad17_routes.py` (route `role-for-title`, #150), `docs/api/*`. Các thay đổi chỉ chạm `skill-rates` và route mới; `city-shares`, `newcomer-roles`, `skills` và khóa trình duyệt không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi.
- GREEN: `uv run pytest -q` → 1018 passed, 217 skipped; `cd web && npx vitest run` → 21 files, 281 passed; `tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.

## Đợt 2026-11-17 (#166): file dùng chung đổi, hành vi của issue này không đổi

Lý do: #166 (hình response `skill-roles`) sửa file mà issue này từng đụng: `haido_api/stat_market.py` (thêm `StatMarket.skill_roles`), `docs/api/envelope-meta.md` (thêm mục `skill-roles` và dòng `HAIDO_MARKET_SOURCE_SKILL_ROLES`), `tests/api/test_fr37_newcomer_roles_stat.py` (lời dựng `create_app`). Thay đổi: `deploy/compose.prod.yml` vẫn đặt `stat` cho `newcomer_roles` như trước và không đặt gì cho `skill_roles`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #166 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `t166_test`) → 1510 passed, không skip; `cd web && npx vitest run` → 22 files, 293 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Đợt 2026-11-17 (#166, đợt 2 theo review): file dùng chung đổi lần nữa, AC của issue này không đổi

Lý do: #166 đợt 2 (cỡ mẫu `skill_count` của `skill_rate`, `mentioned` theo mọi cấp, `data.level`, prod chọn nguồn `stat`) sửa thêm `haido_core/domain/envelope.py` (cỡ mẫu của `skill_rate`, hook `check_against_meta`), `deploy/compose.prod.yml` (thêm `HAIDO_MARKET_SOURCE_SKILL_ROLES: stat`, giữ `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES: stat`), `haido_api/fake_market.py`, `fixtures/fake_market.json`. `newcomer-roles` ở production vẫn đọc `stat`, không đổi; `test_gh146_*` không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi. RED của #166 đợt 2 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx166_test`, không skip) → 1538 passed; `cd web && npx vitest run` → 22 files, 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

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

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `haido_api/stat_market.py`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`, `haido_api/stat_market.py`, `haido_core/domain/envelope.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.
