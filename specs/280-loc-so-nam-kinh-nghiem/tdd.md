# TDD: Lọc bản đồ theo số năm kinh nghiệm (#280)

## Lệnh test

```bash
export HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test
uv run pytest tests/core/test_ad10_rules_config.py tests/domain/test_fr33_aggregate_years.py \
  tests/steps/test_ad4_ingest.py tests/steps/test_fr33_aggregate_years_step.py \
  tests/api/test_fr33_city_shares_years.py tests/deploy/test_gh280_bo_loc_so_nam_khop_config.py -q
npx vitest run   # trong web/
```

## Danh sách hành vi

1. `years_options` đọc từ config `[0, 1, 2, 3, 5]`; thiếu hay sai (rỗng, âm, trùng, không tăng, không nguyên, bool, không phải mảng) thì `ConfigError` nêu `years_options`; `config_version` tăng.
2. Mốc `N` đếm cụm có `years_min ≤ N`; mốc `0` chỉ đếm tin không cần kinh nghiệm.
3. `any` ra đúng số như trước khi có bộ lọc; không truyền `years_options` thì chỉ có `any`.
4. Tin không ghi số năm chỉ nằm trong `any`.
5. `years_unstated` của ô là số cụm của (vai trò, cấp, phạm vi) không ghi số năm, giống nhau ở mọi mốc.
6. Cấp và số năm lọc cùng nhau; `seniority_mix` theo tập đã lọc.
7. Mỗi (vai trò, cấp, số năm) có đủ năm dòng, tổng bằng 1; n = 0 rơi vào `unknown`; cửa sổ 60 ngày giữ nguyên; thứ tự đầu vào không đổi kết quả.
8. Ingest chép `years_experience_min` vào `job_posting_facts.years_min`; đổi số năm thì có phiên bản dữ kiện mới.
9. Bước `aggregate` ghi đủ hàng theo `years`, số và `years_unstated` khớp đếm tay.
10. API: không gửi `years` như `any`; mốc trả `data.years`, mã ô `.y<N>`, cả cấp và số năm; giá trị lạ 422 nêu `years`; OpenAPI liệt kê enum, mặc định `any`.
11. API: `years_unstated` theo (vai trò, cấp), `null` ở `any`.
12. API: mẫu nhỏ theo ô của mốc; mốc không có tin là 404 kèm ngày; snapshot mới chưa có hàng mốc thì lùi về snapshot có; không có snapshot nào thì 404 không ngày, thông báo nói "bộ lọc".
13. Route chuyển `years` cho nguồn, mặc định `any`; bản giả có `all/entry/y1`.
14. Web: `YEARS_OPTIONS` = `any` + `years_options`, nhãn tiếng Việt, mặc định `any`.
15. Web: mở ở `years=any`; sáu nút đúng thứ tự, 44px, `aria-pressed`; bấm mốc gửi `years`; giữ cấp và vai trò; dòng tin bị bỏ chỉ khi khác `any`; khung chú thích có "Bộ lọc"; tiêu đề nêu số năm; response muộn bị bỏ; bộ chọn có ở cả hai lối xem.
16. Web: `data.years` lệch hoặc `years_unstated` không phải số đếm khi khác `any` thì không đọc được; view có `yearsLabel`, `unstatedNote`, `caption.filters`.

## RED (2026-11-12)

Chạy thật trên Postgres local (`haido_test`, cổng 5433), code chưa đổi.

- `uv run pytest <6 file> -q` → 3 lỗi collection:
  - `tests/domain/test_fr33_aggregate_years.py`: `TypeError: CountedPosting.__init__() takes 6 positional arguments but 7 were given` (chưa có `years_min`).
  - `tests/api/test_fr33_city_shares_years.py`: `AttributeError: 'RulesConfig' object has no attribute 'years_options'`.
  - `tests/deploy/test_gh280_bo_loc_so_nam_khop_config.py`: `ImportError: cannot import name 'YEARS_CODES'`.
- Ba file còn lại (`test_ad10_rules_config.py`, `test_ad4_ingest.py`, `test_fr33_aggregate_years_step.py`) → **17 failed, 119 passed**: 12 test config (chưa có khóa `years_options`), 2 test ingest (`SourceFactsRow` không nhận số năm, bảng chưa có `years_min`), 3 test bước aggregate (chưa có cột `years`). 119 test cũ vẫn xanh, kể cả khi `BASE` của test config có thêm dòng `years_options`.
- `npx vitest run` (web) → **11 failed, 149 passed**: cả 11 test của `fr33-years-filter.test.tsx` đỏ vì chưa có `DEFAULT_YEARS`/`YEARS_OPTIONS`, chưa có nhóm "Số năm kinh nghiệm", web chưa gửi `years` (helper không có reply cho URL thiếu `years`), client chưa kiểm `data.years`, view chưa có `yearsLabel`. 149 test cũ xanh với helper mới (echo `data.years`) và `buildEnvelope` mới.

## GREEN (2026-11-12)

Thứ tự sửa: config → bảng và migration 0006 → ingest → hàm tổng hợp → bước aggregate → API → web. Chạy lại đúng file test sau mỗi bước.

**Đổi thiết kế trong lúc GREEN.** Bản đầu trả `data.years_unstated: int`. Test `test_fr33_ban_gia_co_moc_1_cho_all_entry_va_so_tin_bi_bo` và 5 test API khác ra 500 `invalid_response`: `Envelope` (AD-17) từ chối "data.years_unstated là số đứng riêng ngoài Stat". Đổi sang `data.years_unstated_cell_id` trỏ tới ô `vn.<role>[.<level>].ynone` trong `meta.cells` (cùng mẫu `total_cell_id`); sửa test API, test web, `envelopes.ts`, helper `fetch.ts` theo tên mới và thêm test `test_fr33_so_tin_bi_bo_nam_trong_meta_cells_khong_la_so_tran_trong_data`. Hành vi người dùng thấy và AC không đổi. Spec, plan, data-model đã ghi lại.

**Test cũ phải sửa vì thêm chiều số năm** (không AC nào đổi):

- `test_dat20_aggregate_step.py`, `test_fr33_aggregate_level_step.py` (#93, #163): helper đọc `stat_*` theo (vai trò, cấp, phạm vi) nay gặp 6 hàng → thêm `years = 'any'`; số hàng nhân `1 + len(years_options)`; `ORDER BY` thêm `years`.
- `test_dat20_cli.py`: `594 ô`/`495 tỷ trọng` → `3564`/`2970`.
- `test_dat20_stat_tables.py`, `test_fr33_stat_city_shares_level.py`: head là 0006; cột và khóa có `years`, `years_unstated`; câu `INSERT` nêu `years`, `years_unstated` (hai cột không có giá trị mặc định).
- `test_dat20_stat_market.py`, `test_fr33_city_shares_level.py`: seed nêu `years = 'any'`; test double `city_shares` nhận `years`.
- `test_ad17_routes.py`: test double nhận `years`; khóa fixture `entry.y1` tách thành `level=entry&years=1`.
- `test_gh163_bo_loc_cap_bac_khop_config.py`: bản giả có thêm khóa `entry.y1`, chỉ so các khóa cấp.
- `test_ad4_snapshot_schema.py`: `job_posting_facts` có thêm `years_min` (số, không phải văn bản JD).
- Web `fr33-level-filter.test.tsx`, `fr33-map-screen.test.tsx`: URL có `&years=any`; thứ tự Tab có thêm sáu nút số năm giữa nút cấp bậc và dòng thành phố.
- Sinh lại `docs/api/openapi.json` (`HAIDO_UPDATE_OPENAPI=1`) và sáu fixture `web/tests/fixtures/city-shares-*.json` từ API giả.

**Test thêm sau code, không có RED riêng:** `tests/db/test_fr33_stat_years.py` (5 test của migration 0006) viết sau khi migration đã có, nên không chạy đỏ trước. Hành vi của migration đã được các test bước aggregate và ingest (đỏ ở RED vì thiếu cột) che một phần; file này thêm kiểm khóa chính, không có giá trị mặc định và hạ cấp.

| Lệnh | Kết quả |
|---|---|
| `uv run pytest <6 file của danh sách hành vi> -q` | xanh |
| `uv run pytest tests/db/test_fr33_stat_years.py -q` | 5 passed |
| `uv run pytest -q` (Postgres local) | **770 passed** |
| `PYTHONHASHSEED=0 uv run pytest -q -m determinism` | 6 passed |
| `PYTHONHASHSEED=1 uv run pytest -q -m determinism` | 6 passed |
| `uv run ruff check .` | All checks passed |
| `uv run python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7` | 8 pass, 2 skip (FR-22, FR-24, có hạn), 0 fail |
| `uv run alembic heads` | `0006_haido_years_filter (head)` |
| `npx vitest run` (trong `web/`) | **160 passed** |
| `npm run lint` | sạch |
| `npx tsc --noEmit` | sạch |
| `npm run build` | thành công |

Đo cỡ thật: `aggregate_city_shares` với 6500 tin giả, cấu hình thật → 0,96 giây và 3564 ô (trước: 0,28 giây, 594 ô), bộ nhớ đỉnh khoảng 2 MB (`tracemalloc`). Giới hạn 512 MB của container kho không bị đe dọa.

## REFACTOR

Tách thân đếm cũ thành `_count_subset` (không đổi logic), `aggregate_city_shares` chỉ còn kiểm đầu vào, lọc tập con theo mốc và gắn `years_unstated`. Không đổi `CellKey`, không đổi `REGISTRY.md`.

## Đợt 2026-11-13 — #283 giải số năm ở bước ingest

Lý do: #283 sửa `haido_core/db/scraper_source.py` (đọc thêm mô tả, `read_facts`), `haido_core/steps/ingest.py` (phân loại lúc
ingest, làm mới nhãn của tin trong cửa sổ), `haido_core/db/snapshot_store.py`, `haido_core/db/tables.py` (năm cột nhãn,
migration 0007). `years_min` nay là số đã giải: số tháng của nguồn → giá trị bước trích → luật đọc mục yêu cầu; "không yêu
cầu kinh nghiệm" → 0. Tin trong cửa sổ có dữ kiện cũ được làm mới tại S, nên tỷ lệ "không ghi số năm" giảm ngay ở lượt đêm
đầu sau deploy thay vì giảm dần trong 60 ngày. AC của #280 không đổi.

- RED: test của #280 không đổi kỳ vọng ngoài `test_fr33_migration_0006_noi_tiep_0005_va_la_head_duy_nhat` (head nay là 0007).
- GREEN: `tests/steps/test_ad4_ingest.py`, `tests/steps/test_fr33_aggregate_years_step.py`, `tests/db/test_fr33_stat_years.py`
  xanh; `uv run pytest -q` → 887 passed.

## Đợt 2026-11-13 — #284 thêm bảy vai trò

Lý do: số ô và tỷ trọng mỗi snapshot theo số vai trò: 18 × 6 × 9 × 6 = 5832 ô, 18 × 5 × 9 × 6 = 4860 tỷ trọng (trước 3564 và 2970). Bộ lọc số năm không đổi.

- RED: `tests/test_dat20_cli.py` và `test_dat20_determinism_hai_lan_aggregate_ra_cung_hang` đỏ vì số hàng.
- GREEN: đổi số hàng mong đợi; `uv run pytest -q` → 908 passed.

## Đợt 2026-11-13 — #285 34 tỉnh, Remote, Nước ngoài

Lý do: #285 đổi mã nơi (ô theo mốc số năm chỉ có ở nơi có tin; `years_unstated` của nơi không có ô 'không ghi số năm' là 0). Không AC nào của issue này đổi.

- RED: test đếm hàng theo mốc số năm, test head 0006 đỏ; lỗi `KeyError` khi tỉnh chỉ có tin ghi số năm (đã có test riêng ở #285).
- GREEN: sửa kỳ vọng theo mã nơi mới; `uv run pytest -q` → 947 passed; `npx vitest run` → 166 passed.

## Đợt 2026-11-12 — #145, #146 thêm phép đọc người mới vào `stat_market.py`

Lý do: #145, #146 thêm `StatMarket.newcomer_roles`, `_national_cells`, `_cell_meta` và hằng `ENTRY` vào `haido_api/stat_market.py`. `city_shares` và các hàm `_latest_readable`, `_shares`, `_cells`, `_sources` không đổi; `newcomer_roles` dùng lại `_latest_readable(conn, "entry")`.

- RED: không test nào của issue này đổi kỳ vọng.
- GREEN: `tests/api/test_dat20_stat_market.py`, `tests/api/test_fr33_city_shares_level.py`, `tests/api/test_fr33_city_shares_years.py` xanh trong lượt `uv run pytest -q` (Postgres) → 959 passed.

## Đợt 2026-11-12 — #147 export hàm kiểm hợp đồng của `web/lib/city-shares.ts`

Lý do: #147 thêm `export` cho `isRecord`, `isNonEmptyString`, `isStringArray`, `isCount`, `readErrorBody`, `isMeta` để màn người mới dùng chung luật đọc envelope. Thân hàm không đổi; `fetchCityShares` không đổi.

- RED: không test nào của issue này đổi kỳ vọng.
- GREEN: các test `fr33-*` và `ad17-city-shares-client` xanh trong lượt `npx vitest run` → 189 passed; `npx tsc --noEmit` sạch.

## Đợt 2026-11-13 — T020: lượt đêm đầu tiên trên production

Lý do: kiểm T020 sau deploy. Không đổi code, chỉ ghi kết quả chạy thật trên VPS (`ssh haidoit`).

- Log `/opt/haidoit/logs/daily-2026-11-13.log`, bước kho bắt đầu lúc 02:28:06 (+07:00) với image `sha-f0de523269d550a7b7c9973c7e4e1583a265a17d` (merge của PR #290):
  - `alembic upgrade head`: không lỗi.
  - Ingest snapshot 2026-11-13: 7 lượt chạy, 2566 tin, 2566 quan sát, 71 dữ kiện mới.
  - Lifecycle: 6534 tin (`config_version 2026-11-13.3`).
  - Aggregate: 8180 ô, 7208 tỷ trọng thành phố.
  - Publish: `Đã chốt snapshot 2026-11-13 (partial); nguồn lỗi: topdev.`
  - Không có traceback hay dòng lỗi nào của bước kho. Cả lượt kết thúc lúc 02:33:17.
- Snapshot 2026-11-13 được chốt ở trạng thái `partial`, không phải `published`: lúc lấy danh sách, TopDev bị ngắt kết nối (`ConnectionResetError(104)`, `listed=132 complete=False`). `partial` là trạng thái đọc được của API (`READABLE = ("published", "partial")`), và `meta.sources_failed` báo `topdev`.
- Lệnh `curl http://127.0.0.1:8000/api/v1/city-shares?role=all&level=entry&years=1` chạy trong VPS trả HTTP 200:
  - `meta.snapshot_date = 2026-11-13`, `snapshot_status = partial`, `sources_failed = ["topdev"]`.
  - `data.years = "1"`, `data.level = "entry"`, `data.role = "all"`.
  - `data.years_unstated_cell_id = "vn.all.entry.ynone"`, có trong `meta.cells`, `n = 143`.
  - `data.total_cell_id = "vn.all.entry.y1"`, `n = 550`; 22 dòng nơi.
- Kết quả: T020 đạt.

## Đợt 2026-11-13 (#148)

Lý do: `haido_api/stat_market.py` thêm bảo vệ entry > n cho `newcomer_roles`; phần `city_shares` không đổi.

- RED: không có, không test nào đổi kỳ vọng.
- GREEN: `uv run pytest tests/api/test_fr33_city_shares_years.py tests/api/test_dat20_stat_market.py -q` → 45 passed; `cd web && npx vitest run tests/fr33-years-filter.test.tsx` → 11 passed.
