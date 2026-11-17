# Implementation Plan: Phép 2, chọn ô và thứ tự quay về

**Branch**: `gh-151-ty-le-ky-nang-that` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

## Summary

Cài thân hàm duy nhất của `select_cell` ở `haido_core/domain/cells.py`. Bảng ô do người gọi đưa qua `lookup`, nên module không biết DB hay API. `CellChoice` thêm `order` và cho phép `label = None`.

## Technical Context

**Language/Version**: Python 3.13

**Testing**: `uv run pytest tests/domain/test_ad2_select_cell.py tests/domain/test_ad2_registry.py -q`; `python tools/gates/check_gates.py --require AD-2`.

**Constraints**: AD-2 (một Protocol, một thân hàm, một đối tượng và một lô), AD-6 (không đổi phạm vi), AD-17 (cỡ mẫu theo phép đo).

## Project Structure

```text
haido_core/domain/cells.py                  # mới: CellSelector, CellStats
haido_core/domain/registry.py               # CellChoice: label | None, order
haido_core/domain/REGISTRY.md               # ghi phép 2 đã có thân hàm
tests/domain/test_ad2_select_cell.py        # mới
```

**Structure Decision**: Người gọi (`haido_api/stat_market.py`, #151) tạo `CellSelector` với `lookup` đọc `stat_cells` và `n_scanned`; phép không đọc config, DB hay đồng hồ.

## Complexity Tracking

- `registry.py` và `REGISTRY.md` thuộc #101, #139, #283, #285: thêm đợt TDD vào `tdd.md` của các issue có `specs/`. Hành vi và AC của các issue đó không đổi (thêm trường `order` có mặc định, `label` nới thành `str | None`; chưa có chỗ nào gọi `CellChoice`).
