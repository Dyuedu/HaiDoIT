# Tasks: Tỷ lệ kỹ năng thật theo vai trò và cấp

**Input**: `specs/151-ty-le-ky-nang-that/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test ô đủ mẫu: dòng core/common, thứ tự, meta (`n`, `skill_count`), trong `tests/api/test_fr19_skill_rates_stat.py`
- [x] T002 Test quay về nhóm và `all`, nhãn gọi tên hai ô và n, tỷ lệ Mid trở lên; cỡ mẫu theo `n_scanned`
- [x] T003 Test không tập nào đủ: `null_data`, `group = null`, đếm core `null`; ô cuối không kỹ năng nào được nhắc
- [x] T004 Test `have`, 404 vai trò lạ và không tin, 404 chưa có snapshot, snapshot `open`/thiếu nguồn bị bỏ, `partial` đọc được
- [x] T005 Test AD-7: SQL chỉ `stat_*`, không tổng hợp
- [x] T006 Test deploy `HAIDO_MARKET_SOURCE_SKILL_RATES` (prod `stat`, local `fake`) trong `tests/deploy/test_gh151_ty_le_ky_nang_doc_snapshot_that.py`

## Phase 2: Implementation

- [x] T007 Phép 2 ở `haido_core/domain/cells.py` (#106)
- [x] T008 `StatMarket.skill_rates` trong `haido_api/stat_market.py`
- [x] T009 `deploy/compose.prod.yml`
- [x] T010 `docs/api/envelope-meta.md`
- [x] T011 Kiểm web: response thật qua `isSkillRatesEnvelope`; cập nhật `specs/` của các issue cũ có file chung

## Phase 3: Sửa theo review (2026-11-17)

- [x] T012 Test (RED trước): ô không hàng tỷ lệ là 404; `n_scanned` không thống nhất là `RuntimeError`; ô đủ mẫu mọi kỹ năng hiếm; nhãn và tỷ lệ Mid trở lên đúng từng chữ; AD-7 mở rộng; route chưa có số thật 404 `unknown_cell`
- [x] T013 Mutation: đọc `job_*` và dùng `n` thay `n_scanned`, test phải đỏ đúng lý do, rồi khôi phục file
- [x] T014 `haido_core/domain/cells.py` (`sample_noun`, làm tròn nửa lên), `haido_api/stat_market.py` (404, nhất quán `n_scanned`)
- [x] T015 Web: `rows` rỗng với `core_size = 0` đọc được, màn hiện câu giải thích (`web/lib/skill-rates.ts`, `skill-profile-view.ts`, `skill-profile-screen.tsx`, `web/tests/fr19-skill-profile.test.tsx`)
