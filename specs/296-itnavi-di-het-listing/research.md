# Research: ITnavi đi hết listing

## Quyết định

- Trang trống kết thúc listing. Trang trùng hết chỉ kết thúc khi lặp `STALE_PAGES` lần liền.
- Lượt quét chỉ "đủ" khi gặp ≥ 90% tổng số tin site in trên trang.

## Quan sát trên site (2026-11-15)

Quét một lượt bằng `PoliteClient` của dự án (UA thật, 3 giây/request):

- 49 trang, 482 id khác nhau; trang 50 và trang 200 trống. Site không lặp trang cuối, nó trả trang trống.
- Trang 9, 14, 17 chỉ có 9/10 id mới: thứ tự xô lệch giữa các request. Một đêm xô nhiều hơn là đủ cho một trang trùng hết.
- Thứ tự id trong trang không đơn điệu (trang 45: 23678, 23785, 24126...), nên không dừng theo id được.
- Mỗi trang listing có `div.js-tab__show h1` ghi "485 Việc làm", gần với 482 id gặp được.

## Cách làm tham khảo

- [speedyapply/JobSpy, `jobspy/linkedin/__init__.py` @68b88d6](https://github.com/speedyapply/JobSpy/blob/68b88d6909a2342ad75fbb945c4204a3a7ed6665/jobspy/linkedin/__init__.py#L65-L110): vòng phân trang giữ tập `seen`, dừng khi `not new_cards` hoặc trang ít hơn số tin mỗi trang. Lấy: tập `seen` và tách "trang không có thẻ" với "trang không có id mới". Không lấy: dừng ngay khi một trang không có id mới. JobSpy chỉ cần "đủ N tin", còn Hải Đồ cần biết chắc đã đi hết, nên một trang trùng không đủ để kết luận. JobSpy cũng phân biệt trang trống thật với trang trống bất thường ("blocked?"), giống ý đối chiếu với tổng số ở đây.
- `scraper/crawlers/topdev.py` (trong repo): đã dùng `MIN_COVERAGE = 0.9` so với `total` site báo. Lấy cùng ngưỡng để hai crawler nói "đủ" theo cùng một nghĩa.

## Không lấy

- **Tính số trang từ tổng (485 / 10 = 49) rồi đi đúng chừng ấy trang.** Tổng đổi trong lúc quét và thứ tự xô lệch, đi đúng 49 trang vẫn có thể sót. Đi tới trang trống rồi đối chiếu thì chịu được cả hai.
- **Thử lại trang trống.** Không biết trang trống là tạm thời hay hết thật; đối chiếu tổng trả lời câu này mà không tốn thêm request ở cuối mỗi đêm.
