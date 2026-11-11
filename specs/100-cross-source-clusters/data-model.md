# Data model: Cụm chéo nguồn

Không thêm bảng. Cụm tính trong bộ nhớ ở bước `aggregate`, rồi ghi vào `cluster_id` mà phép dân số đã đếm.

Cập nhật 2026-11-11 (#163): #100 không đổi bảng. Sau #163, `stat_cells.seniority` chứa thêm mã cấp lọc và `stat_city_shares` có cột `seniority` (migration 0005, xem `specs/163-loc-ban-do-theo-cap-bac/data-model.md`); mỗi cụm vẫn đếm một lần, ở cấp của tin đại diện.

## ClusterMember

| Trường | Ý nghĩa |
|---|---|
| posting_id | Mã tin trong schema `haido`, dạng chuỗi |
| source | Tên sàn |
| url | `source_url` của tin |
| company, title, location_text, experience_level, job_level | Dữ kiện tại snapshot. Rỗng thì không tính là trường có giá trị |

## Cluster

| Trường | Ý nghĩa |
|---|---|
| cluster_id | `k:` + công ty chuẩn hóa + tab + chức danh chuẩn hóa, hoặc `p:` + mã tin khi không có khóa |
| representative_id | Mã tin đại diện |
| member_ids | Mọi mã tin trong cụm, sắp theo mã tin |

## Khóa danh tính

1. Bỏ dấu tiếng Việt, hạ chữ.
2. Dấu câu thành khoảng trắng, gộp khoảng trắng.
3. Công ty: bỏ tiền tố `cong ty` / `cty` / `company`. Bỏ cụm `co phan` và các token pháp lý (`tnhh`, `ctcp`, `inc`, `ltd`, `llc`, `jsc`, `co`, `cp`, …) ở bất kỳ vị trí nào, miễn là còn lại ít nhất một token tên.
4. Khóa tồn tại khi cả công ty lẫn chức danh còn token.

## Đại diện

Sắp tăng dần theo bộ:

1. Vị trí trong `sources.priority`. Nguồn không có trong danh sách nhận hạng bằng độ dài danh sách.
2. Âm của số trường không rỗng trong năm trường thống kê.
3. URL trống đứng sau URL có giá trị. URL có giá trị xếp A–Z theo chuỗi đã cắt khoảng trắng.
4. `posting_id` A–Z.

Phần tử đầu là đại diện.

## MatchDecision

Một cặp. `matched` đúng khi hai tin cùng khóa và phạm vi đúng: `in_source` đòi cùng nguồn, `cross_source` đòi khác nguồn. Thiếu khóa thì không khớp.
