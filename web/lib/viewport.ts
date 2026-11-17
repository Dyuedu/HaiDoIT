/**
 * Màn có rộng từ 640px (mốc `sm` của Tailwind) không, cho `useSyncExternalStore` (#314). Điện thoại mở Bản đồ ở lối 2D
 * (NFR-12, UX-DR39: danh sách thành phố kèm thanh tỷ trọng); lối 3D vẫn chọn được. Không có `matchMedia` (server, jsdom
 * cũ) thì coi là màn rộng.
 */

const WIDE = "(min-width: 640px)";

function media(): MediaQueryList | null {
  return typeof window !== "undefined" && typeof window.matchMedia === "function" ? window.matchMedia(WIDE) : null;
}

export function subscribeWide(listener: () => void): () => void {
  const list = media();
  if (!list) return () => {};
  list.addEventListener("change", listener);
  return () => list.removeEventListener("change", listener);
}

export function getWideSnapshot(): boolean {
  return media()?.matches ?? true;
}

export function getServerWideSnapshot(): boolean {
  return true;
}
