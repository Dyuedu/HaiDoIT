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

## Đợt 2 — 2026-11-16 — quyết định của người dùng và sửa theo review

Lý do: người dùng chốt D1 (hợp kỹ năng của cụm), D2 (mẫu số chỉ cụm đã quét, cột `n_scanned`), D3 (`vocab_version` ở dữ kiện, quét lại khi từ vựng đổi, `aggregate` từ chối phiên bản lẫn hoặc cũ); review R1–R8. Không đụng lại các đợt cũ.

Lệnh: `HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/<db>_test uv run pytest -q`.

Hành vi mới: hợp kỹ năng (đại diện NULL vẫn tính kỹ năng tin kia; cả hai nhắc vẫn một cụm; nhãn vẫn của đại diện); `n_scanned` và `rate = n_with / n_scanned`, `{}` khác NULL, ô toàn cụm chưa quét ra 0 không lỗi; CHECK `n_with <= n_scanned`; `replace_stats` kiểm `n_scanned <= n` và bắt buộc `skill_rates`; chỉ mục `(snapshot_id, skill)`; `group_skills` từ chối θ NaN, vô hạn, ngoài [0, 1] và `skill_id` trùng; ingest quét lại khi `vocab_version` khác hoặc NULL; `aggregate` từ chối phiên bản lẫn, cũ, NULL và đóng dấu phiên bản.

RED: các test của đợt này được viết cùng lúc với code ở lượt làm trước nên chưa có lượt chạy RED trên cây chưa sửa. Thay bằng đột biến (bên dưới): mỗi quyết định có test đỏ khi bỏ code tương ứng, nên các test không vô nghĩa.

GREEN:
- Bốn file test của #101 → **78 passed** (đợt 1: 43; thêm 35).
- Toàn bộ `uv run pytest -q` → **1194 passed**, không skip (đợt 1: 1156).
- `-m determinism`, `PYTHONHASHSEED=0` và `1` → 8 passed mỗi lần.
- `ruff check .` sạch (đã sửa SIM117 ở `tests/db/test_dat29_stat_skill_rates.py`); `alembic heads` một head `0009_haido_skill_rates`; cổng `--require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11`: 8 pass, 2 skip (FR-22, FR-24 hoãn), 0 fail.
- Số lượt chạy lại của #100 (48), #163 (40), #280 (30), #283 (15), #285 (8) ghi ở `tdd.md` của từng issue.

Đột biến (sửa một chỗ, chạy `tests/domain tests/db tests/steps`, khôi phục file nguyên văn; mỗi lần số test fail):

| Đột biến | Test fail |
|---|---|
| Chỉ lấy kỹ năng của tin đại diện thay vì hợp (`aggregate.py`) | 2 (`d1_ca_hai_nguon_cung_nhac_python...`, `d1_cum_hai_nguon_tin_dai_dien_khong_co_mo_ta...`) |
| Cụm chưa quét vẫn vào mẫu số (`skill_rates.py`) | 6 (`d2_*`, `d1_ca_hai_nguon_chua_quet...`) |
| Ingest không quét lại khi `vocab_version` khác hoặc NULL (`snapshot_store.stale_in_window`) | 2 (`d3_doi_tu_vung...`, `d3_du_kien_cu_chua_ghi_phien_ban...`) |
| `aggregate` không từ chối phiên bản cũ hoặc lẫn | 3 (`d3_tu_choi_*`, `d3_du_kien_da_quet_ma_khong_ghi_phien_ban...`) |
| `group_skills` nhận θ NaN (bỏ kiểm θ hữu hạn và khoảng) | 6 (`fr9_theta_khong_huu_han_hoac_ngoai_0_den_1_la_loi`, trong đó 2 ca NaN) |

Không đột biến nào sống sót nên không thêm test. Lưu ý khi chạy: hai lần đầu `.pyc` cũ làm đột biến trước rò sang đột biến sau (cùng kích thước và cùng giây sửa); bảng trên là lượt chạy lại với `PYTHONDONTWRITEBYTECODE=1` và `.pyc` đã xóa.

Thời gian (`tools/bench_skill_rates.py --runs 7`, 5.600 dữ kiện Zipf, seed 101, 36.450 hàng `stat_skill_rates`; giây, trung vị (nhỏ nhất–lớn nhất); tính và ghi đo riêng):

| Chế độ | Tổng bước | Tính tỷ lệ kỹ năng | Ghi (`replace_stats`) |
|---|---|---|---|
| bật | 7,426 (7,289–9,323) | 0,416 (0,410–0,450) | 2,708 (2,442–4,921) |
| tắt | 5,431 (5,216–11,327) | 0,000 | 1,139 (0,821–7,220) |

Chênh trung vị tổng +1,995 s (1,37 lần); tính tỷ lệ chiếm 0,42 s, phần còn lại là ghi thêm 36.450 hàng (+1,57 s). Đã sửa SC-001 ở `spec.md` cho khớp. Số cũ của đợt 1 (3 lượt, bản sao dữ liệu thật, +2 s) cùng cỡ.

## Đợt 2026-11-17 (#151, #106, #103): file dùng chung đổi, AC của issue này không đổi

Lý do: tỷ lệ kỹ năng thật (#151), phép 2 `select_cell` (#106) và ràng buộc lớp đọc (#103) sửa file mà issue này từng đụng:

  - `haido_core/domain/REGISTRY.md` (ghi thân hàm phép 2);

Hành vi và AC của issue này không đổi: thay đổi chỉ thêm (phương thức `skill_rates` thật, trường `order` có mặc định, một biến môi trường ở prod, một đoạn tài liệu); `city_shares`, `newcomer_roles`, `learning_path`, `skill_roles` của `StatMarket` giữ nguyên. Chi tiết: `specs/151-ty-le-ky-nang-that/plan.md`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #151, #106, #103 nằm ở `specs/151-ty-le-ky-nang-that/tdd.md`, `specs/106-chon-o-quay-ve/tdd.md`, `specs/103-api-doc-ty-le-that/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed; `cd web && npx vitest run` → 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

Cập nhật sau review (đợt 2, 2026-11-17): trong `StatMarket` chỉ `skill_rates` đổi thêm (404 khi ô không có hàng tỷ lệ, `n_scanned` nhất quán, chữ nhãn); hành vi và AC của issue này vẫn không đổi. RED và GREEN: `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `haido_core/db/snapshot_store.py`, `haido_core/db/tables.py`, `haido_core/steps/aggregate.py`, `tests/db/test_ad4_snapshot_schema.py`, `tests/db/test_dat20_stat_tables.py`, `tests/db/test_dat29_stat_skill_rates.py`, `tests/db/test_fr33_stat_city_shares_level.py`, `tests/db/test_fr33_stat_years.py`, `tests/db/test_gh283_facts_labels.py`, `tests/db/test_gh285_fact_city.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: sửa file mà issue này từng đụng (trong số `fake_market.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `tools/gates/check_gates.py`, `web/lib/learning-path.ts`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: sửa file mà issue này từng đụng (trong số `stat_market.py`, `check_gates.py`, `envelope-meta.md`, `compose.prod.yml`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.
