# Tasks: Cổng FR-24 dùng quy tắc chung

**Input**: `specs/138-cong-loi-dan-khong-so/` (spec.md, plan.md). Test đứng trước code.

## Phase 1: Tests (RED)

- [x] T001 `tests/tools/test_fr24_loi_dan_khong_so.py`: "Hơn 30...", "Top 5...", "Cần 3...", "Java 170", "100%", "phần trăm" FAIL
- [x] T002 Cùng file: Java 17, HTML5, S3/EC2/OAuth2 PASS; thư mục có thì được quét
- [x] T003 Cùng file: không thư mục + fixture thì quét `blurb` và `resource.title` (PASS và FAIL); cả hai cùng quét; repo thật PASS; `deferred.json` không còn FR-24
- [x] T004 Chạy, ghi RED vào `tdd.md`

## Phase 2: Implementation (GREEN)

- [x] T010 `tools/gates/check_gates.py`: dùng `prepared_text_problems`, quét fixture, hoãn chỉ khi không có gì để quét
- [x] T011 `tools/gates/deferred.json`: gỡ FR-24; `tests/tools/test_ad11_ad21_rieng_tu.py`: tập mục còn `{"FR-22"}`; `.github/workflows/ci.yml`: thêm `FR-24` vào `--require`
- [x] T012 Chạy lại, ghi GREEN, kiểm đột biến (regex cũ, bỏ fallback fixture)

## Phase 3: Hoàn tất

- [x] T020 `uv run pytest -q`, `uv run ruff check .`, `python tools/gates/check_gates.py --require ...`

## Phase 4: Đợt 2 (2026-11-16, review #138)

- [x] T030 Test trước (`tests/tools/test_fr24_loi_dan_khong_so.py`): văn bản xấu ở kỹ năng cuối của vai trò cuối; fixture hỏng, sai hình dạng, không UTF-8 là FAIL; file blurbs không UTF-8; thư mục rỗng và fixture 0 kỹ năng là FAIL; khóa lạ; `blurb` null, thiếu; cụm vắt hai dòng; NFKC; "Java 17," và "(HTML5)" vẫn PASS
- [x] T031 Test trước (`tests/core/test_fr23_prepared_text.py`): `％`, `²`, `①`, chữ số toàn chiều, "phần trăm" mọi kiểu
- [x] T032 Chạy, ghi RED đợt 2 vào `tdd.md` (31 failed, 62 passed)
- [x] T033 `haido_core/vocab/prepared_text.py`: NFKC, `phần\s+trăm`, cập nhật docstring; docstring của `test_fr23_prepared_text.py`
- [x] T034 `tools/gates/check_gates.py`: đọc byte UTF-8 chặt, kiểm cả file, `_fr24_scan_fixture` (khóa lạ, kiểu sai), đếm văn bản, FAIL khi 0; docstring "Mười cổng"
- [x] T035 Cập nhật `specs/138` (spec, plan, tasks, tdd) và `specs/212` (đợt 5)
- [x] T036 Kiểm đột biến từng lớp (bảng trong `tdd.md`), chạy toàn bộ, ruff, `check_gates.py --require`
