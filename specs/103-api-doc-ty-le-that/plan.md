# Implementation Plan: API đọc tỷ lệ kỹ năng thật

**Branch**: `gh-151-ty-le-ky-nang-that` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

Thêm test khóa hai ràng buộc của lớp đọc (`meta` mọi nơi có số; không tổng hợp `job_*`) cho nguồn `stat`. Mã đọc là `StatMarket.skill_rates` của #151.

## Technical Context

**Language/Version**: Python 3.13, FastAPI

**Testing**: `uv run pytest tests/api/test_ad17_meta_nguon_stat.py tests/api/test_fr19_skill_rates_stat.py -q` (cần `HAIDO_TEST_DATABASE_URL`); `python tools/gates/check_gates.py --require AD-7 AD-17`.

**Constraints**: AD-7 (không tổng hợp trên `job_*`), AD-17 (Envelope).

## Project Structure

```text
tests/api/test_ad17_meta_nguon_stat.py     # mới: mọi route có số, nguồn stat
tests/api/test_fr19_skill_rates_stat.py    # mới (của #151): test AD-7 ghi lại SQL
```

**Structure Decision**: Không file mã nào chỉ của issue này; xem `specs/151-ty-le-ky-nang-that/plan.md`.

## Complexity Tracking

- Không đụng file nào của issue cũ.
