/**
 * Trình duyệt có dựng được CSS 3D không (`transform-style: preserve-3d`), cho `useSyncExternalStore` (#316, FR-36).
 * Bản đồ 3D theo prototype là CSS 3D, không cần WebGL; không dựng được thì màn mở lối 2D. Server render và lần hydrate
 * đầu thấy "không", nên HTML tĩnh là lối 2D.
 */

export function subscribeCss3d(): () => void {
  return () => {};
}

export function getCss3dSnapshot(): boolean {
  try {
    return typeof CSS !== "undefined" && typeof CSS.supports === "function" && CSS.supports("transform-style", "preserve-3d");
  } catch {
    return false;
  }
}

export function getServerCss3dSnapshot(): boolean {
  return false;
}
