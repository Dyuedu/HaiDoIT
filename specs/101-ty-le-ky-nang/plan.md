# Implementation Plan: Tỷ lệ kỹ năng theo ô, nhóm kỹ năng theo θ

**Branch**: `gh-101-ty-le-ky-nang` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

## Summary

Bước `aggregate` đọc thêm `job_posting_facts.skills` của mọi thành viên từng cụm (hợp, D1; NULL là chưa quét, D2), kiểm `vocab_version` của các dữ kiện đã quét (D3), giao cho `aggregate_skill_rates` (hàm thuần, `haido_core/domain/skill_rates.py`) cùng các ô vừa tính. Hàm dùng chung cửa sổ và việc khớp ô của phép 3 (`population.py`, R3) và trả một hàng cho mỗi (ô, mã từ vựng) kèm `n_scanned`. `replace_stats` (bắt buộc nhận `skill_rates`) ghi vào `stat_skill_rates` (migration 0009) trong cùng transaction. `ingest` ghi `vocab_version` và quét lại tin trong cửa sổ khi từ vựng đổi. `group_skills` (phép 4) là hàm thuần ở `skill_groups.py`, không lưu nhóm.

## Technical Context

**Language/Version**: Python 3.13. Không thêm gói.

**Storage**: bảng mới `haido.stat_skill_rates` và cột mới `job_posting_facts.vocab_version` (migration `0009_haido_skill_rates`, xem `data-model.md`). 0009 chưa push và chưa áp dụng ở đâu nên được sửa tại chỗ, không thêm 0010.

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
haido_core/domain/population.py                   (CountedPosting.skills, `postings_in_window`, `matches_cell` dùng chung)
haido_core/db/tables.py                           (stat_skill_rates, chỉ mục, job_posting_facts.vocab_version)
haido_core/db/migrations/versions/0009_haido_skill_rates.py   (mới)
haido_core/db/snapshot_store.py                   (replace_stats ghi tỷ lệ kỹ năng, kiểm n_scanned <= n; FactVersion.vocab_version; stale_in_window)
haido_core/steps/aggregate.py                     (hợp kỹ năng của cụm, kiểm vocab_version, AggregateResult.skill_rates)
haido_core/steps/ingest.py                        (ghi vocab_version, quét lại khi từ vựng đổi)
haido_core/domain/skill_groups.py                 (kiểm θ và skill_id trùng)
haido_core/domain/REGISTRY.md                     (ghi thân hàm phép 4)
tools/bench_skill_rates.py                        (mới: đo thời gian aggregate bật/tắt tỷ lệ kỹ năng)
haido_core/cli.py                                 (dòng báo kết quả)
tests/domain/test_dat29_skill_groups.py, tests/domain/test_dat29_skill_rates.py          (mới)
tests/db/test_dat29_stat_skill_rates.py, tests/steps/test_dat29_aggregate_skill_rates_step.py  (mới)
tests/db/test_ad4_snapshot_schema.py, test_dat20_stat_tables.py, test_fr33_stat_city_shares_level.py,
tests/db/test_fr33_stat_years.py, test_gh283_facts_labels.py, test_gh285_fact_city.py     (head 0009, thêm bảng, cột vocab_version)
tests/steps/test_gh283_ingest_classify.py          (quét lại khi từ vựng đổi)
```

## Spec của issue cũ bị đụng

- `steps/aggregate.py`, `snapshot_store.py`, `tables.py`: #6, #93, #162, #259, #263 (không có `specs/`), #100, #163, #280, #283, #285 (có `specs/`: `plan.md`, `tasks.md` và đợt TDD mới đã thêm).
- `steps/ingest.py` (đợt 2): #6 (không có `specs/`), #280, #283, #285. #283 đổi hành vi (quét lại khi từ vựng đổi) nên có thêm đợt TDD và kịch bản trong `spec.md`; AC của #283 không đổi.
- `domain/population.py`: #93 (không có `specs/`), #280 (có).
- `domain/registry.py`, `REGISTRY.md`: không đổi.
- Test đổi head sang 0009: #93, #163, #280, #283, #285.

## Điểm mở

Xem `spec.md`: nhánh, thành phố và số năm cho tỷ lệ; tên `core/common/company_specific`; tên bảng.
