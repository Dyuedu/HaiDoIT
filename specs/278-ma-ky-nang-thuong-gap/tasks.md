# Tasks: Mã kỹ năng cho mọi kỹ năng tin hay nhắc tới

**Input**: `specs/278-ma-ky-nang-thuong-gap/` (spec.md, plan.md, data-model.md, research.md)

Test đứng trước code. Mỗi test mới phải đỏ trước khi có code (ghi trong tdd.md).

## Phase 1: Tests (RED)

- [x] T001 `tests/domain/test_gh278_vocab.py`: AC1 (673 khóa có mã hoặc có lý do loại trừ; bộ kiểm khóa trùng, thiếu lý do, khóa thuộc từ vựng), AC2 (cặp Anh/Việt, từng dòng quyết định, một mã không tách đôi, ba khóa trùng đã chuyển, mã ghép), `scan_skip`, version đổi, 225 mã cũ còn, 40 mã mới, chặn mạng
- [x] T002 `tests/tools/test_gh278_skill_gaps.py`: `summarize` (gộp dạng bỏ dấu, một lần mỗi tin, thẻ ghép là có mã, tỷ lệ theo vai trò), `remap`, `--after`, số liệu snapshot 2026-11-20
- [x] T003 `tests/steps/test_gh278_skill_gaps_db.py` (Postgres): `counted_postings`, `raw_skills`, `collect`, chỉ-đọc (SQL chụp được toàn SELECT, kho không đổi)

## Phase 2: Implementation (GREEN)

- [x] T010 `haido_core/vocab/skills_seed.json`: 40 mã mới, bí danh, thẻ ghép, `scan_skip`, sửa `solid`, `version` = `seed-2026-11-23`; chuyển ba khóa trùng + `tu duy logic`
- [x] T011 `haido_core/vocab/skills_excluded.json`, `haido_core/vocab/skills.py`: 158 dòng loại trừ; `load_exclusions`, `parse_exclusions`
- [x] T012 `tools/vocab/skill_gaps.py`: đưa vào repo; thêm `remap` và `--after`
- [x] T013 `web/tests/fixtures/skills.json`: sinh lại từ `GET /api/v1/skills`
- [x] T014 Sửa test cũ bị đổi kỳ vọng vì từ vựng lớn lên; ghi từng file trong tdd.md
- [x] T015 `docs/data/vocabulary.md`: từ vựng lớn lên thế nào, danh sách loại trừ, `scan_skip`, chạy `skill_gaps.py` trên VPS, bảng "trước"
- [x] T016 Chạy toàn bộ: `uv run pytest -q`, `uv run ruff check .`, `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24`; ở `web/`: `npx vitest run`, `npx tsc --noEmit`, `npx eslint .`
- [x] T017 Kiểm đột biến (bỏ một bí danh đã duyệt, xóa lý do loại trừ, bỏ một từ `scan_skip`, giữ phiên bản cũ, cho phép ánh xạ gọi mạng): mỗi cái phải làm một test đỏ; ghi trong tdd.md
- [x] T018 Cập nhật spec của #205, #283, #166, #207, #149 (đợt TDD có ngày; plan/tasks nếu file đổi)

## Phase 3: Sau merge

- [x] T030 (review 2026-11-23) Test trước, rồi sửa: `remap` nhận đầu ra của script + `--min-postings`; `_strings` tách dấu phẩy; `ai/ml` neo vị trí + kiểm khi nạp; `scan_skip` thêm 11 từ; khôi phục câu "Phát triển API bằng Docker"; test tên vai trò trong `test_fr13_skill_seed.py`; docs và spec cũ (#150, #166, #205, #283)
- [x] T031 (review 2026-11-23) Đột biến cho mục 1, 2, 3, 5 (ghi trong tdd.md)

- [ ] T020 Sau deploy, chạy lại `tools/vocab/skill_gaps.py` trên prod (lệnh ở `docs/data/vocabulary.md`) và điền cột "sau" theo vai trò vào `docs/data/vocabulary.md`
