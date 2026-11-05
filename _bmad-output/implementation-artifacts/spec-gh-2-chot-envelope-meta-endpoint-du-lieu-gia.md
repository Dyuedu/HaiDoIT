---
title: 'GH-2 [C-1] Chốt envelope meta và endpoint dữ liệu giả'
type: 'chore'
created: '2026-11-04'
updated: '2026-11-05'
status: 'done'
baseline_commit: '9a69b8a88b37ed031ecaddf265f5ccd9c57b5f47'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md'
  - '{project-root}/_bmad-output/planning-artifacts/DOD.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Web cần dựng màn hình ngay từ Sprint 1, nhưng số thật chỉ có từ Sprint 3 (#27). Hiện chưa có hợp đồng nào định nghĩa response chứa số trông ra sao. Nếu web tự đoán hình dạng, mọi màn hình sẽ phải sửa khi nối dữ liệu thật.

**Approach:** Chốt envelope `{data, meta}` của AD-17 thành Pydantic model dùng chung. Mỗi con số trong `data` là một `Stat` mang trạng thái hiển thị do `suppression_for` quyết. Dựng hai route `GET` thật, đọc qua một interface nguồn dữ liệu; #2 chỉ cài bản giả đọc fixture JSON. #27 chỉ cần thay bản cài đặt này, không đổi route hay schema.

## Boundaries & Constraints

**Always:**
- Mọi con số trong `data` là `Stat {value, kind, display, cell_id}`. `cell_id` phải có trong `meta.cells`.
- `display` chỉ do `suppression_for` quyết. Ngưỡng đọc từ một chỗ (`thresholds` trong fixture) rồi truyền vào hàm, không hardcode.
- Tỷ lệ là số thực 0–1, không làm tròn. `snapshot_date` dạng `YYYY-MM-DD`.
- Mọi lỗi có hình `{error: {code, message, snapshot_date}}`, `message` tiếng Việt, kể cả lỗi 422 của FastAPI.
- `haido_core/domain/display_policy.py` chỉ import thư viện chuẩn.
- `haido_core/domain/envelope.py` chỉ import thư viện chuẩn, `pydantic` và `display_policy`. Không import `fastapi` hay bất cứ gì trong `haido_api`.

**Never:**
- Không cài phép chọn ô / quay về (phép 2 của registry, thuộc #3/#17). `fallback_label` lấy nguyên văn từ fixture.
- Không tạo enum vai trò, cấp bậc, thành phố trong `domain/` (thuộc #16). Dùng chuỗi snake_case tạm, chỉ fixture biết.
- Không chạm Postgres/Alembic, không viết code `web/`, không thêm route ngoài hai route, không sửa GitHub issue.
- Không sửa `tools/gates/check_gates.py`. Code của #2 phải qua cổng như nó đang viết.

**Quyết định (04/11/2026; quyết định đầu đổi ngày 05/11/2026):**
- Model envelope (`Stat`, `CellMeta`, `Thresholds`, `CoverageNote`, `Meta`, `Envelope[T]`) cùng validator của chúng nằm ở `haido_core/domain/envelope.py`, cạnh `display_policy.py`. Validator của envelope là một phần luật hiển thị, mà AD-17 đòi luật này có một bản cài đặt. Cách đặt này khớp task đầu của issue #2 và cổng AD-17. AD-1 vẫn giữ: `haido_api` import từ `domain` là đúng chiều, và Pydantic không làm I/O. Phần riêng của tầng HTTP ở lại `haido_api/schemas/`: phần `data` của từng route và `ErrorEnvelope`. Quyết định này thay quyết định ngày 04/11 (đặt cả envelope ở `haido_api/schemas/`); xem Spec Change Log.
- #2 tự dựng khung Python tối thiểu trên nhánh `gh-2-envelope-meta` và báo Dyuedu. Chỉ tạo phần #2 cần; `web/`, `deploy/`, Alembic và các thư mục `haido_core/` khác vẫn để #1 làm.
- Giữ nguyên phạm vi, kể cả hình lỗi và ảnh chụp OpenAPI, dù spec dài hơn mức khuyến nghị.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Đủ mẫu + mẫu nhỏ | `GET /api/v1/city-shares?role=data_ai` | Hà Nội n=412 `shown`; Đà Nẵng n=21 `low_sample_shown`, vẫn có `value`; các dòng `other`, `unknown` riêng; tổng `share` = 1 | N/A |
| Quay về ô rộng | `GET /api/v1/skill-rates?role=java_backend&level=entry` | Ô Backend × entry n=52, `fallback_label` nêu Java Backend chỉ có 26 tin, `seniority_mix` = intern 13, fresher 7, junior 32 | N/A |
| `null_data` | `GET /api/v1/skill-rates?role=data_engineer&level=senior` (n=18) | Mọi `rate.value = null`, `display = null_data`, `group = null` | N/A |
| Biên ngưỡng | `suppression_for` với n = 29, 30, 0 | 30 → `shown`; 29 → `null_data`, riêng `composition_share` → `low_sample_shown`; n = 0 như 29 | n < 0 → `ValueError` |
| Hợp đồng vỡ | Envelope thiếu `meta`; `Stat.cell_id` không có trong `meta.cells`; `low_sample_shown` với kind khác `composition_share`; `null_data` mà `value` khác null | `ValidationError` | N/A |
| Không có ô | `role=khong_ton_tai` | 404, `code = unknown_cell` | Hình lỗi chuẩn |
| Thiếu tham số | `skill-rates` thiếu `level` | 422, `code = invalid_query`, không còn `{"detail": …}` | Hình lỗi chuẩn |

</frozen-after-approval>

## Code Map

Chưa có code `haido_*` nào. `scraper/` có job CI riêng, không liên quan và không được đụng tới. Đường dẫn dưới đây theo cây ở spine §Cây mã nguồn.

Khi `pyproject.toml` xuất hiện ở gốc repo, job `Python - ruff and pytest` trong `.github/workflows/ci.yml` tự bật và chạy `uv run ruff check .` cùng `uv run pytest -q` **từ gốc repo**. Gốc repo hiện có 12 file kiểm thử trong `scraper/tests/` và `.claude/skills/*/scripts/tests/`, cùng hơn 50 file `.py` ngoài `haido_*`. Môi trường `uv` của #2 không chạy được chúng, nên `pyproject.toml` phải giới hạn phạm vi quét.

- `pyproject.toml`, `haido_core/__init__.py`, `haido_core/domain/__init__.py`, `haido_api/__init__.py`, `tests/` -- mới: khung tối thiểu. Python 3.13 qua `uv` (đã cài 3.13.13). Phụ thuộc: `fastapi`, `pydantic`, `uvicorn`; dev: `pytest`, `httpx`, `ruff`. Phiên bản theo bảng Stack của spine. Cấu hình: `[tool.pytest.ini_options]` có `testpaths = ["tests"]` và khai marker `determinism`; `[tool.ruff]` có `extend-exclude = ["scraper", ".claude", "_bmad", "_bmad-output", "tools"]`. Loại `tools/` vì `check_gates.py` có 21 lỗi với bộ luật mặc định của ruff 0.17.3 (kiểm 05/11: UP031, FURB167, BLE001, UP009), mà #2 không được sửa file đó
- `haido_core/domain/display_policy.py` -- mới: `MeasureKind` (`composition_share`, `skill_rate`, `percentile`), `DisplayState` (`shown`, `low_sample_shown`, `null_data`), `suppression_for(measure_kind, n, *, min_sample)`
- `haido_core/domain/envelope.py` -- mới: `Stat`, `CellMeta`, `Thresholds`, `CoverageNote`, `Meta`, `Envelope[T]` (cú pháp PEP 695) và validator. Cổng AD-17 tìm chữ `Envelope` và tám tên trường (`snapshot_date`, `snapshot_status`, `sources`, `sources_failed`, `thresholds`, `coverage_notes`, `n_by_measure`, `insufficient_by_measure`) trong `domain/`, nên giữ đúng tên trường như AD-17
- `haido_api/schemas/market.py` -- mới: `CitySharesData`, `SkillRatesData`
- `haido_api/schemas/error.py` -- mới: `ErrorEnvelope`
- `haido_api/market_source.py` -- mới: `MarketReadModel` (Protocol) và lỗi `UnknownCell`. Nguồn chọn riêng cho từng phép: Story 1.21 cài bản thật cho `city_shares` ngay trong Sprint 1, #27 cài bản thật cho `skill_rates` ở Sprint 3 (đề xuất đổi sprint 05/11)
- `haido_api/fake_market.py` + `haido_api/fixtures/fake_market.json` -- mới: bản giả; tính `display` bằng `suppression_for` từ `n` trong fixture
- `haido_api/routes/market.py`, `haido_api/errors.py`, `haido_api/main.py` -- mới: hai route, bộ xử lý lỗi, app
- `tools/gates/check_gates.py` -- không sửa. Khi #2 thêm `haido_core/domain/` và `haido_api/`, các cổng AD-1, AD-17, AD-7, AD-11/18 và FR-25/31/47 chuyển từ SKIP sang chạy thật. Fixture `.json` trong `haido_api/` cũng bị cổng câu chữ bị cấm quét
- Issue #27 -- trùng 4 task với #2. Sau khi #2 merge, #27 chỉ còn "cài `MarketReadModel` thật cho `skill_rates`"; phần `city_shares` thuộc Story 1.21

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml` và các file `__init__.py` -- tạo nhánh `gh-2-envelope-meta` từ `main`, dựng khung tối thiểu kèm cấu hình `pytest` và `ruff` ở Code Map; `uv sync` chạy được -- #1 chưa có, xem Quyết định; job Python của CI không được quét `scraper/` hay `.claude/`
- [x] `haido_core/domain/display_policy.py` -- viết enum và `suppression_for` -- nguồn duy nhất quyết che số (DoD dòng 3)
- [x] `haido_core/domain/envelope.py` -- viết model và validator: `null_data` ⇒ `value` null; `low_sample_shown` ⇒ kind là `composition_share`; mọi `Stat` trong `data` có ô trong `meta.cells` -- AD-17 "một con số không có mục ô là lỗi schema"; luật hiển thị nằm một chỗ trong `domain`
- [x] `haido_api/schemas/market.py`, `haido_api/schemas/error.py` -- viết hai model `data` theo ví dụ ở Design Notes, và `ErrorEnvelope`; `total_cell_id` cũng phải có trong `meta.cells` -- hình dữ liệu của hai route
- [x] `haido_api/market_source.py`, `haido_api/fake_market.py`, `haido_api/fixtures/fake_market.json` -- viết interface, bản giả và fixture phủ đủ các dòng của I/O Matrix -- #27 thay bản cài đặt mà không đổi route
- [x] `haido_api/routes/market.py`, `haido_api/errors.py`, `haido_api/main.py` -- dựng route với `response_model=Envelope[...]`, chọn nguồn riêng cho từng phép qua `HAIDO_MARKET_SOURCE_CITY_SHARES` và `HAIDO_MARKET_SOURCE_SKILL_RATES` (mặc định `fake`), bắt lỗi về hình chuẩn -- AC "không sửa giao diện"
- [x] `tests/domain/test_ad17_display_policy.py`, `tests/domain/test_ad17_envelope.py`, `tests/api/test_ad17_routes.py` -- kiểm mọi dòng của I/O Matrix: dòng "Biên ngưỡng" ở `display_policy`, dòng "Hợp đồng vỡ" ở `envelope`, các dòng còn lại qua route -- DoD dòng 11
- [x] `docs/api/envelope-meta.md`, `docs/api/openapi.json` -- mô tả hợp đồng cho người làm web, kèm OpenAPI chụp từ `app.openapi()` -- task "ghi vào docs/"

**Acceptance Criteria:**
- Given app chạy với nguồn giả, when kiểm thử duyệt mọi route dưới `/api/v1`, then mỗi route có `response_model` là một `Envelope[...]`, và response thật của nó qua được validator.
- Given `docs/api/openapi.json` đã commit, when schema trong code đổi mà file chưa sinh lại, then một kiểm thử đỏ.
- Given `display_policy.py` và `envelope.py`, when kiểm thử đọc các import của chúng, then `display_policy.py` chỉ có thư viện chuẩn, còn `envelope.py` chỉ có thư viện chuẩn, `pydantic` và `display_policy`.
- Given nhánh của #2, when chạy `python tools/gates/check_gates.py --require AD-1 AD-17`, then AD-1 và AD-17 là PASS, và không cổng nào FAIL.

## Implementation Notes

- Nhánh `gh-2-envelope-meta` tạo từ `main` tại `baseline_commit`. Thêm `.python-version` (3.13) và `uv.lock`; `pytest` có `pythonpath = ["."]` vì project không có build backend.
- Luật thêm ngoài danh sách của spec, đều suy từ AD-17 hoặc Design Notes:
  - `Stat`: `shown`/`low_sample_shown` thì phải có `value`. Tỷ trọng và tỷ lệ nằm trong 0–1; phân vị không giới hạn.
  - `Envelope`: số trần trong `data` là lỗi. Trường trỏ tới ô ngoài `Stat` khai bằng `CellId` để được kiểm.
  - `CellMeta`: hai dict thước đo cùng tập khóa; `n_by_measure` không vượt `n`.
  - `Thresholds`: `theta_common` không lớn hơn `theta_core`.
  - `Meta`: `published` thì `sources_failed` rỗng.
  - `data` của route: tổng tỷ trọng bằng 1; `group` là `null` đúng khi `rate` là `null_data`.
  - Tham số mã khớp `^[a-z0-9_]+$`, tối đa 64 ký tự.
- `fake_market.json` sinh một lần bằng script nháp (không commit). Tỷ trọng đúng bằng `n` ô / `n` toàn quốc, không làm tròn.
- Lỗi 422, 404/405 sai đường dẫn hay phương thức, và 500 có `snapshot_date = null` vì chưa đọc snapshot nào. Chỉ 404 `unknown_cell` mang ngày snapshot.
- FastAPI 0.162 gắn router con một cách lười. Kiểm thử AC 1 duyệt route qua `fastapi.routing.iter_route_contexts` và đối chiếu với `app.openapi()["paths"]`.
- Starlette `TestClient` báo một cảnh báo khuyên dùng `httpx2`. Giữ `httpx` theo Code Map.
- Đã kiểm: `uv lock --check`; `uv run ruff check .`; `uv run pytest -q` (65 test, chỉ trong `tests/`); `pytest -m determinism`; `check_gates.py --require AD-1 AD-17` (5 PASS, 4 SKIP, 0 FAIL); `uvicorn` + `curl` cho 422 `invalid_query`.

## Spec Change Log

### 2026-11-05 — Đổi chỗ đặt model envelope sang `haido_core/domain/` (người sở hữu spec yêu cầu)

- **Nguyên nhân:** quyết định ngày 04/11 đặt model ở `haido_api/schemas/`. Quyết định đó mâu thuẫn với cổng AD-17 (tìm `Envelope` trong `haido_core/domain/`) và với task đầu của issue #2. #2 phải tạm dừng vì chỗ này (đề xuất đổi sprint 05/11, mục *Cập nhật sau khi duyệt*). Spine không quy định chỗ đặt envelope; cổng AD-1 không cấm `pydantic` trong `domain`.
- **Đã sửa:**
  - Trong khối frozen: quyết định đầu; thêm một dòng Always về import của `envelope.py`; thêm một dòng Never "không sửa `tools/gates/check_gates.py`".
  - Ngoài khối frozen: Code Map, Tasks, AC và Verification theo chỗ đặt mới.
  - Thêm cấu hình `pytest`/`ruff` vào `pyproject.toml`, vì job Python của CI tự bật khi file này xuất hiện.
  - Xóa dòng `</content>` thừa ở cuối file.
- **Tránh được:** sửa cổng CI chung để PR của chính mình qua được; luật hiển thị bị chia ra hai package; CI đỏ vì `pytest` thu thập kiểm thử của `scraper/` và `.claude/skills/`, hoặc vì `ruff` báo lỗi trong `scraper/` và `tools/`.
- **Giữ nguyên:** Intent, I/O Matrix, hai route, hình lỗi, chữ ký `suppression_for(measure_kind, n, *, min_sample)`, việc chọn nguồn riêng cho từng phép, Design Notes.

## Review Triage Log

Lượt 1 (05/11/2026). Lớp: VG = verification-gap, BH = blind-hunter, EC = edge-case-hunter. Không có `intent_gap` hay `bad_spec`.

| ID | Phát hiện | Verdict | Bằng chứng | Hướng |
|---|---|---|---|---|
| VG-1 | Sáu điều kiện của validator trong `schemas/market.py` không có kiểm thử từ chối | medium | Đến từ VG, đã kiểm sẵn: tắt từng điều kiện thì vẫn 65/65 xanh | patch E3 |
| VG-2 | Luật `theta_common ≤ theta_core` không có kiểm thử | low | Đến từ VG: `theta_core = 1.5` bị chặn bởi `le=1`, không phải bởi luật thứ tự | patch E3 |
| VG-3 | Instance sửa bằng `model_copy` không bị kiểm lại; lỗi dựng `Envelope` trong nguồn không thành `invalid_response` | medium | Probe: `model_copy(update={"group": "core"})` trên dòng `null_data` trả 200; `ValidationError` trong nguồn trả 500 `internal_error` | patch E2 |
| VG-4 | Bước CI chạy kiểm thử tất định hai lần có `|| exit 0` | low | `.github/workflows/ci.yml` có sẵn trước thay đổi này; diff chỉ thêm test đầu tiên | defer |
| BH-1 | `Envelope` không kiểm `display` khớp `suppression_for` theo `n` của ô | medium | Probe: `skill_rate` `shown` ở ô n = 18 qua được `Envelope[SkillRatesData]` | patch E1 |
| BH-2 | `CellRef` trong `CellId \| None`, `list[CellId]` không được nhận ra | low | `_walk` chỉ đọc `FieldInfo.metadata`; pydantic không đưa metadata của kiểu lồng lên đó. Ghi chú đã hướng dẫn route sau khai `CellId`, nên sẽ gặp | patch E4 |
| BH-3 | `invalid_response` không bao giờ xảy ra với nguồn đúng Protocol | medium | Trùng gốc với VG-3, probe như trên | patch E2 |
| BH-4 | Thông điệp `unknown_cell` lặp lại giá trị người dùng gửi | low | `fake_market.py` chèn `role`/`level` vào thông điệp, trái docstring `errors.py` | patch E8 |
| BH-5 | `Stat` không biểu diễn được phân vị (thiếu thước đo, thiếu CI) | false | Không route nào sinh `percentile`; thêm trường thước đo sau này là thay đổi cộng thêm, không làm vỡ hai route hiện có | reject |
| BH-6 | `group` không gắn với θ, là chuỗi tự do | low | Probe: 0 chỗ lệch θ trong fixture. Tính nhóm từ θ là phép 4 của registry (#17); enum nhóm trái quyết định mã tạm | reject |
| BH-7a | `partial` với `sources_failed` rỗng được chấp nhận | maybe-false | AD-4 chưa định nghĩa `partial` có bắt buộc nguồn lỗi không; cần #6 (1.4) chốt. Nếu đúng thì chỉ low | reject |
| BH-7b | `sources_failed` không nằm trong `sources` được chấp nhận | maybe-false | Chưa rõ `sources` là nguồn đang bật hay nguồn đóng góp; nếu đúng chỉ low | reject |
| BH-7c | `coverage_notes` rỗng được chấp nhận | low | AD-17 và NFR-9 bắt lưu ý trên mọi màn hình có số; nguồn thật trả `[]` vẫn qua | patch E6 |
| BH-7d | Lưu ý `n_sources` trong fixture không có số N | low | Văn bản ghi "các nguồn đang bật", NFR-9 đòi "trên N nguồn"; giao diện hiện nguyên văn | patch E7 |
| BH-8a | Thiếu trường loại dòng cho `other`/`unknown` | false | `other`, `unknown` là mã có ghi trong hợp đồng; đổi chúng là đổi hợp đồng có chủ ý, không vỡ âm thầm | reject |
| BH-8b | Không bảo đảm luôn có ba thành phố | low | Muốn kiểm phải có danh sách mã thành phố trong `domain`, mà khối frozen cấm (thuộc #16) | reject |
| BH-8c | `rows` rỗng và mã thành phố trùng được chấp nhận | low | Probe xác nhận; sửa trực tiếp được | patch E5 |
| BH-9 | Ô `null_data` vẫn trả kỹ năng theo thứ tự tỷ lệ bị che | low | Fixture `data_engineer/senior`: python 0,89 → kafka 0,39, giảm dần | patch E9 |
| BH-10 | Thiếu id và `n` của ô người dùng chọn; `fallback_label` theo ô | false | Hình này do AD-17 quy định (`fallback_label` trong mục ô), và I/O Matrix đặt số 26 trong nhãn | reject |
| BH-11 | Kiểm thử tất định yếu trong CI | low | Trùng gốc VG-4, nằm ở `ci.yml` có sẵn | defer |
| BH-12 | API không có CORS; tài liệu không chỉ cách web gọi API lúc dev | maybe-false | Cách web gọi API (rewrite của Next.js, Caddy cùng origin, hay CORS) do #1 quyết. Nếu cần CORS thì medium | defer |
| BH-13a | Bảng lỗi thiếu mã `http_error` | low | `_http_error` trả `http_error` cho mã khác 404/405, tài liệu không có dòng này | patch E10 |
| BH-13b | `ErrorBody.code` không là enum trong OpenAPI | low | Ít gặp; sửa phải thêm enum công khai | reject |
| BH-13c | 405 không khai trong OpenAPI | low | Ít gặp; chỉ là mô tả | reject |
| BH-14 | Không có kiểm thử hợp đồng dùng lại cho nguồn thật | low | Sau E1, luật nằm trong `Envelope` và test AC 1 kiểm response qua nó; nguồn thật cần DB, chưa có | reject |
| EC-1 | `CellRef` lồng trong Optional/list | low | Trùng gốc BH-2 | patch E4 |
| EC-2 | `Decimal` và số trong `set`/`frozenset` lọt kiểm số trần | low | `_walk` chỉ xét `int \| float` và `list \| tuple`; sửa trực tiếp | patch E4b |
| EC-3 | `display`/`insufficient_by_measure` không khớp `suppression_for` | medium | Trùng gốc BH-1 | patch E1 |
| EC-4 | `composition_share` với `null_data` được chấp nhận | low | `suppression_for` không bao giờ trả trạng thái này; trùng gốc BH-1 | patch E1 |
| EC-5 | Tổng tỷ trọng bị bỏ qua khi `rows` rỗng hoặc có `value` null | low | `if values and ...` bỏ qua cả hai trường hợp | patch E5 |
| EC-6 | Mã thành phố trùng | low | Trùng gốc BH-8c | patch E5 |
| EC-7 | `partial`/`sources_failed` | maybe-false | Trùng BH-7a, BH-7b | reject |
| EC-8 | `n_by_measure` thiếu khóa bắt buộc | low | Ít gặp; sửa phải thêm hằng tên thước đo trước khi Story 1.12 chốt tập thước đo | reject |
| EC-9 | `group` ngoài tập, không khớp θ | low | Trùng BH-6 | reject |
| EC-10 | Tỷ lệ kỹ năng phải xét `n_by_measure.skill_count` | false | `skill_count` là thước đo phân vị "số kỹ năng" (AD-17, FR-30); tỷ lệ kỹ năng xét `n` của ô (DoD dòng 3, NFR-8) | reject |
| EC-11 | `ValidationError` từ nguồn thành `internal_error` | medium | Trùng gốc VG-3 | patch E2 |
| EC-12 | Thông điệp 404 lặp giá trị người dùng | low | Trùng BH-4 | patch E8 |
| EC-13 | `invalid_response` có `snapshot_date = null` dù đã đọc snapshot | low | Tài liệu nói null chỉ khi chưa đọc snapshot; trùng gốc BH-13a (tài liệu lỗi lệch handler) | patch E10 |
| EC-14 | Mã `http_error` không có trong tài liệu | low | Trùng BH-13a | patch E10 |
| EC-15 | Không có CORS | maybe-false | Trùng BH-12 | defer |
| EC-16 | Luật `group`/`null_data` nằm ngoài `domain` | false | Luật thuộc hình `data` của skill-rates, spec đặt ở `haido_api/schemas/`; quyết định che số vẫn từ `suppression_for` | reject |

## Design Notes

**Vì sao mỗi số là một `Stat`, thay vì một cờ chung cho cả ô:** một ô có thể đủ mẫu cho thước đo này mà thiếu cho thước đo khác (AD-17 `n_by_measure`). Cờ đặt ngay cạnh giá trị thì web chỉ cần một component, không phải suy luận gì (AD-22). Tham khảo:
- Census ACS nhét mã giả `-666666666` vào ô số, buộc người dùng tự soi cột chú thích; ở đây ta dùng `null` kèm trạng thái tường minh.
- CDC WONDER tách hai trạng thái có tên riêng, *Suppressed* và *Unreliable*, tương ứng `null_data` và `low_sample_shown`.
- JSON:API cho phép `meta` ở cả cấp tài liệu lẫn cấp phần tử, và cấm `data` cùng `errors` trong một tài liệu; hình lỗi của ta đã tách riêng.

**Chữ ký `suppression_for`** thêm tham số `min_sample` so với AD-17: `domain` phải thuần và DoD dòng 4 cấm hardcode, nên ngưỡng phải được truyền vào. Mã tạm (`data_ai`, `entry`, `ha_noi`…) chỉ fixture biết; #16 chốt mã thật.

```json
"data": {"role": "data_ai", "total_cell_id": "vn.data_ai",
  "rows": [{"city": "da_nang", "share": {"value": 0.04, "kind": "composition_share",
            "display": "low_sample_shown", "cell_id": "da_nang.data_ai"}}]},
"meta": {"snapshot_date": "2026-11-03", "snapshot_status": "published",
  "sources": ["careerlink", "itnavi", "zalo", "momo"], "sources_failed": [],
  "thresholds": {"min_sample": 30, "theta_core": 0.3, "theta_common": 0.1},
  "coverage_notes": [{"code": "n_sources", "text": "…"}],
  "cells": {"da_nang.data_ai": {"n": 21, "fallback_label": "…", "seniority_mix": {"intern": 2, "junior": 9, "mid": 7, "senior": 3},
            "n_by_measure": {"skill_count": 21, "experience_years": 14, "salary": 5},
            "insufficient_by_measure": {"skill_count": true, "experience_years": true, "salary": true}}}}
```

`cells` là dict khóa theo `cell_id`, một chuỗi opaque. `seniority_mix` là số tin theo cấp chi tiết, đúng ví dụ "13 Intern, 7 Fresher, 32 Junior" của EXPERIENCE.

## Verification

**Commands:**
- `uv run ruff check .` và `uv run pytest -q`, chạy từ gốc repo đúng như CI -- expected: xanh, và không thu thập file nào trong `scraper/` hay `.claude/`
- `python tools/gates/check_gates.py --require AD-1 AD-17` -- expected: AD-1 và AD-17 PASS, `0 failed`
- `uv run uvicorn haido_api.main:app` rồi `curl "localhost:8000/api/v1/skill-rates?role=data_engineer"` -- expected: 422 với `error.code = invalid_query`
