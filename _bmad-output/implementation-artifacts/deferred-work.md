# Việc hoãn

- source_spec: `_bmad-output/implementation-artifacts/spec-gh-2-chot-envelope-meta-endpoint-du-lieu-gia.md`
  summary: Chưa chốt cách web gọi API lúc dev và lúc chạy thật (rewrite của Next.js, Caddy cùng origin, hay CORS); app hiện không có CORS, preflight `OPTIONS` nhận 405.
  evidence: Chưa kiểm được có cần CORS hay không vì #1 chưa dựng `web/` và Compose. Nếu web gọi thẳng `:8000` từ trình duyệt thì mức medium. Thuộc #1 (1.1).
  status: Đã giải quyết ở GH-1 bằng route handler cùng origin (`app/api/[...path]/route.ts`), không cần CORS.
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
