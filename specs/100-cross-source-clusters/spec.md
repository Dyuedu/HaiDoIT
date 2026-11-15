# Feature Specification: Gộp tin trùng chéo nguồn thành cụm

**Feature Branch**: `gh-100-cum-cheo-nguon`

**Created**: 2026-11-10

**Status**: Implemented. Cập nhật 2026-11-11 theo #163: ô theo cấp bậc lọc được cũng đếm cụm (một cụm một lần, ở cấp của đại diện). Không AC nào của #100 đổi. Cập nhật 2026-11-12 theo #280: ô theo mốc số năm cũng đếm cụm, số năm của cụm lấy từ tin đại diện như nhãn.

**Input**: GitHub issue [#100](https://github.com/Dyuedu/HaiDoIT/issues/100) — Operation 7 collapses cross-source duplicates into clusters. Later counts use clusters, and the representative is chosen by an explicit rule.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bản đồ đếm một tin đăng trên nhiều sàn là một (Priority: P1)

Người mở bản đồ thấy tỷ trọng thành phố. Cùng một tin của một công ty, cùng chức danh, đăng trên hai sàn, chỉ góp một vào số đếm.

**Why this priority**: Tiêu chí đầu của issue là phép tổng hợp đếm cụm, không đếm bản ghi thô. Không có bước này thì một tin hai sàn làm phình tỷ trọng.

**Independent Test**: Hai tin khác nguồn, cùng công ty và chức danh sau khi chuẩn hóa, cho ra một cụm. Dân số của ô vai trò đó là 1.

**Acceptance Scenarios**:

1. **Given** tin ITviec và tin TopCV cùng công ty "FPT" và chức danh "Backend Dev", **When** gộp cụm, **Then** còn một cụm và số đếm vai trò backend là 1.
2. **Given** hai tin khác chức danh của cùng công ty, **When** gộp cụm, **Then** vẫn là hai cụm.
3. **Given** tin thiếu công ty hoặc thiếu chức danh, **When** gộp cụm, **Then** tin đó đứng một mình, không bị gộp và không bị xóa.

---

### User Story 2 - Đại diện cụm theo quy tắc tường minh (Priority: P1)

Thành phố, cấp bậc và vai trò của cụm lấy từ một tin đại diện. Quy tắc chọn đại diện đọc được, không phụ thuộc thứ tự dữ liệu trả về.

**Why this priority**: Tiêu chí thứ hai của issue. Không có đại diện thì cụm không biết lấy thành phố nào khi hai sàn ghi địa điểm khác nhau.

**Independent Test**: Cùng một cụm, đổi thứ tự đầu vào, đại diện không đổi. Đổi hạng nguồn, số trường hoặc URL thì đại diện đổi đúng thứ tự quy tắc.

**Acceptance Scenarios**:

1. **Given** ITviec đứng trước TopCV trong `sources.priority`, TopCV có nhiều trường hơn, **When** chọn đại diện, **Then** ITviec thắng.
2. **Given** hai tin cùng hạng nguồn, **When** một tin có nhiều trường thống kê hơn, **Then** tin nhiều trường thắng.
3. **Given** cùng hạng nguồn và cùng số trường, **When** so URL, **Then** URL có giá trị thắng URL trống, rồi URL xếp A–Z, rồi mã tin A–Z.
4. **Given** (thêm ở #163) đại diện của cụm là Junior và một thành viên khác là Senior, **When** `aggregate` ghi ô theo cấp bậc lọc được, **Then** cụm chỉ được đếm ở nhóm `entry` và cấp `junior`, không đếm ở `senior`; ô `all` vẫn đếm một lần.

---

### Edge Cases

- "Công ty TNHH FPT" và "FPT" là cùng công ty. "FPT Software" là công ty khác.
- "Java-Backend" và "Java Backend" là cùng chức danh. "Backend Dev" và "QA Tester" là hai tin.
- Tin không có khóa (thiếu công ty hoặc chức danh) không khớp cặp nào.
- Nguồn không có trong `sources.priority` xếp sau mọi nguồn có hạng.
- Cụm rỗng không phát sinh. Hai lần gọi cùng đầu vào ra cùng cụm và cùng đại diện.
- Phép so khớp không xóa tin. Tin không khớp vẫn còn là cụm một thành viên.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Phép tổng hợp đếm cụm. Hai tin cùng khóa danh tính dùng chung một `cluster_id`.
- **FR-002**: Khóa danh tính là công ty đã chuẩn hóa cộng chức danh đã chuẩn hóa. Thiếu một trong hai thì tin không vào cụm chung.
- **FR-003**: Chuẩn hóa gồm bỏ dấu, hạ chữ, bỏ dấu câu, gộp khoảng trắng, bỏ tiền tố "công ty" và token pháp lý (TNHH, CTCP, cổ phần, Inc, Ltd, LLC, JSC, Co) dù token đó đứng giữa tên.
- **FR-004**: Đại diện chọn theo thứ tự: hạng nguồn trong `sources.priority` (đứng trước thắng), số trường thống kê không rỗng (chức danh, công ty, địa điểm, kinh nghiệm, cấp bậc), URL không trống thắng URL trống rồi A–Z, mã tin A–Z.
- **FR-005**: Vai trò, thành phố, cấp bậc của cụm lấy từ tin đại diện. `last_seen` của cụm là ngày thấy gần nhất trong các thành viên.
- **FR-006**: Nguồn của mọi thành viên trong cụm được đếm vẫn được xét vào danh sách nguồn của snapshot.
- **FR-007**: `match_postings` trả khớp hoặc không khớp cho một cặp, theo phạm vi trong nguồn hoặc chéo nguồn. Phép không xóa tin.
- **FR-008**: Thứ hạng nguồn nằm trong `config/rules.toml`. Tăng `config_version` khi thêm khóa này.

### Key Entities

- **ClusterMember**: Một tin đem đi gộp. Có mã tin, nguồn, URL, công ty, chức danh, địa điểm, kinh nghiệm, cấp bậc.
- **Cluster**: Một cụm. Có `cluster_id` ổn định, mã tin đại diện, và các mã thành viên.
- **MatchDecision**: Kết quả một cặp. Có hai mã và cờ `matched`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Hai tin cùng khóa trên hai nguồn cho dân số ô bằng 1, và thành phố của ô là thành phố của đại diện.
- **SC-002**: Đảo thứ tự đầu vào không đổi đại diện và không đổi `cluster_id`.
- **SC-003**: Tin thiếu công ty hoặc chức danh vẫn được đếm như một cụm riêng.
- **SC-004**: `uv run pytest tests/domain/test_dat28_cluster.py` xanh, và các test tổng hợp hiện có vẫn xanh.

## Assumptions

- Tập kỹ năng của tin chưa nằm trong dữ kiện snapshot, nên khóa danh tính dùng công ty và chức danh, theo các repo công khai đã đối chiếu trong `research.md`. Jaccard tập kỹ năng không nằm trong issue #100.
- Hạng nguồn do cấu hình quyết. Bản đầu: itviec, topdev, vietnamworks, careerlink, itnavi, topcv, momo, zalo. Nguồn đứng trước là đại diện khi hòa các tiêu chí sau.
- Gộp theo khóa áp dụng cả hai tin cùng nguồn. Phép `match_postings` vẫn phân biệt phạm vi trong nguồn và chéo nguồn.
- Issue GitHub #100 là spec sản phẩm. Thư mục này là SDD để implement.
