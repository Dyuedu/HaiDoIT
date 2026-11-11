# Implementation Plan: Hình response của màn người mới và dữ liệu giả

**Branch**: `gh-144-hinh-nguoi-moi` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification từ `specs/144-hinh-nguoi-moi/spec.md`

## Summary

Thêm phép thứ ba vào nguồn số liệu thị trường: `newcomer_roles`, route `GET /api/v1/newcomer-roles`. Hình `data` đặt số tin entry-level và n vào hai ô của `meta.cells`, tỷ lệ vào một `Stat` loại mới `level_share` (dưới ngưỡng thì `null_data`). Bản giả đọc mục `newcomer_roles` trong `fake_market.json`. Web có kiểu TypeScript và fixture chép từ API giả.

## Technical Context

**Language/Version**: Python 3.13, FastAPI 0.162, Pydantic 2.14; TypeScript, Next.js 16, Vitest

**Primary Dependencies**: Không thêm gói.

**Storage**: Không đổi cơ sở dữ liệu. Bản giả đọc `haido_api/fixtures/fake_market.json`.

**Testing**: `uv run pytest tests/api tests/domain -q`; `cd web && npx vitest run tests/fr37-newcomer-roles-fixture.test.ts`

**Target Platform**: API trong `haido-prod`; web đọc qua proxy `/api`.

**Constraints**: AD-17 (mọi số là `Stat` hoặc nằm ở `meta`), AD-5 (route không tính), AD-22 (web không tính, không sắp xếp lại).

**Scale/Scope**: 1 route, 10 vai trò giả, 1 loại thước đo mới.

## Constitution Check

- AD-17: số tin entry-level và n là `n` của ô trong `meta.cells`; tỷ lệ là `Stat`; `display` do `suppression_for` quyết; Envelope kiểm `level_share` như các tỷ lệ khác.
- AD-5: route chỉ chuyển cho nguồn.
- Không viết spec vào `_bmad-output/`.

## Project Structure

### Documentation (this feature)

```text
specs/144-hinh-nguoi-moi/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── tasks.md
└── tdd.md
```

### Source Code (repository root)

```text
haido_core/domain/display_policy.py
haido_core/domain/envelope.py
haido_api/schemas/market.py
haido_api/market_source.py
haido_api/fake_market.py
haido_api/stat_market.py
haido_api/routes/market.py
haido_api/fixtures/fake_market.json
docs/api/openapi.json
docs/api/envelope-meta.md
web/lib/city-shares.ts
web/lib/newcomer-roles.ts
web/tests/fixtures/newcomer-roles.json
web/tests/fr37-newcomer-roles-fixture.test.ts
tests/domain/test_ad17_display_policy.py
tests/api/test_fr37_newcomer_roles.py
tests/api/test_ad17_routes.py
tests/api/test_ad17_web_fixtures.py
tests/api/test_dat20_stat_market.py
tests/steps/test_dat20_api_end_to_end.py
```

**Structure Decision**: Số đếm đi qua ô của `meta.cells` thay vì thêm loại `Stat` "count", vì hợp đồng đã đặt mọi cỡ mẫu ở `meta.cells[...].n` và Envelope đã kiểm mọi `cell_id` có mục. Ô entry-level `vn.<role>.entry` cùng quy ước với ô của `skill-rates`. Thêm `level_share` thay vì dùng `composition_share` vì #110 đòi vai trò dưới 30 tin ghi "not enough data", còn `composition_share` dưới ngưỡng thì hiện mờ.

## Complexity Tracking

- `create_app` đòi nguồn cho mọi phép, nên các test của #2 (`test_ad17_routes.py`) và #93 (`test_dat20_stat_market.py`, `test_dat20_api_end_to_end.py`) truyền thêm `newcomer_roles`. Hai issue đó chưa có `specs/`; ghi trong mô tả PR.
- `display_policy.py`, `envelope.py` thuộc #2: thêm một `MeasureKind`, không đổi hành vi của ba loại cũ.

## Thay đổi sau merge (2026-11-11, #163)

#163 (lọc bản đồ theo cấp bậc) sửa các file dùng chung với issue này. Hành vi của `GET /api/v1/newcomer-roles` không đổi.

- `haido_api/fixtures/fake_market.json`: `city_shares` đổi sang dạng `city_shares[role][level]`; thêm ô `<scope>.<role>.entry`. Các ô và mục `newcomer_roles` của #144 giữ nguyên (ghép theo nội dung JSON, không ô nào bị hai bên sửa khác nhau).
- `haido_api/routes/market.py`, `schemas/market.py`, `market_source.py`, `fake_market.py`, `stat_market.py`: `city-shares` nhận tham số tùy chọn `level`, response có `data.level`.
- `docs/api/openapi.json`, `docs/api/envelope-meta.md`: thêm `level` của `city-shares`.
- `tests/api/test_ad17_routes.py`, `test_ad17_web_fixtures.py`, `test_dat20_stat_market.py`, `web/lib/city-shares.ts`: cập nhật cho `level`.

## Thay đổi sau merge (2026-11-12, #212)

#212 (hình response lộ trình học) sửa các file dùng chung với issue này, qua hai đợt (đợt 2 là sửa theo review). Hành vi của issue này không đổi.

- `haido_api/market_source.py`, `fake_market.py`, `stat_market.py`, `routes/market.py`: thêm phép `learning_path` và biến chọn nguồn `HAIDO_MARKET_SOURCE_LEARNING_PATH`; `create_app` đòi nguồn cho phép này (do `SOURCE_ENV` ở `routes/market.py`). `main.py` không đổi.
- `haido_core/domain/envelope.py`: thêm dấu `Ordinal` cho số thứ tự và số đếm của lộ trình (đợt 2 siết: chỉ miễn khi kiểu đúng là `Ordinal` hoặc `Ordinal | None` và giá trị là `int` không âm). `Stat`, `CellMeta`, `Meta` và `MeasureKind.LEVEL_SHARE` của #144 không đổi.
- `haido_api/fixtures/fake_market.json`: mã trong `skill_rates` đổi sang snake_case, thêm và đổi hàng `skill_rates` (đợt 2: `data_engineer/entry` về `vn.data_engineer`, thêm `backend/intern`). Không đụng `cells` hay `newcomer_roles`.
- `docs/api/openapi.json`, `docs/api/envelope-meta.md`: thêm route `learning-path` và ngoại lệ `Ordinal`.
- `tests/api/test_ad17_routes.py`, `test_ad17_web_fixtures.py`, `test_dat20_stat_market.py`, `test_fr33_city_shares_level.py`, `tests/steps/test_dat20_api_end_to_end.py`: thêm nguồn `learning_path` vào các lời gọi `create_app`, thêm route vào `SAMPLE_QUERY` và danh sách yêu cầu của test `display`.
