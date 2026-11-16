# Feature Specification: Tỷ lệ kỹ năng theo ô, nhóm kỹ năng theo θ

**Feature Branch**: `gh-101-ty-le-ky-nang`

**Created**: 2026-11-16

**Status**: Implemented, chờ merge

**Input**: GitHub issue [#101](https://github.com/Dyuedu/HaiDoIT/issues/101) — [DAT.29] Skill rates per cell, and skill groups by θ. Phục vụ #111, #113, #117, #118, #119, #121. Đọc sau này bởi #103, #151, #168 (API), #106 (chọn ô), #102 (đóng băng θ).

## Bối cảnh

`job_posting_facts.skills` đã có mã kỹ năng và số lượt nhắc từ #283, nhưng chưa có bảng tỷ lệ theo ô. API chỉ được tra `stat_*` theo khóa (AD-5, AD-7), nên tỷ lệ phải được tính sẵn ở bước `aggregate`. ARCHITECTURE-SPINE AD-5 (rule bổ sung): bảng phải dày, mỗi kỹ năng một hàng trong mỗi ô, kể cả tỷ lệ 0; hàng thiếu là lỗi dữ liệu, vì kỹ năng thiếu hàng rơi khỏi mẫu số của mức khớp FR-28.

## Quyết định

- Bảng mới `haido.stat_skill_rates` (migration `0009_haido_skill_rates`). Tên số nhiều như `stat_cells`; AC và AD-5 viết `stat_skill_rate`. Mở một điểm: người đọc ở #103/#151 dùng tên trong code.
- Khóa `(snapshot_id, role, branch, seniority, years, scope, skill)`; khóa ô là khóa chính của `stat_cells` và là khóa ngoại tới nó, nên mỗi số gắn snapshot và ô thật (AC 2).
- Cột `n_with` (số cụm trong ô nhắc kỹ năng ít nhất một lần), `rate` (`n_with / n` của ô; 0 khi n = 0), `vocab_version`.
- Ô nào: chỉ phạm vi toàn quốc (`vn`), số năm `any`, nhánh `all`; vai trò là `all` và từng vai trò; cấp là `all` và từng mã của `level_options` (gồm nhóm `entry` và `unknown`). Chỉ viết cho ô có trong `stat_cells` cùng snapshot. `stat_cells` hiện chỉ có `branch = all` (population từ chối nhánh khác), nên chưa có ô nhánh.
- Dày: mỗi ô có đúng một hàng cho mỗi mã trong từ vựng hiện hành (`load_seed_skills`, 225 mã tại `seed-2026-11-11`). Mã trong dữ kiện cũ mà không còn trong từ vựng thì bị bỏ, không tạo hàng.
- Đếm: cùng dân số với `n` của ô. Cùng cửa sổ 60 ngày kết thúc ở S, cùng gộp cụm (#100), cùng nguồn bị loại (#263), cùng nhãn phân loại. Cụm được đại diện bằng tin đại diện, giống nhãn và số năm của cụm: kỹ năng của cụm là tập mã của tin đại diện. Lượt nhắc nhiều lần vẫn tính một. Phép tính từ chối chạy nếu n tự đếm lại không bằng `n` của ô.
- Nhóm (phép 4): `group_skills` ở `haido_core/domain/skill_groups.py`. `rate >= theta_core` là CORE, `rate >= theta_common` là COMMON, còn lại RARE. θ truyền vào mỗi lần gọi. Nhóm không lưu trong bảng, tính lúc đọc từ θ; #102 quyết định θ được ghi và đóng băng ra sao. FR-9: đổi θ thì nhóm đổi ở lần tính kế tiếp, không cần chạy lại `aggregate`.
- Ghi trong cùng transaction với các hàng `stat_*` khác; chạy lại ra cùng hàng; S đã `published` hay `partial` thì từ chối (như cũ).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bảng tỷ lệ dày (Priority: P1)

**Why this priority**: AC 1 của #101.

**Independent Test**: `tests/steps/test_dat29_aggregate_skill_rates_step.py`, `tests/domain/test_dat29_skill_rates.py`.

**Acceptance Scenarios**:

1. **Given** một snapshot có tin, **When** chạy `aggregate`, **Then** mỗi ô `(vai trò, cấp, vn, any)` có đúng 225 hàng, một cho mỗi mã từ vựng, kể cả hàng `rate = 0`.
2. **Given** một snapshot không có tin nào, **Then** mọi ô vẫn có đủ hàng, `n_with = 0`, `rate = 0`.
3. **Given** `n` của ô là 0, **Then** `rate` là 0, không chia cho 0.
4. **Given** hai lượt nhắc cùng một kỹ năng trong một tin, hoặc hai tin cùng cụm, **Then** `n_with` tăng một.

### User Story 2 - Mỗi số gắn snapshot và ô (Priority: P1)

**Why this priority**: AC 2 của #101.

**Independent Test**: test DB và test bước.

**Acceptance Scenarios**:

1. **Given** bảng, **Then** khóa chính là `snapshot_id, role, branch, seniority, years, scope, skill`, mọi cột `NOT NULL`, và có khóa ngoại tới `stat_cells`.
2. **Given** một hàng tỷ lệ cho ô không có trong `stat_cells`, **Then** DB từ chối.
3. **Given** mọi hàng sau `aggregate`, **Then** `rate = n_with / n` của đúng ô đó trong `stat_cells`, và `n_with <= n`.
4. **Given** ràng buộc, **Then** `n_with >= 0` và `0 <= rate <= 1`.

### User Story 3 - Cùng dân số với ô (Priority: P1)

**Independent Test**: test bước.

**Acceptance Scenarios**:

1. **Given** tin cách S 59 ngày và 60 ngày, **Then** chỉ tin 59 ngày vào `n_with`.
2. **Given** hai nguồn cùng công ty, chức danh, **Then** một cụm, kỹ năng của tin đại diện.
3. **Given** tin của nguồn bị loại (`linkedin`) hoặc ngoài IT, **Then** không vào `n` và không vào `n_with`.
4. **Given** cấp `entry`, **Then** gồm các cấp thành viên (`intern`, `fresher`, `junior`).

### User Story 4 - Chạy lại, chốt, lỗi (Priority: P1)

**Acceptance Scenarios**:

1. **Given** S còn `open`, **When** chạy lại, **Then** ra cùng hàng, không nhân đôi (và giống hệt qua `PYTHONHASHSEED` 0 và 1).
2. **Given** S `published` hoặc `partial`, **Then** `SnapshotClosedError`, không ghi gì.
3. **Given** lỗi sau khi ghi, **Then** rollback, giữ hàng cũ.
4. **Given** migration, **Then** nâng cấp và hạ cấp (chỉ bỏ bảng mới) chạy được; `alembic heads` một đầu.

### User Story 5 - Nhóm theo θ (Priority: P1)

**Why this priority**: tên issue, phép 4.

**Independent Test**: `tests/domain/test_dat29_skill_groups.py`.

**Acceptance Scenarios**:

1. **Given** tỷ lệ đúng bằng `theta_core` hoặc `theta_common`, **Then** vào nhóm cao hơn (`>=`).
2. **Given** danh sách rỗng, **Then** tuple rỗng.
3. **Given** một yêu cầu hay một lô, **Then** một tuple hay tuple cùng độ dài; kết quả một lô bằng kết quả từng cái; giữ thứ tự đầu vào.
4. **Given** θ khác nhau ở hai lần gọi, **Then** nhóm khác nhau; hàm không đọc config.
5. **Given** tỷ lệ ngoài [0, 1] hoặc `theta_common > theta_core`, **Then** `ValueError`.

### Edge Cases

- Dữ kiện cũ chưa có `skills` (`NULL`): coi là không nhắc kỹ năng nào; ô vẫn đủ hàng.
- Mã kỹ năng đã bị gỡ khỏi từ vựng: bỏ.
- Tin có `skills` mà tin đại diện của cụm không có còn tin khác trong cụm có: dùng tin đại diện, như nhãn.

## Requirements

- **FR-001**: `aggregate` MUST ghi một hàng cho mỗi (ô, kỹ năng) trong phạm vi nêu trên.
- **FR-002**: `rate` MUST bằng `n_with / n` của `stat_cells` cùng khóa.
- **FR-003**: `group_skills` MUST đúng chữ ký ở `REGISTRY.md`, một chữ ký duy nhất.
- **FR-004**: Nhóm MUST NOT được lưu trong bảng.

## Success Criteria

- **SC-001**: Trên dữ liệu thật, số hàng mỗi snapshot = số ô × 225; thời gian `aggregate` tăng không đáng kể (số đo ở `tdd.md`).

## Điểm mở

- #106 cần ô nhánh × cấp; `stat_cells` chưa có nhánh, nên bảng này chỉ có `branch = all`.
- Tỷ lệ kỹ năng theo thành phố và theo mốc số năm chưa có.
- API (`SkillRateRow.group`) dùng `core`, `common`, `company_specific`; registry dùng CORE, COMMON, RARE. Không đổi API ở đây (#103/#151).
- Tên bảng: `stat_skill_rates` so với `stat_skill_rate` trong AC.
- Cụm dùng kỹ năng của tin đại diện; nếu tin đại diện thiếu `skills` mà tin khác trong cụm có thì thiếu. Hợp nhất kỹ năng các thành viên cần đổi quy tắc đại diện cho cả nhãn.
