# Data model: phân loại tin ở bước ingest (#283)

## Bảng `haido.job_posting_facts` (đổi, migration `0007_haido_classify_at_ingest`)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| **role** | text, null | **mới**. Nhãn vai trò của bộ phân loại (như `Backend`, `BA/PO/PM`, `không thuộc IT`). `null` ở hàng cũ |
| **branch** | text, null | **mới**. Chức danh con trong vai trò (như `Product Owner`, `Network`). `null` khi không khớp hoặc hàng cũ |
| **seniority** | text, null | **mới**. Nhãn cấp (`Intern` … `Lead`, `không xác định`) |
| **skills** | jsonb, null | **mới**. Object mã kỹ năng → số lượt nhắc trong các mục yêu cầu và nhiệm vụ, ví dụ `{"python": 2, "docker": 1}`. Chỉ mã, không có chuỗi nguyên văn |
| **classify_version** | text, null | **mới**. `classify_version` của `config/classify.toml` đã dùng. `null` ở hàng cũ |
| years_min | float8, null | Có từ #280. **Đổi nghĩa**: số năm đã giải theo thứ tự số tháng của nguồn → giá trị bước trích → luật đọc mục yêu cầu; "không yêu cầu kinh nghiệm" cho 0 |

Không có cột văn bản JD, mô tả hay chuỗi kỹ năng nguyên văn (DoD dòng 9). `FactVersion` có thêm năm trường mới; đổi nhãn hoặc phiên bản luật thì ingest thêm phiên bản dữ kiện.

`city` không thêm cột ở #283: thành phố vẫn phân loại từ `location_text` lúc `aggregate`. #285 đổi phần này.

Hạ cấp (`downgrade`) bỏ năm cột. Hàng không mất, chỉ mất nhãn; `aggregate` quay về phân loại từ trường đóng.

## Bảng `stat_*`

Không đổi cột. Số trong `stat_cells` và `stat_city_shares` đổi theo nhãn mới; `config_version` của snapshot ghi phiên bản đã dùng.

## Config

### `config/classify.toml` (mới)

| Khóa | Ý nghĩa |
|---|---|
| `classify_version` | Phiên bản luật, ghi vào từng dữ kiện (`classify-2026-11-13.2`) |
| `generic_it_titles` | Chức danh lãnh đạo/kiến trúc IT (CTO, Solution Architect, Engineering Manager…): luôn là Other, không xét bằng chứng kỹ năng |
| `it_only_sources` | Nguồn chỉ đăng tin IT: `itviec`, `itnavi`. `topdev` bị bỏ (đăng cả tin ngân hàng, xây dựng; 123/629 tin là IT) |
| `non_it_categories` | Danh mục nguồn của việc không thuộc IT (giữ từ luật v1) |
| `[report_as]` | Nhãn mới → nhãn cũ lúc tổng hợp, tới #284. Rỗng từ #284 (mỗi nhãn có mã riêng) |
| `[[roles]]` | Mỗi vai trò: `label`, `phrases` (cụm trong chức danh), thứ tự là thứ tự ưu tiên khi hòa vị trí. Vai trò chung (`Other`) đứng cuối và chỉ dùng khi không vai trò cụ thể nào khớp |
| `non_it_phrases`, `art_phrases` | Cụm chức danh của việc không thuộc IT; cụm nghệ sĩ/đồ họa |
| `[[branches]]` | Chức danh con: `role`, `label`, `phrases` |
| `[skill_hints]` | Mã kỹ năng → vai trò gợi ý; `[category_weights]` trọng số theo nhóm mã |
| `evidence` | Ngưỡng: số kỹ năng kỹ thuật tối thiểu để tin không có cụm vai trò vẫn là IT (4), điểm tối thiểu và tỷ lệ thắng của vai trò theo bằng chứng (4; 1,3), ngưỡng Fullstack |
| `[[levels]]` | Cấp: `label`, `phrases` cho chức danh và chữ cấp của nguồn; `ignore_source_levels` (`Experienced (non-manager)`, `Tất cả cấp bậc`) |
| `[[years_to_level]]` | Bảng #134: `< 1` Fresher, `< 2` Junior, `< 5` Mid, còn lại Senior |
| `sections` | Tiêu đề mục giữ (yêu cầu, nhiệm vụ…) và bỏ (quyền lợi, giới thiệu công ty, địa điểm…) |
| `max_text_chars` | 50000 |

### `config/rules.toml`

- `config_version` `2026-11-12.1` → `2026-11-13.1`.
- `[labels.role]` không đổi (luật "mỗi mã một nhãn" của AD-10 giữ nguyên). Nhãn mới về mã cũ qua `[report_as]` của `classify.toml`: Data Scientist → AI/ML Engineer (`ai_ml`), sáu nhãn còn lại → Other (`other`).

### `haido_core/vocab/skills_seed.json`

- `version` `seed-2026-11-11` → `seed-2026-11-13` (giữ tiền tố `seed-` mà `skills.py` kiểm).
- Giữ 100 mã cũ (hồ sơ người dùng dùng các mã này), thêm bí danh tiếng Việt và cách viết khác; thêm 125 mã mới (tổng 225). Khóa mới `composites` (`c/c++` → `c`, `c++`) và `scan_skip` (từ không quét khi đứng riêng: `c`, `r`, `go`, `ai`, `bi`, `sap`…). Bí danh mơ hồ khi bỏ dấu (`sap` = "sắp", `lan` = "lần", `san` = "sàn", `pic`, `soc`, `solid`, `less`, `word`) không có trong danh sách.
