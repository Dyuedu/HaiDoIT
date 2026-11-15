# Data model: 34 tỉnh, Remote, Nước ngoài (#285)

## `haido.job_posting_facts` (migration `0008_haido_fact_city`)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| **city** | text, null | **mới**. Nhãn nơi của bộ phân loại (tên tỉnh mới, `Remote`, `Nước ngoài`, `không xác định`). `null` ở hàng cũ |

Hạ cấp bỏ cột. `aggregate` dùng `city` đã lưu khi `classify_version` khớp; không thì phân loại từ `location_text`.

## `stat_cells`, `stat_city_shares`

Không đổi cột. Hàng của một nơi chỉ được ghi khi nơi đó có ít nhất một tin trong (vai trò, cấp, số năm), cộng `always_cities`. Mã `other` không còn được ghi.

## `config/rules.toml` (`config_version` → `2026-11-13.3`)

- `[labels.city]`: 34 tỉnh, thành (nhãn tiếng Việt → mã snake_case không dấu), `"Remote" = "remote"`, `"Nước ngoài" = "abroad"`, `"không xác định" = "unknown"`. Thứ tự là thứ tự trong API: ba thành phố lớn, rồi các tỉnh theo vùng Bắc → Nam, rồi Remote, Nước ngoài, không xác định.
- `always_cities = ["ha_noi", "ho_chi_minh", "da_nang", "remote", "abroad", "unknown"]`.

## `config/classify.toml` (`classify_version` → `classify-2026-11-13.3`)

- `[[cities]]`: 34 dòng, `label` và `phrases` (tên mới, tên tỉnh cũ đã nhập vào, thành phố/khu hay gặp).
- `abroad_phrases` (đọc ở `location` và dòng địa chỉ), `abroad_location_phrases` (chỉ ở `location`: "quốc tế", "international", "nước ngoài"), `remote_phrases`.
- `[address]`: `keys` (biểu thức dòng địa chỉ: địa điểm, địa chỉ, nơi làm việc, work location, office…), `next_lines` (số dòng sau tiêu đề được đọc kèm).
- Bỏ `other_city_phrases`.
