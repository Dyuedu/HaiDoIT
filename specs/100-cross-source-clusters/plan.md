# Implementation Plan: Gộp tin trùng chéo nguồn thành cụm

**Branch**: `gh-100-cum-cheo-nguon` | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/100-cross-source-clusters/spec.md`

## Summary

Thêm hàm thuần gộp tin theo công ty và chức danh đã chuẩn hóa, chọn đại diện theo hạng nguồn rồi số trường rồi URL. Bước `aggregate` phát một `CountedPosting` mỗi cụm, `cluster_id` là id cụm, nhãn lấy từ đại diện, `last_seen` là ngày thấy gần nhất của các thành viên. `match_postings` là thân hàm của phép 7, đúng một thân trong `haido_core/domain/`.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: thư viện chuẩn, SQLAlchemy ở bước đọc URL tin. Không thêm gói.

**Storage**: schema `haido` hiện có. Không migration.

**Testing**: `uv run pytest tests/domain/test_dat28_cluster.py` rồi `uv run pytest tests/domain tests/core/test_ad10_rules_config.py -q`

**Target Platform**: bước đêm trên VPS và test local

**Performance Goals**: một đêm vài nghìn tin, gộp trong bộ nhớ một lần

**Constraints**: phép dân số vẫn đếm `cluster_id`. Cổng AD-2 chỉ cho một thân `match_postings` trong `haido_core/domain/`. Không xóa tin. Không ghi spec vào `_bmad-output/`.

**Scale/Scope**: các tin có dòng vòng đời của một snapshot, sau khi bỏ nguồn `sources.excluded`

## Constitution Check

- Một thân hàm `match_postings` trong `haido_core/domain/matching.py`. Hàm gộp tên `collapse_clusters`, không lấy tên của tám phép.
- Quy tắc hạng nguồn nằm trong `config/rules.toml`, thiếu khóa thì lỗi tiếng Việt, không điền mặc định.
- Test mới phải đỏ trước khi có thân hàm.
- Tin thiếu khóa vẫn được đếm.

## Project Structure

### Documentation (this feature)

```text
specs/100-cross-source-clusters/
├── plan.md
├── research.md
├── data-model.md
├── spec.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
haido_core/domain/cluster.py
haido_core/domain/matching.py
haido_core/steps/aggregate.py
haido_core/config.py
haido_core/db/snapshot_store.py
config/rules.toml
tests/domain/test_dat28_cluster.py
tests/steps/test_dat20_aggregate_step.py
```

**Structure Decision**: Hàm thuần nằm trong `haido_core/domain/`. Bước `aggregate` chỉ đọc dữ liệu, gọi hàm, rồi ghi số như hiện tại.

## Complexity Tracking

Không có vi phạm cần biện minh.
