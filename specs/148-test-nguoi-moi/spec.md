# Feature Specification: Test danh sách người mới

**Feature Branch**: `gh-148-test-nguoi-moi`

**Created**: 2026-11-13

**Status**: Implemented, đã sửa theo review (đợt 2, 2026-11-13), chờ merge.

**Input**: GitHub issue [#148](https://github.com/Dyuedu/HaiDoIT/issues/148) — Test the newcomer list. Phục vụ story #110 (US-A1). Kiểm lại #144–#147 sau khi review PR #291 chỉ ra các chỗ test còn hở (G1–G5).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mỗi AC của #110 có test, tên test mang mã FR/AD (Priority: P1)

Người bảo trì đổi `StatMarket.newcomer_roles`, `newcomer-roles-view.ts` hay trang `/insights` thì test đỏ nếu một AC của #110 sai. Tên test mang mã `fr37` (hành vi) hoặc `ad17` (hợp đồng API); test chữ số nằm trong `describe` "fr37 ad8 DEC-6 (#132)" (mã được thực thi là AD-8; #132 mở rộng kiểm chữ số sang câu soạn sẵn).

**Why this priority**: Hai AC của #148.

**Independent Test**: `tests/api/test_fr37_newcomer_roles_stat.py`, `web/tests/fr37-newcomer-list.test.tsx`.

**Acceptance Scenarios**:

1. **Given** fixture có cả dòng `shown` và `null_data`, **When** màn vẽ danh sách, **Then** đọc các dòng theo thứ tự DOM, không dòng `shown` nào đứng sau một dòng `null_data` (G1, #110 AC2).
2. **Given** nguồn `stat`, nhiều vai trò `shown` có n khác nhau và dòng `null_data` có nhiều tin entry hơn một dòng `shown`, **When** gọi API, **Then** mọi dòng `shown` vẫn đứng trước, và tỷ lệ mỗi dòng bằng entry chia n của chính vai trò đó, không chia cho tổng n (G1, F2, API).
3. **Given** fixture có số tin entry khác nhau, **When** màn vẽ, **Then** các dòng `shown` hiện đúng thứ tự máy chủ và số tin giảm nghiêm ngặt (G2, #110 AC1); MỌI dòng (không chỉ dòng 0) hiện đúng số tin entry, n của chính nó và tỷ lệ của chính nó kèm nhãn "số tin của vai trò" (F1).
4. **Given** nguồn `stat`, **When** gọi API, **Then** dòng xếp theo số entry giảm dần rồi theo mã (G2, API).
5. **Given** một chữ số xuất hiện ở bất kỳ chữ nào của trang ngoài danh sách số và khung "Nguồn và lưu ý" (tiêu đề, câu, `<span>`, chữ đang tải, chữ lỗi, thuộc tính `aria-label`, `title`, `alt`), **When** chạy test DEC-6, **Then** test đỏ (G3, F3). Phạm vi: duyệt mọi nút chữ và các thuộc tính đó của `/insights` ở năm trạng thái (đang tải, lỗi mạng có thử lại, không đọc được, `unknown_cell`, có số) và của trang giữ chỗ (ba kiểu `role`: hợp lệ, lạ, `all`). Loại ô số của `ol` và region "Nguồn và lưu ý" (nhận bằng `getByRole("region", { name })`; có test chứng minh số trong khung này không làm đỏ còn số trong tiêu đề thì có). Ca `unknown_cell` không gửi ngày snapshot vì ngày là số liệu của máy chủ, không phải câu.
6. **Given** `/ho-so-ky-nang?role=all`, **When** mở trang giữ chỗ, **Then** hiện "Không có vai trò này", không có "Mọi vai trò" (G4).
7. **Given** ô entry có n lớn hơn n của vai trò (dữ liệu hỏng), **When** gọi `newcomer_roles`, **Then** `RuntimeError` nêu mã vai trò và cả hai số; qua route là 500 `internal_error` (G5). Không cắt xuống 1, không trả tỷ lệ lớn hơn 1.
8. **Given** entry bằng n, **When** gọi, **Then** hợp lệ, tỷ lệ 1,0.
9. **Given** vai trò có đúng n = 30 (`min_sample`) và vai trò có n = 29, **When** gọi `StatMarket.newcomer_roles`, **Then** n = 30 là `shown` và n = 29 là `null_data` (F4, biên ngưỡng).

### Edge Cases

- Trước G5, entry > n ở vai trò đủ mẫu làm `Stat` ném `ValidationError` (route trả 500 `invalid_response`, không có `share > 1` ra ngoài); ở vai trò dưới ngưỡng thì không có tỷ lệ nên không ai bắt. Bảo vệ mới chặn cả hai ở một chỗ, sớm hơn, kèm tên vai trò.
- Fixture web phải trộn cả hai loại dòng và có số khác nhau; test tự khẳng định điều đó để không xanh rỗng.

## Bảng AC → test

| AC | Scenario | File test | Tên test | Loại |
|---|---|---|---|---|
| #110 AC1 sắp theo số tin | 3 | `web/tests/fr37-newcomer-list.test.tsx` | `fr37: #110 AC1 — dòng có tỷ lệ theo đúng thứ tự máy chủ, số tin cho người mới giảm dần` | mới |
| #110 AC1 | 4 | `tests/api/test_fr37_newcomer_roles_stat.py` | `test_fr37_thu_tu_dong_co_ty_le_truoc_roi_so_entry_giam_dan` | có sẵn (#146) |
| #110 AC1 tỷ lệ theo n riêng của vai trò | 2, 4 | `tests/api/test_fr37_newcomer_roles_stat.py` | `test_fr37_148_moi_dong_co_ty_le_theo_n_rieng_va_thu_tu_la_bat_bien` | mới (gộp test thứ tự của đợt 1 vào đây) |
| #110 AC1 web: mọi dòng đúng số, n, tỷ lệ | 3 | `web/tests/fr37-newcomer-list.test.tsx` | `fr37: #110 AC1 — MỌI dòng ghi đúng số tin entry-level, n của vai trò và tỷ lệ của chính dòng đó` | mới (đợt 2) |
| #110 AC2 biên 30/29 | 9 | `tests/api/test_fr37_newcomer_roles_stat.py` | `test_fr37_148_bien_nguong_mau_30_co_ty_le_29_null_data` | mới (đợt 2) |
| #110 AC1 mọi vai trò có dòng, số entry, tỷ lệ | — | `tests/api/test_fr37_newcomer_roles_stat.py` | `test_fr37_moi_vai_tro_cua_config_deu_co_dong`, `test_fr37_so_tin_entry_level_la_n_cua_o_toan_quoc_nhom_entry` | có sẵn (#145, #146) |
| #110 AC1 web hiện số, tỷ lệ, n; không sắp lại | — | `web/tests/fr37-newcomer-list.test.tsx` | `fr37: dòng đủ mẫu có số tin entry-level, tỷ lệ và n của vai trò`, `fr37: web không sắp xếp lại, kể cả khi API gửi thứ tự khác` | có sẵn (#147) |
| #110 AC2 dưới 30 tin ghi X/30 | — | `web/tests/fr37-newcomer-list.test.tsx` | `fr37: vai trò dưới 30 tin ghi chưa đủ dữ liệu (X/30), không có phần trăm` | có sẵn (#147) |
| #110 AC2 | — | `tests/api/test_fr37_newcomer_roles_stat.py` | `test_fr37_vai_tro_duoi_30_tin_khong_co_ty_le_nhung_van_co_so`, `test_fr37_nguong_mau_lay_tu_config` | có sẵn (#146) |
| #110 AC2 đứng sau dòng có tỷ lệ | 1 | `web/tests/fr37-newcomer-list.test.tsx` | `fr37: #110 AC2 — dòng chưa đủ dữ liệu đứng sau mọi dòng có tỷ lệ, theo thứ tự DOM` | mới |
| #110 AC2 | 2 | `tests/api/test_fr37_newcomer_roles_stat.py` | `test_fr37_148_moi_dong_co_ty_le_theo_n_rieng_va_thu_tu_la_bat_bien` | mới |
| #110 AC3 0 tin entry hiện 0, còn trong danh sách | — | `web/tests/fr37-newcomer-list.test.tsx` | `fr37: vai trò không có tin entry-level hiện 0 và vẫn ở trong danh sách` | có sẵn (#147) |
| #110 AC3 | — | `tests/api/test_fr37_newcomer_roles_stat.py` | `test_fr37_vai_tro_du_mau_khong_co_tin_entry_hien_0` | có sẵn (#146) |
| #110 AC4 chạm mở hồ sơ ở cấp entry | — | `web/tests/fr37-newcomer-list.test.tsx` | `fr37: chạm một vai trò mở hồ sơ kỹ năng của vai trò đó ở cấp mới vào nghề` | có sẵn (#147) |
| #110 AC4 trang giữ chỗ gọi tên vai trò, nói sprint sau | — | `web/tests/fr37-newcomer-list.test.tsx` | `fr37: gọi tên vai trò, cấp mới vào nghề, và nói hồ sơ kỹ năng có ở sprint sau`, `fr37: mã vai trò lạ thì không bịa tên vai trò` | có sẵn (#147) |
| #110 AC4 (G4) | 6 | `web/tests/fr37-newcomer-list.test.tsx` | `fr37: role=all không phải một vai trò, hiện 'Không có vai trò này' chứ không phải 'Mọi vai trò'` | mới |
| DEC-6 (#132) không số trong câu (G3) | 5 | `web/tests/fr37-newcomer-list.test.tsx` | `fr37 ad8: khung 'Nguồn và lưu ý' là region có tên, ...`, `fr37 ad8: /insights lúc đang tải, báo lỗi, không đọc được, unknown_cell và có số đều không có chữ số`, `fr37 ad8: trang giữ chỗ không có chữ số, cả khi vai trò lạ và role=all` | mới; thay test cũ chỉ đọc `insight-sentence` |
| AD-17 ô hỏng (G5) | 7, 8 | `tests/api/test_fr37_newcomer_roles_stat.py` | `test_fr37_ad17_o_hong_entry_lon_hon_n_thi_loi_noi_ro_vai_tro_va_hai_so`, `test_fr37_ad17_o_hong_entry_lon_hon_n_la_500_envelope_chuan`, `test_fr37_ad17_o_hong_cung_bi_chan_khi_vai_tro_duoi_nguong_mau`, `test_fr37_ad17_entry_bang_n_van_hop_le_tyle_bang_1` | mới |
| #148 AC1 mỗi AC của #110 có test | 1–8 | bảng này | — | — |
| #148 AC2 tên test mang mã FR/AD | — | mọi test trên | tên có `fr37`; test ô hỏng có thêm `ad17` | — |

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Thứ tự DOM của danh sách người mới có mọi dòng `shown` trước mọi dòng `null_data`, và số tin entry giảm nghiêm ngặt ở phần `shown` của fixture.
- **FR-002**: Nguồn `stat` xếp dòng: `shown` trước `null_data`, rồi số entry giảm dần, rồi mã vai trò; mỗi nhóm theo cùng quy tắc.
- **FR-003**: Test DEC-6 (mã AD-8) đọc mọi nút chữ và thuộc tính `aria-label`, `title`, `alt` của `/insights` (năm trạng thái) và trang giữ chỗ, trừ `ol` số và region "Nguồn và lưu ý".
- **FR-004**: `role=all` ở trang giữ chỗ là vai trò không hợp lệ.
- **FR-005**: `StatMarket.newcomer_roles` ném `RuntimeError` có mã vai trò, số entry và n khi entry > n; không cắt, không bỏ dòng.

## Success Criteria *(mandatory)*

- **SC-001**: `uv run pytest -q` (Postgres), `cd web && npm run test`, lint, build, `ruff check`, cổng `check_gates.py` xanh.
- **SC-002**: Mỗi test mới (trừ G5, có RED thật) đã bị một đột biến làm đỏ (xem `tdd.md`).

## Điểm còn mở

1. **DEC-6 và khung "Nguồn và lưu ý"** (#132): câu lưu ý độ phủ ("…trên 7 nguồn" với fixture) có số. Có được miễn khỏi DEC-6 hay không là câu hỏi mở ở #132. Test DEC-6 loại khung này (nhận bằng region có tên) và loại ô số của danh sách. Khi #132 quyết, sửa `narrative()` trong test.
2. **n = 0**: lời cho vai trò không có tin nào ("chưa có tin nào" thay vì "chưa đủ dữ liệu (0/30)") đổi chữ AC của #147, nên để ngoài #148.
3. **RED yếu của #147**: `specs/147-man-nguoi-moi/tdd.md` ghi RED chỉ là lỗi import. Đó là bản ghi quá khứ, không sửa.
4. **Cột ghi chú của bảng bản đồ trên điện thoại**: bố cục, không thuộc #148.
5. ~~Bảo vệ entry > n làm API trả 500 cho cả danh sách khi một ô hỏng.~~ **Đã quyết ngày 2026-11-13 (phương án A):** giữ nguyên. Ô hỏng là lỗi nội bộ, cả danh sách trả 500 `internal_error` và log, giống ca vai trò đủ mẫu vốn đã 500. AC "mọi vai trò đều có mặt" của #110 và #146 áp dụng khi `stat_cells` nhất quán. Ghi ở Edge Cases của `specs/146-tra-so-nguoi-moi/spec.md`.
6. **Ghi lại thông báo của `RuntimeError` ở `haido_api/errors.py`** (đợt 2, ngoài #148): chưa được log. `errors.py` dùng chung cho mọi route; client đã nhận 500 `internal_error` chung, không lộ gì. Làm riêng.
7. **Dòng `Status` của `spec.md` các issue khác** (#144-#147, #163, #280): hành vi không đổi nên không sửa ở #148.
8. **Hành vi bảo vệ entry > n** (G5) do người dùng quyết riêng; đợt 2 không đụng `haido_api/stat_market.py`.
