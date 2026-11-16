# Implementation Plan: Cổng tất định cho thứ tự lộ trình

**Branch**: `gh-139-cong-tat-dinh-lo-trinh` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

**Input**: `specs/139-cong-tat-dinh-lo-trinh/spec.md`

## Summary

Cài thân hàm phép 8 trong `haido_core/domain/path_order.py` (class `PathOrderer`, Kahn với hàng đợi ưu tiên bốn tầng, kéo tổ tiên, kiểm đầu vào). Cổng FR-22 trong `tools/gates/check_gates.py` nay chạy phép đó trên đồ thị mẫu của cổng, qua tiến trình con với `PYTHONHASHSEED` 0 và 1, thay vì chỉ kiểm file có mặt. Mục hoãn `FR-22` của `deferred.json` đổi hạn từ 2026-11-22 sang 2026-12-13 và chỉ còn nói về AC2 (giữ nguyên khóa để không đụng test AD-11 và phần FR-24 mà #138 sửa). CI thêm `FR-22` vào `--require`.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: Không thêm gói. Cổng chỉ dùng thư viện chuẩn (CI chạy `python tools/gates/check_gates.py` không cài gói).

**Storage**: Không đổi cơ sở dữ liệu.

**Testing**: `uv run pytest -q tests/domain/test_fr22_order_path.py tests/tools/test_fr22_tat_dinh.py`; toàn bộ `uv run pytest -q` với `HAIDO_TEST_DATABASE_URL` trỏ DB `*_test` riêng.

**Constraints**: AD-1, AD-2, FR-22. Không sửa `haido_api/learning_path.py`. Chỉ đụng phần FR-22 của `check_gates.py` và `deferred.json` (#138 sửa phần FR-24 song song).

## Constitution Check

- Không viết spec vào `_bmad-output/`.
- Hàm thuần, không I/O, không đồng hồ, không số ngẫu nhiên (AD-1).
- Phép 8 là đúng một class trong file ghi ở `REGISTRY.md` (cổng AD-2 PASS).

## Project Structure

```text
haido_core/domain/path_order.py            (mới: PathOrderer, PathOrderError; kiểm kiểu đầu vào)
tools/gates/check_gates.py                 (gate_fr22_tat_dinh, đồ thị mẫu, probe tiến trình con ép UTF-8; `_deferral` tách khỏi `check_deferred`; `main()` in lời nhắc khi PASS và thay ký tự không mã hóa được; import os, subprocess)
tools/gates/deferred.json                  (mục FR-22: hạn 2026-12-13, ghi chú AC2)
.github/workflows/ci.yml                   (--require thêm FR-22)
tests/domain/test_fr22_order_path.py       (mới)
tests/tools/test_fr22_tat_dinh.py          (sửa: test dummy cũ, test từng phép kiểm của cổng, in lời nhắc, UTF-8, fixture hạn 2099)
specs/139-cong-tat-dinh-lo-trinh/*
```

Không đổi: `haido_core/domain/registry.py`, `haido_core/domain/REGISTRY.md` (chữ ký hàng 8 đã đúng), `haido_api/learning_path.py`.

## Issue cũ đã đụng tới file

`git log --format='%h %s' -- tools/gates/check_gates.py tools/gates/deferred.json .github/workflows/ci.yml tests/tools/test_fr22_tat_dinh.py` ra các issue #1, #2, #6, #46 (`098498a`, đã sửa `ci.yml`), #140, #162, #259, #263; không issue nào trong số đó có thư mục `specs/`. Các `specs/*/plan.md` và `tasks.md` nhắc `check_gates.py` (#206, #163, #280, #283, #293) chỉ nói việc chạy cổng, không liệt kê nó là file sửa, nên không cần đợt mới. Tên các issue không có spec (#1, #2, #6, #46, #140, #162, #259, #263) ghi ở mô tả commit.
