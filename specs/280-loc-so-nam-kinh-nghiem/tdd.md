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
