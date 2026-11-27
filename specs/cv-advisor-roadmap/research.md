# Research: Tạo lộ trình học kiểu roadmap.sh từ CV, Level, Vị trí & dữ liệu JD bằng LLM

**Date**: 2026-11-27  
**Branch**: `gh-216-lo-trinh-that`

## 1. Tham chiếu các repo GitHub public

Trước khi thiết kế, đã khảo sát các repo và mẫu kiến trúc open-source thực hiện phân tích CV–JD và sinh lộ trình học qua LLM:

1. **`ZeyadElshenawy/SmartCV`** (Python / Django + Groq + Pydantic):
   - Tách 2 pha: (a) parse CV sang schema chuẩn (skills, experience, education), (b) đối chiếu gap và sinh learning path có cấu trúc.
   - **Lấy gì**: Ép schema đầu ra bằng Pydantic; tách pha đọc CV và pha sinh lộ trình để dễ test độc lập và không phụ thuộc văn bản tự do.
   - **Không lấy gì**: Không lưu nội dung CV vào DB; không dùng Django/Groq-only.

2. **`m-lourenco0/resume-analysis-tool`** (FastAPI + LangGraph + structured LLM):
   - Đọc PDF/DOCX thành text trong bộ nhớ (`io.BytesIO` + `pypdf`), dùng structured output để đối chiếu từ khóa thiếu và tính mức độ phù hợp.
   - **Lấy gì**: Đọc PDF/DOCX hoàn toàn qua `BytesIO` trong RAM, không tạo file tạm (`AD-11`).
   - **Không lấy gì**: Không dùng LangGraph hay `UploadFile`/`Form` mặc định của FastAPI vì có thể spill file tạm ra đĩa và vi phạm cổng `AD-11` (`check_gates.py`).

3. **`ahmadkhanraj01/resume-analyzer`** & **`Sajjad-Amjad/Resume-Parser`**:
   - Dùng `with_structured_output` / JSON schema mode để tránh kết quả markdown khó parse, tách rõ danh sách kỹ năng đã có vs. kỹ năng còn thiếu.
   - **Lấy gì**: Trả về JSON cấu trúc chặt gồm `cv_skills`, `advisor_summary`, và `stages` tương thích trực tiếp với schema `LearningPathData` (`PathGraph` kiểu `roadmap.sh` của Hải Đồ IT).
   - **Không lấy gì**: Không để LLM tự bịa phần trăm thị trường hay tỷ lệ xuất hiện kỹ năng — toàn bộ `rate` và `group` (`core` / `common`) phải ghép từ `stat_skill_rates` / `MarketReadModel` của Hải Đồ IT (`AD-7`, `AD-17`).

## 2. Quyết định kiến trúc cho Hải Đồ IT (Hướng B)

- **Parser CV không file tạm**: Tái sử dụng `haido_api/uploads.py` (`read_cv_upload`, streaming multipart trong RAM, trần 5 MB, kiểm tra magic bytes) và bổ sung đọc bytes thuần trong `haido_core/extract/cv_parser.py` (`pypdf.PdfReader(io.BytesIO(...))` cho PDF; `zipfile` + `xml.etree.ElementTree` cho DOCX).
- **Trích & Tổng hợp lộ trình với LLM (`haido_core/extract/advisor.py`)**:
  - Hỗ trợ đa nhà cung cấp qua `httpx` (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY` / `HAIDO_LLM_BASE_URL`, `GEMINI_API_KEY`) và có fallback tất định dựa trên từ vựng song ngữ (`skills_seed.json`) + đồ thị/tỷ lệ thị trường khi chưa cấu hình API key hoặc ở chế độ offline/test.
  - Đầu ra LLM được validate, sửa DAG tiên quyết (đảm bảo cạnh `prerequisite_for` luôn trỏ sang chặng sau, không chu trình), gắn `Stat` + `group` từ `MarketReadModel.skill_rates(role, level)`, kiểm câu chữ cấm (`FR-25/31/47`), và tính `have`, `have_on_path`, `current_stage`, `foundation_for` bằng `haido_api/learning_path.py`.
- **UI kiểu `roadmap.sh` (`/co-van`)**:
  - Tái sử dụng `PathGraph`, `PathNodeCard`, `SkillPanel` (`#217`), mở khóa chọn `level` (thay đổi `DEC-8` `#134` theo yêu cầu người dùng), thêm form upload CV + checkbox đồng ý + tiến trình xử lý + phần tóm tắt CV/khoảng trống phía trên sơ đồ `roadmap.sh`.
