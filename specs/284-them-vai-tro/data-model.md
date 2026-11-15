# Data model: thêm bảy vai trò (#284)

Không đổi bảng, cột hay revision Alembic (head vẫn `0007_haido_classify_at_ingest`).

## `config/rules.toml` (`config_version` `2026-11-13.1` → `2026-11-13.2`)

`roles` (thứ tự hiển thị), mã mới in đậm:

`embedded`, `ai_ml`, **`data_scientist`**, `data_engineer`, `data_analyst`, `qa`, `devops`, **`security`**, **`it_infra`**,
`mobile`, `frontend`, `backend`, **`fullstack`**, **`ba_po_pm`**, **`ui_ux`**, **`game`**, `other`.

`[labels.role]` thêm:

| Nhãn của bộ phân loại | Mã |
|---|---|
| Data Scientist | `data_scientist` |
| Security | `security` |
| Hạ tầng/IT support | `it_infra` |
| Fullstack | `fullstack` |
| BA/PO/PM | `ba_po_pm` |
| UI/UX | `ui_ux` |
| Game | `game` |

## `config/classify.toml`

`[report_as]` rỗng. `classify_version` giữ `classify-2026-11-13.2`: bảng này chỉ đổi cách tổng hợp, không đổi nhãn lưu ở
`job_posting_facts`.

## `stat_cells`, `stat_city_shares`

Không đổi cột. Mỗi snapshot có thêm hàng của bảy mã; hàng `other` chỉ còn tin chức danh chung.

## Bản giả (`haido_api/fixtures/fake_market.json`)

`city_shares.<mã mới>.all`, ô `<phạm vi>.<mã mới>` và `vn.<mã mới>.entry`, dòng `newcomer_roles.rows` cho mỗi mã mới,
theo thứ tự `roles`. Số lấy từ snapshot 12/11 của bản sao local (đếm theo cụm), làm tròn.
