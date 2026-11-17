# Feature Specification: Hình response của một kỹ năng qua các vai trò và dữ liệu giả

**Feature Branch**: `gh-166-hinh-ky-nang-theo-vai-tro`

**Created**: 2026-11-17

**Status**: Implemented, chờ merge. Sửa theo review ngày 2026-11-17 (đợt 2): cỡ mẫu của phép đo, `mentioned` theo mọi cấp, `data.level`, prod chọn `stat`, bộ chốt chống lệch.

**Input**: GitHub issue [#166](https://github.com/Dyuedu/HaiDoIT/issues/166) — Agree the skill-across-roles response shape and add fake data. Phục vụ story #113 (US-A4: thấy vai trò nào dùng kỹ năng mình đã có). Đọc sau này bởi #168 (số thật từ `stat_skill_rates` của #101), #169 (màn hình), #170 (test màn hình). #167 (tìm kỹ năng song ngữ) đã gộp vào #207: `GET /api/v1/skills`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Một hình response cho màn hình và bước đếm (Priority: P1)

Người làm màn (#169) và người làm bước trả số thật (#168) dựng trên cùng một hình: `GET /api/v1/skill-roles?skill=<mã>` trả mỗi vai trò một dòng, có tỷ lệ tin entry-level của vai trò nhắc kỹ năng, kèm cỡ mẫu của phép đo.

**Why this priority**: AC thứ nhất của #166. Nếu hai bên tự đoán hình thì màn chạy trên dữ liệu giả nhưng vỡ khi nối số thật.

**Independent Test**: `tests/api/test_fr09_skill_roles.py` kiểm schema và route; `tests/api/test_ad17_routes.py` kiểm route mới trả Envelope; `tests/domain/test_ad17_envelope.py` kiểm quy tắc cỡ mẫu dùng chung.

**Acceptance Scenarios**:

1. **Given** nguồn giả, **When** gọi `GET /api/v1/skill-roles?skill=python`, **Then** body là `Envelope[SkillRolesData]`: `data` có `skill` (mã và tên song ngữ), `level` (`entry`), `levels`, `mentioned`, `rows`; mỗi dòng có `role` và `share`.
2. **Given** một dòng, **When** tra `meta.cells[share.cell_id]`, **Then** `n` là số tin của ô (cùng số với `newcomer-roles`) và `n_by_measure.skill_count` là cỡ mẫu của tỷ lệ; `share.cell_id = vn.<role>.entry`, `share.kind = skill_rate`.
3. **Given** vai trò có cỡ mẫu của phép đo (`skill_count`) dưới 30, **When** API trả, **Then** `share.display = null_data`, `share.value = null`, kể cả khi `n` của ô từ 30 trở lên; `skill_count` vẫn có ở `meta.cells` để màn ghi "not enough data (skill_count/30)".
4. **Given** vai trò đủ mẫu mà không tin nào nhắc kỹ năng, **Then** `share.value = 0`, `display = shown`, không phải null.
5. **Given** `share` sai loại hoặc sai `cell_id`, vai trò lặp, `rows` hoặc `levels` rỗng, `level` khác `entry`, **When** dựng `SkillRolesData`, **Then** lỗi.
6. **Given** `rows` sai thứ tự (có tỷ lệ tăng dần, hòa không theo mã, `null_data` đứng trước dòng có tỷ lệ), hoặc `mentioned = false` mà có dòng hiện tỷ lệ lớn hơn 0 (dù các dòng khác bằng 0), **When** dựng `SkillRolesData`, **Then** lỗi. Thứ tự giữa các dòng `null_data` (cỡ mẫu giảm dần rồi mã vai trò) cần `meta` nên do `Envelope` kiểm qua `SkillRolesData.check_against_meta`; nguồn thật (#168) cũng bị kiểm.
7. **Given** `skill` không có hoặc sai định dạng, **When** gọi, **Then** 422 `invalid_query`. **Given** `skill` đúng định dạng nhưng không có trong bộ từ vựng, **Then** 404 `unknown_skill`.
8. **Given** `data.level`, **When** #169 mở hồ sơ kỹ năng của một vai trò, **Then** dùng `level = entry` làm tham số của `/ho-so-ky-nang?role=&level=` (trang #111) và của `skill-rates`; mã này có trong `level_options` của `config/rules.toml` và `LEVEL_OPTIONS` của web.

---

### User Story 2 - Dữ liệu giả có sẵn cho màn hình (Priority: P1)

Màn đọc được dữ liệu giả đúng hình ngay hôm nay, qua proxy `/api` khi API chạy nguồn `fake`, và qua fixture khi chạy test web.

**Why this priority**: AC thứ hai của #166. #169 dựng được từ ngày đầu, trước khi #168 có số thật.

**Independent Test**: `tests/api/test_fr09_skill_roles.py` kiểm nội dung giả; `tests/api/test_ad17_web_fixtures.py` so fixture web với response; `web/tests/fr09-skill-roles-fixture.test.ts` kiểm fixture khớp kiểu TypeScript.

**Acceptance Scenarios**:

1. **Given** dữ liệu giả, **When** so tập vai trò của `skill-roles` với `roles` của `config/rules.toml`, **Then** bằng nhau (17 vai trò). Fixture lệch config (thiếu hay thừa vai trò, thiếu ô entry) là lỗi khởi tạo `ValueError` nêu rõ chỗ lệch, không phải `KeyError` lúc gọi.
2. **Given** `python`, **Then** có vai trò đủ mẫu có tỷ lệ dương, hai vai trò dưới 30 trở lên (`null_data`), và vai trò đủ mẫu có tỷ lệ đúng 0 (`mobile`, n = 30).
3. **Given** `figma`, **Then** thứ hạng khác `python`, và vai trò có tỷ lệ thật cao nhất (`ui_ux`) nằm dưới ngưỡng nên bị ẩn, không dẫn đầu.
4. **Given** `abap` (mã hợp lệ, không tin nào nhắc ở cấp nào), **Then** `mentioned = false`, mọi dòng đủ mẫu bằng 0.
5. **Given** `sap` (không tin entry-level nào nhắc, nhưng có tin ở cấp khác), **Then** `mentioned = true` và mọi dòng hiện bằng 0.
6. **Given** vai trò `game` có n của ô = 43 nhưng chỉ 12 tin được quét kỹ năng, **Then** dòng `game` là `null_data` với X = 12 (cỡ mẫu của phép đo), không phải 43.
7. **Given** mọi kỹ năng của fixture, **Then** `share.value` bằng số nhắc chia `skill_count` của ô (khi `shown`), số nhắc không vượt `skill_count`, `skill_count` không vượt `n`, số nhắc ở mọi cấp không nhỏ hơn tổng số nhắc entry-level, mã kỹ năng thuộc bộ từ vựng.
8. **Given** response, **When** đọc thứ tự, **Then** dòng có tỷ lệ trước (giảm dần, hòa theo mã vai trò), rồi dòng `null_data` (cỡ mẫu của phép đo giảm dần, hòa theo mã vai trò).
9. **Given** `machine_learning`, **Then** `name_en = Machine Learning`, `name_vi = Học máy`: nhãn song ngữ không đổi chỗ hai tên.
10. **Given** mã trong bộ từ vựng mà bản giả chưa có số (`java`), **Then** 404 `unknown_cell` có ngày snapshot.
11. **Given** `web/tests/fixtures/skill-roles-{python,figma,abap,sap,machine_learning}.json`, **When** so với response của API giả, **Then** giống hệt.
12. **Given** `fetchSkillRoles` nhận 404 `unknown_skill`, 404 `unknown_cell` hoặc 422 `invalid_query`, **Then** `retryable = false`; lỗi khác `retryable = true`.

---

### User Story 3 - Prod không lặng lẽ phục vụ số giả (Priority: P2)

Production phải thấy 404 `unknown_cell` (chưa có số thật) thay vì số giả cho đến khi #168 nối số thật; compose local giữ bản giả để smoke của CI chạy trên DB rỗng.

**Why this priority**: số giả trong production là số bịa với người dùng thật. Mặc định `fake` của mã chỉ an toàn khi compose prod đặt rõ nguồn, như #146 và #162 đã làm.

**Independent Test**: `tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py` đọc hai file compose; `tests/api/test_fr09_skill_roles.py` kiểm `StatMarket` từ chối.

**Acceptance Scenarios**:

1. **Given** nguồn `stat`, **When** gọi `skill_roles`, **Then** 404 `unknown_cell` không có ngày snapshot (như `learning_path`), không bao giờ trả số giả.
2. **Given** `deploy/compose.prod.yml`, **Then** `HAIDO_MARKET_SOURCE_SKILL_ROLES = stat`.
3. **Given** `deploy/compose.local.yml`, **Then** biến này chưa đặt hoặc là `fake`.

---

### Edge Cases

- Vai trò không có tin nào (n = 0): vẫn có dòng, `null_data`; ô `vn.<role>.entry` có n = 0 và `skill_count` = 0.
- `mentioned = true` mà mọi dòng hiện đều 0: hợp lệ khi tin nhắc nằm ở ô dưới ngưỡng bị ẩn hoặc ở cấp khác entry-level.
- Ô có `n` từ 30 trở lên nhưng `skill_count` dưới 30 (ít tin được quét kỹ năng): `null_data`. Bản giả có đúng một ô như vậy (`vn.game.entry`, 43 và 12).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `GET /api/v1/skill-roles?skill=<mã>` nhận một tham số `skill` (snake_case, tối đa 40 ký tự, theo `SKILL_CODE_PATTERN`) và trả `Envelope[SkillRolesData]`.
- **FR-002**: Cấp bậc cố định là nhóm `entry` (DEC-8: Intern, Fresher, Junior). `data.level = "entry"`; `data.levels` lấy từ `level_groups` của `config/rules.toml`, không viết cứng ở nguồn.
- **FR-003**: `data.skill` là `{code, name_en, name_vi}` lấy từ bộ từ vựng (`haido_core.vocab.skills`), để màn ghi kỹ năng đã dùng.
- **FR-004**: `rows` có đúng một dòng cho mỗi vai trò của `config/rules.toml`. `share` là `Stat` `kind = skill_rate`, `cell_id = vn.<role>.entry`. Cỡ mẫu của tỷ lệ là `meta.cells[cell_id].n_by_measure.skill_count`; `meta.cells[cell_id].n` là số tin của ô. Dưới `min_sample` (30) theo `skill_count`: `null_data` theo `suppression_for`.
- **FR-005**: Thứ tự dòng do máy chủ quyết (AD-22), theo Scenario US2.8. Schema kiểm phần có tỷ lệ; `Envelope` kiểm cả phần `null_data` qua `check_against_meta`.
- **FR-006**: `data.mentioned` do máy chủ tính: `false` khi không tin nào, ở cấp nào, nhắc kỹ năng (AC 4 của #113). Schema chặn `mentioned = false` kèm bất kỳ dòng hiện tỷ lệ dương.
- **FR-007**: Không câu hay nhãn nào trong `data` có chữ số (DEC-6, #132), trừ tên công nghệ ở `data.skill.name_en` và `name_vi`. Số chỉ nằm ở `Stat` và `meta`.
- **FR-008**: Lỗi: 404 `unknown_skill` (mã ngoài bộ từ vựng, `snapshot_date = null`), 404 `unknown_cell` (nguồn chưa có số cho mã hợp lệ), 422 `invalid_query`.
- **FR-009**: Phép có biến chọn nguồn riêng `HAIDO_MARKET_SOURCE_SKILL_ROLES`, mặc định `fake` trong mã; `compose.prod.yml` đặt `stat`, `compose.local.yml` giữ `fake`. `StatMarket.skill_roles` trả 404 `unknown_cell` đến #168.
- **FR-010**: `meta` như mọi response số: ngày và trạng thái snapshot, nguồn, nguồn lỗi, ngưỡng, lưu ý độ phủ, `cells`.

### Key Entities

- **Dòng kỹ năng theo vai trò**: `role`, `share`.
- **Ô entry-level**: `vn.<role>.entry`, cùng ô với `newcomer-roles`: một ô, một `n`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv run pytest -q` xanh, có `tests/api/test_fr09_skill_roles.py`.
- **SC-002**: `cd web && npx vitest run` xanh, có `tests/fr09-skill-roles-fixture.test.ts`.
- **SC-003**: `docs/api/openapi.json` và `docs/api/envelope-meta.md` mô tả route mới, mã lỗi `unknown_skill`, `data.level` và cỡ mẫu `skill_count`.

## Quyết định (người điều phối chốt, 2026-11-17)

Đợt 1:

- Tên route `skill-roles`, kebab-case như `skill-rates`, `newcomer-roles`; phép đọc `skill_roles(*, skill)`; biến nguồn `HAIDO_MARKET_SOURCE_SKILL_ROLES`.
- `unknown_skill` là mã lỗi mới, vì màn cần phân biệt "mã không có trong bộ từ vựng" (không thử lại) với `unknown_cell` ("chưa có số cho kỹ năng này"). Kiểm bộ từ vựng nằm ở route, một chỗ cho mọi nguồn.
- `mentioned` thay cho việc web tự suy từ các dòng, vì ô dưới ngưỡng bị ẩn vẫn có thể có tin nhắc kỹ năng.

Đợt 2 (theo review, 2026-11-17):

1. **Cỡ mẫu của phép đo.** `meta.cells[cell_id].n` giữ nguyên là số tin của ô, vì cùng ô `vn.<role>.entry` đã được `newcomer-roles` phục vụ với n là mọi tin entry-level: một ô không được có hai giá trị n. Cỡ mẫu của tỷ lệ kỹ năng là `n_scanned` của #101 (số tin đã quét kỹ năng; `n_with / n_scanned` là tỷ lệ). Nó nằm ở `meta.cells[cell_id].n_by_measure.skill_count`. Tái dùng khóa `skill_count` đã có (AD-17 `n_with_value`: `envelope-meta.md` ghi "số tin có giá trị của từng thước đo: `skill_count`...", và fixture đã đặt `skill_count` cho mọi ô), không thêm khóa `skill_rate`, vì đó đúng là số tin có giá trị về kỹ năng. `suppression_for` và `Envelope` kiểm `display` của mọi `Stat` `skill_rate` theo `skill_count` (thiếu khóa thì theo `n`), qua hàm chung `sample_n` ở `haido_core/domain/envelope.py`. Các loại khác (`composition_share`, `level_share`, `percentile`) vẫn theo `n` của ô, nên `city-shares`, `newcomer-roles` không đổi. `skill-rates` và `learning-path` dùng chung quy tắc: ở bản giả `skill_count = n` mọi ô trừ `vn.game.entry`, nên chỉ ô đó đổi (xem Ghi chú). Web `rowN` trả `skill_count` (thiếu thì `n`): đó là X trong "not enough data (X/30)".
   - Ghi chú cho #151/#149 (`skill-rates` khi dùng số thật): cùng câu hỏi `n` hay `n_scanned`. `skill_rate` của `skill-rates` cũng phải ghi `skill_count = n_scanned` vào `meta.cells`, không thì Envelope sẽ kiểm theo `n` và có thể từ chối. Phiên này không đổi `skill-rates` thật, chỉ bản giả của ô `vn.game.entry` (`skill_count` 43 xuống 12) bị ẩn tỷ lệ.
2. **`mentioned` theo đúng AC 4 của #113.** "Một kỹ năng mà không tin hiện tại nào nhắc" nghĩa là không tin nào ở BẤT KỲ cấp nào nhắc, không chỉ entry. Fixture có `mentions_all_levels[kỹ năng]` (số tin ở mọi cấp nhắc kỹ năng); `mentioned = mentions_all_levels > 0`. Có ca một kỹ năng 0 tin entry-level ở mọi vai trò nhưng có tin ở cấp khác (`sap`): `mentioned = true`, mọi dòng 0 hoặc ẩn. Với #168: tính từ hàng ô mọi cấp của `stat_skill_rates` (role = `all`, seniority = `all`, years = `any`, scope = `vn`, tức `cell_id` `vn.all`, theo `aggregate_skill_rates` của #101): `mentioned = n_with > 0`. Không cộng `n_with` của các ô entry. Validator `SkillRolesData` giữ: `mentioned = false` không đi với bất kỳ dòng hiện tỷ lệ dương, và có test cho dòng pha trộn 0 và dương.
3. **`data.level = "entry"`** (mã nhóm cấp) để #169 mở hồ sơ kỹ năng của #111 (`/ho-so-ky-nang?role=&level=`). Đã kiểm: trang chấp nhận `level` thuộc `LEVEL_OPTIONS` của `web/lib/labels.ts`, gồm `entry`; API `skill-rates` cũng nhận `entry`. Không phải sửa #111.
4. **Prod đặt `HAIDO_MARKET_SOURCE_SKILL_ROLES=stat`** ở `deploy/compose.prod.yml`: `StatMarket` từ chối, 404 `unknown_cell` đến #168, thay vì phục vụ số giả cho người dùng thật. `compose.local.yml` giữ `fake` để smoke của CI chạy trên DB rỗng. Thay quyết định đợt 1 "compose chưa đặt biến". Hệ quả cần biết: đến #168, production không có màn này (404).
5. **Phủ bản giả**: thêm `machine_learning` (Học máy) để kiểm nhãn song ngữ; giữ `python`, `figma`, `abap`; thêm `sap` cho ca `mentioned` mọi cấp. Mã và tên lấy từ `haido_core/vocab/skills_seed.json`.
6. **Chống lệch**: test chốt mọi kỹ năng của fixture có đúng các vai trò của `config/rules.toml` và ô entry cho từng vai trò; bộ nạp giả báo `ValueError` rõ khi lệch; `SkillRolesData` cũng kiểm thứ tự dòng `null_data` (cỡ mẫu của phép đo giảm dần rồi mã) để nguồn thật của #168 phải khớp.
7. **Web**: `fetchSkillRoles` coi 422 `invalid_query` là không thử lại. `web/lib/skill-rates.ts` (#149 của Dyuedu) có cùng việc `retryable` chưa xét `invalid_query`: để nguyên, báo người làm #149.
8. **DEC-6**: tên kỹ năng là tên công nghệ, được miễn như DEC-6 và AD-8 miễn tên công nghệ. Test chữ số của #170 phải bỏ `data.skill.name_en` và `data.skill.name_vi`, không bỏ gì khác. Có test: mọi chuỗi trong `data` ngoài hai tên này không có chữ số. `meta.coverage_notes` là chuỗi dùng chung cho mọi route (có thể chứa số nguồn), ngoài phạm vi test này.
9. **Mã FR**: giữ FR-9 trong tên test. US-A4 không có mã FR riêng; FR-9 là tỷ lệ kỹ năng theo ô, đúng con số màn này hiện. #170 nên dùng lại FR-9.

## Assumptions

- US-A4 không có mã FR riêng trong PRD; số tỷ lệ kỹ năng theo ô là FR-9, nên test mang mã FR-9 và AD-17.
- Mã kỹ năng giả `python`, `figma`, `abap`, `sap`, `machine_learning` có trong `haido_core/vocab/skills_seed.json` (`seed-2026-11-11`).
- Số nhắc giả không đại diện thị trường thật; chỉ cần nhất quán (số nhắc / `skill_count`) và đủ trường hợp.
