# TDD: Cổng FR-24 dùng quy tắc chung

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh:

```text
uv run pytest -q tests/tools/test_fr24_loi_dan_khong_so.py
uv run pytest -q tests/tools
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/tst138_test uv run pytest -q
uv run ruff check .
python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-24
```

## Các hành vi

1. "Hơn 30 tin cần Python", "Top 5 kỹ năng nên học", "Cần 3 năm kinh nghiệm", "Java 170", "Mức 100%", "phần trăm" (hai kiểu hoa thường) FAIL.
2. "Java 17", "HTML5", "AWS S3, EC2 và OAuth2" PASS.
3. Có `haido_core/vocab/blurbs` thì quét thư mục.
4. Không thư mục, có fixture: quét `blurb` và `resource.title`, PASS hoặc FAIL thật, hit có `vai_trò.kỹ_năng`.
5. Có cả hai thì quét cả hai.
6. Không có gì để quét: hành vi hoãn cũ (bốn test cũ giữ nguyên).
7. Repo thật: PASS, và `deferred.json` không còn FR-24.

## RED (2026-11-16)

`uv run pytest -q tests/tools/test_fr24_loi_dan_khong_so.py` → 12 failed, 10 passed:

- 6 ca `..._outside_tech_names_fail`: regex cũ xóa "chữ + số" nên "Hơn 30", "Top 5", "Cần 3", "Java 170" và câu "phần trăm" (không có số, không được kiểm) đều PASS. "Mức 100%" vẫn FAIL (có `%`) nên nằm trong số passed.
- 4 ca fixture (`scans_fixture_and_passes`, hai ca `fixture_with_bad_text_fails`, `directory_and_fixture_are_both_scanned`): cổng không đọc fixture.
- `real_repo_scans_todays_blurbs_and_passes`: trả SKIP vì còn hoãn.
- `fr24_is_no_longer_in_deferred_ledger`: mục FR-24 vẫn còn.

Test cũ `test_fr24_real_repo_skips` (repo thật phải SKIP, nêu #138 và 2026-11-22) mâu thuẫn trực tiếp với quyết định ngày 2026-11-16 nên được thay bằng `test_fr24_real_repo_scans_todays_blurbs_and_passes`. Sáu test cũ còn lại (ROOT là thư mục tạm rỗng hoặc chỉ có thư mục blurbs) giữ nguyên và vẫn xanh.

## GREEN

- Lần chạy đầu của `tests/tools` còn 3 lỗi: (a) cổng báo hai hit cho dòng "Mức 100%" (một cho `%`, một cho `100`) và test cũ `test_fr24_numbers_in_blurbs_fails` đòi đúng một hit; gộp thành một hit mỗi dòng; (b) `test_ad11_ad21_deferred_ledger_khong_con_muc_tam_cua_ad11` khẳng định tập mục là `{"FR-24", "FR-22"}`; đổi thành `{"FR-22"}` vì mục FR-24 bị gỡ theo quyết định.
- `uv run pytest -q tests/tools/test_fr24_loi_dan_khong_so.py` → 22 passed; `tests/tools` → 118 passed.
- Fixture thật: mọi `blurb` và `resource.title` đạt quy tắc đúng, không sửa chữ sản phẩm.
- Toàn bộ: `uv run pytest -q` (Postgres `tst138_test`, đã xóa sau khi chạy) → 1250 passed; `uv run ruff check .` sạch.
- `check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-24` → 9 pass, 1 skip (FR-22, #139), 0 fail; FR-24 PASS.

## Kiểm đột biến

- Đặt lại regex cũ `[A-Za-z][A-Za-z+#.]*\s?\d+` thay cho `prepared_text_problems` ở nhánh thư mục: 6 failed.
- Bỏ nhánh quét fixture (chỉ hoãn khi không có thư mục): 4 failed.
- Khôi phục đúng nguyên văn, chạy lại xanh.

## Đợt 2 (2026-11-16, review #138)

Lý do: review chỉ ra các lỗ của đợt 1: test không khóa việc quét hết vai trò và kỹ năng (đảo thành chỉ quét cái đầu vẫn xanh), nhánh fixture hỏng đảo thành PASS vẫn xanh, thư mục blurbs đọc bằng `read()` nuốt lỗi giải mã, quét rỗng vẫn xanh, khóa chữ mới trong fixture lọt, `blurb` null làm cổng văng, và `prepared_text_problems` bỏ lọt `％`, `²`, `①`, "phần trăm" nhiều dấu cách/NBSP/xuống dòng/NFD. Không AC nào của issue đổi; độ lệch AC 4 đã có từ đợt 1.

Lệnh:

```text
uv run pytest -q tests/core/test_fr23_prepared_text.py tests/tools/test_fr24_loi_dan_khong_so.py
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/fx138_test uv run pytest -q
uv run ruff check .
python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-24
```

Hành vi mới (nối tiếp danh sách ở trên): 8. văn bản xấu ở kỹ năng cuối của vai trò cuối bị bắt. 9. fixture hỏng, sai hình dạng hay không phải UTF-8 là FAIL. 10. file blurbs không phải UTF-8 là FAIL nêu tên file. 11. quét 0 văn bản là FAIL, chi tiết ghi "scanned N texts". 12. khóa lạ là FAIL nêu khóa. 13. `blurb` hoặc `title` thiếu hay không phải chuỗi là FAIL rõ ràng. 14. cụm "phần" / "trăm" vắt hai dòng bị bắt, báo `tệp:dòng`. 15. `％`, `²`, `①`, chữ số toàn chiều, "PHẦN TRĂM", NFD, hai dấu cách, NBSP, xuống dòng bị bắt; "Java 17," và "(HTML5)" vẫn qua.

### RED (chạy thật trước khi sửa code)

`uv run pytest -q tests/core/test_fr23_prepared_text.py tests/tools/test_fr24_loi_dan_khong_so.py` → 31 failed, 62 passed (93 test):

- `test_fr23_prepared_text.py`: 10 failed. Hai ca `％` (không có `%` ASCII nên không báo `%`); `²` và `①` (không khớp `\d` nên không tính chữ số); sáu ca "phần trăm" (hai dấu cách, NBSP, xuống dòng, tab và CRLF, hai ca NFD) vì chỉ so chuỗi "phần trăm" đúng một dấu cách. Ca viết hoa, chữ số toàn chiều và "Java 17," / "(HTML5)" xanh sẵn.
- `test_fr24_loi_dan_khong_so.py`: 21 failed. `clean_two_roles_two_skills_passes_and_counts` (chưa có "scanned N texts"); `malformed_fixture_fails[{"roles": []}]` (cổng văng lỗi, không có hit nêu tên fixture); `non_utf8_blurb_file_fails_naming_file` (`read()` trả chuỗi rỗng nên PASS); `empty_blurbs_dir_fails`, `fixture_with_zero_skills_fails`, `fixture_with_no_roles_fails` (quét rỗng PASS hoặc không báo); ba ca `unknown_key` và `unknown_resource_key` (khóa lạ không bị chú ý); sáu ca `non_string_text` (null, số, list cho `blurb` và `title`) và `missing_blurb` (cổng văng "gate crashed"); `phrase_split_across_lines` (từng dòng sạch nên PASS); ba ca `normalised_forms` (`²`, `①`, NBSP).
- Hai test "văn bản xấu ở kỹ năng cuối của vai trò cuối" (`blurb`, `title`) xanh sẵn vì cổng đợt 1 thật ra duyệt hết; chúng khóa hành vi này, và các đột biến "chỉ vai trò đầu" và "chỉ kỹ năng đầu" (bảng dưới) làm chúng đỏ.

### GREEN

- Sửa `haido_core/vocab/prepared_text.py` (NFKC, `phần\s+trăm`) và `tools/gates/check_gates.py` (đọc byte UTF-8 chặt, kiểm cả file, `_fr24_scan_fixture` với tập khóa đã biết, kiểm kiểu, đếm văn bản, FAIL khi 0).
- `uv run pytest -q tests/core tests/tools` → 309 passed.
- Toàn bộ: `uv run pytest -q` (Postgres 5433, DB `fx138_test`, đã xóa sau khi chạy) → 1301 passed; `uv run ruff check .` sạch.
- `check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-24` → 10 cổng: 9 pass, 1 skip (FR-22, #139), 0 fail. Gọi trực tiếp `gate_fr24_loi_dan_khong_so()` trên repo thật → `('PASS', 'scanned 54 texts in haido_api/fixtures/fake_learning_path.json', [])`. (CI chỉ in chi tiết khi FAIL hoặc SKIP.)
- Fixture thật không phải sửa chữ sản phẩm.

### Kiểm đột biến (đảo từng lớp, chạy hai file test, khôi phục đúng nguyên văn, kiểm bằng `cmp`)

| Đột biến | Kết quả |
|---|---|
| chỉ quét vai trò đầu | 3 failed |
| chỉ quét kỹ năng đầu của mỗi vai trò | 3 failed |
| nhánh fixture hỏng trả "sạch" | 2 failed |
| giải mã UTF-8 lỏng (`replace`) ở thư mục blurbs | 1 failed |
| cho phép quét rỗng | 3 failed |
| bỏ kiểm khóa lạ | 4 failed |
| ép kiểu thay vì báo "not a string" | 7 failed |
| bỏ kiểm cả file (chỉ từng dòng) | 1 failed |
| bỏ NFKC trong `prepared_text_problems` | 4 failed |
| bỏ NFKC trong `digits_outside_tech` | lần đầu 0 failed (đột biến sống: hàm công khai này chưa có test riêng); thêm `test_fr23_digits_outside_tech_cung_chuan_hoa_nfkc` rồi chạy lại → 1 failed |
| "phần trăm" một dấu cách thay `phần\s+trăm` | 5 failed |

Sau kiểm đột biến: `cmp` với bản gốc khớp, không để file sao lưu hay `.pyc` trong repo.

## Đợt 3 — 2026-11-16 — test hẹn giờ (review #139)

**Lý do:** reviewer của #139 chỉ ra test sổ hoãn trong `tests/tools/test_fr22_tat_dinh.py` ghi cứng hạn `2026-11-22`, nên tự đỏ từ 2026-11-23. Test cùng dạng ở FR-24, `test_fr24_no_blurbs_with_valid_ledger_skips`, có cùng lỗi.

**RED (ngày giả 2026-11-23):** gọi `gate_fr24_loi_dan_khong_so` trên sổ hoãn tạm với hạn cũ `2026-11-22` thì ra `FAIL` (quá hạn), trong khi test chờ `SKIP`. Nghĩa là 1 test sẽ đỏ từ 2026-11-23.

**Sửa:** fixture của test dùng hạn `2099-12-31`. Ca này kiểm sổ hoãn còn hạn, không kiểm một ngày cụ thể.

**GREEN:** với ngày giả 2026-11-23, hạn `2099-12-31` cho ra `SKIP`. `uv run pytest -q tests/tools/test_fr24_loi_dan_khong_so.py` cho 56 passed.

Bom hẹn giờ ở `test_fr22_tat_dinh.py` thuộc #139 và được sửa trên nhánh đó.

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: cổng FR-24 quét thêm tên chủ đề và file lộ trình nháp (RED: 6 failed, 56 passed trong `tests/tools/test_fr24_loi_dan_khong_so.py`). Luật về chữ và AC không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: cổng FR-24 quét `haido_api/content/learning_path.json` và nhận khóa `review` (RED: 1 failed). Luật về chữ không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.
