import { MapScreen } from "./components/map/map-screen";

/**
 * Trang `/` (Bản đồ). Server component chỉ render khung; số liệu do `MapScreen` gọi phía trình
 * duyệt sau khi trang mở.
 */
export default function MapPage() {
  return (
    <section className="py-2">
      <h1 className="m-0 text-title text-text">Bản đồ nhu cầu IT</h1>
      <p className="mt-2 mb-0 max-w-[68ch] text-body-md text-text-quiet">
        Hà Nội, TP.HCM và Đà Nẵng chiếm bao nhiêu phần tin tuyển dụng IT của vai trò bạn chọn,
        kèm cỡ mẫu, nguồn và ngày snapshot.
      </p>
      <MapScreen />
    </section>
  );
}
