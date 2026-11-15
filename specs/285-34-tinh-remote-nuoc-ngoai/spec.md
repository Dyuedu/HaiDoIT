# Feature Specification: Đếm theo 34 tỉnh, thành, cộng Remote và Nước ngoài

**Feature Branch**: `gh-285-34-tinh`

**Created**: 2026-11-13

**Status**: Implemented, chờ merge (sau PR #287, #288). Cập nhật 12/11: câu giới thiệu trang Bản đồ. Cập nhật 2026-11-13 (#293): test của #285 trong `fr33-map-screen` chọn vai trò bằng `<select>` thay cho chip; đợt 2 bỏ hai assert thừa. Không AC nào đổi.

**Input**: GitHub issue [#285](https://github.com/Dyuedu/HaiDoIT/issues/285) — Count postings in all 34 provinces, plus Remote and Abroad, reading the address lines of the posting. Phục vụ [#112](https://github.com/Dyuedu/HaiDoIT/issues/112), [#116](https://github.com/Dyuedu/HaiDoIT/issues/116). Dựa trên [#283](https://github.com/Dyuedu/HaiDoIT/issues/283) (phân loại ở ingest) và [#284](https://github.com/Dyuedu/HaiDoIT/issues/284).

## Bối cảnh

Bản đồ đếm ba thành phố, mọi nơi khác là "Khác" hoặc "không xác định". Thành phố phân loại lúc `aggregate` từ trường `location`. Người dùng chốt ngày 13/11/2026: đếm đủ các tỉnh, quy tỉnh cũ về tỉnh mới, đọc dòng địa chỉ trong JD, tách Remote và Nước ngoài.

## Clarifications

- Mã nơi: 34 mã tỉnh, thành (`ha_noi`, `ho_chi_minh`, `hai_phong`, `da_nang`, `can_tho`, `hue`, …), `remote`, `abroad`, `unknown`. Mã `other` ("Khác") bị bỏ: mọi nơi biết được đều có tỉnh riêng.
- Thứ tự quyết nơi: tỉnh trong trường `location` → nước ngoài trong `location` → tỉnh trong dòng địa chỉ của JD → nước ngoài trong dòng địa chỉ → remote (`location` rồi địa chỉ) → không xác định. Remote chỉ khi tin không nêu tỉnh nào.
- Nhiều tỉnh: cụm khớp sớm nhất thắng (`multi_city = "first_phrase"`, như hiện có).
- Thành phố phân loại ở `ingest` (cần dòng địa chỉ của JD) và lưu vào `job_posting_facts.city` (migration 0008). `classify_version` đổi nên mọi tin trong cửa sổ được phân loại lại ở lượt đêm đầu.
- `stat_*` chỉ ghi hàng của nơi có ít nhất một tin trong bộ lọc, cộng `always_cities` (Hà Nội, TP.HCM, Đà Nẵng, Remote, Nước ngoài, Không xác định); xem research.md.
- Màn Bản đồ: thanh vẫn là Hà Nội, TP.HCM, Đà Nẵng; dòng chú thích là Remote, Nước ngoài, Không xác định; bảng có ba thành phố, rồi các tỉnh khác nơi nhiều tin đứng trước, rồi ba dòng chú thích.
- AC "Other appears only in the legend" của #112 không còn đối tượng (không còn "Khác"); người dùng đã chọn thay "Khác" bằng từng tỉnh. Các tỉnh ngoài ba thành phố nằm trong bảng, không thành thanh.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tỉnh cũ quy về tỉnh mới (Priority: P1)

**Why this priority**: AC 1, 4 của #285.

**Independent Test**: `RuleClassifier.classify` với chữ địa điểm.

**Acceptance Scenarios**:

1. **Given** `location` "Bình Dương", "Thủ Dầu Một", "Vũng Tàu", **Then** TP.HCM. **Given** "Quảng Nam", "Hội An", **Then** Đà Nẵng. **Given** "Hải Dương", **Then** Hải Phòng. **Given** "Bắc Giang", **Then** Bắc Ninh. **Given** "Nam Định", **Then** Ninh Bình. **Given** "Long An", **Then** Tây Ninh.
2. **Given** "Vĩnh Phúc", **Then** Phú Thọ (không bị đọc thành Vĩnh Long hay Nghệ An). **Given** "Phường Vỹ Dạ, Huế", **Then** Huế.
3. **Given** "Đà Nẵng / Hà Nội", **Then** Đà Nẵng (cụm sớm nhất).
4. **Given** bảng tỉnh trong `classify.toml`, **When** kiểm, **Then** đúng 34 nhãn tỉnh, mỗi nhãn có mã trong `[labels.city]`.

---

### User Story 2 - Đọc dòng địa chỉ khi `location` trống (Priority: P1)

**Why this priority**: AC 2 của #285.

**Independent Test**: `address_text` và `classify` với `location` trống.

**Acceptance Scenarios**:

1. **Given** `location` trống và JD có "Địa điểm làm việc: Tòa nhà X, Cầu Giấy, Hà Nội", **Then** Hà Nội.
2. **Given** JD có "Công ty thành lập tại Đà Nẵng năm 2010" ở phần giới thiệu và không có dòng địa chỉ, **Then** không xác định.
3. **Given** `location` "Hà Nội" và địa chỉ JD ở TP.HCM, **Then** Hà Nội (trường `location` thắng).

---

### User Story 3 - Remote và Nước ngoài (Priority: P1)

**Why this priority**: AC 3 của #285.

**Acceptance Scenarios**:

1. **Given** `location` trống, JD có "Hình thức: Remote / làm việc từ xa", không nêu tỉnh, **Then** Remote.
2. **Given** `location` "Remote" và dòng địa chỉ nêu Hà Nội, **Then** Hà Nội.
3. **Given** `location` "Quốc tế" hoặc "Nước ngoài", **Then** Nước ngoài. **Given** dòng địa chỉ "Làm việc tại Tokyo, Nhật Bản", **Then** Nước ngoài.
4. **Given** không có gì, **Then** không xác định, không phải Remote.

---

### User Story 4 - Số theo từng nơi, chỉ nơi có tin (Priority: P1)

**Why this priority**: AC 5, 6, 7 của #285.

**Independent Test**: hàm `aggregate_city_shares` và bước `aggregate` (Postgres); API.

**Acceptance Scenarios**:

1. **Given** tin ở Hà Nội, Hải Phòng, Remote, **When** tổng hợp, **Then** có ô và tỷ trọng của Hải Phòng; tỉnh không có tin (ví dụ Cà Mau) không có hàng; sáu nơi trong `always_cities` luôn có hàng; tỷ trọng mỗi (vai trò, cấp, số năm) cộng lại bằng 1.
2. **Given** API, **When** gọi `city-shares`, **Then** hàng theo thứ tự `[labels.city]`; nơi dưới 30 tin bị làm mờ như hiện có.
3. **Given** `job_posting_facts`, **When** ingest, **Then** có cột `city` (nhãn nơi); `aggregate` dùng nhãn đã lưu khi `classify_version` khớp.
4. **Given** snapshot 12/11 của bản sao local, **When** so trước/sau, **Then** ghi tỷ lệ tin IT không xác định nơi.

---

### User Story 5 - Màn Bản đồ hiện mọi nơi có tin (Priority: P1)

**Why this priority**: AC 5, 7 của #285.

**Independent Test**: test web với envelope có thêm Hải Phòng, Bắc Ninh.

**Acceptance Scenarios**:

1. **Given** envelope có Hà Nội, TP.HCM, Đà Nẵng, Hải Phòng (n 41), Bắc Ninh (n 34), Remote, Nước ngoài, Không xác định, **When** dựng màn, **Then** ba thanh; ba dòng chú thích Remote, Nước ngoài, Không xác định; bảng có tám dòng theo thứ tự: ba thành phố, Hải Phòng, Bắc Ninh, rồi ba dòng chú thích; mỗi dòng có nhãn tiếng Việt.
2. **Given** dòng dưới 30 tin, **Then** "chưa đủ dữ liệu" như hiện có.
3. **Given** `web/lib/labels.ts`, **When** so với config, **Then** nhãn của 34 tỉnh trùng nhãn trong `[labels.city]`.
4. **Given** khung 360px, **Then** không cuộn ngang trang.
5. **Given** trang Bản đồ, **When** đọc câu giới thiệu, **Then** câu nói tới từng tỉnh, thành, làm từ xa và nước ngoài, không chỉ ba thành phố (người dùng chốt 12/11).

### Edge Cases

- Snapshot cũ có hàng `other`: API vẫn trả hàng đó (đọc theo khóa), web hiện nhãn mã đó trong bảng. Lượt đêm đầu sau deploy không còn `other`.
- Tin vừa nêu tỉnh trong `location` vừa nêu nước ngoài trong JD: tính theo tỉnh.

## Requirements *(mandatory)*

- **FR-001**: `config/rules.toml`: `[labels.city]` có 34 tỉnh, `Remote`, `Nước ngoài`, `không xác định`; khóa mới `always_cities`; `config_version` đổi. `config.py` bỏ tập mã cố định, kiểm mã dạng snake_case, có `unknown`, `always_cities` ⊆ mã.
- **FR-002**: `config/classify.toml`: `[[cities]]` cho 34 tỉnh với tên mới, tên cũ và tên thành phố/huyện hay gặp; `abroad_phrases`, `abroad_location_phrases`, `remote_phrases`, `[address]` (biểu thức dòng địa chỉ, số dòng kèm theo); bỏ `other_city_phrases`; `classify_version` đổi.
- **FR-003**: `PostingFacts.address_text` (dòng địa chỉ đã bỏ dấu, chỉ trong bộ nhớ); `posting_text.address_text`.
- **FR-004**: `job_posting_facts.city` (migration 0008); ingest lưu, `aggregate` dùng khi phiên bản luật khớp.
- **FR-005**: `aggregate_city_shares(..., always_cities=...)` bỏ hàng của nơi không có tin ngoài `always_cities`.
- **FR-006**: Web: `LEGEND_CITIES` là `remote`, `abroad`, `unknown`; nhãn 34 tỉnh; bảng có các tỉnh khác nơi nhiều tin đứng trước.
- **FR-007**: Bản giả: thay `other` bằng `hai_phong`, thêm `remote`, `abroad`; sinh lại fixture web.

## Success Criteria *(mandatory)*

- **SC-001**: Trên snapshot 12/11 của bản sao, tỷ lệ tin IT không xác định nơi giảm (ghi số trước/sau).
- **SC-002**: Số hàng `stat_*` mỗi snapshot của bản sao không quá 3 lần số hiện tại (5832 ô, 4860 tỷ trọng); ghi đủ mọi nơi sẽ là khoảng 6 lần.
- **SC-003**: Mọi test Python và web, lint, build xanh; 360px không cuộn ngang.
