# Research: bộ lọc số năm kinh nghiệm trong repo public

Ngày 12/11/2026. Tìm bằng `gh search code` các từ `max_years_experience`, `min_years_of_experience`.

## matiasoliveraqa/job-hunter

- Link: https://github.com/matiasoliveraqa/job-hunter/blob/8371e34d3faa3a2cea3ec52e810604c2739bac96/src/scanners/base.py#L662-L672 và https://github.com/matiasoliveraqa/job-hunter/blob/8371e34d3faa3a2cea3ec52e810604c2739bac96/src/scanners/lever.py#L74-L84
- Cách làm: `matches_experience(text, max_years)` giữ tin khi số năm yêu cầu ≤ `max_years`; tin không ghi số năm **được giữ**. Số năm trích bằng regex từ mô tả lúc lọc.
- Lấy: ngữ nghĩa "tối đa N năm" so với số năm **tối thiểu** tin yêu cầu (`req_years > max_years` thì loại), đúng nhu cầu "tôi có N năm, tin nào nộp được".
- Không lấy: giữ tin không ghi số năm. Ở đây khoảng 32% tin không ghi; nếu giữ, mọi mốc đều mang cùng khối tin đó và số của mốc 0 năm bị thổi phồng. AC 3 của #280 chọn bỏ ra và nói rõ đã bỏ bao nhiêu. Không lấy regex lúc lọc: số năm đã được bước trích ghi sẵn (`years_experience_min`), kho chỉ chép.

## Clueless-Community/scrape-up (Wuzzuf)

- Link: https://github.com/Clueless-Community/scrape-up/blob/5a92d9b64d25329035c4afc0ef7f18e49d774997/src/scrape_up/wuzzuf/wuzzuf.py#L24-L60
- Cách làm: bộ lọc của Wuzzuf nhận `years_of_experience_min` và `years_of_experience_max` như hai tham số URL, lọc phía máy chủ.
- Lấy: số năm là tham số truy vấn của API, một mã cho mỗi lựa chọn.
- Không lấy: hai đầu min/max tự do. Ô thống kê phải tính trước cho từng lựa chọn (AD-5: API không đếm lúc gọi), nên lựa chọn là danh sách mốc cố định trong config.

## openedx/taxonomy-connector

- Link: https://github.com/openedx/taxonomy-connector/blob/5c7e5094e406a3486792dcfb3eba39a487492808/src/taxonomy/enums.py#L33-L34
- Cách làm: dữ liệu tin tuyển dụng (Lightcast) mang hai trường `min_years_experience`, `max_years_experience` tách riêng.
- Lấy: lọc theo trường tối thiểu, vì đó là ngưỡng nộp được.
- Không lấy: trường tối đa (scraper có `years_experience_max` nhưng AC không cần).
