# Research: Hình response của tin dán ("Soi tin")

Ngày: 2026-11-27. Mục đích: so ý tưởng về hình response của việc đọc một tin tuyển dụng dán vào, khớp với hồ sơ, và kiểm dấu hiệu, trước khi chốt hình của #230. Đọc bằng `gh api` ở commit ghi dưới đây.

## Các repo đã xem

### 1. srbhr/Resume-Matcher (Apache-2.0), commit `959e4587dab33d7ff849d822b8182e11e7669dfc` (2026-11-16)

- Link: <https://github.com/srbhr/Resume-Matcher/tree/959e4587dab33d7ff849d822b8182e11e7669dfc/apps/backend/app>
- Xem: `schemas/models.py`, `mcp_server/tools/set_job_keywords.py`, `routers/jobs.py`.
- **Lấy**: tách hai việc. Bước "đọc tin thành từ khóa" (`set_job_keywords`: từ khóa gắn vào một job đã lưu, do model trích) tách khỏi bước "dùng từ khóa để cải thiện CV". Kết quả đọc là một đối tượng có kiểu (`JobKeywords`), không phải chữ tự do. Điều này khớp quyết định hai bước của #230: bước một ra sự kiện đóng, bước hai chỉ dùng mã.
- **Không lấy**: nó lưu job và từ khóa vào cơ sở dữ liệu (`db.update_job`) và từ khóa là chuỗi tự do. Ta cấm cả hai: AD-11 không lưu chữ của tin, và AD-22 chỉ cho mã của bộ từ vựng lên query.

### 2. AnasAito/SkillNER (MIT), commit `e8cdbb6f591211bf5d0fe2c8a61ddb95526a78b3` (2023-08-22)

- Link: <https://github.com/AnasAito/SkillNER/blob/e8cdbb6f591211bf5d0fe2c8a61ddb95526a78b3/skillNer/skill_extractor_class.py>
- Xem: `SkillExtractor.annotate`, kết quả `results.full_matches` và `results.ngram_scored` (mỗi mục có `skill_id`, `doc_node_value`, `score`, `type`).
- **Lấy**: phân biệt kỹ năng khớp đúng bộ từ vựng (có `skill_id`) với cụm chỉ khớp mờ có điểm; mỗi mục mang cả mã chuẩn lẫn chữ nguyên văn trong tin. Từ đó có hai danh sách trong #230: `skills` (mã của bộ từ vựng, kèm số lần nhắc) và `unrecognised` (chữ nguyên văn, chỉ hiện trên màn, không tính vào mức khớp, đúng FR-29).
- **Không lấy**: điểm khớp mờ (`score`) và vị trí từ trong văn bản (`doc_node_id`): #230 không có model đọc (đó là #232) và vị trí trong chữ dán là dữ liệu của chữ, không được rời cổng đọc.

### 3. ceydaucdirhem/JobGuardAI (không ghi giấy phép), commit `5d2e77b02c363f80d27a522803bdc0b6f2e79354`

- Link: <https://github.com/ceydaucdirhem/JobGuardAI/blob/5d2e77b02c363f80d27a522803bdc0b6f2e79354/README.md>
- Xem: README (không có mã nguồn backend; gọi model ngay trên trình duyệt).
- **Lấy**: ý nêu các nhóm dấu hiệu (uy tín công ty, lời hứa lương, kênh liên hệ, yêu cầu tiền trước) thành danh sách có tên, mỗi dấu hiệu có lời giải thích; và lưu lịch sử quét ở phía người dùng, không phía máy chủ. Từ đó: `checklist` bốn mục cố định và `signs` có mã đóng trong hình `warnings`.
- **Không lấy**: "điểm an toàn 0 đến 100" và mức "Low/Suspicious/High". #126 cấm nói có nên nộp hồ sơ hay không và cấm từ "lừa đảo", nên hình chỉ có sự kiện đã trích (present/absent, trích dẫn) và "hãy tự kiểm tra", không có điểm tổng. Cũng không lấy việc gửi khóa API từ trình duyệt.

### 4. Miru-nalini/Job-Posting-Scam-Detector, commit `04625224078237457ff3a97322e0c4744bf09eb5`

- Link: <https://github.com/Miru-nalini/Job-Posting-Scam-Detector/tree/04625224078237457ff3a97322e0c4744bf09eb5>
- Xem: danh sách file (`model.py`, hai bộ dữ liệu tin thật và tin giả).
- **Không lấy**: bộ phân loại nhị phân thật/giả huấn luyện trên bộ dữ liệu. Không phù hợp: #126 đòi sự kiện kiểm được và "không suy diễn về tin", không phải nhãn.

## Kết luận lấy gì

| Quyết định của #230 | Gốc |
|---|---|
| Hai bước: đọc ra sự kiện đóng, rồi dùng mã | Resume-Matcher (tách trích từ khóa khỏi việc dùng) |
| `skills` theo mã và số lần nhắc, `unrecognised` nguyên văn riêng | SkillNER (`full_matches` và mục chỉ khớp mờ) |
| `warnings` là danh sách mục có tên, không có điểm tổng | JobGuardAI (nhóm dấu hiệu), bỏ điểm tổng theo AC của #126 |
| Không lưu chữ, không ghi log | Quyết định riêng AD-11 (cả ba repo đều lưu hoặc gửi chữ đi nơi khác) |

## Vòng review 2026-11-27: trần cỡ thân của POST

### 4. kaspa-ng/kaspa-rest-server (MIT), commit `e8bb07e003572fada853c785f8d1e22ffbe1265e`

- Link: <https://github.com/kaspa-ng/kaspa-rest-server/blob/e8bb07e003572fada853c785f8d1e22ffbe1265e/helper/LimitUploadSize.py> (file ghi là chép lại từ `fastapi/fastapi#362`, middleware kiểm `Content-Length`).
- **Lấy**: kiểm `Content-Length` trước khi đọc thân và từ chối bằng 413, để thân lớn không bao giờ vào bộ nhớ.
- **Không lấy**: (a) đòi `Content-Length` (411) khi thiếu: client hợp lệ gửi chunked, và `int(header)` không kiểm có thể ném lỗi với chuỗi dài; (b) chỉ tin vào header: một client khai nhỏ rồi gửi nhiều, hoặc gửi chunked, vẫn lọt. Ta làm như `haido_api/uploads.py` (#140) đã làm với CV: kiểm header (và số chữ số của nó), rồi đếm byte lúc đọc và dừng ngay khi vượt trần. Khác `uploads.py`: thân của ta là JSON để FastAPI phân tích nên bộ đếm nằm ở lớp `receive` bọc quanh route (route class của FastAPI), không phải bộ phân tích multipart; vượt trần thì giả vờ client ngắt để lớp đọc thân dừng, rồi đổi lỗi thành 413.
- Không có repo nào làm "cắt kết quả của model trước khi dựng schema" theo cách ta cần (cụm chưa nhận diện 50×60 nhưng kết quả giữ hợp lệ); đó là quy tắc của riêng #230 (`truncate_read`): cắt chữ và danh sách, không đoán số.
