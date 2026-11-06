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
- Vai trò là danh sách trong config cộng `all`; `all` đếm mọi tin IT. Năm dòng thành phố (Hà Nội, TP.HCM, Đà Nẵng, Khác, không xác định) luôn có mặt, kể cả `n = 0`. #68 trả nhãn tiếng Việt (`"Hà Nội"`, `"Backend"`…), không có enum: bước tổng hợp đổi nhãn sang mã snake_case theo bảng đổi trong config.
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
- Tin, quan sát, snapshot và lượt chạy từng nguồn đọc từ schema `haido` của #6 (1.4, PR #77).
- Config tạm là file `config/rules.toml` có `config_version`. #6 đã tạo file với `window_days` và `sources.auto`; #69 thêm khóa của mình vào cùng file. Luật phân loại của #68 vẫn nằm trong code (`default_classify_config`). Chuyển sang bảng sau (nợ AD-10 và DoD dòng 4).
- (06/11, sau #6) Mã của vai trò, cấp bậc, thành phố do #69 đổi từ nhãn của #68 bằng bảng đổi trong `config/rules.toml`, không sửa #68.
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
- `haido_core/domain/REGISTRY.md`, `registry.py` (#3, đã merge) -- phép 3 là Protocol `Population.population(requests: OneOrMany[PopulationRequest]) -> OneOrMany[int]`, `PopulationRequest(cell: CellKey, window_days)`, `CellKey(snapshot_id, role, branch, seniority, scope)`. Dữ liệu tin truyền vào lúc dựng object (như `RuleClassifier(config)`), nên `population` vẫn là hàm thuần. Cài ở `haido_core/domain/population.py`.
- `haido_core/domain/classify.py` (#68, đã merge) -- `RuleClassifier(default_classify_config()).classify(PostingFacts)` trả `Classification(role, branch, seniority, city)` bằng nhãn tiếng Việt; `counts_in_aggregate()` loại `"không thuộc IT"`. Không sửa file này.
- `haido_core/db/tables.py`, `snapshot_store.py` (#6) -- schema `haido`:
  - `snapshots(snapshot_id DATE, status open|published|partial, closed_at, sources_failed TEXT[])`. Không có cột `sources`.
  - `pipeline_runs(snapshot_id, source, mode auto|manual, success)`.
  - `job_postings(id, source, source_url)`.
  - `job_observations(posting_id, snapshot_id, pipeline_run_id)`.
  - `stat_job_lifecycle(snapshot_id, posting_id, last_seen, …)`.
  - Dữ kiện tin tại S lấy bằng `snapshot_store.facts_at(conn, S)`: `title`, `company`, `location_text`, `experience_level`, `job_level`.
- `haido_core/db/migrations/versions/0002_haido_snapshot.py` (#6) -- head hiện tại. Migration của #69 đặt `down_revision = "0002_haido_snapshot"`, tạo bảng trong schema `haido`. `env.py` từ chối máy chủ ở xa nếu thiếu `HAIDO_ALLOW_REMOTE_MIGRATION=1`.
- `haido_core/config.py`, `config/rules.toml` (#6) -- `load_rules()` trả `RulesConfig(config_version, window_days, auto_sources)`; mở rộng thêm khóa, giữ lỗi tiếng Việt khi thiếu khóa.
- `haido_core/cli.py`, `haido_core/steps/common.py`, `haido_core/db/engine.py` (#6) -- thêm lệnh con `aggregate` và `publish` vào `COMMANDS`; dùng lại `StepError`, `SnapshotClosedError`, `parse_snapshot_id`, `make_write_engine`. Chạy bằng `uv run python -m haido_core.cli …` (lệnh `haido` chưa cài được).
- `tests/conftest.py` (#6) -- fixture `pg_engine`, `scraper_db`; `HAIDO_TEST_DATABASE_URL` phải có tên DB kết thúc bằng `_test`. `tests/steps/conftest.py` có `Env.ingest()`, `Env.lifecycle()` để dựng dữ liệu qua đúng hai bước của #6.
- `web/lib/labels.ts` (#46) -- chip vai trò đang là mã của bản giả (`all`, `data_ai`, `backend`). Spec #46 cho phép đổi riêng file này khi có mã thật.
- `tools/gates/check_gates.py` -- cổng mang mã AD-7 (nội dung là AD-5) quét `haido_api/`. CI chạy `--require AD-1 AD-17 AD-25 AD-2 AD-7`.
- `.github/workflows/ci.yml` -- job `python` đã có Postgres và `HAIDO_TEST_DATABASE_URL` (#6).
- `_bmad-output/implementation-artifacts/deferred-work.md` -- mục của #1 "chưa có đường chạy migration trên prod" vẫn mở.

## Tasks & Acceptance

**Cách làm: TDD** theo `docs/templates/test-driven-tdd/test-driven-development.md`, như #46 và #6. Mỗi cặp: viết test, chạy đúng file test đó và thấy đỏ vì chưa có hành vi (không phải lỗi cú pháp hay import), ghi một dòng vào Implementation Notes, rồi code vừa đủ cho xanh.

**Chạy test:** trong vòng đỏ-xanh chỉ chạy file test đang làm; chạy toàn bộ `uv run pytest -q` một lần ở cuối. Postgres local: `docker compose -f deploy/compose.local.yml up -d --wait postgres`, tạo DB `haido_test` một lần (lệnh ở README), rồi đặt `HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test`.

**Execution:**
- [ ] Test đỏ `tests/core/test_ad10_rules_config.py` rồi code xanh `config/rules.toml`, `haido_core/config.py` -- thêm `min_sample` (30), `theta_core` (0.3), `theta_common` (0.1), `coverage_notes`, danh sách vai trò và ba bảng đổi nhãn → mã ở Design Notes; tăng `config_version`; test rằng mọi nhãn mà `default_classify_config()` có thể trả đều có mã -- DoD dòng 4
- [ ] Test đỏ `tests/domain/test_ad2_dan_so_o.py` rồi code xanh `haido_core/domain/population.py` -- cài Protocol `Population` của `registry.py`: dựng với danh sách tin (mã cụm, mã vai trò, mã cấp bậc, mã thành phố, `last_seen`), `population(...)` trả số cụm của ô; gọi được cho một yêu cầu và cho một lô -- AD-2
- [ ] Test đỏ `tests/db/test_ad6_stat_schema.py` rồi code xanh migration `0003` và `haido_core/db/tables.py` -- `haido.stat_cells` (khóa `snapshot_id, role, branch, seniority, scope`; `branch`, `seniority` = `all`; `scope` = mã thành phố hoặc `vn`; `n`, `seniority_mix` JSONB, `config_version`) và `haido.stat_city_shares` (`snapshot_id, role, city, share double precision`) -- AD-6, một head
- [ ] Test đỏ `tests/steps/test_fr33_ty_trong_thanh_pho.py` rồi code xanh `haido_core/steps/aggregate_city_shares.py` và lệnh `aggregate` trong `haido_core/cli.py` -- nạp tin của S từ schema `haido`, phân loại bằng `RuleClassifier`, đổi nhãn sang mã, gọi phép 3, ghi `stat_*` trong một transaction, từ chối S đã chốt; dữ liệu test dựng qua `Env.ingest()` và `Env.lifecycle()` -- AD-4, AD-15
- [ ] Test đỏ `tests/steps/test_ad4_publish.py` rồi code xanh `haido_core/steps/publish.py` và lệnh `publish` -- đặt `status`, `closed_at`, `sources_failed` theo Design Notes; từ chối S chưa có `stat_city_shares` -- AD-4
- [ ] Test đỏ `tests/api/test_ad17_city_shares_stat.py` rồi code xanh `haido_api/stat_market.py` và `"stat": StatMarket` trong `haido_api/routes/market.py` -- tra theo khóa, dựng `Envelope` theo bảng `meta`, mở kết nối khi có request; `skill_rates` báo `NotImplementedError` tới #27 -- AD-5
- [ ] `web/lib/labels.ts` và test web liên quan -- `ROLE_OPTIONS` là `all` cộng các vai trò trong config, cùng mã, nhãn tiếng Việt theo nhãn của #68; mặc định vẫn `all` -- để chip gọi đúng ô có thật (spec #46: chỉ đổi file này trong `web/lib/`)
- [ ] `docs/api/envelope-meta.md`, `README.md` -- nguồn `stat`, thứ tự lệnh `ingest → lifecycle → aggregate → publish`, bảng đổi mã -- DoD dòng 14

**Acceptance Criteria:**
- Given S đã `ingest` và `lifecycle`, when chạy `aggregate`, then có một ô cho mỗi thành phố × vai trò và một ô toàn quốc cho mỗi vai trò, kể cả `all`. Mỗi ô có `n` và cơ cấu cấp bậc, và năm tỷ trọng của mỗi vai trò cộng lại bằng 1.
- Given S đã tổng hợp, when `publish` chạy, then S thành `published` hoặc `partial`, và từ đó API đọc được S.
- Given nguồn `stat` và S đã chốt, when `GET /api/v1/city-shares?role=all`, then response qua được `Envelope[CitySharesData]`, `meta.snapshot_date = S`, và `docs/api/openapi.json` không đổi.
- Given code của #69, when chạy `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7`, then không cổng nào FAIL.

## Implementation Notes

## Spec Change Log

### 2026-11-06 — Cập nhật theo #6 và #68 đã có code (người sở hữu spec quyết)

- **Nguyên nhân:** #6 (PR #77) và #68 (PR #74) đã có code. #68 trả nhãn tiếng Việt chứ không có enum, còn luật phân loại nằm trong code Python, không nằm trong `config/rules.toml`.
- **Đã sửa trong khối frozen** (người sở hữu spec quyết ngày 06/11):
  - #69 đổi nhãn của #68 sang mã bằng bảng đổi trong config.
  - Config vẫn là `config/rules.toml`, dùng chung file với #6.
  - Bảng của #6 nằm ở schema `haido`.
- **Đã sửa ngoài frozen:**
  - Code Map ghi tên bảng và hàm thật của #6.
  - Tasks theo TDD; bỏ task thêm Postgres vào CI vì #6 đã làm; thêm task cho chip vai trò của web.
  - Design Notes: bảng đổi mã, cách lấy `sources`, cửa sổ tính từ `last_seen`.
- **Tránh được:**
  - dùng `in_window` của #6, vốn cho 61 ngày, trong khi Matrix đòi 60;
  - API giả định snapshot có cột `sources`.
- **Giữ nguyên:** Intent, Matrix, Never, AC (chỉ cập nhật lệnh cổng).

## Review Triage Log

## Design Notes

`meta` của nguồn `stat` lấy từ đâu:

| Trường | Nguồn |
|---|---|
| `snapshot_date`, `snapshot_status`, `sources_failed` | `haido.snapshots` của S (`publish` đã đặt) |
| `sources` | Nguồn có lượt chạy ở S trong `haido.pipeline_runs`, xếp A–Z (bảng snapshot không có cột `sources`) |
| `thresholds` | Config: `min_sample`, `theta_core`, `theta_common` |
| `coverage_notes` | Config: ba lưu ý của FR-36, cộng "Dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên N nguồn", với N = số `sources` |
| `cells[cell_id]` | `stat_cells`: `n`, `seniority_mix`; `fallback_label = null`; `n_by_measure = {}`, `insufficient_by_measure = {}` (ô thành phố chưa có phân vị) |

`cell_id` có dạng `<scope>.<role>`, ví dụ `vn.data_engineer` hay `da_nang.data_engineer`, đúng như bản giả. `total_cell_id` là `vn.<role>`.

Cửa sổ: tin thuộc S khi `S − (window_days − 1) ≤ last_seen ≤ S`. `last_seen` chỉ xét quan sát có `snapshot_id ≤ S`, nên tính lại một S cũ vẫn ra đúng số cũ.
- Lấy `last_seen` từ `haido.stat_job_lifecycle` của S. Không dùng cột `in_window`, vì cột này cho khoảng cách từ 0 tới `window_days`, tức 61 ngày.
- Tin không có hàng vòng đời ở S thì không vào ô nào. Đó là tin chỉ xuất hiện trong lượt chạy lỗi (AD-4).
- `stat_job_lifecycle` của S cũ hơn lần `ingest` gần nhất thì phải chạy lại `lifecycle` trước. `aggregate` không tự chạy `lifecycle`.

Đầu vào phép 6 cho mỗi tin, từ `facts_at(conn, S)` và `job_postings`:
- `title`, `location_text` lấy thẳng;
- `source` là `job_postings.source`;
- `source_category` là `None`;
- `seniority_text` là `job_level` và `experience_level` nối bằng dấu cách, bỏ phần trống.
- Tin không có dữ kiện thì mọi chữ trống. Phép 6 sẽ trả cấp bậc và thành phố "không xác định", và vai trò theo luật nguồn chỉ có tin IT.

Bảng đổi nhãn của #68 sang mã, ghi trong `config/rules.toml`:

| Loại | Nhãn của #68 → mã |
|---|---|
| Thành phố | `Hà Nội` → `ha_noi`, `TP.HCM` → `ho_chi_minh`, `Đà Nẵng` → `da_nang`, `Khác` → `other`, `không xác định` → `unknown` |
| Vai trò | `Embedded` → `embedded`, `AI/ML Engineer` → `ai_ml`, `Data Engineer` → `data_engineer`, `Data Analyst/BI` → `data_analyst`, `QA/Tester` → `qa`, `DevOps` → `devops`, `Mobile` → `mobile`, `Frontend` → `frontend`, `Backend` → `backend`, `Other` → `other` |
| Cấp bậc | `Intern` → `intern`, `Fresher` → `fresher`, `Junior` → `junior`, `Mid` → `mid`, `Senior` → `senior`, `Lead` → `lead`, `không xác định` → `unknown` |

Quy tắc khi đổi mã:
- Tin `"không thuộc IT"` không vào ô nào (`counts_in_aggregate`).
- Gặp nhãn không có trong bảng đổi thì `aggregate` báo lỗi và không ghi gì, không đoán. Test ở task 1 giữ bảng đổi khớp với luật của #68.

`publish` cho S:
- **Chạy được khi:** S đang `open` và đã có hàng `stat_city_shares`.
- **Nguồn lỗi (`sources_failed`):** mọi nguồn trong `sources.auto` có lượt `success = false` ở S, hoặc không có lượt nào ở S. Xếp A–Z.
- **Trạng thái:** `sources_failed` rỗng thì `published`, ngược lại `partial`. Đặt luôn `closed_at = now()`.
- **Nguồn thủ công** (`mode = manual`, ví dụ `topcv`) không làm S thành `partial`.

## Verification

**Commands:**
- `uv run ruff check .` và `uv run pytest -q` -- expected: xanh; với `HAIDO_TEST_DATABASE_URL` thì test DB chạy thật, không skip
- `npm --prefix web run lint`, `npm --prefix web run test`, `npm --prefix web run build` -- expected: thành công sau khi đổi `labels.ts`
- `uv run alembic heads` -- expected: đúng một head
- `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7` -- expected: `0 failed`
- Trên Postgres local: `uv run python -m haido_core.cli ingest --snapshot <S>`, rồi lần lượt `lifecycle`, `aggregate`, `publish` cho cùng S; chạy API với `HAIDO_MARKET_SOURCE_CITY_SHARES=stat` và gọi `/api/v1/city-shares?role=all` -- expected: 200, `meta.snapshot_date = S`
