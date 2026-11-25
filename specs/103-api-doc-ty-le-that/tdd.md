# TDD: API đọc tỷ lệ kỹ năng thật (#103)

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Cần Postgres thật (`HAIDO_TEST_DATABASE_URL` trỏ DB `*_test`).

Lệnh:

```text
uv run pytest tests/api/test_ad17_meta_nguon_stat.py tests/api/test_fr19_skill_rates_stat.py -q
python tools/gates/check_gates.py --require AD-7 AD-17
```

## Các hành vi

1. (`test_ad17_meta_nguon_stat.py`) Với nguồn `stat` cho mọi phép: `city-shares`, `skill-rates`, `newcomer-roles` trả `{data, meta}` có `meta.snapshot_date` và `meta.cells`. (AC 1)
2. (cùng file) `learning-path` và `skill-roles` ở nguồn `stat` chưa có số thật: trả `{error}`, không có `data`. (AC 1)
3. (`test_fr19_skill_rates_stat.py::test_ad7_...`) Mọi câu SQL của một lần gọi `skill-rates` chỉ đọc `stat_skill_rates` và `stat_cells`; không có `job_`, `group by`, `avg(`, `count(`, `sum(`, `percentile`. (AC 2)
4. Cổng AD-7 của `check_gates.py` PASS. (AC 2)

## RED

Chạy 2026-11-17, trước khi viết `StatMarket.skill_rates`:

- Hành vi 3: `uv run pytest tests/api/test_fr19_skill_rates_stat.py -q` → 14 failed, 3 passed; `test_ad7_...` đỏ vì `skill-rates` trả 404 `unknown_cell` "Tỷ lệ kỹ năng chưa có số liệu thật" (chưa đọc bảng nào).
- Hành vi 1 và 2: viết sau khi `skill_rates` đã có, nên không có RED riêng: hành vi 1 xanh ngay lần chạy đầu cho `skill-rates` (xác nhận, không chứng minh được bằng đỏ). Lần chạy đầu của test lỗi 500 ở `city-shares` vì dữ liệu dựng thiếu ô thành phố (lỗi của test, sửa dữ liệu dựng, không sửa code). Hành vi 2 xanh ngay vì `StatMarket.learning_path` và `skill_roles` vốn trả `UnknownCell`.

## GREEN

- `uv run pytest tests/api/test_ad17_meta_nguon_stat.py tests/api/test_fr19_skill_rates_stat.py -q` → 20 passed (2 + 18).
- Số chạy toàn bộ và cổng: xem `specs/151-ty-le-ky-nang-that/tdd.md`.

## Đợt 2 (2026-11-17): sửa theo review

Lý do: test route chưa có số thật chấp nhận cả 404 lẫn 500; một lỗi 500 sẽ lọt. Siết thành 404 và `error.code == "unknown_cell"`. AC không đổi.

- RED: không có. Điều kiện siết đã đúng với code hiện tại (`StatMarket.learning_path` và `skill_roles` ném `UnknownCell`), nên test xanh ngay; đây là siết, không chứng minh bằng đỏ.
- GREEN (chạy thật): `uv run pytest tests/api/test_ad17_meta_nguon_stat.py -q` → 2 passed. Số chạy toàn bộ: `specs/151-ty-le-ky-nang-that/tdd.md`.

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `deploy/compose.prod.yml`, `docs/api/envelope-meta.md`, `haido_api/stat_market.py`, `tests/api/test_ad17_meta_nguon_stat.py`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #324 (2026-11-19): câu chữ trên màn viết lại

Lý do: #324 viết lại chữ hiển thị bằng tiếng Việt dễ hiểu (bỏ nhãn `n = `, "snapshot", "entry-level"; câu thiếu mẫu "Mới có X tin, cần ít nhất 30"; khung nguồn "Đang xem", "Cập nhật", tên nguồn). File của issue này bị đụng: `web/lib/skill-profile-view.ts`. Số, thứ tự và ẩn số theo ngưỡng không đổi. Hành vi và AC của issue này không đổi.

- RED và GREEN: `specs/324-cau-chu-de-hieu/tdd.md` (RED 42 failed / 299 passed; GREEN 357 passed, chạy `npx vitest run` từ PowerShell).

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `docs/api/envelope-meta.md`, `haido_api/stat_market.py`, `tests/api/test_fr19_skill_rates_stat.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.

## Đợt #328 (2026-11-19): market-overview có số thật

Lý do: #328 cài `StatMarket.market_overview`, nên `/api/v1/market-overview` đọc nguồn `stat` trả 200. `tests/api/test_ad17_meta_nguon_stat.py` thêm route này vào `REAL`. Hành vi và AC của issue này không đổi: route có số thật trả `data` và `meta`, route chưa có trả `unknown_cell`.

- RED: CI của PR #331, `test_ad17_103_route_chua_co_so_that_tra_loi_chuan_khong_co_data` đỏ vì route mới trả 200. GREEN: xem `specs/328-tong-quan-thi-truong-that/tdd.md`.

## Đợt #217 (2026-11-25): lộ trình học thành chủ đề

Lý do: sửa file mà issue này từng đụng (trong số `fake_market.py`, `docs/api/openapi.json`, `docs/api/envelope-meta.md`, `tools/gates/check_gates.py`, `web/lib/learning-path.ts`, test lộ trình): chỉ phần lộ trình học. Hành vi và AC của issue này không đổi.

RED và GREEN: `specs/217-man-lo-trinh/tdd.md` đợt 4.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: `learning-path` ở nguồn `stat` hết 404 cố định, nên chuyển sang nhóm route có số thật (RED: `test_ad17_103_route_chua_co_so_that_tra_loi_chuan_khong_co_data` đỏ vì nhận 200 `not_ready` có `meta`). Test đó thay bằng "chưa có snapshot thì mọi route trả lỗi chuẩn". AC không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.
