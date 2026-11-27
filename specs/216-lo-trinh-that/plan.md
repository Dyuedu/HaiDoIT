# Implementation Plan: API trả lộ trình đã xếp kèm tỷ lệ của từng kỹ năng

**Branch**: `gh-216-lo-trinh-that` | **Date**: 2026-11-25 | **Spec**: [spec.md](spec.md)

## Summary

Chuyển phần ghép của app demo (#217) vào `StatMarket`, thêm dấu rà soát cho nội dung. App demo chỉ còn bỏ qua dấu đó.

## Project Structure

```text
haido_api/stat_path.py                          # mới: Review, RolePath, load_paths, not_ready, ready
haido_api/content/learning_path.json            # chuyển từ fixtures/draft_learning_path.json, thêm review
haido_api/stat_market.py                        # learning_path, _path_for, _path_not_ready
haido_api/draft_path.py                         # chỉ còn ghi đè _path_for
tools/gates/check_gates.py                      # FR-24 quét đường dẫn mới
deploy/compose.prod.yml                         # chú thích
docs/api/envelope-meta.md
tests/api/test_fr22_learning_path_stat.py       # mới
tests/api/test_fr22_learning_path_draft.py
tests/api/test_fr22_learning_path.py            # bỏ test 404 của nguồn stat
tests/tools/test_fr24_loi_dan_khong_so.py
```

## Complexity Tracking

Issue chưa có `specs/` mà file bị đụng: #2, #93, #140, #162, #259, #263 (ghi trong mô tả PR).

**Cập nhật 2026-11-27 (#230)**: các file sau của issue này được #230 sửa thêm, hành vi không đổi: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `haido_api/stat_market.py`, `tests/api/test_ad17_meta_nguon_stat.py`, `tests/api/test_fr22_learning_path_draft.py`, `tests/api/test_fr22_learning_path_stat.py`. Xem `specs/230-hinh-soi-tin/plan.md`.
