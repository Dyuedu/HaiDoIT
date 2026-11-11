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
