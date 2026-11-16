# Feature Specification: Cổng lời dẫn không số dùng chung một quy tắc

**Feature Branch**: `gh-138-cong-loi-dan-khong-so`

**Created**: 2026-11-16

**Status**: Implemented, chờ merge. Có một chỗ lệch với AC 4 của issue theo quyết định của người dùng ngày 2026-11-16 (xem "Quyết định"). Đợt 2 (2026-11-16) sửa theo review: chuẩn hóa NFKC, "phần trăm" mọi kiểu viết, đọc UTF-8 chặt, cấm quét rỗng, cấm khóa lạ trong fixture.

**Input**: GitHub issue [#138](https://github.com/Dyuedu/HaiDoIT/issues/138) — Blurb gate rejects digits outside technology names. Liên quan: quy tắc FR-23 ở `haido_core/vocab/prepared_text.py` (#212, DEC-6 #132).

## Bối cảnh

Cổng FR-24 trong `tools/gates/check_gates.py` có regex riêng `[A-Za-z][A-Za-z+#.]*\s?\d+` để miễn "tên công nghệ". Regex này xóa mọi "chữ + số", nên "Hơn 30 tin cần Python", "Top 5 kỹ năng", "Cần 3 năm kinh nghiệm" đều qua (đã chạy thử); chỉ số đứng đầu dòng bị bắt, và "phần trăm" không được kiểm. Quy tắc đúng đã có một chỗ ở `haido_core/vocab/prepared_text.py` (`prepared_text_problems`) và test FR-23 đang dùng nó. Cổng phải dùng đúng hàm đó, không giữ bản thứ hai.

Thư mục `haido_core/vocab/blurbs` chỉ có cùng #218 (Sprint 4), sau hạn hoãn 2026-11-22. Lời dẫn đang hiện ra hôm nay là các trường `blurb` và `resource.title` của `haido_api/fixtures/fake_learning_path.json`.

## Quyết định của người dùng (2026-11-16, phương án A)

Khi `haido_core/vocab/blurbs` chưa có, cổng quét **chữ viết sẵn đang hiển thị**: `blurb` và `resource.title` của mọi kỹ năng trong fixture, và cho PASS/FAIL thật. Khi thư mục có, cổng quét thư mục và vẫn quét fixture. Nhánh hoãn (`deferred.json`) chỉ còn cho trường hợp không có gì để quét (không thư mục, không fixture). Mục FR-24 bị gỡ khỏi `tools/gates/deferred.json`, và `FR-24` được thêm vào `--require` của CI.

Điều này **lệch với lời của AC 4** ("cho tới khi thư mục có, `deferred.json` ghi #138 và 2026-11-22 và CI in ra việc hoãn"). Lời AC giữ nguyên; người dùng đã chấp nhận độ lệch và lead đã ghi nhận trên issue: [comment về độ lệch AC 4](https://github.com/Dyuedu/HaiDoIT/issues/138#issuecomment-6911911511).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cổng bắt mọi chữ số ngoài tên công nghệ (Priority: P1)

**Independent Test**: `tests/tools/test_fr24_loi_dan_khong_so.py`, ROOT trỏ tới thư mục tạm; `tests/core/test_fr23_prepared_text.py` cho quy tắc.

**Acceptance Scenarios**:

1. **(AC 1)** **Given** `haido_core/vocab/blurbs` có tồn tại, **When** chạy cổng FR-24, **Then** cổng quét từng dòng của mọi file trong thư mục và báo `tệp:dòng`.
2. **(AC 2)** **Given** một dòng có "Java 17", "HTML5", "S3", "EC2", "OAuth2" (kể cả "Java 17," và "(HTML5)"), **When** quét, **Then** PASS.
3. **(AC 3)** **Given** một dòng "Hơn 30 tin cần Python", "Top 5 kỹ năng", "Cần 3 năm kinh nghiệm", "Java 170", "Mức 100%", hoặc chữ "phần trăm", **When** quét, **Then** FAIL, một hit cho mỗi dòng.
4. **(đợt 2)** **Given** văn bản dùng ký tự tương đương: `％` toàn chiều, `²`, `①`, chữ số toàn chiều, "PHẦN TRĂM" viết hoa, "phần trăm" dạng NFD, hai dấu cách, dấu cách không ngắt (NBSP), hoặc xuống dòng giữa "phần" và "trăm", **When** quét, **Then** FAIL. Cụm vắt qua hai dòng của một file trong thư mục báo `tệp:dòng` của dòng bắt đầu cụm.

### User Story 2 - Chưa có thư mục thì quét chữ đang hiển thị (Priority: P1)

**Acceptance Scenarios**:

5. **(AC 4, theo quyết định 2026-11-16)** **Given** không có `haido_core/vocab/blurbs` nhưng có `fake_learning_path.json`, **When** quét, **Then** cổng đọc `blurb` và `resource.title` của mọi kỹ năng của mọi vai trò (kể cả kỹ năng cuối của vai trò cuối), PASS khi sạch, FAIL khi có lỗi và hit nêu `vai_trò.kỹ_năng.trường`; không còn SKIP.
6. **Given** cả thư mục lẫn fixture, **When** quét, **Then** quét cả hai.
7. **(phần còn lại của AC 4)** **Given** không có thư mục và không có fixture, **When** quét, **Then** vẫn đi qua `deferred.json` như cũ: SKIP khi mục còn hạn, FAIL khi quá hạn, sai URL hoặc thiếu file.
8. **Given** repo thật, **When** chạy cổng với `--require` của CI, **Then** FR-24 là PASS và nêu fixture đã quét; `deferred.json` không còn mục FR-24. Lưu ý: CI chỉ in chi tiết khi FAIL hoặc SKIP, nên khi PASS log chỉ có "PASS"; số văn bản đã quét ("scanned N texts in ...") nằm trong chuỗi chi tiết mà hàm cổng trả về.

### User Story 3 - Cổng không xanh oan (Priority: P1, đợt 2)

**Acceptance Scenarios**:

9. **Given** một file trong thư mục blurbs không giải mã được UTF-8 (hoặc không đọc được), **When** quét, **Then** FAIL, hit nêu tên file; không bỏ qua im lặng.
10. **Given** tổng số văn bản đã quét bằng 0 (thư mục rỗng, fixture không có vai trò hay kỹ năng nào), **When** quét, **Then** FAIL: quét rỗng không phải PASS.
11. **Given** fixture không đọc được, không phải JSON, hoặc sai hình dạng (gốc không phải object, `roles` không phải object, `skills` không phải list, nút không phải object), **When** quét, **Then** FAIL, hit nêu `fake_learning_path.json`.
12. **Given** một nút kỹ năng, `resource`, một vai trò hoặc gốc fixture có khóa ngoài tập đã biết (nút: `skill`, `requires`, `foundation`, `blurb`, `resource`; `resource`: `title`, `url`; vai trò: `skills`; gốc: `_note`, `roles`), **When** quét, **Then** FAIL nêu khóa lạ, để trường chữ mới không lọt qua cổng.
13. **Given** `blurb` hoặc `resource.title` thiếu, `null`, số hay list, **When** quét, **Then** FAIL với hit nêu `vai_trò.kỹ_năng.trường` và "not a string", không phải "gate crashed".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cổng gọi `prepared_text_problems` của `haido_core/vocab/prepared_text.py`; không còn regex tên công nghệ riêng trong `check_gates.py`.
- **FR-002**: `check_gates.py` import module này bằng cách thêm gốc repo vào `sys.path` ngay trong cổng (CI chạy `python tools/gates/check_gates.py` bằng Python trơn, không cài gói). Module chỉ dùng thư viện chuẩn; `haido_core/__init__.py` và `vocab/__init__.py` chỉ có docstring nên không kéo SQLAlchemy.
- **FR-003**: Một dòng lỗi cho mỗi dòng hoặc trường, gồm lý do của `prepared_text_problems`.
- **FR-004** (đợt 2): `prepared_text_problems` và `digits_outside_tech` chuẩn hóa NFKC trước khi kiểm; "phần trăm" khớp bằng `phần\s+trăm` trên văn bản casefold. `TECH_NAMES` không nới.
- **FR-005** (đợt 2): file trong thư mục blurbs được đọc dạng byte và giải mã UTF-8 chặt (không dùng `read()` chung vì nó nuốt lỗi); kiểm cả văn bản của file chứ không chỉ từng dòng.
- **FR-006** (đợt 2): tổng số văn bản quét bằng 0 thì FAIL; chuỗi chi tiết ghi "scanned N texts in ...". Mỗi file trong thư mục là một văn bản; mỗi `blurb` và `resource.title` là một văn bản.
- **FR-007** (đợt 2): khóa lạ, kiểu sai hay trường thiếu trong fixture là hit FAIL có tên rõ, không để cổng văng lỗi.

### Edge Cases

- Cụm "phần" / "trăm" vắt qua hai dòng của file trong thư mục: bị bắt, báo dòng bắt đầu cụm.
- File blurbs sai mã hóa (ví dụ UTF-16): FAIL nêu tên file.
- Thư mục blurbs rỗng, hoặc fixture `roles` rỗng, `skills` rỗng: FAIL (quét 0 văn bản). Thư mục rỗng nhưng fixture có văn bản vẫn tính đủ theo tổng.
- Văn bản xấu nằm ở kỹ năng cuối của vai trò cuối: vẫn bị bắt (test hai vai trò x hai kỹ năng).
- `blurb` thiếu, `null`, số, list: FAIL có thông điệp rõ.
- Khóa lạ ở bốn cấp (gốc, vai trò, nút, `resource`): FAIL. `_note` ở gốc được phép và không bị quét.
- "Java 17," (dấu phẩy), "(HTML5)" (ngoặc): vẫn là tên công nghệ, PASS. "Java 170", "MyS3": vẫn bị tính chữ số (tên công nghệ chỉ miễn khi khớp nguyên từ; cố ý chặt).
- Số viết bằng chữ ("mười hai") vẫn ngoài phạm vi.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Mọi test mới và cũ trong `tests/tools/test_fr24_loi_dan_khong_so.py` và `tests/core/test_fr23_prepared_text.py` xanh; trước khi sửa code, đợt 2 đỏ thật (số liệu trong `tdd.md`).
- **SC-002**: Mỗi lớp bảo vệ mới (quét hết vai trò, quét hết kỹ năng, nhánh fixture hỏng, UTF-8 chặt, cấm quét rỗng, khóa lạ, kiểu sai, kiểm cả file, NFKC, `phần\s+trăm`) có ít nhất một test đỏ khi đảo lớp đó (bảng đột biến trong `tdd.md`).
- **SC-003**: `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-24` có FR-24 PASS trên repo thật; fixture thật không phải sửa chữ sản phẩm.
- **SC-004**: `uv run pytest -q` và `uv run ruff check .` sạch.

## Assumptions

- Mọi file trong `haido_core/vocab/blurbs` (kể cả thư mục con) là chữ viết sẵn cần quét; định dạng chi tiết của thư mục này do #218 quyết định, cổng chỉ cần UTF-8.
- Tập khóa đã biết của fixture khớp fixture hiện tại và `haido_api/schemas/learning_path.py`; thêm trường chữ mới vào fixture thì phải sửa cổng cùng lúc (cố ý).
- Số viết bằng chữ vẫn ngoài phạm vi, như `prepared_text.py`.
- Fixture thật đã quét bằng quy tắc đúng: không dòng nào lỗi.
- #139 đổi phần FR-22 của `check_gates.py`, `deferred.json` và có thể `ci.yml` song song; #138 chỉ đụng phần FR-24. `tests/tools/test_ad11_ad21_rieng_tu.py` khẳng định tập mục của `deferred.json`; #138 đổi thành `{"FR-22"}`, #139 sẽ đổi tiếp khi gộp.
- `haido_core/vocab/prepared_text.py` thuộc #212: hành vi mới được ghi thành đợt 5 trong `specs/212-hinh-lo-trinh-hoc/`.
