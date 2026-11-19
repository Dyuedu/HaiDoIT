# Research: Hình response của toàn cảnh thị trường

## Tham khảo

- Our World in Data, `owid/etl`: https://github.com/owid/etl/tree/a13692fd543e2432ba59cec34996c5a4cf6c42b1
  - Lấy: chỉ số được tính sẵn ở bước dữ liệu, biểu đồ chỉ vẽ giá trị đã có. Áp vào: máy chủ trả tỷ trọng đã chia, web không chia (AD-22).
  - Không lấy: kho dữ liệu nhiều tầng và định dạng xuất của họ; Hải Đồ đã có `stat_cells`.
- sdcMicro, ẩn ô nhỏ khi công bố bảng thống kê: https://github.com/sdcTools/sdcMicro/blob/39cbf5ec779a5a84b4ed90031f7d59028d119097/R/localSuppression.R
  - Lấy: ô nhỏ vẫn có mặt trong bảng nhưng được đánh dấu, không bị bỏ đi. Áp vào: vai trò dưới 30 tin vẫn có dòng; tỷ lệ cấp là `null_data`, tỷ trọng là `low_sample_shown`, theo `suppression_for` sẵn có.
  - Không lấy: thuật toán k-anonymity và ẩn cục bộ theo bản ghi; ở đây chỉ ẩn theo ngưỡng mẫu.
- Trong repo: `newcomer_roles` của `StatMarket` (#145) và `city_shares` (#93). Lấy cách gọi `suppression_for` theo `n` của ô mà `Stat` trỏ tới, và cách xếp thứ tự ở máy chủ.

## Quyết định

- Một route cho cả toàn cảnh, không ghép nhiều lượt gọi `city-shares` ở web: mockup cần 17 + 5 lượt gọi và vẫn phải tự chia số.
- Dùng chung biến nguồn với `newcomer-roles`. Thêm biến mới buộc sửa khoảng 20 chỗ dựng app trong test của các issue khác, trong khi hai phép đọc cùng ô toàn quốc.
- Mốc số năm chia theo `years_options` của `config/rules.toml`, không viết cứng.
