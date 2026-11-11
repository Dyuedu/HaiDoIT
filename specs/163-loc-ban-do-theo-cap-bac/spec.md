# Feature Specification: Lọc bản đồ theo cấp bậc

**Feature Branch**: `gh-163-loc-ban-do-theo-cap-bac`

**Created**: 2026-11-11

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#163](https://github.com/Dyuedu/HaiDoIT/issues/163) — The map has a level filter. It opens on the default level recorded on #134, and changing the level updates the table and the chart together. Phục vụ story [#112](https://github.com/Dyuedu/HaiDoIT/issues/112). Quyết định ràng buộc: [#134](https://github.com/Dyuedu/HaiDoIT/issues/134) (cấp mặc định và cách chia cấp), [#260](https://github.com/Dyuedu/HaiDoIT/issues/260) (không đổi ngưỡng, θ, lưu ý độ phủ).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bản đồ mở ở cấp mặc định của #134 (Priority: P1)

Người mới vào nghề mở bản đồ và thấy bộ chọn cấp bậc đang ở "Mới vào nghề" (nhóm Intern + Fresher + Junior). Các lựa chọn đúng danh sách #134: nhóm mới vào nghề, từng cấp (Intern, Fresher, Junior, Mid, Senior, Lead), "Chưa ghi cấp bậc" và "Mọi cấp bậc". Số trên bản đồ là số của nhóm đó, nên khớp với mọi màn khác nói "mới vào nghề".

**Why this priority**: AC thứ nhất của #163. Câu hỏi của story #112 là "ở cấp của tôi", nên mặc định phải là cấp của người dùng chứ không phải mọi cấp.

**Independent Test**: Mở `MapScreen` với API giả. Lượt gọi đầu có `level=entry`, nút "Mới vào nghề" có `aria-pressed="true"`, danh sách nút khớp `level_options` trong `config/rules.toml` cộng `all`.

**Acceptance Scenarios**:

1. **Given** trang vừa mở, **When** lượt gọi đầu đi ra, **Then** URL là `/api/v1/city-shares?role=all&level=entry` và nút "Mới vào nghề" được chọn.
2. **Given** bộ chọn cấp bậc, **When** đọc danh sách nút, **Then** thứ tự là entry, intern, fresher, junior, mid, senior, lead, unknown, all, nhãn tiếng Việt, mỗi nút là `<button aria-pressed>` cao tối thiểu 44px.
3. **Given** `config/rules.toml` có nhóm `entry = [intern, fresher, junior]`, **When** `aggregate` chạy, **Then** ô `entry` có n bằng tổng n của ba cấp và `unknown` không nằm trong nhóm.
4. **Given** API gọi không có `level`, **When** route xử lý, **Then** trả số của mọi cấp như trước (tương thích ngược); web luôn gửi `level` rõ ràng.

---

### User Story 2 - Đổi cấp bậc thì bảng và biểu đồ đổi cùng lúc (Priority: P1)

Người dùng bấm một cấp khác. Màn hiện "Đang tải số liệu…" thay cho số cũ, rồi biểu đồ 2D và bảng cùng hiện số của cấp mới, từ cùng một envelope. Response về muộn của cấp cũ bị bỏ.

**Why this priority**: AC thứ hai của #163. Bảng và biểu đồ lệch nhau là lỗi mà story #112 cấm ("cùng bộ số").

**Independent Test**: Test web đổi cấp rồi so số ở lối 2D và lối Bảng; test Python so `stat_cells` và `stat_city_shares` của từng cấp với số đếm tay.

**Acceptance Scenarios**:

1. **Given** bản đồ ở cấp `entry`, **When** bấm "Senior", **Then** gửi `level=senior`, hiện trạng thái đang tải, rồi cả thanh và bảng hiện số của `senior`.
2. **Given** người dùng bấm "Senior" rồi "Lead" nhanh, **When** response của "Senior" về sau cùng, **Then** màn vẫn hiện số của "Lead".
3. **Given** vai trò đã chọn và cấp đã đổi, **When** đổi vai trò, **Then** cấp được giữ nguyên và lượt gọi mang cả `role` lẫn `level`.
4. **Given** một vai trò không có tin nào ở cấp đã chọn, **When** API trả `unknown_cell`, **Then** màn hiện thông báo kèm ngày snapshot, bộ chọn cấp vẫn bấm được.
5. **Given** `aggregate` chạy cho snapshot S, **When** đọc `stat_city_shares` theo (role, level), **Then** mỗi (role, level) có đủ năm dòng thành phố và tổng tỷ trọng bằng 1; khi n của cấp đó bằng 0 thì toàn bộ rơi vào `unknown`.
6. **Given** `level` ngoài danh sách cấu hình, **When** gọi API, **Then** 422 `invalid_query` không lặp lại giá trị đã gửi.

---

### User Story 3 - Thành phố dưới 30 tin ở cấp đã chọn bị làm mờ như bản đồ mọi cấp (Priority: P1)

Ở cấp đã chọn, thành phố có dưới 30 tin vẫn có số nhưng mờ, có nhãn cỡ mẫu nhỏ, ô bảng ghi "chưa đủ dữ liệu". Quy tắc đúng như bản đồ mọi cấp; ngưỡng đọc từ `config/rules.toml`, không đổi.

**Why this priority**: AC thứ ba của #163 và là quy tắc ẩn số của AD-17.

**Independent Test**: Cấp có Đà Nẵng n < 30 cho `display = low_sample_shown`; test web kiểm thanh mờ (`data-low-sample`), nhãn "Cỡ mẫu nhỏ (n = … < 30)" và ô bảng.

**Acceptance Scenarios**:

1. **Given** thành phố có n = 29 ở cấp `entry`, **When** API trả `city-shares`, **Then** `display = low_sample_shown` và `meta.cells[cell_id].n = 29`; n = 30 thì `shown`.
2. **Given** `display = low_sample_shown`, **When** web vẽ, **Then** thanh mờ có sọc, nhãn cỡ mẫu nhỏ luôn hiện, phần trăm chỉ hiện khi trỏ hoặc focus, ô bảng ghi "chưa đủ dữ liệu" và n.
3. **Given** mẫu nhỏ được quyết bằng n của ô (thành phố, vai trò, cấp), **When** cấp đổi, **Then** trạng thái mờ đổi theo n của cấp mới, không theo n của mọi cấp.

---

### Edge Cases

- Cấp `unknown` ("Chưa ghi cấp bậc") không thuộc nhóm `entry` (#134).
- Vai trò × cấp không có tin: API trả 404 `unknown_cell` kèm ngày snapshot (cùng hành vi vai trò không có tin).
- Snapshot cũ đã chốt trước khi có tính năng chỉ có cấp `all` và không sửa được: API chọn snapshot theo cấp, nên cấp khác `all` lùi về snapshot mới nhất có hàng của cấp đó (không đoán số từ ô khác); `all` vẫn đọc snapshot mới nhất. Nếu không snapshot nào có hàng của cấp đã chọn thì 404 `unknown_cell` không có ngày, thông báo nói chưa có snapshot công bố nào được tính cho cấp bậc này (không đổ lỗi cho vai trò). Cấu hình `level_groups` sai (không phải bảng, tên nhóm hay mã ngoài `a-z0-9_`) và nhóm có thành viên trùng bị từ chối; hạ cấp migration 0005 bỏ cả ô `stat_cells` theo cấp.
- Nguồn giả chỉ phục vụ `entry` và `all`; cấp khác trả `unknown_cell`.
- Ô của một cấp luôn có `seniority_mix` chỉ gồm các cấp thuộc nó và cộng lại bằng `n`.
- Số tin của tin cụm (#100) và nguồn bị loại (#263) giữ nguyên: mỗi cụm đếm một lần ở đúng một cấp.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `config/rules.toml` có `level_options` (thứ tự hiển thị, không gồm `all`) và bảng `level_groups` (`entry = [intern, fresher, junior]`). `haido_core/config.py` kiểm và báo lỗi tiếng Việt khi sai; `config_version` tăng. `min_sample`, `theta_*`, `coverage_notes` không đổi (#260).
- **FR-002**: `aggregate` ghi, cho mỗi vai trò (cùng `all`) và mỗi cấp trong `all` + `level_options`, năm dòng tỷ trọng thành phố và sáu ô (năm thành phố cộng `vn`). Ô nhóm có n bằng tổng n các cấp của nhóm. Cùng một transaction, cửa sổ 60 ngày, cụm, nguồn bị loại và `stat_sources` giữ nguyên.
- **FR-003**: `stat_city_shares` có thêm cột `seniority` trong khóa chính; hàng cũ nhận `all`. Migration mới nối vào head hiện tại.
- **FR-004**: `GET /api/v1/city-shares` nhận `level` tùy chọn, giá trị trong `all` + `level_options`; không gửi thì `all`; giá trị lạ là 422 `invalid_query`. `data.level` trả cấp đã dùng.
- **FR-005**: Mã ô của cấp khác `all` là `<scope>.<role>.<level>`; của `all` giữ `<scope>.<role>`. `display` do `suppression_for` quyết theo n của ô.
- **FR-006**: Nguồn giả phục vụ `entry` và `all` cho `all`, `ai_ml`, `backend`; cấp khác trả `unknown_cell`.
- **FR-007**: Web có bộ chọn cấp bậc, mặc định `entry`; đổi cấp gọi lại API với cả `role` và `level`, bỏ response muộn, bảng và biểu đồ dùng cùng envelope. Nhãn tiếng Việt ở `web/lib/labels.ts`, khớp config.
- **FR-008**: `docs/api/openapi.json` và `docs/api/envelope-meta.md` mô tả `level`, `data.level` và mã ô theo cấp.

### Key Entities

- **LevelOption**: mã cấp lọc được: `all`, một nhóm (`entry`) hoặc một cấp (`intern` … `unknown`).
- **LevelGroup**: nhóm cấp trong config; thành viên rời nhau nên n của nhóm là tổng n của thành viên.
- **Ô theo cấp**: (snapshot, vai trò, cấp lọc, phạm vi) với `n` và `seniority_mix`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Mở bản đồ thấy cấp `entry` được chọn và số của `entry`; một lần bấm đổi cấp thì bảng và biểu đồ cùng đổi.
- **SC-002**: Với mọi (vai trò, cấp), tổng tỷ trọng thành phố bằng 1 và n của ô nhóm bằng tổng n của các cấp thành viên.
- **SC-003**: `uv run pytest -q`, `npm run test`, các cổng `check_gates.py`, `ruff`, `alembic heads` (một head) xanh; hai lần chạy `-m determinism` với `PYTHONHASHSEED=0` và `1` cho cùng kết quả.

## Assumptions

- Giá trị mặc định `entry` là của #134; web giữ hằng `DEFAULT_LEVEL` trong `web/lib/labels.ts` (web không đọc config), và test đối chiếu nhãn và thứ tự với `config/rules.toml`.
- Tỷ trọng thành phố của một cấp là n thành phố ở cấp đó chia n toàn quốc ở cấp đó, đúng công thức của bản đồ mọi cấp.
- Tỷ trọng mô hình làm việc (remote, hybrid) là #164, không nằm ở đây.
- Issue GitHub #163 là spec sản phẩm. Thư mục này là SDD để implement.
