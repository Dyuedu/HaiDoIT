# TDD: Hình response của toàn cảnh thị trường và dữ liệu giả

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Lệnh:

```text
uv run pytest -q -p no:cacheprovider tests/api/test_ad22_market_overview.py
```

## Các hành vi

1. Tỷ lệ từng cấp và tỷ lệ người mới tính ở máy chủ; số đếm ở `meta.cells`.
2. Vai trò: nhiều tin trước, `other` cuối, đủ mọi vai trò của config.
3. Tỷ trọng, tỷ lệ người mới, tỷ lệ cấp, Hà Nội/TP.HCM của một vai trò.
4. Vai trò dưới ngưỡng: tỷ lệ `null_data`, tỷ trọng `low_sample_shown`.
5. Nơi làm việc: bảy phần, các tỉnh khác gộp; tỷ trọng Hà Nội hoặc TP.HCM.
6. Mốc số năm theo `years_options`, cộng lại bằng `n` toàn quốc.
7. Số đếm lệch (mốc giảm, entry nhiều hơn cả nhóm) thì báo lỗi.
8. Route bản giả trả envelope hợp lệ.
9. Fixture web bằng response bản giả.

## Đợt 1 (2026-11-19)

### RED

- Lần chạy đầu: `ERROR tests/api/test_ad22_market_overview.py` — `ModuleNotFoundError: No module named 'haido_api.market_overview'`; cả 9 test không nạp được.
- Sau khi có schema và hàm dựng: `2 failed, 7 passed`. Đỏ đúng lý do: route trả 404 `not_found` (chưa có route), fixture web chưa có.

### GREEN

- `tests/api/test_ad22_market_overview.py`: 9 passed.
- Cả repo lần đầu: 4 failed. `test_ad17_routes` (2 test) đỏ vì route mới chưa có trong `SAMPLE_QUERY` và `openapi.json` chưa sinh lại; cổng FR-25/31/47 đỏ vì cụm "số tin giảm dần" chứa chuỗi bị cấm "tin giả" (cổng so chuỗi con). Thêm route vào `SAMPLE_QUERY`, sinh lại OpenAPI (`HAIDO_UPDATE_OPENAPI=1`), viết lại thành "nhiều tin trước, cùng số tin thì theo mã".
- `uv run pytest -q` → 1336 passed, 304 skipped (test Postgres skip trên máy không đặt `HAIDO_TEST_DATABASE_URL`). `uv run ruff check .` sạch.

## Đợt 2 (2026-11-19): thứ hạng do máy chủ xếp

Lý do: màn #329 cần xếp vai trò theo cấp người dùng chọn trên biểu đồ tròn, và câu tóm tắt cần thứ hạng cấp, thứ hạng tỷ lệ người mới. AD-22 không cho web sắp xếp, nên `data` thêm `levels_by_size`, `roles_by_level`, `roles_by_entry_share`.

- Hành vi thêm: (10) cấp nhiều tin trước, không gồm `unknown`; mỗi cấp một thứ tự vai trò đủ mọi vai trò, `other` cuối; vai trò có tỷ lệ người mới hiện được, tỷ lệ cao trước.
- RED: `1 failed, 9 passed` — `AttributeError` vì `MarketOverviewData` chưa có `levels_by_size`. Kỳ vọng đầu của test viết sai (cho rằng `backend` đứng thứ hai ở cấp Intern, trong khi các vai trò cùng 0 tin xếp theo mã nên `ai_ml` đứng trước); sửa kỳ vọng thành chỉ kiểm vai trò đứng đầu.
- GREEN: sau khi sinh lại `web/tests/fixtures/market-overview.json` và `docs/api/openapi.json`: `uv run pytest -q` → 1337 passed, 304 skipped; `ruff check .` sạch.

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: sửa file mà issue này từng đụng (trong số `fake_market.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `tools/gates/check_gates.py`, `web/lib/learning-path.ts`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.
