# Implementation Plan: Lọc bản đồ theo cấp bậc

**Branch**: `gh-163-loc-ban-do-theo-cap-bac` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/163-loc-ban-do-theo-cap-bac/spec.md`

## Summary

Danh sách cấp lọc và nhóm `entry` nằm trong `config/rules.toml` (#134). Bước `aggregate` ghi thêm, cho mỗi cấp lọc, tỷ trọng thành phố và ô; `stat_city_shares` có thêm cột `seniority` trong khóa (migration 0005). `GET /api/v1/city-shares` nhận `level` tùy chọn và trả `data.level`. Web thêm bộ chọn cấp bậc, mặc định `entry`, đổi cấp thì gọi lại API và bỏ response muộn theo cùng mẫu đổi vai trò.

## Technical Context

**Language/Version**: Python 3.13 (core, API), TypeScript 5 với Next.js 16 và React 19 (web)

**Primary Dependencies**: SQLAlchemy, Alembic, FastAPI, Pydantic; Vitest và Testing Library cho web. Không thêm gói.

**Storage**: PostgreSQL, schema `haido`. Một migration mới: thêm `seniority` vào khóa của `stat_city_shares`.

**Testing**: `uv run pytest <file> -q` cho từng file (Postgres: `HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test`); `npm --prefix web run test` cho web.

**Target Platform**: bước đêm trên VPS, API FastAPI, web Next.js

**Project Type**: web-service và web app (pipeline, API, web)

**Performance Goals**: số lần hỏi `ClusterPopulation` vẫn là (vai trò × phạm vi × cấp thô); cấp nhóm cộng từ cấp thô, không hỏi thêm.

**Constraints**: một transaction; cửa sổ 60 ngày, cụm (#100), nguồn bị loại (#263), `stat_sources` (#259) giữ nguyên. `min_sample`, θ, coverage notes không đổi (#260). Mẫu nhỏ do `suppression_for` quyết theo n của ô (thành phố, vai trò, cấp). Không sửa `_bmad-output/`, `scraper/`, `haido_core/domain/classify.py`, `.github/workflows/deploy.yml`. Hợp đồng API tương thích ngược khi không gửi `level`.

**Scale/Scope**: 11 vai trò (cả `all`) × 9 cấp lọc × 6 phạm vi = 594 ô, 495 dòng tỷ trọng mỗi snapshot.

## Constitution Check

- AD-5, AD-7: API đọc `stat_*` theo khóa, không cộng lại từ bảng tin; web không tự tính số, không so n với ngưỡng.
- AD-10: danh sách cấp và nhóm nằm trong `config/rules.toml`, thiếu khóa thì lỗi tiếng Việt, tăng `config_version`.
- AD-17: số vẫn là `Stat` với `display` do `suppression_for` quyết.
- AD-25: một head Alembic; migration có `downgrade`.
- Test đặt tên có mã FR hoặc AD; test mới phải đỏ trước khi có code.
- Task #164 (tỷ trọng remote/hybrid) nằm ngoài phạm vi.

## Project Structure

### Documentation (this feature)

```text
specs/163-loc-ban-do-theo-cap-bac/
├── plan.md
├── research.md
├── data-model.md
├── spec.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
config/rules.toml
haido_core/config.py
haido_core/domain/aggregate.py
haido_core/steps/aggregate.py
haido_core/db/snapshot_store.py
haido_core/db/tables.py
haido_core/db/migrations/versions/0005_haido_city_share_level.py
haido_api/schemas/market.py
haido_api/market_source.py
haido_api/routes/market.py
haido_api/stat_market.py  (chọn snapshot theo cấp, F1)
haido_api/fake_market.py
haido_api/fixtures/fake_market.json
docs/api/openapi.json
docs/api/envelope-meta.md
web/lib/labels.ts
web/lib/city-shares.ts
web/lib/city-shares-view.ts
web/app/components/map/map-screen.tsx
web/app/components/map/level-chips.tsx
web/tests/fixtures/city-shares-*.json
tests/core/test_ad10_rules_config.py
tests/domain/test_fr33_aggregate_level.py
tests/db/test_fr33_stat_city_shares_level.py
tests/db/test_dat20_stat_tables.py
tests/steps/test_fr33_aggregate_level_step.py
tests/steps/test_dat20_aggregate_step.py
tests/api/test_fr33_city_shares_level.py
tests/api/test_ad17_routes.py
tests/api/test_ad17_web_fixtures.py
tests/api/test_dat20_stat_market.py
tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py
web/tests/fr33-level-filter.test.tsx
web/tests/fr33-map-screen.test.tsx
web/tests/ad17-city-shares-client.test.ts
web/tests/helpers/fetch.ts
web/tests/fixtures/envelopes.ts
```

**Structure Decision**: Hàm thuần ở `haido_core/domain/aggregate.py` nhận danh sách cấp lọc và nhóm; bước `aggregate` đọc chúng từ `RulesConfig`. Route chỉ chuyển `level` cho nguồn (AD-5); `StatMarket` đọc theo khóa (role, level). Web giữ nhãn ở `labels.ts`, không đọc config lúc chạy; test đối chiếu `labels.ts` với `config/rules.toml`.

## Quyết định thiết kế

- Mã cấp lọc: `all`, `entry` (nhóm), `intern`, `fresher`, `junior`, `mid`, `senior`, `lead`, `unknown`. Cấp nhóm và cấp đơn dùng chung cột `seniority`.
- Mã ô theo cấp: `<scope>.<role>.<level>`; cấp `all` giữ `<scope>.<role>` nên response cũ không đổi mã ô.
- `level` thiếu ở route nghĩa là `all`. Web luôn gửi `level`.
- Tham số `level` của route là `Literal` dựng từ config lúc import, nên OpenAPI liệt kê enum và giá trị lạ đi qua trình xử lý 422 chuẩn.
- `data.level` trả lại cấp đã dùng để web đối chiếu như đã đối chiếu `data.role`.
- Vai trò × cấp có n toàn quốc bằng 0 thì `unknown_cell` (như vai trò không có tin).
- Mẫu mặc định `entry` là hằng `DEFAULT_LEVEL` của web (web không đọc config).

## Complexity Tracking

Không có vi phạm cần biện minh.

## Cập nhật 2026-11-13 theo #293

`level-chips.tsx` bị xóa; ô Cấp bậc là `FilterSelect` (`filter-select.tsx`) dựng trong `map-screen.tsx` với `LEVEL_OPTIONS`, dòng chú thích "Mới vào nghề gồm Intern, Fresher và Junior." là prop `note` nối `aria-describedby`. `web/tests/fr33-level-filter.test.tsx`, `web/tests/fr33-map-screen.test.tsx` và `tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` đổi theo. Xem `specs/293-bo-loc-dropdown/`.
