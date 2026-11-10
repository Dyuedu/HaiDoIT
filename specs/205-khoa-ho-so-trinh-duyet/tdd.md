# TDD: Khóa hồ sơ trình duyệt và danh sách kỹ năng mồi

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Mỗi test một hành vi. Test Python không mạng, không database. Test web chạy trong jsdom, dùng `localStorage` thật của jsdom; trường hợp bộ nhớ bị chặn thì stub `Storage.prototype` cho ném lỗi.

Lệnh:

```text
uv run pytest tests/core/test_fr13_skill_seed.py tests/api -q
cd web && npx vitest run tests/ad23-haido-keys.test.ts
```

## Các hành vi

Python:

1. Mã kỹ năng khớp `^[a-z0-9]+(_[a-z0-9]+)*$`, tối đa 40 ký tự; `c++`, `ci/cd`, `Python`, `a__b`, `a,b` bị từ chối.
2. Danh sách mồi có 60–150 kỹ năng, mã không trùng và xếp theo thứ tự, `version` bắt đầu bằng `seed-`.
3. Mỗi kỹ năng có tên tiếng Anh, tên tiếng Việt và nguồn.
4. Không tên hay bí danh nào (sau chuẩn hóa) trỏ tới hai mã.
5. "học máy" và "Machine Learning" ra `machine_learning`; "C#" ra `csharp`; "ReactJS" ra `react`.
6. Không có tên vai trò như `tester`, `fullstack`, `data engineer`.
7. `GET /api/v1/skills` trả `{data: {vocab_version, skills}}` đúng thứ tự file mồi; mỗi dòng có đúng `code`, `name_en`, `name_vi`, `aliases`; không có số.
8. Test AD-17: mọi route `/api/v1` hoặc trả Envelope có số, hoặc nằm trong `NUMBERLESS_ROUTES` và không có số.

Web:

9. Đúng ba khóa `haido:eval`, `haido:profile`, `haido:session`.
10. Định dạng mã kỹ năng giống Python.
11. Chưa có gì thì ra hồ sơ rỗng; ghi rồi đọc ra đúng hồ sơ.
12. Bỏ mã sai, mã trùng, cắt ở 200.
13. JSON hỏng, sai `v`, sai kiểu ra hồ sơ rỗng.
14. Bỏ trường lạ; mã vai trò sai định dạng thành `null`.
15. `clearHaidoData` xóa mọi `haido:*`, kể cả khóa ngoài danh sách, giữ khóa của trang khác.
16. `Storage` ném lỗi thì module không ném ra ngoài.

## RED

- `uv run pytest tests/core/test_fr13_skill_seed.py tests/api -q` → 2 errors lúc thu thập (`ModuleNotFoundError: No module named 'haido_core.vocab.skills'`).
- `uv run pytest tests/api/test_ad17_routes.py -q` → 1 failed, 35 passed: `test_ad17_moi_route_tra_envelope` đỏ vì chưa có `/api/v1/skills`.
- `npx vitest run tests/ad23-haido-keys.test.ts` → 1 file failed: `Failed to resolve import "@/lib/haido-keys"`.

## GREEN

- `uv run pytest tests/core/test_fr13_skill_seed.py tests/api -q` → 51 passed, 22 skipped (skip là test Postgres sẵn có). Lần chạy đầu còn `test_ad17_openapi_da_commit_khop_voi_code` đỏ cho tới khi sinh lại `docs/api/openapi.json` bằng `HAIDO_UPDATE_OPENAPI=1`.
- `npx vitest run tests/ad23-haido-keys.test.ts` → 9 passed. Toàn bộ `npm test` → 115 passed.
- `uv run pytest -q` → 370 passed, 126 skipped.
- `uv run python tools/gates/check_gates.py` → AD-23 PASS, 8 pass, 2 skip, 0 fail.
- `npm run lint`, `npx tsc --noEmit`, `uv run ruff check .` sạch.
- Chạy `uvicorn` trên máy, `curl /api/v1/skills` trả `seed-2026-11-11` và 100 kỹ năng.
