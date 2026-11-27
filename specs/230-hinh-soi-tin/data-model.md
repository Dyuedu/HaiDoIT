# Data Model: Hình response của tin dán ("Soi tin")

**Không đổi bảng, cột hay revision Alembic.** Chữ của tin dán không bao giờ chạm bảng nào (AD-11); `posting_check` giả đọc fixture, bản thật (#234) đọc `stat_skill_rates` và `stat_cells` sẵn có.

## Cấu hình có phiên bản (`config/rules.toml`)

| Khóa | Giá trị | Ghi chú |
|---|---|---|
| `config_version` | `2026-11-19.1` thành `2026-11-27.1`, rồi `2026-11-27.2` (vòng review) | Đổi giá trị trong `rules.toml` thì tăng phiên bản (quy ước của file) |
| `[posting_match] weight_core` | 3 | FR-28 |
| `[posting_match] weight_common` | 2 | FR-28 |
| `[posting_match] weight_specific` | 1 | FR-28 |
| `[posting_read] max_chars` | 20000 | FR-26: chữ dán tối đa 20.000 ký tự (vòng review) |
| `[posting_read] max_body_bytes` | 131072 | AD-9: trần byte của thân `POST posting-reads`, kiểm bằng `Content-Length` rồi đếm lúc đọc. 4 byte × 20.000 ký tự = 80.000 cộng phụ trội của JSON; không quá 1 MiB (vòng review) |
| `[posting_market] ci_below_n` | 100 | FR-30, AD-26: phân vị của tin dán kèm khoảng tin cậy 95% khi `min_sample <= n < ci_below_n`; lớn hơn `min_sample` (vòng review) |

`load_rules` kiểm: `[posting_match]` có đủ ba khóa và không thừa, số nguyên từ 1, không tăng dần từ core đến specific; `[posting_read]` có đúng hai khóa, `max_chars` từ 1, `max_body_bytes` từ `max_chars` đến 1 MiB; `[posting_market]` có đúng khóa `ci_below_n`, số nguyên lớn hơn `min_sample`. `RulesConfig` có `posting_match_weights` (`dict` `{core, common, specific}`), `posting_max_chars`, `posting_max_body_bytes`, `posting_ci_below_n`. `PostingReadRequest.text` có `max_length` bằng `posting_max_chars` (test giữ hai chỗ khớp nhau).

## Fixture

- `haido_api/fixtures/fake_market.json`: thêm ô `vn.backend.junior` (n = 32, `seniority_mix` `{junior: 32}`, `skill_count` 32, `experience_years` 24, `salary` 9) và `skill_rates.backend.junior` (15 kỹ năng, 6 core, 7 common, 2 company_specific, tỷ lệ là số nguyên trên 32).
- `haido_api/fixtures/fake_posting_reads.json` (mới): `model_id`, `prompt_version`, `min_chars`, `it_markers`, `deposit_markers`, hai tin mẫu `backend` và `fee`.
- `web/tests/fixtures/posting-read-*.json` (4) và `posting-check-*.json` (4): sinh từ `TestClient`, được `tests/api/test_ad17_web_fixtures.py` giữ bằng response của API giả.

## Không đổi bảng, cột hay revision Alembic (vòng review 2026-11-27)

Vòng review không thêm bảng, cột hay revision Alembic: lần gọi `POST posting-reads` vẫn không chạm cơ sở dữ liệu. Tin thu thập khớp (`collected`, FR-32) hiện đến từ fixture của bản giả; bản thật (#246) đọc `stat_job_lifecycle` và cụm của #100 sẵn có.

### Đường ghi sẽ có (AD-11), chưa cài đặt ở #230

Các issue sau sẽ thêm đúng **một** đường ghi, và chỉ được ghi những gì AD-11 cho phép, không bao giờ chữ của tin:

| Issue | Ghi gì | Bảng |
|---|---|---|
| FR-29 (`unknown_mentions_pasted`) | từ khóa của cụm chưa nhận diện, tần suất, lần thấy cuối | bảng danh sách chờ FR-6 (sẽ có revision riêng ở issue đó) |
| FR-26 (sự kiện ẩn danh mỗi lần soi) | đúng bốn trường, không kèm nội dung tin | bảng sự kiện ẩn danh (sẽ có revision riêng ở issue đó) |

Đường ghi nằm ở một mô-đun riêng mà route gọi với đúng các trường ấy; `routes/posting.py` và `posting_read.py` vẫn không import cơ sở dữ liệu (test AD-11 giữ nguyên và chỉ đổi khi mô-đun ghi có mặt). #230 chỉ ghi nhận kế hoạch này.

## Fixture (vòng review)

- `haido_api/fixtures/fake_posting_reads.json`: thêm `job_markers`, `devops_markers`; ba tin mẫu `backend`, `fee`, `cloud`; mỗi tin có `branch`, `duties_described`, `title_level`, `salary_non_numeric`, `contact_quotes`, `collected`. `cloud` là tin DevOps nhánh `cloud`, cấp `mid`, lương "thỏa thuận", đã có tin thu thập khớp (link `example.com`).
- `web/tests/fixtures/`: thêm `posting-read-{cloud,not-it}.json`, `posting-check-backend.unknown-fee.json`, `posting-check-ready-{full,sparse}.json`; sinh lại các file cũ (có thêm trường, `config_version` mới) bằng một script dùng `TestClient` và `tests/api/posting_examples.py`.
