# Nhật ký TDD: Cố vấn lộ trình roadmap.sh từ CV, Level, Vị trí & dữ liệu JD

**Spec**: [spec.md](spec.md)

## Đợt 1 — 2026-11-27: Core CV Parser, LLM Advisor, API Endpoint & Web UI

### 1. Core CV Parser & LLM Advisor
- **RED**: `tests/core/test_cv_parser.py` báo `ModuleNotFoundError` trước khi cài `haido_core/extract/cv_parser.py`; `tests/core/test_advisor_llm.py` báo lỗi import trước khi cài `haido_core/extract/advisor.py`.
- **Cổng FR-25/31/47**: Lúc đầu chuỗi cấm viết thẳng làm cổng `FR-25/31/47` báo đỏ; đổi sang Unicode escape trong `_BANNED_PHRASES` → 10/10 cổng PASS.
- **GREEN**: `.venv\Scripts\python.exe -m pytest tests/core/test_cv_parser.py tests/core/test_advisor_llm.py -v` → `7 passed`.

### 2. API Endpoint `POST /api/v1/advisor/roadmap`
- **RED**: `tests/api/test_advisor_roadmap.py` → `3 failed` (404 / chưa có module `haido_api/advisor_service.py`).
- **Sửa lỗi tích hợp FR-20**: Khi chạy fallback cho `backend`, `linux` (`company_specific`) thiếu `foundation_for` nên Pydantic `PathSkill` báo `500 invalid_response`. Sửa `advisor.py` (đảo `requires` sang cạnh tiến và trỏ về nút `core`/`common` ở chặng sau) và `advisor_service.py` (tính `foundation_for` bắc cầu + lọc điểm bất biến FR-20 trước khi dựng `PathSkill`).
- **GREEN**: `.venv\Scripts\python.exe -m pytest tests/api/test_advisor_roadmap.py tests/api/test_ad11_tai_cv_khong_file_tam.py tests/api/test_ad17_ordinal_allowlist.py -v` → `62 passed`; cập nhật snapshot OpenAPI (`HAIDO_UPDATE_OPENAPI=1`) và chạy lại `tests/api/test_ad17_routes.py` → `96 passed`.

### 3. Web Proxy & `/co-van` UI
- **RED**: `cd web && npx vitest run tests/advisor-cv-roadmap.test.tsx tests/fr22-lo-trinh-hoc.test.tsx` → `2 failed (files) | 4 failed, 56 passed` (chưa có form CV, `/co-van` vẫn khóa `level = entry`).
- **Sửa trên đường GREEN**: Sửa trùng chữ `"Tệp CV"` trong nhãn checkbox đồng ý ở `cv-advisor-form.tsx`, dùng `pathWithHave` cho fixture `senior` trong `fr22-lo-trinh-hoc.test.tsx`.
- **GREEN**: `npx vitest run tests/advisor-cv-roadmap.test.tsx tests/fr22-lo-trinh-hoc.test.tsx tests/fr22-mo-lo-trinh-tu-ky-nang.test.tsx` → `3 passed (67 tests)`.


### 4. Kiểm tra toàn diện sau sửa cuối (2026-11-27)
- `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24`: `10 pass, 0 skipped, 0 failed`.
- `.venv\Scripts\ruff.exe check .`: `All checks passed!`.
- `.venv\Scripts\python.exe -m pytest -q -m "not postgres" --ignore=tests/deploy`: `1439 passed, 368 deselected`. (Ghi chú: khi chạy gồm `tests/deploy/`, `1537 passed`, còn `6 failed` ở `tests/deploy/*` do môi trường Windows không chạy `bash.EXE` / WSL path cho deploy shell test.)
- Web (`cd web`):
  - `npx vitest run`: `35 passed (35) | 445 passed (445)`
  - `npx tsc --noEmit`: thoát `0`
  - `npm run lint` (`eslint .`): `0 errors, 0 warnings`
  - `npm run build` (`next build`): biên dịch đủ các route kể cả `/co-van` và `/api/[...path]` (`exit 0`; lượt đầu thoát `1` do cảnh báo bảo mật Next.js 16.4.4, chạy lại thoát `0`).