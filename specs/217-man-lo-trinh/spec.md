# Feature Specification: Màn lộ trình học theo chặng

**Feature Branch**: `gh-217-man-lo-trinh`

**Created**: 2026-11-25

**Status**: Implemented, chờ merge. 2026-11-25: thêm app demo chạy bằng snapshot thật (`haido_api.demo`, một phần của #216; #216 chưa xong). 2026-11-25 đợt 4: người dùng thấy màn chưa giống roadmap.sh, chọn làm lại theo chủ đề, giữ nền tối.

**Input**: GitHub issue [#217](https://github.com/Dyuedu/HaiDoIT/issues/217) — Show the learning path as stages. Phục vụ story #121 (US-C1). Đọc hình response của #212 (dữ liệu giả; bản thật ở #216). Người dùng chọn giao diện kiểu roadmap.sh (25/11/2026): lấy cách trình bày, không lấy nội dung.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Xem lộ trình theo chặng và đánh dấu kỹ năng đã có (Priority: P1)

Một sinh viên mở `/co-van?role=backend`. Trục giữa là các chủ đề theo thứ tự học, mỗi chủ đề có một cụm ô kỹ năng ở một bên, so le phải trái, nối bằng đường chấm. Họ đánh dấu kỹ năng đã có và thấy chặng sau lên thay.

**Why this priority**: AC 1 của #217; AC 1, 2, 3 của #121.

**Independent Test**: `web/tests/fr22-lo-trinh-hoc.test.tsx`.

**Acceptance Scenarios**:

1. **Given** lộ trình `ready`, **When** mở màn, **Then** mỗi chặng của API là một mục có số chặng và tên chủ đề; kỹ năng trong chặng đúng thứ tự API (cốt lõi trước), mỗi ô có tên ngắn và tỷ lệ; nhóm hiện bằng màu có chú giải và bằng chữ cho trình đọc màn hình; "Kỹ năng nền tảng (cần cho X)" (FR-20) ở ngăn chi tiết và cho trình đọc màn hình.
1a. **Given** chặng `choose_one`, **When** xem, **Then** cụm nằm trong khung "Chọn một"; có một kỹ năng là chặng "Đã xong"; ngăn chi tiết liệt kê "Lựa chọn thay thế".
2. **Given** một kỹ năng chưa có, **When** đánh dấu "Đã có", **Then** nút hiện "Đã có" ngay, hồ sơ trình duyệt được lưu, API được hỏi lại với `have=`, dòng "N/M" lấy từ API. Bỏ đánh dấu thì trở lại. (AC 1)
3. **Given** kỹ năng cuối còn thiếu của chặng đang học, **When** đánh dấu, **Then** chặng đó ghi "Đã xong", chặng sau thành "Đang học" (`aria-current="step"`) và kỹ năng còn thiếu của nó lên khung "Học tiếp" ở đầu màn. (AC 1)
4. **Given** mọi chặng đã xong (`current_stage = null`), **When** xem, **Then** màn nói "Bạn đã đi hết các chặng của lộ trình này.", không chặng nào đang học; "N/M" vẫn đếm kỹ năng.
5. **Given** API trả `have_on_path` và `current_stage`, **When** vẽ, **Then** màn dùng nguyên hai số đó, không tự đếm (AD-22).
6. **Given** URL có `level=senior`, **When** mở, **Then** lộ trình vẫn hỏi `level=entry` (#134); lối về hồ sơ kỹ năng giữ cấp của URL.

### User Story 2 - Trên điện thoại là danh sách (Priority: P1)

**Why this priority**: AC 2 của #217; AC 6 của #121.

**Independent Test**: `web/tests/fr22-lo-trinh-hoc.test.tsx`; Chrome headless 360px.

**Acceptance Scenarios**:

1. **Given** màn hẹp hơn `lg` (1024px), **When** xem, **Then** không đường nối nào hiện, mọi chặng và kỹ năng xếp một cột theo thứ tự API, không cuộn ngang. (AC 2)
2. **Given** trình đọc màn hình, **When** đọc, **Then** đường nối bị ẩn (`aria-hidden`); mỗi kỹ năng chỉ có một nút và một ô tick trong DOM.

### User Story 3 - Mở một kỹ năng để xem chi tiết (Priority: P2)

Kiểu roadmap.sh: bấm một nút mở ngăn chi tiết. Phần màn của AC 1 #218; nội dung (lời dẫn, tài liệu đã rà soát) vẫn là việc của #218.

**Independent Test**: `web/tests/fr22-lo-trinh-hoc.test.tsx`.

**Acceptance Scenarios**:

1. **Given** một nút, **When** bấm, **Then** ngăn mở với tỷ lệ, nhóm, lời dẫn, "Cần học trước", "Học xong thì học được", một tài liệu miễn phí, ô "Tôi đã có kỹ năng này". Không gọi thêm API (FR-23).
2. **Given** ngăn đang mở, **When** bấm Escape hay Đóng, **Then** ngăn đóng, focus về nút đã mở.
3. **Given** `?skill=spring_boot`, **When** mở trang, **Then** ngăn của Spring Boot mở sẵn (#153). Kỹ năng không có trên lộ trình thì nói "… không nằm trên lộ trình của vai trò này."; mã lạ không được in.

### Edge Cases

- `not_ready`: "Lộ trình học có thứ tự cho vai trò này đang được biên soạn." và lối sang hồ sơ kỹ năng (AC 2 của #121).
- 404 `unknown_cell` (chưa có snapshot; prod trước #216): câu của API, không "Thử lại", vẫn có lối sang hồ sơ kỹ năng. Mạng hỏng: có "Thử lại".
- Mọi tỷ lệ `null_data`: mỗi nút ghi "chưa đủ dữ liệu", không %, không nhóm, không câu "Tính trên … tin".
- Cụm một kỹ năng: một cột hẹp; cụm lẻ: ô cuối chiếm cả hàng.
- Không có `role`: dùng vai trò mục tiêu đã lưu (FR-14); chưa có thì mời chọn, không gọi API lộ trình.
- Đang tải lại sau khi đánh dấu: giữ số cũ, thứ tự không nhảy.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Thứ tự, chặng, chặng đang học, "N/M" và tỷ lệ lấy nguyên từ `learning-path` (AD-7, AD-22).
- **FR-002**: Hồ sơ đọc và ghi qua `profile-store.ts` (AD-23); đánh dấu giữ nguyên vai trò và cấp đã lưu.
- **FR-003**: Câu trên màn không chứa số; số ở ô riêng (DEC-6). Số chặng là thứ tự, không phải số thống kê.
- **FR-004**: `fetchLearningPath` từ chối envelope sai hợp đồng, link tài liệu không phải https, hoặc của vai trò hay cấp khác.
- **FR-007**: Nội dung nháp (`haido_api/content/learning_path.json` (chuyển chỗ ở #216)) do nhóm tự soạn, không chép từ roadmap.sh; phủ mọi kỹ năng core và common của Backend (entry) và Data Engineer (mọi cấp) ở snapshot 2026-11-25; snapshot sau có thể thêm kỹ năng chưa có trong nháp.
- **FR-005**: Nút, liên kết và ô tick cao tối thiểu 44px.

- **FR-006** (demo): `haido_api.demo:app` đọc mọi phép từ snapshot thật; lộ trình lấy tỷ lệ, nhóm và ô của `skill-rates` thật, ghép với đồ thị chưa rà soát, kèm lưu ý "bản nháp". Chỉ `deploy/compose.demo.yml` chạy app này; `main:app`, prod và compose.local không đổi (#96, #309).

## Success Criteria *(mandatory)*

- **SC-001**: `cd web && npx vitest run` xanh; `npx tsc --noEmit`, `npm run lint`, `npm run build` xong.
- **SC-002**: Chrome headless 360px: không cuộn ngang, không đường nối; 1024px và 1280px: có đường nối.

## Assumptions

- #121 AC 1 và AC 5 (số thật, thứ tự từ đồ thị đã rà soát) là việc của #213–#216, không phải của màn này.
- "in stages, core before common" của #121: mỗi chủ đề là một chặng, cốt lõi đứng trước trong từng chặng (người dùng chọn 2026-11-25).
- Kỹ năng đã có vẫn nằm trên lộ trình và được tô (FR-010 của #212).


## Thay đổi sau merge (2026-11-27, Hướng B — CV Advisor)

Người dùng chọn **Hướng B**: mở khóa chọn `Cấp bậc` (`level`) trên `/co-van` và tích hợp tải CV + đối chiếu JD + LLM:
- `web/app/co-van/page.tsx` đọc `initialLevel` từ URL (`entry` chỉ là mặc định `DEFAULT_PATH_LEVEL` trong `web/lib/learning-path-view.ts`, bỏ khóa cứng `level = entry` của #134).
- `web/app/components/advisor/learning-path-screen.tsx` thêm `<FilterSelect label="Cấp bậc" />` và nhúng `CvAdvisorForm` (`web/app/components/advisor/cv-advisor-form.tsx`) gọi `POST /api/v1/advisor/roadmap`.
- Đánh dấu `have` trên `PathGraph` khi đang xem lộ trình sinh từ CV cập nhật trực tiếp trạng thái lộ trình & hồ sơ trình duyệt mà không phải upload lại CV. Chi tiết: [specs/cv-advisor-roadmap/spec.md](../cv-advisor-roadmap/spec.md).