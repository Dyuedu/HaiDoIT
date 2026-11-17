# Feature Specification: Phép 2, chọn ô và thứ tự quay về

**Feature Branch**: `gh-151-ty-le-ky-nang-that`

**Created**: 2026-11-17

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#106](https://github.com/Dyuedu/HaiDoIT/issues/106) — Operation 2: choose the cell and its fallback order. Phục vụ #111, #121, #125.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Một chỗ duy nhất quyết định ô nào được dùng (Priority: P1)

Mọi màn có số theo ô (hồ sơ kỹ năng, lộ trình, Soi tin) cần cùng một quyết định: ô được yêu cầu đủ mẫu thì dùng, không đủ thì quay về tập rộng hơn trong cùng phạm vi, và nói rõ đã dùng tập nào.

**Why this priority**: AC 1, 2, 3 của #106. Không có nó, #151 và #121 mỗi bên tự viết chuỗi quay về (AD-6).

**Independent Test**: `tests/domain/test_ad2_select_cell.py`.

**Acceptance Scenarios**:

1. **Given** ô được yêu cầu có cỡ mẫu từ `min_sample` trở lên, **When** gọi `select_cell`, **Then** trả chính ô đó, `label = None`, và không tra ô rộng hơn. (AC 1, 2)
2. **Given** `fresher` dưới ngưỡng, nhóm `entry` đủ, **When** gọi, **Then** trả ô `entry`, `n` của nó, nhãn gọi tên cả hai ô và n của cả hai; `order` là `fresher, entry, all`. (AC 2)
3. **Given** `fresher` và `entry` đều thiếu, `all` đủ, **When** gọi, **Then** trả ô `all`; với cấp mới vào nghề, nhãn ghi thêm tỷ lệ tin Mid trở lên tính từ `seniority_mix` của ô `all` (FR-19). Cấp `mid` quay về `all` thì không có câu này. (AC 2)
4. **Given** không ô nào đủ, **When** gọi, **Then** trả ô cuối cùng đã xét (`all`) với nhãn nói chưa tập nào đủ ngưỡng, kèm n của từng tập đã thử. (AC 2)
5. **Given** cấp `all`, **When** gọi, **Then** chỉ có một ứng viên.
6. **Given** truy vấn ở phạm vi `hanoi`, **When** gọi, **Then** mọi ô được tra và trả về đều ở `hanoi`; không bao giờ quay về `vn` (AD-6). Vai trò và snapshot cũng không đổi.
7. **Given** cùng truy vấn và cùng bảng ô, **When** gọi nhiều lần, một đối tượng hay một lô, **Then** cùng kết quả; một lô trả `tuple` cùng độ dài, đúng thứ tự đầu vào. (AC 3, AD-2)
9. **Given** người gọi truyền `sample_noun` (ví dụ "tin đọc được kỹ năng"), **When** sinh nhãn, **Then** mọi chỗ nhãn nêu n đều dùng danh từ đó ("Backend · Fresher chỉ có 26 tin đọc được kỹ năng (dưới 30), …", "(52 tin đọc được kỹ năng)"), để con số không trông như mâu thuẫn với `n` của ô. Mặc định là "tin". (đợt 2)
10. **Given** nhãn có câu "Mid trở lên", **When** tính tỷ lệ, **Then** mẫu số là mọi tin trong `seniority_mix` của ô, kể cả `unknown`, và làm tròn nửa lên (12,5% thành 13%). (đợt 2)
8. **Given** `CellStats.sample_n` khác `n`, **When** gọi, **Then** quyết định theo `sample_n` và `CellChoice.n` là `sample_n` của ô được chọn.

### Edge Cases

- Ô thiếu trong bảng tính như cỡ mẫu 0. `min_sample < 1` hoặc phần tử lô không phải `CellQuery` là `ValueError`.
- Yêu cầu có nhánh: mỗi bước thử nhánh trước rồi nhánh `all`. Nhánh chưa có dữ liệu ở bản chạy thật (`stat_cells.branch` luôn `all`), nên chỉ thành các ô thiếu.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Thân hàm duy nhất của `select_cell` ở `haido_core/domain/cells.py` (class `CellSelector`), gọi được cho một đối tượng và một lô (`as_batch`).
- **FR-002**: Thứ tự quay về: `(vai trò, cấp)`; nếu cấp thô thuộc một nhóm của `level_groups` thì `(vai trò, nhóm)`; rồi `(vai trò, all)`. Cấp `all` chỉ một ứng viên.
- **FR-003**: `CellChoice` thêm `order` (mọi ứng viên theo thứ tự) và `label: str | None` (`None` khi ô được yêu cầu đủ mẫu).
- **FR-004**: Nhãn tiếng Việt: ô được yêu cầu và n, ô đã dùng và n; ở bước `all` với cấp mới vào nghề, tỷ lệ tin Mid trở lên của ô đó. Tên vai trò và cấp do người gọi truyền vào (`names`).
- **FR-005**: Bảng ô đi vào qua `lookup(CellKey) -> CellStats | None` ở constructor; module chỉ import thư viện chuẩn và registry.

## Success Criteria *(mandatory)*

- **SC-001**: `uv run pytest tests/domain/test_ad2_select_cell.py tests/domain/test_ad2_registry.py -q` xanh; cổng AD-2 xanh (một Protocol, một thân hàm).

## Assumptions

- "Mid trở lên" là các cấp thô không thuộc nhóm nào và không phải `unknown` (Mid, Senior, Lead); người gọi truyền danh sách này.
- Fixture bản giả không dùng phép này (ghi ở `fake_market.py`); chỉ bản `stat` dùng.
