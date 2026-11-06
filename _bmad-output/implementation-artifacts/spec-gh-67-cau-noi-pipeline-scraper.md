---
title: 'GH-67 [C-11] Hoàn tất cầu nối pipeline scraper/: UA có liên hệ, dedupe chỉ đọc dữ liệu đã redact, ghi lại AD-20 và AD-21'
type: 'chore'
created: '2026-11-06'
status: 'done'
baseline_commit: '0fb4611d3894a144c371db21bd99a770c3595620'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/planning-artifacts/DOD.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Nhịp một đã chạy hằng ngày trên VPS nhưng User-Agent chưa có địa chỉ liên hệ, và `dedupe.py` mặc định vẫn đọc `data/raw`, nên chạy tay không tham số thì dữ liệu chưa `redact` có thể đi tới `extract`. Spine AD-20 còn ghi ITviec và MoMo phải hỏi `robots.txt`, trái với quyết định mới.

**Approach:** Thêm email vào `USER_AGENT`, đổi mặc định của `dedupe.py` sang `data/redacted` kèm test cho cả chuỗi, và ghi quyết định ngày 06/11/2026 vào AD-20 và AD-21.

**Quyết định của người dùng (06/11/2026):**
- Crawler trình duyệt không cần hỏi `robots.txt`: bỏ task ITviec và trang danh sách MoMo.
- Không cần xóa file thô sau `ingest`: bỏ task xóa và AC tương ứng.
- Email liên hệ là `hoangduy20407@gmail.com`, ghi thẳng trong `polite.py`, dù repo public.

## Boundaries & Constraints

**Always:**
- Tên test chứa mã FR hoặc AD (DoD 11).
- AD-20 và AD-21 ghi rõ ngày, phạm vi và phần code hiện tại không làm. Không tự thêm lý do mà người dùng chưa nêu.
- AD-21 phải nói rõ `data/raw` còn chứa liên hệ chưa xóa, và chỉ `redact` mới được đưa dữ liệu đó đi tiếp.

**Never:**
- Không commit thay đổi đang có sẵn ở `deploy/topcv-manual.sh`, và không sửa file này.
- Không đổi `PoliteClient.allowed()` hay việc `get`/`post` kiểm `robots.txt`: các crawler HTTP giữ nguyên.
- Không sửa `itviec.py`, `momo.py`, `redact.py`, `ingest.py`.
- Không sửa PRD, `epics.md`, `WORK-SPLIT.md` trong item này; chỗ lệch được ghi vào `deferred-work.md`.
- Không gỡ cầu nối, vì việc đó chờ Story 1.3. PR dùng `Refs #67`, không đóng issue.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Dedupe mặc định | raw có email và số điện thoại, đã chạy `redact` | `data/dedup.jsonl` không khớp mẫu email hay số điện thoại Việt Nam | N/A |
| Chưa chạy redact | raw có dữ liệu, không có `data/redacted` | `dedup.jsonl` rỗng, không có dòng nào từ raw | N/A |
| Truyền `--raw` tường minh | `--raw <thư mục>` | Đọc đúng thư mục đó, như cũ | N/A |

</frozen-after-approval>

## Code Map

- `scraper/crawlers/polite.py:15` -- `USER_AGENT`. `browser_polite.py` dùng lại hằng này nên Playwright tự có email. `rp.can_fetch` chỉ so phần tên trước `/`, nên thêm email không đổi kết quả robots.
- `scraper/dedupe.py:43` -- default `--raw` đổi sang `data/redacted`. `pipeline.run_dedupe` và Makefile đã truyền đúng, không cần sửa.
- `scraper/extract.py:49` -- `IN_CANDIDATES` chỉ đọc đầu ra của dedupe/clean, không đổi. Test khóa điều này.
- `scraper/tests/test_observations.py` -- fixture `workdir` chdir vào thư mục tạm; `redact.main()` và `dedupe.main()` dùng đường dẫn tương đối nên gọi được trực tiếp sau khi đặt `sys.argv`.
- `_bmad-output/planning-artifacts/architecture/architecture-HaiDoIT-2026-11-03/ARCHITECTURE-SPINE.md:228` -- câu cuối của AD-20 ("Crawler dùng trình duyệt cũng phải hỏi...") là chỗ cần sửa. AD-21 ở dòng 230-235. Cập nhật `updated` ở frontmatter.

## Tasks & Acceptance

**Execution:**
- [x] `scraper/tests/test_observations.py` -- thêm test đỏ trước cho I/O Matrix, UA có email (FR-2), `IN_CANDIDATES` không trỏ vào raw (AD-21) -- TDD
- [x] `scraper/crawlers/polite.py` -- thêm email vào `USER_AGENT` -- FR-2
- [x] `scraper/dedupe.py` -- default đọc `data/redacted` -- `extract` chỉ nhận dữ liệu đã redact
- [x] `ARCHITECTURE-SPINE.md` -- ghi quyết định vào AD-20 và AD-21 -- yêu cầu của người dùng
- [x] `scraper/README.md` -- ghi `data/raw` được giữ lại và còn liên hệ chưa xóa -- DoD 14
- [x] `_bmad-output/implementation-artifacts/deferred-work.md` -- ghi chỗ lệch với PRD FR-2, FR-5, AC Story 1.2, `WORK-SPLIT.md:48`, và việc gỡ cầu nối chờ Story 1.3 -- ngoài phạm vi item này

**Acceptance Criteria:**
- Given crawler HTTP hoặc trình duyệt, when gửi request hoặc mở trang, then User-Agent có email liên hệ.
- Given spine sau khi sửa, when đọc AD-20 và AD-21, then thấy đúng quyết định ngày 06/11/2026 và không còn yêu cầu crawler trình duyệt hỏi `robots.txt`.

## Implementation Notes

Claude làm trực tiếp, không dùng `agy`: cấu hình worker cấm ghi vào `scraper/`, người dùng chọn cách này ngày 06/11/2026. Issue #67 đã được sửa trên GitHub theo quyết định của người dùng.

## Spec Change Log

## Review Triage Log

| Phát hiện | Verdict | Route | Bằng chứng |
|---|---|---|---|
| Test UA trình duyệt chỉ so hằng số với chính nó (VG, Blind) | medium | patch | Đúng: xóa `user_agent=` ở `browser_polite.py:37` thì test vẫn xanh. Đã viết lại với Playwright giả. |
| Chuỗi AD-21 chưa kiểm `clean`, bước `extract` đọc đầu tiên (VG, Blind) | medium | patch | Đúng: test dừng ở `dedup.jsonl`. Đã nối thêm `clean.main()`. |
| Lệnh dedupe hằng ngày và default của `ingest` không có test (VG) | medium | patch | Đúng: `pipeline.py:117` và `ingest.py:197` đổi sang raw thì không test nào đỏ. Đã thêm hai test. |
| AD-21 tự mâu thuẫn với "trước mọi lệnh ghi" (Blind) | medium | patch | Đúng. Đã ghi rõ là ngoại lệ. |
| AD-20 mở đầu tuyệt đối rồi mới miễn trừ (Blind, Edge) | low | patch | Đúng. Đã ghi rõ là ngoại lệ. |
| README nói crawler dựng tập đã biết từ raw, nhưng ba nguồn xóa raw đầu lượt (Edge) | low | patch | Đúng: `momo.py:80`, `vietnamworks.py:102`, `zalo.py:69`. Đã sửa câu chữ. |
| Docstring và README còn mô tả sai đầu vào của dedupe, `data/raw` (Blind) | low | patch | Đúng. Đã sửa câu chữ; không đổi tên cờ `--raw` vì Makefile và pipeline đang dùng. |
| `data/raw` không có thời hạn giữ, chưa nối FR-47 (Blind) | medium | defer | Đúng, và code chưa từng xóa raw. Đã ghi `deferred-work.md`. |
| Ngoại lệ robots không nằm trong `crawl_exceptions`; `WORK-SPLIT.md:63` lệch (Blind) | medium | defer | Đúng; bảng chưa tồn tại. Đã ghi `deferred-work.md` cho Story 1.2. |
| Đường trình duyệt thiếu trần request và kiểm 403/429 (Blind) | medium | defer | Đúng, có từ trước #67. Đã ghi `deferred-work.md`. |
| File dedup hoặc consolidated cũ có thể dựng từ raw (Blind, Edge) | maybe-false | defer | Cần đếm dòng khớp mẫu trên từng máy. Đã ghi `deferred-work.md`, mức medium chưa xác minh. |
| AC UA không đúng với TopCV và LinkedIn (VG, Blind, Edge) | low | reject | Có thật: TopCV không đặt UA, LinkedIn dùng `SAFARI_UA`; cả hai ngoài lịch tự động. Cách sửa là đổi AC của spec nên bị loại theo quy tắc; báo người dùng. |
| `--raw data/raw` tường minh vẫn đưa liên hệ đi tiếp (Blind, Edge) | low | reject | Ma trận đã chốt `--raw` tường minh đọc đúng thư mục đó, nên intent loại trừ guard; báo người dùng. |
| Dedupe thiếu input vẫn exit 0 và ghi file rỗng (Blind, Edge) | low | reject | Ma trận đã chốt `dedup.jsonl` rỗng; lịch chạy luôn có `data/redacted`. |
| Crawl tay rồi dedupe bỏ qua redact dùng dữ liệu cũ (Edge) | low | reject | Có thật nhưng hiếm, cách sửa phải thêm guard theo mtime. |
| Test chỉ phủ email và phone, thiếu tên và Zalo (Blind) | false | reject | `test_redact_removes_contact_details` đã phủ đủ bốn loại ngay trên `redact`. |
| Email hard-code hai lần; tên test ghi "team" (Blind) | low | reject | Test cố ý khóa địa chỉ người dùng đã chọn; sửa chỉ làm test lỏng hơn. |
| Diff thiếu spec được `deferred-work.md` trích dẫn (Blind) | false | reject | Spec bị cố ý bỏ khỏi diff review và sẽ được commit cùng thay đổi; `topcv-manual.sh` sẽ được loại khi stage. |

## Verification

**Commands:**
- Tạo venv riêng rồi `pip install -r scraper/requirements-vps.txt pytest`, như job `scraper` của CI, vì `.venv` gốc thiếu `requests` và `scraper/.venv` thiếu `pytest`. Sau đó `cd scraper && <venv>/python -m pytest tests -q` -- expected: toàn bộ pass; test cần Postgres chỉ skip khi không có `TEST_DATABASE_URL`, và CI vẫn chạy chúng
