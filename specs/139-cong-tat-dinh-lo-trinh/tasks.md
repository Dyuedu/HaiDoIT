# Tasks: Cổng tất định cho thứ tự lộ trình

**Input**: `specs/139-cong-tat-dinh-lo-trinh/`. Test viết trước, chạy đỏ, ghi `tdd.md`.

## Phase 1: Test

- [x] T001 [US1] Test phép 8: đồ thị mẫu, xáo đầu vào, bốn tầng, tổ tiên, cạnh thắng chặng, lô, kiểm đầu vào, hai `PYTHONHASHSEED` (`tests/domain/test_fr22_order_path.py`)
- [x] T002 [US1, US2] Test cổng: bản giả phải FAIL, bản thật PASS, hết hạn mục `FR-22` (AC2) FAIL, sổ hoãn thật, CI có `FR-22` (`tests/tools/test_fr22_tat_dinh.py`)
- [x] T003 Chạy hai file test, ghi RED vào `tdd.md`

## Phase 2: Code

- [x] T004 [US1] `haido_core/domain/path_order.py`
- [x] T005 [US1] `tools/gates/check_gates.py`: đồ thị mẫu, probe tiến trình con, PASS hoặc FAIL kèm hits, in lời hoãn AC2
- [x] T006 [US2] `tools/gates/deferred.json`: mục `FR-22` đổi hạn sang 2026-12-13, chỉ còn AC2
- [x] T007 [US1] `.github/workflows/ci.yml`: `--require` thêm `FR-22`

## Phase 3: Kiểm

- [x] T008 Ghi GREEN vào `tdd.md`
- [x] T009 Kiểm đột biến (bỏ từng tầng, đảo tỷ lệ, bỏ kéo tổ tiên, bỏ cạnh), ghi bảng vào `tdd.md`
- [x] T010 `uv run pytest -q`, `uv run ruff check .`, `check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22`, `alembic heads`

## Phase 4: Đợt 2, sửa theo review (2026-11-16)

- [x] T011 Test trước: kiểu sai của `order_path`, bản giả cho từng phép kiểm của cổng, lời nhắc AC2 qua `main()`, lỗi tiếng Việt của probe, fixture hạn 2099; ghi RED vào `tdd.md`
- [x] T012 `haido_core/domain/path_order.py`: kiểm kiểu, kiểm miền `rate` trước `isfinite`
- [x] T013 `tools/gates/check_gates.py`: probe ép UTF-8, `main()` in lời nhắc khi PASS và không ném `UnicodeEncodeError`
- [x] T014 `tools/gates/deferred.json`: ghi chú không phụ thuộc ngày
- [x] T015 Kiểm đột biến cho chính cổng, giả ngày 2026-11-23 và 2026-12-14, ghi GREEN vào `tdd.md`

## Ngoài phạm vi

- [ ] AC2: mở rộng cổng cho mức khớp, tín hiệu, câu Insights, hạn 2026-12-13
- [ ] Nối đồ thị #96 và θ #102, đưa vào API: #213, #216
