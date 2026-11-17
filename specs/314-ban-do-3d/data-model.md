# Data model: Lối xem bản đồ 3D

Không đổi bảng, cột, revision Alembic hay hình API: lối 3D đọc `GET /api/v1/city-shares` như lối 2D, qua `buildCitySharesView`.

Dữ liệu tĩnh mới của web:

| File | Nội dung | Nguồn |
|---|---|---|
| `web/lib/geo/vietnam-outline.json` | 7 vòng (đất liền và đảo lớn), 548 điểm, ~9,5 KB, `[kinh độ, vĩ độ]` làm tròn 3 chữ số | geoBoundaries gbOpen VNM ADM0 simplified, `wmgeolab/geoBoundaries` @ `9469f09`, CC BY 4.0; rút gọn Douglas–Peucker 0,02° |
| `web/lib/vietnam-geo.ts` (hằng số) | Điểm đảo đại diện của Hoàng Sa (Hoàng Sa, Phú Lâm, Tri Tôn, Linh Côn, Quang Ảnh) và Trường Sa (Trường Sa, Song Tử Tây, Thị Tứ, Ba Bình, Nam Yết, Sinh Tồn, An Bang); tọa độ Hà Nội, TP.HCM, Đà Nẵng | Tọa độ xấp xỉ, bản đồ tỷ lệ nhỏ |

Trình duyệt: không thêm khóa `localStorage`. Gói npm mới: `three@0.187.0`, `@react-three/fiber@9.8.2`, `@types/three@0.187.0` (dev).
