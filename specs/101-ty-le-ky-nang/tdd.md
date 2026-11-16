# TDD: Tỷ lệ kỹ năng theo ô, nhóm kỹ năng theo θ (#101)

## Lệnh test

```bash
export HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test
uv run pytest tests/domain/test_dat29_skill_groups.py tests/domain/test_dat29_skill_rates.py \
  tests/db/test_dat29_stat_skill_rates.py tests/steps/test_dat29_aggregate_skill_rates_step.py -q
PYTHONHASHSEED=0 uv run pytest -m determinism -q     # và PYTHONHASHSEED=1
```

## Danh sách hành vi

1. `group_skills`: đúng θ thì vào nhóm cao hơn (`>=`); rỗng ra rỗng; một yêu cầu và một lô cho cùng kết quả; giữ thứ tự; θ theo từng lần gọi; tỷ lệ ngoài [0, 1] hay `theta_common > theta_core` là lỗi.
2. `aggregate_skill_rates`: dày kể cả tỷ lệ 0 và n = 0; cụm đếm một lần dù nhiều tin hay nhiều lượt nhắc; cửa sổ 60 ngày; vai trò `all`; cấp `all`, nhóm, cấp thô; chỉ `vn` và `any`; mã ngoài từ vựng bị bỏ; `n` lệch là lỗi; thứ tự ổn định.
3. Migration 0009: một head, cột và khóa, khóa ngoại tới `stat_cells`, ràng buộc, hạ cấp và nâng cấp lại.
4. Bước `aggregate`: mỗi ô 225 hàng; mỗi hàng khớp ô trong `stat_cells`; `rate = n_with / n`; cửa sổ, cụm, nguồn bị loại, tin ngoài IT; chạy lại cùng hàng; đã chốt thì từ chối; lỗi sau khi ghi thì giữ hàng cũ; snapshot đã chốt không bị động.

## RED (2026-11-16)

Chạy thật, code chưa có (hai module `skill_groups.py`, `skill_rates.py` được dời ra khỏi cây để chạy RED vì đã viết trước khi chạy test; migration và bảng chưa tạo).

- `uv run pytest tests/domain/test_dat29_skill_groups.py tests/domain/test_dat29_skill_rates.py -q` → **2 lỗi collection**: `ModuleNotFoundError: No module named 'haido_core.domain.skill_rates'` (và `skill_groups`). 21 test của hai file không chạy được.
- `uv run pytest tests/db/test_dat29_stat_skill_rates.py tests/steps/test_dat29_aggregate_skill_rates_step.py -q` → **22 failed**: 5 test DB (chưa có migration 0009 và bảng), 17 test bước (chưa có `stat_skill_rates`, `AggregateResult.skill_rates`).

## GREEN (2026-11-16)

Thứ tự: `skill_groups.py`, `skill_rates.py` + `CountedPosting.skills` → `tables.py`, migration 0009, `snapshot_store.replace_stats` → `steps/aggregate.py`, `cli.py` → đổi test cũ kiểm head.

- Bốn file test mới: **43 passed** (21 domain, 5 DB, 17 bước).
- Toàn bộ: `uv run pytest -q` → **1156 passed** (nền trước khi đổi: 1113 passed; thêm đúng 43). Không skip.
- `-m determinism` với `PYTHONHASHSEED=0` và `1` → 8 passed mỗi lần.
- `ruff check .` sạch; `alembic heads` một head `0009_haido_skill_rates`; cổng `--require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11`: 8 pass, 2 skip (FR-22, FR-24 hoãn), 0 fail.

Phát hiện trong lúc GREEN:

- Lần chạy toàn bộ đầu có **1 failed**: `tests/domain/test_ad2_registry.py` (cổng AD-2: "group_skills: hơn một thân hàm trong domain/"), vì tôi để cả hàm module `group_skills` lẫn phương thức của `SkillGrouper`. Bỏ hàm module, test dùng `SkillGrouper().group_skills`; chạy lại xanh.
- Test bước ban đầu dùng mã vai trò `data` (không có trong `rules.toml`); sửa thành `frontend`, `data_analyst`.

Test cũ đổi: các test kiểm head 0008 ở `tests/db/` (`test_dat20_stat_tables.py`, `test_fr33_stat_city_shares_level.py`, `test_fr33_stat_years.py`, `test_gh283_facts_labels.py`, `test_gh285_fact_city.py`) nay kiểm head 0009; `test_ad4_snapshot_schema.py` có thêm bảng `stat_skill_rates`. Không AC cũ nào đổi.

## Thời gian và số hàng trên bản sao dữ liệu thật

Bản sao local (DB `haido`, snapshot 10/11/2026, 5636 dữ kiện, 6065 tin trong vòng đời), nâng lên 0009; `skills` của dữ kiện điền ngẫu nhiên có phân bố Zipf (bản local chưa có kỹ năng thật) để phép đếm có việc làm. Mỗi cấu hình chạy 3 lần `aggregate_snapshot`:

| | Lần 1 / 2 / 3 (giây) | Hàng ghi |
|---|---|---|
| Trước (không tính tỷ lệ kỹ năng) | 3,98 / 4,87 / 4,67 | `stat_cells` 7077 |
| Sau | 6,23 / 6,53 / 6,50 | thêm 36.450 hàng `stat_skill_rates` |

36.450 = 162 ô (18 vai trò × 9 cấp) × 225 kỹ năng; dưới ngưỡng 200k. Tăng khoảng 2 giây mỗi lần `aggregate` (khoảng 1,5 lần); chưa tối ưu vì mỗi đêm chạy một lần.
