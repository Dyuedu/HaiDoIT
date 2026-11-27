# Implementation Plan: Hình response của tin dán ("Soi tin") và dữ liệu giả

**Branch**: `gh-230-hinh-soi-tin` | **Date**: 2026-11-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/230-hinh-soi-tin/spec.md`

## Summary

Thêm hai route: `POST /api/v1/posting-reads` (đọc chữ dán một lần, nguồn riêng `PostingReader`, không lưu gì) và `GET /api/v1/posting-check` (phép thứ sáu của `MarketReadModel`, `posting_check`, chỉ nhận mã và số). Schema ở `haido_api/schemas/posting.py`. Phép tính mức khớp ở `haido_api/posting_match.py`, dùng chung cho bản giả và bản thật (#234); trọng số 3/2/1 ở `config/rules.toml` mục `[posting_match]` (AD-10). Bản giả của `posting_check` dựng trên `skill_rates` của cùng ô nên cùng ô và nhãn quay về; thêm ô `vn.backend.junior` vào `fake_market.json` để ví dụ FR-28 chạy trên một ô đủ mẫu mà không quay về. Mục `market` và `warnings` có hình `ready` đầy đủ (FR-30, FR-31) nhưng luôn `not_ready` ở dữ liệu tới #240–#246. Prod: `posting_check` đọc `stat` (503 `check_unavailable` tới #234), nguồn đọc là `model` (503 `read_unavailable` tới #232).

**Vòng review 2026-11-27**: bước 1 thêm `not_it`, `branch`, sự kiện danh sách (`duties_described`, `title_level`, `salary_non_numeric`), `contact_quotes`, `collected`; bước 2 nhận thêm các mã và số tương ứng và lặp lại `branch`; hình `ready` của `market` (phân vị kèm khoảng tin cậy, lương quy đổi, `cell_id` riêng) và `warnings` (bảy dấu hiệu D1 đến D7 có trạng thái, dữ kiện có kiểu, gợi ý, câu ghi chú cố định) được chốt và kiểm với `meta`; kết quả đọc quá cỡ bị cắt, lỗi của nguồn đọc là 502 và không lọt chữ ra log; thân POST bị chặn cỡ trước khi phân tích (AD-9); `stat` trả 503 `check_unavailable`; bản giả quay về ô mọi cấp cho cấp không có ô; web nhận hình `ready`.

## Technical Context

**Language/Version**: Python 3.13, FastAPI, Pydantic 2; TypeScript, Next.js, Vitest

**Primary Dependencies**: Không thêm gói.

**Storage**: Không đổi cơ sở dữ liệu. Chữ dán không bao giờ chạm bảng nào (AD-11).

**Testing**: `HAIDO_TEST_DATABASE_URL=... uv run pytest -q`; `cd web && npx vitest run tests/fr28-posting-fixture.test.ts`

**Constraints**: AD-9 (một cổng đọc, truy vết `model_id`/`prompt_version`/`vocab_version`; trần ở #231), AD-10 (trọng số trong config có phiên bản), AD-11 (không lưu, không log chữ dán), AD-17 (số của thị trường là `Stat`; điểm và số đếm là `Ordinal`), AD-22 (hồ sơ chỉ ở GET `?have=`, phép tính ở API), #309 (prod không bao giờ giả).

## Constitution Check

- AD-17: tỷ lệ là `Stat` có `meta.cells`; `PostingReadData` không có `meta` vì không có số liệu thị trường (xem spec.md).
- AD-22: mức khớp, nhóm, cờ `have`, `cv_first` tính ở API; web không đếm.
- Không viết spec vào `_bmad-output/`.

## Project Structure

### Documentation (this feature)

```text
specs/230-hinh-soi-tin/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
haido_api/schemas/posting.py                 (mới; vòng review: PostingReadData thêm not_it, branch, duties_described, title_level, salary_non_numeric,
                                               contact_quotes, collected; MAX_TEXT_CHARS, MAX_SALARY, POSTING_READ_MESSAGES; PostingMarket/PostingPercentile/
                                               PostingSalaryComparison (quy đổi, tỷ giá, ci_low/ci_high); PostingWarnings, PostingWarningSign và bảy kiểu dữ kiện;
                                               PostingCheckData.branch và check_against_meta; bộ đọc cấu hình có cache)
haido_api/posting_match.py                   (mới: build_match, match_percent)
haido_api/posting_read.py                    (mới; vòng review: truncate_read, job_markers, devops_markers, hợp đồng lỗi không mang chữ của tin)
haido_api/routes/posting.py                  (mới: POST /api/v1/posting-reads; vòng review: route class chặn cỡ thân, bắt lỗi của nguồn đọc, chỉ ghi tên kiểu)
haido_api/fixtures/fake_posting_reads.json   (mới: dấu chọn kết quả và ba tin mẫu: backend, fee, cloud)
haido_api/routes/market.py                   (SOURCE_ENV posting_check, parse_code_list, route GET /posting-check, bộ chặn tham số lạ; vòng review: tham số mới, nhánh theo vai trò, 503 khai trong OpenAPI)
haido_api/market_source.py                   (MarketReadModel.posting_check; vòng review: CheckUnavailable)
haido_api/fake_market.py                     (FakeMarket.posting_check; vòng review: quay về ô mọi cấp cho cấp không có ô, echo branch)
haido_api/stat_market.py                     (StatMarket.posting_check: CheckUnavailable (503) tới #234)
haido_api/fixtures/fake_market.json          (ô vn.backend.junior và skill_rates.backend.junior)
haido_api/errors.py, haido_api/main.py       (handler PostingReadRefused (câu chuẩn của mã lỗi) và CheckUnavailable, create_app(posting_reader=), router)
haido_core/config.py, config/rules.toml      ([posting_match] trọng số; vòng review: [posting_read] max_chars, max_body_bytes, [posting_market] ci_below_n, config_version 2026-11-27.2)
deploy/compose.prod.yml, compose.demo.yml, compose.loadtest.yml (HAIDO_MARKET_SOURCE_POSTING_CHECK: stat, HAIDO_POSTING_READER: model)
docs/api/openapi.json, docs/api/envelope-meta.md
web/lib/posting.ts                           (mới: kiểu, bộ kiểm gồm hình ready, postingCheckUrl, fetchPostingRead, fetchPostingCheck)
web/tests/fixtures/posting-read-{backend,fee,cloud,not-posting,not-it,too-short}.json, posting-check-{backend.junior-have,backend.junior,backend.intern-have,backend.unknown-fee,data_engineer.entry-have}.json (mới, sinh từ API giả),
  posting-check-ready-{full,sparse}.json (mới, ví dụ viết tay của hình ready)
```

### Test code

```text
tests/api/posting_samples.py                 (mới: chữ mẫu, mã kỹ năng; vòng review: tin not_it, tin DevOps, query_from_read, danh sách trường của bước 1)
tests/api/posting_examples.py                (mới, vòng review: hai ví dụ ready của market và warnings)
tests/api/test_fr30_fr31_posting_ready_shapes.py (mới, vòng review: hình ready và các kiểu sai)
tests/api/test_gh230_posting_read_caps.py    (mới, vòng review: trần cỡ thân, cắt kết quả quá cỡ, 502 read_failed)
web/tests/fr30-fr31-posting-ready.test.ts    (mới, vòng review: web nhận hình ready)
tests/api/test_fr28_posting_check.py         (mới)
tests/api/test_fr26_posting_read.py          (mới)
tests/api/test_ad22_posting_check_query.py   (mới)
tests/api/test_ad11_posting_read.py          (mới; vòng review: bắt lỗi nguồn đọc, log và uvicorn.error không có chữ của tin)
tests/deploy/test_gh230_posting_nguon_prod.py (mới; vòng review: mã chính xác 503 check_unavailable, demo và loadtest)
web/tests/fr28-posting-fixture.test.ts       (mới)
tests/core/test_ad10_rules_config.py         (BASE có [posting_match], [posting_read], [posting_market]; test trọng số, trần thân, ngưỡng khoảng tin cậy)
tests/api/test_ad17_routes.py                (SAMPLE_QUERY, route nhận chữ người dùng, yêu cầu fixture)
tests/api/test_ad17_ordinal_allowlist.py     (sáu trường Ordinal; vòng review: tiền quy đổi, tỷ giá, số đếm của dữ kiện từng dấu hiệu)
tests/api/test_ad17_meta_nguon_stat.py       (vòng review: stat trả 503 check_unavailable)
tests/api/test_ad17_web_fixtures.py          (fixture web của tin dán)
Thêm nguồn "posting_check" vào create_app ở: test_ad22_market_overview_stat, test_dat20_stat_market, test_fr09_skill_roles_stat,
test_fr19_skill_rates_stat, test_fr22_learning_path_draft, test_fr22_learning_path_stat, test_fr33_city_shares_level,
test_fr33_city_shares_years, test_fr37_newcomer_roles_stat, test_gh102_stat_market_theta, tests/steps/test_dat20_api_end_to_end,
tests/steps/test_gh284_aggregate_vai_tro_moi
```

## Issue cũ chưa có thư mục `specs/` mà #230 chạm vào file của chúng

Theo CLAUDE.md ("Khi sửa code thuộc một issue đã có spec"), issue cũ chưa có `specs/` thì không bắt buộc dựng lại nhưng phải ghi tên trong mô tả PR. Các file mà #230 sửa (`haido_api/errors.py`, `haido_api/main.py`, `haido_api/market_source.py`, `haido_api/fake_market.py`, `haido_api/fixtures/fake_market.json`, `haido_api/routes/market.py`, `haido_api/stat_market.py`, `haido_core/config.py`, `config/rules.toml`, `deploy/*`, `docs/api/*` và các test của chúng) đã được các issue sau đụng tới (tìm bằng `git log -- <file>`), chưa có thư mục `specs/` (tên theo thân commit khi `gh` không tìm thấy issue):

- #1 mở khung Hải Đồ IT trên máy dev
- #2 chốt envelope meta và endpoint dữ liệu giả
- #6 chốt snapshot và vòng đời tin
- #46 màn Bản đồ lối 2D và Bảng
- #93 [DAT.20] City-share aggregation, the publish step, and the API's real stat source
- #113 [US-A4] See which roles use a skill I already have
- #140 Reject an oversized CV before reading it and leave no temporary file (mẫu cho trần cỡ thân của POST `posting-reads`; `haido_api/uploads.py` không đổi)
- #162 Switch the map from fake data to real snapshots
- #259 List as sources only the sources whose postings are counted
- #263 Keep old LinkedIn postings out of every public number

Hành vi của các issue này không đổi: #230 chỉ thêm khóa nguồn, bảng cấu hình, ô và hàng fixture, route, và một lỗi 503 mới cho một route mới. Ghi các issue trên vào mô tả PR.

Các issue đã có `specs/` mà #230 chạm vào file đã được ghi một mục "Đợt sửa 2026-11-27 (#230)" ở `tdd.md` và `plan.md` của chúng. Riêng #149 (`skill-rates`) và #212 (`learning-path`) có thêm một thay đổi hành vi của **bản giả**: `backend/junior` nay trả 200 (ô `vn.backend.junior` mới), ghi ở `tdd.md` của hai issue đó.

**Structure Decision**: Giữ cách của #166: route chỉ chuyển tham số, nguồn chọn qua biến môi trường, hình `data` ở `schemas/`. Khác biệt duy nhất: bước một không phải số liệu thị trường nên không đi qua `MarketReadModel` mà có `PostingReader` và biến riêng.

## Complexity Tracking

| Vi phạm | Vì sao cần | Phương án đơn giản hơn bị loại vì |
|---|---|---|
| `posting_check` mang tham số sự kiện (`years_min`, `salary_*`, `contacts`, `fees`...) mà #230 chưa đọc | Chốt cách mã hóa một lần để ba màn dựng cùng nhau (mục đích của #230) | Để #240 và #244 tự thêm tham số làm đổi hợp đồng giữa chừng |
| Thêm ô `vn.backend.junior` vào fixture dùng chung | Ví dụ FR-28 cần một ô đủ mẫu của cấp `junior` (cấp mà bước một trả); không có thì màn phải gọi `entry` | Dùng `entry` làm cấp của tin: không đúng mã mà bước một trả |
