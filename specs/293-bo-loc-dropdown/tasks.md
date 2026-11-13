# Tasks: Bộ lọc bản đồ chọn bằng dropdown

**Input**: `specs/293-bo-loc-dropdown/` (spec.md, plan.md, data-model.md)

Test đứng trước code. Mỗi test mới phải đỏ trước khi có code (ghi trong tdd.md).

## Phase 1: Tests (RED)

- [x] T001 `web/tests/helpers/filters.ts`: hàm `roleSelect()`, `levelSelect()`, `yearsSelect()`, `pick(user, select, label)` dùng `userEvent.selectOptions`
- [x] T002 `web/tests/fr33-filter-selects.test.tsx`: nhãn hiện, `combobox` có tên, option và thứ tự, mặc định, không `optgroup`, không `aria-pressed`, mô tả của ô Cấp bậc và Số năm, chọn lại cùng giá trị không gọi lại, class bố cục (`min-h-target`, lưới một cột rồi ba cột); không có test Tab
- [x] T003 `web/tests/fr33-map-screen.test.tsx`: đổi vai trò bằng `<select>`, bỏ response muộn, lỗi và 404 vẫn đổi được, thứ tự Tab (Tab giữa ba ô còn ở `fr33-role-chips-new-roles`)
- [x] T004 `web/tests/fr33-level-filter.test.tsx`, `fr33-years-filter.test.tsx`, `fr33-role-chips-new-roles.test.tsx`: chuyển sang `<select>`; giữ đủ hành vi cũ
- [x] T005 Chạy, ghi RED vào `tdd.md`

## Phase 2: Implementation (GREEN)

- [x] T010 `web/app/components/map/filter-select.tsx`
- [x] T011 `web/app/components/map/map-screen.tsx` dùng `FilterSelect`; xóa `role-chips.tsx`, `level-chips.tsx`, `years-chips.tsx`; sửa chú thích `web/lib/labels.ts`
- [x] T012 Chạy test, ghi GREEN vào `tdd.md`
- [x] T013 Kiểm trình duyệt thật (Edge headless) ở 1280×900 và 360×640, ghi số đo vào `tdd.md`
- [x] T014 Cập nhật spec của #163, #280, #284 (spec/plan/tasks/tdd, đợt mới có ngày)
- [x] T015 `npm run lint`, `npm run test`, `npm run build`, `uv run pytest -q tests/deploy`, `check_gates.py`

## Phase 3: Đợt 2 — sửa theo review (2026-11-13)

- [x] T020 Test chốt AC 3 trong `fr33-filter-selects` (class ô chọn, `min-w-[`, `globals.css`), assert nhãn hiện không `sr-only`/`hidden`; thứ tự option viết cứng; bỏ assert thừa `.not.toBe`
- [x] T021 Đổi tên test bàn phím của `fr33-level-filter`: Tab tới ô rồi chọn
- [x] T022 Hằng `LEVEL_ENTRY_NOTE` trong `labels.ts`, `map-screen.tsx` dùng, test deploy #163 đọc hằng đó
- [x] T023 `forced-colors:text-[CanvasText]` cho mũi tên của `FilterSelect`
- [x] T024 Chứng minh bằng đột biến, đo lại ở 360×640 (có mũi tên xuống), ghi vào `tdd.md`
- [x] T025 Sửa spec #163 (số test), #284, #285
