# Feature Specification: Mã kỹ năng cho mọi kỹ năng tin hay nhắc tới

**Feature Branch**: `gh-278-ma-ky-nang-thuong-gap`

**Created**: 2026-11-23

**Status**: Implemented, chờ merge. AC1, AC4 kiểm bằng test; AC2 kiểm bằng test cho các cặp đã liệt kê, phần còn lại dựa vào việc người dùng duyệt `de-xuat-tu-vung.md`. AC3: bảng "trước" theo vai trò và số "sau" ở mức khóa đã báo cáo; số "sau" theo vai trò đo trên prod sau khi deploy, nên PR ghi "Refs #278" (không "Closes") và #278 mở cho đến khi đo xong (xem mục AC3). Đợt review 2026-11-23: sửa `--after`, mã ghép `ai/ml`, mở rộng `scan_skip`.

**Input**: GitHub issue [#278](https://github.com/Dyuedu/HaiDoIT/issues/278) — Give a skill code to every skill that postings often ask for (task, phục vụ [#111](https://github.com/Dyuedu/HaiDoIT/issues/111) và [#119](https://github.com/Dyuedu/HaiDoIT/issues/119)). Liên quan: [#283](https://github.com/Dyuedu/HaiDoIT/issues/283) (phân loại ở ingest, đã dùng từ vựng), [#97](https://github.com/Dyuedu/HaiDoIT/issues/97) (phép 1 không gọi mạng), [#96](https://github.com/Dyuedu/HaiDoIT/issues/96) (từ vựng v1 có giảng viên duyệt).

## Bối cảnh

Snapshot 2026-11-20 có 4.688 tin IT trong cửa sổ 60 ngày. Thẻ kỹ năng thô của site có 673 kỹ năng (sau khi gộp hoa thường, bỏ dấu) được nhắc ở từ 20 tin trở lên; từ vựng `seed-2026-11-13` (225 mã) tra được 369, còn 304 chưa có mã. Tin có thẻ không mã thì thẻ đó rơi khỏi tỷ lệ kỹ năng, nên hồ sơ kỹ năng của vai trò trông mỏng hơn tin thật. Số liệu và đề xuất: `gaps-2026-11-20.json` (kết quả `tools/vocab/skill_gaps.py` chạy trên prod, đã lọc: giữ khóa từ 20 tin, đổi `code` thành `code_before` và `roles` thành `roles_before`; `--after` đọc cả dạng thô lẫn dạng đã lọc, mặc định `--min-postings 20`), [de-xuat-tu-vung.md](de-xuat-tu-vung.md) (bản người đọc), `quyet-dinh-2026-11-20.json` (quyết định cho từng thẻ, **người dùng đã duyệt ngày 2026-11-20**).

Issue nói "khoảng 475 kỹ năng"; số trong snapshot 2026-11-20 là 673 vì đếm theo tin, mỗi thẻ một lần, gồm cả thẻ địa điểm và danh mục (phần lớn bị loại trừ).

## Clarifications

- Thay đổi này **không** thay review của giảng viên: bộ từ vựng v1 (#96) sẽ thay `skills_seed.json`. Ở đây chỉ là mở rộng bản mồi theo dữ liệu, người dùng duyệt từng quyết định; không tuyên bố đã qua duyệt của giảng viên.
- Danh sách loại trừ là một file riêng (`skills_excluded.json`), không nằm trong `skills_seed.json`, để từ vựng chỉ chứa kỹ năng.
- Một thẻ "ghép" như `Agile/Scrum` là hai lượt nhắc (`agile`, `scrum`), cùng cách `c/c++` đã làm ở #283.
- `scan_skip`: thẻ có mã nhưng không quét trong văn bản JD vì chữ quá chung (`cloud`, `api`, `monitoring`…). Phần tra thẻ của site vẫn dùng chúng.
- Ánh xạ lại không gọi mô hình: phép 1 (#97) chỉ tra bảng. Từ vựng đổi phiên bản thì `ingest` kế tiếp quét lại các tin trong cửa sổ (đã có từ #283, test `test_dat29_d3_doi_tu_vung_thi_ingest_ke_tiep_quet_lai_tin_trong_cua_so`; không làm lại ở đây).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mọi thẻ hay gặp có mã hoặc có lý do bị loại (Priority: P1)

**Why this priority**: AC1. Thẻ không mã làm mỏng hồ sơ kỹ năng; thẻ không phải kỹ năng (địa điểm, chức danh) phải bị loại có chủ ý, không bỏ sót lặng lẽ.

**Independent Test**: `tests/domain/test_gh278_vocab.py` đọc `gaps-2026-11-20.json` và tra từng khóa với `load_vocabulary()` và `load_exclusions()`.

**Acceptance Scenarios**:

1. **Given** 673 khóa kỹ năng có từ 20 tin ở snapshot 2026-11-20, **When** tra từng khóa, **Then** mỗi khóa nằm trong `lookup` hoặc `composites`, hoặc nằm trong danh sách loại trừ với lý do không rỗng; danh sách khóa còn lại rỗng.
2. **Given** danh sách loại trừ 158 dòng, **When** đọc, **Then** mỗi dòng có lý do và số tin bằng chứng khớp với `gaps` (từ 20 tin).
3. **Given** một khóa vừa trong danh sách loại trừ vừa trong từ vựng, hoặc dòng thiếu lý do, hoặc khóa trùng, **When** nạp, **Then** `ValueError` nêu khóa; không nạp lặng lẽ.

---

### User Story 2 - Cách viết Anh và Việt về một mã (Priority: P1)

**Why this priority**: AC2; hồ sơ không được tách một kỹ năng thành hai mã vì tin viết "Cơ sở dữ liệu" hay "database".

**Mức chứng minh của AC2**: test chứng minh các cặp đã liệt kê (19 cặp Anh/Việt), từng dòng của quyết định đã duyệt, và không khóa nào thuộc hai mã. Việc mọi cặp Anh/Việt còn lại của 673 thẻ cùng về một mã không tự kiểm được bằng máy (cần biết hai chữ cùng nghĩa); phần đó dựa vào việc người dùng đã duyệt `de-xuat-tu-vung.md`.

**Independent Test**: `fold` hai cách viết rồi tra `lookup`.

**Acceptance Scenarios**:

1. **Given** "Cơ sở dữ liệu" và "database", **When** tra, **Then** cùng mã `databases`. Tương tự "Xử lý sự cố" / "troubleshooting" → `troubleshooting`; "Quản trị hệ thống" / "system administration" → `system_administration`; thêm 16 cặp khác trong test.
2. **Given** mỗi dòng đã duyệt của quyết định (`new`, `alias`), **When** tra khóa, **Then** ra đúng mã đã duyệt; mỗi dòng `composite` ra đúng các phần đã duyệt; mỗi dòng `exclude` không có trong từ vựng.
3. **Given** mỗi mã mới, **When** tra tên Anh, tên Việt và các khóa thẻ của nó, **Then** chỉ ra một mã.
4. **Given** hai mã bất kỳ, **When** bỏ dấu mọi tên và bí danh, **Then** không khóa nào thuộc hai mã.
5. **Given** 225 mã của `seed-2026-11-13`, **When** nạp từ vựng mới, **Then** còn đủ 225 mã.

---

### User Story 3 - Báo cáo tỷ lệ lượt nhắc có mã theo vai trò, trước và sau (Priority: P2)

**Why this priority**: AC3.

**Independent Test**: test hàm thuần `summarize` và `remap` (`tests/tools/test_gh278_skill_gaps.py`), test `collect` trên Postgres (`tests/steps/test_gh278_skill_gaps_db.py`).

**Acceptance Scenarios**:

1. **Given** các tin với thẻ thô, **When** `summarize`, **Then** mỗi vai trò có số tin, lượt nhắc, lượt có mã và tỷ lệ; một tin nhắc một khóa hai lần (khác hoa thường, dấu) chỉ tính một lần; thẻ ghép tính là có mã.
2. **Given** kho `haido` và bảng `public.jobs` của scraper, **When** `collect`, **Then** chỉ tin IT của nguồn không bị loại trong cửa sổ được đếm, thẻ và kỹ năng nguyên văn ghép lại, và mọi câu SQL là SELECT.
3. **Given** `gaps-2026-11-20.json`, **When** `skill_gaps.py --after gaps.json`, **Then** in số khóa và lượt nhắc thẻ có mã trước và sau với từ vựng hiện hành, và bảng tỷ lệ theo vai trò "trước".
4. **Given** snapshot 2026-11-20, **Then** số khóa có mã tăng từ 369 lên 515 trên 673, 158 khóa nằm trong danh sách loại trừ, không còn khóa nào bị bỏ sót (`keys_unresolved` rỗng); tỷ lệ lượt nhắc thẻ (của khóa từ 20 tin) có mã tăng từ 56,4% lên 69,1%.

**Bảng "trước" theo vai trò** (snapshot 2026-11-20, `seed-2026-11-13`, mọi lượt nhắc thẻ thô, không chỉ khóa từ 20 tin):

| Vai trò | Tin | Lượt nhắc | Có mã | Tỷ lệ trước |
|---|---:|---:|---:|---:|
| AI/ML Engineer | 213 | 5.745 | 1.669 | 29,1% |
| BA/PO/PM | 992 | 20.646 | 3.912 | 18,9% |
| Backend | 556 | 12.626 | 5.563 | 44,1% |
| Data Analyst/BI | 183 | 2.914 | 865 | 29,7% |
| Data Engineer | 179 | 3.876 | 1.284 | 33,1% |
| Data Scientist | 34 | 679 | 232 | 34,2% |
| DevOps | 273 | 7.349 | 3.027 | 41,2% |
| Embedded | 110 | 2.518 | 549 | 21,8% |
| Frontend | 87 | 1.848 | 816 | 44,2% |
| Fullstack | 217 | 6.020 | 2.629 | 43,7% |
| Game | 114 | 2.078 | 387 | 18,6% |
| Hạ tầng/IT support | 648 | 15.310 | 2.903 | 19,0% |
| Mobile | 106 | 2.600 | 719 | 27,7% |
| Other | 280 | 4.659 | 1.303 | 28,0% |
| QA/Tester | 373 | 7.736 | 2.349 | 30,4% |
| Security | 234 | 4.903 | 1.399 | 28,5% |
| UI/UX | 89 | 2.787 | 432 | 15,5% |
| **Tổng** | 4.688 | 104.294 | 30.038 | 28,8% |

**AC3 và issue.** Cột "sau" theo vai trò chỉ đo được trên prod sau deploy, nên PR ghi "Refs #278", không "Closes #278"; #278 mở cho đến khi số đó được điền vào `docs/data/vocabulary.md` (task T020).

**Cột "sau" theo vai trò chưa có.** Tỷ lệ theo vai trò cần dữ liệu từng tin, mà file `gaps` chỉ giữ tổng theo khóa. Số "sau" được đo trên prod sau khi deploy bằng cách chạy lại script (lệnh ở [docs/data/vocabulary.md](../../docs/data/vocabulary.md)); không ước lượng từ số khóa. Mẫu số lớn (104.294 lượt) gồm cả thẻ địa điểm và danh mục bị loại trừ có chủ ý nên tỷ lệ tổng không thể đạt 100%.

---

### User Story 4 - Thêm mã thì đổi phiên bản từ vựng; ánh xạ chạy lại không gọi mô hình (Priority: P1)

**Why this priority**: AC4. Phiên bản từ vựng là khóa để `ingest` quét lại; ánh xạ không được cần mạng (#97).

**Independent Test**: test đọc `skills_seed.json`; test chặn `socket`.

**Acceptance Scenarios**:

1. **Given** từ vựng sau thay đổi, **When** đọc `version`, **Then** khác `seed-2026-11-13` và bằng `load_vocabulary().version`.
2. **Given** từ vựng đổi phiên bản, **When** `ingest` kế tiếp chạy, **Then** các tin trong cửa sổ được quét lại với phiên bản mới, tin cũ không bị mất — đã có ở #283 (`test_dat29_d3_doi_tu_vung_thi_ingest_ke_tiep_quet_lai_tin_trong_cua_so`), không nhân đôi test.
3. **Given** `socket.socket`, `socket.create_connection` và `socket.getaddrinfo` đều ném lỗi, **When** nạp từ vựng, `map_mentions` cho mọi khóa của từ vựng và `find_mentions` trên một đoạn văn, **Then** vẫn chạy và ra đúng mã.

---

### User Story 5 - Chữ quá chung tra được thẻ nhưng không quét trong JD (Priority: P2)

**Why this priority**: tránh phồng số tin: "cloud", "api", "monitoring" trong đoạn mô tả không nói tin cần kỹ năng đó.

**Independent Test**: `scan_skip` của quyết định.

**Acceptance Scenarios**:

1. **Given** 31 từ `scan_skip` của quyết định, **When** nạp từ vựng, **Then** không từ nào nằm trong `scan_terms` nhưng mọi từ đều còn trong `lookup`.
2. **Given** văn bản chỉ có các từ đó, **When** `find_mentions`, **Then** không ra lượt nhắc nào.
3. **Given** văn bản có "troubleshooting, debugging, code review" (không thuộc `scan_skip`), **When** `find_mentions` và `map_mentions`, **Then** ra `troubleshooting`, `debugging`, `code_review`.
4. **Given** `scan_skip` của seed (ngoài 31 từ của quyết định còn `bao mat`, `lap ke hoach`, `phan quyen`, `wifi`, `wi-fi`, `it infrastructure`, `it operations`, `it support`, `presentation`, `khoa hoc du lieu`, `tri tue nhan tao`), **When** quét "Tốt nghiệp chuyên ngành Khoa học dữ liệu, Trí tuệ nhân tạo, Khoa học máy tính" và "Cam kết bảo mật thông tin khách hàng, có wifi, lập kế hoạch công việc", **Then** không ra `data_science`, `artificial_intelligence` và không ra lượt nhắc từ các bí danh mới; thẻ của site (`IT Support`, `Khoa học dữ liệu`) vẫn tra ra mã.
5. **Given** mã ghép `ai/ml`, **When** quét "dùng ai/ml cho nlp", **Then** hai lượt nhắc `ai` (5-7) và `ml` (8-10) có vị trí thật, không phải -1; và `load_vocabulary` ném `ValueError` nếu một phần của mã ghép không nằm trong cụm.

---

### Giới hạn đã biết

- Bí danh cũ `bảo mật thông tin` (của `cybersecurity`, có từ trước #278) vẫn được quét trong JD và khớp câu như "cam kết bảo mật thông tin khách hàng". Giữ nguyên, ngoài phạm vi.
- Tỷ lệ lịch sử dịch chuyển khi phiên bản từ vựng đổi: `problem_solving`, `terraform`, `protocols_hw` mất các bí danh đã chuyển sang mã mới (`tu duy phan tich`, `tu duy logic`, `infrastructure as code`, `can bus`), còn `software_architecture` và `cybersecurity` được thêm bí danh. Tỷ lệ qua mốc `seed-2026-11-13` → `seed-2026-11-23` vì thế không so trực tiếp được.
- `leadership` khớp "ban lãnh đạo" trong khoảng một nửa số tin. Có từ trước #278, ngoài phạm vi; sẽ mở issue riêng.
- `ml` (bí danh của `machine_learning`) và `ai` (đã trong `scan_skip`) là chữ ngắn; `ml` vẫn được quét đứng riêng như trước #278.

### Edge Cases

- Ba khóa của mã mới trùng khóa của mã cũ (`can bus` ở `protocols_hw`, `infrastructure as code` ở `terraform`, `tu duy phan tich` ở `problem_solving`): chuyển về mã mới, cùng `tu duy logic`. Lý do và danh sách ở [data-model.md](data-model.md).
- Bí danh `"solid, "` (dư dấu phẩy) khiến thẻ SOLID (54 tin) không khớp; sửa thành `solid`.
- Cùng một thẻ viết hai lần trong một tin (thẻ và kỹ năng nguyên văn) chỉ đếm một lần.
- `jobs.skills_raw` có thể vắng ở DB cũ: `raw_skills` chỉ đọc cột khi nó có.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `skills_seed.json` MUST có 40 mã mới (tên Anh và Việt, bí danh là cách viết thật của thẻ, `source` bắt đầu `gh-278`), bí danh mới cho mã có sẵn, 6 mã ghép, và `scan_skip` mở rộng; 225 mã cũ MUST còn.
- **FR-002**: `version` của `skills_seed.json` MUST đổi (`seed-2026-11-23`).
- **FR-003**: `skills_excluded.json` MUST liệt kê mọi thẻ từ 20 tin chưa có mã, mỗi dòng có khóa đã bỏ dấu, cách viết gốc, lý do không rỗng và số tin; `load_exclusions` MUST từ chối khóa trùng, thiếu lý do, thiếu cách viết, số tin nhỏ hơn 1, danh sách rỗng, khóa không bỏ dấu, hoặc khóa cũng nằm trong từ vựng.
- **FR-004**: `tools/vocab/skill_gaps.py` MUST chỉ đọc; `--after FILE` MUST in báo cáo "sau" ngoại tuyến từ file `gaps`.
- **FR-005**: Ánh xạ và quét MUST không mở kết nối mạng.
- **FR-006**: `load_vocabulary` MUST từ chối mã ghép có phần không nằm nguyên văn trong cụm đã bỏ dấu (lượt nhắc không được có vị trí -1).
- **FR-007**: `skill_gaps.py --after` MUST đọc đầu ra thô của chính script và lọc theo `--min-postings` (mặc định 20).

### Key Entities

- **Mã kỹ năng**: định danh `snake_case`, có tên Anh, tên Việt, bí danh. Không đổi lược đồ DB.
- **Danh sách loại trừ**: thẻ cố ý không có mã, kèm lý do và số tin bằng chứng.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 673 khóa từ 20 tin ở snapshot 2026-11-20: 515 có mã, 158 bị loại trừ có lý do, 0 bỏ sót.
- **SC-002**: Tỷ lệ lượt nhắc thẻ (khóa từ 20 tin) có mã: 56,4% → 69,1% (26.750 → 32.802 trên 47.444).
- **SC-003**: Từ vựng 225 → 265 mã; `version` đổi; test chặn mạng xanh.

## Assumptions

- Quyết định 304 thẻ ở `quyet-dinh-2026-11-20.json` là của người dùng duyệt; thay đổi này làm đúng theo đó, chỉ lệch ở ba khóa trùng và `tu duy logic` (xem [data-model.md](data-model.md)).
- Số "sau" theo vai trò đo trên prod sau deploy. Việc đó cần ssh vào VPS nên không làm được trong PR.
- Từ vựng v1 có giảng viên duyệt (#96) sẽ thay `skills_seed.json`; mã `snake_case` giữ định dạng.
