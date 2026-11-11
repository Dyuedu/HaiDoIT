# Feature Specification: Hình response của lộ trình học và dữ liệu giả

**Feature Branch**: `gh-212-hinh-lo-trinh-hoc`

**Created**: 2026-11-12

**Status**: Implemented, chờ merge. Đợt 2 (2026-11-12) sửa theo review: xem `tdd.md`.

**Input**: GitHub issue [#212](https://github.com/Dyuedu/HaiDoIT/issues/212) — Agree the learning-path response shape and add fake data. Phục vụ story #121 (US-C1: biết nên học gì trước cho vai trò đã chọn) và cũng phải đủ cho story #122 (so sánh hai hướng: "N of M skills on this path", số tin entry-level của từng vai trò; task #220, #221).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Một hình response cho màn lộ trình và bước dựng lộ trình (Priority: P1)

Người làm màn lộ trình (#217), người làm bước dựng lộ trình thật (#213, #216) và người viết lời dẫn (#218) dựng trên cùng một hình: `GET /api/v1/learning-path?role=&level=&have=` trả các kỹ năng đã xếp sẵn theo chặng, mỗi kỹ năng có tỷ lệ xuất hiện.

**Why this priority**: AC thứ nhất của #212 ("The response lists skills in stages, each with a share").

**Independent Test**: `tests/api/test_fr22_learning_path.py`.

**Acceptance Scenarios**:

1. **Given** API chạy nguồn giả, **When** gọi `learning-path?role=backend&level=entry`, **Then** body là `Envelope[LearningPathData]`, `data.status = ready`, `data.stages` đánh số 1..k, mỗi kỹ năng có `skill`, `rate`, `group`, `foundation_for`, `prerequisite_for`, `have`, `blurb`, `resource`.
2. **Given** một chặng, **When** đọc thứ tự kỹ năng, **Then** theo (nhóm cốt lõi trước thường gặp, tỷ lệ giảm dần, mã A–Z) (FR-22); không kỹ năng nào đứng ở chặng sớm hơn hoặc bằng chặng của kỹ năng nó cần.
3. **Given** `rate` của mọi kỹ năng, **When** so với `skill-rates` cùng vai trò, cấp, ô, **Then** cùng giá trị, cùng `display`, cùng `group` (story #121: khớp hồ sơ kỹ năng #111).
4. **Given** `have=java,sql`, **When** gọi, **Then** hai kỹ năng đó có `have = true`, `have_on_path = 2`, `path_size = M`, `current_stage` là chặng đầu còn kỹ năng `have = false`; thứ tự và số chặng không đổi.
5. **Given** `have` chứa mã đúng định dạng nhưng không có trên lộ trình, **When** gọi, **Then** mã đó nằm ở `have_ignored` (xếp A–Z), không tính vào `have_on_path`; mã trùng chỉ tính một lần.
6. **Given** `have` có mã sai định dạng, hoặc hơn 200 mã, hoặc phần tử rỗng, **When** gọi, **Then** 422 `invalid_query`. `have` rỗng coi như không gửi.
7. **Given** vai trò chưa có lộ trình đã rà soát, **When** gọi, **Then** 200, `status = not_ready`, không có chặng, `current_stage = null`, `have_on_path = path_size = 0`, envelope và `meta` vẫn đủ (`entry_cell_id` có trong `meta.cells`).
8. **Given** ô entry của vai trò dưới 30 tin và ô vai trò × mọi cấp đủ 30 (backend ở cấp `intern`), **When** gọi, **Then** `data.cell_id` là `vn.backend` (quay về trong cùng vai trò, FR-19), mọi `rate` có số, `meta.cells[cell_id].fallback_label` ghi tỷ lệ tin Mid trở lên tính từ chính `seniority_mix` của ô, `entry_cell_id` vẫn trỏ ô entry và `meta.cells[entry_cell_id].n` là số tin entry-level (#221).
8a. **Given** không ô nào trong vai trò đạt 30 tin (data_engineer: ô entry n = 4, `vn.data_engineer` n = 22), **When** gọi, **Then** lộ trình vẫn `ready` (đã rà soát) nhưng mọi `rate` là `null_data`, `group = null`, `foundation_for` rỗng; `cell_id` là ô cuối đã thử trong vai trò (`vn.data_engineer`); `fallback_label` nói cả hai ô chưa đạt 30 tin nên chưa hiển thị tỷ lệ. `cell_id` không bao giờ là ô của vai trò khác (FR-19).
8b. **Given** bản giả không có ô tỷ lệ phủ hết kỹ năng của lộ trình (data_engineer ở `senior`), **When** gọi, **Then** 404 `unknown_cell`, không bao giờ 500: bản giả chỉ ném `UnknownCell` với yêu cầu hợp lệ.
9. **Given** dữ liệu sai hợp đồng (rate khác ô, chặng không liền nhau, sai thứ tự, mã lặp, tham chiếu không có trên lộ trình, kỹ năng đứng trước kỹ năng nó cần, đếm sai, `not_ready` mà có chặng), **When** dựng `LearningPathData`, **Then** lỗi.
10. **Given** cùng yêu cầu gọi hai lần, **Then** body giống hệt (có test `determinism`).

---

### User Story 2 - Dữ liệu giả có sẵn cho màn hình (Priority: P1)

**Why this priority**: AC thứ hai của #212 ("Fake data is available to the screen").

**Independent Test**: `tests/api/test_fr22_learning_path.py`, `tests/api/test_ad17_web_fixtures.py`, `web/tests/fr22-learning-path-fixture.test.ts`.

**Acceptance Scenarios**:

1. **Given** dữ liệu giả, **When** liệt kê vai trò, **Then** `backend` entry sẵn sàng (n >= 30, ít nhất 3 chặng, 12–16 kỹ năng, có kỹ năng nền tảng, cốt lõi và thường gặp xen trong một chặng), `backend` intern sẵn sàng qua `vn.backend` (có số, nhãn ghi tỷ lệ Mid trở lên), `data_engineer` entry sẵn sàng nhưng mọi tỷ lệ `null_data`, mọi vai trò khác của `config/rules.toml` là `not_ready`. `ai_ml` entry là `not_ready` nhưng có `skill-rates` để mở hồ sơ kỹ năng (#111); `qa` là `not_ready` không có hồ sơ kỹ năng.
2. **Given** mọi mã kỹ năng trong `skill-rates` và `learning-path` giả, **When** so với `haido_core/vocab/skills_seed.json`, **Then** đều thuộc danh sách mồi, và đều là snake_case.
3. **Given** lời dẫn và tên tài liệu (`resource.title`) của mọi kỹ năng trong fixture, **When** quét bằng `haido_core/vocab/prepared_text.py`, **Then** không có chữ số ngoài tên công nghệ (khớp nguyên từ), không có `%`; lời dẫn không nói bao nhiêu tin đòi kỹ năng. Số viết bằng chữ ngoài phạm vi. Cổng CI của #138 nên dùng lại hàm này.
4. **Given** `web/tests/fixtures/learning-path-*.json` (backend, backend có `have`, backend intern, data_engineer, data_engineer có `have` theo ví dụ FR-24, ai_ml, qa), **When** so với response của API giả, **Then** giống hệt.
5. **Given** mọi vai trò của `config/rules.toml` × mọi `LevelCode`, có và không có `have`, **When** quét, **Then** mọi response là 200 hoặc 404, không bao giờ 500, và mọi 200 giữ các điều kiện: mọi kỹ năng `core`/`common` của ô tỷ lệ có trên lộ trình, kỹ năng nhóm khác `core`/`common` có `foundation_for` không rỗng, `cell_id` thuộc vai trò đã chọn.
6. **Given** đồ thị `requires` có mã không có nút hoặc chu trình, **When** tính chặng, **Then** `PathGraphError` rõ ràng (không `KeyError`, không `RecursionError`); fixture thật không có lỗi đó.
7. **Given** hồ sơ {java, sql, git} và vai trò Data Engineer (FR-24), **When** gọi, **Then** `sql` và `git` có `have = true`, `have_on_path = 2` trên `path_size = 11`, `java` nằm ở `have_ignored`.

---

### Edge Cases

- Cấp bậc khác `entry` của vai trò sẵn sàng (backend, data_engineer): bản giả chỉ có ô `entry`, như `skill-rates` giả, nên 404 `unknown_cell`. Lộ trình dùng đúng ô mà `skill-rates` của cùng (vai trò, cấp) dùng.
- Vai trò `not_ready` ở mọi cấp hợp lệ: 200 `not_ready`; `entry_cell_id` là ô entry của vai trò bất kể cấp.
- Vai trò không có trong `config/rules.toml` (kể cả `all`): 404 `unknown_cell`, như `city-shares`.
- Kỹ năng nền tảng (FR-20): có thể thuộc nhóm `company_specific`; chỉ kỹ năng nền tảng mới được như vậy.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `GET /api/v1/learning-path?role=<mã>&level=<cấp>&have=<mã,mã,...>`; `level` dùng `LevelCode` như `city-shares`, mặc định `entry` (DEC-8, #134); `have` tùy chọn, tối đa 200 mã (AD-22), mỗi mã theo `SKILL_CODE_PATTERN`.
- **FR-002**: `data` có `role`, `level`, `status` (`ready` hoặc `not_ready`), `cell_id` (null khi `not_ready`), `entry_cell_id`, `stages`, `current_stage`, `have_on_path`, `path_size`, `have_ignored`.
- **FR-003**: Mỗi chặng `{stage, skills}`; mỗi kỹ năng `{skill, rate, group, foundation_for, prerequisite_for, have, blurb, resource{title,url}}`. `rate` là `Stat` `skill_rate` có `cell_id = data.cell_id`.
- **FR-004**: Máy chủ trả lộ trình đã xếp (AD-7) và tự đếm `have_on_path`, `path_size`, `current_stage`, `have_ignored` (AD-22). Web không sắp xếp, không đếm.
- **FR-005**: **Hợp đồng cho #213: chặng là thuộc tính của nút kỹ năng**, không phụ thuộc `have`. Lọc theo `have` không bao giờ đổi chặng hay thứ tự của kỹ năng; chỉ đổi `have`, `current_stage`, `have_on_path`, `have_ignored`.
- **FR-006**: Khóa xếp trong chặng theo FR-22: (nhóm: cốt lõi, thường gặp, riêng công ty, ẩn; tỷ lệ giảm dần; mã A–Z). Không kỹ năng nào ở chặng sớm hơn hoặc bằng chặng của kỹ năng nó cần.
- **FR-007**: Lời dẫn là câu chữ viết sẵn, không có chữ số ngoài tên công nghệ, không `%` (FR-23, DEC-6 #132), không nói về tần suất trong tin tuyển dụng; tài nguyên là một link miễn phí, trung lập về nhà cung cấp khi kỹ năng trung lập.
- **FR-008**: Phép có biến chọn nguồn `HAIDO_MARKET_SOURCE_LEARNING_PATH`, mặc định `fake`. `StatMarket.learning_path` trả `UnknownCell` cho tới #216.
- **FR-009**: Số tin entry-level của vai trò là `meta.cells[entry_cell_id].n`, có cả khi `cell_id` đã quay về ô khác (#221).

- **FR-010 (đối chiếu FR-20/FR-22)**: Response **giữ kỹ năng đã có** (`have = true`) trên lộ trình và tính chúng vào `path_size`, khác chữ "kỹ năng đã có không nằm trong lộ trình" của FR-20/FR-22. Lý do: #121 AC3 và #220/FR-24 cần "N of M skills on this path" và tô kỹ năng trùng hồ sơ; chặng là thuộc tính của nút nên `have` không đổi thứ tự (FR-005). Web tô kỹ năng đã có chứ không ẩn.
- **FR-011**: FR-19 trong vai trò: quay về chỉ đi vai trò × cấp rồi vai trò × mọi cấp; `cell_id` không bao giờ là ô của vai trò khác. Không ô nào đạt 30 thì mọi `rate` là `null_data`, `group = null`, lộ trình vẫn `ready`, `cell_id` là ô cuối đã thử. Ở bước vai trò × mọi cấp, nhãn ghi tỷ lệ tin Mid trở lên.
- **FR-012**: `foundation_for` = các kỹ năng `core` hoặc `common` trên lộ trình có kỹ năng này là tổ tiên, bắc cầu qua `prerequisite_for` (cháu cũng tính); `prerequisite_for` chỉ cạnh trực tiếp. Rỗng khi nhóm bị ẩn. Kỹ năng riêng công ty trên lộ trình phải có `foundation_for` không rỗng.
- **FR-013**: Hợp đồng AD-17 có một ngoại lệ có tên: dấu `Ordinal` cho vị trí và số đếm trên chính các mã kỹ năng của người dùng (AD-22): `PathStage.stage`, `LearningPathData.current_stage`, `have_on_path`, `path_size`; không bao giờ là số tin, tỷ lệ, tỷ trọng hay n. Chỉ miễn khi kiểu đúng là `Ordinal` hoặc `Ordinal | None` và giá trị là `int` không âm (không `bool`); kiểu ghép vẫn bị kiểm; tập trường bị khóa bằng test.
- **FR-014**: `have`: trần 200 đếm trên số mã gửi lên trước khi loại trùng; chỉ đọc một tham số `have` (lặp thì lấy cái cuối); 200 mã dài có thể làm URL khoảng 8 KB. Web chỉ lọc đầu vào (bỏ trùng, bỏ mã sai định dạng, rồi cắt 200), không đếm hay sắp xếp.

### Key Entities

- **Kỹ năng trên lộ trình**, **Chặng**, **Lộ trình** (xem `data-model.md`).

## Success Criteria *(mandatory)*

- **SC-001**: `uv run pytest -q` xanh, không skip vì thiếu DB.
- **SC-002**: `cd web && npm run test` xanh, có `tests/fr22-learning-path-fixture.test.ts`.
- **SC-003**: `docs/api/openapi.json` và `docs/api/envelope-meta.md` mô tả route mới.

## Assumptions

- Mã kỹ năng trong dữ liệu giả chỉ lấy từ `skills_seed.json`. Bản mồi thiếu `spark`, `airflow`, `pandas`; #96 (bộ từ vựng v1) nên thêm.
- Đợt 1 để data_engineer quay về `vn.all.entry` (mọi vai trò); đợt 2 bỏ vì FR-19 giữ quay về trong vai trò. Demo quay về có số là backend ở `intern` (`vn.backend`, n = 157); demo "chưa đủ dữ liệu" là data_engineer ở `entry`. Tỷ lệ của `vn.backend` trong `fake_market.json` là số giả do đợt 2 đặt (157 tin, nhóm theo θ), không phải số đo thật.
- Hàm kiểm lời dẫn ở `haido_core/vocab/prepared_text.py` là nơi #138 nên lấy quy tắc FR-23 cho cổng CI (`tools/gates/check_gates.py` chưa đổi ở #212). Số viết bằng chữ ngoài phạm vi. Tên công nghệ như "Java 17" được che nguyên từ; "Java 17 năm" vẫn qua vì "Java 17" là đúng một tên công nghệ.
- `cell_id = null` khi `not_ready` (không có ô nào cho tỷ lệ).
