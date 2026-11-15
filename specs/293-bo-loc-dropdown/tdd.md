# TDD: Bộ lọc bản đồ chọn bằng dropdown

Issue: [#293](https://github.com/Dyuedu/HaiDoIT/issues/293). Ngày 2026-11-13.

## Lệnh test

```text
cd web && npx vitest run                       # toàn bộ web (14 file)
cd web && npx vitest run tests/fr33-filter-selects.test.tsx tests/fr33-map-screen.test.tsx \
  tests/fr33-level-filter.test.tsx tests/fr33-years-filter.test.tsx tests/fr33-role-chips-new-roles.test.tsx
uv run pytest -q tests/deploy                  # test đối chiếu labels.ts với config
```

## Danh sách hành vi và test

| AC / Scenario | Test |
|---|---|
| AC1 · US1.1 mặc định `all`, `entry`, `any`, URL đầu có đủ ba | `fr33-filter-selects` (mặc định), `fr33-map-screen` "mở trang", `fr33-level-filter`, `fr33-years-filter` |
| AC1 · US1.2, US1.3 option và thứ tự khớp `labels.ts`, vai trò không `optgroup` | `fr33-filter-selects`, `fr33-role-chips-new-roles` (18 option), `fr33-level-filter` (9), `fr33-years-filter` (6) |
| AC1 · US1.4 `<select>` có `<label for>` hiện, không `aria-pressed`, không còn nhóm chip | `fr33-filter-selects` |
| AC2 · US2.1 đổi bộ lọc gửi một lượt, thanh và bảng cùng đổi | `fr33-filter-selects` (đổi cả ba ô), `fr33-level-filter`, `fr33-years-filter` |
| AC2 · US2.2 chọn lại cùng giá trị không gọi lại | `fr33-filter-selects` |
| AC2 · US2.3 bỏ response muộn | `fr33-map-screen`, `fr33-filter-selects`, `fr33-level-filter`, `fr33-years-filter` |
| AC2 · US2.4 giữ hai bộ lọc còn lại | `fr33-level-filter`, `fr33-years-filter`, `fr33-filter-selects` |
| AC2 · US2.5 đổi được khi đang tải và sau lỗi; Thử lại giữ lựa chọn | `fr33-filter-selects`, `fr33-map-screen` (404, 502), `fr33-level-filter` |
| AC2 · US2.6 ghi chú "Mới vào nghề gồm Intern, Fresher và Junior." nối `aria-describedby` | `fr33-filter-selects`, `fr33-level-filter`; `tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` (chữ khớp config) |
| AC2 · US2.7 tiêu đề, caption, khung nguồn nêu bộ lọc | `fr33-level-filter`, `fr33-years-filter`, `fr36-snapshot-caption` (không đổi, vẫn xanh) |
| AC3 · US3.1, US3.4 lưới một cột rồi ba cột, ô `w-full min-w-0` | `fr33-filter-selects` (class) + đo trình duyệt thật |
| AC3 · US3.2 ô cao ≥ 44px | `fr33-filter-selects` (`min-h-target`) + đo trình duyệt thật |
| AC3 · US3.3 Tab, vòng focus | `fr33-map-screen` (thứ tự Tab), `fr33-role-chips-new-roles` (Tab giữa ba ô) + đo trình duyệt thật |

Các test chip bị chuyển, không xóa: `aria-pressed` của chip → `selectedLabel(select)`; `user.click(chip)` → `userEvent.selectOptions`; "Tab đi qua 18 nút" → "Tab đi qua ba ô"; kiểm `flex-wrap` → kiểm lưới và `w-full`. `fr36-snapshot-caption.test.tsx` không hỏi chip nên không đổi.

## Đợt 1 — 2026-11-13: chuyển chip sang `<select>`

**RED** (chạy `npx vitest run` khi `RoleChips`, `LevelChips`, `YearsChips` còn nguyên):

- `Test Files 5 failed | 9 passed (14)`, `Tests 58 failed | 139 passed (197)`.
- Theo file: `fr33-filter-selects` 8/8 đỏ (mới), `fr33-role-chips-new-roles` 3/3, `fr33-years-filter` 8/11, `fr33-level-filter` 19/20, `fr33-map-screen` 20/32 đỏ.
- Lý do: `TestingLibraryElementError: Unable to find an accessible element with the role "combobox" and name "Vai trò"` (32 lần), `"Cấp bậc"` (17), `"Số năm kinh nghiệm"` (8); riêng test Tab của `fr33-map-screen` đỏ vì danh sách điểm dừng vẫn là từng chip.
- `uv run pytest -q tests/deploy` ở thời điểm sau khi xóa `level-chips.tsx`: 1 failed, 57 passed (`test_gh163_dong_chu_thich_nhom_entry...` đọc `level-chips.tsx`, `FileNotFoundError`). Test được sửa để đọc prop `note` của ô "Cấp bậc" trong `map-screen.tsx`.

**GREEN** (thêm `filter-select.tsx`, `map-screen.tsx` dùng nó, xóa ba file chip):

- `npx vitest run` → `Test Files 14 passed (14)`, `Tests 197 passed (197)`.
- `uv run pytest -q tests/deploy` → 58 passed.
- `npm run lint` sạch; `npm run build` thành công.

## Kiểm bằng trình duyệt thật

Edge headless (playwright-core), API giả `uvicorn haido_api.main:app --port 8012`, web `next dev -p 3012` với `API_BASE_URL=http://localhost:8012`. jsdom không có layout nên phần này đo thật. Script: `scratchpad\br293.js`; ảnh: `scratchpad\shots293\` (`desktop-default.png`, `phone-default.png`, `*-focus-1..3.png`, `*-longlabel.png`, `*-notfound.png`, `*-table.png`).

| Đo | 1280×900 | 360×780 (cảm ứng, DPR 2) |
|---|---|---|
| `scrollWidth` / `clientWidth` | 1280 / 1280 | 360 / 360 |
| `scrollWidth` sau chọn "Hạ tầng & IT support" | 1280 / 1280 | 360 / 360 |
| Bố cục ba ô | một hàng, mỗi ô rộng 403px | một cột, mỗi ô rộng 312px |
| Cao ô Vai trò / Cấp bậc / Số năm | 44 / 44 / 44 px | 44 / 44 / 44 px |
| Tab tới từng ô | lần Tab thứ 6, 7, 8 | lần Tab thứ 6, 7, 8 |
| Vòng focus của từng ô | `solid 2px rgb(197,243,106)`, lệch 2px (`#C5F36A`) | như desktop |
| Mũi tên xuống trên ô Vai trò | đổi "Tất cả" thành "Nhúng", tải lại | như desktop |

Chọn bằng `selectOption`:

- "Backend": tiêu đề biểu đồ "BACKEND · MỚI VÀO NGHỀ · MỌI SỐ NĂM".
- Rồi "Senior", rồi "Tối đa 2 năm": bản giả không có ô Backend·Senior nên màn hiện lỗi `unknown_cell` "Không có ô thống kê nào cho vai trò, cấp bậc và số năm đã chọn." kèm ngày snapshot 03/11/2026; ba ô vẫn đổi được (đúng như chip, bản giả chỉ có `all/entry` cho các mốc năm).
- Chọn "Mọi cấp bậc" và "Mọi số năm" với Backend: thanh hiện "BACKEND · MỌI CẤP BẬC · MỌI SỐ NĂM", Hà Nội 38,9% · 61 tin.
- Chọn "Tất cả", "Mới vào nghề", "Tối đa 1 năm": tiêu đề biểu đồ và `<caption>` của bảng đều "Tất cả · Mới vào nghề · Tối đa 1 năm"; khung "Nguồn và lưu ý" nêu "Bộ lọc" (ảnh `desktop-default.png`).

Phát hiện khi đo: lần đầu vòng focus đọc ra màu `rgb(230,237,243)` vì class `transition-colors` làm `outline-color` chạy chậm từ màu chữ sang `#C5F36A`. Đổi thành `transition-[border-color]` thì vòng focus đúng màu ngay.

Dọn: tắt cả hai server, xóa `web/AGENTS.md` và `web/.vitest/` do `next dev` và `vitest` sinh ra.

## Đợt 2 — 2026-11-13 — sửa theo review

Lý do: review tìm ra AC 3 (bố cục, 44px, vòng focus) không có test tự động: bốn đột biến sống sót qua mọi test (`focus-visible:outline-none` trên ô, đưa lại `transition-colors`, `sm:min-h-target`, `min-w-[480px]` trên lưới). Thêm test chốt, sửa các điểm yếu còn lại (F2 đến F8). Không thêm Playwright hay job CI: e2e là điểm còn mở trong `spec.md`.

Việc đã làm:

- F1: `fr33-filter-selects` thêm 3 test: (a) class ô chọn có `min-h-target` không tiền tố, không `outline-none`/`focus:outline-none`/`focus-visible:outline-none`/`transition-colors`/`transition-all`; (b) từ ô chọn lên tới `body` không có class `min-w-` trừ `min-w-0`; (c) đọc `web/app/globals.css`: `--spacing-target: 44px`, `--color-primary: #c5f36a`, luật `:focus-visible` có `outline: 2px solid var(--color-primary)` và `outline-offset: 2px`.
- F2: test của `fr33-level-filter` đổi tên "Tab tới bộ chọn cấp bậc rồi chọn giá trị"; giờ thật sự dùng `user.tab()` từ ô Vai trò. Đổi bằng phím mũi tên chỉ kiểm trong trình duyệt thật (bảng dưới).
- F3: hằng `LEVEL_ENTRY_NOTE` trong `web/lib/labels.ts`, `map-screen.tsx` dùng; test deploy #163 đọc hằng đó. Chú thích số năm không có test deploy đọc nên giữ nguyên.
- F4: test "nhãn hiện" khẳng định class của `<label>` không có `sr-only` và không có `hidden` (kể cả `sm:hidden`).
- F5: `fr33-filter-selects` viết cứng mã và nhãn của vai trò (thứ tự `config/rules.toml`, `all` đầu), cấp bậc, số năm; không import `labels.ts`.
- F6: bỏ 4 assert `.not.toBe(...)` thừa (2 ở `fr33-level-filter`, 2 ở `fr33-map-screen`).
- F7: mũi tên của `FilterSelect` thêm `forced-colors:text-[CanvasText]` (Tailwind 4.3.4 có biến thể `forced-colors:`).
- F8: sửa số test của #163, câu về file phủ Tab và "không gọi lại" trong `plan.md` và `tasks.md`, Status của #284 và #285.

**RED** (đột biến trên mã sản phẩm, chạy `npx vitest run tests/fr33-filter-selects.test.tsx`; trước khi có test mới cả bốn đột biến đầu đều xanh 8/8):

| Đột biến | Kết quả |
|---|---|
| `focus-visible:outline-none` trên ô | 1 failed, 10 passed (test class ô chọn) |
| `transition-colors` thay `transition-[border-color]` | 1 failed (test class ô chọn) |
| `sm:min-h-target` thay `min-h-target` | 1 failed (test class ô chọn) |
| `min-w-[480px]` trên lưới | 1 failed (test `min-w-`) |
| `<label>` thêm `sr-only` (F4) | 1 failed (test nhãn hiện) |
| `globals.css` `--spacing-target: 40px` | 1 failed (test `globals.css`) |
| `globals.css` `outline-offset: 0` | 1 failed (test `globals.css`) |
| Đảo `embedded` và `ai_ml` trong `labels.ts` (F5) | 1 failed (test thứ tự viết cứng) |
| Hằng `LEVEL_ENTRY_NOTE` lệch config (F3) | pytest #163: 1 failed, 5 passed |
| `entry` của config thêm `mid` (F3) | pytest #163: 2 failed, 4 passed |

Mọi đột biến đã hoàn lại (`git status` chỉ còn các file sửa có chủ đích).

**GREEN**: `npx vitest run` → 14 file, 200 passed (197 + 3 test mới); `uv run pytest -q tests/deploy` và các lệnh còn lại: xem mục "Số đếm cuối" bên dưới.

### Đo lại bằng trình duyệt thật (đợt 2)

Edge headless, API giả `uvicorn --port 8014`, `next dev -p 3014` với `API_BASE_URL=http://localhost:8014`; script `scratchpad\br293b.js` (khổ phone đổi từ 360×780 sang 360×640 theo DoD); ảnh `scratchpad\shots293b\`.

| Đo | 1280×900 | 360×640 (cảm ứng, DPR 2) |
|---|---|---|
| `scrollWidth` / `clientWidth` | 1280 / 1280 | 360 / 360 |
| sau chọn "Hạ tầng & IT support" | 1280 / 1280 | 360 / 360 |
| cuối lượt (cả chế độ Bảng) | 1280 / 1280 | 360 / 360 |
| Bố cục, rộng mỗi ô | một hàng, 403px | một cột, 312px |
| Cao ô Vai trò / Cấp bậc / Số năm | 44 / 44 / 44 px | 44 / 44 / 44 px |
| Tab tới từng ô | lần 6, 7, 8 | lần 6, 7, 8 |
| Vòng focus | `solid 2px rgb(197,243,106)`, lệch 2px | như desktop |
| **ArrowDown trên ô Vai trò đang focus** | giá trị "Tất cả" thành "Nhúng"; lượt gọi 4 thành 5, URL `/api/v1/city-shares?role=embedded&level=entry&years=any` | như desktop |

Bằng chứng phím mũi tên: ArrowDown trên `<select>` đang focus đổi giá trị và phát đúng một lượt gọi mới. Dọn: tắt hai server, xóa `web/AGENTS.md`; DB tạm `fx293_test` đã xóa.

Số đếm cuối đợt 2: `npm run lint` sạch; `npm run test` 14 file, 200 passed; `npm run build` thành công; `uv run pytest -q tests/deploy` 58 passed; `check_gates.py --require ...` 10 gates: 8 pass, 2 skipped, 0 failed.
