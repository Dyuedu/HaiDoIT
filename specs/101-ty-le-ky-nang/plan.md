# Implementation Plan: Tỷ lệ kỹ năng theo ô, nhóm kỹ năng theo θ

**Branch**: `gh-101-ty-le-ky-nang` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

## Summary

Bước `aggregate` đọc thêm `job_posting_facts.skills` của tin đại diện từng cụm, giao cho `aggregate_skill_rates` (hàm thuần, `haido_core/domain/skill_rates.py`) cùng các ô vừa tính. Hàm trả một hàng cho mỗi (ô, mã từ vựng). `replace_stats` ghi vào `stat_skill_rates` (migration 0009) trong cùng transaction. `group_skills` (phép 4) là hàm thuần ở `skill_groups.py`, không lưu nhóm.

## Technical Context

**Language/Version**: Python 3.13. Không thêm gói.

**Storage**: bảng mới `haido.stat_skill_rates` (migration `0009_haido_skill_rates`, xem `data-model.md`).

**Testing**: pytest (Postgres), ruff, cổng `tools/gates/check_gates.py`.

**Constraints**: tập hợp trong bộ nhớ như `aggregate` hiện có (AD-5: API không đếm); mọi hàng của S trong một transaction; S đã chốt thì từ chối; θ truyền vào từng lần gọi (REGISTRY.md).

## Constitution Check

- AD-2: không thêm phép; cài thân phép 4 đúng chữ ký, `REGISTRY.md` không đổi.
- AD-4/AD-7: bảng dẫn xuất `stat_*`, chỉ `haido_core/steps/` ghi.
- AD-5: bảng dày, kể cả tỷ lệ 0.
- AD-25: một head Alembic (0009).

## Project Structure

```text
haido_core/domain/skill_groups.py                 (mới: phép 4)
haido_core/domain/skill_rates.py                  (mới: tỷ lệ theo ô, dày)
haido_core/domain/population.py                   (CountedPosting.skills)
haido_core/db/tables.py                           (stat_skill_rates)
haido_core/db/migrations/versions/0009_haido_skill_rates.py   (mới)
haido_core/db/snapshot_store.py                   (replace_stats ghi tỷ lệ kỹ năng)
haido_core/steps/aggregate.py                     (kỹ năng của tin đại diện, AggregateResult.skill_rates)
haido_core/cli.py                                 (dòng báo kết quả)
tests/domain/test_dat29_skill_groups.py, tests/domain/test_dat29_skill_rates.py          (mới)
tests/db/test_dat29_stat_skill_rates.py, tests/steps/test_dat29_aggregate_skill_rates_step.py  (mới)
tests/db/test_ad4_snapshot_schema.py, test_dat20_stat_tables.py, test_fr33_stat_city_shares_level.py,
tests/db/test_fr33_stat_years.py, test_gh283_facts_labels.py, test_gh285_fact_city.py     (head 0009, thêm bảng)
```

## Spec của issue cũ bị đụng

- `steps/aggregate.py`, `snapshot_store.py`, `tables.py`: #6, #93, #162, #259, #263 (không có `specs/`), #100, #163, #280, #283, #285 (có `specs/`: `plan.md`, `tasks.md` và đợt TDD mới đã thêm).
- `domain/population.py`: #93 (không có `specs/`), #280 (có).
- `domain/registry.py`, `REGISTRY.md`: không đổi.
- Test đổi head sang 0009: #93, #163, #280, #283, #285.

## Điểm mở

Xem `spec.md`: nhánh, thành phố và số năm cho tỷ lệ; tên `core/common/company_specific`; tên bảng.
