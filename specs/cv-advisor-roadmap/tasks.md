# Tasks: Cố vấn lộ trình roadmap.sh từ CV, Level, Vị trí & dữ liệu JD

**Input**: `specs/cv-advisor-roadmap/spec.md`, `plan.md`, `data-model.md`

## Phase 1: Setup & Dependencies
- [x] T001 Thêm `pypdf` và đưa `httpx` vào `dependencies` của `pyproject.toml` + `uv.lock`
- [x] T002 Mở rộng `haido_api/uploads.py` hỗ trợ đọc kèm các trường text giới hạn kích thước (`role`, `level`, `consent`, `have`) vẫn tuân thủ `AD-11`

## Phase 2: Core CV Parser & LLM Advisor (TDD)
- [x] T003 [TDD RED→GREEN] Viết `tests/core/test_cv_parser.py` và cài `haido_core/extract/cv_parser.py` (đọc PDF/DOCX trong `BytesIO`, phát hiện CV scan < 30 ký tự)
- [x] T004 [TDD RED→GREEN] Viết `tests/core/test_advisor_llm.py` và cài `haido_core/extract/advisor.py` (prompt + LLM adapters qua `httpx` + fallback tất định + hậu kiểm DAG/tỷ lệ/cấm từ)

## Phase 3: API Endpoint & OpenAPI (TDD)
- [x] T005 [TDD RED→GREEN] Viết `tests/api/test_advisor_roadmap.py` và cài `AdvisorRoadmapData`, lỗi `cv_unreadable`/`cv_consent_required`, route `POST /api/v1/advisor/roadmap` trong `haido_api/`
- [x] T006 Cập nhật `tests/api/test_ad17_routes.py`, `docs/api/envelope-meta.md` và sinh lại `docs/api/openapi.json`

## Phase 4: Web Proxy & `/co-van` UI (TDD)
- [x] T007 Thêm `POST` multipart/JSON handler vào `web/app/api/[...path]/route.ts`
- [x] T008 [TDD RED→GREEN] Viết `web/tests/advisor-cv-roadmap.test.tsx`, cập nhật `web/tests/fr22-lo-trinh-hoc.test.tsx` (mở khóa chọn `level`), tạo `web/lib/advisor-roadmap.ts` + `web/app/components/advisor/cv-advisor-form.tsx`, cập nhật `web/app/co-van/page.tsx` & `learning-path-screen.tsx`

## Phase 5: Specs Sync & Full Verification
- [x] T009 Cập nhật `specs/217-man-lo-trinh/`, và hoàn tất `specs/cv-advisor-roadmap/tdd.md`
- [x] T010 Chạy đủ Python `pytest`, `ruff check .`, 10 cổng `tools/gates/check_gates.py`, và Web `vitest`, `tsc`, `eslint`, `next build`
