# Research: Bản đồ 3D theo prototype

## Quyết định

- Dựng đúng cách của prototype màn 01 (người dùng chọn 17/11/2026): CSS 3D, không WebGL. Mọi số đo lấy từ mã của prototype: khung `perspective: 1500px`, `perspective-origin: 50% 18%`, cao 560px (420px và `scale(.62)` dưới 640px); sân khấu 460×560, `translateY(40px) rotateX(rx) rotateZ(rz)`, mở màn `rx` 0 → 56 sau 250ms, `rz` −16; tấm lưới 800×800 ở `translateZ(-44px)`, mặt nạ radial; năm lớp SVG của hình đất ở `translateZ` −36, −12, −8, −4, 0; cột 28×28, cao `p × 4` px, năm mặt (`top` ở `translateZ(h)`, `fr`/`bk` `rotateX(90deg)`, `lf`/`rt` `rotateY(-90deg)`); thẻ nhãn ở `translateZ(h + 12)` rồi `rotateZ(-rz) rotateX(-rx)` để đứng thẳng; nút xoay ±30°, đặt lại 56/−16; kéo ngang 0,35°/px, kéo dọc 0,3°/px trong 0–72°, bắt đầu sau 6px.
- Lấy từ: `_bmad-output/planning-artifacts/ux-designs/ux-HaiDoIT-2026-11-03/.working/screens-inner/01.html` (template, CSS, `renderVals`), `DESIGN.md` (token màu, `map-column`, `icon-button`, khung 560/420px).

## Cách các repo công khai làm

- [pmndrs/react-three-fiber @ d74622e, `packages/fiber/src/web/Canvas.tsx`](https://github.com/pmndrs/react-three-fiber/blob/d74622ea8ed717f7212d7e19d65ff3e325508389/packages/fiber/src/web/Canvas.tsx) (#314): canvas WebGL cần tự dò WebGL và bọc error boundary mới rơi về 2D được. CSS 3D không cần context đồ họa, nên chỉ cần dò `transform-style: preserve-3d`.
- [mdn/content @ 7d55f11, `files/en-us/web/css/reference/properties/transform-style/index.md`](https://github.com/mdn/content/blob/7d55f113b5a05afe6ada6bb9b76bd3b0458f077d/files/en-us/web/css/reference/properties/transform-style/index.md): `preserve-3d` cho con của phần tử nằm trong cùng không gian 3D; đây là thứ prototype dựa vào để xếp lớp đất, mặt cột và thẻ. Dò bằng `CSS.supports("transform-style", "preserve-3d")`.

## Không lấy

- Không giữ three.js: thiết kế dựng bằng CSS, thẻ nhãn là DOM (bấm, đọc được), và bỏ được ~924 KB.
- Không dùng đa giác vẽ tay của prototype: dùng viền geoBoundaries thật chiếu vào sân khấu, giữ style.
- Không vẽ "Khác" thành thẻ trên biển như một bản prototype khác (bundle `Hải Đồ IT — Prototype…html`): DESIGN.md và FR-33 cấm.
