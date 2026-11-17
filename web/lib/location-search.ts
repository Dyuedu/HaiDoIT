/**
 * Đọc và đổi một tham số của URL hiện tại cho `useSyncExternalStore` (#169: `?skill=` trên `/insights`).
 *
 * Server render và lần hydrate đầu thấy chuỗi rỗng, nên trang vẫn dựng tĩnh và HTML không lệch. Đổi tham số bằng
 * `history.replaceState` (không thêm mục lịch sử) rồi báo các màn đang nghe; nút Back/Forward báo qua `popstate`.
 */

const CHANGE = "haido:locationchange";

export function subscribeLocation(listener: () => void): () => void {
  window.addEventListener("popstate", listener);
  window.addEventListener(CHANGE, listener);
  return () => {
    window.removeEventListener("popstate", listener);
    window.removeEventListener(CHANGE, listener);
  };
}

export function getLocationSearch(): string {
  return window.location.search;
}

export function getServerLocationSearch(): string {
  return "";
}

/** Đặt `?key=value` (hoặc bỏ khi `value` là `null`), giữ các tham số khác và đường dẫn. */
export function replaceSearchParam(key: string, value: string | null): void {
  const url = new URL(window.location.href);
  if (value === null) url.searchParams.delete(key);
  else url.searchParams.set(key, value);
  window.history.replaceState(window.history.state, "", `${url.pathname}${url.search}${url.hash}`);
  window.dispatchEvent(new Event(CHANGE));
}
