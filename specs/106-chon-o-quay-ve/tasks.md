# Tasks: Phép 2, chọn ô và thứ tự quay về

**Input**: `specs/106-chon-o-quay-ve/`

**Tests**: Viết trước theo `tdd.md`.

## Phase 1: Test

- [x] T001 Test ô đủ mẫu giữ nguyên, ngưỡng đúng bằng `min_sample`, trong `tests/domain/test_ad2_select_cell.py`
- [x] T002 Test thứ tự `cấp → nhóm → all`, nhãn gọi tên hai ô và n, tỷ lệ Mid trở lên ở bước cuối (FR-19)
- [x] T003 Test không ô nào đủ: ô cuối kèm nhãn; ô thiếu coi như 0
- [x] T004 Test AD-6: phạm vi, vai trò, snapshot không đổi; nhánh trước, nhánh sau
- [x] T005 Test AD-2: cùng truy vấn cùng kết quả; một đối tượng và một lô; đầu vào sai là `ValueError`
- [x] T006 Test AD-17: quyết định theo `sample_n`

## Phase 2: Implementation

- [x] T007 `haido_core/domain/registry.py`: `CellChoice.label: str | None`, `CellChoice.order`
- [x] T008 `haido_core/domain/cells.py`: `CellSelector`, `CellStats`
- [x] T009 `haido_core/domain/REGISTRY.md`: ghi thân hàm phép 2
