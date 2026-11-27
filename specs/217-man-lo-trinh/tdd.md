# TDD: Màn lộ trình học theo chặng

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. Test thay `fetch` bằng fixture `web/tests/fixtures/learning-path-*.json` (response của API giả, khóa bằng `tests/api/test_ad17_web_fixtures.py`), không gọi mạng. Chạy từ PowerShell.

Lệnh:

```text
cd web && npx vitest run tests/fr22-lo-trinh-hoc.test.tsx
```

## Các hành vi

1. Chặng, thứ tự, nút, nền tảng, quay về, chưa đủ dữ liệu, khung nguồn, câu không số; luôn hỏi `entry`.
2. Đánh dấu và bỏ đánh dấu; chặng sau lên thay; có hết; số là của API; không nhảy khi tải lại; giữ vai trò và cấp đã lưu.
3. Ngăn chi tiết: nội dung, chuyển kỹ năng, Escape và Đóng, focus, không gọi API, `?skill=`, URL.
4. Chọn vai trò, vai trò đã lưu, mã lạ; `not_ready`; 404; mạng hỏng.
5. Đường nối `aria-hidden` và chỉ hiện từ `lg`; mỗi kỹ năng một nút; `connectorPath`; chia hai bên giữ thứ tự.
6. Envelope sai hợp đồng thì không đọc được.

## RED (2026-11-25)

- `npx vitest run tests/fr22-lo-trinh-hoc.test.tsx` → 1 file failed, không test nào chạy: `Failed to resolve import "@/lib/learning-path-view"` (chưa có).
- Trong lúc viết màn sửa một test: fixture `backend.intern` có `level = intern` mà màn hỏi `entry`; test đặt lại `level` cho đúng hợp đồng (API trả lại cấp đã hỏi).

## GREEN (2026-11-25)

- Ba file `fr22-lo-trinh-hoc`, `fr22-mo-lo-trinh-tu-ky-nang`, `fr22-learning-path-fixture` → 66 passed, 2 failed: hai test trang giữ chỗ của #153, hết đúng từ issue này. Thay bằng test của màn thật (bỏ bốn test trang giữ chỗ, thêm bốn).
- `npx vitest run` → 34 files, 431 passed.

## Đợt 2 (2026-11-25): sau khi xem ảnh chụp màn

Lý do: Data Engineer không có tỷ lệ nào mà vẫn ghi "Tính trên 22 tin"; chặng chỉ có một nhóm dồn hết về bên phải.

- RED: `npx vitest run tests/fr22-lo-trinh-hoc.test.tsx` → 2 failed, 45 passed (còn câu "Tính trên"; các chặng không so le).
- GREEN: `npx vitest run` → 34 files, 432 passed; `npx tsc --noEmit`, `npm run lint` thoát 0.
- Sửa kèm, không có test tự động (jsdom không có layout): cuộn kỹ năng mở sẵn lên đầu màn để ngăn ở đáy điện thoại không che.

## Kiểm tra chung (2026-11-25)

- `npm run build`: lượt đầu biên dịch xong và in đủ route nhưng thoát 1 vì Next.js 16.4.4 báo phiên bản có lỗ hổng bảo mật đã biết (`SecurityFatalError`); chạy lại thoát 0, kèm cảnh báo đó. Không nâng phiên bản trong issue này.
- `uv run pytest -q` → 1499 passed, 346 skipped; `tools/gates/check_gates.py` → 10 pass, 0 skip, 0 fail.
- Chrome headless trên `next start` với API local (nguồn giả):
  - 360×740 (backend, backend có ngăn mở, qa): không cuộn ngang (360/360), không đường nối nào hiện, không ô bấm nào dưới 44px, không chữ bị cắt.
  - 1024×800 và 1280×900: có đường nối (backend 5 khung, data_engineer 3 khung), không cuộn ngang.

## Đợt 3 (2026-11-25): demo bằng snapshot thật

Lý do: demo `/co-van` bằng số thật trước khi #216 xong. Lệnh: `HAIDO_TEST_DATABASE_URL=... uv run pytest -q tests/api/test_fr22_learning_path_draft.py` (Postgres thật).

- RED: 1 error lúc nạp, `ModuleNotFoundError: No module named 'haido_api.draft_path'`. Trước khi viết code, hai test cuối đổi từ "biến môi trường `draft`" sang app riêng `haido_api.demo`.
- GREEN: 11 passed; `uv run pytest -q` → 1856 passed, không test nào bị bỏ qua; `check_gates.py` → 10 pass, 0 fail.
- RED lần hai, sau khi xem ảnh: Frontend `not_ready` vẫn mang lưu ý bản nháp → 1 failed, 10 passed. GREEN: 11 passed.
- Image thật (compose.local + compose.demo), snapshot 2026-11-25: Backend 14 kỹ năng ở ô `vn.backend.entry` (78 tin); Data Engineer quay về `vn.data_engineer` (168 tin); Frontend chưa có lộ trình.

## Đợt 4 (2026-11-25): làm lại theo chủ đề, kiểu roadmap.sh

Lý do: người dùng thấy màn chưa giống roadmap.sh; chọn phương án đổi cấu trúc (chủ đề, chọn một) và giữ nền tối.

- RED API: 14 failed, 85 passed, 2 errors (chi tiết ở `specs/212-hinh-lo-trinh-hoc/tdd.md`, đợt B). RED cổng FR-24: 6 failed, 56 passed (khóa `topics` lạ, file nháp chưa được quét).
- RED web: `npx vitest run tests/fr22-lo-trinh-hoc.test.tsx` → 13 failed (chưa có tên chủ đề, "Chọn một", màu và chú giải, "Lựa chọn thay thế"; envelope sai `title`/`choose_one` vẫn đọc được).
- Test cũ đổi theo hợp đồng mới: chặng 1 là Git và Linux; câu đi hết lộ trình; bỏ hai test chia trái phải theo nhóm, thay bằng test so le theo chặng.
- GREEN: `npx vitest run` → 34 files, 441 passed. Sau khi xem ảnh, tên song ngữ dài làm vỡ ô ở 1024px: thêm test tên ngắn (RED: 1 failed) rồi sửa → 442 passed; `npx tsc --noEmit`, `npm run lint` thoát 0.
- `uv run pytest -q` (Postgres thật) → 1879 passed; `check_gates.py` → 10 pass, 0 skip, 0 fail.
- Mọi kỹ năng core/common của hai ô demo có trên nháp (so với DB `haido_demo`); 75 link tài liệu đã gọi thử: hai link không trả 200 (`dev.mysql.com`, `learnenglish.britishcouncil.org`) đã thay bằng link trả 200.
- Image thật, Chrome headless: 360 (backend, data_engineer, ngăn mở), 1024, 1280px: không cuộn ngang, không ô bấm dưới 44px, không chữ bị cắt, 360px không đường nối.

## Sau khi mở PR (2026-11-25)

CI đỏ ở `ruff check .` (4 lỗi I001, chưa chạy lệnh này trước khi đẩy) và GitGuardian (mật khẩu mặc định của Postgres local lặp lại trong `compose.demo.yml`). Sửa import; `compose.demo.yml` đọc mật khẩu từ `HAIDO_LOCAL_DB_PASSWORD`, không có mặc định. Không đổi hành vi.

## Đợt #216 (2026-11-25): lộ trình thật trong StatMarket

Lý do: phần ghép và nội dung chuyển chỗ; màn và app demo không đổi.

RED và GREEN: `specs/216-lo-trinh-that/tdd.md`.


## Đợt 5 (2026-11-27, Hướng B): mở khóa chọn cấp bậc & lộ trình từ CV

Chi tiết RED/GREEN cho chọn `level` và tải CV trên `/co-van`: [specs/cv-advisor-roadmap/tdd.md](../cv-advisor-roadmap/tdd.md).