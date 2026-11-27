# TDD: Đo sức chịu tải baseline của API bằng k6 (#342)

**Lệnh test**:

```
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test \
  uv run pytest tests/deploy/test_gh342_do_tai_baseline.py tests/tools/test_gh342_loadtest_seed.py -q
```

Postgres lấy từ `deploy/compose.local.yml` (`docker compose -f deploy/compose.local.yml up -d postgres`).

## Danh sách hành vi cần test

### Compose đo (KB2)
1. `api` build từ `deploy/api.Dockerfile`, context là gốc repo
2. `api` không ghi đè `command`/`entrypoint`
3. Mọi khóa của `SOURCE_ENV` là `stat` (5 test, tham số theo nguồn)
4. `api` giới hạn 2 CPU
5. Healthcheck của `api` giống prod
6. Mọi cổng chỉ mở trên `127.0.0.1`
7. DB đo có tên kết thúc bằng `_test`

### Script k6 (KB3)
8. Mọi đường dẫn `/api/v1/...` trong script có trong OpenAPI
9. Script không gọi `/api/v1/learning-path`
10. Vai trò, cấp bậc, kỹ năng trong `params.json` có trong config và từ vựng (3 test)
11. Có kịch bản `smoke` và `breakpoint`, dùng `ramping-arrival-rate`
12. Ngưỡng `p(95)<200` và `rate<0.001` đều có `abortOnFail: true`

### Seed (KB1)
13. Từ chối host ngoài local, DB không tên `_test`, DB tên `_test` ở giữa (3 test)
14. Nhận DB local tên `_test`
15. Seed công bố đúng một snapshot `published`, và API `stat` trả 200 cho mọi URL của kịch bản (cần Postgres)

## RED — Đợt 1 (2026-11-23)

Lệnh: như trên.

Kết quả:

- `tests/deploy/test_gh342_do_tai_baseline.py`: **18 fail, 0 pass**. Cả 18 đều `FileNotFoundError`: chưa có `deploy/compose.loadtest.yml`, `loadtest/k6/baseline.js`, `loadtest/k6/params.json`.
- `tests/tools/test_gh342_loadtest_seed.py`: **lỗi lúc collect** (`ModuleNotFoundError: No module named 'tools.loadtest_seed'`), nên cả 5 test của file chưa chạy được.

## GREEN — Đợt 1 (2026-11-23)

Lệnh: như trên.

Kết quả: **23 pass, 0 fail** (18 của compose/k6, 5 của seed; test seed chạy thật trên Postgres, không skip).

Kiểm tra thêm:

- `uv run pytest tests/deploy tests/tools -q`: 299 pass, 0 fail.
- `uv run ruff check .`: sạch. Đã sửa một lỗi FURB167 trong test (`re.S` → `re.DOTALL`).

Đã thêm:

- `tools/loadtest_seed.py`: `check_target` (host local, DB tên `_test`) và `seed` (dùng lại `_build` của `tools/bench_skill_rates.py`, thêm lượt chạy hoàn tất cho mọi nguồn tự động, rồi `aggregate` và `publish`). Phải chạy dạng module (`python -m tools.loadtest_seed`). Chạy dạng file thì `tools/` nằm đầu `sys.path`, nên không import được `haido_core`.
- `deploy/compose.loadtest.yml`: postgres + api, 2 CPU / 1 GB mỗi service, cổng 5434 và 8001 trên localhost.
- `loadtest/k6/baseline.js`, `loadtest/k6/params.json`, `loadtest/README.md`.

Đo thật: `smoke` qua (119 URL đều 200). Số breakpoint ở [ket-qua-do.md](ket-qua-do.md).

## Đợt #343 (2026-11-23): compose đo bật cache mặc định như prod

Lý do: #343 thêm `HAIDO_RESPONSE_CACHE: ${HAIDO_RESPONSE_CACHE:-on}` vào `deploy/compose.loadtest.yml`, để môi trường đo khớp prod. Đo lại baseline không cache: `HAIDO_RESPONSE_CACHE=off docker compose -f deploy/compose.loadtest.yml up -d`. Số baseline trong `ket-qua-do.md` đo trước thay đổi này, tức không có cache.

- `uv run pytest tests/deploy/test_gh342_do_tai_baseline.py`: chạy lại sau khi sửa compose, xem `specs/343-cache-response/tdd.md`.
- `loadtest/k6/baseline.js` thêm chỉ số `cache_hit` (tỷ lệ response có `x-cache: HIT`). Kịch bản, ngưỡng và URL không đổi; `tests/deploy/test_gh342_do_tai_baseline.py` vẫn xanh.

## Đợt sửa 2026-11-27 (#230, hình tin dán "Soi tin")

**Vì sao sửa**: #230 thêm nguồn `posting_check` vào `SOURCE_ENV`, bảng `[posting_match]` vào `config/rules.toml`, ô `vn.backend.junior` vào
`fake_market.json`, route `posting-reads` và `posting-check`. Các file của issue này bị chạm: `deploy/compose.loadtest.yml`.

**Hành vi của issue này**: không đổi; không AC nào của #342 đúng khác đi. Mọi thay đổi chỉ cộng thêm (khóa nguồn mới, mục cấu hình mới, ô và hàng
fixture mới, hàng tài liệu mới, nguồn `posting_check` trong các lời gọi `create_app` của test).

**RED/GREEN**: RED (chạy thật): trả 13 file test cũ dựng create_app với năm nguồn về bản ở HEAD rồi chạy với code mới thì 109 failed, 54 lỗi, 32 passed (thiếu nguồn posting_check). GREEN: sau khi thêm nguồn và sửa các file, uv run pytest -q toàn bộ được 2029 passed (không còn test nào đỏ của issue này). Chi tiết ở specs/230-hinh-soi-tin/tdd.md.
