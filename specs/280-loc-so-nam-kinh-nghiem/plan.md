# Implementation Plan: Lọc bản đồ theo số năm kinh nghiệm

**Branch**: `gh-280-loc-nam-kinh-nghiem` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/280-loc-so-nam-kinh-nghiem/spec.md`

## Summary

Ingest chép `years_experience_min` của scraper vào `job_posting_facts.years_min`. Bước `aggregate` lọc tập tin đã đếm theo từng mốc số năm rồi chạy lại đúng phép đếm hiện có (`ClusterPopulation`) trên tập con, nên cửa sổ ngày, quy tắc cụm và quy tắc cấp lọc không có bản thứ hai. `stat_cells` và `stat_city_shares` thêm cột `years` vào khóa (migration 0006), `stat_cells` thêm `years_unstated`. API nhận `years`, trả `data.years` và `data.years_unstated`. Web thêm bộ chọn số năm cùng mẫu với bộ chọn cấp bậc của #163.

## Technical Context

**Language/Version**: Python 3.13 (core, API), TypeScript 5 với Next.js 16 và React 19 (web)

**Primary Dependencies**: SQLAlchemy, Alembic, FastAPI, Pydantic; Vitest và Testing Library. Không thêm gói.

**Storage**: PostgreSQL schema `haido`. Migration `0006_haido_years_filter`.

**Testing**: `uv run pytest <file> -q` (Postgres: `HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test`); `npm --prefix web run test`.

**Constraints**: `CellKey` và chữ ký phép 3 trong `REGISTRY.md` không đổi: lọc số năm làm ở hàm tổng hợp, trước khi giao cho `ClusterPopulation`. Phân loại (`classify.py`) không đổi. `min_sample`, θ, `coverage_notes` không đổi (#260). API tương thích ngược khi không gửi `years`. Không sửa `scraper/`, `_bmad-output/`.

**Scale/Scope**: 11 vai trò × 9 cấp lọc × 6 mã số năm × 6 phạm vi = 3564 ô; 2970 dòng tỷ trọng mỗi snapshot (gấp 6 lần hiện tại).

## Constitution Check

- AD-2: không thêm phép mới, không đổi chữ ký trong `REGISTRY.md`; phân loại vẫn không đọc JD, không gọi mô hình.
- AD-5, AD-7: API đọc `stat_*` theo khóa; `years_unstated` do `aggregate` ghi, API không đếm.
- AD-10: mốc số năm nằm trong `config/rules.toml`, có kiểm và tăng `config_version`.
- AD-17: số vẫn là `Stat`, `display` do `suppression_for` theo n của ô đang chọn.
- AD-25: một head Alembic, có `downgrade`.

## Project Structure

### Documentation (this feature)

```text
specs/280-loc-so-nam-kinh-nghiem/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
config/rules.toml
haido_core/config.py
haido_core/db/scraper_source.py
haido_core/db/snapshot_store.py
haido_core/db/tables.py
haido_core/db/migrations/versions/0006_haido_years_filter.py
haido_core/domain/population.py          (CountedPosting.years_min, mặc định None)
haido_core/domain/aggregate.py
haido_core/steps/ingest.py
haido_core/steps/aggregate.py
haido_api/schemas/market.py
haido_api/market_source.py
haido_api/routes/market.py
haido_api/stat_market.py
haido_api/fake_market.py
haido_api/fixtures/fake_market.json
docs/api/openapi.json
docs/api/envelope-meta.md
web/lib/labels.ts
web/lib/city-shares.ts
web/lib/city-shares-view.ts
web/app/components/map/map-screen.tsx
web/app/components/map/years-chips.tsx    (mới)
web/app/components/map/share-bars.tsx
web/app/components/map/share-table.tsx
web/app/components/map/snapshot-caption.tsx
web/tests/fixtures/*.json, web/tests/fixtures/envelopes.ts
tests/core/test_ad10_rules_config.py
tests/domain/test_fr33_aggregate_years.py            (mới)
tests/steps/test_fr33_aggregate_years_step.py        (mới)
tests/db/test_fr33_stat_years.py                     (mới: migration 0006)
tests/steps/test_ad4_ingest.py, tests/db/test_ad4_snapshot_schema.py
tests/steps/test_dat20_aggregate_step.py, tests/steps/test_fr33_aggregate_level_step.py, tests/test_dat20_cli.py
tests/db/test_dat20_stat_tables.py, tests/db/test_fr33_stat_city_shares_level.py
tests/api/test_dat20_stat_market.py, tests/api/test_fr33_city_shares_level.py
tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py
web/tests/fr33-level-filter.test.tsx, web/tests/fr33-map-screen.test.tsx, web/tests/helpers/fetch.ts
tests/api/test_fr33_city_shares_years.py             (mới)
tests/api/test_ad17_routes.py, tests/api/test_ad17_web_fixtures.py
tests/deploy/test_gh280_bo_loc_so_nam_khop_config.py (mới)
web/tests/fr33-years-filter.test.tsx                 (mới)
```

## Quyết định thiết kế

- Mã số năm: `any` và chuỗi của từng số trong `years_options`. Mã `N` nghĩa là `years_min ≤ N`; tin không ghi số năm chỉ thuộc `any` (AC 3 của #280: bị bỏ và được đếm riêng). Khác `job-hunter` (giữ tin không ghi số năm), xem research.md.
- Mã ô: thêm hậu tố `.y<N>` sau mã cấp; `any` không có hậu tố nên mọi `cell_id` cũ không đổi.
- Số tin bị bỏ là `n` của ô `vn.<role>[.<level>].ynone` trong `meta.cells`, `data` chỉ mang `years_unstated_cell_id` (`CellId`). Bản đầu để số trần trong `data`; `Envelope` của AD-17 từ chối ("số đứng riêng ngoài Stat"), nên đổi theo cùng mẫu `total_cell_id`. Hình dạng `CellMeta` không đổi.
- Lọc trước khi đếm: `aggregate_city_shares` dựng một `ClusterPopulation` cho mỗi tập con theo mốc; cụm lấy nhãn và `years_min` từ tin đại diện như cấp bậc.
- `_latest_readable` chọn snapshot có hàng của đúng (cấp, số năm).
- Bản giả: khóa `city_shares[vai trò][cấp]` cho `any`, khóa `"<cấp>.y<N>"` cho mốc khác.

## Complexity Tracking

Không có vi phạm cần biện minh.

## Cập nhật 2026-11-13 theo #293

`years-chips.tsx` bị xóa; ô Số năm kinh nghiệm là `FilterSelect` (`filter-select.tsx`) trong `map-screen.tsx` với `YEARS_OPTIONS` và dòng chú thích "Tính theo số năm tối thiểu tin yêu cầu." là prop `note`. `web/tests/fr33-years-filter.test.tsx`, `fr33-level-filter.test.tsx`, `fr33-map-screen.test.tsx` đổi theo. Xem `specs/293-bo-loc-dropdown/`.

## Ghi chú 2026-11-13 (#148)

`haido_api/stat_market.py` thêm bảo vệ entry > n trong `newcomer_roles`. Phần `city_shares` của #280 không đổi; không AC nào của #280 đổi.
