# Feature Specification: Bộ lọc bản đồ chọn bằng dropdown

**Feature Branch**: `gh-293-bo-loc-dropdown`

**Created**: 2026-11-13

**Status**: Implemented, chờ merge. Đợt 2 (2026-11-13) sửa theo review: thêm test chốt AC 3, hằng `LEVEL_ENTRY_NOTE`, đo lại ở 360×640.

**Input**: GitHub issue [#293](https://github.com/Dyuedu/HaiDoIT/issues/293) — Pick the map filters from dropdowns instead of chips. Phục vụ story bản đồ [#112](https://github.com/Dyuedu/HaiDoIT/issues/112) và lọc số năm [#280](https://github.com/Dyuedu/HaiDoIT/issues/280). Đụng tới màn do #46, #162, #163, #280, #284, #285 dựng.

## Bối cảnh

Ba bộ lọc của màn Bản đồ (vai trò, cấp bậc, số năm) là ba hàng chip `<button aria-pressed>`. Riêng 18 chip vai trò chiếm khoảng tám hàng ở 360px. Issue đổi ba bộ lọc thành `<select>` gốc có `<label>` hiện; cụm "3D / Biểu đồ 2D / Bảng" vẫn là nút. Vai trò giữ thứ tự `ROLE_OPTIONS` (khớp `config/rules.toml`), không chia nhóm.

Quyết định đã chốt: dùng `<select>` gốc, không dựng listbox hay combobox riêng; chỉ đổi điều khiển, luồng dữ liệu trong `map-screen.tsx` giữ nguyên.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mỗi bộ lọc là một `<select>` có nhãn, mặc định như cũ (Priority: P1)

Người dùng thấy ba ô chọn có nhãn "Vai trò", "Cấp bậc", "Số năm kinh nghiệm". Trang mở ở "Tất cả", "Mới vào nghề", "Mọi số năm".

**Why this priority**: AC 1 của #293.

**Independent Test**: Render `MapScreen` với API giả; `getByRole("combobox", { name })` cho từng ô; danh sách option và thứ tự khớp `ROLE_OPTIONS`, `LEVEL_OPTIONS`, `YEARS_OPTIONS` (đã được test deploy đối chiếu với `config/rules.toml`).

**Acceptance Scenarios**:

1. **Given** trang vừa mở, **When** lượt gọi đầu đi ra, **Then** URL là `/api/v1/city-shares?role=all&level=entry&years=any` và ba ô có giá trị `all`, `entry`, `any`.
2. **Given** ô "Vai trò", **When** đọc các option, **Then** có 18 option theo đúng thứ tự `ROLE_OPTIONS`, "Tất cả" đứng đầu, không có `<optgroup>`.
3. **Given** ô "Cấp bậc" và ô "Số năm kinh nghiệm", **When** đọc các option, **Then** thứ tự là `LEVEL_OPTIONS` (9 option) và `YEARS_OPTIONS` (6 option).
4. **Given** mỗi ô, **When** đọc cây truy cập, **Then** là `<select>` có `<label for>` hiện, không có `aria-pressed`, và không còn nhóm `role="group"` nào tên "Vai trò", "Cấp bậc", "Số năm kinh nghiệm".

---

### User Story 2 - Đổi bộ lọc thì tải lại, biểu đồ và bảng cùng đổi (Priority: P1)

Người dùng chọn "Backend", rồi "Senior", rồi "Tối đa 2 năm" bằng `<select>`.

**Why this priority**: AC 2 của #293: hành vi như chip.

**Independent Test**: `userEvent.selectOptions`, đếm lượt `fetch`, thanh và bảng dựng từ cùng một envelope.

**Acceptance Scenarios**:

1. **Given** màn đã tải, **When** chọn một vai trò, cấp hoặc số năm khác, **Then** gửi đúng một lượt gọi mới mang giá trị đó, hiện "Đang tải số liệu…", rồi thanh và bảng cùng hiện số mới; ô vừa chọn giữ giá trị mới.
2. **Given** màn đã tải, **When** chọn lại đúng giá trị đang chọn, **Then** không có lượt gọi mới.
3. **Given** lượt gọi của lựa chọn cũ chưa về, **When** chọn tiếp một giá trị khác và lượt cũ về muộn, **Then** số của lượt cũ bị bỏ, màn chỉ hiện số của lựa chọn mới nhất.
4. **Given** đã chọn cấp "Senior" và số năm "Tối đa 3 năm", **When** đổi vai trò, **Then** lượt gọi mang vai trò mới, `level=senior`, `years=3`; tương tự khi đổi một trong hai bộ lọc còn lại.
5. **Given** đang tải, hoặc lượt gọi lỗi (kể cả 404 `unknown_cell`), **When** người dùng đổi bộ lọc, **Then** ba ô vẫn đổi được; bấm "Thử lại" giữ nguyên lựa chọn.
6. **Given** cấp "Mới vào nghề" đang chọn, **When** đọc ô "Cấp bậc", **Then** mô tả của ô (`aria-describedby`) là "Mới vào nghề gồm Intern, Fresher và Junior."; ô "Số năm kinh nghiệm" được mô tả bởi "Tính theo số năm tối thiểu tin yêu cầu."
7. **Given** envelope nêu bộ lọc, **When** dựng màn, **Then** tiêu đề biểu đồ, caption bảng và khung "Nguồn và lưu ý" vẫn nêu vai trò, cấp, số năm đã chọn như trước.

---

### User Story 3 - Trên điện thoại ba ô vừa màn hình, bấm và đọc được (Priority: P1)

**Why this priority**: AC 3 của #293 và DoD điện thoại, bàn phím (#137).

**Independent Test**: test web kiểm thứ tự Tab; test web kiểm class và CSS (ô `min-h-target` không tiền tố, không `outline-none` hay `transition-colors`, không `min-w-[` cố định, `globals.css` giữ token 44px và luật `:focus-visible`); kiểm bằng trình duyệt thật (Edge headless) ở 1280×900 và 360×640 (DoD): `scrollWidth ≤ clientWidth`, chiều cao ô ≥ 44px, vòng focus hiện, mũi tên xuống trên ô Vai trò đổi giá trị và gửi lượt gọi mới. Số đo ghi ở `tdd.md`. Đổi giá trị bằng phím mũi tên chỉ kiểm được trong trình duyệt thật, vì jsdom và user-event không cài phím mũi tên của `<select>`; test web chỉ kiểm thứ tự Tab và chọn bằng `selectOptions`.

**Acceptance Scenarios**:

1. **Given** khổ 360px, **When** mở màn, **Then** ba ô xếp thành một cột, trang không cuộn ngang; ở khổ desktop ba ô nằm trên một hàng.
2. **Given** mỗi ô, **When** đo, **Then** cao tối thiểu 44px (`min-h-target`).
3. **Given** bàn phím, **When** Tab từ đầu trang, **Then** lần lượt tới ô Vai trò, Cấp bậc, Số năm kinh nghiệm, cụm Lối xem, rồi từng dòng thành phố; mỗi ô có vòng `:focus-visible` (outline dùng chung của DoD) và đổi giá trị được bằng phím mũi tên.
4. **Given** nhãn dài như "Hạ tầng & IT support", **When** hiện trong ô hẹp, **Then** không làm tràn ngang (ô `w-full`, `min-w-0`).

---

### Điểm còn mở

- Chưa có test e2e tự động trong CI (Playwright) để giữ bố cục và phím mũi tên; quyết định thêm hay không nằm ngoài #293. Hiện bố cục được chốt bằng test class và CSS trong vitest, cộng đo tay bằng Edge headless mỗi đợt.
- #284 và #162 có AC viết "nút"/"chip" cho vai trò. Ngày 2026-11-13 đã ghi chú trên #284 (https://github.com/Dyuedu/HaiDoIT/issues/284#issuecomment-6846775699) và #162 (https://github.com/Dyuedu/HaiDoIT/issues/162#issuecomment-6846776280): ô vai trò thành `<select>` gốc qua #293, ý của AC còn đúng, chỉ chữ "nút"/"chip" lỗi thời. Không sửa chữ AC.

## Edge Cases

- Cụm "Lối xem" (3D / 2D / Bảng) không đổi, vẫn `aria-pressed`.
- Không còn `RoleChips`, `LevelChips`, `YearsChips`; không để mã chết.
- Giá trị của ô luôn là một option trong danh sách; mã lạ không xuất hiện.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Một component `FilterSelect` dùng chung (nhãn hiện, `<select>` gốc, ghi chú tùy chọn nối bằng `aria-describedby`); ba bộ lọc dùng nó với `ROLE_OPTIONS`, `LEVEL_OPTIONS`, `YEARS_OPTIONS`.
- **FR-002**: `map-screen.tsx` giữ luồng `request`, `changeRole/Level/Years`, bỏ response muộn, không gọi lại khi chọn cùng giá trị; chỉ đổi cách dựng điều khiển.
- **FR-003**: Bố cục ba ô: một cột ở điện thoại, ba cột từ `sm`; `min-h-target`; outline focus dùng chung của `globals.css`.

### Key Entities

Không thêm thực thể. Danh sách option vẫn là `web/lib/labels.ts`.

## Success Criteria *(mandatory)*

- **SC-001**: Mọi AC của #293 có test đỏ trước khi có code.
- **SC-002**: Mọi hành vi mà test chip bảo vệ (mặc định, thứ tự, đổi, bỏ response muộn, giữ bộ lọc kia, lỗi, thử lại) vẫn có test, chuyển sang `<select>`.
- **SC-003**: Đo trên trình duyệt thật: không cuộn ngang ở 360px, mọi ô ≥ 44px.

## Assumptions

- `<select>` gốc đủ: danh sách dài nhất là 18 option, dùng picker của hệ điều hành trên điện thoại.
- Thứ tự Tab: ba ô lọc đứng trước cụm Lối xem (trước đây cụm Lối xem nằm giữa vai trò và cấp bậc).
