# TDD: Thêm bảy vai trò vào danh sách vai trò (#284)

## Lệnh test

```bash
export HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test
uv run pytest tests/deploy/test_gh284_vai_tro_moi.py tests/deploy/test_gh162_ban_do_doc_snapshot_that.py \
  tests/steps/test_gh284_aggregate_vai_tro_moi.py -q
npx vitest run tests/fr33-role-chips-new-roles.test.tsx   # trong web/
```

## Danh sách hành vi

1. `roles` của config có 17 mã theo thứ tự đã chốt; chip web là `all` cộng 17 mã đó, nhãn tiếng Việt.
2. Mỗi nhãn vai trò của bộ phân loại có mã riêng trong `[labels.role]`; `[report_as]` rỗng; `classify_version` không đổi.
3. Tin của vai trò mới vào ô của mã đó; `other` chỉ còn chức danh chung.
4. Vai trò mới có đủ hàng theo cấp, số năm, phạm vi; API trả 200 và làm mờ thành phố dưới 30 tin như vai trò cũ.
5. Bản giả có city-shares (`all` và `entry`) và dòng `newcomer_roles` cho mỗi mã mới; `newcomer_roles` theo thứ tự `roles`; fixture web sinh lại khớp.
6. Bộ chọn vai trò: 18 nút, `flex-wrap`, Tab đi qua đủ, 360px không cuộn ngang.

## RED (2026-11-13)

Chạy thật, code và config chưa đổi.

- `uv run pytest tests/deploy/test_gh284_vai_tro_moi.py tests/deploy/test_gh162_ban_do_doc_snapshot_that.py tests/steps/test_gh284_aggregate_vai_tro_moi.py -q` → **7 failed, 7 passed**: 4 test deploy (`roles` 10 mã, `report_as` còn bảy dòng, chip web 11, bản giả không có mã mới), 3 test bước aggregate (không có hàng `fullstack`, `data_scientist`…; API 404 cho `role=fullstack`). 7 test của #162 xanh (web và config vẫn khớp nhau ở 10 mã).
- `npx vitest run tests/fr33-role-chips-new-roles.test.tsx` → **2 failed, 1 passed**: 11 nút thay vì 18, không có nút "Fullstack". Test Tab xanh sẵn vì nó chỉ kiểm thứ tự focus giữa các nút đang có.

## GREEN (2026-11-13)

- `config/rules.toml`: 17 mã, bảy nhãn mới, `config_version` `2026-11-13.2`. `config/classify.toml`: `[report_as]` rỗng, `classify_version` giữ nguyên (dòng đầu file ghi ngoại lệ cho bảng này).
- `web/lib/labels.ts`: bảy chip mới.
- `haido_api/fixtures/fake_market.json`: `city_shares` (`all` và `entry`, vì test của #163 đòi mỗi vai trò của bản giả có cả hai), ô sáu phạm vi ở hai cấp và dòng `newcomer_roles` cho bảy mã, số lấy từ snapshot 12/11 của bản sao local; file chỉ có dòng thêm. Sinh lại `web/tests/fixtures/newcomer-roles.json` từ API giả.

Sửa test trong lúc GREEN: `fr33-role-chips-new-roles.test.tsx` tìm "34 tin" nhưng màn không hiện tổng; đổi sang tìm dòng "Hà Nội: … 19 tin".

Test cũ đổi vì danh sách vai trò dài hơn (không AC nào đổi):

| Test | Issue | Vì sao |
|---|---|---|
| `tests/core/test_ad10_rules_config.py` (2 test) | #6 | Danh sách `roles` và bảng `[labels.role]` có bảy mã mới |
| `tests/core/test_gh283_classify_config.py::test_gh283_moi_nhan_vai_tro_co_ma_trong_rules_sau_report_as` | #283 | `report_as` rỗng; nhãn mới có mã riêng |
| `tests/steps/test_gh283_ingest_classify.py::test_gh283_aggregate_dung_nhan_da_luu` | #283 | Data Scientist vào `data_scientist`, không còn vào `ai_ml` |
| `tests/steps/test_dat20_aggregate_step.py::test_dat20_determinism_hai_lan_aggregate_ra_cung_hang`, `tests/test_dat20_cli.py` | #93 | Số ô 18 × 6 × 9 × 6 = 5832, tỷ trọng 18 × 5 × 9 × 6 = 4860 |
| `web/tests/fr33-city-shares-view.test.ts`, `web/tests/fr33-map-screen.test.tsx` (thứ tự Tab) | #162, #163 | Danh sách chip có 18 nút |

## Kiểm trên bản sao local và trình duyệt

Gỡ snapshot 12/11 khỏi bản sao `haido_preview` rồi chạy lại (`ingest` 14,3 giây, thêm lại 6255 dữ kiện vì snapshot bị gỡ; `aggregate` 4,0 giây, 5832 ô, 4860 tỷ trọng). Mỗi vai trò (cụm, mọi cấp / mới vào nghề): BA / PO / PM 791 / 128, Hạ tầng & IT support 485 / 132, Bảo mật 186 / 36, Fullstack 179 / 34, Phát triển game 99 / 43, UI/UX 77 / 21, Khoa học dữ liệu 28 / 5. `other` từ 2044 xuống **227** (6,1% của 3748 cụm IT; SC-001 đạt).

Chrome headless qua DevTools Protocol, khung 360 × 780, `http://localhost:3000`: 18 chip vai trò, chip thấp nhất 44px, `scrollWidth` 360 / `clientWidth` 360 trước và sau khi bấm "Fullstack"; bấm "Fullstack" thì chip được chọn và dòng Hà Nội hiện "70,6%, 24 tin. Cỡ mẫu nhỏ (n = 24 < 30)".

## Kết quả cuối

| Lệnh | Kết quả |
|---|---|
| `uv run pytest -q` (Postgres local) | **908 passed** |
| hai lượt `-m determinism` | 6 passed mỗi lượt |
| `uv run ruff check .` | All checks passed |
| cổng `--require AD-1 AD-17 AD-25 AD-2 AD-7` | 8 pass, 2 skip, 0 fail |
| `npx vitest run` (web) | **163 passed** |
| `npm run lint`, `npx tsc --noEmit`, `npm run build` | sạch |

## Đợt 2026-11-13 — #285 34 tỉnh, Remote, Nước ngoài

Lý do: #285 đổi mã nơi (bản giả thay `other` bằng `hai_phong`, thêm `remote`, `abroad` cho mọi vai trò, kể cả bảy vai trò mới). Không AC nào của issue này đổi.

- RED: `test_gh284_vai_tro_moi_co_du_hang_theo_cap_so_nam_pham_vi` đỏ vì số hàng mỗi vai trò nay là `always_cities` + vn.
- GREEN: sửa kỳ vọng theo mã nơi mới; `uv run pytest -q` → 947 passed; `npx vitest run` → 166 passed.
