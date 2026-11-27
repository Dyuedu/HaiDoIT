# Tasks: Hình response của tin dán ("Soi tin") và dữ liệu giả

**Input**: Design documents from `specs/230-hinh-soi-tin/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Viết trước theo `tdd.md`. Test mới phải đỏ trước khi viết code.

## Phase 1: Test

- [x] T001 [US1] Test mục `match`: ví dụ FR-28 (16/18 = 89%), đếm nhóm, nhóm theo kỹ năng, kỹ năng không có dòng, `cv_first`, không hồ sơ, quay về ô rộng, không ô nào đủ mẫu, không kỹ năng, `market` và `warnings` `not_ready`, hình `ready` đã khai, làm tròn nửa lên, trọng số truyền vào, trong `tests/api/test_fr28_posting_check.py`
- [x] T002 [US1] Test `POST /api/v1/posting-reads`: hình, mã trong bộ mã, tin có phí, không phải tin, quá ngắn, thứ tự chọn của nguồn giả, ranh giới 200 ký tự, schema sai, thân sai hình, mã lỗi đã khai trong OpenAPI, nguồn `model` trả 503, chọn nguồn bằng biến, trong `tests/api/test_fr26_posting_read.py`
- [x] T003 [US1] Test query chỉ mã và số: tham số lạ, kỹ năng ngoài bộ từ vựng, cụm chưa nhận diện của bước một, trần 200, `have` dùng chung bộ đọc, sự kiện đóng sai định dạng, trong `tests/api/test_ad22_posting_check_query.py`
- [x] T004 [US1] Test AD-11: nguồn không giữ trạng thái, không log, không cache POST, không ghi file, mã nguồn không có dấu vết lưu trữ, trong `tests/api/test_ad11_posting_read.py`
- [x] T005 [US1] Test prod không bao giờ giả: compose đặt `stat` và `model`, prod trả 503 và 404, trong `tests/deploy/test_gh230_posting_nguon_prod.py`
- [x] T006 [US1] Test trọng số trong cấu hình có phiên bản trong `tests/core/test_ad10_rules_config.py`
- [x] T007 [US1] Cập nhật `tests/api/test_ad17_routes.py` (route mới, route nhận chữ người dùng), `test_ad17_ordinal_allowlist.py`, `test_ad17_web_fixtures.py`; thêm nguồn `posting_check` vào các lời gọi `create_app` ở mười hai file test khác
- [x] T008 [US1] Test web: hình, URL chỉ mã và số, lỗi, fixture, trong `web/tests/fr28-posting-fixture.test.ts`

## Phase 2: Implementation

- [x] T009 `[posting_match]` trong `config/rules.toml` và `posting_match_weights` trong `haido_core/config.py`
- [x] T010 `haido_api/schemas/posting.py`
- [x] T011 `haido_api/posting_match.py`
- [x] T012 `haido_api/posting_read.py`, `fixtures/fake_posting_reads.json`, `routes/posting.py`, handler trong `errors.py`, `create_app` trong `main.py`
- [x] T013 `MarketReadModel.posting_check`, `SOURCE_ENV`, route GET `/posting-check`, `FakeMarket.posting_check`, `StatMarket.posting_check`, ô `vn.backend.junior` của `fake_market.json`
- [x] T014 `deploy/compose.prod.yml` và `compose.loadtest.yml`
- [x] T015 `web/lib/posting.ts`, sinh tám fixture web
- [x] T016 Sinh lại `docs/api/openapi.json`, cập nhật `docs/api/envelope-meta.md`

## Phase 3: Sau merge

- [ ] T017 Comment hợp đồng lên #230 cho người làm #231–#247

## Vòng review 2026-11-27

Test đứng trước code; kết quả RED và GREEN ở `tdd.md` mục "Đợt review (2026-11-27)".

### Phase R1: Test

- [x] T101 [US1] Test bước một: `not_it` (quy tắc `job_markers`), `branch`, `duties_described`, `title_level`, `salary_non_numeric`, `contact_quotes`, `collected` (đủ link), mọi trường của bước một thuộc `QUERY_FIELDS` hoặc `SCREEN_ONLY_FIELDS`, trong `tests/api/test_fr26_posting_read.py`
- [x] T102 [US1] Test bước hai: tham số mới, nhánh thuộc vai trò, `have` mã lạ bị bỏ qua, trần lương chung, mọi tin đọc được ở bước một qua bước hai (cấp `unknown` quay về ô mọi cấp), route chuyển đủ sự kiện cho nguồn, trong `tests/api/test_ad22_posting_check_query.py`
- [x] T103 [US1] Test hình `ready` của `market` (khoảng tin cậy theo n, lương quy đổi, `cell_id` riêng) và `warnings` (bảy dấu hiệu, dữ kiện có kiểu, `not_evaluable`, câu ghi chú cố định) cùng các kiểu sai, trong `tests/api/test_fr30_fr31_posting_ready_shapes.py` và `tests/api/posting_examples.py`
- [x] T104 [US1] Test trần cỡ thân (Content-Length, đếm byte lúc đọc, 20.001 ký tự, 20.000 ký tự 3 và 4 byte), cắt kết quả quá cỡ, 502 `read_failed`, trong `tests/api/test_gh230_posting_read_caps.py`
- [x] T105 [US1] Test AD-11: bắt mọi lỗi của nguồn đọc, log và `uvicorn.error` không có chữ của tin, câu lỗi chuẩn, trong `tests/api/test_ad11_posting_read.py`
- [x] T106 [US1] Test prod: mã chính xác 503 `check_unavailable`, demo và loadtest cùng `model` và `stat`, trong `tests/deploy/test_gh230_posting_nguon_prod.py` và `tests/api/test_ad17_meta_nguon_stat.py`
- [x] T107 [US1] Test cấu hình `[posting_read]`, `[posting_market]`, phiên bản 2026-11-27.2, trong `tests/core/test_ad10_rules_config.py`; cập nhật `test_ad17_ordinal_allowlist.py`, `test_ad17_routes.py`, `test_ad17_web_fixtures.py`
- [x] T108 [US1] Test web: trường mới, URL không có chữ, `ready` market và warnings, `check_unavailable` thử lại được, trong `web/tests/fr28-posting-fixture.test.ts` và `web/tests/fr30-fr31-posting-ready.test.ts`
- [x] T109 Sửa hai nit của test (`test_ad22_su_kien_chua_doi_ket_qua_o_230` kiểm 200, comment của `test_fr28_ky_nang_ngoai_tin_khong_doi_muc_khop`)

### Phase R2: Implementation

- [x] T110 `config/rules.toml` (`[posting_read]`, `[posting_market]`, phiên bản) và `haido_core/config.py`
- [x] T111 `haido_api/schemas/posting.py`: trường mới của bước một, hình `ready` của `market` và `warnings`, `check_against_meta`, bộ đọc cấu hình có cache (`_rules`, `_read_vocab`, `branch_codes`)
- [x] T112 `haido_api/posting_read.py` (`truncate_read`, `job_markers`, `devops_markers`), `fixtures/fake_posting_reads.json` (ba tin), `routes/posting.py` (route class chặn cỡ, bắt lỗi), `errors.py` (câu chuẩn, `CheckUnavailable`)
- [x] T113 `haido_api/routes/market.py` (tham số mới, nhánh theo vai trò, 503 khai trong OpenAPI), `market_source.py`, `fake_market.py` (quay về ô mọi cấp), `stat_market.py` (503)
- [x] T114 `deploy/compose.*.yml` (chú thích; demo và loadtest đã `model` và `stat`)
- [x] T115 `web/lib/posting.ts` (kiểu, bộ kiểm hình `ready`, URL), sinh lại fixture web, hai ví dụ `ready`
- [x] T116 Sinh lại `docs/api/openapi.json` (`HAIDO_UPDATE_OPENAPI=1 uv run pytest tests/api/test_ad17_routes.py -q`), cập nhật `docs/api/envelope-meta.md`
- [x] T117 Cập nhật `spec.md`, `plan.md`, `data-model.md`, `research.md`, `tdd.md`; thêm ghi chú ngày vào `specs/212-hinh-lo-trinh-hoc/spec.md` và `tdd.md` của #149 và #212

### Phase R3: Sau merge

- [ ] T118 Comment hợp đồng vòng review lên #230 cho người làm #231–#247 (#231: trần cỡ đã có, còn trần tốc độ và câu chữ)
