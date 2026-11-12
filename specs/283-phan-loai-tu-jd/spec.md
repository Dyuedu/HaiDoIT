# Feature Specification: Phân loại tin ở bước ingest từ chức danh và nội dung JD

**Feature Branch**: `gh-283-phan-loai-tu-jd`

**Created**: 2026-11-13

**Status**: Implemented, chờ merge. SC-001 đạt trên mẫu chính sau đợt 2 nhưng IT recall trên mẫu giữ riêng là 81% (< 85%), xem tdd.md. SC-002, SC-003, SC-004 đạt.

**Input**: GitHub issue [#283](https://github.com/Dyuedu/HaiDoIT/issues/283) — Classify each posting at ingest from its title and text, and store role, sub-role, skills, level and years. Thay phạm vi của [#279](https://github.com/Dyuedu/HaiDoIT/issues/279) (đã đóng). Phục vụ [#112](https://github.com/Dyuedu/HaiDoIT/issues/112), [#110](https://github.com/Dyuedu/HaiDoIT/issues/110), [#111](https://github.com/Dyuedu/HaiDoIT/issues/111). Bảng số năm → cấp: [#134](https://github.com/Dyuedu/HaiDoIT/issues/134). Việc tiếp theo dùng kết quả này: [#284](https://github.com/Dyuedu/HaiDoIT/issues/284) (danh sách vai trò), [#285](https://github.com/Dyuedu/HaiDoIT/issues/285) (thành phố), [#286](https://github.com/Dyuedu/HaiDoIT/issues/286) (chức danh trong nhóm).

## Bối cảnh

`RuleClassifier` (phép 6) chỉ đọc chức danh và chữ cấp bậc của nguồn. Trên bản sao prod ngày 12/11/2026, luật này coi khoảng một nửa tin IT là không thuộc IT, chỉ đếm 110 tin AI/ML (11 tin mới vào nghề), và 2917 trên khoảng 3800 tin IT không rõ cấp. Phân tích đầy đủ ở [research.md](research.md).

`REGISTRY.md` (phép 6) đổi trong cùng PR: phân loại được đọc văn bản JD đầy đủ nhưng không gọi mô hình; văn bản chỉ đi qua bộ nhớ.

## Clarifications

- Phân loại chạy ở bước `ingest`, lúc văn bản JD còn trong bộ nhớ. Kho chỉ lưu nhãn và mã (cách A, người dùng chốt 12/11/2026).
- Bước `aggregate` đọc nhãn đã lưu. Dữ kiện chưa có nhãn của phiên bản luật hiện tại (dữ liệu cũ, test cũ) thì phân loại ngay từ trường đóng như trước, không đọc JD.
- Vai trò mới (Data Scientist, Fullstack, BA/PO/PM, Security, Hạ tầng/IT support, UI/UX, Game) là nhãn của bộ phân loại từ #283. Mã hiển thị và danh sách vai trò trên web đổi ở #284; tới lúc đó `[labels.role]` đưa các nhãn mới về `other`, riêng Data Scientist về `ai_ml`.
- Số năm tối thiểu: số tháng có cấu trúc của nguồn (CareerLink) thắng; rồi giá trị bước trích đã ghi (`jobs.years_experience_min`); rồi luật đọc mục yêu cầu (lấy yêu cầu chính, không lấy số nhỏ nhất). Câu "không yêu cầu kinh nghiệm" cho 0 khi bước trích để trống.
- Mã kỹ năng giữ nguyên 100 mã của `skills_seed.json` (hồ sơ người dùng đã lưu các mã đó) và thêm mã mới vào cùng file, đổi phiên bản từ vựng.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Vai trò đọc cả chức danh và nội dung tin (Priority: P1)

**Why this priority**: AC 1, 3, 4 của #283; là nguyên nhân chính khiến số AI/ML và số tin IT thấp.

**Independent Test**: Hàm thuần `RuleClassifier.classify` với `PostingFacts` có chức danh, văn bản ngắn tự viết và mã kỹ năng; bảng scenario dưới đây.

**Acceptance Scenarios**:

1. **Given** chức danh "Senior Software Engineer (Java)", **When** phân loại, **Then** vai trò Backend (vai trò cụ thể trong chức danh thắng cụm chung).
2. **Given** chức danh "Lập trình viên" và mục yêu cầu nhắc React, TypeScript, Node.js, PostgreSQL, Docker, **When** phân loại, **Then** vai trò Fullstack; chỉ nhắc React, CSS, HTML thì Frontend.
3. **Given** chức danh "Kỹ sư AI", "AI Agent Engineer (Python, LLM)", "LLM Engineer", **When** phân loại, **Then** AI/ML. **Given** "Data Scientist" hoặc "Thực tập sinh Khoa học dữ liệu", **Then** Data Scientist.
4. **Given** chức danh "Product Owner (OCR/AI)", "Phụ trách thương mại hóa sản phẩm AI", "Sales Executive (AI SaaS)", **When** phân loại, **Then** không phải AI/ML (BA/PO/PM, không thuộc IT, không thuộc IT).
5. **Given** "Business Analyst", "Scrum Master", "Head of Product", "Product Specialist", **Then** BA/PO/PM. **Given** "Chuyên viên Khách hàng Doanh nghiệp - Khu vực Sơn Tây, Ba Vì", **Then** không thuộc IT ("Ba Vì" không phải BA).
6. **Given** "CyberSecurity Engineer", "Kỹ Sư An Ninh Thông Tin", "Penetration Tester", **Then** Security. **Given** "Nhân viên IT Helpdesk", "Quản trị mạng", "System Engineer", **Then** Hạ tầng/IT support.
7. **Given** "UI/UX Designer", **Then** UI/UX. **Given** "Graphic & Motion Designer", "2D Game Artist", **Then** không thuộc IT. **Given** "Unity Game Developer", "Technical Artist", **Then** Game.
8. **Given** "Kỹ Sư Quy Hoạch Mạng Vô Tuyến Di Động 4G, 5G", "Nhân Viên Lập Trình CNC", "Product Developer Manager" với mô tả về may mặc, **Then** không thuộc IT.
9. **Given** "Product Owner (E-Commerce/SaaS)", **Then** BA/PO/PM ("e-commerce" không làm tin thành không thuộc IT). **Given** "Nhân viên kinh doanh phần mềm", **Then** không thuộc IT.
10. **Given** "Test Engineer (Kỹ Sư Phòng Thử Nghiệm)" với mô tả thử nghiệm sản phẩm điện và không có kỹ năng kiểm thử phần mềm, **Then** không thuộc IT. **Given** "Tester Intern" không có kỹ năng nào trong mô tả, **Then** QA.
11. **Given** chức danh không có cụm vai trò nào nhưng mục yêu cầu có từ 4 kỹ năng kỹ thuật, **Then** vai trò theo bằng chứng kỹ năng; dưới 4 thì không thuộc IT.
12. **Given** cùng đầu vào và cùng cấu hình, **When** phân loại hai lần hoặc đổi thứ tự lô, **Then** cùng nhãn.

---

### User Story 2 - Mỗi tin có chức danh con trong vai trò (Priority: P1)

**Why this priority**: AC 5 của #283; #286 dùng.

**Independent Test**: `Classification.branch` của các chức danh mẫu.

**Acceptance Scenarios**:

1. **Given** BA/PO/PM với chức danh "Business Analyst", "Product Owner", "IT Project Manager", "SAP FICO Consultant", **Then** chức danh con lần lượt Business Analyst, Product Owner, Project Manager, ERP/SAP consultant.
2. **Given** Hạ tầng với "IT Helpdesk", "Network Engineer", "System Administrator", **Then** Helpdesk/Support, Network, System Admin.
3. **Given** chức danh không khớp chức danh con nào của vai trò, **Then** `branch` là `None` (không đoán).

---

### User Story 3 - Kỹ năng lấy từ mục yêu cầu và nhiệm vụ, đếm mọi lượt nhắc (Priority: P1)

**Why this priority**: AC 1, 6 của #283; #111 và #278 dùng.

**Independent Test**: `requirement_text` và `find_mentions` + `map_mentions` trên văn bản tự viết có các mục "Mô tả công việc", "Yêu cầu", "Quyền lợi", "Giới thiệu công ty".

**Acceptance Scenarios**:

1. **Given** văn bản có "Python" hai lần ở mục yêu cầu và "Docker" ở mục nhiệm vụ, **When** quét, **Then** `{python: 2, docker: 1}`.
2. **Given** "machine learning" chỉ xuất hiện ở mục "Quyền lợi" hoặc "Về chúng tôi", **Then** không có `machine_learning`.
3. **Given** "Tốt nghiệp chuyên ngành Khoa học máy tính", **Then** không có `machine_learning`.
4. **Given** "chăm sóc khách hàng", **Then** không có `siem`. **Given** "sắp xếp công việc", **Then** không có `sap`.
5. **Given** "C/C++" , **Then** cả `c` và `cpp`. **Given** "ASP.NET Core", **Then** `dotnet`, không có thêm mã nào từ ".net" đứng riêng.
6. **Given** "kiểm thử tự động" và "automation testing", **Then** cùng mã `automation_testing` (song ngữ, hai lượt).
7. **Given** chuỗi không có trong từ vựng, **When** `map_mentions`, **Then** `skill_id = None`.
8. **Given** văn bản không có tiêu đề mục nào, **Then** quét toàn bộ văn bản.

---

### User Story 4 - Cấp và số năm (Priority: P1)

**Why this priority**: AC 7, 8 của #283.

**Independent Test**: Hàm số năm và nhánh cấp của `classify`. Thứ tự: chữ cấp của nguồn → chức danh → số năm → không xác định (chữ cấp của nguồn đứng trước chức danh như luật hiện có, test `test_ad2_cap_bac_uu_tien_chu_nguon_ghi`).

**Acceptance Scenarios**:

1. **Given** nguồn CareerLink có `{"monthsOfExperience": 24}`, **Then** số năm 2, kể cả khi bước trích ghi số khác.
2. **Given** bước trích ghi 3, **Then** số năm 3. **Given** bước trích để trống và mục yêu cầu có "Không yêu cầu kinh nghiệm", **Then** 0.
3. **Given** bước trích để trống và yêu cầu "Tối thiểu 5 năm kinh nghiệm, trong đó ít nhất 2 năm quản lý", **Then** 5. "Có từ 3–5 năm kinh nghiệm" cho 3. "Công ty thành lập 10 năm" không cho số nào.
4. **Given** chức danh không ghi cấp và số năm 0 / 1 / 3 / 6, **Then** cấp Fresher / Junior / Mid / Senior (bảng của #134 trong config). Không bao giờ ra Intern hay Lead từ số năm.
5. **Given** "Product Manager", **Then** cấp không phải Lead. **Given** "Head of Product", "Tech Lead", "Trưởng nhóm Java", **Then** Lead.
6. **Given** VietnamWorks ghi `Experienced (non-manager)`, **Then** chữ này không cho cấp nào.
7. **Given** chức danh, chữ cấp của nguồn và số năm đều không có, **Then** cấp "không xác định".

---

### User Story 5 - Kho chỉ lưu mã, JD không bao giờ xuống đĩa (Priority: P1)

**Why this priority**: AC 2, 9 của #283; DoD dòng 9.

**Independent Test**: Postgres: chạy `ingest` với nguồn giả có mô tả chứa chuỗi đánh dấu; tìm chuỗi đó trong mọi cột text/jsonb của schema `haido`.

**Acceptance Scenarios**:

1. **Given** nguồn có mô tả, **When** `ingest`, **Then** `job_posting_facts` có `role`, `branch`, `seniority`, `skills` (object mã → số lượt), `years_min`, `classify_version`; chuỗi đánh dấu trong mô tả không xuất hiện ở bảng nào.
2. **Given** tin trong cửa sổ có dữ kiện mới nhất với `classify_version` cũ và không được quan sát ở S, **When** `ingest` S, **Then** tin đó có phiên bản dữ kiện mới tại S với nhãn của luật hiện tại; tin đã có nhãn của luật hiện tại thì không thêm phiên bản.
3. **Given** dữ kiện có nhãn của luật hiện tại, **When** `aggregate`, **Then** nhãn đã lưu được dùng, không phân loại lại. **Given** dữ kiện không có, **Then** phân loại từ trường đóng (chức danh, chữ cấp, địa điểm) như trước.
4. **Given** luật, danh sách cụm hoặc từ vựng đổi, **Then** `classify_version` đổi và `config_version` đổi.

---

### User Story 6 - Đo trên mẫu tự gán nhãn (Priority: P2)

**Why this priority**: AC 10, 11 của #283.

**Independent Test**: `tools/classify_eval/` đọc nhãn tay (không chứa văn bản JD) và bản sao local, in precision/recall theo vai trò và tỷ lệ khớp số năm, cho luật cũ, luật mới và bước trích.

**Acceptance Scenarios**:

1. **Given** ít nhất 150 tin tự gán nhãn, trong đó ít nhất 30 tin AI/ML hoặc khoa học dữ liệu, **When** chạy công cụ đo, **Then** in precision và recall theo vai trò, khớp số năm, cho ba bộ; kết quả ghi vào `tdd.md`.
2. **Given** snapshot 12/11/2026 của bản sao local, **When** so trước và sau, **Then** mỗi vai trò có tỷ lệ "không xác định cấp" và số tin mới vào nghề, ghi vào `tdd.md`.

### Edge Cases

- Mô tả rỗng hoặc `None`: phân loại chỉ bằng chức danh và chữ cấp; không lỗi.
- Văn bản rất dài (trên 50.000 ký tự): chỉ đọc 50.000 ký tự đầu.
- Chức danh chứa nhiều vai trò ("Backend/DevOps"): cụm khớp sớm nhất thắng, hòa vị trí thì thứ tự bảng thắng.
- Tin quan sát ở snapshot sau S (chạy bù): không thêm phiên bản tại S, như quy tắc hiện có.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `PostingFacts` có thêm `text` (văn bản JD, chỉ trong bộ nhớ), `skills` (cặp mã → số lượt) và `years_min`; mặc định rỗng để lời gọi cũ chạy như trước.
- **FR-002**: `Classification.branch` mang chức danh con; `role` có thêm bảy nhãn vai trò mới.
- **FR-003**: Phép 1 `map_mentions` có thân hàm (`haido_core/domain/mapping.py`), ánh xạ chuỗi qua bí danh của từ vựng; chuỗi lạ ra `None`.
- **FR-004**: Tìm lượt nhắc (`find_mentions`) chỉ trên văn bản của các mục yêu cầu và nhiệm vụ (`requirement_text`), che "khoa học máy tính" trước khi quét.
- **FR-005**: Luật vai trò, chức danh con, cấp, cụm không thuộc IT, trọng số bằng chứng kỹ năng và bảng số năm → cấp nằm ở `config/classify.toml`, có `classify_version`; `config/rules.toml` đổi `config_version` cùng lúc.
- **FR-006**: `ingest` đọc thêm mô tả (`description_consolidated`, rỗng thì `description`) và `years_experience_min`, phân loại, ghi nhãn vào `job_posting_facts`; làm mới nhãn của tin trong cửa sổ có `classify_version` cũ.
- **FR-007**: `aggregate` dùng nhãn đã lưu khi `classify_version` khớp; nhãn lạ vẫn dừng như hiện có.
- **FR-008**: `REGISTRY.md` phép 6 và docstring `PostingFacts` nói phân loại được đọc JD, không gọi mô hình, không lưu JD.

### Key Entities

- **job_posting_facts**: thêm `role`, `branch`, `seniority`, `skills`, `classify_version` (xem [data-model.md](data-model.md)).
- **Từ vựng kỹ năng** (`haido_core/vocab/skills_seed.json`): mã, tên, bí danh song ngữ; phiên bản mới.

## Success Criteria *(mandatory)*

- **SC-001**: Trên mẫu tự gán nhãn, recall "là tin IT" ≥ 85% và precision ≥ 90%; AI/ML có precision và recall ≥ 80%.
- **SC-002**: Trên snapshot 12/11/2026 của bản sao, tỷ lệ tin IT "không xác định cấp" giảm từ khoảng 76% xuống dưới 20%.
- **SC-003**: Không cột nào của schema `haido` chứa văn bản JD (test chuỗi đánh dấu).
- **SC-004**: `ingest` một ngày (khoảng 2700 quan sát cộng phần làm mới) chạy dưới 2 phút và dưới 512 MB trên container kho.
