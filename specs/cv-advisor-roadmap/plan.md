# Implementation Plan: Cố vấn lộ trình roadmap.sh từ CV, Level, Vị trí & dữ liệu JD (Hướng B)

**Branch**: `gh-216-lo-trinh-that` | **Date**: 2026-11-27 | **Spec**: [spec.md](spec.md)

## Summary

Mở rộng chức năng **Cố vấn** (`/co-van`) để người dùng upload CV (PDF/DOCX, không file tạm), chọn **Vị trí** (`role`) và **Cấp bậc** (`level`), gửi qua backend FastAPI kết hợp thống kê kỹ năng từ các JD thật của nhà tuyển dụng (`MarketReadModel.skill_rates`) để LLM (hoặc bộ dự phòng tất định theo thị trường khi không có API key) dựng lộ trình từng chặng hiển thị trực tiếp lên sơ đồ `PathGraph` kiểu `roadmap.sh`.

## Technical Context

- **Backend**: Python 3.13, FastAPI 0.162, Pydantic 2.14, `pypdf` (đọc PDF trong RAM), `zipfile` + `xml.etree.ElementTree` (đọc DOCX trong RAM), `httpx` (gọi LLM qua HTTP: Anthropic / OpenAI / Gemini).
- **Frontend**: Next.js 16, React 19, Tailwind 4, TypeScript, tái sử dụng `PathGraph`, `PathNodeCard`, `SkillPanel` và `profile-store.ts`.
- **Constraints**:
  - `AD-1`: Hướng phụ thuộc một chiều (`web` → `haido_api` → `haido_core` → `domain`).
  - `AD-2`: Không thay đổi hay nhân bản 8 phép trong `haido_core/domain/REGISTRY.md`.
  - `AD-7`: Không truy vấn/tổng hợp bảng `job_*` trong `haido_api`; mọi tỷ lệ JD lấy qua `MarketReadModel.skill_rates`.
  - `AD-11`: CV xử lý 100% trong RAM (`haido_api/uploads.py`), không dùng `UploadFile`/`File`/`Form`/`request.form`/`tempfile`, không lưu hay log văn bản CV, không đặt tên biến trùng `bad_cols` của cổng `AD-11`.
  - `AD-17`: Response trả về `Envelope[AdvisorRoadmapData]`, khớp `docs/api/openapi.json` và allowlist `Ordinal`.
  - `AD-23`: `localStorage` chỉ truy cập qua `web/lib/haido-keys.ts`.
  - `FR-25/31/47`: Lọc câu chữ cấm khỏi phản hồi và code.

## Project Structure

```text
haido_core/extract/
├── __init__.py
├── cv_parser.py                  # mới: đọc PDF/DOCX trong BytesIO, phát hiện CV scan (< 30 ký tự)
└── advisor.py                    # mới: trích kỹ năng CV + gọi LLM (hoặc fallback) tạo lộ trình từ JD rates

haido_api/
├── uploads.py                    # mở rộng đọc thêm field chữ có giới hạn (role, level, consent, have)
├── errors.py                     # thêm handler UnreadableCvError -> 422 cv_unreadable, MissingConsentError -> 400
├── schemas/learning_path.py      # thêm AdvisorRoadmapData (bọc LearningPathData + cv_skills + summary + mode)
├── routes/market.py              # thêm POST /api/v1/advisor/roadmap -> Envelope[AdvisorRoadmapData]
└── main.py                       # không đổi hoặc giữ router market

web/
├── app/api/[...path]/route.ts    # thêm handler POST proxy multipart/JSON an toàn
├── app/co-van/page.tsx           # truyền initialLevel từ URL searchParams
├── lib/learning-path-view.ts     # bỏ khóa cứng entry; hỗ trợ level linh hoạt
├── lib/advisor-roadmap.ts        # mới: kiểu + hàm POST /api/v1/advisor/roadmap
└── app/components/advisor/
    ├── learning-path-screen.tsx  # thêm ô chọn Cấp bậc, form upload CV, progress steps, tóm tắt & PathGraph
    └── cv-advisor-form.tsx       # mới: dropzone PDF/DOCX, consent checkbox, tiến trình, tóm tắt khoảng trống

tests/
├── core/test_cv_parser.py        # mới (TDD)
├── core/test_advisor_llm.py      # mới (TDD)
└── api/test_advisor_roadmap.py   # mới (TDD)

web/tests/
└── advisor-cv-roadmap.test.tsx   # mới (TDD)
```
