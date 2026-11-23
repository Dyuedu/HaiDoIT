# Research: bảng kỹ năng có bí danh và danh sách loại trừ trong repo public (#278)

Ngày 23/11/2026. Câu hỏi: các dự án mở giữ một bảng kỹ năng thế nào để nhiều cách viết (Anh, Việt, viết tắt) về một mã, và thẻ không phải kỹ năng (chức danh, địa điểm, chữ quá chung) được giữ ra ngoài ra sao. Số liệu của kho này (673 thẻ từ 20 tin, 304 thẻ chưa có mã) nằm ở [de-xuat-tu-vung.md](de-xuat-tu-vung.md).

## workforce-data-initiative/skills-ml

- Link: https://github.com/workforce-data-initiative/skills-ml/blob/feffead90815ccdecf24bf1a995f79683442b046/skills_ml/algorithms/skill_extractors/exact_match.py (MIT).
- Cách làm: `ExactMatchSkillExtractor` dựng bảng `id_lookup`: tên đã `lower()` của mỗi năng lực trong khung (`competency_framework`) → mã định danh, rồi một regex trie từ các khóa đó quét văn bản. Chỉ khớp đúng chuỗi sau khi hạ chữ thường; bộ khác trong cùng thư mục (`fuzzy_match.py`, `symspell.py`) khớp gần đúng.
- Lấy: một bảng phẳng "khóa đã chuẩn hóa → mã", dựng một lần từ danh sách tên; quét bằng một regex từ chính các khóa đó. Đây là cách `load_vocabulary` làm (`lookup` và `scan_terms`), thêm bỏ dấu.
- Không lấy: chỉ có tên chính (không có cột bí danh), nên "Cơ sở dữ liệu" và "database" sẽ là hai mã; khớp gần đúng (đổi kết quả theo ngưỡng, khó kiểm thử). Hai khóa trùng nhau thì lớp sau đè lớp trước, không báo lỗi; ở đây `load_vocabulary` ném `ValueError` khi một khóa thuộc hai mã.

## nestauk/ojd_daps_skills

- Link: https://github.com/nestauk/ojd_daps_skills/blob/e73c2b5045793d891678ad387b2c7fda1756d236/ojd_daps_skills/map_skills/format_taxonomy/esco_formatting.py#L259-L270 (MIT).
- Cách làm: bảng kỹ năng ESCO có `preferredLabel` và `altLabels`; `altLabels` được tách ra (`explode`) thành mỗi dòng một cách viết, cùng `id` với nhãn chính, nên nhiều cách viết trỏ về một mã. Một bước riêng (`hard_coded_mapper_formatting.py`, cùng thư mục) giữ bảng ánh xạ viết tay đè lên phần khớp mô hình.
- Lấy: mô hình "một mã, một tên chính, nhiều cách viết khác, mỗi cách viết là một dòng tra cứu"; bảng viết tay đứng trên phần tự động, nghĩa là quyết định của người thắng phỏng đoán. Ở đây quyết định đã duyệt (`quyet-dinh-2026-11-20.json`) là bảng viết tay đó.
- Không lấy: khớp bằng vector BERT và cosine (cùng thẻ có thể ra mã khác khi đổi mô hình; trái AC4: ánh xạ lại không gọi mô hình). Taxonomy ESCO/Lightcast nguyên bộ (chỉ tiếng Anh ở mức dùng được, không có "xử lý sự cố", "quản trị hệ thống"). Cũng không có chỗ cho thẻ "không phải kỹ năng": thẻ không khớp thì rơi xuống nhóm cha, còn ở đây cần nói rõ là bỏ và vì sao.

## AnasAito/SkillNER

- Link: https://github.com/AnasAito/SkillNER/blob/e8cdbb6f591211bf5d0fe2c8a61ddb95526a78b3/skillNer/matcher_class.py (MIT); dữ liệu: https://github.com/AnasAito/SkillNER/tree/e8cdbb6f591211bf5d0fe2c8a61ddb95526a78b3/skillNer (bộ `skill_db`, mỗi kỹ năng có nhiều "surface form").
- Cách làm: đã mô tả ở [specs/283-phan-loai-tu-jd/research.md](../283-phan-loai-tu-jd/research.md). Điểm liên quan ở đây: matcher tách dạng đáng tin (cụm đủ) khỏi dạng thấp tin cậy (từ đơn, viết tắt) và áp ngưỡng riêng cho dạng thấp.
- Lấy: ý "một thẻ có thể tra được nhưng không được quét trong văn bản" thành `scan_skip`: `cloud`, `api`, `monitoring`, `windows`, `rest`… tra được thẻ của site về mã, nhưng không quét trong JD vì trong văn bản chúng quá chung. #283 đã có `scan_skip` cho `c`, `r`, `go`; #278 mở rộng cùng cơ chế.
- Không lấy: chấm điểm n-gram cho dạng thấp tin cậy (xem #283).

## ESCO và Lightcast Open Skills (đọc cách làm qua `ojd_daps_skills`, không dùng dữ liệu)

- Tìm repo public giữ riêng bảng bí danh kiểu ESCO/Lightcast kèm danh sách loại trừ viết tay thì không thấy: `skills-ml` và `ojd_daps_skills` ở trên là hai nơi đọc được cách làm. `ojd_daps_skills` đọc cả hai taxonomy (`esco_formatting.py`, `lightcast_formatting.py`) vào cùng một dạng bảng "một dòng mỗi cách viết".
- ESCO có nhãn chính, `altLabels` và nhãn ẩn; ở đây tên Anh, tên Việt và bí danh của `skills_seed.json` đóng vai nhãn chính và `altLabels`, còn `scan_skip` đóng vai nhãn "chỉ để tra".
- Kết luận: không nhập bảng ESCO/Lightcast. Dữ liệu của hai bộ đó chưa được kiểm điều khoản dùng lại trong nhóm, và không có tên tiếng Việt cho "xử lý sự cố", "quản trị hệ thống". Mã vẫn là mã của Hải Đồ; khi bộ từ vựng v1 ([#96](https://github.com/Dyuedu/HaiDoIT/issues/96)) có giảng viên duyệt thì mới đối chiếu với ESCO.

## Điều rút ra cho #278

1. Bảng "khóa chuẩn hóa → mã" phẳng, một khóa chỉ thuộc một mã, trùng thì báo lỗi (khác `skills-ml`, nơi trùng lặng lẽ đè). `load_vocabulary` đã làm vậy; #278 gặp ba lần trùng và xử lý ở [data-model.md](data-model.md).
2. Bí danh do người duyệt, không do mô hình đoán (khác `ojd_daps_skills` ở phần BERT): ánh xạ chạy lại không cần mô hình và không cần mạng.
3. Thẻ không phải kỹ năng có danh sách riêng, mỗi dòng có lý do và số tin bằng chứng. Hai dự án trên không có phần này nên thiết kế là của kho này. Khóa loại trừ không được đồng thời là khóa từ vựng.
4. Chữ chung vẫn tra được nhưng không quét (`scan_skip`), theo ý "dạng thấp tin cậy" của SkillNER.
