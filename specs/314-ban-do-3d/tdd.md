# TDD: Lối xem bản đồ 3D

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. jsdom không có WebGL: test hình học chạy hàm thuần; test màn thay `map-3d.tsx` (canvas) bằng bản giả và giả lập kết quả dò WebGL. Kiểm canvas thật bằng Chrome headless. Chạy từ ổ `D:\` viết hoa.

Lệnh:

```text
cd web && npx vitest run tests/fr33-ban-do-3d-hinh.test.ts tests/fr33-ban-do-3d.test.tsx
```

## Các hành vi

1. Viền có ít nhất một vòng lớn (đất liền) và mọi điểm trong khung 102–110°Đ, 8–24°B; nguồn và giấy phép ghi trong file.
2. Hoàng Sa: mọi điểm trong 15–17,5°B, 110,5–113°Đ; Trường Sa: trong 7–12°B, 111–117°Đ; mỗi quần đảo có nhãn.
3. Phép chiếu: Hà Nội nằm phía bắc (z nhỏ hơn) TP.HCM; Đà Nẵng nằm giữa; Hoàng Sa ở phía đông Đà Nẵng.
4. Cột: đúng ba, thứ tự Hà Nội, TP.HCM, Đà Nẵng theo `view.bars`; chiều cao = `value` × hằng số; cột mẫu nhỏ `faded` và có câu "Cỡ mẫu nhỏ (n = X < 30): số liệu chỉ để tham khảo".
5. Màn có WebGL: lối 3D chọn sẵn, khung 3D hiện; "Biểu đồ 2D"/"Bảng"/"3D" chuyển qua lại.
6. Chọn cột bằng nút: `role="status"` ghi "Hà Nội: 47,0%, 1.234 tin".
7. Lối 3D vẫn có khung "Nguồn và lưu ý" và chú thích các phần không thành cột.
8. Không có WebGL: lối 2D, nút 3D `aria-disabled`, câu "Trình duyệt này không chạy được bản đồ 3D, nên đang hiện biểu đồ 2D."
9. Component 3D ném lỗi: màn chuyển 2D, có câu trên, không có `role="alert"`.
10. Màn hẹp hơn 640px có WebGL: mở lối 2D, nút 3D vẫn bấm được và mở khung 3D.

## RED (2026-11-17)

`npx vitest run tests/fr33-ban-do-3d-hinh.test.ts tests/fr33-ban-do-3d.test.tsx`:

- `fr33-ban-do-3d-hinh`: không nạp được, `Failed to resolve import "@/lib/map-3d-view"` (chưa có `vietnam-geo`, `map-3d-view`).
- `fr33-ban-do-3d`: 6/6 failed, `Unable to find an element by: [data-testid="map-3d-canvas"]`: màn chưa có lối 3D.
- Test nút 3D cũ (`fr33-map-screen.test.tsx`) sửa trước khi viết code: câu đi kèm nút khi không có WebGL đổi từ "Bản đồ 3D sắp có" sang câu giải thích mới.

## GREEN (2026-11-17)

- Hình học: 7 passed. Màn: 6 passed; `fr33-map-screen`: xanh với câu mới.
- `npx tsc --noEmit`: lỗi ép kiểu JSON viền (`number[][][]` sang `[number, number][][]`), sửa bằng `as unknown as Outline`. `npm run lint`: cấm gán ref trong lúc render (`react-hooks/refs`), chuyển vào `useEffect`.
- Kiểm tay lần 1 (Chrome headless, SwiftShader): bản đồ vẽ đúng ở 1280px, nhưng (1) kéo có thể xoay ngược bản đồ, (2) Trường Sa sát mép dưới, (3) điện thoại cũng mở 3D, trái NFR-12 và UX-DR39 (điện thoại là danh sách thành phố kèm thanh). Sửa: giới hạn xoay ngang ±60°, tâm nhìn lệch nam; thêm `web/lib/viewport.ts`, màn dưới 640px mở 2D.
- RED đợt 2: test "màn hẹp hơn 640px mở lối 2D dù có WebGL" → 1 failed (mở 3D). GREEN: 7 passed.
- `npx vitest run` → 27 files, 342 passed; `tsc`, `lint` sạch; `npm run build` xong (`/` vẫn tĩnh; chunk three.js ~924 KB chỉ tải khi mở lối 3D). Build in cảnh báo GHSA-mfr8-8qww-v76h của Next 16.4.4 và dừng một lần để nhắc nâng cấp (không liên quan thay đổi này). `npm audit --omit=dev`: chỉ còn lỗ hổng đó, ba gói mới không thêm lỗ hổng.
- `tools/gates/check_gates.py` → 10 pass, 0 fail.
- Kiểm tay lần 2 (Chrome headless, `next start`, API local nguồn giả):
  - 1280×900: lối 3D chọn sẵn, canvas 1175×520, không cuộn ngang, không nút nào thấp hơn 44px; ảnh chụp có đất liền, ba cột (TP.HCM cao nhất, Đà Nẵng thấp), nhãn và đảo của Quần đảo Hoàng Sa, Quần đảo Trường Sa.
  - Kéo chuột: góc nhìn đổi (so hai ảnh chụp), dừng ở giới hạn 60°, không lật ngược.
  - Nút "Hà Nội": khung thông tin "Hà Nội: 41,7%, 848 tin".
  - 360×740: lối 2D chọn sẵn, không cuộn ngang, không có canvas cho tới khi bấm 3D.
  - Đo điểm ảnh của canvas qua `drawImage` ra rỗng vì `preserveDrawingBuffer` tắt; kết luận về hình dựa trên ảnh chụp màn hình.

## Đợt 2026-11-17 (#316): dựng lại bằng CSS 3D theo prototype

Lý do: lối 3D WebGL không giống prototype màn 01 (DESIGN.md: perspective 1500px, `translateZ`, cột năm mặt, thẻ nhãn DOM). #316 viết lại `map-3d.tsx` bằng CSS 3D, xóa `map-3d-panel.tsx` và `web/lib/webgl.ts`, gỡ `three`, `@react-three/fiber`, `@types/three`, đổi `buildColumns` sang nhận cả view và trả vị trí sân khấu 460×560. AC "trình duyệt không có WebGL thì 2D" của #314 không còn đúng nguyên văn; người dùng chốt đổi thành "không dựng được CSS 3D thì 2D" (2026-11-17).

- RED/GREEN của đợt này ghi ở `specs/316-ban-do-3d-theo-prototype/tdd.md`. Test của #314 (`fr33-ban-do-3d*.test.ts(x)`) được viết lại theo hành vi mới.
