# Việc hoãn

- source_spec: `_bmad-output/implementation-artifacts/spec-gh-2-chot-envelope-meta-endpoint-du-lieu-gia.md`
  summary: Chưa chốt cách web gọi API lúc dev và lúc chạy thật (rewrite của Next.js, Caddy cùng origin, hay CORS); app hiện không có CORS, preflight `OPTIONS` nhận 405.
  evidence: Chưa kiểm được có cần CORS hay không vì #1 chưa dựng `web/` và Compose. Nếu web gọi thẳng `:8000` từ trình duyệt thì mức medium. Thuộc #1 (1.1).
