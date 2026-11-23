# Tasks: Cache response của API thị trường, xóa theo snapshot

**Input**: Design documents từ `specs/343-cache-response/`

## Phase 1: Tests (RED trước)

- [x] T001 [KB1–KB5] `tests/api/test_gh343_cache_response.py`

## Phase 2: Implementation (GREEN)

- [x] T002 [KB1, KB3, KB4] `haido_api/response_cache.py`
- [x] T003 [KB2] `version()` trong `market_source.py`, `fake_market.py`, `stat_market.py`
- [x] T004 [KB5] `haido_api/main.py`, `deploy/compose.prod.yml`, `deploy/compose.loadtest.yml`
- [x] T005 Ghi đợt mới vào `tdd.md` của #150, #205, #309, #328, #342

## Phase 3: Đo

- [x] T006 [KB6] Chạy lại kịch bản #342 với cache bật, ghi `ket-qua-do.md`

## Dependencies

- T001 → RED
- T002–T004 → GREEN
- T006 sau T004
