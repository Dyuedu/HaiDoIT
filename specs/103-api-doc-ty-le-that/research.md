# Research: API đọc tỷ lệ kỹ năng thật (#103)

Ngày 17/11/2026.

Cùng phần research với `specs/106-chon-o-quay-ve/research.md` và `specs/151-ty-le-ky-nang-that/research.md` (cùng một nhánh, cùng một lát cắt).

- Hai ràng buộc của issue này đã có tiền lệ trong repo: cổng AD-7 của `tools/gates/check_gates.py` (quét chữ trong `haido_api/`) và test ghi lại SQL ở `tests/api/test_fr37_newcomer_roles_stat.py` (fixture `statements`). Dùng lại cách ghi SQL qua sự kiện `before_cursor_execute`; không viết cổng mới.
- Không lấy: kiểm bằng đọc AST của mã để tìm `GROUP BY`. Test ghi SQL thật bắt được cả SQL dựng động, mà cổng chữ không thấy.
