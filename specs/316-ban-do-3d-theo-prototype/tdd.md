# TDD: Bản đồ 3D theo prototype

Theo `docs/templates/test-driven-tdd/test-driven-development.md`. jsdom không có `CSS.supports`: test màn giả lập kết quả dò CSS 3D; phần còn lại là mã thật. Chạy từ ổ `D:\` viết hoa.

Lệnh:

```text
cd web && npx vitest run tests/fr33-ban-do-3d-hinh.test.ts tests/fr33-ban-do-3d.test.tsx
```

## Các hành vi

1. Sân khấu: mọi điểm viền, đảo, ba thành phố nằm trong 460×560; Hà Nội trên (y nhỏ hơn) Đà Nẵng, Đà Nẵng trên TP.HCM; Hoàng Sa bên phải Đà Nẵng.
2. Cột: đúng ba, cao `value × 400`, mẫu nhỏ `faded`, thẻ có "41,7% · 848/2.040 tin" (theo fixture), câu cỡ mẫu nhỏ.
3. Mở lối 3D: sân khấu `rotateX(56deg) rotateZ(-16deg)` sau mở màn; ba thẻ nhãn là nút có tên đọc được gồm tỷ trọng và n.
4. Thẻ mẫu nhỏ: tỷ trọng nằm trong phần `data-reveal`; câu cỡ mẫu nhỏ hiện.
5. Bấm thẻ: `aria-pressed = true`, mặt trên `data-selected`.
6. "Xoay phải 30 độ" → `rotateZ(14deg)`; "Xoay trái 30 độ" hai lần → `rotateZ(-46deg)`; "Đặt lại góc nhìn" → 56/−16.
7. Kéo ngang 100px → `rotateZ` +35°; kéo dọc lên 400px → `rotateX` dừng ở 72°; kéo dưới 6px không đổi.
8. Panel phải "Tin Tất cả nằm ở đâu": ba nơi với tỷ trọng và "n / tổng tin", các dòng Làm từ xa, Nước ngoài, Không xác định, khung "Nguồn và lưu ý"; có ở lối 2D và Bảng.
9. Không CSS 3D: lối 2D, nút 3D `aria-disabled` kèm câu.
10. Màn hẹp: lối 2D, nút 3D bấm được.
11. `web/package.json` không có `three`, `@react-three/fiber`, `@types/three`.

## RED (2026-11-17)

`npx vitest run tests/fr33-ban-do-3d-hinh.test.ts tests/fr33-ban-do-3d.test.tsx`:

- `fr33-ban-do-3d-hinh`: 9/9 failed: chưa có `STAGE`, `toStage`, `OUTLINE_PATH`, `shortLabel`; `buildColumns` còn nhận `view.bars`; `web/package.json` còn `three`, `@react-three/fiber`, `@types/three`.
- `fr33-ban-do-3d`: 9/10 failed: chưa có khung "Bản đồ 3D" CSS, sân khấu, nút xoay, panel bên phải. Test "không CSS 3D thì 2D" xanh sẵn (jsdom chưa bị giả lập, màn đang ở 2D vì không có WebGL).

## GREEN (2026-11-17)

- Lượt đầu: 16 passed, 3 failed. Hai lỗi của test: đọc `package.json` qua `import.meta.url` (jsdom không phải `file:`), và fixture mẫu nhỏ mang `role = backend` nên bị coi là sai vai trò. Một lỗi của cách đợi: hẹn giờ mở màn 250ms không chạy theo đồng hồ giả trong jsdom (in góc nghiêng: sau `advanceTimersByTime` vẫn 0°, sau 400ms thật là 56°); bỏ đồng hồ giả, đợi bằng `waitFor`. Code không đổi.
- Toàn bộ: 34 test cũ đỏ vì jsdom trả `true` cho `CSS.supports("transform-style", "preserve-3d")` nên mở 3D, và nút "Trỏ hoặc chạm để xem %" của panel trùng tên với nút thanh 2D. Sửa: `web/tests/setup.ts` coi jsdom là không dựng được CSS 3D (jsdom không tính layout 3D); tên nút của panel bắt đầu bằng "Tỷ trọng". Còn 1 test của #163 đỏ vì panel nhắc lại câu cỡ mẫu nhỏ; giới hạn tìm trong biểu đồ 2D.
- `npx vitest run` → 27 files, 347 passed; `tsc`, `lint` sạch; `npm run build` xong, chunk three.js (~924 KB) không còn; `tools/gates/check_gates.py` → 10 pass, 0 fail.
- Kiểm tay (Chrome headless, `next start`, API local nguồn giả):
  - 1440px: ảnh chụp đặt cạnh ảnh prototype màn 01: cùng khung nghiêng có lưới mờ, Việt Nam viền `selected` tô chấm, cột vuông năm mặt, thẻ nhãn, ba nút tròn, câu hướng dẫn, panel bên phải. Khác dữ liệu: cột TP.HCM 47,8% cao 191px (quy tắc `p × 4`) nên thẻ của nó che một phần thẻ Đà Nẵng; prototype có tỷ trọng ~31–34% nên không chồng.
  - 360px (giả lập thiết bị): mở lối 2D, không cuộn ngang; bấm 3D mở được, sân khấu `rotateX(56deg) rotateZ(-16deg)`.
  - Lần đo đầu ở 360px: thẻ nhãn 28–34px (sân khấu thu 0,62). Thêm phần bù cho thẻ dưới 640px; lần đo tiếp vẫn 38px vì khối `@media` đứng trước quy tắc `.card` gốc nên bị đè. Chuyển xuống cuối file: không còn ô bấm nào dưới 44px ở 360px và 1440px.
  - Ảnh chụp bằng `--window-size=360` của Chrome headless dàn trang rộng hơn 360px rồi cắt; chỉ dùng số đo của giả lập thiết bị.
