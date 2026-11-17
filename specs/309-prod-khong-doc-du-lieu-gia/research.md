# Research: Production không bao giờ phục vụ fixture giả

## Tham khảo

- Django, kiểm tra cấu hình khi deploy (`manage.py check --deploy`): https://github.com/django/django/blob/4e7c04fdfa7651d0cda59fb4d8020fb644d1a401/django/core/checks/security/base.py
  - Lấy: ý "mặc định tiện cho dev, nhưng có một bước kiểm riêng cho cấu hình production" (các check `deploy=True`, ví dụ `DEBUG` phải tắt). Ở đây bước đó là test đọc compose.prod.
  - Không lấy: cơ chế đăng ký check lúc chạy. Hải Đồ chưa có cờ "đang chạy prod" trong app; thêm cờ đó để app từ chối khởi động với nguồn `fake` là thay đổi lớn hơn và lặp lại thông tin mà compose.prod đã giữ.
- Trong repo: `tests/deploy/test_gh166_ky_nang_vai_tro_doc_snapshot_that.py` (#166) và test cùng khuôn của #146. Lấy cách đọc YAML; bỏ cách chép tay tên biến, vì chính việc chép tay từng biến là lý do `skill_rates` và `learning_path` bị sót.

## Quyết định

Không đổi `DEFAULT_SOURCE` sang `stat`: CI smoke và môi trường dev chạy trên DB rỗng và dựa vào bản giả (`compose.local.yml`). Chặn ở compose.prod bằng test sinh từ `SOURCE_ENV`.
