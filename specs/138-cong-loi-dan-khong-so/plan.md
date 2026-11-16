# Implementation Plan: Cổng FR-24 dùng quy tắc chung

**Branch**: `gh-138-cong-loi-dan-khong-so` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

**Input**: `specs/138-cong-loi-dan-khong-so/spec.md`

## Summary

`gate_fr24_loi_dan_khong_so` gọi `prepared_text_problems` cho từng dòng của `haido_core/vocab/blurbs` (nếu có) và cho `blurb`, `resource.title` trong `haido_api/fixtures/fake_learning_path.json` (nếu có). Chỉ khi không có gì để quét mới gọi `check_deferred("FR-24")`. Đợt 2 (review): file đọc byte UTF-8 chặt và kiểm cả văn bản; quét 0 văn bản là FAIL; fixture kiểm khóa lạ và kiểu; quy tắc chung chuẩn hóa NFKC.

## Technical Context

**Language/Version**: Python 3.13, chỉ stdlib trong cổng. **Testing**: `uv run pytest -q tests/tools/test_fr24_loi_dan_khong_so.py`.

**Constraints**: CI (`.github/workflows/ci.yml`, job `gates`) chạy `python tools/gates/check_gates.py --require ...` bằng Python trơn, nên import phải chỉ cần stdlib; đã kiểm `prepared_text.py` chỉ import `re`. Trước đây `--require` không có `FR-24` nên cổng chạy nhưng SKIP không làm CI đỏ; nay thêm `FR-24` để SKIP hay FAIL đều đỏ.

## File sẽ sửa

```text
tools/gates/check_gates.py                    (chỉ phần FR-24: bỏ regex riêng, dùng prepared_text_problems, quét fixture; đợt 2: đọc UTF-8 chặt, kiểm cả file, đếm văn bản, khóa lạ, kiểu sai; docstring "Mười cổng")
tools/gates/deferred.json                     (gỡ mục FR-24)
.github/workflows/ci.yml                      (thêm FR-24 vào --require)
haido_core/vocab/prepared_text.py             (đợt 2: chuẩn hóa NFKC, phần\s+trăm, docstring; file của #212)
tests/tools/test_fr24_loi_dan_khong_so.py     (test mới; test real_repo đổi từ SKIP sang PASS; đợt 2: quét vai trò/kỹ năng cuối, fixture hỏng, UTF-8, quét rỗng, khóa lạ, kiểu sai, NFKC)
tests/core/test_fr23_prepared_text.py         (đợt 2: ca NFKC và "phần trăm"; file của #212)
tests/tools/test_ad11_ad21_rieng_tu.py        (tập mục của deferred.json: bỏ FR-24)
specs/212-hinh-lo-trinh-hoc/{spec,plan,tasks,research,tdd}.md   (đợt 5: hành vi mới của prepared_text.py)
specs/138-cong-loi-dan-khong-so/*             (mới)
```

## Issue cũ đã đụng tới các file này

Tìm bằng `git log --format='%h %s' -- <file>` cho từng file đổi và bằng grep `specs/*/plan.md`, `specs/*/tasks.md`:

- `tools/gates/check_gates.py`: #1 (`ff0c3c6`), #140 (`1ffb0b3`), cùng các commit không số issue (`749ceaf`, `012d853`, `f7fc686`, `9173ced`, `f217636`).
- `tools/gates/deferred.json`: #140 (`1ffb0b3`) và `f217636`.
- `.github/workflows/ci.yml`: #1, #2 (`506f2fc`), #6 (`aea4b30`), #46 (`098498a`), #162, #259, #263 (`5a4d9e9`), cùng các commit không số issue (`749ceaf`, `012d853`, `193235f`, `8b5c358`, `fa0cb5b`, `f7fc686`, `9173ced`, `f217636`).
- `tests/tools/test_fr24_loi_dan_khong_so.py`: chỉ `f217636` (không số issue). `tests/tools/test_ad11_ad21_rieng_tu.py`: `1ffb0b3` (#140) và `f217636`.
- `haido_core/vocab/prepared_text.py` và `tests/core/test_fr23_prepared_text.py`: chỉ `68fc7a1` (#212). #212 có `specs/212-hinh-lo-trinh-hoc/`, nên cập nhật cùng commit: đợt 5 trong `tdd.md`, `tasks.md` (T026, T027), `spec.md`, `plan.md`, `research.md`.
- Các issue #1, #2, #6, #46, #140, #162, #259, #263 chưa có thư mục `specs/` (đã kiểm `ls specs`), nên không bắt buộc dựng lại; ghi tên chúng trong mô tả PR. Các `tasks.md` của #163, #206, #280, #283, #293 chỉ nhắc lệnh chạy cổng hoặc `--require`, hành vi của chúng không đổi.
