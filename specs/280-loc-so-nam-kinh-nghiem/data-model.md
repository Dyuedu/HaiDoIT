# Data model: số năm kinh nghiệm của bản đồ

## Config (`config/rules.toml`, `config_version` `2026-11-11.1` → `2026-11-12.1`)

| Khóa | Ý nghĩa |
|---|---|
| `years_options` | Mốc "tối đa N năm", số nguyên ≥ 0, tăng dần, không trùng: `[0, 1, 2, 3, 5]`. `any` luôn có thêm và không nằm ở đây |

`haido_core/config.py`: `ANY_YEARS = "any"`, `RulesConfig.years_options: tuple[int, ...]`.

## Bảng `haido.job_posting_facts` (đổi)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| **years_min** | float8, null | **mới**. Chép từ `jobs.years_experience_min` của scraper. `null` = tin không ghi |

`FactVersion` có thêm `years_min`; giá trị đổi so với phiên bản mới nhất thì ingest thêm phiên bản.

## Bảng `haido.stat_cells` (đổi)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| **years** | text, not null | **mới**, khóa. `any` hoặc mã mốc (`0`, `1`, …). Hàng cũ nhận `any` |
| **years_unstated** | integer, not null, không có giá trị mặc định | **mới**. Số cụm của (vai trò, cấp, phạm vi) không ghi số năm; cùng giá trị ở mọi mã số năm của bộ đó. Hàng cũ nhận 0 |

Khóa chính: `(snapshot_id, role, branch, seniority, years, scope)`.

## Bảng `haido.stat_city_shares` (đổi)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| **years** | text, not null | **mới**, khóa. Hàng cũ nhận `any` |

Khóa chính: `(snapshot_id, role, seniority, years, city)`.

## Revision Alembic

`0006_haido_years_filter`, `down_revision = "0005_haido_city_share_level"`.

- `upgrade`: thêm `job_posting_facts.years_min`; thêm `years` (`server_default 'any'`) vào hai bảng stat và đổi khóa chính; thêm `stat_cells.years_unstated` (`server_default 0`); bỏ `server_default` của cả hai để bước ghi buộc phải nêu.
- `downgrade`: xóa hàng `years <> 'any'`, trả khóa chính cũ, bỏ các cột mới.

Một head: `0006_haido_years_filter`.

## Mã ô trong envelope

| Cấp | Số năm | `cell_id` |
|---|---|---|
| `all` | `any` | `<scope>.<role>` |
| `L` | `any` | `<scope>.<role>.<L>` |
| `all` | `N` | `<scope>.<role>.y<N>` |
| `L` | `N` | `<scope>.<role>.<L>.y<N>` |
| `all` / `L` | `N` | `vn.<role>[.<L>].ynone`: ô các tin không ghi số năm, chỉ có `n` |

## API (`CitySharesData`)

- `years: str` — mã số năm đã dùng (`any` khi không gửi).
- `years_unstated_cell_id: CellId | null` — ô `vn.<role>[.<level>].ynone`; `meta.cells[...].n` là số cụm toàn quốc của (vai trò, cấp) không ghi số năm; `null` khi `years = any`.

Đổi so với bản đầu: bản đầu để `years_unstated: int` thẳng trong `data`, nhưng `Envelope` (AD-17) từ chối mọi số đứng trần ngoài `Stat` trong `data`. Số đếm nằm ở `meta.cells[...].n` như mọi số đếm khác, giống `total_cell_id`.
