# Implementation Plan: Đo sức chịu tải baseline của API bằng k6

**Branch**: `gh-342-do-tai-baseline` | **Date**: 2026-11-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/342-do-tai-baseline/spec.md`

## Summary

Dựng môi trường đo tách khỏi production: một compose riêng chạy API cùng image và lệnh với prod trên Postgres local, một tool seed snapshot giả qua pipeline thật, và một script k6 có kịch bản `smoke` và `breakpoint`. Chạy bài đo, ghi RPS baseline và nút thắt vào `ket-qua-do.md`. Không sửa mã của API.

## Technical Context

**Language/Version**: Python 3.13, JavaScript (k6 2.2)

**Primary Dependencies**: k6 (cài trên máy đo, không thêm vào `pyproject.toml`). Không thêm thư viện Python.

**Storage**: Postgres 18.6 trong compose đo, DB `haido_load_test`, cổng `127.0.0.1:5434`.

**Testing**: `uv run pytest tests/deploy/test_gh342_do_tai_baseline.py tests/tools/test_gh342_loadtest_seed.py`. Test seed cần `HAIDO_TEST_DATABASE_URL` như các test Postgres khác.

**Target Platform**: Máy dev (Docker Desktop). Không chạy trên VPS.

## Constitution Check

- Không bắn tải vào production.
- Production đọc `stat` cho mọi nguồn (#309): compose đo cũng vậy, để đo đúng đường đọc thật.
- Không viết spec vào `_bmad-output/`.

## Project Structure

```text
deploy/
└── compose.loadtest.yml          # Mới: postgres + api, giới hạn 2 CPU

tools/
├── bench_skill_rates.py          # Dùng lại _build (không sửa)
└── loadtest_seed.py              # Mới: seed + aggregate + publish

loadtest/
├── README.md                     # Mới: cách chạy
└── k6/
    ├── baseline.js               # Mới: smoke + breakpoint
    └── params.json               # Mới: vai trò, cấp bậc, kỹ năng dùng trong URL

tests/
├── deploy/test_gh342_do_tai_baseline.py   # Mới: compose đo + script k6
└── tools/test_gh342_loadtest_seed.py      # Mới: seed (cần Postgres)

specs/342-do-tai-baseline/
└── ket-qua-do.md                 # Mới: số đo baseline
```

## Complexity Tracking

Không có vi phạm.
