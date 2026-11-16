# Feature Specification: Tỷ lệ kỹ năng theo ô, nhóm kỹ năng theo θ

**Feature Branch**: `gh-101-ty-le-ky-nang`

**Created**: 2026-11-16

**Status**: Implemented, chờ merge. Đã sửa 2026-11-16 theo quyết định của người dùng (hợp kỹ năng của cụm, mẫu số chỉ cụm đã quét, quét lại khi từ vựng đổi) và review.

**Input**: GitHub issue [#101](https://github.com/Dyuedu/HaiDoIT/issues/101) — [DAT.29] Skill rates per cell, and skill groups by θ. Phục vụ #111, #113, #117, #118, #119, #121. Đọc sau này bởi #103, #151, #168 (API), #106 (chọn ô), #102 (đóng băng θ).

## Bối cảnh

`job_posting_facts.skills` đã có mã kỹ năng và số lượt nhắc từ #283, nhưng chưa có bảng tỷ lệ theo ô. API chỉ được tra `stat_*` theo khóa (AD-5, AD-7), nên tỷ lệ phải được tính sẵn ở bước `aggregate`. ARCHITECTURE-SPINE AD-5 (rule bổ sung): bảng phải dày, mỗi kỹ năng một hàng trong mỗi ô, kể cả tỷ lệ 0; hàng thiếu là lỗi dữ liệu, vì kỹ năng thiếu hàng rơi khỏi mẫu số của mức khớp FR-28.

## Quyết định

- Bảng mới `haido.stat_skill_rates` (migration `0009_haido_skill_rates`). Tên số nhiều như `stat_cells`; AC và AD-5 viết `stat_skill_rate` (xem Điểm mở).
- Khóa `(snapshot_id, role, branch, seniority, years, scope, skill)`; khóa ô là khóa chính của `stat_cells` và là khóa ngoại tới nó, nên mỗi số gắn snapshot và ô thật (AC 2). Chỉ mục phụ `(snapshot_id, skill)` cho #168 đọc một kỹ năng qua các vai trò.
- Cột `n_with`, `n_scanned`, `rate`, `vocab_version`:
  - `n_with`: số cụm của ô nhắc kỹ năng ít nhất một lần.
  - `n_scanned`: số cụm của ô đã được quét kỹ năng (mẫu số), cùng một giá trị ở mọi hàng của ô.
  - `rate = n_with / n_scanned`, 0 khi `n_scanned = 0`.
  - `vocab_version`: phiên bản từ vựng của các dữ kiện đã đọc (D3).
- **`n_scanned` là cỡ mẫu của chính phép đo này** (AD-17 `n_with_value`), không phải `n` của ô (số cụm, kể cả cụm chưa quét). #151 và #168 chặn theo ngưỡng 30 bằng cách tra `n_scanned` theo khóa; không cần đọc `stat_cells`. Một ô có `n = 80` mà chỉ 20 cụm đã quét thì mẫu của kỹ năng là 20, dưới ngưỡng.
- Ô nào: chỉ phạm vi toàn quốc (`vn`), số năm `any`, nhánh `all`; vai trò là `all` và từng vai trò; cấp là `all` và từng mã của `level_options` (gồm nhóm `entry` và `unknown`). Chỉ viết cho ô có trong `stat_cells` cùng snapshot. `stat_cells` hiện chỉ có `branch = all` (population từ chối nhánh khác), nên chưa có ô nhánh.
- Dày: mỗi ô có đúng một hàng cho mỗi mã trong từ vựng hiện hành (`load_seed_skills`, 225 mã tại `seed-2026-11-11`). Mã trong dữ kiện cũ mà không còn trong từ vựng thì bị bỏ, không tạo hàng.
- Đếm: cùng dân số với `n` của ô. Cùng cửa sổ 60 ngày kết thúc ở S, cùng gộp cụm (#100), cùng nguồn bị loại (#263), cùng nhãn phân loại. Cửa sổ và việc khớp ô là hai hàm dùng chung của phép 3 (`postings_in_window`, `matches_cell` trong `population.py`); `skill_rates.py` không có bản thứ hai. Phép tính từ chối chạy nếu `n` tự đếm lại không bằng `n` của ô.
- **D1, hợp kỹ năng của cụm.** Cụm nhắc kỹ năng X khi BẤT KỲ thành viên nào của cụm (trong cửa sổ) đã quét và nhắc X; cụm vẫn đếm một lần. Nhãn vai trò, cấp, thành phố và số năm của cụm không đổi: vẫn lấy từ tin đại diện. Bước `aggregate` đưa mỗi cụm một tin mang hợp kỹ năng của mọi thành viên; hàm thuần `aggregate_skill_rates` cũng hợp kỹ năng của các tin cùng `cluster_id` khớp ô. Lượt nhắc nhiều lần vẫn tính một.
- **D2, mẫu số chỉ gồm cụm đã quét.** Cụm đã quét khi có ít nhất một thành viên có `skills` khác NULL; `{}` (quét, không thấy mã nào) là đã quét. Cụm mà mọi thành viên NULL (dữ kiện cũ trước #283) không vào tử số lẫn mẫu số. Hệ quả: `n_scanned <= n`, kiểm bằng CHECK `n_with <= n_scanned` ở DB và kiểm ở `replace_stats` (mẫu không vượt dân số của ô). Vòng kiểm lại `n` bằng `stat_cells.n` giữ nguyên; `n_scanned` là số khác, `<= n`.
- **D3, quét lại khi từ vựng đổi.** `job_posting_facts.vocab_version` (nullable, thêm ở migration 0009) ghi phiên bản từ vựng đã dùng để quét `skills` lúc ingest. Lúc ingest, dữ kiện trong cửa sổ 60 ngày mà `vocab_version` khác phiên bản hiện hành (NULL tính là khác) được thêm một phiên bản dữ kiện mới, giống cách xử lý lệch `classify_version` (#283, `_refresh_labels`). `aggregate` đóng dấu `stat_skill_rates.vocab_version` bằng phiên bản của các dữ kiện nó đọc. Nếu các dữ kiện đã quét của những cụm được đếm (thành viên thấy trong cửa sổ) mang hơn một `vocab_version`, hoặc khác phiên bản hiện hành (kể cả NULL ở dữ kiện có `skills`), bước dừng bằng `StepError` yêu cầu chạy lại `ingest`. Khác nhãn luật (aggregate tự phân loại lại từ trường đóng), kỹ năng cần văn bản JD mà aggregate không có, nên từ chối chứ không đoán. Dữ kiện chưa quét (`skills` NULL) không chặn: nó không đóng góp gì vào tỷ lệ.
- Nhóm (phép 4): `group_skills` ở `haido_core/domain/skill_groups.py`. `rate >= theta_core` là CORE, `rate >= theta_common` là COMMON, còn lại RARE. θ truyền vào mỗi lần gọi. Từ chối θ không hữu hạn hoặc ngoài [0, 1], `theta_common > theta_core`, tỷ lệ không hữu hạn hoặc ngoài [0, 1], và `skill_id` trùng trong một yêu cầu. Nhóm không lưu trong bảng, tính lúc đọc từ θ; #102 quyết định θ được ghi và đóng băng ra sao. FR-9: đổi θ thì nhóm đổi ở lần tính kế tiếp, không cần chạy lại `aggregate`.
- Ghi trong cùng transaction với các hàng `stat_*` khác; chạy lại ra cùng hàng; S đã `published` hay `partial` thì từ chối (như cũ). `replace_stats` bắt buộc nhận `skill_rates` (không có giá trị mặc định).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bảng tỷ lệ dày (Priority: P1)

**Why this priority**: AC 1 của #101.

**Independent Test**: `tests/steps/test_dat29_aggregate_skill_rates_step.py`, `tests/domain/test_dat29_skill_rates.py`.

**Acceptance Scenarios**:

1. **Given** một snapshot có tin, **When** chạy `aggregate`, **Then** mỗi ô `(vai trò, cấp, vn, any)` có đúng 225 hàng, một cho mỗi mã từ vựng, kể cả hàng `rate = 0`.
2. **Given** một snapshot không có tin nào, **Then** mọi ô vẫn có đủ hàng, `n_with = 0`, `n_scanned = 0`, `rate = 0`.
3. **Given** `n_scanned` của ô là 0, **Then** `rate` là 0, không chia cho 0.
4. **Given** hai lượt nhắc cùng một kỹ năng trong một tin, hoặc hai tin cùng cụm, **Then** `n_with` tăng một.

### User Story 2 - Mỗi số gắn snapshot và ô (Priority: P1)

**Why this priority**: AC 2 của #101.

**Independent Test**: test DB và test bước.

**Acceptance Scenarios**:

1. **Given** bảng, **Then** khóa chính là `snapshot_id, role, branch, seniority, years, scope, skill`, mọi cột `NOT NULL`, có khóa ngoại tới `stat_cells` và chỉ mục phụ `(snapshot_id, skill)`.
2. **Given** một hàng tỷ lệ cho ô không có trong `stat_cells`, **Then** DB từ chối.
3. **Given** mọi hàng sau `aggregate`, **Then** `rate = n_with / n_scanned` (0 khi `n_scanned = 0`), `n_with <= n_scanned <= n` của đúng ô đó trong `stat_cells`.
4. **Given** ràng buộc, **Then** `n_with >= 0`, `n_with <= n_scanned` và `0 <= rate <= 1`.
5. **Given** `replace_stats` nhận hàng có `n_scanned` lớn hơn `n` của ô, **Then** `ValueError`, không ghi gì.

### User Story 3 - Cùng dân số với ô (Priority: P1)

**Independent Test**: test bước.

**Acceptance Scenarios**:

1. **Given** tin cách S 59 ngày và 60 ngày, **Then** chỉ tin 59 ngày vào `n_with`.
2. **Given** hai nguồn cùng công ty, chức danh, **Then** một cụm; kỹ năng của cụm là hợp kỹ năng của hai tin (D1).
3. **Given** tin của nguồn bị loại (`linkedin`) hoặc ngoài IT, **Then** không vào `n` và không vào `n_with`.
4. **Given** cấp `entry`, **Then** gồm các cấp thành viên (`intern`, `fresher`, `junior`).

### User Story 4 - Chạy lại, chốt, lỗi (Priority: P1)

**Acceptance Scenarios**:

1. **Given** S còn `open`, **When** chạy lại, **Then** ra cùng hàng, không nhân đôi (và giống hệt qua `PYTHONHASHSEED` 0 và 1).
2. **Given** S `published` hoặc `partial`, **Then** `SnapshotClosedError`, không ghi gì.
3. **Given** lỗi sau khi ghi, **Then** rollback, giữ hàng cũ.
4. **Given** migration, **Then** nâng cấp và hạ cấp (bỏ bảng mới và cột `vocab_version`) chạy được; `alembic heads` một đầu.

### User Story 5 - Nhóm theo θ (Priority: P1)

**Why this priority**: tên issue, phép 4.

**Independent Test**: `tests/domain/test_dat29_skill_groups.py`.

**Acceptance Scenarios**:

1. **Given** tỷ lệ đúng bằng `theta_core` hoặc `theta_common`, **Then** vào nhóm cao hơn (`>=`).
2. **Given** danh sách rỗng, **Then** tuple rỗng.
3. **Given** một yêu cầu hay một lô, **Then** một tuple hay tuple cùng độ dài; kết quả một lô bằng kết quả từng cái; giữ thứ tự đầu vào.
4. **Given** θ khác nhau ở hai lần gọi, **Then** nhóm khác nhau; hàm không đọc config.
5. **Given** tỷ lệ hoặc θ là NaN, vô hạn hay ngoài [0, 1], `theta_common > theta_core`, hoặc `skill_id` trùng trong một yêu cầu, **Then** `ValueError`. Giá trị đúng 0 và 1 hợp lệ.

### User Story 6 - Hợp kỹ năng của cụm (Priority: P1)

**Why this priority**: quyết định D1.

**Independent Test**: test bước (hai nguồn) và test hàm thuần.

**Acceptance Scenarios**:

1. **Given** cụm hai nguồn mà tin đại diện không có mô tả (`skills` NULL) còn tin kia nhắc Python, **Then** `n_with(python) = 1`, `n_scanned = 1`.
2. **Given** cả hai tin cùng nhắc Python, **Then** `n_with(python) = 1`, không phải 2.
3. **Given** hai tin nhắc kỹ năng khác nhau (Docker ở một tin, SQL ở tin kia), **Then** cụm tính cả hai.
4. **Given** nhãn cấp, vai trò của cụm, **Then** vẫn của tin đại diện (không đổi).

### User Story 7 - Mẫu số chỉ cụm đã quét (Priority: P1)

**Why this priority**: quyết định D2.

**Independent Test**: test bước và test hàm thuần.

**Acceptance Scenarios**:

1. **Given** ô có 3 cụm, một cụm chưa quét (mọi thành viên NULL), **Then** `n = 3`, `n_scanned = 2`, `rate = n_with / 2`.
2. **Given** cụm quét mà không thấy mã nào (`{}`), **Then** vẫn vào `n_scanned`.
3. **Given** ô mà mọi cụm chưa quét, **Then** `n_scanned = 0`, `rate = 0`, không lỗi.
4. **Given** mọi hàng của một ô, **Then** `n_scanned` giống nhau và `<= n`.

### User Story 8 - Quét lại khi từ vựng đổi (Priority: P1)

**Why this priority**: quyết định D3.

**Independent Test**: `tests/steps/test_gh283_ingest_classify.py` (ingest), `tests/steps/test_dat29_aggregate_skill_rates_step.py` (aggregate).

**Acceptance Scenarios**:

1. **Given** từ vựng đổi phiên bản, **When** chạy `ingest` kế tiếp, **Then** dữ kiện trong cửa sổ được thêm phiên bản mới mang `vocab_version` mới; chạy lại cùng từ vựng không thêm gì.
2. **Given** dữ kiện cũ có `vocab_version` NULL trong cửa sổ, **Then** cũng được quét lại.
3. **Given** các dữ kiện đã quét của cụm được đếm mang hơn một `vocab_version`, hoặc khác hiện hành, hoặc NULL, **When** chạy `aggregate`, **Then** `StepError` yêu cầu chạy lại `ingest` và không ghi gì.
4. **Given** mọi dữ kiện cùng một phiên bản, **Then** `stat_skill_rates.vocab_version` bằng phiên bản đó.
5. **Given** dữ kiện chưa quét, hoặc nằm ngoài cửa sổ, hoặc thuộc tin không được đếm, **Then** không chặn.

### Edge Cases

- Dữ kiện cũ chưa có `skills` (`NULL`): không vào tử số lẫn mẫu số (D2); ô vẫn đủ hàng.
- Mã kỹ năng đã bị gỡ khỏi từ vựng: bỏ.
- Cụm có thành viên đã quét và thành viên chưa quét: cụm đã quét, kỹ năng là của các thành viên đã quét.
- Thành viên của cụm không thấy trong cửa sổ (nhưng cụm có thành viên khác trong cửa sổ): không góp kỹ năng, vì ingest không quét lại nó.

## Requirements

- **FR-001**: `aggregate` MUST ghi một hàng cho mỗi (ô, kỹ năng) trong phạm vi nêu trên.
- **FR-002**: `rate` MUST bằng `n_with / n_scanned` của chính hàng đó, và `n_scanned` MUST không vượt `n` của `stat_cells` cùng khóa.
- **FR-003**: `group_skills` MUST đúng chữ ký ở `REGISTRY.md`, một chữ ký duy nhất.
- **FR-004**: Nhóm MUST NOT được lưu trong bảng.
- **FR-005**: Kỹ năng của cụm MUST là hợp kỹ năng của các thành viên đã quét; cụm chưa quét MUST NOT vào tử số hay mẫu số.
- **FR-006**: `aggregate` MUST từ chối khi dữ kiện đã quét mang phiên bản từ vựng khác hiện hành hoặc lẫn nhiều phiên bản.

## Success Criteria

- **SC-001**: Số hàng mỗi snapshot = số ô × 225 (18 vai trò × 9 cấp × 225 = 36.450). Chi phí đo được (`tools/bench_skill_rates.py`, 5.600 dữ kiện Zipf, 7 lượt, trung vị): tổng bước `aggregate` tăng từ 5,43 s (5,22–11,33) lên 7,43 s (7,29–9,32), +2,0 s, 1,37 lần. Trong đó tính tỷ lệ 0,42 s (0,41–0,45) và ghi (`replace_stats`) tăng từ 1,14 s (0,82–7,22) lên 2,71 s (2,44–4,92), 36.450 hàng, +1,57 s: ghi là phần chính, tính toán không đáng kể. Khoảng rộng ở các lượt tắt và lượt đầu là nhiễu của máy (lượt đầu nguội); trung vị ổn định. Chưa tối ưu vì bước chạy mỗi đêm một lần; số chi tiết ở `tdd.md`.
- **SC-002**: Tỷ lệ của một ô dựa trên đúng các cụm đã quét; `n_scanned` cho #151 và #168 chặn ngưỡng 30 bằng một lần tra khóa.

## Điểm mở

- Hàng cho ô nhánh chưa có: `stat_cells` chưa có nhánh nên bảng chỉ có `branch = all`. #106 cần ô nhánh × cấp và sẽ phải thêm chúng ở cả hai bảng.
- Chưa có tỷ lệ kỹ năng theo thành phố và theo mốc số năm (chỉ `vn` và `any`).
- Tên bảng: code dùng `stat_skill_rates` (số nhiều như `stat_cells`), còn AC của #101 và AD-5 viết `stat_skill_rate`. Người đọc ở #103/#151 dùng tên trong code; nên sửa chữ trong AC và AD-5 cho khớp.
- Khoảng cách tên nhóm: API (`SkillRateRow.group`) dùng `core`, `common`, `company_specific`; `REGISTRY.md` và `SkillBand` dùng CORE, COMMON, RARE. Không đổi API ở đây (#103/#151 cần chốt một cách gọi).
- θ không được lưu ở đâu cả: bảng này không có cột nhóm và không đọc θ. Việc ghi và đóng băng θ là của #102.
