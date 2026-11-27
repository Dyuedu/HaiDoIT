# TDD: Hình response của tin dán ("Soi tin") và dữ liệu giả

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test viết trước, chạy cho thấy đỏ, rồi mới viết code. Thư mục `specs/230-hinh-soi-tin/` được viết trước code; riêng `tdd.md` này ghi kết quả sau mỗi lần chạy thật.

Ngày: 2026-11-27. Môi trường: Git Bash, `PYTHONUTF8=1`, Postgres test ở cổng 5433 (`HAIDO_TEST_DATABASE_URL`).

## Lệnh

```text
uv run pytest tests/api/test_fr28_posting_check.py tests/api/test_fr26_posting_read.py tests/api/test_ad22_posting_check_query.py tests/api/test_ad11_posting_read.py tests/deploy/test_gh230_posting_nguon_prod.py tests/core/test_ad10_rules_config.py tests/api/test_ad17_routes.py tests/api/test_ad17_ordinal_allowlist.py tests/api/test_ad17_web_fixtures.py -q
cd web && npx vitest run tests/fr28-posting-fixture.test.ts
uv run pytest -q          # toàn bộ, cần Postgres test
uv run ruff check .
uv run python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24
cd web && npx vitest run && npx tsc --noEmit && npx eslint .
```

Sinh lại `docs/api/openapi.json` bằng `HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api/test_ad17_routes.py -q`; sinh tám fixture web bằng `TestClient(app)` (`json.dumps(..., ensure_ascii=False, indent=2)` cộng dòng trống cuối).

## Các hành vi

Python:

1. (`test_fr28_posting_check.py`) Ví dụ FR-28: hồ sơ có 6 kỹ năng đầu của tin Backend Junior thì `match.level` là 16 trên 18 và 89; đếm thô `4/4, 2/2, 0/2`; trọng số lấy từ `config/rules.toml`, `build_match` dùng trọng số truyền vào; `match_percent` làm tròn nửa lên (16/18 là 89, 5/8 là 63).
2. Nhóm của từng kỹ năng, thứ tự do máy chủ, kỹ năng không có dòng trong ô là `specific` với tỷ lệ 0, kỹ năng ngoài tin không đổi mức khớp, `cv_first`, cờ `have` từng kỹ năng.
3. Không hồ sơ: `has_profile = false`, `level = null`, `have = null`, `groups[].had = null`, `cv_first = []`, nhóm và tỷ lệ vẫn có.
4. Ô dưới 30 quay về ô rộng có `fallback_label`; không ô nào đủ mẫu thì `not_enough_data` (không nhóm, tỷ lệ `null_data`, `cv_first` vẫn có); tin không kỹ năng thì `no_skills`; vai trò lạ thì 404 `unknown_cell`.
5. `market` và `warnings` là `not_ready` và rỗng; hình `ready` đã khai hợp lệ, và từng kiểu sai bị schema từ chối (not_ready mà có dữ liệu, ready thiếu mục, `compared` mà ẩn số, `not_stated` mà có số, thiếu một mục của checklist, dấu hiệu lạ).
6. (`test_fr26_posting_read.py`) `POST /api/v1/posting-reads`: tin Backend Junior có đủ sự kiện đóng và không có `meta`; mã vai trò, cấp và kỹ năng nằm trong bộ mã; tin có phí; không phải tin; quá ngắn; thứ tự chọn của nguồn giả (ngắn, rồi dấu IT, rồi `đặt cọc`, rồi backend); ranh giới 199 và 200 ký tự; tất định; 15 kiểu `data` sai bị schema từ chối; thân sai hình là 422 không lặp lại chữ; mã lỗi đã khai trong OpenAPI; nguồn `model` trả 503; chọn nguồn bằng biến môi trường; lỗi của nguồn thành hình lỗi chuẩn.
7. (`test_ad22_posting_check_query.py`) Query chỉ mã và số: tham số lạ (kể cả `text`) và kỹ năng ngoài bộ từ vựng là 422 không lặp lại giá trị; mọi cụm chưa nhận diện của bước một bị bước hai từ chối; trần 200 mã đếm trước khi loại trùng; `have` dùng chung bộ đọc; 16 kiểu sự kiện sai định dạng; `role` và `level` bắt buộc; danh sách tham số của OpenAPI.
8. (`test_ad11_posting_read.py`) Nguồn giả không giữ trạng thái; kết quả không chứa chữ dán; route không ghi log cả khi thân sai hình hoặc nguồn lỗi; `POST` không vào cache response; không ghi file khi đọc; mã của `posting_read.py` và `routes/posting.py` không có dấu vết lưu trữ hay log.
9. (`test_gh230_posting_nguon_prod.py`) `compose.prod.yml` đặt `posting_check: stat` và `HAIDO_POSTING_READER: model`; prod dựng nguồn thật cho cả hai bước và không trả dữ liệu giả (503 và 404); compose.local giữ nguồn giả.
10. (`test_ad10_rules_config.py`) `rules.toml` có trọng số 3/2/1 và `config_version` mới; trọng số đổi theo file; bảy kiểu cấu hình sai bị từ chối.
11. (`test_ad17_routes.py`, `test_ad17_ordinal_allowlist.py`, `test_ad17_web_fixtures.py`) Route mới nằm trong `SAMPLE_QUERY` và danh sách kiểm `display`; route nhận chữ người dùng chỉ có `data` và số chỉ ở các trường cho phép; sáu trường `Ordinal` mới được khóa; tám fixture web bằng response của API giả; OpenAPI khớp code.

Web (`web/tests/fr28-posting-fixture.test.ts`): 12. kiểu và bộ kiểm hợp đồng của cả hai bước; URL bước hai chỉ có mã và số, không có chữ chưa nhận diện hay trích dẫn phí; đổi vai trò hoặc cấp dùng lại cùng tin; không phải tin thì không có URL; fixture `16/18 = 89%`, không hồ sơ, quay về ô rộng, `not_enough_data`; `market` và `warnings` `not_ready`; gọi API (POST chỉ `{text}`, lỗi chuẩn và `retryable`, body sai là `unreadable`, không gọi mạng khi không có URL).

## RED (2026-11-27, trước khi viết code)

Chạy các file của mục 1 đến 11 và web khi chưa có `haido_api/posting_*.py`, `schemas/posting.py`, `routes/posting.py`, `web/lib/posting.ts`, `[posting_match]`:

- Python: **56 failed, 4 lỗi thu thập, 226 passed** (226 là các test cũ của chín file). Bốn file không thu thập được vì thiếu module (`haido_api.posting_match`, `haido_api.posting_read`): `test_fr28_posting_check.py`, `test_fr26_posting_read.py`, `test_ad11_posting_read.py`, `test_gh230_posting_nguon_prod.py`. 56 đỏ: 33 ở `test_ad22_posting_check_query.py` (route chưa có nên 404 thay vì 200 hay 422), 9 ở `test_ad10_rules_config.py` (chưa có `posting_match_weights`), 8 ở `test_ad17_web_fixtures.py` (chưa có route hay fixture), 5 ở `test_ad17_routes.py` (route chưa có trong OpenAPI, `SAMPLE_QUERY` và danh sách yêu cầu), 1 ở `test_ad17_ordinal_allowlist.py` (khóa Ordinal thiếu sáu trường).
- Web: `fr28-posting-fixture.test.ts` không nạp được (`@/lib/posting` chưa có): 0 test chạy, 1 file đỏ.

## GREEN (từng bước)

- Sau `[posting_match]` và `posting_match_weights`: `uv run pytest tests/core -q` được 221 passed (chín test mới của mục 10 xanh).
- Sau schema, `posting_match`, `posting_read`, route và nguồn: năm file mới cộng `tests/deploy`, `test_ad10`, `test_ad17_routes`, `test_ad17_ordinal_allowlist` được 98 passed, 1 failed (thiếu `HAIDO_MARKET_SOURCE_POSTING_CHECK` ở `compose.prod.yml`); sau khi thêm: 423 passed, 2 failed (`test_gh342_do_tai_baseline` cần khóa này ở `compose.loadtest.yml`, và OpenAPI chưa sinh lại). Thêm khóa, sinh lại OpenAPI bằng `HAIDO_UPDATE_OPENAPI=1`: 101 passed ở `test_ad17_routes.py`.
- Web: sau `web/lib/posting.ts` và tám fixture, lần đầu 19 passed 1 failed (regex URL thiếu chữ hoa `%2C`, sửa test), `tsc` báo `min`/`max` có thể `undefined` (sửa kiểu); rồi 20 passed.
- Toàn bộ `uv run pytest -q` lần 1: 4 failed, 2025 passed (635 giây). Hai nguồn lỗi thật chưa thấy ở các lượt trước: `test_ad17_meta_nguon_stat.py` (3, `create_app` thiếu `posting_check` và danh sách "route đọc `stat`" chưa biết `posting-check` chưa có số thật) và `test_gh309_ban_nhap_chi_chay_bang_compose_demo` (1, `compose.demo.yml` thiếu khóa mới). Sửa `compose.demo.yml` (`HAIDO_MARKET_SOURCE_POSTING_CHECK: stat`, `HAIDO_POSTING_READER: model`) và `test_ad17_meta_nguon_stat.py` (thêm nguồn, thêm `PENDING = {posting-check}`: có snapshot rồi vẫn 404): 130 passed ở `test_ad17_meta_nguon_stat.py`, `test_fr22_learning_path_draft.py` và `tests/deploy`.
- Test `tests/deploy/test_gh230_posting_nguon_prod.py` ban đầu import `posting_samples` của `tests/api`, chạy riêng thì lỗi thu thập; đã bỏ import (5 passed khi chạy riêng).
- Cuối cùng: xem mục "Kết quả cuối" bên dưới.

## RED của các test cũ khi `SOURCE_ENV` có khóa mới

Trả 13 file test cũ về bản ở HEAD (chúng dựng `create_app({...})` với năm nguồn) rồi chạy với code mới: **109 failed, 54 lỗi, 32 passed** (thông báo `Thiếu nguồn cho phép: posting_check`). Thêm `"posting_check"` vào các lời gọi (và đổi danh sách của `test_ad17_meta_nguon_stat.py`) cho xanh lại; các file là `test_ad22_market_overview_stat`, `test_dat20_stat_market`, `test_fr09_skill_roles_stat`, `test_fr19_skill_rates_stat`, `test_fr22_learning_path_draft`, `test_fr22_learning_path_stat`, `test_fr33_city_shares_level`, `test_fr33_city_shares_years`, `test_fr37_newcomer_roles_stat`, `test_gh102_stat_market_theta`, `tests/steps/test_dat20_api_end_to_end`, `tests/steps/test_gh284_aggregate_vai_tro_moi`, `test_ad17_meta_nguon_stat`.

## Đột biến (mutation), mỗi lần khôi phục đúng byte

Mỗi đột biến sửa một chỗ rồi chạy tám file test (`-x`); cả 15 bị bắt:

| # | Đột biến | Test bắt đầu tiên |
|---|---|---|
| M1 | Bỏ trọng số (`points += had`) | `test_fr28_vi_du_16_tren_18_la_89_phan_tram` |
| M2 | Làm tròn xuống thay vì nửa lên | `test_fr28_vi_du_16_tren_18_la_89_phan_tram` |
| M3 | `company_specific` gộp vào `common` | `test_fr28_vi_du_16_tren_18_la_89_phan_tram` |
| M4 | Kỹ năng không có dòng thành `common` | `test_fr29_ky_nang_hiem_trong_o_la_specific_ke_ca_khi_khong_co_dong` |
| M5 | Cờ `have` luôn là bool kể cả không hồ sơ | `test_fr29_nhom_cua_tung_ky_nang_va_thu_tu_do_may_chu` |
| M6 | Không chặn tham số lạ | `test_ad22_tham_so_la_bi_tu_choi_ke_ca_chu_tu_do[text]` |
| M7 | Kỹ năng ngoài bộ từ vựng lọt qua | `test_ad22_ky_nang_phai_nam_trong_bo_tu_vung` |
| M8 | Mốc `too_short` lệch một ký tự (`<=`) | `test_fr26_dung_200_ky_tu_thi_khong_con_ngan` |
| M9 | Nguồn `model` thành nguồn giả | `test_ad9_chon_nguon_bang_bien_moi_truong` |
| M10 | `compose.prod.yml` đặt `HAIDO_POSTING_READER: fake` | `test_gh230_prod_dat_nguon_doc_chu_dan_la_model_khong_phai_gia` |
| M11 | `StatMarket.posting_check` trả dữ liệu giả | `test_gh230_prod_khong_tra_du_lieu_gia_o_ca_hai_buoc` |
| M12 | `cv_first` lấy kỹ năng thiếu | `test_fr28_hinh_envelope_va_ba_muc` |
| M13 | Route ghi log chữ dán | `test_ad11_route_khong_ghi_log_chu_dan[fake]` |
| M14 | Đọc sai trọng số `specific` từ cấu hình | `test_fr28_vi_du_16_tren_18_la_89_phan_tram` |
| M15 | `warnings` `not_ready` không cần rỗng | `test_fr31_warnings_ready_hop_le_va_not_ready_phai_rong` |

## Kết quả cuối

Chạy sau khi mọi thay đổi code, test, fixture và tài liệu đã xong (2026-11-27):

| Lệnh | Kết quả |
|---|---|
| `uv run pytest -q` (toàn bộ, Postgres test thật) | **2029 passed**, 625,89 giây |
| `uv run ruff check .` | All checks passed |
| `uv run python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` | 10 gates: 10 pass, 0 skipped, 0 failed |
| `npx vitest run` (web) | 35 file, **462 passed** (20 test mới ở `fr28-posting-fixture.test.ts`) |
| `npx tsc --noEmit` (web) | không lỗi |
| `npx eslint .` (web) | không lỗi |

Số test mới của #230: `test_fr28_posting_check.py` 27, `test_fr26_posting_read.py` 29, `test_ad22_posting_check_query.py` 34, `test_ad11_posting_read.py` 8, `test_gh230_posting_nguon_prod.py` 5, `test_ad10_rules_config.py` thêm 9, `test_ad17_web_fixtures.py` thêm 8, web 20; cộng các dòng mới trong `test_ad17_routes.py` (5 yêu cầu fixture) và `test_ad17_ordinal_allowlist.py`.


## Đợt review (2026-11-27)

**Vì sao sửa**: review của #230 đòi hợp đồng đã chốt phải mang được #231–#247 chỉ bằng cách thêm giá trị: thiếu `not_it`, nhánh, sự kiện của danh sách (#244), trích dẫn liên hệ (#245), tin thu thập khớp có link (FR-32), cắt kết quả quá cỡ, trần lương không khớp giữa hai bước, hình `ready` của `market` (FR-30: khoảng tin cậy, quy đổi lương theo tỷ giá, mẫu số theo ô của `market`) và `warnings` (FR-31: D1 đến D7), prod trả 404 `unknown_cell` lẫn với "không có số", web trắng khi `ready`, tin có phí 404 ở bước hai, route đã sống mà chưa có trần cỡ thân, lỗi của nguồn đọc thoát lên ASGI, cùng các điểm nhỏ ở test và tài liệu. Không đổi bảng hay migration; không AC nào của #230 đúng khác đi (các AC của #124 đến #126 mà hình phải mang được còn rộng hơn, xem `spec.md` scenario 12 đến 20).

**Lệnh**

```text
uv run pytest tests/api/test_fr28_posting_check.py tests/api/test_fr26_posting_read.py tests/api/test_ad22_posting_check_query.py tests/api/test_ad11_posting_read.py tests/api/test_gh230_posting_read_caps.py tests/api/test_fr30_fr31_posting_ready_shapes.py tests/deploy/test_gh230_posting_nguon_prod.py tests/core/test_ad10_rules_config.py tests/api/test_ad17_routes.py tests/api/test_ad17_ordinal_allowlist.py tests/api/test_ad17_web_fixtures.py tests/api/test_ad17_meta_nguon_stat.py -q --continue-on-collection-errors
cd web && npx vitest run tests/fr28-posting-fixture.test.ts tests/fr30-fr31-posting-ready.test.ts
uv run pytest -q ; uv run ruff check . ; uv run python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24
cd web && npx vitest run ; npx tsc --noEmit ; npx eslint .
HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api/test_ad17_routes.py -q     # sinh lại docs/api/openapi.json
```

**Các hành vi** (số trong ngoặc là mục của review):

1. (1) Bước một có `reason = not_it`; bản giả chọn tất định: ngắn → `too_short`; không dấu IT mà có dấu tin tuyển dụng (`job_markers`) → `not_it`; không có cả hai → `not_posting` (`test_fr26_*not_it*`, schema từ chối mọi trường còn lại khi không phải tin).
2. (2) `branch` ở bước một (mã snake_case của nhãn trong `classify.toml`, phải thuộc `role`); bước hai nhận `branch` kiểm với cấu hình (nhánh không thuộc vai trò → 422) và lặp lại ở `data.branch`.
3. (3) `duties_described`, `title_level` (đóng, không gồm `unknown`) và `salary_non_numeric` ở bước một; bước hai nhận ba tham số tương ứng.
4. (4) `contact_quotes` (5 × 120, kênh nằm trong `contacts`) cạnh enum `contacts`; chỉ hiện từ response bước một, không có trong tham số của bước hai (OpenAPI giữ).
5. (5) `collected` ở bước một (`url` bắt buộc); bước hai nhận `collected_reposts` và `collected_snapshots` đi cặp; route chuyển đủ sự kiện cho nguồn (`test_ad22_moi_su_kien_toi_duoc_nguon_nhu_da_gui`).
6. (6) Kết quả quá cỡ bị cắt trước khi dựng model (`truncate_read`); `years_min` quá 60 thành `null`; lỗi còn lại là 502 `read_failed`, không 500, không chữ của tin.
7. (7) `MAX_SALARY` là một trần chung của `PostingSalary` và `salary_min`, `salary_max`.
8. (8) `market` `ready`: `cell_id` riêng; `years` và `skill_count` mang `state`, `percentile`, `ci_low`, `ci_high` (chỉ khi 30 ≤ n < 100, `Envelope` kiểm với `meta`); `salary` mang `state` (`compared|not_enough_data|not_stated|not_numeric`), `converted` kèm `fx` (tỷ giá và đơn vị), `note` trung tính; trạng thái `not_comparable` đã bỏ; X/30 theo ô của `market` và thước của chính trường.
9. (9) `warnings` `ready`: đủ bảy dấu hiệu D1 đến D7 với `status`, `reason` (D4 `not_in_data`), `fact` có kiểu (D1 mang P90; D3 mang P75 và P25), `action`, `source_field` nullable; `disclaimer`, `salary_note`, `collected_match`; checklist bốn mục.
10. (10) Prod trả chính xác 503 `check_unavailable` (khai trong OpenAPI, web thử lại được), khác 404 `unknown_cell`.
11. (11) Web nhận và kiểm hình `ready` (hai ví dụ viết tay), từ chối kiểu sai; không trắng khi API nối số thật.
12. (12) Tin có phí (cấp `unknown`) và mọi cấp không có ô quay về ô mọi cấp của vai trò ở bản giả; chuỗi hai bước (POST → dựng query → GET) 200 cho mọi tin `is_posting`; fixture `posting-check-backend.unknown-fee.json`.
13. (13) Trần cỡ thân: `Content-Length`, đếm byte lúc đọc, `max_length` 20.000 ký tự, 413 `text_too_long` nêu giới hạn, nguồn không được gọi.
14. (14) Route bắt mọi lỗi của nguồn đọc, chỉ ghi tên kiểu, 502; sentinel không ở response, `caplog`, hay bản ghi nào của root, `uvicorn`, `uvicorn.error`, kể cả `exc_info`; không ném lại lên ASGI (`TestClient` mặc định không bắt được ngoại lệ nào); câu lỗi luôn là câu chuẩn của mã.
15. (15) Đường ghi AD-11 sẽ có được ghi ở `spec.md` và `data-model.md`; test cấm chạm DB và đĩa ở route và nguồn đọc được giữ (chọn giữ, không nới).
16. (16, 20) `have` mã lạ bị bỏ qua như `skill-rates`; hai nit của test.
17. (17, 18) Demo và loadtest cùng `model` và `stat` như prod; mặc định `fake` khi không đặt biến, đã ghi chú.
18. (19) Bộ kiểm của `PostingReadData` không đọc lại TOML mỗi lần.
19. (21, 22) Ghi chú cho #149 và #212; OpenAPI và `envelope-meta.md` sinh lại và cập nhật.

**RED (chạy thật, trước khi viết code)**

- Python (mười hai file trên, `--continue-on-collection-errors`): **48 failed, 317 passed, 4 lỗi thu thập**. Bốn file không nạp được vì thiếu tên mới (`MAX_SALARY`, `truncate_read`, hình `ready`, `CheckUnavailable`): `test_ad22_posting_check_query.py`, `test_gh230_posting_read_caps.py`, `test_fr30_fr31_posting_ready_shapes.py`, `test_gh230_posting_nguon_prod.py`. 48 đỏ: 18 ở `test_ad10_rules_config.py` (chưa có `[posting_read]`, `[posting_market]`), 11 ở `test_ad11_posting_read.py` (lỗi của nguồn đọc thoát ra thành 500 và ghi log), 10 ở `test_fr26_posting_read.py` (chưa có `not_it`, `branch`, trường mới), 5 ở `test_ad17_web_fixtures.py` (chưa có fixture mới), 2 ở `test_fr28_posting_check.py` (hình `not_ready` mới), 1 ở `test_ad17_ordinal_allowlist.py`, 1 ở `test_ad17_meta_nguon_stat.py` (503).
- Web: hai file test không nạp được (thiếu fixture `posting-check-ready-*.json`, `posting-read-cloud.json`...): 0 test chạy.
- Một số test viết sau lượt RED đầu, khi code đã có (header khai gian, đếm byte với khoảng trắng, spy sự kiện, bộ kiểm không đọc lại TOML, mã nhánh): không có RED; được kiểm bằng đột biến M13a, M13b, M5c, M19a, M19b. Các hành vi có từ trước (`have` mã lạ, demo và loadtest `model`) cũng chỉ kiểm bằng đột biến và đọc kết quả xanh.

**GREEN**: sau từng bước (cấu hình, schema, nguồn đọc, route, fixture, sinh lại OpenAPI, web) chạy lại hai bộ trên; cuối cùng 535 passed ở bộ Python mục tiêu, 65 passed ở hai file web. Các lỗi gặp giữa chừng: `meta_nguon_stat` còn đòi 404 (đổi thành 503), logger bị đếm ba lần trong test AD-11 (khử trùng bản ghi), một test web dùng nhầm ví dụ `full` cho `not_stated`.

**Đột biến** (sửa một chỗ, chạy mười hai file, khôi phục đúng byte, so sha256): cả 23 bị bắt. Hai đột biến sống lần đầu rồi được siết test: M13b (đếm byte lúc đọc: test chunked ban đầu vẫn qua nhờ `max_length`, nay dùng JSON hợp lệ cộng khoảng trắng) và M5c (không test nào kiểm route chuyển đủ sự kiện, thêm test spy).

| # | Mục | Đột biến | Test đỏ đầu tiên |
|---|---|---|---|
| M1a | 1 | bản giả không bao giờ chọn not_it | `test_fr26_khong_thuoc_it_co_dau_tin_tuyen_dung_la_not_it` |
| M1b | 1 | schema bỏ mã not_it | `test_fr26_khong_thuoc_it_co_dau_tin_tuyen_dung_la_not_it` |
| M5a | 5 | tin thu thập khớp không bắt buộc có link (FR-32) | `test_fr26_data_sai_la_loi[patch24]` |
| M5b | 5 | bước hai nhận một trong hai số của tin khớp | `test_ad22_su_kien_sai_dinh_dang_la_422[bad26]` |
| M5c | 5 | route bỏ hai số của tin khớp | `test_ad22_moi_su_kien_toi_duoc_nguon_nhu_da_gui` |
| M6a | 6 | cổng đọc không cắt kết quả quá cỡ | `test_ad11_ket_qua_qua_co_bi_cat_thay_vi_sap` |
| M6b | 6 | route không bắt lỗi của nguồn đọc (ValidationError thành 500) | `test_ad11_nguon_loi_bat_ngo_khong_ghi_chu_dan_va_route_tu_xu_ly_502[runtime]` |
| M9a | 9 | ready không đòi câu ghi chú cố định | `test_fr31_warnings_sai_hinh_bi_tu_choi[ready` |
| M9b | 9 | không có tin khớp mà D4 vẫn đánh giá được | `test_fr31_warnings_sai_hinh_bi_tu_choi[D4` |
| M9c | 9 | not_evaluable với lý do bất kỳ | `test_fr31_warnings_sai_hinh_bi_tu_choi[not_evaluable` |
| M9d | 9 | dấu hiệu bất kỳ có source_field bất kỳ | `test_fr31_warnings_sai_hinh_bi_tu_choi[D1` |
| M9e | 9 | khoảng tin cậy không kiểm theo n | `test_fr30_market_sai_hinh_bi_tu_choi[n` |
| M9f | 9 | state compared không kiểm theo n của ô market | `test_fr30_market_sai_hinh_bi_tu_choi[n` |
| M10 | 10 | stat trả 404 unknown_cell như "không có số" | `test_gh230_prod_khong_tra_du_lieu_gia_o_ca_hai_buoc` |
| M12 | 12 | bản giả không quay về ô mọi cấp (tin có phí 404 ở bước hai) | `test_ad22_moi_tin_doc_duoc_o_buoc_1_deu_qua_buoc_2_tra_200[fee]` |
| M13a | 13 | không kiểm Content-Length | `test_ad9_content_length_khai_qua_lon_bi_chan_ngay_du_than_that_nho` |
| M13b | 13 | không đếm byte lúc đọc | `test_ad9_than_khong_co_content_length_bi_chan_khi_dem_byte` |
| M13c | 13 | text không có max_length | `test_ad9_text_khai_max_length_20000_trong_schema_va_openapi` |
| M19a | 19 | bộ kiểm đọc lại rules.toml | `test_fr26_bo_kiem_khong_doc_lai_rules_toml_moi_lan_kiem` |
| M19b | 19 | đọc lại classify.toml mỗi lần | `test_fr26_bo_kiem_khong_doc_lai_rules_toml_moi_lan_kiem` |
| M14a | 14 | ghi thông điệp của lỗi vào log | `test_ad11_nguon_loi_bat_ngo_khong_ghi_chu_dan_va_route_tu_xu_ly_502[runtime]` |
| M14b | 14 | response dùng thông điệp của nguồn đọc | `test_ad9_nguon_do_loi_cua_rieng_no_thanh_hinh_loi_chuan` |
| M14c | 14 | lỗi bất ngờ thoát lên ASGI | `test_ad11_nguon_loi_bat_ngo_khong_ghi_chu_dan_va_route_tu_xu_ly_502[runtime]` |

**Kết quả cuối** (2026-11-27, sau mọi thay đổi):

| Lệnh | Kết quả |
|---|---|
| `uv run pytest -q` (toàn bộ, Postgres test thật) | **2215 passed**, 598 giây |
| `uv run ruff check .` | All checks passed |
| `uv run python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` | 10 gates: 10 pass, 0 failed |
| `npx vitest run` (web) | 36 file, **507 passed** |
| `npx tsc --noEmit` (web) | không lỗi (đã revert `web/tsconfig.tsbuildinfo`) |
| `npx eslint .` (web) | không lỗi |


## Đợt rà lại (2026-11-27)

**Vì sao sửa**: sáu lỗ hổng của hợp đồng còn sót sau đợt review: D2 không có lý do `not_evaluable`, `skills` của bước một không có trần như bước hai, `market` thiếu câu "so sánh, không phải phán quyết" (#125 AC5, #242), checklist không biểu diễn được "không biết", khóa lạ trong thân 422 bị lặp lại trong thông điệp, và bộ kiểm D7 của web không tương thích tiến.

**Lệnh**

```text
uv run pytest -q tests/api/test_fr30_fr31_posting_ready_shapes.py tests/api/test_gh230_posting_read_caps.py
cd web && npx vitest run tests/fr30-fr31-posting-ready.test.ts
HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api/test_ad17_routes.py -q     # sinh lại docs/api/openapi.json
```

**Các hành vi**:

1. D2 `not_evaluable` với `not_enough_data` hợp lệ; lý do khác (`not_in_data`) bị từ chối; D5, D6, D7 vẫn không có `not_evaluable` (Python và web).
2. `PostingReadData.skills` tối đa 200; `truncate_read` cắt giữ thứ tự (hàm thuần); chuỗi hai bước với 240 kỹ năng cho query `skills` đúng 200 và bước hai trả 200.
3. `market.note = comparisons_not_verdict` bắt buộc khi `ready`, `null` khi `not_ready` (cả hai chiều bị kiểm); ví dụ và fixture `ready` mang mã này, fixture `not_ready` mang `note: null`.
4. `checklist[].present` nhận `null` (không biết), khứ hồi đúng; chữ như "có" vẫn bị từ chối.
5. 422 với khóa lạ trong thân `{"text": <hợp lệ>, "<SENTINEL>": 1}` không chứa SENTINEL, nói chung "có trường không có trong hợp đồng".
6. Web nhận D7 `triggered` có thêm trường lạ; `kind` sai vẫn bị từ chối.

**RED** (chạy thật, trước khi sửa code): Python **8 fail** (`market` not_ready thiếu `note`; hai ví dụ `ready` thiếu `note`; D2 `not_enough_data` bị từ chối; `present = null` bị từ chối; hai test trần 200 kỹ năng, vì model chưa có trần và `truncate_read` chưa cắt; 422 còn lặp lại tên khóa lạ), 106 pass. Web **6 fail** (hai ca `note` thiếu hoặc chữ tự do được nhận, D2 `not_enough_data`, `note` của `not_ready`, `present = null`, D7 trường lạ), 39 pass.

**GREEN**: cùng hai lệnh: Python 99 + 15 pass ở hai file đích; web 45 pass. Các test cũ phải đổi theo hình mới: `test_fr28_market_va_warnings_chua_xong_la_not_ready` và `fr28-posting-fixture.test.ts` (thêm `note: null`), `test_fr30_market_not_ready_la_null_het_ke_ca_cell_id`, hai ca BAD của D2 và `present` được viết lại cho đúng ý mới.

**Đột biến** (mỗi lần khôi phục đúng byte, so byte sau khôi phục):

| # | Mục | Đột biến | Kết quả |
|---|---|---|---|
| M20a | 1 | bỏ `d2_specific_heavy` khỏi `NOT_EVALUABLE_REASONS` | 1 fail |
| M20b | 2 | `truncate_read` không cắt `skills` | 2 fail |
| M20c | 3 | `ready` không đòi `note` | 1 fail |
| M20d | 4 | `present: bool` | 1 fail |
| M20e | 5 | `invalid_query_message` nêu tên khóa lạ | 1 fail |
| M20f | 6 | D7 đòi đúng một khóa như cũ | 1 fail (web) |

**Kết quả cuối** (2026-11-27, sau đợt này):

| Lệnh | Kết quả |
|---|---|
| `uv run pytest -q` (toàn bộ, Postgres test thật) | **2225 passed**, 817 giây |
| `uv run ruff check .` | All checks passed |
| `uv run python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` | 10 gates: 10 pass, 0 failed |
| `npx vitest run` (web) | 36 file, **514 passed** |
| `npx tsc --noEmit` (web) | không lỗi (đã revert `web/tsconfig.tsbuildinfo`) |
| `npx eslint .` (web) | không lỗi |
