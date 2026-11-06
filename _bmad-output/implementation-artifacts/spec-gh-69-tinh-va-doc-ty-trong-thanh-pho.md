---
title: 'GH-69 [1.21] Tính và đọc tỷ trọng thành phố kèm cỡ mẫu'
type: 'feature'
created: '2026-11-06'
status: 'ready-for-dev'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/DOD.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Màn Bản đồ (1.15, #46) cần số thật, nhưng `GET /api/v1/city-shares` hiện chỉ có bản giả của #2. Chưa có bước nào biến tin đã thu thành tỷ trọng thành phố kèm cỡ mẫu, và chưa có bước nào đánh dấu một snapshot là đã tính xong.

**Approach:** Thêm ba thứ, chạy bằng CLI cho một snapshot S:
1. hàm dùng chung "chọn tin của một ô rồi đếm" (phép 3 trong `REGISTRY.md`), đặt trong `domain`;
2. bước tổng hợp: ghi số tin, cơ cấu cấp bậc và tỷ trọng theo thành phố × vai trò vào bảng `stat_*`;
3. bước `publish`: tự chạy sau mọi bước tính của S, chuyển S sang `published` hoặc `partial`.

API thêm nguồn `stat`, chỉ tra `stat_*` và snapshot theo khóa, cắm vào `IMPLEMENTATIONS`. Route và schema của #2 giữ nguyên.

## Boundaries & Constraints

**Always:**
- Vai trò, cấp bậc, thành phố của tin lấy từ hàm dùng chung số 6 của #68 (phân loại). Không tự viết luật gán nhãn.
- Hàm dùng chung số 3 là hàm thuần trong `haido_core/domain/`, đúng chữ ký trong `REGISTRY.md` (#3), gọi được cho một ô và cho một lô. Bước tổng hợp chỉ nạp dữ liệu, gọi hàm số 6 và số 3, rồi ghi.
- Đếm theo cụm: số cụm khác nhau, không phải số bản ghi. Phát hiện tin trùng thuộc 1.8; trong Sprint 1 mỗi tin là một cụm riêng.
- Tin thuộc ô của S khi ngày thấy cuối, xét trên các quan sát có `snapshot_id ≤ S`, nằm trong `window_days` ngày tính tới S, kể cả ngày S.
- Config đọc từ file có `config_version`, không viết cứng trong code. `stat_cells` lưu `config_version` đã dùng.
- Vai trò là danh sách trong config cộng `all`; `all` đếm mọi tin IT. Năm dòng thành phố (Hà Nội, TP.HCM, Đà Nẵng, Khác, không xác định) luôn có mặt, kể cả `n = 0`. Mã lấy từ enum của #68.
- Tỷ trọng = `n` ô thành phố ÷ `n` ô toàn quốc của cùng vai trò, kiểu `double precision`, không làm tròn, tính ở bước tổng hợp. Ô toàn quốc có `n = 0` thì ghi các ô với `n = 0` và không ghi tỷ trọng.
- Hàng `stat_*` của S ghi trong một transaction. Chạy lại cho S chưa chốt thì xóa rồi ghi lại; S đã `published` hoặc `partial` thì từ chối.
- `publish` đặt `published` khi mọi nguồn tự động đang bật của S chạy thành công, ngược lại `partial` kèm `sources_failed`. Nó chỉ chạy sau khi mọi bước tính của S đã ghi xong.
- API đọc snapshot mới nhất có trạng thái `published` hoặc `partial` và có hàng `stat_city_shares`. `meta` lấy theo bảng ở Design Notes. `display` chỉ do `suppression_for` quyết; response qua được `Envelope[CitySharesData]`.
- Cùng S, cùng config thì chạy lại cho kết quả giống hệt.

**Never:**
- `haido_api` không chạy `GROUP BY`, `COUNT`, `AVG` trên bảng tin và không nhắc tên bảng `job_*` (AD-5, cổng mang mã AD-7). API chỉ tra `stat_*` và bảng snapshot theo khóa.
- Không đọc bảng riêng của scraper (`jobs`, `source_runs`). Không ghi bảng tin của #6. Trên bảng snapshot của #6, chỉ bước `publish` được đổi cột trạng thái.
- Không đổi route, schema hay `docs/api/openapi.json` của #2.
- Không làm tỷ lệ kỹ năng (#27), nhánh (#16), phát hiện tin trùng (1.8), hay nút admin bật/tắt snapshot.

**Quyết định (06/11/2026):**
- Bảng `stat_*` tạo bằng migration Alembic trên head của #1 (`haido_core/db/migrations`), kết nối qua `HAIDO_DATABASE_URL`.
- Tin, quan sát, snapshot và lượt chạy từng nguồn đọc từ bảng của #6 (1.4). Phần đọc bắt đầu khi #6 merge.
- Config tạm là file `config/rules.toml` có `config_version`, dùng chung với #68. Chuyển sang bảng sau (nợ AD-10 và DoD dòng 4).
- #69 viết hàm dùng chung số 3; #6, #17, #36 gọi lại.
- #69 viết bước `publish`, tự chạy sau mọi bước tính. Admin bật/tắt snapshot để sau.
- Giữ một spec dù dài hơn mức khuyến nghị.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Đủ mẫu + mẫu nhỏ | Ở S, `data_engineer` có HN 40, HCM 35, ĐN 5, Khác 3, không rõ 2 | Năm dòng; ô `vn.data_engineer` n = 85; ĐN n = 5 `low_sample_shown`; tổng `share` = 1 | N/A |
| Cơ cấu cấp bậc | Trong 40 tin HN có 10 junior, 30 senior | Ô `ha_noi.data_engineer` có `seniority_mix` = {junior: 10, senior: 30} | N/A |
| Vai trò `all` | Như trên, cộng tin `backend` và tin "không thuộc IT" | Ô `all` đếm mọi tin IT, không có tin "không thuộc IT" | N/A |
| Thành phố trống | Không có tin ĐN | Dòng ĐN: n = 0, `share` = 0, `low_sample_shown` | N/A |
| Biên cửa sổ | Tin thấy cuối ở S − 59 và ở S − 60 | S − 59 được đếm; S − 60 không | N/A |
| Quan sát sau S | Tin chỉ có quan sát `snapshot_id = S + 1` | Không vào ô nào của S | N/A |
| Cùng cụm | Hai tin mang cùng mã cụm | Đếm là 1 | N/A |
| Toàn quốc n = 0 | `qa` có trong config, không tin nào ở S | Ô n = 0, không có tỷ trọng; API trả 404 `unknown_cell`, `snapshot_date = S` | Hình lỗi chuẩn |
| Chạy lại S chưa chốt | Chạy bước tổng hợp hai lần cho S | Hàng `stat_*` giống hệt, không lỗi khóa | N/A |
| S đã chốt | Chạy bước tổng hợp cho S `published` hoặc `partial` | Không ghi hàng nào; lệnh thoát mã khác 0 kèm lý do | Báo lỗi, không sửa dữ liệu |
| `publish` | Mọi nguồn tự động của S thành công / một nguồn lỗi | `published`, `sources_failed = []` / `partial`, `sources_failed` = [nguồn đó] | N/A |
| Chưa có snapshot đọc được | Nguồn `stat`, chưa snapshot nào đã chốt có `stat_city_shares` | 404 `unknown_cell`, `snapshot_date = null` | Hình lỗi chuẩn |

</frozen-after-approval>

## Code Map

- `haido_api/market_source.py` -- `MarketReadModel.city_shares`, `UnknownCell(snapshot_date=None)`: bản thật cài đúng Protocol này.
- `haido_api/routes/market.py` -- `IMPLEMENTATIONS` nhận hàm không đối số, và app dựng ngay lúc import. Vì vậy `StatMarket` không mở kết nối DB trong `__init__`, chỉ mở khi có request.
- `haido_api/fake_market.py` -- mẫu dựng `Meta`, `CellMeta` bằng `suppression_for`; dùng lại cách làm, không import bản giả.
- `haido_api/schemas/market.py` -- `CitySharesData`: tổng `share` = 1 (sai số 1e-9), không trùng `city`, không `value` null.
- `haido_core/domain/envelope.py`, `display_policy.py` -- dùng nguyên. `Thresholds` bắt buộc `theta_core`, `theta_common`; `Meta` bắt buộc ít nhất một `coverage_notes`.
- `haido_core/domain/REGISTRY.md` (#3) -- chữ ký hàm số 3 và số 6, và chỗ đặt code. Chưa có thì chờ #3.
- `haido_core/db/migrations/` (#1, head `0001_initial`) -- thêm migration cho `stat_cells`, `stat_city_shares`. `env.py` đọc `HAIDO_DATABASE_URL` và từ chối máy chủ ở xa nếu thiếu `HAIDO_ALLOW_REMOTE_MIGRATION=1`.
- Bảng của #6 -- `job_postings`, `job_observations` (có `snapshot_id`), snapshot (trạng thái, `sources`, `sources_failed`), lượt chạy từng nguồn. Tên cột theo migration của #6 khi merge.
- `tools/gates/check_gates.py` -- cổng mang mã AD-7 (nội dung là AD-5) quét `haido_api/`. CI đã chạy `--require AD-1 AD-17 AD-25`.
- `.github/workflows/ci.yml` -- job `python` chưa có Postgres.
- `_bmad-output/implementation-artifacts/deferred-work.md` -- mục của #1 "chưa có đường chạy migration trên prod": #69 là story đầu tiên thêm bảng.

## Tasks & Acceptance

**Execution:**
- [ ] `config/rules.toml`, `haido_core/config.py` -- `config_version`, `min_sample` (30), `window_days` (60), `theta_core` (0.3), `theta_common` (0.1), lưu ý độ phủ; đọc bằng `tomllib`. #68 thêm danh sách vai trò vào cùng file -- DoD dòng 4
- [ ] Module trong `haido_core/domain/` theo `REGISTRY.md` -- hàm dùng chung số 3: nhận tin (mã cụm, nhãn, ngày thấy cuối) và S, trả tập tin của ô và số cụm -- AD-2
- [ ] `haido_core/db/` và migration mới trên `0001_initial` -- `stat_cells` (khóa `snapshot_id, role, branch, seniority, scope`; `branch`, `seniority` = `all`; `scope` = mã thành phố hoặc `vn`; `n`, `seniority_mix`, `config_version`) và `stat_city_shares` (`snapshot_id, role, city, share double precision`) -- AD-6, một head
- [ ] `haido_core/steps/aggregate_city_shares.py` -- CLI `--snapshot YYYY-MM-DD`: nạp tin của S từ bảng #6, gọi hàm số 6 và số 3, ghi `stat_*` trong một transaction, từ chối S đã chốt -- AD-4, AD-15
- [ ] `haido_core/steps/publish.py` -- CLI `--snapshot`: đặt `published`/`partial` theo lượt chạy từng nguồn của S -- AD-4
- [ ] `haido_api/stat_market.py` -- `StatMarket.city_shares` tra theo khóa, dựng `Envelope` theo bảng `meta`, mở kết nối khi có request; `skill_rates` báo `NotImplementedError` tới #27 -- AD-5
- [ ] `haido_api/routes/market.py` -- thêm `"stat": StatMarket` -- route và schema không đổi
- [ ] `tests/domain/test_ad2_dan_so_o.py`, `tests/steps/test_fr33_ty_trong_thanh_pho.py`, `tests/api/test_ad17_city_shares_stat.py` -- mọi dòng I/O Matrix; test tất định gắn `@pytest.mark.determinism`; test DB đọc `TEST_DATABASE_URL` -- DoD dòng 11
- [ ] `.github/workflows/ci.yml` -- thêm service Postgres và `TEST_DATABASE_URL` cho job `python`, để test DB chạy thật chứ không bị bỏ qua -- DoD dòng 12
- [ ] `docs/api/envelope-meta.md`, `README.md` -- nguồn `stat`, lệnh CLI của bước tổng hợp và `publish` -- DoD dòng 14

**Acceptance Criteria:**
- Given S đã nạp và đã phân loại, when bước tổng hợp chạy, then có một ô cho mỗi thành phố × vai trò và một ô toàn quốc cho mỗi vai trò, kể cả `all`. Mỗi ô có `n` và cơ cấu cấp bậc, và năm tỷ trọng của mỗi vai trò cộng lại bằng 1.
- Given S đã tổng hợp, when `publish` chạy, then S thành `published` hoặc `partial`, và từ đó API đọc được S.
- Given nguồn `stat` và S đã chốt, when `GET /api/v1/city-shares?role=all`, then response qua được `Envelope[CitySharesData]`, `meta.snapshot_date = S`, và `docs/api/openapi.json` không đổi.
- Given code của #69, when chạy `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25`, then cổng mang mã AD-7 cũng PASS và không cổng nào FAIL.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

`meta` của nguồn `stat` lấy từ đâu:

| Trường | Nguồn |
|---|---|
| `snapshot_date`, `snapshot_status`, `sources`, `sources_failed` | Snapshot S của #6 (`publish` đã đặt trạng thái) |
| `thresholds` | Config: `min_sample`, `theta_core`, `theta_common` |
| `coverage_notes` | Config: ba lưu ý của FR-36, cộng "Dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên N nguồn", với N = số `sources` |
| `cells[cell_id]` | `stat_cells`: `n`, `seniority_mix`; `fallback_label = null`; `n_by_measure = {}`, `insufficient_by_measure = {}` (ô thành phố chưa có phân vị) |

`cell_id` có dạng `<scope>.<role>`, ví dụ `vn.data_engineer` hay `da_nang.data_engineer`, đúng như bản giả. `total_cell_id` là `vn.<role>`.

Cửa sổ: tin thuộc S khi `S − (window_days − 1) ≤ last_seen ≤ S`. `last_seen` chỉ xét quan sát có `snapshot_id ≤ S`, nên tính lại một S cũ vẫn ra đúng số cũ.

## Verification

**Commands:**
- `uv run ruff check .` và `uv run pytest -q` -- expected: xanh; test DB chạy thật khi có `TEST_DATABASE_URL`
- `uv run alembic heads` -- expected: đúng một head
- `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25` -- expected: `0 failed`
- `uv run python -m haido_core.steps.aggregate_city_shares --snapshot <S>`, rồi `uv run python -m haido_core.steps.publish --snapshot <S>`, rồi chạy API với `HAIDO_MARKET_SOURCE_CITY_SHARES=stat` và gọi `/api/v1/city-shares?role=all` -- expected: 200, `meta.snapshot_date = S`
