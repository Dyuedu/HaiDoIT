# Feature Specification: Khóa hồ sơ trình duyệt và danh sách kỹ năng mồi

**Feature Branch**: `gh-205-khoa-ho-so`

**Created**: 2026-11-11

**Status**: Implemented, chờ merge.

**Input**: GitHub issue [#205](https://github.com/Dyuedu/HaiDoIT/issues/205) — The browser profile keys and the skill-code format are agreed, with a seed skill list, because #111, #121, #122, #123, and #124 all read the profile. Phục vụ story #120.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Một danh sách khóa đóng cho cả web (Priority: P1)

Dev của #206–#211 và #111, #121–#124 đọc và ghi hồ sơ qua một module duy nhất, `web/lib/haido-keys.ts`. Không ai tự đặt khóa `localStorage`.

**Why this priority**: AC thứ nhất của #205. AD-23 ghi rõ rủi ro: ba người dùng ba khóa tự đặt, rồi "Xóa hồ sơ" bỏ sót khóa của hai người kia mà mọi test đơn lẻ vẫn xanh.

**Independent Test**: `web/tests/ad23-haido-keys.test.ts` kiểm danh sách khóa, đọc/ghi hồ sơ, xóa theo tiền tố, và trường hợp bộ nhớ bị chặn. Cổng AD-23 trong `tools/gates/check_gates.py` chặn `localStorage` ở file khác.

**Acceptance Scenarios**:

1. **Given** module khóa, **When** liệt kê `HAIDO_KEYS`, **Then** có đúng `haido:profile`, `haido:session`, `haido:eval`, cùng tiền tố `haido:`.
2. **Given** hồ sơ `{v:1, role, level, skills}`, **When** ghi rồi đọc lại, **Then** nhận đúng hồ sơ đó.
3. **Given** hồ sơ có mã sai định dạng, mã trùng hoặc hơn 200 mã, **When** ghi, **Then** mã sai và mã trùng bị bỏ, danh sách bị cắt ở 200.
4. **Given** giá trị lưu là JSON hỏng, sai `v` hoặc sai kiểu, **When** đọc, **Then** nhận hồ sơ rỗng, không ném lỗi.
5. **Given** có khóa `haido:*` ngoài danh sách và khóa của trang khác, **When** gọi `clearHaidoData()`, **Then** mọi khóa `haido:*` mất, khóa của trang khác còn.
6. **Given** trình duyệt ném lỗi khi chạm `localStorage`, **When** đọc, ghi hoặc xóa, **Then** module không ném lỗi ra ngoài.

---

### User Story 2 - Danh sách kỹ năng mồi có sẵn trước khi màn hình đọc hồ sơ (Priority: P1)

Web lấy được danh sách kỹ năng song ngữ qua `GET /api/v1/skills` để hiện tên kỹ năng đã tick và để #207 tìm kiếm.

**Why this priority**: AC thứ hai của #205. Bộ từ vựng v1 (#96) chưa xong, nhưng #206–#208 cần mã và tên ngay trong Sprint 2.

**Independent Test**: `tests/core/test_fr13_skill_seed.py` kiểm file mồi. `tests/api/test_fr13_skills_route.py` kiểm route.

**Acceptance Scenarios**:

1. **Given** file `haido_core/vocab/skills_seed.json`, **When** nạp, **Then** mọi mã đúng định dạng, không trùng, có tên tiếng Anh, tên tiếng Việt và nguồn.
2. **Given** mọi tên và bí danh sau chuẩn hóa, **When** so với nhau, **Then** không có từ nào trỏ tới hai mã.
3. **Given** từ tìm "học máy", **When** tra trong tên và bí danh, **Then** ra `machine_learning`.
4. **Given** web gọi `GET /api/v1/skills`, **When** API trả lời, **Then** body là `{data: {vocab_version, skills: [{code, name_en, name_vi, aliases}]}}` và không chứa con số nào.

---

### Edge Cases

- Trình duyệt chặn bộ nhớ (Safari tắt cookie, chế độ riêng tư): module trả hồ sơ rỗng và `writeProfile` trả `false`. Giữ tick cho phiên hiện tại là việc của #210.
- Hồ sơ phiên bản khác `1`: đọc ra rỗng. Khi đổi hình hồ sơ thì tăng `PROFILE_VERSION` và thêm bước chuyển đổi.
- Mã vai trò hoặc cấp bậc sai định dạng: đọc thành `null`, không làm mất phần còn lại của hồ sơ.
- Route danh sách kỹ năng không có số nên không dùng Envelope. Test AD-17 khai nó trong `NUMBERLESS_ROUTES` và kiểm response không có số.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Mọi khóa `localStorage` có tiền tố `haido:` và nằm trong `HAIDO_KEYS` của `web/lib/haido-keys.ts`.
- **FR-002**: `haido:profile` lưu JSON `{"v":1,"role":<mã>|null,"level":<mã>|null,"skills":[<mã kỹ năng>,…]}`.
- **FR-003**: `haido:session` lưu mã phiên ẩn danh (FR-17). `haido:eval` lưu `"1"` khi vào bằng link thử nghiệm (FR-41, FR-45).
- **FR-004**: Mã kỹ năng khớp `^[a-z0-9]+(_[a-z0-9]+)*$`, tối đa 40 ký tự. Hồ sơ tối đa 200 mã, không trùng.
- **FR-005**: `clearHaidoData()` xóa theo tiền tố `haido:`.
- **FR-006**: Không hàm nào của module ném lỗi khi bộ nhớ bị chặn.
- **FR-007**: `haido_core/vocab/skills_seed.json` là nguồn duy nhất của danh sách mồi. `load_seed_skills()` kiểm định dạng, tên, nguồn, thứ tự và bí danh không trùng.
- **FR-008**: `GET /api/v1/skills` trả danh sách mồi theo thứ tự mã, kèm `vocab_version`.

### Key Entities

- **Hồ sơ trình duyệt**: vai trò, cấp bậc, danh sách mã kỹ năng đã tick. Một khóa duy nhất, nên ba màn hình của #208 luôn đọc cùng một hồ sơ.
- **Kỹ năng mồi**: `code`, `name_en`, `name_vi`, `aliases`, `source`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run pytest tests/core/test_fr13_skill_seed.py tests/api -q` xanh.
- **SC-002**: `cd web && npm test` xanh, có `tests/ad23-haido-keys.test.ts`.
- **SC-003**: Cổng AD-23 của `tools/gates/check_gates.py` là PASS.
- **SC-004**: `curl /api/v1/skills` trên máy và qua proxy `/api` của web trả 100 kỹ năng.

## Assumptions

- Mã vai trò là các mã trong `roles` của `config/rules.toml`. Mã cấp bậc là giá trị của `[labels.level]`. Module chỉ kiểm định dạng, không kiểm mã có trong danh sách: danh sách vai trò đổi theo config.
- #96 sẽ thay `skills_seed.json` bằng bộ từ vựng v1. Mã đã có giữ nguyên để hồ sơ đã lưu và link đã chia sẻ không hỏng.
