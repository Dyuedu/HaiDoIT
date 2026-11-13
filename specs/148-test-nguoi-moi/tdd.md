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
