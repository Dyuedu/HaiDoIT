# Feature Specification: Cố vấn lộ trình roadmap.sh từ CV, Level, Vị trí & dữ liệu JD (Hướng B)

**Feature Branch**: `gh-216-lo-trinh-that`  
**Created**: 2026-11-27  
**Status**: In Progress (theo yêu cầu người dùng chọn Hướng B ngày 27/11/2026)  
**Input**: Người dùng upload CV (PDF/DOCX), chọn cấp bậc (`level`) và vị trí việc làm mong muốn (`role`), hệ thống (LLM kết hợp dữ liệu yêu cầu kỹ năng từ các JD của nhà tuyển dụng trong lĩnh vực & cấp bậc đó) vạch ra lộ trình học hiển thị theo giao diện `roadmap.sh` (`/co-van`).

> [!IMPORTANT]
> **Thay đổi có chủ đích so với AC/quyết định cũ (đã báo và được người dùng xác nhận chọn Hướng B):**
> - **#134 (`DEC-8`) & #217 AC6**: `/co-van` không còn khóa cứng `level = entry`; người dùng chọn được cấp bậc mong muốn (`entry`, `intern`, `fresher`, `junior`, `mid`, `senior`, `lead`, `all`).
> - **#108 (`Q.1`), #121, #138 (`FR-24`), #139 (`FR-22`)**: Cho phép LLM (khi có API key) tổng hợp cấu trúc chặng, lời giải thích cá nhân hóa (`advisor_summary`, `blurb`) dựa trên CV + thống kê kỹ năng JD thật từ `stat_skill_rates` cho mọi vai trò/cấp bậc, thay vì chỉ giới hạn ở đồ thị soạn sẵn cho `backend`/`data_engineer`. Toàn bộ số liệu thống kê (`rate`, `group`, `n`) vẫn do server gắn từ `MarketReadModel` (`AD-7`, `AD-17`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload CV, chọn vị trí và level để nhận lộ trình roadmap.sh (Priority: P1)

Người dùng mở `/co-van`, chọn **Vị trí việc làm mong muốn** (`role`) và **Cấp bậc** (`level`), tích đồng ý điều kiện xử lý CV, tải lên file CV (PDF hoặc DOCX, tối đa 5 MB). Hệ thống đọc CV trong bộ nhớ, đối chiếu với yêu cầu kỹ năng từ các JD tuyển dụng của `(role, level)` đó, gọi LLM (hoặc bộ phân tích dự phòng khi offline/không có key) để tổng hợp lộ trình từng chặng kiểu `roadmap.sh`, tô sẵn các kỹ năng người dùng đã có từ CV và giải thích các khoảng trống cần học.

**Why this priority**: Đây là luồng lõi mà người dùng yêu cầu trực tiếp.

**Independent Test**: `tests/api/test_advisor_roadmap.py` & `web/tests/advisor-cv-roadmap.test.tsx`.

**Acceptance Scenarios**:

1. **Given** một file CV PDF/DOCX hợp lệ (≥ 30 ký tự có nghĩa), đã tích đồng ý, đã chọn `role` và `level`, **When** gửi yêu cầu tạo lộ trình (`POST /api/v1/advisor/roadmap`), **Then** server đọc file hoàn toàn trong bộ nhớ (không file tạm, không lưu văn bản CV vào DB/log), lấy yêu cầu kỹ năng JD của `(role, level)` từ `MarketReadModel.skill_rates`, sinh lộ trình `stages` hợp lệ theo `LearningPathData` (`Envelope`), gắn `rate` & `group` từ số liệu JD thật, đánh dấu `have = true` cho các kỹ năng có trong CV, và trả về `200` kèm `cv_skills`, `missing_core_skills`, `advisor_summary`, `generation_mode`, `path` và `meta`.
2. **Given** phản hồi `200` từ API, **When** hiển thị trên `/co-van`, **Then** hồ sơ trình duyệt (`haido:profile`) tự cập nhật `role`, `level`, `skills` (`cv_skills` gộp hợp lệ), tóm tắt phân tích CV và sơ đồ `PathGraph` kiểu `roadmap.sh` hiển thị đầy đủ các chặng, trạng thái `Đã xong` / `Đang học`, và bấm vào từng node mở `SkillPanel`.
3. **Given** người dùng chưa tích ô đồng ý hoặc chưa chọn file/vị trí, **When** bấm *"Tạo lộ trình từ CV"*, **Then** hệ thống chặn gửi request lên server và hiển thị thông báo nhắc nhở rõ ràng (`role="alert"`).

### User Story 2 - Chọn level và tương tác trực tiếp trên sơ đồ roadmap.sh (Priority: P1)

Người dùng có thể đổi **Cấp bậc** (`level`) ngay trên `/co-van` (mặc định vẫn là `entry` nếu URL không chỉ định), có thể giữ nguyên hoặc tick/bỏ tick kỹ năng ngay trên từng node của sơ đồ `PathGraph` để cập nhật tiến độ `N/M` và chặng đang học ngay lập tức.

**Why this priority**: Yêu cầu người dùng chỉ định rõ phải chọn được `level` và xem/tương tác kiểu `roadmap.sh`.

**Independent Test**: `web/tests/fr22-lo-trinh-hoc.test.tsx` & `web/tests/advisor-cv-roadmap.test.tsx`.

**Acceptance Scenarios**:

1. **Given** người dùng mở `/co-van?role=backend&level=senior`, **When** trang tải hoặc khi đổi ô Cấp bậc từ `entry` sang `mid`/`senior`, **Then** hệ thống giữ và dùng đúng `level` đã chọn (cả khi gọi `GET /api/v1/learning-path` lẫn khi gửi CV lên `POST /api/v1/advisor/roadmap`).
2. **Given** lộ trình đã tạo từ CV hiển thị trên `PathGraph`, **When** người dùng tick/bỏ tick một kỹ năng trên node, **Then** trạng thái `have`, `have_on_path`, `current_stage` và hồ sơ trình duyệt cập nhật nhất quán mà không bắt upload lại CV.

### User Story 3 - Xử lý lỗi CV scan, file quá cỡ, sai định dạng & chế độ không có LLM key (Priority: P2)

**Acceptance Scenarios**:

1. **Given** file CV > 5 MB hoặc sai định dạng (không phải PDF/DOCX hoặc magic byte sai), **When** tải lên, **Then** bị từ chối ở lớp streaming trước khi đọc hết body (`413` / `415`) và thông báo tiếng Việt.
2. **Given** file PDF/DOCX ảnh scan hoặc rỗng (`< 30` ký tự chữ đọc được), **When** phân tích, **Then** trả `422` `cv_unreadable` ngay mà không gọi LLM, kèm gợi ý xuất PDF có lớp chữ (Word/Canva/Overleaf), dùng DOCX hoặc tự chọn kỹ năng.
3. **Given** môi trường chưa cấu hình LLM API key (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY`) hoặc cấu hình `HAIDO_ADVISOR_MODE=offline`, **When** gọi tạo lộ trình, **Then** hệ thống dùng bộ trích xuất từ vựng song ngữ (`skills_seed.json`) + bộ xếp lộ trình thị trường từ `skill_rates` + `learning_path.json` (nếu có) để vẫn trả về lộ trình `roadmap.sh` hợp lệ với `generation_mode = "market_fallback"`.

## Requirements *(mandatory)*

- **FR-001**: Endpoint `POST /api/v1/advisor/roadmap` nhận `multipart/form-data` (`cv`, `role`, `level`, `consent`) qua `haido_api/uploads.py` (không dùng `UploadFile`, `File(`, `Form(`, `request.form()`, `tempfile`).
- **FR-002**: Parser CV trong `haido_core/extract/cv_parser.py` xử lý PDF (`pypdf` trên `BytesIO`) và DOCX (`zipfile` + `xml.etree.ElementTree` trên `BytesIO`) hoàn toàn trong RAM; không ghi file tạm, không lưu/log nội dung CV (`AD-11`).
- **FR-003**: Generator `haido_core/extract/advisor.py` hỗ trợ gọi LLM qua `httpx` (Anthropic, OpenAI-compatible, Gemini) với prompt bảo vệ trước prompt injection, ràng buộc danh sách mã kỹ năng hợp lệ (`skills_seed.json`) và dữ liệu yêu cầu JD thật của `(role, level)`.
- **FR-004**: Server hậu kiểm mọi output từ LLM: sửa mọi cạnh vòng/ngược chặng thành DAG tăng chặng hợp lệ; ép `rate` và `group` lấy 100% từ `MarketReadModel.skill_rates(role, level)`; thay URL không hợp lệ (`not https://`) hoặc cụm từ cấm (`FR-25/31/47`).
- **FR-005**: Next.js proxy `web/app/api/[...path]/route.ts` hỗ trợ `POST` chuyển tiếp `multipart/form-data` an toàn lên FastAPI (giữ nguyên rule chống path traversal).
- **FR-006**: Giao diện `/co-van` (`LearningPathScreen`) cho phép chọn `Vai trò`, `Cấp bậc` (`level`), upload CV + checkbox đồng ý, hiển thị tiến trình từng bước, tóm tắt đối chiếu CV–JD và sơ đồ `PathGraph` kiểu `roadmap.sh`.

## Success Criteria

- **SC-001**: Toàn bộ Python unit tests (`pytest -q -m "not postgres"`), `ruff check .`, và 10 cổng kiến trúc `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` PASS.
- **SC-002**: Toàn bộ Web Vitest (`npm run test`), `npx tsc --noEmit`, `npm run lint`, và `npm run build` PASS.
- **SC-003**: `docs/api/openapi.json` khớp 100% với `app.openapi()` (`test_ad17_routes.py`).
