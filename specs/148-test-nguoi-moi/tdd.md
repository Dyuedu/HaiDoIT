# TDD: Test danh sách người mới

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Phần lớn test của issue này khóa hành vi đã có (hồi quy), nên không có RED tự nhiên; chứng minh chúng cắn bằng đột biến. Riêng G5 sửa hành vi nên có RED thật.

Lệnh:

```text
HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/haido_test uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q
cd web && npx vitest run tests/fr37-newcomer-list.test.tsx
```

## Các hành vi

1. G1 web: `fr37: #110 AC2 — dòng chưa đủ dữ liệu đứng sau mọi dòng có tỷ lệ, theo thứ tự DOM`.
2. G2 web: `fr37: #110 AC1 — dòng có tỷ lệ theo đúng thứ tự máy chủ, số tin cho người mới giảm dần`.
3. G3: hai test DEC-6 (`/insights`; trang giữ chỗ với ba kiểu `role`).
4. G4: `fr37: role=all không phải một vai trò, ...`.
5. G1, G2 API: `test_fr37_148_thu_tu_la_bat_bien_null_data_sau_cung_entry_giam_dan_roi_theo_ma`.
6. G5 API: `test_fr37_ad17_o_hong_entry_lon_hon_n_thi_loi_noi_ro_vai_tro_va_hai_so`, `..._la_500_envelope_chuan`, `test_fr37_ad17_o_hong_cung_bi_chan_khi_vai_tro_duoi_nguong_mau`, `test_fr37_ad17_entry_bang_n_van_hop_le_tyle_bang_1`.

## RED / khóa hồi quy (2026-11-13)

- Test 1–5 (G1–G4 và thứ tự API): mã sản phẩm đã đúng nên **xanh ngay, không có RED**. Ghi là khóa hồi quy. Web: `npx vitest run tests/fr37-newcomer-list.test.tsx` → 26 passed (22 cũ, trong đó test DEC-6 cũ được thay bằng hai test mới, cộng bốn test mới).
- G5, trước khi sửa `haido_api/stat_market.py`: `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → **3 failed, 12 passed**.
  - `..._thi_loi_noi_ro_vai_tro_va_hai_so`: không ném `RuntimeError`; thay vào đó `pydantic ValidationError: level_share phải nằm trong 0–1, nhận 1.6` từ `Stat` (backend 80/50).
  - `..._la_500_envelope_chuan`: 500 nhưng `code = invalid_response`, không phải `internal_error`.
  - `..._cung_bi_chan_khi_vai_tro_duoi_nguong_mau`: `DID NOT RAISE` (ui_ux entry 20, n 12 không có tỷ lệ nên không ai bắt). Đây là kẽ hở thật hơn cả điều ticket mô tả.
  - Test `entry_bang_n_van_hop_le` xanh sẵn (khóa biên).

Phát hiện: ticket nói API sẽ phục vụ `share > 1`. Thực tế `Stat` của schema đã từ chối `share > 1` và route trả 500 `invalid_response` (đã log). Điều chưa có là thông báo nêu vai trò và hai số, và chặn ở vai trò dưới ngưỡng.

## Đột biến (mỗi lần chạy thật, rồi hoàn lại bằng sao chép file gốc)

| # | Đột biến | Test đỏ |
|---|---|---|
| M1 | web: `buildNewcomerView` đưa dòng `null_data` lên đầu (`web/lib/newcomer-roles-view.ts`) | 5 failed, 21 passed: gồm test G1 và G2 mới |
| M2 | web: sắp dòng theo mã vai trò | 4 failed, 22 passed: gồm test G1 và G2 mới |
| M3 | thêm chữ số vào h2 (`Cửa vào cho 1 người mới`, `web/app/insights/page.tsx`) | 1 failed, 25 passed: `tiêu đề và mọi câu văn của /insights không có chữ số`. Test cũ (chỉ đọc `insight-sentence`) sẽ xanh |
| M4 | thêm chữ số vào h1 trang giữ chỗ (`Hồ sơ kỹ năng 2`, nhánh vai trò lạ) | 1 failed, 25 passed: test DEC-6 của trang giữ chỗ |
| M5 | `role=all` thành vai trò hợp lệ (bỏ `!== "all"`) | 1 failed, 25 passed: test G4 |
| A1 | API: bỏ khóa `null_data` khỏi `rows.sort` | lần đầu 1 failed (test cũ), test mới G1 vẫn xanh vì dữ liệu chưa đủ ép; sửa fixture (cho một dòng `shown` có ít entry hơn dòng `null_data`) rồi chạy lại: 2 failed, 13 passed, gồm test mới |
| A2 | API: đảo dấu số entry | 2 failed, 13 passed (test cũ và test mới) |
| A3 | API: bỏ khóa mã vai trò | 2 failed, 13 passed (test cũ và test mới) |

Mọi đột biến đã hoàn lại; `git diff` chỉ còn thay đổi có chủ đích.

## GREEN (2026-11-13)

- `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` → 15 passed (10 cũ + 5 mới).
- `uv run pytest -q` (Postgres) → 964 passed, không skip vì thiếu DB (trước đó 959).
- `-m determinism` với `PYTHONHASHSEED=0` và `1` → 6 passed mỗi lần.
- `uv run ruff check .` sạch; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11` → 8 pass, 2 skip (FR-22, FR-24, hoãn), 0 fail.
- `cd web && npm run lint` sạch; `npm run test` → 13 files, 193 passed (trước đó 189); `npm run build` xong.

## Đợt 2 — 2026-11-13 — sửa theo review

Lý do: review chỉ ra các test của đợt 1 còn hở (F1–F5). Đợt 1 giữ nguyên. Đợt này chỉ sửa test và spec, không sửa code sản phẩm (kể cả bảo vệ entry > n của G5). DB riêng `fx148_test` (`HAIDO_TEST_DATABASE_URL=postgresql+psycopg://haido:haido_local@127.0.0.1:5433/fx148_test`), xóa khi xong.

### Hành vi thêm

1. F1 web: `fr37: #110 AC1 — MỌI dòng ghi đúng số tin entry-level, n của vai trò và tỷ lệ của chính dòng đó` (lặp qua mọi dòng, dùng `formatPercent`, `formatCount` của sản phẩm, nhãn "số tin của vai trò").
2. F2 API: `test_fr37_148_moi_dong_co_ty_le_theo_n_rieng_va_thu_tu_la_bat_bien` (4 vai trò `shown` có n khác nhau; gộp thứ tự của test #148 đợt 1, test đó bị xóa vì không bắt đột biến nào mà `test_fr37_thu_tu_dong_co_ty_le_truoc...` bỏ sót).
3. F3 web: `narrative()` duyệt mọi nút chữ và thuộc tính `aria-label`, `title`, `alt`, loại `ol` và region "Nguồn và lưu ý" thật (`queryByRole("region", { name })`); ba test `fr37 ad8: ...` (khung là region và `narrative()` phân biệt số trong khung với số trong tiêu đề; `/insights` ở năm trạng thái; trang giữ chỗ ba kiểu `role`).
4. F4 API: `test_fr37_148_bien_nguong_mau_30_co_ty_le_29_null_data`.
5. F5: `_set_entry_n` kiểm `rowcount == 1`.

### RED / khóa hồi quy

Mã sản phẩm đã đúng nên các test xanh ngay, không có RED tự nhiên; chứng minh bằng đột biến. Lúc mới viết: `uv run pytest tests/api/test_fr37_newcomer_roles_stat.py -q` có một lần đỏ do sai kỳ vọng của chính test (vai trò 0 entry xếp theo mã, `ai_ml` đứng trước `embedded`), đã sửa kỳ vọng; sau đó 16 passed. Web: 28 passed.

### Đột biến (chạy thật, hoàn lại bằng `git checkout` file sản phẩm)

| # | Đột biến | Kết quả |
|---|---|---|
| F1a | `formatPercent(data.rows[0].share.value)` cho mọi dòng `shown` (`web/lib/newcomer-roles-view.ts`) | 2 failed, 26 passed: test F1 mới và `vai trò không có tin entry-level hiện 0...` |
| F1b | đổi n của dòng 4 và dòng 5 (chỉ `nText`) | 1 failed, 27 passed: chỉ test F1 mới |
| F2 | `entry_n / max(1, sum(tổng n mọi vai trò))` (`haido_api/stat_market.py`) | 2 failed, 14 passed: test nhiều vai trò mới và test biên 30/29; `test_fr37_thu_tu_dong_co_ty_le_truoc...` cũ vẫn xanh, nên chỉ test mới bắt được |
| F4 | `min_sample=min_sample + 1` ở chỗ gọi `suppression_for` | 1 failed, 15 passed: test biên 30/29 |
| F3a | chữ số trong chữ đang tải (`Đang tải 3 số liệu…`) | 1 failed: `fr37 ad8: /insights lúc đang tải, ...` |
| F3b | chữ số trong `UNREADABLE` (`Thử lại sau 5 phút.`) | 1 failed: cùng test |
| F3c | `title="3 tin"` trên liên kết "Quay lại" của trang giữ chỗ (ngoài `ol`; liên kết trong `ol` nằm ngoài phạm vi) | 1 failed: `fr37 ad8: trang giữ chỗ ...` |
| F3c' | `aria-label="3 tin"` trên một phần tử ngoài `ol` của `/insights` | 1 failed: test năm trạng thái |
| F3d | chữ số trong `<span>` của câu giới thiệu | 1 failed: test năm trạng thái |
| F3e | thêm chữ số vào h2 của khung "Nguồn và lưu ý" | 2 failed (tên region đổi nên không tìm thấy; test chú thích riêng và test năm trạng thái): không bắt nhầm số của khung như câu văn |

Mọi đột biến đã hoàn lại; `git diff` chỉ còn thay đổi có chủ đích.

Ngày snapshot ở ca `unknown_cell` là số liệu, nên ca đó gửi `snapshot_date: null`; ca có ngày vẫn có test riêng ở `fr37: unknown_cell báo lỗi kèm ngày...`.

### GREEN (2026-11-13)

- `uv run pytest -q` (DB riêng `fx148_test`): 965 passed, không skip vì thiếu DB (đợt 1: 964; test thứ tự cũ #148 gộp, thêm test biên 30/29 và test nhiều vai trò).
- `-m determinism` với `PYTHONHASHSEED=0` và `1`: 6 passed mỗi lần.
- `uv run ruff check .` sạch; `check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11`: 8 pass, 2 skip (hoãn), 0 fail.
- `cd web && npm run lint` sạch; `npm run test`: 13 files, 195 passed (đợt 1: 193); `npm run build` xong.
- Web `fr37-newcomer-list.test.tsx`: 28 passed (đợt 1: 26).
- Chỉ đụng hai file test của #148 và `specs/148-test-nguoi-moi/`; không đụng file sản phẩm, nên không cần đợt mới ở spec của issue khác.

## Đợt 2026-11-15 — gộp main vào #212 (thêm nguồn `learning_path`)

Lý do: nhánh #212 thêm `"learning_path": fake` vào lời dựng `create_app` ở `tests/api/test_fr37_newcomer_roles_stat.py` (file dùng chung của #148); `StatMarket.newcomer_roles` và bảo vệ entry > n giữ nguyên.

- RED: không có. Hành vi của issue không đổi; test chỉ thêm nguồn `learning_path` vào lời dựng `create_app` (nếu có) hoặc chạy lại trên fixture mới.
- GREEN (chạy lại thật, 2026-11-15): `uv run pytest -q tests/api/test_fr37_newcomer_roles_stat.py tests/api/test_fr37_newcomer_roles.py tests/api/test_ad17_web_fixtures.py` → 42 passed; toàn bộ `uv run pytest -q` → 1113 passed.

## Đợt 2026-11-16 (#111, #152)

Lý do: test trang giữ chỗ trong `web/tests/fr37-newcomer-list.test.tsx` (khối DEC-6 của đợt 2026-11-13) đổi theo trang hồ sơ kỹ năng thật của #152; xem `specs/147-man-nguoi-moi/tdd.md`. Các test thứ tự, `null_data`, `role=all` của #148 không đổi.

- GREEN: `npx vitest run` → 21 files, 281 passed.

## Đợt 2026-11-17 (#166): file dùng chung đổi, hành vi của issue này không đổi

Lý do: #166 (hình response `skill-roles`) sửa file mà issue này từng đụng: `haido_api/stat_market.py` (thêm `StatMarket.skill_roles`) và `tests/api/test_fr37_newcomer_roles_stat.py` (lời dựng `create_app`). Thay đổi: bảo vệ entry > n của `newcomer_roles` không đổi.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #166 nằm ở `specs/166-hinh-ky-nang-theo-vai-tro/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `t166_test`) → 1510 passed, không skip; `cd web && npx vitest run` → 22 files, 293 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

## Đợt 2026-11-17 (#151, #106, #103): file dùng chung đổi, AC của issue này không đổi

Lý do: tỷ lệ kỹ năng thật (#151), phép 2 `select_cell` (#106) và ràng buộc lớp đọc (#103) sửa file mà issue này từng đụng:

  - `haido_api/stat_market.py` (thêm `skill_rates` thật, đọc `stat_skill_rates`);

Hành vi và AC của issue này không đổi: thay đổi chỉ thêm (phương thức `skill_rates` thật, trường `order` có mặc định, một biến môi trường ở prod, một đoạn tài liệu); `city_shares`, `newcomer_roles`, `learning_path`, `skill_roles` của `StatMarket` giữ nguyên. Chi tiết: `specs/151-ty-le-ky-nang-that/plan.md`.

- RED: không có, vì không có hành vi nào của issue này đổi; không test nào của issue này đổi kỳ vọng. RED của #151, #106, #103 nằm ở `specs/151-ty-le-ky-nang-that/tdd.md`, `specs/106-chon-o-quay-ve/tdd.md`, `specs/103-api-doc-ty-le-that/tdd.md`.
- GREEN (chạy thật, 2026-11-17): `uv run pytest -q` (Postgres thật, DB `fx151_test`, không skip) → 1580 passed; `cd web && npx vitest run` → 298 passed; `tools/gates/check_gates.py --require AD-1 AD-17 AD-25 AD-2 AD-7 FR-25/31/47 AD-11 FR-22 FR-24` → 10 pass, 0 skip, 0 fail.

Cập nhật sau review (đợt 2, 2026-11-17): trong `StatMarket` chỉ `skill_rates` đổi thêm (404 khi ô không có hàng tỷ lệ, `n_scanned` nhất quán, chữ nhãn); hành vi và AC của issue này vẫn không đổi. RED và GREEN: `specs/151-ty-le-ky-nang-that/tdd.md` đợt 2.

## Đợt 2026-11-17 (#113, #169)

Lý do: test DEC-6 "lúc đang tải…" của #148 trong `web/tests/fr37-newcomer-list.test.tsx` đọc `getByRole("status")` trên cả trang; từ #169 trang có hai vùng trạng thái. Test đọc vùng của mục người mới; điều nó kiểm không đổi. Xem `specs/147-man-nguoi-moi/tdd.md`.

- GREEN: `npx vitest run` → 25 files, 328 passed.

## Đợt #168 (2026-11-17): file dùng chung đổi, AC của issue này không đổi

Lý do: #168 cài `StatMarket.skill_roles` đọc `stat_skill_rates` (số thật cho `skill-roles`), sửa file mà issue này từng đụng: `haido_api/stat_market.py`.
Hành vi và AC của issue này không đổi; thay đổi chỉ thêm phương thức `skill_roles` thật và chữ mô tả. RED, GREEN và mutation: `specs/168-ky-nang-vai-tro-that/tdd.md`.

## Đợt #102 (2026-11-19): θ có phiên bản, AC của issue này không đổi

Lý do: #102 đóng băng θ (`config/theta.toml`, `theta-1` = 0,3/0,1), thêm `snapshots.theta_version` (migration 0010) và `meta.thresholds.theta_version`, sửa file mà issue này từng đụng: `haido_api/stat_market.py`.
Giá trị θ không đổi nên số, nhóm và hành vi của issue này không đổi; test chỉ thêm `theta_version` vào ngưỡng hoặc đổi head migration mong đợi sang 0010. RED, GREEN và đột biến: `specs/102-dong-bang-theta/tdd.md`.

## Đợt #327, #328 (2026-11-19): thêm route toàn cảnh thị trường, AC của issue này không đổi

Lý do: #327 và #328 thêm `GET /api/v1/market-overview` và sửa file mà issue này từng đụng (`haido_api/schemas/market.py`, `fake_market.py`, `market_source.py`, `routes/market.py`, `stat_market.py`, `fixtures/fake_market.json`, `docs/api/envelope-meta.md`, `tests/api/test_ad17_routes.py`). Thay đổi chỉ thêm: schema, phương thức, route, một mục fixture, một dòng `SAMPLE_QUERY`; route cũ và số của chúng không đổi.

- RED và GREEN: `specs/327-tong-quan-thi-truong-api/tdd.md`. `uv run pytest -q` → 1336 passed, 304 skipped.

## Đợt #329 (2026-11-19): /insights thêm toàn cảnh ở đầu trang, AC của issue này không đổi

Lý do: #329 thêm mục toàn cảnh thị trường lên đầu `/insights` (`web/app/insights/page.tsx`). Mock `fetch` trong test của mục này (`web/tests/fr37-newcomer-list.test.tsx`, `web/tests/helpers/skill-roles.ts`) trả "đang tải" mãi cho `/api/v1/market-overview`, để test vẫn chỉ kiểm mục của issue này. Hành vi và AC không đổi.

- RED và GREEN: `specs/329-man-tong-quan/tdd.md` (`npx vitest run` → 366 passed).
