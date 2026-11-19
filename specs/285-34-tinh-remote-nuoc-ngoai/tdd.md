# TDD: Đếm theo 34 tỉnh, thành, cộng Remote và Nước ngoài (#285)

## Lệnh test

```bash
export HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test
uv run pytest tests/domain/test_gh285_city.py tests/domain/test_gh285_aggregate_sparse.py \
  tests/deploy/test_gh285_noi_khop_config.py tests/steps/test_gh285_ingest_city.py tests/db/test_gh285_fact_city.py -q
npx vitest run tests/fr33-provinces.test.tsx   # trong web/
```

## Danh sách hành vi

1. Tên tỉnh cũ, thành phố, khu hay gặp quy về đúng một trong 34 tỉnh, thành mới; cụm sớm nhất thắng khi nhiều tỉnh.
2. `location` không nêu tỉnh thì đọc dòng địa chỉ của JD (dòng có "địa điểm", "địa chỉ", "nơi làm việc", "work location"…, cộng dòng kế); chữ ngoài các dòng đó không đặt nơi.
3. Thứ tự: tỉnh ở `location` → nước ngoài ở `location` → tỉnh ở địa chỉ → nước ngoài ở địa chỉ → remote → không xác định.
4. 34 tỉnh trong `classify.toml` và `[labels.city]`; nhãn web của 34 tỉnh trùng nhãn config.
5. `job_posting_facts.city` (migration 0008); ingest lưu; aggregate dùng khi `classify_version` khớp.
6. `stat_*` chỉ có hàng của nơi có tin cộng `always_cities`; tỷ trọng cộng bằng 1.
7. Web: ba thanh, chú thích Remote/Nước ngoài/Không xác định, bảng có các tỉnh khác nơi nhiều tin đứng trước.

## RED (2026-11-13)

Chạy thật, code và config chưa đổi.

- `uv run pytest tests/domain/test_gh285_city.py -q` → **lỗi collection**: `ImportError: cannot import name 'address_text'`.
- `uv run pytest tests/domain/test_gh285_aggregate_sparse.py tests/deploy/test_gh285_noi_khop_config.py tests/steps/test_gh285_ingest_city.py tests/db/test_gh285_fact_city.py -q` → **10 failed, 2 passed**: hàm tổng hợp chưa nhận `always_cities` (3), config chưa có 34 tỉnh, `always_cities`, bản giả còn `other` (3), ingest chưa lưu nơi, aggregate còn ghi `other` (2), chưa có migration 0008 (2). Hai test xanh sẵn: nhãn 3 thành phố hiện có đều có mã, nhãn web của 5 mã hiện có khớp config.
- `npx vitest run tests/fr33-provinces.test.tsx` → **3 failed**: `LEGEND_CITIES` còn `other`, bảng chưa có tỉnh khác, mã tỉnh chưa có nhãn.

## GREEN (2026-11-13)

Thứ tự: config (`rules.toml` 37 nơi và `always_cities`, `classify.toml` 34 tỉnh, `abroad_phrases`, `remote_phrases`, `[address]`, `config.py`) → `posting_text.address_text`, `PostingFacts.address_text`, `classify._city` → migration 0008, `snapshot_store`, `ingest` → `aggregate_city_shares(always_cities=…)`, bước `aggregate` → web (`labels.ts`, `city-shares-view.ts`) → bản giả và fixture web.

Phát hiện và sửa trong lúc GREEN:

- Cổng FR-25/31/47 bắt chữ cấm "tin giả" trong câu chú thích "theo số tin giảm dần" của `labels.ts`; viết lại câu.
- Web coi mọi envelope thiếu dòng Remote/Nước ngoài là không đọc được: snapshot tính trước #285 (có `other`, không có hai dòng đó) sẽ hỏng tới lượt đêm đầu sau deploy. `REQUIRED_CITIES` nay chỉ là ba thành phố và không xác định; Remote, Nước ngoài có thì hiện; `other` của snapshot cũ hiện trong bảng với nhãn "Khác".
- Chạy lại snapshot 12/11 trên bản sao: `aggregate` ném `KeyError: ('all', 'all', 'nghe_an')` — tỉnh có tin ghi số năm mà không có tin nào không ghi thì không có ô "không ghi số năm" để tra. Thêm `test_gh285_tinh_chi_co_tin_ghi_so_nam_van_tong_hop_duoc_theo_moc`, chạy **đỏ** (`KeyError: ('all', 'all', 'hai_phong')`), sửa bằng `unstated.get(..., 0)`, xanh.

Test cũ đổi vì không còn "Khác" và mỗi bộ lọc không còn đủ 5 hàng (không AC nào của issue cũ đổi, xem mục #112 ở spec.md):

| Test | Issue | Vì sao |
|---|---|---|
| `tests/core/test_ad10_rules_config.py` (`BASE` có `always_cities`; bảng nhãn nơi; 2 ca lỗi bảng nhãn) | #6, #280 | Mã bắt buộc là `always_cities`; Huế là tỉnh hợp lệ; 37 nơi |
| `tests/domain/test_ad2_classify.py::test_ad2_nhieu_thanh_pho_lay_cum_xuat_hien_truoc` | #3 | Hải Phòng → "Hải Phòng", Remote → "Remote" |
| `tests/domain/test_ad2_registry.py` | #3 | `PostingFacts.address_text` |
| `tests/db/test_ad4_snapshot_schema.py`, bốn test kiểm head | #6, #93, #163, #280, #283 | Cột `city`; head 0008 |
| `tests/api/test_dat20_stat_market.py`, `test_fr33_city_shares_level.py`, `test_fr33_city_shares_years.py`, `test_ad17_routes.py` | #93, #163, #280 | Seed dùng `hai_phong` thay `other`; bản giả có 7 dòng |
| `tests/steps/test_dat20_aggregate_step.py`, `test_fr33_aggregate_level_step.py`, `test_fr33_aggregate_years_step.py`, `test_dat20_api_end_to_end.py`, `test_gh284_aggregate_vai_tro_moi.py`, `tests/test_dat20_cli.py` | #93, #163, #280, #284 | Mỗi bộ lọc 6 nơi luôn có + vn; tỉnh khác chỉ khi có tin; số hàng 6804/5832 trong test CLI |
| `web/tests/fr33-city-shares-view.test.ts`, `fr33-map-screen.test.tsx` | #162, #163 | Chú thích là Remote, Nước ngoài, Không xác định nơi làm việc; Hải Phòng ở bảng; thứ tự Tab có thêm một dòng |

## Trước/sau trên snapshot 12/11/2026 của bản sao local

| | Trước (`2026-11-13.2`) | Sau (`2026-11-13.3`) |
|---|---|---|
| Cụm IT không xác định nơi | 237 / 3748 (6,3%) | **48 / 3748 (1,3%)** |
| "Khác" | 47 | — (không còn mã này) |
| Tỉnh có tin | 3 thành phố | 25 tỉnh, thành; Nước ngoài 16; Remote 1 |
| Hàng `stat_cells` / `stat_city_shares` | 5832 / 4860 | 8180 / 7208 (×1,4; SC-002 đạt) |

Tỉnh nhiều tin nhất ngoài ba thành phố: Hải Phòng 38, Bắc Ninh 31, Đồng Nai 27, Hưng Yên 25, Phú Thọ 14. Remote chỉ 1 vì phần lớn tin remote vẫn nêu một tỉnh (tỉnh thắng theo spec). `ingest` 17,3 giây (phân loại lại 6255 dữ kiện), `aggregate` 8,8 giây.

Chrome headless, 360 × 780, `http://localhost:3000`: 18 chip vai trò, `scrollWidth` 360 / `clientWidth` 360 ở lối Biểu đồ và lối Bảng; Fullstack · Mới vào nghề ở lối Bảng có 8 dòng: Hà Nội, TP.HCM, Đà Nẵng, Đồng Nai, Thái Nguyên, Làm từ xa (Remote), Nước ngoài, Không xác định nơi làm việc.

## Kết quả cuối

| Lệnh | Kết quả |
|---|---|
| `uv run pytest -q` (Postgres local) | **947 passed** |
| hai lượt `-m determinism` | 6 passed mỗi lượt |
| `uv run ruff check .` | All checks passed |
| cổng `--require AD-1 AD-17 AD-25 AD-2 AD-7` | 8 pass, 2 skip, 0 fail |
| `uv run alembic heads` | `0008_haido_fact_city (head)` |
| `npx vitest run` (web) | **166 passed** |
| `npm run lint`, `npx tsc --noEmit`, `npm run build` | sạch |

## Đợt 2 — 2026-11-12, câu giới thiệu trang Bản đồ

Lý do: câu "Hà Nội, TP.HCM và Đà Nẵng chiếm bao nhiêu phần tin tuyển dụng IT…" của `web/app/page.tsx` không còn đúng khi bảng liệt kê mọi tỉnh; người dùng chốt sửa.

- RED: thêm `web/tests/fr33-map-page-intro.test.tsx`; `npx vitest run tests/fr33-map-page-intro.test.tsx` → **1 failed** (`expected 'Hà Nội, TP.HCM và Đà Nẵng chiếm bao n…' to contain 'từng tỉnh, thành'`).
- GREEN: câu mới "Tin tuyển dụng IT của vai trò bạn chọn chia theo từng tỉnh, thành, làm từ xa và nước ngoài, kèm cỡ mẫu, nguồn và ngày snapshot." Sửa trong lúc GREEN: regex của test tìm "tin" viết thường, câu mới viết hoa "Tin"; đổi sang tìm "tuyển dụng IT của vai trò bạn chọn". `npx vitest run` → **167 passed**; `lint`, `tsc`, `build` sạch.

## Đợt 2026-11-12 — #147 export hàm kiểm hợp đồng của `web/lib/city-shares.ts`

Lý do: #147 thêm `export` cho `isRecord`, `isNonEmptyString`, `isStringArray`, `isCount`, `readErrorBody`, `isMeta` để màn người mới dùng chung luật đọc envelope. Thân hàm không đổi; `fetchCityShares` không đổi.

- RED: không test nào của issue này đổi kỳ vọng.
- GREEN: các test `fr33-*` và `ad17-city-shares-client` xanh trong lượt `npx vitest run` → 189 passed; `npx tsc --noEmit` sạch.

## Đợt 2026-11-13 — #293 bộ lọc thành `<select>`

Lý do: `web/tests/fr33-map-screen.test.tsx` (nơi #285 có test dòng tỉnh, Remote, Nước ngoài) chọn vai trò bằng `<select>` thay cho chip. Không AC nào của #285 đổi.

- RED: 20/32 test của `fr33-map-screen` đỏ vì không tìm thấy `combobox` "Vai trò"; test về nơi (Remote, Nước ngoài, tỉnh) đỏ chỉ ở bước chọn vai trò.
- GREEN: 32/32 xanh; `npx vitest run` → 197 passed.

## Đợt 2026-11-13 — #293 sửa theo review

Lý do: `web/tests/fr33-map-screen.test.tsx` bỏ hai assert `.not.toBe(...)` thừa ngay sau `.toBe(...)` của cùng ô chọn. Không AC nào của #285 đổi; hành vi nơi (Remote, Nước ngoài, tỉnh) không đụng tới.

- RED: không có (chỉ bỏ assert không thể đỏ riêng).
- GREEN: `npx vitest run` toàn bộ xanh (số đếm ở `specs/293-bo-loc-dropdown/tdd.md`, đợt 2).

## Đợt 2026-11-15 — gộp main vào #212

Lý do: `fake_market.json` đổi `skill_rates` (phần `city_shares` của #285 giữ nguyên); `test_ad17_web_fixtures.py` còn khớp sáu fixture city-shares.

- RED: không có. Hành vi của issue không đổi; test chỉ thêm nguồn `learning_path` vào lời dựng `create_app` (nếu có) hoặc chạy lại trên fixture mới.
- GREEN (chạy lại thật, 2026-11-15): `uv run pytest -q tests/api/test_ad17_web_fixtures.py tests/api/test_fr33_city_shares_level.py tests/api/test_fr33_city_shares_years.py tests/api/test_dat20_stat_market.py` → 85 passed; toàn bộ `uv run pytest -q` → 1113 passed.

## Đợt 2026-11-16 (#111): file dùng chung đổi, hành vi của issue này không đổi

Lý do: nhánh `gh-111-ho-so-ky-nang` sửa file mà issue này từng đụng: `haido_api/fixtures/fake_market.json` (thêm `skill_rates` cho mọi vai trò, #149), `haido_api/schemas/market.py`, `routes/market.py`, `market_source.py`, `fake_market.py`, `stat_market.py` (chữ ký `skill_rates` nhận `have`, #149), `haido_api/main.py` và `tests/api/test_ad17_routes.py` (route `role-for-title`, #150), `docs/api/*`. Các thay đổi chỉ chạm `skill-rates` và route mới; `city-shares`, `newcomer-roles`, `skills` và khóa trình duyệt không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi.
- GREEN: `uv run pytest -q` → 1018 passed, 217 skipped; `cd web && npx vitest run` → 21 files, 281 passed; `tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.

## Đợt 2026-11-16 (theo #101)

Lý do: #101 sửa `haido_core/steps/ingest.py` (dữ kiện mang thêm `vocab_version`; nhãn thành phố không đổi), `haido_core/steps/aggregate.py`, `haido_core/db/snapshot_store.py` (`FactVersion` có trường mới ở cuối, sau `city`), `haido_core/db/tables.py`. `tests/db/test_gh285_fact_city.py` đổi kỳ vọng head Alembic từ 0008 sang 0009. Không thêm hành vi mới nào của issue này, không AC nào đổi.

Chạy lại thật sau thay đổi (đợt 2 của #101): `uv run pytest tests/steps/test_gh285_ingest_city.py tests/db/test_gh285_fact_city.py tests/domain/test_gh285_aggregate_sparse.py -q` → **8 passed**. Toàn bộ `uv run pytest -q` → **1194 passed**.

## Đợt 2026-11-17 (#166): file dùng chung đổi, hành vi của issue này không đổi

Lý do: #166 (hình response `skill-roles`) sửa file mà issue này từng đụng: `haido_api/fixtures/fake_market.json` (chỉ thêm mục `skill_roles`), `tests/api/test_fr33_city_shares_level.py`, `test_fr33_city_shares_years.py`, `test_dat20_stat_market.py`, `tests/steps/test_dat20_api_end_to_end.py`, `tests/steps/test_gh284_aggregate_vai_tro_moi.py` (lời dựng `create_app` thêm `skill_roles`). Thay đổi: mã nơi (34 tỉnh, Remote, Nước ngoài) không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #166 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `t166_test`) → 1510 passed, không skip; `cd web && npx vitest run` → 22 files, 293 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Đợt 2026-11-17 (#166, đợt 2 theo review): file dùng chung đổi lần nữa, AC của issue này không đổi

Lý do: #166 đợt 2 (cỡ mẫu `skill_count` của `skill_rate`, `mentioned` theo mọi cấp, `data.level`, prod chọn nguồn `stat`) sửa thêm `haido_api/fixtures/fake_market.json`. Số tin theo tỉnh không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi. RED của #166 đợt 2 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx166_test`, không skip) → 1538 passed; `cd web && npx vitest run` → 22 files, 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Chạy lại (2026-11-17, #302)

#302 sửa `config/rules.toml` (`[sources].auto` thêm `topcv`, `config_version` lên `2026-11-17.1`), `tests/core/test_ad10_rules_config.py` và `tests/steps/test_ad4_ingest.py` (ví dụ nguồn chạy tay đổi từ `topcv` sang `linkedin`). Không đổi scenario của issue này.

- `uv run pytest -q` → 1018 passed, 217 skipped.

## Đợt 2026-11-17 (#151, #106, #103): file dùng chung đổi, AC của issue này không đổi

Lý do: tỷ lệ kỹ năng thật (#151), phép 2 `select_cell` (#106) và ràng buộc lớp đọc (#103) sửa file mà issue này từng đụng:

  - `haido_core/domain/registry.py` (`CellChoice.label` nới thành `str | None`, thêm `CellChoice.order` có mặc định);

Hành vi và AC của issue này không đổi: thay đổi chỉ thêm (phương thức `skill_rates` thật, trường `order` có mặc định, một biến môi trường ở prod, một đoạn tài liệu); `city_shares`, `newcomer_roles`, `learning_path`, `skill_roles` của `StatMarket` giữ nguyên. Chi tiết: `specs/151-ty-le-ky-nang-that/plan.md`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #151, #106, #103 nằm ở `specs/151-ty-le-ky-nang-that/tdd.md`, `specs/106-chon-o-quay-ve/tdd.md`, `specs/103-api-doc-ty-le-that/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed; `cd web && npx vitest run` → 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

Cập nhật sau review (đợt 2, 2026-11-17): trong `StatMarket` chỉ `skill_rates` đổi thêm (404 khi ô không có hàng tỷ lệ, `n_scanned` nhất quán, chữ nhãn); hành vi và AC của issue này vẫn không đổi. RED và GREEN: `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.

## Đợt #324 (2026-11-19): câu chữ trên màn viết lại

Lý do: #324 viết lại chữ hiển thị bằng tiếng Việt dễ hiểu (bỏ nhãn `n = `, "snapshot", "entry-level"; câu thiếu mẫu "Mới có X tin, cần ít nhất 30"; khung nguồn "Đang xem", "Cập nhật", tên nguồn). File của issue này bị đụng: `web/lib/city-shares-view.ts`, `web/app/page.tsx`. Số, thứ tự và ẩn số theo ngưỡng không đổi. Hành vi và AC của issue này không đổi.

- RED và GREEN: `specs/324-cau-chu-de-hieu/tdd.md` (RED 42 failed / 299 passed; GREEN 357 passed, chạy `npx vitest run` từ PowerShell).

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `config/rules.toml`, `haido_api/fixtures/fake_market.json`, `haido_core/config.py`, `haido_core/db/snapshot_store.py`, `haido_core/db/tables.py`, `haido_core/steps/aggregate.py`, `tests/api/test_dat20_stat_market.py`, `tests/api/test_fr33_city_shares_level.py`, `tests/core/test_ad10_rules_config.py`, `tests/db/test_ad4_snapshot_schema.py`, `tests/db/test_dat20_stat_tables.py`, `tests/db/test_fr33_stat_city_shares_level.py`, `tests/db/test_fr33_stat_years.py`, `tests/db/test_gh283_facts_labels.py`, `tests/db/test_gh285_fact_city.py`, `web/lib/city-shares.ts`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. Riêng `tests/core/test_ad10_rules_config.py`: `rules.toml` không còn `theta_core`/`theta_common` nên `BASE` dùng `theta_version`, và các ca kiểm θ cũ (thiếu khóa, giá trị ngoài [0, 1], `theta_common > theta_core`) đã chuyển sang `tests/core/test_gh102_theta_dong_bang.py`, nay kiểm trên `config/theta.toml`. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.
