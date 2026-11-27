# TDD: Toàn cảnh thị trường đọc số thật

Lệnh:

```text
uv run pytest -q -p no:cacheprovider tests/api/test_ad22_market_overview_stat.py
```

## Các hành vi

1. Số tin vai trò, Hà Nội/TP.HCM của vai trò, nơi, mốc số năm đúng bằng `n` của các ô.
2. Chưa có snapshot đọc được thì 404 `unknown_cell`.

## Đợt 1 (2026-11-19)

### RED

Chưa chạy được trên máy làm việc: không có Postgres (Docker Desktop tắt), hai test skip với "HAIDO_TEST_DATABASE_URL chưa đặt". Không ghi RED khi chưa chạy thật. Test được viết trước code; CI của dự án bắt buộc chạy test Postgres (thiếu biến thì `pytest.fail`).

### GREEN

CI của PR #331 (job "Python - ruff and pytest", Postgres thật): hai test của `tests/api/test_ad22_market_overview_stat.py` qua. Cùng lượt chạy, `tests/api/test_ad17_meta_nguon_stat.py::test_ad17_103_route_chua_co_so_that_tra_loi_chuan_khong_co_data` đỏ: test này liệt kê route đã có số thật (`REAL`) và chờ 404 `unknown_cell` ở route còn lại; `market-overview` đọc nguồn thật nên trả 200. Thêm route vào `REAL` (ý của test #103 không đổi: route có số thật trả `data` và `meta`, route chưa có trả lỗi chuẩn). Kết quả CI sau sửa ghi ở mô tả PR.

## Đợt 2 (2026-11-19): gộp main sau #102

Lý do: #102 (θ có phiên bản) vào main trước PR này, thêm `theta_version` bắt buộc vào `meta.thresholds` và hàm `StatMarket._thresholds(latest)`. `market_overview` chuyển sang dùng hàm đó thay vì tự dựng `Thresholds`; fixture web `market-overview.json` và `docs/api/openapi.json` sinh lại. Xung đột khi gộp chỉ ở các `tdd.md` (hai đợt cùng thêm cuối file); giữ cả hai, đợt #102 trước.

- GREEN ở máy: `uv run pytest -q` → 1403 passed, 339 skipped; `ruff check .` sạch. Test Postgres chạy trên CI.

## Đợt #343 (2026-11-23): thêm `version()` cho nguồn, AC của issue này không đổi

Lý do: #343 thêm `version()` vào `MarketReadModel`, `FakeMarket`, `StatMarket` để cache response biết khi nào có snapshot mới. `version()` được hỏi ở mỗi request, nên `market-overview` vẫn đọc snapshot đọc được mới nhất ngay sau khi chốt (`test_gh343_snapshot_moi_duoc_phuc_vu_ngay_request_ke_tiep` kiểm đúng route này trên Postgres).

- RED và GREEN: `specs/343-cache-response/tdd.md`.

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: sửa file mà issue này từng đụng (trong số `fake_market.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `tools/gates/check_gates.py`, `web/lib/learning-path.ts`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: sửa file mà issue này từng đụng (trong số `stat_market.py`, `check_gates.py`, `envelope-meta.md`, `compose.prod.yml`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.

## Đợt sửa 2026-11-27 (#230, hình tin dán "Soi tin")

**Vì sao sửa**: #230 thêm nguồn `posting_check` vào `SOURCE_ENV`, bảng `[posting_match]` vào `config/rules.toml`, ô `vn.backend.junior` vào
`fake_market.json`, route `posting-reads` và `posting-check`. Các file của issue này bị chạm: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `docs/api/openapi.json`, `haido_api/fake_market.py`, `haido_api/fixtures/fake_market.json`, `haido_api/market_source.py`, `haido_api/routes/market.py`, `haido_api/stat_market.py`, `tests/api/test_ad17_meta_nguon_stat.py`, `tests/api/test_ad17_routes.py`, `tests/api/test_ad22_market_overview_stat.py`.

**Hành vi của issue này**: không đổi; không AC nào của #328 đúng khác đi. Mọi thay đổi chỉ cộng thêm (khóa nguồn mới, mục cấu hình mới, ô và hàng
fixture mới, hàng tài liệu mới, nguồn `posting_check` trong các lời gọi `create_app` của test).

**RED/GREEN**: RED (chạy thật): trả 13 file test cũ dựng create_app với năm nguồn về bản ở HEAD rồi chạy với code mới thì 109 failed, 54 lỗi, 32 passed (thiếu nguồn posting_check). GREEN: sau khi thêm nguồn và sửa các file, uv run pytest -q toàn bộ được 2029 passed (không còn test nào đỏ của issue này). Chi tiết ở specs/230-hinh-soi-tin/tdd.md.
