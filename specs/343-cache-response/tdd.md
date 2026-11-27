# TDD: Cache response của API thị trường, xóa theo snapshot (#343)

**Lệnh test**:

```
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test \
  uv run pytest tests/api/test_gh343_cache_response.py -q
```

## Danh sách hành vi cần test

1. Lần hai lấy từ cache: `MISS` rồi `HIT`, cùng bytes và `content-type`, nguồn gọi một lần
2. Thứ tự tham số không tách khóa
3. Giá trị tham số khác là khóa khác
4. `version()` đổi thì request kế tiếp tính lại
5. Mỗi request đều hỏi `version()`
6. Không cache request có `have` hoặc `title` (3 URL)
7. Không giữ bản sao chức danh hay `have` trong khóa
8. Không cache lỗi: 404 `unknown_cell`, 404 `unknown_skill`, 422 (3 URL)
9. `version()` hỏng thì đi thẳng vào route, không header `x-cache`
10. Chỉ `GET /api/v1/*`
11. Trần số mục, bỏ theo LRU
12. Mặc định tắt; bật bằng `HAIDO_RESPONSE_CACHE=on`
13. `FakeMarket.version()` không đổi
14. `compose.prod.yml` bật; `compose.local.yml` không đặt; `compose.loadtest.yml` mặc định `on`, tắt được
15. `StatMarket.version()` chỉ đổi khi snapshot được chốt, không đổi khi mở snapshot mới (Postgres)
16. Snapshot mới được phục vụ ngay ở request kế tiếp, kiểm trên `market-overview` thật (Postgres)

## RED — Đợt 1 (2026-11-23)

Lần chạy đầu: lỗi lúc collect (`ModuleNotFoundError: No module named 'haido_api.response_cache'`).

Để RED đo ở mức hành vi, tạo `haido_api/response_cache.py` chỉ có hai hằng `CACHE_ENV`, `CACHE_HEADER`, chạy lại:

**7 fail, 14 error, 2 pass** (23 test).

- 14 error ở fixture `client`: `create_app()` chưa nhận `response_cache` (`TypeError`).
- 7 fail: `create_app()` chưa nhận `cache_max_entries`, chưa đọc `HAIDO_RESPONSE_CACHE`; `FakeMarket` và `StatMarket` chưa có `version()`; `compose.prod.yml` và `compose.loadtest.yml` chưa có biến.
- 2 pass vì hành vi vốn đã đúng: mặc định không có cache (`test_gh343_mac_dinh_tat`), `compose.local.yml` không đặt biến (`test_gh343_local_cua_ci_giu_mac_dinh`).

## GREEN — Đợt 1 (2026-11-23)

Lệnh: như trên.

Lần đầu: **22 pass, 1 fail**. `test_gh343_so_muc_co_tran` dùng `frontend`, `mobile`, nhưng fixture giả chỉ có `city_shares` cho 10 vai trò, nên hai URL đó trả 404 và không được lưu. Đây là lỗi của test, không phải của mã: test đổi sang `fullstack`, `security` và kiểm thêm status 200 trước khi xét LRU.

Lần hai: **23 pass, 0 fail** (2 test Postgres chạy thật, không skip).

`uv run ruff check .`: sạch, sau khi sắp lại import ở `main.py` và đổi `ResponseStore.keys()` thành `__iter__` (SIM118).

Toàn bộ: `uv run pytest -q` → **1845 pass, 0 fail** (chạy trước khi đổi `keys()` → `__iter__`; chạy lại `test_gh343_*`, `test_gh342_*`, `test_gh309_*` sau đó: 52 pass).

## Đo (2026-11-23)

Kết quả ở [ket-qua-do.md](ket-qua-do.md): 300 RPS giữ p95 < 200 ms (baseline 40). Script k6 của #342 thêm chỉ số `cache_hit`.

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: sửa file mà issue này từng đụng (trong số `fake_market.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `tools/gates/check_gates.py`, `web/lib/learning-path.ts`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: sửa file mà issue này từng đụng (trong số `stat_market.py`, `check_gates.py`, `envelope-meta.md`, `compose.prod.yml`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.

## Đợt sửa 2026-11-27 (#230, hình tin dán "Soi tin")

**Vì sao sửa**: #230 thêm nguồn `posting_check` vào `SOURCE_ENV`, bảng `[posting_match]` vào `config/rules.toml`, ô `vn.backend.junior` vào
`fake_market.json`, route `posting-reads` và `posting-check`. Các file của issue này bị chạm: `deploy/compose.loadtest.yml`, `deploy/compose.prod.yml`, `haido_api/fake_market.py`, `haido_api/main.py`, `haido_api/market_source.py`, `haido_api/stat_market.py`.

**Hành vi của issue này**: không đổi; không AC nào của #343 đúng khác đi. Mọi thay đổi chỉ cộng thêm (khóa nguồn mới, mục cấu hình mới, ô và hàng
fixture mới, hàng tài liệu mới, nguồn `posting_check` trong các lời gọi `create_app` của test).

**RED/GREEN**: RED (chạy thật): trả 13 file test cũ dựng create_app với năm nguồn về bản ở HEAD rồi chạy với code mới thì 109 failed, 54 lỗi, 32 passed (thiếu nguồn posting_check). GREEN: sau khi thêm nguồn và sửa các file, uv run pytest -q toàn bộ được 2029 passed (không còn test nào đỏ của issue này). Chi tiết ở specs/230-hinh-soi-tin/tdd.md.
