# TDD: Đọc số tin entry-level từ cơ cấu cấp bậc toàn quốc

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test dùng Postgres thật (`haido_test` trên Docker local), dựng thẳng hàng `stat_*`, không có tin nào trong bảng tin.

Lệnh:

```text
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q
```

## Các hành vi

1. `test_fr37_so_tin_entry_level_la_n_cua_o_toan_quoc_nhom_entry`: entry = n của ô `vn` nhóm `entry` (20), n = ô `vn` ở `all` (50), mix giữ nguyên, ô `ha_noi` cấp `entry` (n = 999) không được dùng, `levels` = Intern/Fresher/Junior.
2. `test_fr37_doc_so_nguoi_moi_khong_cham_bang_tin`: không câu SQL nào có `job_`, `public.`, `sum(`, `count(`.
3. `test_fr37_doc_snapshot_cong_bo_moi_nhat_bo_qua_snapshot_dang_mo`: snapshot `open` mới hơn bị bỏ qua.

## RED (2026-11-12)

`uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → 9 failed, 1 passed. Ba test của issue này đỏ vì `StatMarket.newcomer_roles` còn là bản giữ chỗ của #144, luôn ném `UnknownCell` nên route trả 404 (`assert 404 == 200`). Test xanh duy nhất là test 404 khi chưa có snapshot của #146 (bản giữ chỗ cũng trả 404).

## GREEN (2026-11-12)

- `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → 10 passed.
- `uv run pytest -q` (Postgres) → 959 passed.
- `uv run ruff check .` sạch; `tools/gates/check_gates.py` → 8 pass (có AD-7), 2 skip, 0 fail.
- Số thật: `StatMarket.newcomer_roles` trên DB local `haido` (bản sao prod, snapshot 12/11) cho `it_infra` 132/485, `ba_po_pm` 128/791, `backend` 56/470, `game` 43/99; khớp `n` của ô `vn` mà `GET /api/v1/city-shares?level=entry` của prod trả cùng ngày.

## Đợt 2026-11-13 (#148)

Lý do: `stat_market.py` và file test chung thêm bảo vệ entry > n (xem `specs/146-tra-so-nguoi-moi/tdd.md`). Không đổi kỳ vọng nào của #145.

- RED: không có, test của #145 không đổi.
- GREEN: `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → 15 passed (gồm ba test của #145).

## Đợt 2026-11-15 — gộp main vào #212 (thêm nguồn `learning_path`)

Lý do: nhánh #212 thêm `"learning_path": fake` vào lời dựng `create_app` ở `tests/api/test_fr37_newcomer_roles_stat.py` (file dùng chung của #145); `StatMarket.newcomer_roles` và bảo vệ entry > n giữ nguyên.

- RED: không có. Hành vi của issue không đổi; test chỉ thêm nguồn `learning_path` vào lời dựng `create_app` (nếu có) hoặc chạy lại trên fixture mới.
- GREEN (chạy lại thật, 2026-11-15): `uv run pytest -q tests/api/test_fr37_newcomer_roles_stat.py tests/api/test_fr37_newcomer_roles.py tests/api/test_ad17_web_fixtures.py` → 42 passed; toàn bộ `uv run pytest -q` → 1113 passed.

## Đợt 2026-11-16 (#111): file dùng chung đổi, hành vi của issue này không đổi

Lý do: nhánh `gh-111-ho-so-ky-nang` sửa file mà issue này từng đụng: `haido_api/fixtures/fake_market.json` (thêm `skill_rates` cho mọi vai trò, #149), `haido_api/schemas/market.py`, `routes/market.py`, `market_source.py`, `fake_market.py`, `stat_market.py` (chữ ký `skill_rates` nhận `have`, #149), `haido_api/main.py` và `tests/api/test_ad17_routes.py` (route `role-for-title`, #150), `docs/api/*`. Các thay đổi chỉ chạm `skill-rates` và route mới; `city-shares`, `newcomer-roles`, `skills` và khóa trình duyệt không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi.
- GREEN: `uv run pytest -q` → 1018 passed, 217 skipped; `cd web && npx vitest run` → 21 files, 281 passed; `tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.

## Đợt 2026-11-17 (#166): file dùng chung đổi, hành vi của issue này không đổi

Lý do: #166 (hình response `skill-roles`) sửa file mà issue này từng đụng: `haido_api/stat_market.py` (thêm `StatMarket.skill_roles`, cập nhật docstring lớp) và `tests/api/test_fr37_newcomer_roles_stat.py` (lời dựng `create_app` thêm nguồn `skill_roles`). Thay đổi: `newcomer_roles` thật không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #166 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `t166_test`) → 1510 passed, không skip; `cd web && npx vitest run` → 22 files, 293 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

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

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`, `haido_api/stat_market.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.
