# Research: Trang listing TopCV rỗng thì thử lại sau

## Quyết định

- Trang vẫn rỗng sau `EMPTY_PAGE_TRIES` lần tải ngay thì không kết luận hết listing; để lại, đi tiếp, rồi tải lại sau một quãng nghỉ.
- Chỉ thử lại khi có lý do: trang rỗng kẹp giữa trang có tin, hoặc thiếu so với 90% tổng. Đêm bình thường không tốn thêm gì.
- Tối đa 2 vòng, nghỉ 120–240 giây mỗi vòng. Đây là số đoán; chỉnh theo log các đêm sau.

## Quan sát trên VPS (`daily-2026-11-18.log`)

- Tiêu đề ghi 2.502 việc làm, mỗi trang 50 thẻ, nên trang cuối khoảng 51.
- Trang 18, 20, 25 cần tải lại một lần; trang 41–44 cần 1–2 lần; trang 45 rỗng 3 lần. Mật độ trang rỗng tăng theo thời gian: TopCV chặn mềm, không trả trang Cloudflare.
- 45 trang cho 2.169 URL khác nhau (khoảng 48/trang): trang có thẻ trùng, nên trang cuối thật có thể lớn hơn `ceil(tổng / 50)`. Đi quá trang đó không hại: lượt #302 ngày 16/11 thấy trang 47 lặp lại trang 46, và crawler dừng ở trang lặp.

## Nguyên nhân trang rỗng (đọc lại log, 2026-11-18)

- Trang 24 chỉ có 22/50 thẻ: HTML bị đọc khi danh sách mới tải được một phần. `fetch()` cũ gọi `page.select("div.job-item-search-result", timeout=6)`, trả về ngay khi thẻ đầu tiên có trong DOM, rồi `get_content()`.
- Trang rỗng: thẻ đầu chưa có sau 6 giây, ngủ 1,5 giây rồi đọc.
- Listing đêm 18/11 không có trang Cloudflare nào; đêm 17/11 có 2 lần, qua được, không trang nào rỗng. Tải lại ngay thường ra tin.
- Kết luận tạm: TopCV trả chậm (tải phía họ lúc 2–3 giờ sáng, hoặc làm chậm theo IP), crawler đọc sớm. Chưa loại được trang "nhẹ" không có danh sách mà không phải Cloudflare, nên lưu HTML để kiểm.

## Cách làm tham khảo

- [scrapy/scrapy, `scrapy/downloadermiddlewares/retry.py` @953a7f4](https://github.com/scrapy/scrapy/blob/953a7f423a6e506bf47e44d52c7dd0e45c979b8b/scrapy/downloadermiddlewares/retry.py#L38-L118) và [`default_settings.py`](https://github.com/scrapy/scrapy/blob/953a7f423a6e506bf47e44d52c7dd0e45c979b8b/scrapy/settings/default_settings.py#L609-L610): request lỗi được tạo lại với `priority = priority + RETRY_PRIORITY_ADJUST` (mặc định −1), tức xếp sau các request đang chờ; số lần thử là hằng `RETRY_TIMES`. Lấy: thử lại *sau* các trang khác chứ không ngay lập tức, và số vòng nằm ở hằng. Không lấy: hàng đợi ưu tiên và middleware. Vòng quét TopCV tuần tự, một trình duyệt, nên một danh sách trang rỗng và vòng thử lại cuối lượt là đủ.
- `specs/296-itnavi-di-het-listing/research.md` (trong repo): ITnavi chọn *không* thử lại trang trống vì site trả trang trống thật ở cuối và đối chiếu tổng là đủ. TopCV khác: trang rỗng nằm giữa listing, đối chiếu tổng chỉ nói được là thiếu chứ không lấy lại được tin. Giữ chung ngưỡng `MIN_COVERAGE = 0.9`.

- Chờ số phần tử đứng yên thay vì chờ phần tử đầu tiên: cùng ý với `networkidle` / `wait_for_load_state` của Playwright, nhưng nodriver không có sẵn, nên tự đếm bằng `page.evaluate` (nodriver 0.50.99, `Tab.evaluate` trả thẳng giá trị chuỗi). Lấy `readyState` `interactive` là đủ, không chờ `complete` vì ảnh và script quảng cáo có thể làm `complete` rất chậm; số thẻ đứng yên 3 nhịp (1,5 giây) bù cho phần còn lại.

## Không lấy

- **Nghỉ dài giữa mọi trang.** Làm đêm nào cũng chậm, kể cả đêm TopCV không chặn. Thử lại chỉ tốn thời gian ở đêm có trang rỗng.
- **Mở lại trình duyệt hay đổi profile trước vòng thử lại.** Chưa có dấu hiệu TopCV gắn chặn mềm với phiên trình duyệt; để sau nếu log cho thấy vòng thử lại vẫn rỗng.
- **Thử lại cả trang bị chặn (Cloudflare).** #302 quyết định trang bị chặn dừng lượt; giữ nguyên.
