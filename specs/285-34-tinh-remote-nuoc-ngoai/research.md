# Research: tỉnh, thành sau sáp nhập 2025 và đọc địa chỉ trong tin

Ngày 13/11/2026.

## tranngocminhhieu/vietnamadminunits

- Link: https://github.com/tranngocminhhieu/vietnamadminunits/blob/7fac8c45805aad9916b17237c54baf4502303b93/data/interim/convert_legacy_2025_simple.csv
- Cách làm: bảng chuyển từng phường/xã của 63 tỉnh cũ sang 34 tỉnh, thành mới (hiệu lực 1/7/2025, Nghị quyết 202/2025/QH15), kèm bộ bí danh tên tỉnh (`data/alias_keywords/`).
- Lấy: đối chiếu bảng tỉnh cũ → tỉnh mới của issue này. Chạy trên file trên: 63 tỉnh cũ → 34 tỉnh mới; 29 tỉnh bị nhập, khớp đúng bảng trong `config/classify.toml` (ví dụ Bình Dương, Bà Rịa - Vũng Tàu → TP.HCM; Quảng Nam → Đà Nẵng; Hải Dương → Hải Phòng; Sóc Trăng, Hậu Giang → Cần Thơ; Bắc Giang → Bắc Ninh; Thái Bình → Hưng Yên; Hà Nam, Nam Định → Ninh Bình; Vĩnh Phúc, Hòa Bình → Phú Thọ; Long An → Tây Ninh; Bình Phước → Đồng Nai; Bình Định → Gia Lai; Kon Tum → Quảng Ngãi; Phú Yên → Đắk Lắk; Ninh Thuận → Khánh Hòa; Đắk Nông, Bình Thuận → Lâm Đồng; Bến Tre, Trà Vinh → Vĩnh Long; Tiền Giang → Đồng Tháp; Kiên Giang → An Giang; Bạc Liêu → Cà Mau; Quảng Bình → Quảng Trị; Hà Giang → Tuyên Quang; Yên Bái → Lào Cai; Bắc Kạn → Thái Nguyên).
- Không lấy: thư viện và bảng cấp phường. Tin tuyển dụng chỉ ghi tỉnh/thành hoặc tên thành phố, khu công nghiệp; kéo thêm 10.040 phường cũ làm dò chữ chậm và dễ khớp nhầm (tên phường trùng chữ thường dùng). Không thêm phụ thuộc.

## Dữ liệu thật (bản sao local, snapshot 12/11/2026)

Đếm ở lượt thử của #283/#285 (`scratchpad/skills/cities.py`): trường `location` ghi đúng một tỉnh ở 5855/6255 tin, trống ở 283 tin; đọc thêm dòng địa chỉ trong JD còn 199 tin không xác định. 48 tỉnh cũ xuất hiện; 88 tin nhắc nơi ở nước ngoài (71 chỉ trong JD), 36 tin remote (chỉ trong JD). Hà Nội và TP.HCM chiếm khoảng 92% tin IT.

## Dung lượng

Ghi đủ mọi (vai trò, cấp, số năm, nơi) cho 37 nơi là khoảng 73.000 hàng `stat_*` mỗi đêm, quá sức gói Supabase khi giữ nhiều snapshot. Quyết định: ghi hàng của một nơi chỉ khi nơi đó có ít nhất một tin trong bộ lọc, cộng nhóm luôn có (`always_cities`: Hà Nội, TP.HCM, Đà Nẵng, Remote, Nước ngoài, Không xác định). Tỷ trọng vẫn cộng lại bằng 1 vì hàng bị bỏ đều bằng 0.
