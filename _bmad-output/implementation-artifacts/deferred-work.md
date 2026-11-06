# Việc hoãn

- source_spec: `_bmad-output/implementation-artifacts/spec-gh-2-chot-envelope-meta-endpoint-du-lieu-gia.md`
  summary: Chưa chốt cách web gọi API lúc dev và lúc chạy thật (rewrite của Next.js, Caddy cùng origin, hay CORS); app hiện không có CORS, preflight `OPTIONS` nhận 405.
  evidence: Chưa kiểm được có cần CORS hay không vì #1 chưa dựng `web/` và Compose. Nếu web gọi thẳng `:8000` từ trình duyệt thì mức medium. Thuộc #1 (1.1).
  status: Đã giải quyết ở GH-1 bằng route handler cùng origin (`app/api/[...path]/route.ts`), không cần CORS.

- source_spec: none
  summary: Story 1.20 (#68) — phép phân loại tất định gán vai trò, cấp bậc và thành phố, loại tin không thuộc IT.
  evidence: Tách khỏi #3 vì có thể review và merge riêng sau khi chữ ký phép 6 trong REGISTRY.md tồn tại.

- source_spec: none
  summary: Story 1.4 (#6) — snapshot `YYYY-MM-DD` theo Asia/Ho_Chi_Minh và vòng đời tin (số lần thấy, biến mất, đăng lại).
  evidence: Tách khỏi #3 vì vòng đời snapshot là deliverable riêng, không cần registry để ship.

- source_spec: none
  summary: Chore C-3 (#8) — email xin phép ITviec, TopCV và tác giả repo gốc, lưu bản sao trong docs/permissions/.
  evidence: Tách khỏi #3 vì là việc giấy tờ và gửi thư, không phụ thuộc hợp đồng tám phép.

- source_spec: none
  summary: Phần còn lại của #9 — cổng CI không tổng hợp trên job_* và cổng hình dạng meta. Cổng registry đóng tám phép nằm trong #3.
  evidence: Tách khỏi #3 vì hai cổng đó bảo vệ code của story khác, có thể merge riêng sau khi registry đã có.

- source_spec: `_bmad-output/implementation-artifacts/spec-gh-1-mo-khung-hai-do-it.md`
  summary: `deploy.yml` paths thiếu `pyproject.toml`, `uv.lock`, `alembic.ini`, `.dockerignore`, nên merge chỉ đổi dependency không build lại image.
  evidence: Hai image chép các file này nhưng `paths` không liệt kê; spec #1 cấm sửa `deploy.yml`.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-1-mo-khung-hai-do-it.md`
  summary: Chưa có đường chạy migration trên prod và chưa có gì chép `compose.prod.yml` lên VPS; phải kiểm `VPS_PATH` vì `--remove-orphans`.
  evidence: `compose.prod` và `deploy.yml` không gọi Alembic; deploy đang tắt nên chưa gây hại, story đầu tiên thêm bảng sẽ gặp.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-1-mo-khung-hai-do-it.md`
  summary: Cổng AD-25 không hiểu `down_revision` dạng tuple nên migration merge vẫn bị tính là hai head.
  evidence: Regex của cổng chỉ khớp chuỗi đơn; có từ trước #1, chưa có migration merge nào.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-1-mo-khung-hai-do-it.md`
  summary: `compose.prod` chưa giới hạn bộ nhớ và chưa xoay log.
  evidence: AD-15 nêu trần bộ nhớ, `deploy.yml` ghi đĩa 35 GB; cần số đo thật trước khi bật deploy.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-69-tinh-va-doc-ty-trong-thanh-pho.md`
  summary: Config (ngưỡng mẫu, cửa sổ 60 ngày, θ, danh sách vai trò, lưu ý độ phủ) đang ở file `config/rules.toml`; phải chuyển sang bảng cấu hình có phiên bản.
  evidence: AD-10 và DoD dòng 4 nói "bảng cấu hình có phiên bản". Ngày 06/11 nhóm chọn file tạm để không chờ thêm; snapshot vẫn lưu `config_version`.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-69-tinh-va-doc-ty-trong-thanh-pho.md`
  summary: Chưa có cách cho admin bật hoặc tắt một snapshot; hiện `publish` tự chạy sau mọi bước tính.
  evidence: Quyết định ngày 06/11: tự động publish trước, vai trò admin để sau. Cần khi muốn giữ lại một snapshot lỗi mà không xóa.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-46-xem-ty-trong-ba-thanh-pho.md`
  summary: Ba trang giữ chỗ `/insights`, `/co-van`, `/soi-tin` còn màu viết cứng (`text-[#E6EDF3]`, `text-[#9FB0C2]`), chưa dùng token của `globals.css`.
  evidence: Có từ #1; #46 chỉ chuyển `layout`, `globals.css`, header và màn Bản đồ sang token. Sửa khi làm màn thật của từng trang.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-67-cau-noi-pipeline-scraper.md`
  summary: PRD FR-2 ("URL bị `robots.txt` cấm thì không bao giờ được request") và AC của Story 1.2 (crawler trình duyệt hỏi cổng) lệch với AD-20 mới; `WORK-SPLIT.md:48` vẫn liệt kê việc này cho C-11.
  evidence: Ngày 06/11/2026 người dùng quyết crawler trình duyệt không cần hỏi `robots.txt`; spec #67 chỉ sửa spine, không sửa PRD, `epics.md`, `WORK-SPLIT.md`.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-67-cau-noi-pipeline-scraper.md`
  summary: PRD FR-5 (xóa liên hệ "trước khi lưu") lệch với việc giữ `data/raw` còn liên hệ chưa xóa trên volume VPS.
  evidence: Ngày 06/11/2026 người dùng quyết không xóa file thô sau `ingest`; AD-21 đã ghi, PRD chưa sửa.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-67-cau-noi-pipeline-scraper.md`
  summary: Gỡ cầu nối C-11 khi Story 1.3 xong.
  evidence: Task còn mở của #67, Story 1.3 nằm ở Sprint 2 nên PR của spec này chưa đóng được issue.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-67-cau-noi-pipeline-scraper.md`
  summary: Chưa có thời hạn giữ, quyền truy cập hay cách xử lý yêu cầu gỡ (FR-47) cho `data/raw` còn liên hệ chưa xóa trên volume VPS.
  evidence: Cơ chế gỡ của AD-21 chỉ sinh `source_exclusions`, không chạm `data/raw`; quyết định ngày 06/11 giữ file thô nhưng chưa nói về vòng đời của nó.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-67-cau-noi-pipeline-scraper.md`
  summary: Khi port sang `haido_core/crawl/polite.py`, Story 1.2 phải chốt ngoại lệ `robots.txt` của crawler trình duyệt: `WORK-SPLIT.md:63` vẫn xếp cổng `polite` cho crawler trình duyệt, còn AD-20 nói ngoại lệ phải là hàng trong `crawl_exceptions`.
  evidence: Ngoại lệ ngày 06/11 hiện chỉ nằm trong văn bản AD-20 vì bảng `crawl_exceptions` chưa tồn tại, nên chưa có công tắc theo nguồn hay theo bước.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-67-cau-noi-pipeline-scraper.md`
  summary: Đường trình duyệt của MoMo và ITviec không có trần request và không kiểm mã HTTP 403/429 như `PoliteClient`, trong khi AD-20 yêu cầu cả hai.
  evidence: `momo.list_job_paths` và `itviec.fetch_detail` có từ trước #67: chúng gọi thẳng `page.goto`, ITviec chỉ dò dấu hiệu chặn trong nội dung trang.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-67-cau-noi-pipeline-scraper.md`
  summary: (Chưa xác minh, mức medium nếu đúng) `data/dedup.jsonl` hoặc `data/consolidated.jsonl` trên một máy có thể đã được dựng từ raw bằng lệnh `dedupe.py` không tham số trước #67, và `extract` sẽ vẫn đọc chúng.
  evidence: Lịch chạy VPS luôn truyền `data/redacted` nên khó xảy ra ở đó. Muốn chốt thì đếm số dòng khớp mẫu email và số điện thoại trong hai file này trên từng máy, không in giá trị.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-6-chot-snapshot-va-vong-doi-tin.md`
  summary: Chưa bật lịch hằng ngày cho `haido ingest` và `haido lifecycle`, chưa kiểm tay ba ngày liên tiếp (hai task cuối của issue #6).
  evidence: Quyết định ngày 06/11: kho của Hải Đồ trên VPS chưa bật, `deploy/daily.sh` thuộc C-11 (#67), và phải chạy migration lên Supabase trước. Story này chạy tay bằng CLI.
- source_spec: `_bmad-output/implementation-artifacts/spec-gh-6-chot-snapshot-va-vong-doi-tin.md`
  summary: Chưa đóng gói dự án (`[build-system]`), nên `[project.scripts] haido` chưa cài được; lệnh chạy là `uv run python -m haido_core.cli`.
  evidence: Đóng gói phải lock lại `uv.lock` và sửa `deploy/api.Dockerfile` (chỉ chép `haido_core`, `haido_api`); ngoài phạm vi #6.
