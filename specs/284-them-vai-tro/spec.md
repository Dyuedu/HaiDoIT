# Feature Specification: Thêm bảy vai trò vào danh sách vai trò

**Feature Branch**: `gh-284-them-vai-tro`

**Created**: 2026-11-13

**Status**: Implemented, chờ merge (sau PR #287 của #283).

**Input**: GitHub issue [#284](https://github.com/Dyuedu/HaiDoIT/issues/284) — Add Data Scientist, Fullstack, BA/PO/PM, Security, IT infrastructure, UI/UX and Game to the role list. Phục vụ [#112](https://github.com/Dyuedu/HaiDoIT/issues/112), [#110](https://github.com/Dyuedu/HaiDoIT/issues/110). Dựa trên nhãn của bộ phân loại [#283](https://github.com/Dyuedu/HaiDoIT/issues/283).

## Bối cảnh

#283 lưu bảy nhãn vai trò mới cho từng tin nhưng bảng `[report_as]` của `config/classify.toml` đưa chúng về `ai_ml` (Data Scientist) và `other` (sáu nhãn còn lại) lúc tổng hợp, vì danh sách vai trò của config, API và web chỉ có 10 mã. Issue này thêm bảy mã và bỏ `report_as`.

## Clarifications

- Mã và nhãn: `data_scientist` "Khoa học dữ liệu", `fullstack` "Fullstack", `ba_po_pm` "BA / PO / PM", `security` "Bảo mật", `it_infra` "Hạ tầng & IT support", `ui_ux` "UI/UX", `game` "Phát triển game".
- Thứ tự hiển thị: Tất cả, Nhúng, AI/ML, Khoa học dữ liệu, Kỹ sư dữ liệu, Phân tích dữ liệu, Kiểm thử (QA), DevOps, Bảo mật, Hạ tầng & IT support, Mobile, Frontend, Backend, Fullstack, BA / PO / PM, UI/UX, Phát triển game, Vai trò khác.
- Bỏ `report_as` không đổi nhãn đã lưu, nên `classify_version` không đổi (không làm mới dữ kiện). `config_version` của `config/rules.toml` đổi.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Danh sách vai trò giống nhau ở config, API, web (Priority: P1)

**Why this priority**: AC 1 của #284.

**Independent Test**: test đối chiếu `roles` của `config/rules.toml` với `ROLE_OPTIONS` của web (có sẵn từ #162). Tham số `role` của API là chuỗi tự do (không có enum), nên OpenAPI không đổi.

**Acceptance Scenarios**:

1. **Given** `config/rules.toml`, **When** đọc `roles`, **Then** có 17 mã theo thứ tự ở Clarifications, có bảy mã mới.
2. **Given** `[labels.role]`, **When** đọc, **Then** mỗi nhãn của bộ phân loại có một mã riêng (Data Scientist → `data_scientist`, Fullstack → `fullstack`, BA/PO/PM → `ba_po_pm`, Security → `security`, Hạ tầng/IT support → `it_infra`, UI/UX → `ui_ux`, Game → `game`) và `[report_as]` của `classify.toml` rỗng.
3. **Given** `web/lib/labels.ts`, **When** so với config, **Then** `ROLE_OPTIONS` là `all` cộng 17 mã, cùng thứ tự, nhãn tiếng Việt không rỗng.
4. **Given** API, **When** gọi `city-shares` với một mã mới, **Then** route nhận mã đó như mã cũ; mã không có trong config vẫn là 404 `unknown_cell`.

---

### User Story 2 - Vai trò mới có số như vai trò cũ (Priority: P1)

**Why this priority**: AC 2, 3 của #284.

**Independent Test**: Postgres: ingest tin của mỗi vai trò mới rồi `aggregate`; đọc `stat_cells`, `stat_city_shares`.

**Acceptance Scenarios**:

1. **Given** tin "Senior Fullstack Developer" ở Hà Nội, **When** `aggregate`, **Then** ô `vn.fullstack` có n = 1, ô `vn.other` có n = 0, và có đủ hàng theo cấp và số năm như mọi vai trò.
2. **Given** tin của từng vai trò mới, **When** `aggregate`, **Then** mỗi mã mới có ô và tỷ trọng thành phố; tổng tỷ trọng mỗi (vai trò, cấp, số năm) bằng 1.
3. **Given** tin "Software Engineer" không có văn bản ở nguồn chỉ-IT, **When** `aggregate`, **Then** vẫn vào `other`.
4. **Given** API nguồn `stat`, **When** gọi `city-shares?role=fullstack&level=entry&years=1`, **Then** 200 với `data.role = fullstack`; thành phố dưới 30 tin bị làm mờ như vai trò khác.

---

### User Story 3 - Bản giả và fixture web có vai trò mới (Priority: P1)

**Why this priority**: AC 4 của #284.

**Independent Test**: test của #162 (`city_shares` của bản giả ⊆ vai trò của config) cộng test mới: mỗi vai trò mới có `city_shares` ở `all` và một dòng `newcomer_roles`.

**Acceptance Scenarios**:

1. **Given** API giả, **When** gọi `city-shares?role=<mã mới>`, **Then** 200, ô và tỷ trọng đọc được.
2. **Given** API giả, **When** gọi `newcomer-roles`, **Then** có một dòng cho mỗi mã của `roles`, theo thứ tự config.
3. **Given** `web/tests/fixtures/`, **When** sinh lại từ API giả, **Then** test fixture của web xanh.

---

### User Story 4 - Bộ chọn vai trò vẫn dùng được trên điện thoại và bàn phím (Priority: P1)

**Why this priority**: AC 5 của #284.

**Independent Test**: test web: nhóm "Vai trò" có 18 nút `aria-pressed`, xuống dòng (`flex-wrap`), Tab đi qua đủ 18 nút theo thứ tự; đo trên trình duyệt ở 360px.

**Acceptance Scenarios**:

1. **Given** màn Bản đồ, **When** đếm nút trong nhóm "Vai trò", **Then** 18 nút theo thứ tự config, mỗi nút cao tối thiểu 44px.
2. **Given** bàn phím, **When** Tab từ nút đầu, **Then** đi qua 18 nút vai trò rồi tới nút cấp bậc.
3. **Given** khung 360px, **When** mở màn Bản đồ, **Then** không có thanh cuộn ngang trang.

### Edge Cases

- Snapshot cũ (tính trước #284) không có hàng của mã mới: chọn vai trò mới trả 404 "chưa có snapshot" như #280; lượt đêm kế tiếp có số.
- Ô `other` của snapshot cũ chứa tin của bảy nhóm; snapshot mới thì không. Không trộn hai snapshot.

## Requirements *(mandatory)*

- **FR-001**: `config/rules.toml`: `roles` có 17 mã; `[labels.role]` thêm bảy nhãn với mã riêng; `config_version` đổi.
- **FR-002**: `config/classify.toml`: `[report_as]` rỗng; code giữ hỗ trợ bảng này.
- **FR-003**: `web/lib/labels.ts`: `ROLE_OPTIONS` thêm bảy mã với nhãn tiếng Việt.
- **FR-004**: `haido_api/fixtures/fake_market.json`: `city_shares` và `cells` cho bảy mã mới; `newcomer_roles.rows` theo đúng `roles`.
- **FR-005**: Sinh lại `web/tests/fixtures/newcomer-roles.json` từ API giả; các fixture city-shares của web (`all`, `ai_ml`, `backend`) không đổi. `docs/api/openapi.json` không đổi.

## Success Criteria *(mandatory)*

- **SC-001**: Trên snapshot 12/11 của bản sao local, `other` chỉ còn tin chức danh chung (dưới 10% tin IT).
- **SC-002**: Mọi test, lint, build của Python và web xanh; trang Bản đồ ở 360px không cuộn ngang.
