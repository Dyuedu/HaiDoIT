# Research: phân loại tin và trích kỹ năng bằng luật trong repo public

Ngày 13/11/2026. Tìm trên GitHub các bộ trích kỹ năng không dùng mô hình sinh, và các bộ gán nghề từ chức danh. Kèm một lượt thử trên dữ liệu thật (bản sao local của prod, snapshot 12/11/2026) trước khi viết spec.

## AnasAito/SkillNER

- Link: https://github.com/AnasAito/SkillNER/blob/e8cdbb6f591211bf5d0fe2c8a61ddb95526a78b3/skillNer/matcher_class.py (MIT).
- Cách làm: mỗi kỹ năng có một id và nhiều "surface form" (dạng đầy đủ, viết tắt, dạng thấp tin cậy). Bộ so khớp là một chuỗi matcher theo thứ tự: khớp đủ cụm nhiều từ, khớp viết tắt, khớp một từ, khớp dạng thấp, rồi chấm điểm n-gram. Khớp đủ cụm dài được ưu tiên trước.
- Lấy: một mã kỹ năng có nhiều bí danh; so cụm dài trước cụm ngắn trong cùng một đoạn (một regex xen kẽ sắp theo độ dài giảm dần, khớp không chồng lấn); tách "dạng đáng tin" khỏi chữ quá chung (ở đây: bỏ hẳn bí danh mơ hồ khỏi bộ từ vựng).
- Không lấy: spaCy và cơ sở EMSI (chỉ tiếng Anh, không có "kiểm thử", "lập trình nhúng"); bước chấm điểm n-gram (khớp một phần cho ra kỹ năng sai, khó kiểm thử); không có khái niệm mục trong JD nên đếm cả chữ ở phần giới thiệu công ty.

## aeturrell/occupationcoder

- Link: https://github.com/aeturrell/occupationcoder/blob/dbaee15a2015fa5b80dc3fb7ea235190dbeb1ea4/occupationcoder/coder.py#L62-L139 (MIT).
- Cách làm: làm sạch chức danh, thử khớp đúng chức danh với danh sách chức danh biết trước của từng mã nghề; không khớp thì dùng TF-IDF trên chức danh + mô tả + ngành để chọn 5 mã ứng viên, rồi so mờ chức danh với các mã đó.
- Lấy: hai tầng "chức danh trước, mô tả sau": chức danh nói rõ vai trò thì thắng; chức danh chung chung ("Software Engineer", "Lập trình viên") mới dựa vào bằng chứng trong mô tả. Làm sạch chức danh (bỏ cấp, địa điểm, lương) trước khi so.
- Không lấy: TF-IDF và so mờ (ngưỡng điểm, kết quả đổi khi danh sách đổi, cần thêm sklearn và rapidfuzz). Ở đây tầng hai là đếm mã kỹ năng có trọng số theo vai trò, cùng đầu vào thì cùng nhãn.

## nestauk/ojd_daps_skills

- Link: https://github.com/nestauk/ojd_daps_skills/tree/e73c2b5045793d891678ad387b2c7fda1756d236 (MIT).
- Cách làm: mô hình NER (spaCy, có huấn luyện) tách "skill entity" và "experience entity" trong tin, rồi một bước riêng ánh xạ chuỗi kỹ năng sang taxonomy (ESCO/Lightcast).
- Lấy: tách bước tìm lượt nhắc khỏi bước ánh xạ sang mã, đúng như phép 1 `map_mentions` của `REGISTRY.md` (lượt nhắc → mã, không khớp thì `None`); tách câu kinh nghiệm ("3 năm kinh nghiệm") khỏi kỹ năng.
- Không lấy: mô hình NER có huấn luyện (cần dữ liệu gán nhãn tiếng Việt, kết quả khó giải thích, trái tinh thần "cùng đầu vào cùng nhãn" của phép 6).

## Lượt thử trên dữ liệu thật (scratchpad, không vào repo)

Chạy bản nháp luật trên 6255 tin trong cửa sổ 60 ngày của bản sao local, so với luật hiện tại (`classify.py`, chỉ đọc chức danh) và với nhãn của bước trích (`title_category`, `seniority_category`, `years_experience_min` do Haiku ghi trong `public.jobs`).

| | Luật hiện tại | Bản nháp | Bước trích |
|---|---|---|---|
| Khớp vai trò với bước trích | 46% | 81% | — |
| Nhận ra tin IT (so với bước trích) | precision 78%, recall 50% | precision 94%, recall 90% | — |
| Tin AI/ML / trong đó mới vào nghề | 110 / 11 | 213 / 42 | 206 / 25 |
| Số năm khớp (kể cả cả hai không ghi) | — | 91% | — |

Tự đọc 30 tin lệch vai trò: bước trích đúng khoảng 21, bản nháp đúng 1–3, còn lại khó phân xử. Lỗi của bản nháp phần lớn là lỗi luật sửa được, và spec này ghi thành scenario: "ba" khớp "Ba Vì"; "học máy" khớp trong "khoa học máy tính" sau khi bỏ dấu; "soc" khớp "chăm sóc"; thiếu "cybersecurity", "an ninh thông tin"; "e-commerce" bị coi là không thuộc IT; "di động" khớp "mạng di động 4G/5G"; "Product Manager" bị coi là cấp quản lý; "Experienced (non-manager)" của VietnamWorks bị đọc thành cấp quản lý; game artist bị coi là lập trình game.

Tự đọc 22 tin lệch số năm: bước trích đúng khoảng 18. Lỗi chính của bản nháp là lấy số nhỏ nhất ("tối thiểu 5 năm, trong đó 2 năm quản lý" ra 2). Sửa thành lấy yêu cầu chính thì khớp 91%. Bước trích sai có hệ thống ở "không yêu cầu kinh nghiệm": trả `null` thay vì 0 (bản nháp ra 0 ở 70 tin IT, bước trích ở 19).

Kết luận dùng cho thiết kế: số năm lấy giá trị của bước trích khi có, bù bằng luật ("không yêu cầu kinh nghiệm" → 0, số tháng có cấu trúc của nguồn); vai trò và cấp bằng luật đọc chức danh + mã kỹ năng từ các mục yêu cầu và nhiệm vụ.
