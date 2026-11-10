# Research: Gộp tin trùng chéo nguồn

## Quyết định

Khóa cụm là công ty đã chuẩn hóa cộng chức danh đã chuẩn hóa. Thiếu một trong hai thì tin đứng riêng. Đại diện chọn theo hạng nguồn, rồi số trường thống kê, rồi URL.

## Cách các repo công khai làm

- [rezearcher/unified-jobs-scraper-cli](https://github.com/rezearcher/unified-jobs-scraper-cli): khóa `normalized-company | normalized-title | city`. Bỏ hậu tố pháp lý (Inc, LLC). Giữ từ cấp bậc trong chức danh để không gộp hai vị trí khác nhau. Bản ghi không khớp chắc thì giữ riêng, không xóa.
- [ever-jobs canonical-key.ts](https://github.com/ever-jobs/ever-jobs/blob/6eedb2ed/packages/common/src/canonical-key.ts): khóa `normCompany | normTitle | normLocation`. Hàm thuần, cùng đầu vào thì cùng khóa. Đại diện là giá trị đã chọn, mọi nguồn vẫn được giữ.
- [JobHunt_Spark_Agent, bước chuẩn hóa](https://github.com/nanduxdev/JobHunt_Spark_Agent/blob/main/instructions/03_JOB_NORMALIZATION_AND_DEDUPLICATION.md): một tin logic, nhiều `source_variant`. Khớp theo công ty + chức danh + thành phố trước, rồi mới tới so gần đúng. Không xóa biến thể cũ.

## Vì sao không lấy thành phố vào khóa

Hai sàn thường ghi địa điểm khác chuỗi cho cùng một tin ("Hà Nội" và "Ha Noi, Việt Nam"). Đưa địa điểm vào khóa sẽ tách đôi tin mà issue yêu cầu đếm một. Thành phố trên bản đồ lấy từ đại diện.

## Vì sao không dùng Jaccard tập kỹ năng

Dữ kiện snapshot hiện có chức danh, công ty, địa điểm, kinh nghiệm, cấp bậc. Chưa có tập mã kỹ năng trên tin. Issue #100 yêu cầu đếm cụm và quy tắc đại diện, không yêu cầu tập kỹ năng.

## Vì sao giữ từ cấp bậc trong chức danh

`job-radar` và unified-jobs-scraper đều giữ "Senior" và "Junior" trong chức danh. "Backend Dev" và "Senior Backend Dev" là hai tin cho tới khi có khóa chặt hơn.
