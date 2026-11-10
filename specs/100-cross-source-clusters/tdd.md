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
