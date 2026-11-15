# TDD: Hình response của màn người mới và dữ liệu giả

Theo `docs/templates/test-driven-tdd/test-driven-development.md`.

Mỗi test một hành vi. Test Python không mạng, không database, chạy API qua `TestClient` với nguồn giả. Test web đọc fixture JSON, không gọi API.

Lệnh:

```text
uv run pytest tests/api tests/domain -q
cd web && npx vitest run tests/fr37-newcomer-roles-fixture.test.ts
```

## Các hành vi

Python:

1. `suppression_for(level_share)` dưới ngưỡng ra `null_data`, đủ ngưỡng ra `shown` (cả trong bảng của `test_ad17_display_policy.py`).
2. `Stat` loại `level_share` không được `low_sample_shown`, giá trị phải trong 0–1.
3. `NewcomerRoleRow` từ chối `share` sai loại, `share.cell_id` khác `total_cell_id`, `entry_cell_id` trùng `total_cell_id`.
4. `NewcomerRolesData` từ chối vai trò lặp, `rows` rỗng, `levels` rỗng.
5. Route trả `{data, meta}`, `levels` là Intern/Fresher/Junior, mỗi dòng đủ bốn trường, `display` khớp `suppression_for` trên n của vai trò, entry ≤ n.
6. Dữ liệu giả có đúng tập vai trò của `config/rules.toml`.
7. Số entry-level bằng Intern+Fresher+Junior của ô vai trò; `share.value` = entry/n khi `shown`, `null` khi `null_data`.
8. Dữ liệu giả có bốn trường hợp: đủ mẫu, đủ mẫu mà 0 entry-level, dưới 30, không có tin.
9. Thứ tự dòng: có tỷ lệ trước, entry giảm dần, rồi mã.
10. Route mới có trong `SAMPLE_QUERY` của AD-17 và trong danh sách truy vấn kiểm `display`.
11. Fixture web giống hệt response của API giả.

Web:

12. Mọi dòng của fixture có hai ô trong `meta.cells`, `share` là `level_share` của ô vai trò.
13. `rowCounts` tra đúng `{entry: 501, n: 877}` cho `ai_ml`.
14. Vai trò dưới ngưỡng: `share.value = null`, vẫn có entry và n.
15. Vai trò đủ mẫu mà 0 entry-level: `share.value = 0`.
16. `rowCounts` ném lỗi khi thiếu ô.

## RED

- `uv run pytest tests/api tests/domain -q` → 2 errors lúc thu thập: `ImportError: cannot import name 'NewcomerRoleRow'` (`test_fr37_newcomer_roles.py`) và `AttributeError: type object 'MeasureKind' has no attribute 'LEVEL_SHARE'` (`test_ad17_display_policy.py`).
- `uv run pytest tests/api/test_ad17_routes.py tests/api/test_ad17_web_fixtures.py -q` → 3 failed, 38 passed: `test_ad17_moi_route_tra_envelope` (chưa có route trong app), `test_ad17_display_chi_do_suppression_for_quyet[/api/v1/newcomer-roles]` (404), `test_ad17_fixture_web_khop_response_newcomer_roles` (404).
- `npx vitest run tests/fr37-newcomer-roles-fixture.test.ts` → 1 file failed: `Failed to resolve import "./fixtures/newcomer-roles.json"`.

## GREEN

- `uv run pytest tests/api -q` với `HAIDO_UPDATE_OPENAPI=1` để sinh lại `docs/api/openapi.json` → 116 passed, 22 skipped.
- `uv run pytest -q` → 498 passed, 126 skipped. Skip là test Postgres (`HAIDO_TEST_DATABASE_URL` chưa đặt trên máy); các lời gọi `create_app` đã sửa trong `test_dat20_stat_market.py` và `test_dat20_api_end_to_end.py` chạy trong CI.
- `npx vitest run tests/fr37-newcomer-roles-fixture.test.ts` → 5 passed. Toàn bộ `npx vitest run` → 120 passed.
- `uv run ruff check .`, `npx tsc --noEmit`, `npm run lint` sạch.
- `uv run python tools/gates/check_gates.py` → 8 pass, 2 skip, 0 fail.

## Đợt 2 — 2026-11-11, sau khi ghép #163

Lý do: #163 sửa `fake_market.json`, route, schema và tài liệu API dùng chung với #144. Rebase #163 lên `main` (đã có #144) gặp xung đột trong `haido_api/fixtures/fake_market.json`; ghép theo nội dung JSON.

- RED: không có test nào của #144 đỏ. Hành vi của #144 không đổi, nên không có RED mới cho issue này.
- GREEN:
  - `uv run pytest -q tests/api/test_fr37_newcomer_roles.py tests/api/test_ad17_routes.py tests/api/test_ad17_web_fixtures.py` → 59 passed.
  - `npx vitest run tests/fr37-newcomer-roles-fixture.test.ts` → 5 passed.
  - `uv run pytest -q` (có Postgres) → 715 passed.

## Đợt 3 — 2026-11-12, sau khi thêm lộ trình học (#212)

Lý do: #212 thêm phép `learning_path` vào `create_app`, đổi mã kỹ năng của `skill_rates` giả sang snake_case và (đợt 2 của #212) sửa nội dung `skill_rates`, `envelope.py`, schema OpenAPI.

- Không viết test mới của issue này và không có đợt RED: hành vi của issue không đổi. Bản ghi trước ghi một RED giả định ("sẽ báo...") không kèm số đếm; thay bằng ghi chú này.
- Đã chạy lại các test có sẵn của issue này trên mã sau đợt 2 của #212 (kết quả thật, 2026-11-12):
  - `uv run pytest tests/api tests/domain -q` → 425 passed (lệnh quét cả thư mục nên gồm cả test mới của #212).
  - `npx vitest run tests/fr37-newcomer-roles-fixture.test.ts` → 5 passed.
- GREEN: `uv run pytest -q` (có Postgres) → 862 passed, không skip; hai lượt `-m determinism` (`PYTHONHASHSEED=0` và `1`) → 7 passed mỗi lượt; web `npm run test` → 164 passed.

## Đợt 2026-11-12 — #280 thêm tham số `years` cho city-shares

Lý do: #280 sửa `haido_api/schemas/market.py` (`CitySharesData.years`, `years_unstated_cell_id`), `market_source.py`, `routes/market.py`, `stat_market.py`, `fake_market.py`, `fake_market.json` (thêm khóa `all/entry.y1` và ô `vn.all.entry.ynone`), `web/lib/city-shares.ts`, và sinh lại `docs/api/openapi.json`. Phần `newcomer-roles` không đổi.

- RED: không có test nào của #144 đỏ. Hành vi của #144 không đổi.
- GREEN: `uv run pytest -q tests/api/test_fr37_newcomer_roles.py tests/api/test_ad17_routes.py tests/api/test_ad17_web_fixtures.py` xanh; `npx vitest run tests/fr37-newcomer-roles-fixture.test.ts` xanh; `uv run pytest -q` → 770 passed.

## Đợt 2026-11-12 — #145, #146 cài bản thật của `newcomer-roles`

Lý do: #145, #146 thay bản giữ chỗ `StatMarket.newcomer_roles` (luôn 404) bằng phép đọc `stat_cells`, và `deploy/compose.prod.yml` chọn nguồn `stat`. Hình response và bản giả không đổi; cạnh biên "nguồn `stat` trả 404" trong `spec.md` được sửa theo.

- RED: không test nào của #144 đổi kỳ vọng. Test mới nằm ở `tests/api/test_fr37_newcomer_roles_stat.py` (RED ghi trong `specs/145-doc-so-tin-entry/tdd.md`, `specs/146-tra-so-nguoi-moi/tdd.md`).
- GREEN: `uv run pytest -q tests/api/test_fr37_newcomer_roles.py tests/api/test_ad17_routes.py tests/api/test_ad17_web_fixtures.py` xanh trong lượt `uv run pytest -q` → 959 passed.

## Đợt 2026-11-12 — #147 thêm `fetchNewcomerRoles` vào `web/lib/newcomer-roles.ts`

Lý do: #147 thêm hàm gọi API và kiểm envelope vào `web/lib/newcomer-roles.ts`; kiểu và `rowCounts` của #144 giữ nguyên. Hình response không đổi.

- RED: không test nào của #144 đổi kỳ vọng.
- GREEN: `npx vitest run tests/fr37-newcomer-roles-fixture.test.ts` xanh trong lượt `npx vitest run` → 189 passed.

## Đợt 2026-11-13 — #284 thêm bảy vai trò vào bản giả

Lý do: #284 thêm dòng `newcomer_roles.rows` cho bảy mã mới (theo đúng thứ tự `roles`) và ô `vn.<mã>`, `vn.<mã>.entry` vào `haido_api/fixtures/fake_market.json`; sinh lại `web/tests/fixtures/newcomer-roles.json`. Hình của response không đổi.

- RED: không chạy riêng. Fixture web được sinh lại ngay sau khi đổi bản giả; không test nào của #144 đổi kỳ vọng.
- GREEN: sinh lại fixture; `tests/api/test_fr37_newcomer_roles.py`, `tests/api/test_ad17_web_fixtures.py`, `web/tests/fr37-newcomer-roles-fixture.test.ts` xanh.

## Đợt 2026-11-13 — #285 34 tỉnh, Remote, Nước ngoài

Lý do: #285 đổi mã nơi (bản giả thay `other` bằng `hai_phong`, thêm `remote`, `abroad`; sinh lại sáu fixture city-shares và `newcomer-roles.json` của web). Không AC nào của issue này đổi.

- RED: không test nào của #144 đổi kỳ vọng; fixture sinh lại ngay sau khi đổi bản giả.
- GREEN: sửa kỳ vọng theo mã nơi mới; `uv run pytest -q` → 947 passed; `npx vitest run` → 166 passed.

## Đợt 2026-11-13 (#148)

Lý do: `haido_api/stat_market.py` thêm bảo vệ entry > n cho nguồn `stat` của `newcomer_roles`; bản giả và hình response không đổi.

- RED: không có, không test nào của #144 đổi kỳ vọng.
- GREEN: `uv run pytest tests/api tests/domain -q` → 487 passed; `cd web && npx vitest run tests/fr37-newcomer-roles-fixture.test.ts` → 5 passed.

## Đợt 2026-11-15 — gộp main vào #212

Lý do: `fake_market.json` `skill_rates` đổi (xem `specs/212-hinh-lo-trinh-hoc/tdd.md` đợt 3); `fake_market.py` và `stat_market.py` gộp với `newcomer_roles` thật của #145, #146, #148. Hành vi của #144 không đổi.

- RED: không có. Hành vi của issue không đổi; test chỉ thêm nguồn `learning_path` vào lời dựng `create_app` (nếu có) hoặc chạy lại trên fixture mới.
- GREEN (chạy lại thật, 2026-11-15): `uv run pytest -q tests/api/test_fr37_newcomer_roles.py tests/api/test_ad17_routes.py tests/api/test_ad17_web_fixtures.py` → 86 passed; `npx vitest run tests/fr37-newcomer-roles-fixture.test.ts tests/ad23-haido-keys.test.ts` → 14 passed; toàn bộ `uv run pytest -q` → 1113 passed, web `npm run test` → 221 passed.
