---
title: 'GH-46 [1.15] Xem tỷ trọng ba thành phố'
type: 'feature'
created: '2026-11-06'
status: 'done'
baseline_commit: 'e18038e91430f5404f08a851082647bea4f1e585'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/DOD.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-11-03/DESIGN.md'
  - '{project-root}/docs/api/envelope-meta.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Trang `/` (Bản đồ) hiện chỉ có tiêu đề giữ chỗ của #1. Sinh viên chưa thấy được Hà Nội, TP.HCM, Đà Nẵng chiếm bao nhiêu phần tin của vai trò mình chọn, kèm cỡ mẫu, nguồn và ngày snapshot.

**Approach:** Dựng màn Bản đồ ở lối **Biểu đồ 2D** và lối **Bảng**. Cả hai đọc cùng một response `GET /api/v1/city-shares?role=` qua proxy `/api/*` của #1, và không tự tính số nào. Hôm nay màn chạy trên dữ liệu giả của #2. Khi #69 cắm nguồn `stat`, màn chạy trên số thật mà không sửa code web, trừ file nhãn khi #68 chốt mã thật. Nút 3D có mặt nhưng tắt, chờ 1.17.

## Boundaries & Constraints

**Always:**
- **Cách tải:** màn là component phía trình duyệt (`"use client"`), gọi `/api/v1/city-shares?role=` sau khi trang mở. Server chỉ render header và trạng thái "Đang tải số liệu…", nên `next build` không gọi API và không đóng băng số vào HTML.
- **Không tự tính:** mọi con số lấy từ envelope: `share.value`, `share.display`, `meta.cells[cell_id].n`, `meta.thresholds.min_sample`, `meta.cells[data.total_cell_id].n`. Web không cộng, không chia, không so `n` với ngưỡng; trạng thái hiển thị chỉ đọc từ `display`.
- **Mặc định:** mở trang thì vào lối 2D, vai trò "Tất cả" (`all`). Lối "Bảng" hiện đúng bộ số đó. Cụm "3D / Biểu đồ 2D / Bảng" có mặt ở mọi khổ màn hình.
- **Thanh:** chỉ ba thanh Hà Nội, TP.HCM, Đà Nẵng; Đà Nẵng luôn có mặt. Độ rộng thanh = `share.value × 100%` của cả rãnh, không co theo giá trị lớn nhất, không có độ rộng tối thiểu; rãnh luôn hiện, kể cả khi tỷ trọng là 0. "Khác" và phần không xác định thành phố không thành thanh; mỗi phần một dòng riêng trong chú thích, kèm tỷ trọng và `n`.
- **Mẫu nhỏ** (`display = low_sample_shown`): thanh mờ và phủ sọc, kèm nhãn luôn hiện "Cỡ mẫu nhỏ (n = X < N): số liệu chỉ để tham khảo" (X là `n`, N là `min_sample`). Phần trăm chỉ hiện khi trỏ chuột, chạm hoặc focus. Dòng chú thích "Khác" và "không xác định" theo cùng quy tắc.
- **Bảng:** cột Nơi, Tỷ trọng, Số tin, Ghi chú; có cả dòng Khác và không xác định. Dòng có `display` khác `shown` không hiện tỷ trọng, chỉ ghi "chưa đủ dữ liệu", nhưng vẫn ghi `n`. Dòng tổng ghi cố định "100%" và `n` của `data.total_cell_id`, không cộng các dòng.
- **Định dạng:** kiểu Việt Nam. Phần trăm một chữ số thập phân với dấu phẩy ("47,0%"), làm tròn đúng một lần ở lớp hiển thị. Ngày `dd/mm/yyyy`.
- **Chú thích luôn hiện** ở mọi trạng thái có dữ liệu, kể cả trên điện thoại: `meta.sources` in đúng như API gửi, ngày `snapshot_date`, và mọi câu trong `meta.coverage_notes` in nguyên văn. Snapshot `partial` thì ghi thêm "Nguồn lỗi ở snapshot này: …" với `sources_failed`.
- **Ngưỡng nhóm:** màn này không hiện nhóm kỹ năng. Nếu sau này hiện, phải đọc `meta.thresholds.theta_core` và `theta_common` (30% và 10%), không viết cứng.
- **Nhãn:** mã và nhãn tiếng Việt của vai trò và thành phố nằm trong `web/lib/labels.ts`. Mã nào không có trong file thì hiện chính mã đó.
- **Đổi vai trò:** hiện trạng thái đang tải thay cho số cũ. Response về muộn của vai trò cũ thì bỏ (`data.role` phải bằng vai trò đang chọn).
- **Lỗi:** theo bảng lỗi ở Design Notes. Thông báo lỗi có `role="alert"`; trạng thái tải có `role="status"`.
- **Bàn phím và trình đọc màn hình:**
  - Chip vai trò và cụm lối xem là `<button aria-pressed>`. Nút 3D dùng `aria-disabled="true"` (không dùng `disabled`), nối với chú thích "Bản đồ 3D sắp có" bằng `aria-describedby`.
  - Mỗi dòng thành phố ở lối 2D là một `<button>` cao tối thiểu 44px. Tên đọc được của nó luôn gồm tên nơi, phần trăm, `n`, và câu mẫu nhỏ nếu có.
  - Phần trăm hiện ra nằm trong chính button đó, nên di chuột lên phần trăm không làm nó biến mất. Chạm hoặc bấm lần nữa, hoặc nhấn Esc, thì ẩn lại.
  - Vùng bấm tối thiểu 44px. Vòng focus `outline: 2px solid #C5F36A; outline-offset: 2px`. `prefers-reduced-motion` tắt mọi transition.
- **Giao diện:** màu, chữ, khoảng cách lấy từ token của `DESIGN.md`, khai một lần trong `globals.css`. Số, `n`, ngày, phần trăm dùng JetBrains Mono. Mốc điện thoại 640px làm bằng CSS, không dùng `matchMedia`.

**Never:**
- Không thêm thẻ `<a aria-current="page">` nào, và không thêm thẻ `<nav>` thứ hai trên `/`. Job `smoke` đếm đúng một thẻ `<a aria-current>` và bốn thẻ `<a>` trong nav.
- Không thêm thư viện vẽ biểu đồ. Không gọi API trực tiếp, bỏ qua proxy `/api/*`. Không dùng `localStorage`.
- Không làm 3D (1.17), bảng chi tiết thành phố và nút "Xem chi tiết" (1.16), nút sang Cố vấn (Epic 2).
- Không sửa `haido_api`, schema hay `docs/api/openapi.json`.

**Quyết định (06/11/2026):**
- Danh sách vai trò của các chip nằm trong một file của `web/`, mã và nhãn khớp bản giả (`all` "Tất cả", `data_ai` "Data/AI", `backend` "Backend"). File này là `web/lib/labels.ts`, chứa luôn nhãn thành phố. Khi #68 chốt mã thật, chỉ sửa file này.
- Giữ một spec dù dài hơn mức khuyến nghị.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Mở trang | API giả, mở `/` | Lối 2D; chip "Tất cả" `aria-pressed="true"`; ba thanh HN, HCM, ĐN theo `share.value`; chú thích có nguồn, ngày snapshot, bốn câu `coverage_notes` | N/A |
| Mẫu nhỏ ở 2D | `role=data_ai`: ĐN `low_sample_shown`, n = 21 | Thanh ĐN mờ, có sọc, nhãn mẫu nhỏ với n = 21; % chỉ hiện khi trỏ, chạm, focus; Esc ẩn | N/A |
| Mẫu nhỏ ở Bảng | Như trên, chọn "Bảng" | Ô tỷ trọng ĐN ghi "chưa đủ dữ liệu", cột số tin ghi 21 | N/A |
| Khác, không xác định | `role=backend`: Khác n = 5, không xác định n = 8 | Hai dòng chú thích riêng, mỗi dòng có nhãn mẫu nhỏ; bảng có hai dòng này | N/A |
| Dòng tổng | `role=all`, làm tròn từng dòng cộng ra 100,1% | Dòng tổng ghi "100%" và n = 3.586; có chú thích lệch do làm tròn | N/A |
| Tỷ trọng 0 | Một thành phố `share = 0`, n = 0, `low_sample_shown` | Rãnh trống vẫn hiện; button focus được; nhãn "Cỡ mẫu nhỏ (n = 0 < 30)…" | N/A |
| Mọi dòng mẫu nhỏ | Envelope có năm dòng đều `low_sample_shown` | Mọi thanh mờ có nhãn; chú thích vẫn đầy đủ | N/A |
| Đổi vai trò | Bấm chip vai trò khác | Trạng thái đang tải, rồi số của vai trò mới; `aria-pressed` đổi theo | N/A |
| Đổi vai trò nhanh | Bấm A rồi B, response của A về sau | Chỉ hiện số của B | Bỏ response của A |
| Bấm 3D | Bấm hoặc Enter trên nút 3D | Lối không đổi; nút vẫn `aria-disabled="true"`, chú thích "Bản đồ 3D sắp có" | N/A |
| Snapshot cũ | API trả `snapshot_date` cũ hơn hôm nay (đêm pipeline lỗi) | Hiện đúng ngày của snapshot đó | N/A |
| Snapshot partial | `snapshot_status = partial`, `sources_failed = [x]` | Chú thích ghi "Nguồn lỗi ở snapshot này: x" | N/A |
| API tắt | Proxy trả 502 `api_unavailable` | Hiện `error.message`, nút "Thử lại"; không có thanh hay bảng | Theo bảng lỗi |
| Vai trò không có ô | 404 `unknown_cell` | Hiện `error.message` kèm ngày `snapshot_date` nếu có; chip vẫn đổi được | Theo bảng lỗi |
| Envelope hỏng | Thiếu dòng `da_nang`, thiếu `meta`, hoặc body không phải JSON | "Không đọc được số liệu. Thử lại sau.", nút "Thử lại" | Theo bảng lỗi |
| Điện thoại | Khung nhìn hẹp hơn 640px | Danh sách thành phố kèm thanh, gợi ý "Mở trên máy tính để xem bản đồ đầy đủ."; cụm lối xem và chú thích vẫn hiện | N/A |
| Bàn phím | Nhấn Tab từ đầu trang | Thứ tự: nav → chip vai trò → cụm lối xem → từng dòng thành phố; mỗi điểm dừng có vòng focus | N/A |

</frozen-after-approval>

## Code Map

- `web/app/page.tsx` -- trang `/` giữ chỗ của #1; thay bằng màn Bản đồ. Server component chỉ render khung; phần số là component phía trình duyệt.
- `web/app/layout.tsx`, `web/app/globals.css` -- font Be Vietnam Pro qua `next/font`; mới có 6 biến màu. Rà soát #1 để lại cho #46: màu viết cứng, thiếu `:focus-visible`, thiếu `color-scheme`.
- `web/app/components/app-header.tsx` -- nav và `aria-current` của #1. Chỉ đổi màu viết cứng sang token, không đổi cấu trúc.
- `web/app/api/[...path]/route.ts` -- proxy chỉ nhận `GET`, chuyển nguyên status và body của API; API tắt hoặc quá 10 giây thì trả 502 `api_unavailable`.
- `docs/api/envelope-meta.md`, `docs/api/openapi.json` -- hợp đồng `{data, meta}`, `Stat`, `CellMeta`, `cell_id` dạng `<scope>.<role>`, `data.total_cell_id`, các mã lỗi. Mã vai trò, thành phố hiện là chuỗi tạm.
- `haido_api/fixtures/fake_market.json` -- ba vai trò: `data_ai` (ĐN n = 21), `backend` (ĐN 9, Khác 5, không xác định 8), `all` (tổng n = 3.586).
- `_bmad-output/implementation-artifacts/spec-gh-69-tinh-va-doc-ty-trong-thanh-pho.md` -- envelope thật sẽ có `n_by_measure = {}`, có thể có dòng `n = 0`, và bốn câu `coverage_notes`.
- `web/package.json`, `web/package-lock.json`, `web/tsconfig.json` -- Next 16.4.4, React 19.3.1, Tailwind 4.3.4; chưa có test. `tsconfig` gồm mọi `**/*.ts(x)`, nên `next build` kiểm kiểu cả file test.
- `.github/workflows/ci.yml` -- job `web` chạy `npm ci`, `lint`, `build`. Job `smoke` đếm `<a aria-current>` trên `/` bằng regex tham lam trên HTML một dòng.
- `tools/gates/check_gates.py` -- cổng câu chữ bị cấm (FR-25/31/47) quét `web/`; cổng AD-23 chặn `localStorage` ngoài module khóa đóng.

## Tasks & Acceptance

**Cách làm: TDD** theo `docs/templates/test-driven-tdd/test-driven-development.md` (red → green → refactor). Mỗi cặp task "test" rồi "code":
1. Viết test trước.
2. Chạy `npm --prefix web run test` và thấy **đỏ vì đúng lý do**: chưa có code hoặc hành vi chưa đúng, không phải lỗi cú pháp hay import sai.
3. Ghi một dòng vào Implementation Notes: tên test, số test đỏ, lý do đỏ.
4. Viết code vừa đủ cho xanh, rồi dọn code mà vẫn giữ xanh.

Không viết code của một cặp trước khi test của cặp đó đã đỏ.

Test cho mọi dòng I/O Matrix, trừ "Điện thoại" và phần vòng focus (kiểm tay). Dùng cả envelope giả và một envelope có hình như output của #69 (`n_by_measure = {}`, một dòng `n = 0`, bốn câu `coverage_notes`). Tên test chứa `fr33`, `fr36` hoặc `ad17` (DoD dòng 11).

**Execution:**
- [x] `web/package.json`, `web/package-lock.json`, `web/vitest.config.mts` -- thêm Vitest, `@vitejs/plugin-react`, jsdom, `@testing-library/react`, `@testing-library/user-event`; script `test`. File test import API của Vitest tường minh vì `next build` kiểm kiểu chúng. Kiểm hạ tầng bằng một test rỗng chạy được -- hạ tầng TDD
- [x] Test đỏ: `web/tests/fr33-city-shares-view.test.ts` -- các dòng Matrix về số và chữ: ba thanh, Khác và không xác định, mẫu nhỏ, tỷ trọng 0, mọi dòng mẫu nhỏ, dòng tổng "100%" kèm n = 3.586, định dạng vi-VN, snapshot cũ và `partial`, nhãn lấy từ `labels.ts` và mã lạ hiện nguyên mã -- RED
- [x] Code xanh: `web/lib/labels.ts`, `web/lib/city-shares-view.ts` -- hàm thuần envelope → ba thanh, hai dòng chú thích, hàng bảng, dòng tổng, chú thích snapshot; chỉ đọc `value`, `display`, `n`, `min_sample` -- GREEN
- [x] Test đỏ: `web/tests/ad17-city-shares-client.test.ts` -- hàm gọi API trả dữ liệu, hoặc từng loại lỗi trong bảng lỗi (502, 404 `unknown_cell`, mã lỗi khác, `fetch` bị từ chối, body không phải JSON, envelope thiếu `meta` hoặc thiếu dòng `da_nang`) -- RED
- [x] Code xanh: `web/lib/city-shares.ts` -- kiểu TypeScript của envelope theo `openapi.json`; hàm gọi `/api/v1/city-shares?role=` qua proxy -- GREEN
- [x] Test đỏ: `web/tests/fr33-map-screen.test.tsx`, `web/tests/fr36-snapshot-caption.test.tsx` -- các dòng Matrix về tương tác: mở trang, chip "Tất cả", đổi vai trò, đổi vai trò nhanh, bấm 3D (`aria-disabled`, `aria-describedby`), lối Bảng, trỏ hoặc focus hiện %, Esc ẩn, trạng thái tải và lỗi (`role="status"`, `role="alert"`), bốn câu chú thích kể cả `posting_not_demand`, `big_city_bias`, `salary_disclosed_only` -- RED
- [x] Code xanh: `web/app/components/map/`, `web/app/page.tsx` -- chip vai trò, cụm lối xem, danh sách thanh (`<figure>` chứa `<ul>`, mỗi dòng một `<button>`), bảng, chú thích snapshot, trạng thái tải và lỗi; `page.tsx` ghép lại -- GREEN, AC 1.15
- [x] `web/app/globals.css`, `web/app/layout.tsx`, `web/app/components/app-header.tsx` -- token `DESIGN.md` thành biến CSS; JetBrains Mono qua `next/font`; `:focus-visible` toàn cục; `color-scheme: dark`; `prefers-reduced-motion`; header dùng token. Kiểm bằng `build` và kiểm tay, không cần test đỏ -- nợ từ rà soát #1
- [x] `.github/workflows/ci.yml` -- job `web` chạy thêm `npm run test` -- DoD dòng 12
- [x] `README.md` -- lệnh chạy test web -- DoD dòng 14

**Acceptance Criteria:**
- Given API giả và Compose local, when mở `localhost:3000/`, then thấy màn Bản đồ ở lối 2D với số của `role=all`, và `/` vẫn có đúng một thẻ `<a aria-current="page">` và một thẻ `<nav>`.
- Given #69 đổi `HAIDO_MARKET_SOURCE_CITY_SHARES=stat`, when mở `/`, then màn chạy trên số thật mà không sửa file nào trong `web/` ngoài `web/lib/labels.ts`.
- Given code của #46, when CI chạy, then job `web` (`lint`, `build`, `test`), job `smoke` và cổng kiến trúc đều xanh.

## Implementation Notes

- RED `tests/fr33-city-shares-view.test.ts`: 21/21 đỏ. Lý do: `labels.ts` và `city-shares-view.ts` mới là vỏ có chữ ký, thân hàm ném `chưa cài` và danh sách vai trò rỗng; không có lỗi cú pháp hay import.
- RED `tests/ad17-city-shares-client.test.ts`: 29/29 đỏ (21 test cũ vẫn xanh). Lý do: `fetchCityShares` mới là chữ ký, thân hàm ném `chưa cài`; kiểu envelope đã có nên file test qua kiểm kiểu.
- RED `tests/fr33-map-screen.test.tsx` + `tests/fr36-snapshot-caption.test.tsx`: 31/31 đỏ (25 + 6; 50 test cũ vẫn xanh). Lý do: `MapScreen` mới là vỏ `return null`, nên không có trạng thái tải, chip, thanh, bảng, lỗi hay chú thích (`Unable to find role=…`, SSR ra chuỗi rỗng).
- GREEN: 81/81 xanh sau ba cặp. Cặp 3 lần đầu còn 1 đỏ ("di chuột lên chính phần trăm"): `onPointerLeave` của React suy từ `pointerout` + `relatedTarget`; user-event không gửi `relatedTarget` nên dòng mất phần trăm. Sửa bằng `pointerenter`/`pointerleave` gốc của trình duyệt (không bắn khi vào phần tử con), đúng ngữ nghĩa ở cả trình duyệt lẫn jsdom.
- Hạ tầng: vitest 5.0.5, @vitejs/plugin-react 6.1.2, jsdom 30.1.3, @testing-library/react 16.3.3, user-event 14.6.8, thêm @testing-library/dom 10.4.2 (peer bắt buộc của RTL 16). Chọn bản phát hành trước 23/10/2026. Test rỗng của hạ tầng đã chạy rồi xóa. `tests/setup.ts` gọi `cleanup` vì không bật `globals`. Config đặt tên `vitest.config.mts` để Vite nạp như ESM (tên `.ts` làm Vite cảnh báo mỗi lần chạy).
- Fixture: `tests/fixtures/city-shares-{all,data_ai,backend}.json` là response thật của API giả (#2), sinh bằng `TestClient(haido_api.main.app)`. `statEnvelope()` dựng envelope hình #69 (`n_by_measure = {}`, ĐN `n = 0`, bốn câu `coverage_notes`).
- Quyết định nhỏ trong phạm vi spec:
  - `fetchCityShares` kiểm phần hợp đồng mà màn đọc: năm dòng bắt buộc (lấy từ `labels.ts`), không trùng `city`, `kind = composition_share`, `display` là `shown` hoặc `low_sample_shown`, `value` là số trong 0–1, mọi `cell_id` có trong `meta.cells` với `n` nguyên ≥ 0, `meta` đủ trường, `coverage_notes` ≥ 1, và `data.role` bằng vai trò đã hỏi. Sai một chỗ thì "Không đọc được số liệu. Thử lại sau.".
  - Mã lỗi chuẩn không có trong bảng (ví dụ `method_not_allowed`) đi như "mã lỗi chuẩn khác": hiện `message`, có "Thử lại". Chỉ `unknown_cell` không có nút này.
  - Dòng có mã thành phố lạ (ngoài năm mã) không thành thanh: xếp sau Khác và không xác định, cả ở chú thích lẫn bảng, nhãn là chính mã.
  - Cột Ghi chú của bảng: dòng mẫu nhỏ ghi "Cỡ mẫu nhỏ (n = X < N)" (bỏ vế "số liệu chỉ để tham khảo" vì ô tỷ trọng đã là "chưa đủ dữ liệu"); dòng khác để trống. Câu lệch làm tròn luôn hiện vì web không cộng để biết có lệch hay không.
  - Chạm hoặc bấm đảo trạng thái hiện của phần trăm; focus từ chuột hoặc chạm không tính là focus bàn phím, nên chạm lần đầu hiện, lần hai ẩn. Rời focus cũng ẩn.
  - Chữ mới ngoài danh sách của spec: nhãn nhóm "Vai trò", "Lối xem", "Chú thích" (cho trình đọc màn hình), tiêu đề "Tỷ trọng tin theo thành phố · {vai trò}", "Nguồn và lưu ý", "Nguồn", "Ngày snapshot", "Tổng", và câu dẫn dưới tiêu đề trang.
  - Token khai bằng `@theme static` của Tailwind 4 nên mọi token có biến CSS trên `:root`; thanh dùng CSS module `share-line.module.css` đọc `var(--…)`. Sọc mẫu nhỏ dùng `color-mix` trên `--color-selected`, cùng giá trị `rgba(98,217,238,.35/.08)` của Design Notes.
  - Job CI giữ tên "Web - lint and build" để không làm lệch required check của branch protection; chỉ thêm bước `npm run test`.
- Sửa theo rà soát lượt 1 (E1–E12 ở Review Triage Log):
  - E1: phần trăm của dòng mẫu nhỏ có bốn cờ riêng (trỏ, focus bàn phím, ghim, đã giấu). Bấm/Enter/Space khi đang hiện thì ghim; lần sau hoặc Esc thì giấu tới khi con trỏ rời đi hoặc focus đổi chỗ. Mọi con trỏ không phải cảm ứng tính là trỏ (cả bút). `focusFromPointer` reset ở `pointerup`/`pointercancel`.
  - E4: kết quả gắn với `id` của lượt gọi. `id` tăng khi đổi vai trò hoặc thử lại (trong handler, cùng lúc với vai trò), không tăng trong effect: tăng trong effect thì phải setState đồng bộ trong effect hoặc đọc ref lúc render, cả hai đều bị lint React chặn và render đầu sau khi đổi vẫn thấy kết quả cũ.
  - E6, E7: một `<p role="status" tabIndex={-1}>` sống suốt màn, chỉ đổi chữ (ẩn kiểu `sr-only` khi rỗng); "Thử lại" đưa focus về đó.
  - E3: `tests/api/test_ad17_web_fixtures.py` so ba fixture của web với response của `TestClient`.
  - Test "render phía server" chuyển sang `tests/fr33-map-screen-ssr.test.tsx` với `// @vitest-environment node`.
- Kiểm (06/11/2026):
  - `npm --prefix web run test` 81/81, `lint` sạch, `build` qua (bước TypeScript kiểm cả file test), `check_gates.py --require AD-1 AD-17 AD-25` → `0 failed`.
  - Docker daemon không chạy trên máy này nên chưa chạy `compose.local.yml`. Thay bằng `uvicorn` (:8000) + `next start` của bản build (:3000), chạy đủ sáu bước của job `smoke`: một `<a aria-current="page">` trỏ `/` và `/soi-tin`, bốn `<a>` trong nav, một `<nav>`, proxy có `data`/`meta`, traversal 404, tắt API → 502 `api_unavailable`. HTML tĩnh của `/` chỉ có "Đang tải số liệu…", không có phần trăm.
  - Kiểm tay bằng Chromium (Playwright) ở 1280px và 375px: thanh rộng đúng `share.value`, mỗi dòng cao 44px, chip và cụm lối xem cao 44px; ĐN `data_ai` mờ có sọc, nhãn luôn hiện, % hiện khi trỏ (cả khi trỏ lên chính %), focus bàn phím, chạm; Esc và chạm lần hai ẩn; vòng focus `2px solid #C5F36A`, offset 2px; 3D không đổi lối; bảng đúng số; 375px không cuộn ngang, có gợi ý mở trên máy tính, có cụm lối xem và chú thích; reduced motion tắt transition; API tắt thì hiện message và "Thử lại", chip vẫn đổi được; không có lỗi console.

## Spec Change Log

### 2026-11-06 — Sắp lại Tasks theo TDD (người sở hữu spec yêu cầu, sau khi duyệt)

- **Nguyên nhân:** người sở hữu spec yêu cầu code theo TDD: viết test đỏ trước rồi mới code cho xanh.
- **Đã sửa:** chỉ phần Tasks, nằm ngoài khối frozen. Tách thành từng cặp test đỏ → code xanh, thêm bước ghi kết quả đỏ vào Implementation Notes, và dẫn tới `docs/templates/test-driven-tdd/test-driven-development.md`. Phần token và header vẫn kiểm bằng `build` và kiểm tay.
- **Tránh được:** test viết sau code, chỉ để khớp với code đã có.
- **Giữ nguyên:** khối frozen, Code Map, AC, Design Notes, Verification.

## Review Triage Log

Lượt 1 (06/11/2026). Lớp: BH = blind-hunter, EC = edge-case-hunter, VG = verification-gap. Không có `intent_gap` hay `bad_spec`.

| ID | Phát hiện | Verdict | Bằng chứng | Hướng |
|---|---|---|---|---|
| BH-1, EC-1, VG-khác | Bấm chuột hoặc Enter trên dòng đang hiện % (do trỏ hoặc focus) lại làm % ẩn | medium | `onClick` đảo mọi trạng thái khác `null` về `null`; VG đã thử trong jsdom: trỏ rồi bấm → ẩn, focus rồi Enter → ẩn | patch E1 |
| EC-2 | Một biến trạng thái cho cả trỏ, focus, chạm: trỏ → focus → rời chuột thì ẩn dù còn focus | medium | `setReveal(current === "hover" ? null : current)` và `onBlur` xóa hết | patch E1 |
| EC-3 | `pointerdown` rồi `pointercancel` không có click: lần focus bàn phím sau bị coi là từ chuột | low | `focusFromPointer` chỉ được reset trong `onFocus`/`onClick` | patch E1 |
| EC-4 | Bút (`pen`) trỏ không hiện % | low | Chỉ xét `pointerType === "mouse"` | patch E1 |
| VG-1 | Rời focus (Tab đi) không được kiểm là ẩn % | low | Đến từ VG: xóa `onBlur` vẫn 81/81 xanh | patch E1 |
| BH-7, VG-2 | Tám luật kiểm envelope không có test; vài nhánh dẫn tới vỡ màn hay số sai | medium | Đến từ VG: bỏ từng luật vẫn xanh; thiếu `sources_failed` làm `join` ném lỗi, `value` 1,2 ra "120,0%", thiếu `n` ra "NaN tin" | patch E2 |
| BH-8, VG-4 | Fixture của web chép tay từ API, không gì kiểm chúng còn khớp API | medium | Đến từ VG: đổi mã trong `fake_market.json` mà quên `labels.ts` thì mọi kiểm tra vẫn xanh, còn `/` hiện "Không đọc được" | patch E3 |
| EC-5, VG-3 | Kết quả gắn theo vai trò + lượt thử: quay lại vai trò cũ khi lượt khác đang chờ thì hiện số hoặc lỗi cũ thay cho trạng thái tải; không test nào kiểm trạng thái tải sau lỗi | low | Đến từ VG: bỏ điều kiện vai trò hoặc lượt thử vẫn xanh | patch E4 |
| BH-4, EC-8, EC-9 | `partial` với `sources_failed` rỗng ra câu cụt; `sources` rỗng ra dòng "Nguồn" trống | low | `Meta` phía server cho phép cả hai | patch E5 |
| BH-5 | `role="status"` được chèn cùng nội dung rồi gỡ đi, trình đọc màn hình hay bỏ qua | low | Vùng live chỉ tồn tại khi đang tải | patch E6 |
| BH-6 | Bấm "Thử lại" thì nút bị gỡ khỏi DOM, focus rơi về `<body>` | low | `LoadError` bị unmount khi `attempt` tăng | patch E7 |
| BH-9 | Chế độ tương phản cao của Windows làm mất rãnh và thanh | low | `.track`, `.fill` chỉ dùng `background`, bị `forced-colors` xóa | patch E8 |
| BH-11, EC-12 | Không ghi yêu cầu phiên bản Node (jsdom 30 cần `^22.22.2 \|\| ^24.15.0`) | low | `web/package.json` không có `engines`, README không nói | patch E9 |
| BH-12 | Test "render phía server" chạy trong jsdom, có `window` | low | `renderToString` dưới môi trường jsdom | patch E10 |
| EC-13 | `vitest.config.ts` bị nạp như CommonJS, Vite cảnh báo mỗi lần chạy | low | `web/package.json` không có `"type": "module"` | patch E11 |
| BH-14 | Nhánh không bao giờ tới (`data.role !== role`, `value ?? 0`), hai mảng song song, `key={index}` | low | Validator đã chặn trước; sửa trực tiếp | patch E12 |
| BH-15 | `toBeDefined()` sau `getBy*` không bao giờ đỏ; `stubFetch` chép lại `jsonResponse` | low | `getBy*` tự ném khi không thấy | patch E12 |
| BH-2, EC-10 | Nhãn có thể ghi sai "n = 150 < 30" khi `display` và `n` lệch nhau | false | Validator `Envelope` phía server bắt `display` khớp `suppression_for`; lệch là 500 `invalid_response`, không tới màn | reject |
| BH-3, EC-11 | Câu "có thể lệch 0,1%" có lúc sai: năm dòng có thể lệch tới 0,2% | low | Đúng về toán, nhưng câu này do Design Notes của spec chốt; sửa là sửa spec | reject, báo người sở hữu |
| EC-6 | Không có timeout phía trình duyệt | false | Proxy của #1 dùng `AbortSignal.timeout(10000)` và trả 502 `api_unavailable` | reject |
| EC-7 | `invalid_query`, `not_found`, `http_error` vẫn có "Thử lại" | low | Bảng lỗi của spec ghi "Có"; code làm đúng spec | reject |
| BH-10a | `sprint-status` ghi `in-progress` trong khi spec `in-review` | false | Quy trình chuyển sang `review` ở bước trình bày, chưa tới | reject |
| BH-10b | `last_updated` của `sprint-status` ghi giờ đoán | low | Giờ do người điều phối ghi; sửa lúc đồng bộ ở bước trình bày | sửa khi đồng bộ |
| BH-13a | Ba trang giữ chỗ (`/insights`, `/co-van`, `/soi-tin`) còn màu viết cứng | low | Có từ #1, ngoài phạm vi #46 | defer |
| BH-13b | Không reset bảng màu mặc định của Tailwind | low | Ít gặp hại; reset có thể làm vỡ class đang dùng | reject |

## Design Notes

Thanh dựng bằng HTML + CSS, không dùng SVG hay thư viện. Ba thanh không cần thư viện; thẻ HTML tự có focus và chạy đúng trên điện thoại; Safari và VoiceOver focus thẻ `<rect>` của SVG không ổn định. Tham khảo:
- Tremor BarList (github.com/tremorlabs/tremor): chỉ lấy ý thanh là `div` rộng theo %. Không chép cách nó co thanh theo giá trị lớn nhất hay độ rộng tối thiểu 2%.
- maartenzam/accessible-html-dataviz: biểu đồ dạng danh sách, kèm bảng tương đương.
- UK Analysis Function: bảng là bản chữ của biểu đồ; giá trị yếu phải có nhãn chữ, không chỉ đổi màu.

```text
Hà Nội     ███████████████████████  47,0% · 412 tin
TP.HCM     ███████████████████      38,0% · 333 tin
Đà Nẵng    ░░ (mờ, sọc)             Cỡ mẫu nhỏ (n = 21 < 30): số liệu chỉ để tham khảo
Chú thích: Khác 5,2% · 46 tin · Không xác định thành phố 7,4% · 65 tin
```

Sọc của thanh mẫu nhỏ theo `DESIGN.md`: `repeating-linear-gradient(135deg, rgba(98,217,238,.35) 0 4px, rgba(98,217,238,.08) 4px 8px)`. Chú thích dưới dòng tổng: "Tổng các dòng có thể lệch 0,1% do làm tròn."

Bảng lỗi:

| Tình huống | Hiện gì | Nút "Thử lại" | Chip đổi được |
|---|---|---|---|
| 502 `api_unavailable` | `error.message` | Có | Có |
| 404 `unknown_cell` | `error.message`, kèm ngày `snapshot_date` nếu có | Không | Có |
| Mã lỗi chuẩn khác (`invalid_response`, `internal_error`, `invalid_query`, `http_error`, `not_found`) | `error.message` | Có | Có |
| `fetch` bị từ chối, body không phải JSON, hoặc envelope thiếu trường hay thiếu một trong năm dòng thành phố | "Không đọc được số liệu. Thử lại sau." | Có | Có |

Chuỗi chưa có trong tài liệu, do spec này chọn: "Đang tải số liệu…", "Thử lại", "Mở trên máy tính để xem bản đồ đầy đủ.", "Nguồn lỗi ở snapshot này: …", "Không đọc được số liệu. Thử lại sau.", "Tổng các dòng có thể lệch 0,1% do làm tròn."

## Verification

**Commands:**
- `npm --prefix web run lint`, `npm --prefix web run build`, `npm --prefix web run test` -- expected: thành công
- `python tools/gates/check_gates.py --require AD-1 AD-17 AD-25` -- expected: `0 failed`
- `docker compose -f deploy/compose.local.yml up -d --wait --build`, rồi chạy lại các bước kiểm của job `smoke` trên `localhost:3000/` -- expected: đúng một `<a aria-current="page">` trỏ `/`, bốn `<a>` trong nav

**Manual checks:**
- Mở `localhost:3000` trên máy tính và ở khung nhìn 375px:
  - lối 2D và lối Bảng;
  - mẫu nhỏ của ĐN với `role=data_ai`;
  - nút 3D tắt;
  - đổi vai trò;
  - Tab qua từng điểm dừng và thấy vòng focus;
  - Esc ẩn phần trăm.
