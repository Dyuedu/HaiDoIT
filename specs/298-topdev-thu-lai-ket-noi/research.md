# Research: TopDev thử lại khi rớt kết nối

## Quyết định

- Thử lại trong crawler, chỉ cho `ConnectionError`, `Timeout`, `ChunkedEncodingError`; tổng 4 lần, chờ 30, 60, 120 giây.
- Không thử lại `BlockedError` hay lỗi HTTP.

## Cách làm tham khảo

- [urllib3, `src/urllib3/util/retry.py` @d9f9b0a](https://github.com/urllib3/urllib3/blob/d9f9b0ad5b99247e06aa9a50b7a5747aa5c2e35d/src/urllib3/util/retry.py#L324-L344): `get_backoff_time()` = `backoff_factor × 2^(số lỗi liên tiếp − 1)`, chặn trên bởi `backoff_max`. Lấy: công thức chờ tăng gấp đôi. Không lấy: gắn `Retry` vào `HTTPAdapter` của `PoliteClient`, vì client dùng chung cho mọi crawler và cả bước robots; đổi ở đó làm thay đổi hành vi của mọi nguồn, ngoài phạm vi issue.
- [scrapy, `scrapy/settings/default_settings.py` @e63a574](https://github.com/scrapy/scrapy/blob/e63a574c767d7a9438c21db158f605f1c44c6e6a/scrapy/settings/default_settings.py#L592-L610): mặc định thử lại các lỗi kết nối (`ConnectionLost`, `ConnectError`, `DownloadTimeoutError`...) với `RETRY_TIMES = 2`, và tách riêng danh sách mã HTTP. Lấy: chỉ thử lại lỗi tầng kết nối, liệt kê tường minh. Không lấy: thử lại 429, vì luật của Hải Đồ coi 429 là bị từ chối và dừng.
- [jd/tenacity @aac059c](https://github.com/jd/tenacity/tree/aac059c906170ee7b6ce1aa086a226f3aded5c99): thư viện decorator thử lại. Không lấy: thêm một dependency cho một vòng lặp sáu dòng, và test cần đếm chính xác số lần chờ qua `topdev.time.sleep`, vốn đã được các test cũ dùng.

## Không lấy

- **Tiếp tục từ trang lỗi ở lượt sau.** Lượt đêm là một ngày quan sát; thử lại ngay trong lượt là đủ cho lỗi mạng thoáng qua.
- **Thu hẹp TopDev về danh mục IT để quét ít trang hơn.** Đó là đổi phạm vi dữ liệu (docstring của `topdev.py` ghi danh mục IT chỉ bắt 80% tin IT), không thuộc issue này.
