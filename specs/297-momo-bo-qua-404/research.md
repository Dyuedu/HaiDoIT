# Research: MoMo bỏ qua trang chi tiết 404

## Quyết định

- Lỗi HTTP hoặc kết nối ở một trang chi tiết: ghi log, bỏ qua, sang trang kế.
- `BlockedError` vẫn dừng. Mười lỗi liền nhau cũng dừng.

## Cách làm tham khảo

- [speedyapply/JobSpy, `jobspy/linkedin/__init__.py` @68b88d6](https://github.com/speedyapply/JobSpy/blob/68b88d6909a2342ad75fbb945c4204a3a7ed6665/jobspy/linkedin/__init__.py#L96-L103): mỗi tin xử lý trong `try`, lỗi thì `log.warning("skipping job: ...")` rồi `continue`; chỉ lỗi ở trang tìm kiếm mới `break`. Lấy: tách lỗi của một tin khỏi lỗi của cả nguồn. Không lấy: `except Exception` rộng, vì Hải Đồ phải để `BlockedError` đi qua để dừng.
- `scraper/crawlers/topdev.py` và `careerlink.py` (trong repo): đã bỏ qua trang chi tiết lỗi và dừng sau `MAX_CONSECUTIVE_FAILURES = 10`. Lấy cùng ngưỡng và cùng câu log để log đêm đọc giống nhau giữa các nguồn.

## Không lấy

- **Thử lại trang 404.** 404 ở đây là tin đã gỡ; thử lại chỉ tốn request.
- **Ghi dòng rỗng cho tin lỗi.** Raw file chỉ chứa tin có mô tả; tin đã gỡ vẫn có trong file seen của ngày đó nếu listing thấy nó.
