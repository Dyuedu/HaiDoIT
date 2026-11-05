---
title: 'GH-2 [C-1] Chốt envelope meta và endpoint dữ liệu giả'
type: 'chore'
created: '2026-11-04'
status: 'draft'
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

**Never:**
- Không cài phép chọn ô / quay về (phép 2 của registry, thuộc #3/#17). `fallback_label` lấy nguyên văn từ fixture.
- Không tạo enum vai trò, cấp bậc, thành phố trong `domain/` (thuộc #16). Dùng chuỗi snake_case tạm, chỉ fixture biết.
- Không chạm Postgres/Alembic, không viết code `web/`, không thêm route ngoài hai route, không sửa GitHub issue.

**Quyết định (04/11/2026):**
- Pydantic model nằm ở `haido_api/schemas/`. Phần thuần (`MeasureKind`, `DisplayState`, `suppression_for`) nằm ở `haido_core/domain/`. Giữ AD-1; lệch có chủ đích với dòng task đầu của issue.
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

Chưa có code `haido_*` nào. Code duy nhất là `scraper/`, không liên quan và không được đụng tới. Đường dẫn dưới đây theo cây ở spine §Cây mã nguồn.

- `pyproject.toml`, `haido_core/__init__.py`, `haido_core/domain/__init__.py`, `haido_api/__init__.py`, `tests/` -- mới: khung tối thiểu. Python 3.13 qua `uv` (đã cài 3.13.13). Phụ thuộc: `fastapi`, `pydantic`, `uvicorn`; dev: `pytest`, `httpx`. Phiên bản theo bảng Stack của spine
- `haido_core/domain/display_policy.py` -- mới: `MeasureKind` (`composition_share`, `skill_rate`, `percentile`), `DisplayState` (`shown`, `low_sample_shown`, `null_data`), `suppression_for(measure_kind, n, *, min_sample)`
- `haido_api/schemas/envelope.py` -- mới: `Stat`, `CellMeta`, `Thresholds`, `CoverageNote`, `Meta`, `Envelope[T]` (cú pháp PEP 695), `ErrorEnvelope`
- `haido_api/schemas/market.py` -- mới: `CitySharesData`, `SkillRatesData`
- `haido_api/market_source.py` -- mới: `MarketReadModel` (Protocol) và lỗi `UnknownCell`. Nguồn chọn riêng cho từng phép: Story 1.21 cài bản thật cho `city_shares` ngay trong Sprint 1, #27 cài bản thật cho `skill_rates` ở Sprint 3 (đề xuất đổi sprint 05/11)
- `haido_api/fake_market.py` + `haido_api/fixtures/fake_market.json` -- mới: bản giả; tính `display` bằng `suppression_for` từ `n` trong fixture
- `haido_api/routes/market.py`, `haido_api/errors.py`, `haido_api/main.py` -- mới: hai route, bộ xử lý lỗi, app
- Issue #27 -- trùng 4 task với #2. Sau khi #2 merge, #27 chỉ còn "cài `MarketReadModel` thật cho `skill_rates`"; phần `city_shares` thuộc Story 1.21

## Tasks & Acceptance

**Execution:**
- [ ] `pyproject.toml` và các file `__init__.py` -- tạo nhánh `gh-2-envelope-meta` từ `main`, dựng khung tối thiểu; `uv sync` chạy được -- #1 chưa có, xem Quyết định
- [ ] `haido_core/domain/display_policy.py` -- viết enum và `suppression_for` -- nguồn duy nhất quyết che số (DoD dòng 3)
- [ ] `haido_api/schemas/envelope.py` -- viết model và validator: `null_data` ⇒ `value` null; `low_sample_shown` ⇒ kind là `composition_share`; mọi `Stat` trong `data` có ô trong `meta.cells` -- AD-17 "một con số không có mục ô là lỗi schema"
- [ ] `haido_api/schemas/market.py` -- viết hai model `data` theo ví dụ ở Design Notes; `total_cell_id` cũng phải có trong `meta.cells` -- hình dữ liệu của hai route
- [ ] `haido_api/market_source.py`, `haido_api/fake_market.py`, `haido_api/fixtures/fake_market.json` -- viết interface, bản giả và fixture phủ đủ các dòng của I/O Matrix -- #27 thay bản cài đặt mà không đổi route
- [ ] `haido_api/routes/market.py`, `haido_api/errors.py`, `haido_api/main.py` -- dựng route với `response_model=Envelope[...]`, chọn nguồn riêng cho từng phép qua `HAIDO_MARKET_SOURCE_CITY_SHARES` và `HAIDO_MARKET_SOURCE_SKILL_RATES` (mặc định `fake`), bắt lỗi về hình chuẩn -- AC "không sửa giao diện"
- [ ] `tests/domain/test_ad17_display_policy.py`, `tests/api/test_ad17_envelope.py` -- kiểm mọi dòng của I/O Matrix -- DoD dòng 11
- [ ] `docs/api/envelope-meta.md`, `docs/api/openapi.json` -- mô tả hợp đồng cho người làm web, kèm OpenAPI chụp từ `app.openapi()` -- task "ghi vào docs/"

**Acceptance Criteria:**
- Given app chạy với nguồn giả, when kiểm thử duyệt mọi route dưới `/api/v1`, then mỗi route có `response_model` là một `Envelope[...]`, và response thật của nó qua được validator.
- Given `docs/api/openapi.json` đã commit, when schema trong code đổi mà file chưa sinh lại, then một kiểm thử đỏ.
- Given `display_policy.py`, when kiểm thử đọc các import của nó, then chỉ thấy thư viện chuẩn.

## Implementation Notes

## Spec Change Log

## Review Triage Log

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
- `uv run pytest tests -q` -- expected: mọi kiểm thử xanh
- `uv run uvicorn haido_api.main:app` rồi `curl "localhost:8000/api/v1/skill-rates?role=data_engineer"` -- expected: 422 với `error.code = invalid_query`
</content>
