# Việc hoãn

- source_spec: `_bmad-output/implementation-artifacts/spec-gh-2-chot-envelope-meta-endpoint-du-lieu-gia.md`
  summary: Chưa chốt cách web gọi API lúc dev và lúc chạy thật (rewrite của Next.js, Caddy cùng origin, hay CORS); app hiện không có CORS, preflight `OPTIONS` nhận 405.
  evidence: Chưa kiểm được có cần CORS hay không vì #1 chưa dựng `web/` và Compose. Nếu web gọi thẳng `:8000` từ trình duyệt thì mức medium. Thuộc #1 (1.1).

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
