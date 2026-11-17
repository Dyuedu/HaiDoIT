# Data model: Bản đồ 3D theo prototype

Không đổi bảng, cột, revision Alembic hay hình API: lối 3D và panel đọc `GET /api/v1/city-shares` qua `buildCitySharesView`, như lối 2D và bảng.

Dữ liệu tĩnh: giữ `web/lib/geo/vietnam-outline.json` (geoBoundaries, CC BY 4.0) và điểm đảo của `web/lib/vietnam-geo.ts` từ #314; thêm phép chiếu sang sân khấu 460×560 px của prototype.

Gói npm: gỡ `three`, `@react-three/fiber`, `@types/three`. Trình duyệt: không thêm khóa `localStorage`.
