# Research: Câu chữ trên màn hình viết bằng tiếng Việt dễ hiểu

## Tham khảo

- 18F Content Guide, "Use plain language": https://github.com/18F/content-guide/blob/1b1723d3d5b8f91d92c16487c88b56265dc0ec3a/_pages/our-approach/plain-language.md
  - Lấy: viết như đang nói với một người, dùng từ ngắn thay từ chuyên môn khi từ ngắn đủ nghĩa. Áp vào: "Cỡ mẫu nhỏ (n = 12 < 30)" thành "Mới có 12 tin, chưa đủ 30".
  - Không lấy: danh sách từ cần tránh của tiếng Anh.
- 18F Content Guide, "Abbreviations and acronyms": https://github.com/18F/content-guide/blob/1b1723d3d5b8f91d92c16487c88b56265dc0ec3a/_pages/our-style/abbreviations-and-acronyms.md
  - Lấy: tránh ký hiệu và viết tắt người đọc không quen. Áp vào: bỏ `n`, bỏ "snapshot", "entry-level"; tên nguồn viết như chính trang đó viết.
- 18F Content Guide, "Numbers, percentages, and dates": https://github.com/18F/content-guide/blob/1b1723d3d5b8f91d92c16487c88b56265dc0ec3a/_pages/our-style/numbers-and-percentages.md
  - Lấy: nhãn giao diện dùng chữ số và dấu `%` để dễ quét. Giữ "29,4%" nổi bật, số tin bằng chữ số.
  - Không lấy: viết chữ các số từ một tới chín (quy ước tiếng Anh, và ở đây số đứng cạnh số khác).
- Our World in Data grapher, chân biểu đồ: https://github.com/owid/owid-grapher/blob/c94293a6db2ed50486f8f6014072fb0b2cf13edb/packages/@ourworldindata/grapher/src/footer/Footer.tsx
  - Lấy: nguồn và ghi chú đặt ở chân biểu đồ bằng nhãn ngắn ("Sources", "Note"), tên nguồn viết đầy đủ chứ không theo mã.
  - Không lấy: bố cục chân biểu đồ và nút tải; khung "Nguồn và lưu ý" của Hải Đồ giữ chỗ cũ.

## Quyết định

- Đổi chữ ở tầng view (`web/lib/*-view.ts`), nơi test đã kiểm chuỗi; component chỉ in.
- Tên nguồn để file riêng `web/lib/source-labels.ts`, không thêm vào `labels.ts` (file đó được test deploy so với `config/rules.toml`, và chín issue khác đã đụng).
- "Hôm nay chưa lấy đủ…" trong bảng duyệt viết thành "Lần cập nhật này chưa lấy đủ…", vì số trên màn có thể của ngày trước.
- Dòng 0 tin ghi "Chưa có tin nào" thay vì "Mới có 0 tin…".
