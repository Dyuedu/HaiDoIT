# TDD: Gộp tin trùng chéo nguồn

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh của repo: `uv run pytest <file> -q`. Test nhỏ, không mạng, không database, cho hành vi thuần. Test bước aggregate dùng Postgres và marker `postgres`.

Mỗi test một hành vi. Assert đầu ra, không assert hàm nội bộ đã được gọi. Tên test nói điều kiện và kết quả.

## RED

Viết `tests/domain/test_dat28_cluster.py` khi `haido_core/domain/cluster.py` chưa có. `uv run pytest tests/domain/test_dat28_cluster.py -q` phải fail.

Các hành vi:

1. "Công ty TNHH FPT" + "Java-Backend" cùng khóa với "FPT" + "Java Backend".
2. "FPT Software" khác khóa với "FPT".
3. Thiếu công ty hoặc chức danh thì không có khóa, và tin đó là cụm riêng.
4. Hai nguồn cùng khóa thành một cụm. Dân số ô của `cluster_id` đó là 1.
5. Hạng nguồn thắng số trường. Cùng hạng thì nhiều trường thắng. Cùng hạng và cùng số trường thì URL có giá trị thắng URL trống, rồi A–Z, rồi mã tin.
6. Đảo thứ tự đầu vào không đổi đại diện và không đổi `cluster_id`.
7. `match_postings` khớp chéo nguồn khi khác nguồn cùng khóa, khớp trong nguồn khi cùng nguồn cùng khóa, và không khớp khi thiếu khóa.
8. Một cặp trả `MatchDecision`. Một lô trả tuple cùng độ dài.

## GREEN

Code tối thiểu trong `cluster.py`, `matching.py`, `config.py`, `aggregate.py` để các test đó và test dân số hiện có cùng xanh.

## REFACTOR

Giữ hàm thuần. Không thêm gói. Chạy lại đúng file test sau mỗi lần sửa.

## Đợt 2 — 2026-11-11, sửa theo #163 (ô theo cấp bậc lọc được)

Lý do: `aggregate` ghi thêm ô và tỷ trọng theo cấp bậc, nên các số đếm hàng và truy vấn trong `tests/steps/test_dat20_aggregate_step.py` đổi. Hành vi gộp cụm của #100 không đổi.

Lệnh: `uv run pytest tests/steps/test_fr33_aggregate_level_step.py tests/steps/test_dat20_aggregate_step.py -q` (cần `HAIDO_TEST_DATABASE_URL`).

Hành vi thêm: 9. Hai nguồn cùng khóa, đại diện là Junior (ITviec) còn thành viên kia là Senior (TopCV), cụm đếm ở `entry` và `junior`, không đếm ở `senior`.

### RED

Sau khi thêm migration 0005 mà `aggregate` chưa ghi cột `seniority`: `tests/steps/test_fr33_aggregate_level_step.py` 12 failed (`NotNullViolation: null value in column "seniority" of relation "stat_city_shares"`), gồm test cụm ở mục 9. Ở lần chạy `tests/steps` đầu sau khi có code, `tests/steps/test_dat20_aggregate_step.py` 19 failed (cùng `tests/steps/test_dat20_api_end_to_end.py` và `tests/test_dat20_cli.py`, tổng 21) vì mỗi (vai trò, phạm vi) giờ có 9 hàng `stat_cells` và truy vấn cũ không lọc `seniority`.

### GREEN

`tests/steps/test_fr33_aggregate_level_step.py` 12 passed. Sau khi sửa truy vấn và số đếm (66 → 594 ô, 55 → 495 tỷ trọng), `tests/steps` + `tests/test_dat20_cli.py` + `tests/test_ad4_cli.py` xanh. Các đợt trước giữ nguyên.

## Đợt 2026-11-12 — #280 thêm chiều số năm kinh nghiệm

Lý do: #280 sửa `haido_core/domain/aggregate.py`, `population.py`, `steps/aggregate.py`, `db/snapshot_store.py`, `config.py`: hàm tổng hợp lọc tập cụm theo mốc số năm rồi chạy lại cùng phép đếm; số năm của cụm lấy từ tin đại diện.

- RED: không có test nào của #100 đổi kỳ vọng. `test_dat28_hai_nguon_cung_cong_ty_va_chuc_danh_dem_mot_va_lay_thanh_pho_dai_dien` đỏ một lượt vì helper `_n` gặp 6 hàng `stat_cells` (một hàng mỗi mã số năm), sửa bằng `years = 'any'` (xem tdd của #280).
- GREEN: `tests/domain/test_dat28_cluster.py`, `tests/steps/test_dat20_aggregate_step.py`, `tests/steps/test_fr33_aggregate_level_step.py` xanh; `uv run pytest -q` → 770 passed.

## Đợt 2026-11-13 — #283 nhãn của tin đại diện lấy từ dữ kiện đã lưu

Lý do: #283 sửa `haido_core/steps/aggregate.py`: nhãn vai trò và cấp của cụm lấy từ dữ kiện đã lưu của tin đại diện khi
`classify_version` khớp, không thì phân loại từ trường đóng như trước. Quy tắc cụm và chọn tin đại diện không đổi. Không AC
nào của #100 đổi.

- RED: `test_dat20_nguon_chi_it_thi_tin_khong_ro_vai_tro_la_other_va_tin_ngoai_it_bi_loai` đỏ vì "Nhân viên kinh doanh" nay là
  không thuộc IT; đổi ví dụ sang "Chuyên viên sản phẩm" (không mang cụm nào), giữ ý của test.
- GREEN: `tests/domain/test_dat28_cluster.py`, `tests/steps/test_dat20_aggregate_step.py` xanh; `uv run pytest -q` → 887 passed.

## Đợt 2026-11-13 — #285 34 tỉnh, Remote, Nước ngoài

Lý do: #285 đổi mã nơi (nơi của cụm lấy từ `job_posting_facts.city` của tin đại diện khi `classify_version` khớp). Không AC nào của issue này đổi.

- RED: `test_dat20_ty_trong_thanh_pho_va_n_dung_cho_tung_vai_tro` đỏ vì dòng `other`.
- GREEN: sửa kỳ vọng theo mã nơi mới; `uv run pytest -q` → 947 passed; `npx vitest run` → 166 passed.


## Đợt 2026-11-16 (theo #101)

Lý do: #101 sửa `haido_core/steps/aggregate.py` (vòng gộp cụm đưa mỗi cụm một tin mang hợp kỹ năng của mọi thành viên trong cửa sổ; cách gộp cụm và chọn đại diện không đổi), `haido_core/db/snapshot_store.py`, `haido_core/db/tables.py`. Test của issue này không phải sửa. `tests/db/test_dat20_stat_tables.py` (kiểm head Alembic, thuộc #93) đổi sang head 0009. Không thêm hành vi mới nào của issue này, không AC nào đổi.

Chạy lại thật sau thay đổi (đợt 2 của #101): `uv run pytest tests/domain/test_dat28_cluster.py tests/steps/test_dat20_aggregate_step.py -q` → **48 passed**. Toàn bộ `uv run pytest -q` → **1194 passed**.

## Chạy lại (2026-11-17, #302)

#302 sửa `config/rules.toml` (`[sources].auto` thêm `topcv`, `config_version` lên `2026-11-17.1`), `tests/core/test_ad10_rules_config.py` và `tests/steps/test_ad4_ingest.py` (ví dụ nguồn chạy tay đổi từ `topcv` sang `linkedin`). Không đổi scenario của issue này.

- `uv run pytest -q` → 1018 passed, 217 skipped.

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `config/rules.toml`, `haido_core/config.py`, `haido_core/db/snapshot_store.py`, `haido_core/db/tables.py`, `haido_core/steps/aggregate.py`, `tests/core/test_ad10_rules_config.py`, `tests/db/test_dat20_stat_tables.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. Riêng `tests/core/test_ad10_rules_config.py`: `rules.toml` không còn `theta_core`/`theta_common` nên `BASE` dùng `theta_version`, và các ca kiểm θ cũ (thiếu khóa, giá trị ngoài [0, 1], `theta_common > theta_core`) đã chuyển sang `tests/core/test_gh102_theta_dong_bang.py`, nay kiểm trên `config/theta.toml`. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.
