# Feature Specification: Toàn cảnh thị trường đọc số thật của snapshot

**Feature Branch**: `gh-327-tong-quan-thi-truong` (làm cùng #327)

**Created**: 2026-11-19

**Status**: Implemented, chờ merge. Test Postgres chạy trên CI.

**Input**: GitHub issue [#328](https://github.com/Dyuedu/HaiDoIT/issues/328) — Return the market overview from the published snapshot. Task phục vụ story #326.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Số thật, không bảng mới (Priority: P1)

**Independent Test**: `tests/api/test_ad22_market_overview_stat.py` (cần `HAIDO_TEST_DATABASE_URL`).

**Acceptance Scenarios**:

1. **Given** snapshot đã công bố có ô `stat_cells` của mọi vai trò, mọi nơi và các mốc số năm của `vn.all`, **When** gọi `GET /api/v1/market-overview` với nguồn `stat`, **Then** số tin của vai trò, của nơi, của người mới bằng `n` của các ô đó, giống `city-shares` và `newcomer-roles`. (AC 1)
2. **Given** các ô mốc số năm (`years = 0…5`) và `years_unstated`, **When** dựng, **Then** các phần cộng lại bằng `n` toàn quốc. (AC 2)
3. **Given** `deploy/compose.prod.yml`, **When** đọc `HAIDO_MARKET_SOURCE_NEWCOMER_ROLES`, **Then** là `stat`, nên production đọc số thật. (AC 3)
4. **Given** chưa có snapshot nào đọc được, **When** gọi, **Then** 404 `unknown_cell`.

## Requirements *(mandatory)*

- **FR-001**: `StatMarket.market_overview` đọc một lượt các ô cần dùng (`_overview_rows`) rồi gọi `build_market_overview` của #327.
- **FR-002**: Snapshot là bản đã công bố mới nhất có `stat_city_shares` ở cấp `all` (`_latest_readable(conn, "all")`), như bản đồ mọi cấp.

## Success Criteria *(mandatory)*

- **SC-001**: CI chạy `tests/api/test_ad22_market_overview_stat.py` trên Postgres thật và xanh.
