# Feature Specification: Lọc bản đồ theo số năm kinh nghiệm

**Feature Branch**: `gh-280-loc-nam-kinh-nghiem`

**Created**: 2026-11-12

**Status**: Implemented, chờ merge. Cập nhật 2026-11-13 theo #293: bộ chọn số năm là `<select>` thay cho hàng nút `aria-pressed` (hành vi và AC không đổi).

**Input**: GitHub issue [#280](https://github.com/Dyuedu/HaiDoIT/issues/280) — As an entry-level job seeker, I want to narrow the map to postings that ask for no more years of experience than I have, so that I can see where the jobs I can apply for today are. Liên quan: bộ lọc cấp bậc [#163](https://github.com/Dyuedu/HaiDoIT/issues/163) (cùng mẫu), story bản đồ [#112](https://github.com/Dyuedu/HaiDoIT/issues/112), quy tắc mẫu nhỏ AD-17, không đổi ngưỡng [#260](https://github.com/Dyuedu/HaiDoIT/issues/260).

## Bối cảnh

Bước trích của scraper (`scraper/extract.py`) đã ghi `years_experience_min` cho khoảng 68% tin trong bảng `jobs` (4283/6255 ngày 12/11/2026), nhưng kho (`haido`) chưa chép trường này và bản đồ chỉ lọc được theo cấp bậc. Số năm là trường đóng đã trích sẵn: kho chỉ chép, không đọc JD và không gọi mô hình.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bộ chọn số năm kinh nghiệm trên bản đồ (Priority: P1)

Người dùng thấy, dưới bộ chọn cấp bậc, một bộ chọn số năm: "Mọi số năm", "Không cần kinh nghiệm", "Tối đa 1 năm", "Tối đa 2 năm", "Tối đa 3 năm", "Tối đa 5 năm". Trang mở ở "Mọi số năm".

**Why this priority**: AC 1 của #280.

**Independent Test**: Render `MapScreen` với API giả; danh sách option khớp `years_options` của `config/rules.toml` với `any` đứng đầu; lượt gọi đầu có `years=any`.

**Acceptance Scenarios**:

1. **Given** trang vừa mở, **When** lượt gọi đầu đi ra, **Then** URL là `/api/v1/city-shares?role=all&level=entry&years=any` và ô "Số năm kinh nghiệm" đang chọn "Mọi số năm" (từ #293; trước đó nút có `aria-pressed="true"`).
2. **Given** bộ chọn số năm, **When** đọc danh sách option, **Then** thứ tự là any, 0, 1, 2, 3, 5, nhãn tiếng Việt, trong một `<select>` cao tối thiểu 44px (#293; trước đó mỗi nút là `<button aria-pressed>`).
3. **Given** `config/rules.toml` có `years_options = [0, 1, 2, 3, 5]`, **When** test đối chiếu `web/lib/labels.ts`, **Then** mã của web đúng bằng `any` cộng các giá trị đó.

---

### User Story 2 - Chọn số năm thì chỉ đếm tin yêu cầu không quá số đó (Priority: P1)

Người dùng chọn "Tối đa 2 năm". Bản đồ chỉ đếm các tin có số năm tối thiểu yêu cầu ≤ 2.

**Why this priority**: AC 2 của #280, là chính tính năng.

**Independent Test**: Hàm thuần `aggregate_city_shares` với tin có `years_min` = 0, 1.5, 2, 3, None: ô `y2` đếm ba tin đầu.

**Acceptance Scenarios**:

1. **Given** tin có `years_min` 0, 1.5, 2, 3 và một tin không ghi, **When** tổng hợp với `years = 2`, **Then** n toàn quốc là 3.
2. **Given** `years = 0`, **When** tổng hợp, **Then** chỉ đếm tin có `years_min = 0`.
3. **Given** `years = any`, **When** tổng hợp, **Then** số giống hệt khi chưa có tính năng (mọi tin, kể cả không ghi số năm).
4. **Given** bản đồ ở `years=any`, **When** bấm "Tối đa 2 năm", **Then** gửi `years=2`, hiện trạng thái đang tải, rồi thanh và bảng cùng hiện số của `years=2`; response về muộn của lựa chọn cũ bị bỏ.
5. **Given** `years` ngoài danh sách cấu hình, **When** gọi API, **Then** 422 `invalid_query`.
6. **Given** ingest chạy và bảng `jobs` của scraper có `years_experience_min`, **When** chép dữ kiện, **Then** `job_posting_facts.years_min` mang giá trị đó; giá trị đổi so với phiên bản trước thì có phiên bản dữ kiện mới.

---

### User Story 3 - Màn nói rõ bao nhiêu tin bị bỏ vì không ghi số năm (Priority: P1)

Khi đang lọc theo số năm, màn có một dòng: "N tin của <vai trò> · <cấp> không ghi số năm kinh nghiệm nên không được tính."

**Why this priority**: AC 3 của #280. Khoảng 32% tin không ghi số năm; giấu chuyện đó làm người dùng tưởng thị trường nhỏ hơn thật.

**Independent Test**: API trả `data.years_unstated_cell_id` trỏ tới ô `vn.<role>[.<level>].ynone` trong `meta.cells`, có `n` bằng số cụm không ghi số năm của (vai trò, cấp) toàn quốc (AD-17: số nằm trong `meta.cells`, không đứng trần trong `data`); web hiện dòng đó khi `years ≠ any` và không hiện khi `years = any`.

**Acceptance Scenarios**:

1. **Given** vai trò có 10 cụm trong cửa sổ, 4 cụm không ghi số năm, **When** gọi `years=1`, **Then** `data.years_unstated_cell_id = "vn.<role>.ynone"` và `meta.cells` của ô đó có `n = 4`.
2. **Given** `years = any`, **When** gọi API, **Then** `data.years_unstated_cell_id` là `null` và web không hiện dòng bị bỏ.
3. **Given** cấp `entry` đang chọn, **When** gọi `years=2`, **Then** ô `vn.<role>.entry.ynone` chỉ đếm cụm cấp `entry` không ghi số năm.

---

### User Story 4 - Hai bộ lọc chạy cùng nhau, màn nêu cả hai và ngày snapshot (Priority: P1)

**Why this priority**: AC 4 của #280.

**Independent Test**: Test web: đổi cấp rồi đổi số năm, lượt gọi mang cả `level` và `years`; khung "Nguồn và lưu ý" có dòng "Bộ lọc" nêu vai trò, cấp, số năm, cạnh "Ngày snapshot".

**Acceptance Scenarios**:

1. **Given** cấp `senior` và số năm `3`, **When** đổi vai trò, **Then** lượt gọi mang `role` mới, `level=senior`, `years=3`.
2. **Given** envelope có `data.level = entry`, `data.years = 2`, **When** dựng màn, **Then** khung chú thích có "Bộ lọc: AI/ML · Mới vào nghề · Tối đa 2 năm" và ngày snapshot; tiêu đề biểu đồ và caption của bảng cũng nêu số năm.
3. **Given** envelope có `data.years` khác số năm đã hỏi, **When** web kiểm hợp đồng, **Then** coi là không đọc được.
4. **Given** `aggregate` chạy, **When** đọc `stat_city_shares` theo (vai trò, cấp, số năm), **Then** mỗi bộ ba có đủ năm dòng thành phố và tổng bằng 1; n bằng 0 thì toàn bộ rơi vào `unknown`.

---

### User Story 5 - Thành phố dưới 30 tin theo bộ lọc đã chọn bị làm mờ (Priority: P1)

**Why this priority**: AC 5 của #280; cùng quy tắc của #163 và AD-17.

**Independent Test**: Ô (thành phố, vai trò, cấp, số năm) có n = 29 → `low_sample_shown`; n = 30 → `shown`.

**Acceptance Scenarios**:

1. **Given** Đà Nẵng có 29 tin ở `entry` và `years=2`, **When** API trả `city-shares`, **Then** `display = low_sample_shown` và `meta.cells["da_nang.<role>.entry.y2"].n = 29`.
2. **Given** đổi số năm, **When** n của ô mới ≥ 30, **Then** thanh hết mờ; trạng thái theo n của ô đang chọn, không theo n của `any`.

---

### User Story 6 - Trên điện thoại bộ chọn số năm vẫn dùng được ở danh sách thành phố (Priority: P1)

**Why this priority**: AC 6 của #280 và DoD dòng điện thoại (#137).

**Independent Test**: Bộ chọn số năm nằm ngoài khối chỉ-desktop, một cột ở điện thoại trong lưới của #293 (trước đó `flex-wrap`), không có cuộn ngang; test web chạy ở lối danh sách (2D) và lối bảng đều thấy bộ chọn.

**Acceptance Scenarios**:

1. **Given** khổ 360px ở lối danh sách thành phố, **When** bấm "Tối đa 1 năm", **Then** lượt gọi mang `years=1` và danh sách đổi số.
2. **Given** bộ chọn số năm, **When** dùng bàn phím, **Then** ô chọn focus được, có vòng focus và nhãn hiện "Số năm kinh nghiệm" (#293; trước đó mỗi nút và nhãn nhóm).

---

### Edge Cases

- Tin ghi `years_min` không nguyên (1.5) được so trực tiếp: 1.5 ≤ 2 nhưng > 1.
- Tin không ghi số năm luôn nằm trong `any`, không nằm trong mọi mốc khác.
- Snapshot đã chốt trước migration 0006 chỉ có hàng `years = any`: API chọn snapshot theo (cấp, số năm), nên số năm khác `any` lùi về snapshot mới nhất có hàng đó; không có thì 404 `unknown_cell` không ngày, thông báo nói chưa có snapshot nào được tính cho bộ lọc này.
- Ngay sau khi triển khai, tin trong cửa sổ 60 ngày nhưng không được thấy lại từ khi có cột `years_min` vẫn mang `years_min = null`, nên tỷ lệ "không ghi" của vài snapshot đầu cao hơn 32%; dòng số tin bị bỏ nói đúng con số đó. Bước trích (`process`) chạy sau bước kho trong `daily.sh`, nên tin mới có số năm ở snapshot hôm sau.
- Nguồn giả chỉ có `years=any` cho mọi (vai trò, cấp) và thêm `years=1` cho `all/entry`; tổ hợp khác trả `unknown_cell`.
- Gọi API không có `years` thì như `any` (tương thích ngược); web luôn gửi `years`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `config/rules.toml` có `years_options` (số nguyên ≥ 0, tăng dần, không trùng); `haido_core/config.py` kiểm và báo lỗi tiếng Việt; `config_version` tăng.
- **FR-002**: Ingest chép `jobs.years_experience_min` của scraper vào cột mới `job_posting_facts.years_min`; `FactVersion` có `years_min`.
- **FR-003**: `aggregate` ghi ô và tỷ trọng cho mỗi (vai trò, cấp lọc, mã số năm) với mã số năm trong `any` + `years_options`; mã `N` đếm tin có `years_min ≤ N`. Mỗi ô ghi thêm `years_unstated`: số cụm của (vai trò, cấp, phạm vi) không ghi số năm.
- **FR-004**: `stat_cells` và `stat_city_shares` có cột `years` trong khóa chính (hàng cũ nhận `any`); `stat_cells` có `years_unstated`. Migration 0006 nối vào 0005, có `downgrade`.
- **FR-005**: `GET /api/v1/city-shares` nhận `years` tùy chọn (Literal dựng từ config); trả `data.years` và `data.years_unstated_cell_id` (`null` khi `any`), ô đó nằm trong `meta.cells` với `n` là số tin không ghi số năm. Mã ô: `<scope>.<role>[.<level>][.y<years>]`; ô tin bị bỏ: `vn.<role>[.<level>].ynone`.
- **FR-006**: Web có bộ chọn số năm (mặc định `any`), gửi `years` cùng `role` và `level`, hiện dòng tin bị bỏ khi `years ≠ any`, nêu bộ lọc ở khung chú thích, tiêu đề biểu đồ và caption bảng.

### Key Entities

- **Mã số năm**: `any` hoặc chuỗi số nguyên `N` (≤ N năm tối thiểu).
- **years_unstated**: số cụm không ghi số năm của (vai trò, cấp) toàn quốc ở snapshot đó; kho ghi ở `stat_cells.years_unstated`, API trả qua ô `...ynone` của `meta.cells`.

## Success Criteria *(mandatory)*

- **SC-001**: Mọi AC của #280 có test tương ứng, đỏ trước khi có code.
- **SC-002**: `years = any` cho đúng số như trước tính năng ở mọi (vai trò, cấp).
- **SC-003**: Lượt đêm đầu tiên sau triển khai ghi ô số năm và `GET /api/v1/city-shares?role=all&level=entry&years=1` trả 200.

## Assumptions

- Số năm do bước trích ghi được coi là đúng như tin viết ("Never guess" trong prompt); kiểm độ chính xác của bước trích nằm ngoài issue này.
- Mốc 0, 1, 2, 3, 5 theo bản nháp issue đã được duyệt ngày 12/11/2026.
