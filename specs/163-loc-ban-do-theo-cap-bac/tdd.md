# TDD: Lọc bản đồ theo cấp bậc

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh của repo, chạy từng file trong lúc làm (Postgres cho test có DB, dùng `127.0.0.1`):

```text
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test uv run pytest <file> -q
npm --prefix web run test            # hoặc: cd web && npx vitest run <file>
```

Mỗi test một hành vi, assert đầu ra. Tên test mang mã FR hoặc AD (`test_fr33_*` cho tỷ trọng thành phố, `test_ad17_*` cho hợp đồng API). Ngày: 2026-11-11.

## Các hành vi và test phủ

| AC của #163 | Scenario | Test |
|---|---|---|
| AC1: bộ lọc hiện mặc định của #134 | US1.1, US1.2 | `web/tests/fr33-level-filter.test.tsx` (mặc định `entry`, URL `level=entry`, danh sách và thứ tự nút, `aria-pressed`, 44px), `tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` (nút khớp config, `DEFAULT_LEVEL = "entry"`) |
| AC1 | US1.3 | `tests/core/test_ad10_rules_config.py::test_fr33_cap_bac_*`, `tests/domain/test_fr33_aggregate_level.py::test_fr33_nhom_entry_*`, `tests/steps/test_fr33_aggregate_level_step.py::test_fr33_nhom_entry_*` |
| AC1 | US1.4 | `tests/api/test_fr33_city_shares_level.py::test_fr33_khong_gui_level_*`, `::test_fr33_route_chuyen_level_*` |
| AC2: đổi cấp thì bảng và biểu đồ đổi cùng nhau | US2.1–US2.4 | `web/tests/fr33-level-filter.test.tsx` (đổi cấp ở cả lối 2D và Bảng, bỏ response muộn, giữ cấp khi đổi vai trò, `unknown_cell`, Thử lại, `data.level` lệch) |
| AC2 | US2.5 | `tests/domain/test_fr33_aggregate_level.py`, `tests/steps/test_fr33_aggregate_level_step.py`, `tests/db/test_fr33_stat_city_shares_level.py` (tổng bằng 1, n = 0 rơi vào `unknown`, một transaction, chạy lại không nhân đôi) |
| AC2 | US2.6 | `tests/api/test_fr33_city_shares_level.py::test_fr33_cap_la_tra_422_*`, `::test_fr33_openapi_liet_ke_*` |
| AC3: dưới 30 tin ở cấp đã chọn thì mờ như mọi cấp | US3.1 | `tests/api/test_fr33_city_shares_level.py::test_fr33_thanh_pho_duoi_30_*`, `::test_fr33_display_do_suppression_for_*` |
| AC3 | US3.2, US3.3 | `web/tests/fr33-level-filter.test.tsx` (nhóm "thành phố dưới 30 tin"), `tests/api/test_fr33_city_shares_level.py::test_fr33_mo_theo_n_cua_cap_*` |
| #260: không đổi ngưỡng, θ, lưu ý | Edge | `tests/core/test_ad10_rules_config.py::test_fr33_cap_bac_khong_doi_*`, `tests/api/test_fr33_city_shares_level.py::test_fr33_cap_bac_khong_doi_*` |
| #100, #263, #259 giữ nguyên | Edge | `tests/steps/test_fr33_aggregate_level_step.py` (cụm, cửa sổ 60 ngày, nguồn bị loại, `stat_sources`) |
| Nguồn giả cho local và smoke | FR-006 | `tests/api/test_fr33_city_shares_level.py::test_fr33_ban_gia_*`, `tests/api/test_ad17_web_fixtures.py`, `tests/api/test_ad17_routes.py` |

## Đợt 1 — config (`level_options`, `level_groups`)

Test: `tests/core/test_ad10_rules_config.py` (thêm `test_fr33_*`, và `BASE` có hai khóa mới).

**RED**: `uv run pytest tests/core/test_ad10_rules_config.py -q` → 20 failed, 71 passed. 2 lỗi `AttributeError: 'RulesConfig' object has no attribute 'level_options'`, 1 lỗi `config_version` vẫn là `2026-11-10.3`, 17 lỗi `DID NOT RAISE ConfigError` (cấu hình sai chưa bị bắt).

**GREEN**: thêm hai khóa vào `config/rules.toml` (`config_version` lên `2026-11-11.1`) và `_level_filter` trong `haido_core/config.py` → 91 passed.

## Đợt 2 — hàm thuần `aggregate_city_shares`

Test: `tests/domain/test_fr33_aggregate_level.py` (10 test, một test `determinism`).

**RED**: `uv run pytest tests/domain/test_fr33_aggregate_level.py -q` → 10 failed, cùng lỗi `TypeError: aggregate_city_shares() got an unexpected keyword argument 'level_options'`.

**GREEN**: `CellRow.seniority`, `ShareRow.seniority`, tham số `level_options` và `level_groups` → 10 passed; cả `tests/domain` 124 passed (test cũ của #93 nguyên vẹn vì không khai cấp lọc thì chỉ có `all`).

## Đợt 3 — migration 0005 và `tables.py`

Test: `tests/db/test_fr33_stat_city_shares_level.py` (6 test: một head, cột và khóa, khác cấp không trùng khóa, `seniority` không NULL và không mặc định, hạ cấp rồi nâng lại, hàng cũ nhận `all`).

**RED**: → 6 failed. `AssertionError: ['0004_haido_stat_sources'] == ['0005_haido_city_share_level']` và `UndefinedColumn: column "seniority" ... does not exist`.

**GREEN**: `0005_haido_city_share_level.py` và cột `seniority` trong `tables.py` → 6 passed. `tests/db` còn 2 test cũ của #93, #259 đỏ (đòi head 0004 và khóa không có `seniority`); sửa chúng và câu INSERT vị trí trong `test_dat20_stat_tables.py` → `tests/db` 52 passed.

## Đợt 4 — bước `aggregate` và kho dữ liệu

Test: `tests/steps/test_fr33_aggregate_level_step.py` (12 test, một `determinism`).

**RED**: → 12 failed. `psycopg.errors.NotNullViolation: null value in column "seniority" of relation "stat_city_shares"`: migration đã có, bước chưa ghi cấp bậc.

**GREEN**: `snapshot_store.replace_stats` ghi `seniority`, `aggregate_snapshot` truyền `level_options` và `level_groups` từ config → 12 passed.

Sau đó `uv run pytest tests/steps tests/test_dat20_cli.py tests/test_ad4_cli.py -q` đỏ 21 test cũ (19 trong `test_dat20_aggregate_step.py`, 1 `test_dat20_api_end_to_end.py`, 1 `test_dat20_cli.py`) vì mỗi (vai trò, phạm vi) có 9 hàng. Sửa các hàm đọc để lọc `seniority = 'all'`, đổi `ORDER BY` thêm `seniority`, đổi số đếm (66 → 594 ô, 55 → 495 tỷ trọng). Test e2e chờ đợt 5.

## Đợt 5 — API và nguồn giả

Test: `tests/api/test_fr33_city_shares_level.py` (25 test), `tests/api/test_ad17_web_fixtures.py` (thêm cấp `entry`).

**RED**: `uv run pytest tests/api/test_fr33_city_shares_level.py -q` → 20 failed, 5 passed. Lỗi: `KeyError: 'level'` (chưa có `data.level`), `TypeError: FakeMarket.city_shares() got an unexpected keyword argument 'level'`, `assert 404 == 422` (cấp lạ chưa bị từ chối), `'shown' == low_sample_shown` (chưa đọc hàng của cấp).
`tests/api/test_ad17_web_fixtures.py` → 6 failed (3 `FileNotFoundError` của file `.entry.json`, 3 lệch vì chưa có `data.level`).

**GREEN**: `data.level` trong `schemas/market.py`, `level` trong `market_source.py`, `routes/market.py` (`Literal` dựng từ config), `stat_market.py`, `fake_market.py` và `fixtures/fake_market.json` (`city_shares[vai trò][cấp]`) → 25 passed. Sinh lại 6 file `web/tests/fixtures/city-shares-*.json` bằng `TestClient` như docstring của test mô tả → 6 passed. Sinh lại `docs/api/openapi.json` bằng `HAIDO_UPDATE_OPENAPI=1`.
Test cũ đỏ vì đổi hợp đồng: 32 test trong `tests/api` (stub nguồn không nhận `level`, `INSERT ... VALUES` vị trí của `_seed`, test dựng `CitySharesData` thiếu `level`, ảnh chụp OpenAPI). Sửa → `tests/api` xanh; `tests/steps/test_dat20_api_end_to_end.py` xanh.

## Đợt 6 — web

Test: `web/tests/fr33-level-filter.test.tsx` (18 test), `tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` (5 test).

**RED**: `npx vitest run tests/fr33-level-filter.test.tsx` → 18 failed. Màn chưa gửi `level` nên bản thay `fetch` (khóa `all|entry`) không có reply cho `role=all` không cấp, màn hiện "Không đọc được số liệu" và mọi test không tìm thấy `Hà Nội:` (`TestingLibraryElementError: Unable to find role="button"`); chưa có nhóm "Cấp bậc".
`uv run pytest tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py -q` → 4 failed, 1 passed (`không thấy LEVEL_OPTIONS trong web/lib/labels.ts`). Test thứ năm (bản giả chỉ có `all` và `entry`) xanh ngay vì fixture đã đổi ở đợt 5.

**GREEN**: `LEVEL_OPTIONS`, `DEFAULT_LEVEL`, `levelLabel` trong `labels.ts`; `level` trong `fetchCityShares` và kiểm `data.level`; `level-chips.tsx`; `map-screen.tsx` (`Request` có `level`, `changeLevel`, cùng cơ chế bỏ response muộn với đổi vai trò); tiêu đề biểu đồ và bảng kèm nhãn cấp → 18 passed và 5 passed (sau khi neo regex `export const LEVEL_OPTIONS` để không khớp nhầm đoạn chú thích đầu file).
Test cũ đỏ vì đổi hợp đồng: 2 test của #46 trong `web/tests/fr33-map-screen.test.tsx` (URL nay có `&level=entry`; thêm 9 điểm Tab của nhóm cấp bậc). Sửa → xanh. Bản thay `fetch` trong `tests/helpers/fetch.ts` nay chọn hàng theo `role|level` và trả lại cấp đã hỏi ở `data.level` như API thật (`echoLevel`), nên các test cũ không đổi.

Test mức thư viện thêm sau code, rồi kiểm RED bằng cách tạm hoàn tác `web/lib/city-shares.ts` và `city-shares-view.ts` (`git stash`): `web/tests/ad17-city-shares-client.test.ts` (`fr33 #163 — cấp bậc trong lượt đọc city-shares`) và `web/tests/fr33-city-shares-view.test.ts` (`fr33 #163 — nhãn cấp bậc trên view`) → 6 failed, 70 passed; khôi phục code → xanh (hai test dữ liệu thuần vốn xanh).

## Đợt 7 — sửa sau review (2026-11-11)

Test: `tests/api/test_fr33_city_shares_level.py` (thay test 404 của snapshot cũ bằng hai test), `tests/core/test_ad10_rules_config.py` (+3), `tests/domain/test_fr33_aggregate_level.py` (+1), `tests/db/test_fr33_stat_city_shares_level.py` (mở rộng), `web/tests/fr33-level-filter.test.tsx` (+2), `tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` (+1).

**RED**: `uv run pytest` trên năm file Python → 6 failed, 137 passed: F1 hai test API (snapshot mới chỉ có `all` vẫn trả 404; thông báo cũ nói về vai trò), F2 hai test (tên nhóm `En-try` và mã `Jun-ior` được nhận), F3 một test (`DID NOT RAISE ValueError`), F4 một test (`stat_cells` còn hàng `entry` sau hạ cấp). Test `level_groups` không phải bảng xanh ngay vì `_level_filter` đã có nhánh `isinstance(groups, dict)`; giữ làm test chống lùi. Web: 2 test mới (F5) xanh trên mã hiện tại; kiểm đột biến bằng cách tạm bỏ `· {view.levelLabel}` và `aria-describedby` → 2 failed, 18 passed; khôi phục. F6 xanh ngay vì ghi chú đang khớp config; nó chỉ đỏ khi config đổi mà UI không đổi.

**GREEN**: `_latest_readable(conn, level)` lọc `stat_city_shares.seniority = level`, không có thì `UnknownCell` không ngày kèm thông báo "chưa có snapshot nào đã công bố được tính cho cấp bậc này"; `_CODE_SHAPE` trong `config.py`; kiểm trùng thành viên đầu `aggregate_city_shares`; downgrade 0005 xóa thêm `stat_cells.seniority <> 'all'` → 5 file Python xanh, `tests/api` xanh.

| Lệnh | Kết quả |
|---|---|
| `uv run pytest -q` | 690 passed |
| `uv run ruff check .` | All checks passed |
| `check_gates.py --require ...` | 8 pass, 2 skip, 0 fail |
| `uv run alembic heads` | `0005_haido_city_share_level (head)` |
| `npm run lint` / `test` / `build` | sạch / 144 passed / thành công |

## Lần chạy cuối

| Lệnh | Kết quả |
|---|---|
| `uv run pytest -q` (có `HAIDO_TEST_DATABASE_URL`) | 684 passed |
| `PYTHONHASHSEED=0 uv run pytest -q -m determinism` | 6 passed |
| `PYTHONHASHSEED=1 uv run pytest -q -m determinism` | 6 passed |
| `uv run ruff check .` | All checks passed |
| `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11` | 8 pass, 2 skip (FR-22, FR-24, có hạn), 0 fail |
| `uv run alembic heads` | `0005_haido_city_share_level (head)` |
| `npm run lint` (trong `web/`) | sạch |
| `npm run test` | 142 passed |
| `npm run build` | thành công |

## REFACTOR

Giữ hàm thuần: nhóm cộng từ cấp thô, không hỏi phép dân số thêm. Không thêm gói. Chạy lại đúng file test sau mỗi lần sửa.

## Đợt 8 — 2026-11-11, rebase lên `main` có #144

Lý do: `main` nhận #144 (hình response màn người mới), bắt `create_app` phải có nguồn `newcomer_roles`, và cùng sửa `fake_market.json`.

- RED: `uv run pytest -q` → 2 failed, 18 errors, đều trong `tests/api/test_fr33_city_shares_level.py`: `ValueError: Thiếu nguồn cho phép: newcomer_roles.` vì test dựng app chỉ với `city_shares` và `skill_rates`.
- Sửa: thêm `"newcomer_roles": FakeMarket()` vào các app dựng trong test; ghép `fake_market.json` theo nội dung (ô của hai bên không trùng).
- GREEN: `tests/api/test_fr33_city_shares_level.py` → 26 passed; `uv run pytest -q` → 715 passed; hai lượt `-m determinism` → 6 passed mỗi lượt; web `npm run test` → 149 passed, `lint` sạch, `build` qua; `ruff` sạch; cổng 0 failed.

## Đợt 9 — 2026-11-12, sau khi thêm lộ trình học (#212)

Lý do: #212 thêm phép `learning_path` vào `create_app`, đổi mã kỹ năng của `skill_rates` giả sang snake_case và (đợt 2 của #212) sửa nội dung `skill_rates`, `envelope.py`, schema OpenAPI.

- Không viết test mới của issue này và không có đợt RED: hành vi của issue không đổi. Bản ghi trước ghi một RED giả định ("sẽ báo...") không kèm số đếm; thay bằng ghi chú này.
- Đã chạy lại các test có sẵn của issue này trên mã sau đợt 2 của #212 (kết quả thật, 2026-11-12):
  - `uv run pytest -q tests/api/test_fr33_city_shares_level.py tests/api/test_ad17_routes.py tests/api/test_ad17_web_fixtures.py tests/api/test_dat20_stat_market.py tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` → 116 passed.
  - `npx vitest run tests/fr33-level-filter.test.tsx tests/fr33-map-screen.test.tsx tests/ad17-city-shares-client.test.ts` → 104 passed.
- GREEN: `uv run pytest -q` (có Postgres) → 862 passed, không skip; hai lượt `-m determinism` (`PYTHONHASHSEED=0` và `1`) → 7 passed mỗi lượt; web `npm run test` → 164 passed.

## Đợt 9 — 2026-11-12, #280 thêm chiều số năm kinh nghiệm

Lý do: #280 thêm mốc số năm vào ô và tỷ trọng (cột `years` trong khóa của `stat_cells`, `stat_city_shares`; migration 0006), tham số `years` của `GET /api/v1/city-shares`, và web gửi `years` cùng `level`. Hành vi của #163 ở `years = any` không đổi.

- RED: sau khi có code của #280, `uv run pytest -q` → các test của #163 đỏ vì (1) helper đọc `stat_*` theo (vai trò, cấp, phạm vi) nay có 6 hàng (`too many values to unpack`), (2) số hàng chưa nhân 6 mã số năm, (3) head Alembic là 0006, (4) seed `INSERT` không nêu `years` (`NotNullViolation`), (5) test double `city_shares(role, level)` không nhận `years` (500), (6) bản giả có khóa `entry.y1`. Web: `fr33-level-filter.test.tsx` 4 failed, `fr33-map-screen.test.tsx` 2 failed (URL thiếu `&years=any`, thứ tự Tab có thêm nút số năm).
- Sửa: chỉ test (đọc hàng `years = 'any'`, nhân số hàng, head 0006, seed nêu `years`/`years_unstated`, test double nhận `years`, so khóa cấp của bản giả, URL có `&years=any`, Tab có sáu nút số năm). Không sửa code của #163 ngoài chỗ #280 nối thêm `years`.
- GREEN: `uv run pytest -q` → 770 passed; hai lượt `-m determinism` → 6 passed mỗi lượt; web `npx vitest run` → 160 passed; `lint`, `tsc`, `build` sạch; cổng 0 failed.

## Đợt 2026-11-12 — #145, #146 thêm phép đọc người mới vào `stat_market.py`

Lý do: #145, #146 thêm `StatMarket.newcomer_roles`, `_national_cells`, `_cell_meta` và hằng `ENTRY` vào `haido_api/stat_market.py`. `city_shares` và các hàm `_latest_readable`, `_shares`, `_cells`, `_sources` không đổi; `newcomer_roles` dùng lại `_latest_readable(conn, "entry")`.

- RED: không test nào của issue này đổi kỳ vọng.
- GREEN: `tests/api/test_dat20_stat_market.py`, `tests/api/test_fr33_city_shares_level.py`, `tests/api/test_fr33_city_shares_years.py` xanh trong lượt `uv run pytest -q` (Postgres) → 959 passed.

## Đợt 2026-11-12 — #147 export hàm kiểm hợp đồng của `web/lib/city-shares.ts`

Lý do: #147 thêm `export` cho `isRecord`, `isNonEmptyString`, `isStringArray`, `isCount`, `readErrorBody`, `isMeta` để màn người mới dùng chung luật đọc envelope. Thân hàm không đổi; `fetchCityShares` không đổi.

- RED: không test nào của issue này đổi kỳ vọng.
- GREEN: các test `fr33-*` và `ad17-city-shares-client` xanh trong lượt `npx vitest run` → 189 passed; `npx tsc --noEmit` sạch.

## Đợt 10 — 2026-11-13, #283 phân loại cấp ở bước ingest

Lý do: #283 thay luật cấp trong `haido_core/domain/classify.py` (đọc từ `config/classify.toml`): chữ cấp của nguồn → chức
danh → số năm theo bảng #134 → không xác định; "Product Manager" không phải cấp Lead; "Experienced (non-manager)" của
VietnamWorks không cho cấp. Bước `aggregate` dùng nhãn đã lưu ở `job_posting_facts`. Mã cấp và nhóm `entry` không đổi; tỷ lệ
"không xác định cấp" trên snapshot 12/11 của bản sao giảm từ 68,4% xuống 13,3%. Không AC nào của #163 đổi.

- RED: `test_fr33_migration_0005_noi_tiep_0004_va_la_head_duy_nhat` đỏ vì head là 0007; các test khác của #163 không đổi.
- GREEN: `tests/steps/test_fr33_aggregate_level_step.py`, `tests/db/test_fr33_stat_city_shares_level.py`,
  `tests/api/test_fr33_city_shares_level.py` xanh; `uv run pytest -q` → 887 passed.

## Đợt 11 — 2026-11-13, #284 thêm bảy vai trò

Lý do: #284 thêm bảy mã vai trò vào `config/rules.toml` và `web/lib/labels.ts`; bộ lọc cấp áp cho mọi vai trò như cũ. Bản giả có city-shares `all` và `entry` cho bảy mã mới (test `test_gh163_ban_gia_chi_co_cap_all_va_entry_la_ma_trong_config` đòi cả hai cấp). Không AC nào của #163 đổi.

- RED: `test_gh163_ban_gia_chi_co_cap_all_va_entry_la_ma_trong_config` đỏ khi bản giả mới chỉ có `all` cho mã mới; thứ tự Tab trong `fr33-map-screen.test.tsx` có thêm bảy nút.
- GREEN: thêm khối `entry`; `uv run pytest -q` → 908 passed; `npx vitest run` → 163 passed.

## Đợt 2026-11-13 — #285 34 tỉnh, Remote, Nước ngoài

Lý do: #285 đổi mã nơi (mỗi (vai trò, cấp) có hàng của 6 nơi luôn có và tỉnh có tin, không còn `other`). Không AC nào của issue này đổi.

- RED: các test đếm 5 hàng thành phố mỗi cấp, test head 0005, test seed API dùng `other` đỏ.
- GREEN: sửa kỳ vọng theo mã nơi mới; `uv run pytest -q` → 947 passed; `npx vitest run` → 166 passed.

## Đợt 2026-11-13 — #293 bộ chọn cấp bậc thành `<select>`

Lý do: #293 đổi hàng nút `aria-pressed` thành `<select>` có nhãn. Không AC nào của #163 đổi (mặc định `entry`, đổi cấp cập nhật bảng và biểu đồ cùng lúc, mẫu nhỏ làm mờ như cũ).

- RED: `web/tests/fr33-level-filter.test.tsx` 19/20 đỏ (`Unable to find an accessible element with the role "combobox" and name "Cấp bậc"`); `tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` 1 đỏ (`level-chips.tsx` đã xóa).
- GREEN: `fr33-level-filter` 20/20 xanh; test deploy 6/6 xanh; `npx vitest run` → 197 passed, `uv run pytest -q tests/deploy` → 58 passed. Chi tiết ở `specs/293-bo-loc-dropdown/tdd.md`.

## Đợt 2026-11-13 — #293 sửa theo review

Lý do: dòng chú thích "Mới vào nghề gồm Intern, Fresher và Junior." thành hằng `LEVEL_ENTRY_NOTE` trong `web/lib/labels.ts`; test deploy đọc hằng đó theo dòng `export const` thay cho regex trên `map-screen.tsx`. Test bàn phím của `fr33-level-filter` đổi tên cho đúng việc nó làm (Tab tới ô rồi chọn) và bỏ hai assert thừa. Không AC nào của #163 đổi. Dòng "test deploy 5/5" ở đợt trên là sai số: file có 6 test.

- Đột biến: đổi hằng thành "…Intern, Fresher, Junior và Mid." → `test_gh163_dong_chu_thich_...` đỏ (1 failed, 5 passed); thêm `mid` vào `entry` của `config/rules.toml` → 2 failed, 4 passed. Đã hoàn lại cả hai.
- GREEN: `uv run pytest -q tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` → 6 passed; `fr33-level-filter` xanh.

## Đợt 2026-11-13 (#148)

Lý do: `haido_api/stat_market.py` thêm bảo vệ entry > n cho `newcomer_roles`; phần `city_shares` không đổi.

- RED: không có, không test nào đổi kỳ vọng.
- GREEN: `uv run pytest tests/api/test_fr33_city_shares_level.py tests/api/test_dat20_stat_market.py -q` → 51 passed; `cd web && npx vitest run tests/fr33-level-filter.test.tsx` → 20 passed.

## Đợt 2026-11-15 — gộp main vào #212

Lý do: `fake_market.json` `skill_rates` đổi; `fake_market.py` giữ `city_shares` có `years` của #280. Hành vi của #163 không đổi.

- RED: không có. Hành vi của issue không đổi; test chỉ thêm nguồn `learning_path` vào lời dựng `create_app` (nếu có) hoặc chạy lại trên fixture mới.
- GREEN (chạy lại thật, 2026-11-15): `uv run pytest -q tests/api/test_fr33_city_shares_level.py tests/api/test_ad17_routes.py tests/api/test_ad17_web_fixtures.py tests/api/test_dat20_stat_market.py tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` → 131 passed; toàn bộ `uv run pytest -q` → 1113 passed, web `npm run test` → 221 passed.

## Đợt 2026-11-16 (#111): file dùng chung đổi, hành vi của issue này không đổi

Lý do: nhánh `gh-111-ho-so-ky-nang` sửa file mà issue này từng đụng: `haido_api/fixtures/fake_market.json` (thêm `skill_rates` cho mọi vai trò, #149), `haido_api/schemas/market.py`, `routes/market.py`, `market_source.py`, `fake_market.py`, `stat_market.py` (chữ ký `skill_rates` nhận `have`, #149), `haido_api/main.py` và `tests/api/test_ad17_routes.py` (route `role-for-title`, #150), `docs/api/*`. Các thay đổi chỉ chạm `skill-rates` và route mới; `city-shares`, `newcomer-roles`, `skills` và khóa trình duyệt không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi.
- GREEN: `uv run pytest -q` → 1018 passed, 217 skipped; `cd web && npx vitest run` → 21 files, 281 passed; `tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.

## Đợt 2026-11-16 (theo #101)

Lý do: #101 sửa `haido_core/steps/aggregate.py`, `haido_core/db/snapshot_store.py` (`replace_stats` bắt buộc nhận `skill_rates`), `haido_core/db/tables.py`; ô theo nhóm cấp được dùng lại để tính tỷ lệ kỹ năng nhưng cách lọc cấp không đổi. `tests/db/test_fr33_stat_city_shares_level.py` đổi kỳ vọng head Alembic từ 0008 sang 0009. Không thêm hành vi mới nào của issue này, không AC nào đổi.

Chạy lại thật sau thay đổi (đợt 2 của #101): `uv run pytest tests/domain/test_fr33_aggregate_level.py tests/steps/test_fr33_aggregate_level_step.py tests/db/test_fr33_stat_city_shares_level.py tests/db/test_dat20_stat_tables.py -q` → **40 passed**. Toàn bộ `uv run pytest -q` → **1194 passed**.

## Đợt 2026-11-17 (#166): file dùng chung đổi, hành vi của issue này không đổi

Lý do: #166 (hình response `skill-roles`) sửa file mà issue này từng đụng: `haido_api/market_source.py`, `fake_market.py`, `stat_market.py`, `routes/market.py`, `schemas/market.py`, `fixtures/fake_market.json`, `docs/api/*`, `tests/api/test_fr33_city_shares_level.py` (lời dựng `create_app`). Thay đổi: `city-shares` theo cấp không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #166 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `t166_test`) → 1510 passed, không skip; `cd web && npx vitest run` → 22 files, 293 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Đợt 2026-11-17 (#166, đợt 2 theo review): file dùng chung đổi lần nữa, AC của issue này không đổi

Lý do: #166 đợt 2 (cỡ mẫu `skill_count` của `skill_rate`, `mentioned` theo mọi cấp, `data.level`, prod chọn nguồn `stat`) sửa thêm `haido_api/fake_market.py`, `fixtures/fake_market.json`, `schemas/market.py`, `routes/market.py`. `city-shares` dùng `composition_share` theo `n` của ô, không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi. RED của #166 đợt 2 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx166_test`, không skip) → 1538 passed; `cd web && npx vitest run` → 22 files, 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Chạy lại (2026-11-17, #302)

#302 sửa `config/rules.toml` (`[sources].auto` thêm `topcv`, `config_version` lên `2026-11-17.1`), `tests/core/test_ad10_rules_config.py` và `tests/steps/test_ad4_ingest.py` (ví dụ nguồn chạy tay đổi từ `topcv` sang `linkedin`). Không đổi scenario của issue này.

- `uv run pytest -q` → 1018 passed, 217 skipped.

## Đợt 2026-11-17 (#151, #106, #103): file dùng chung đổi, AC của issue này không đổi

Lý do: tỷ lệ kỹ năng thật (#151), phép 2 `select_cell` (#106) và ràng buộc lớp đọc (#103) sửa file mà issue này từng đụng:

  - `haido_api/stat_market.py` (thêm `skill_rates` thật, đọc `stat_skill_rates`);
  - `docs/api/envelope-meta.md` (mô tả bản thật của `skill-rates`);

Hành vi và AC của issue này không đổi: thay đổi chỉ thêm (phương thức `skill_rates` thật, trường `order` có mặc định, một biến môi trường ở prod, một đoạn tài liệu); `city_shares`, `newcomer_roles`, `learning_path`, `skill_roles` của `StatMarket` giữ nguyên. Chi tiết: `specs/151-ty-le-ky-nang-that/plan.md`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #151, #106, #103 nằm ở `specs/151-ty-le-ky-nang-that/tdd.md`, `specs/106-chon-o-quay-ve/tdd.md`, `specs/103-api-doc-ty-le-that/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed; `cd web && npx vitest run` → 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

Cập nhật sau review (đợt 2, 2026-11-17): trong `StatMarket` chỉ `skill_rates` đổi thêm (404 khi ô không có hàng tỷ lệ, `n_scanned` nhất quán, chữ nhãn); hành vi và AC của issue này vẫn không đổi. RED và GREEN: `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.

## Đợt 2026-11-17 (#314): màn Bản đồ có lối 3D

Lý do: #314 sửa `web/app/components/map/map-screen.tsx` (lối 3D mặc định trên màn rộng có WebGL) và `view-switch.tsx` (nút 3D bật được). Bộ lọc vai trò, cấp bậc, số năm và cách gọi `city-shares` không đổi; lối 3D dựng từ cùng `buildCitySharesView`. Không AC nào của issue này đổi.

- RED: không có test nào của issue này đỏ.
- GREEN: `npx vitest run` → 27 files, 342 passed (jsdom không có WebGL nên các test cũ vẫn chạy ở lối 2D).

## Đợt 2026-11-17 (#316): màn Bản đồ có panel bên phải và lối 3D CSS

Lý do: #316 sửa `web/app/components/map/map-screen.tsx`: bố cục hai cột (panel "Tin <vai trò> nằm ở đâu" và "Nguồn và lưu ý" bên phải), lối 3D dựng bằng CSS 3D. Bộ lọc và cách gọi `city-shares` không đổi. Không AC nào của issue này đổi.
- Sửa test `fr33-level-filter.test.tsx` ("mờ theo n của cấp đã chọn"): panel bên phải nhắc lại câu cỡ mẫu nhỏ nên tìm trong biểu đồ 2D (`within(figure)`); điều test kiểm không đổi.

- GREEN: `npx vitest run` → 27 files, 347 passed.

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`, `haido_api/stat_market.py`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #324 (2026-11-19): câu chữ trên màn viết lại

Lý do: #324 viết lại chữ hiển thị bằng tiếng Việt dễ hiểu (bỏ nhãn `n = `, "snapshot", "entry-level"; câu thiếu mẫu "Mới có X tin, cần ít nhất 30"; khung nguồn "Đang xem", "Cập nhật", tên nguồn). File của issue này bị đụng: `web/lib/city-shares-view.ts`. Số, thứ tự và ẩn số theo ngưỡng không đổi. Câu trong scenario của `spec.md` đã sửa theo câu mới; ý của AC giữ nguyên (người dùng đồng ý 2026-11-19).

- RED và GREEN: `specs/324-cau-chu-de-hieu/tdd.md` (RED 42 failed / 299 passed; GREEN 357 passed, chạy `npx vitest run` từ PowerShell).

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `config/rules.toml`, `docs/api/envelope-meta.md`, `docs/api/openapi.json`, `haido_api/fixtures/fake_market.json`, `haido_api/stat_market.py`, `haido_core/config.py`, `haido_core/db/snapshot_store.py`, `haido_core/db/tables.py`, `haido_core/steps/aggregate.py`, `tests/api/test_dat20_stat_market.py`, `tests/api/test_fr33_city_shares_level.py`, `tests/core/test_ad10_rules_config.py`, `tests/db/test_dat20_stat_tables.py`, `tests/db/test_fr33_stat_city_shares_level.py`, `web/lib/city-shares.ts`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. Riêng `tests/core/test_ad10_rules_config.py`: `rules.toml` không còn `theta_core`/`theta_common` nên `BASE` dùng `theta_version`, và các ca kiểm θ cũ (thiếu khóa, giá trị ngoài [0, 1], `theta_common > theta_core`) đã chuyển sang `tests/core/test_gh102_theta_dong_bang.py`, nay kiểm trên `config/theta.toml`. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.
