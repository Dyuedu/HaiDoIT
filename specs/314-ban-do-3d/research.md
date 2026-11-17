# Research: Lối xem bản đồ 3D

## Quyết định

- three.js với react-three-fiber (người dùng chọn 17/11/2026). Không dùng drei: chỉ cần OrbitControls (có sẵn trong `three/examples/jsm`) và vài nhãn (sprite từ canvas 2D).
- Hình Việt Nam là mặt phẳng đùn (`ExtrudeGeometry`) từ GeoJSON, chiếu tuyến tính quanh vĩ độ 16°B (kinh độ nhân cos 16°). Không tile, không dịch vụ bản đồ ngoài.
- Dò WebGL trước, cộng error boundary: react-three-fiber không tự rơi về khi không tạo được context.
- Nút chọn cột và khung thông tin ở DOM thường, ngoài canvas, để bàn phím và trình đọc màn hình dùng được.

## Cách các repo công khai làm

- [pmndrs/react-three-fiber @ d74622e, `packages/fiber/src/web/Canvas.tsx`](https://github.com/pmndrs/react-three-fiber/blob/d74622ea8ed717f7212d7e19d65ff3e325508389/packages/fiber/src/web/Canvas.tsx): prop `fallback` chỉ là nội dung thay thế đặt trong thẻ canvas ("similar to img's alt prop"); khi tạo renderer lỗi, `Canvas` giữ lỗi trong state rồi `throw` ra ngoài (`if (error) throw error`). Vì vậy Hải Đồ tự dò WebGL trước khi mở 3D và bọc canvas bằng error boundary để chuyển 2D, đúng FR-36 "không hiện màn hình lỗi".
- [mrdoob/three.js @ 95ae210, `examples/jsm/controls/OrbitControls.js`](https://github.com/mrdoob/three.js/blob/95ae21052df72e9b78a013d6d4e89ef87fc847a0/examples/jsm/controls/OrbitControls.js): có `maxPolarAngle`, `minDistance`/`maxDistance`, `enableDamping`, `enablePan`. Lấy để giới hạn góc nghiêng (không lật xuống dưới mặt đất) và tắt kéo ngang (bản đồ luôn ở giữa).
- [mrdoob/three.js @ 95ae210, `src/geometries/ExtrudeGeometry.js`](https://github.com/mrdoob/three.js/blob/95ae21052df72e9b78a013d6d4e89ef87fc847a0/src/geometries/ExtrudeGeometry.js): đùn `Shape` thành khối có độ dày; dùng cho mỗi vòng viền.

## Dữ liệu viền

- [wmgeolab/geoBoundaries @ 9469f09, `releaseData/gbOpen/VNM/ADM0/geoBoundaries-VNM-ADM0_simplified.geojson`](https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/VNM/ADM0/geoBoundaries-VNM-ADM0_simplified.geojson), giấy phép CC BY 4.0 (theo API `geoboundaries.org/api/current/gbOpen/VNM/ADM0/`). 90 polygon, 3.604 điểm, 162 KB. Kinh độ lớn nhất 109,46°Đ: **không có Hoàng Sa, Trường Sa**.
- Rút gọn: giữ polygon có bbox rộng hơn 0,12°, Douglas–Peucker 0,02°, làm tròn 3 chữ số → 7 vòng, 548 điểm, ~9,5 KB.
- Hoàng Sa, Trường Sa: vẽ riêng bằng các điểm đảo đại diện, tọa độ xấp xỉ, luôn có nhãn "Quần đảo Hoàng Sa", "Quần đảo Trường Sa". Bản đồ Việt Nam công khai phải thể hiện hai quần đảo này.

## Không lấy

- Không dùng drei (`OrbitControls`, `Html`, `Text`): kéo theo nhiều gói phụ cho đúng hai thứ cần.
- Không dùng deck.gl hay MapLibre: cần tile hoặc nhiều hơn mức ba cột cần.
- Không dùng Natural Earth: không gán Hoàng Sa, Trường Sa cho Việt Nam; geoBoundaries cũng không có, nhưng có đất liền chi tiết hơn và giấy phép rõ.
