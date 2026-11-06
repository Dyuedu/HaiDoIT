import { vi } from "vitest";

type Reply = Response | Promise<Response>;

/** Response JSON như proxy `/api/*` chuyển về. */
export function jsonResponse(status: number, body: unknown): Response {
  const text = typeof body === "string" ? body : JSON.stringify(body);
  return new Response(text, { status, headers: { "content-type": "application/json" } });
}

/**
 * Thay `fetch` toàn cục: mỗi lần gọi `/api/v1/city-shares?role=X` lấy reply kế tiếp trong
 * hàng của X. Hàng chỉ còn một reply thì reply đó dùng lại mãi.
 */
export function routeCityShares(replies: Record<string, (() => Reply)[]>) {
  const queues = Object.fromEntries(Object.entries(replies).map(([role, list]) => [role, [...list]]));
  const fetchMock = vi.fn(async (input: RequestInfo | URL, _init?: RequestInit) => {
    const url = new URL(String(input), "http://localhost");
    if (url.pathname !== "/api/v1/city-shares") throw new Error(`URL lạ: ${String(input)}`);
    const role = url.searchParams.get("role") ?? "";
    const queue = queues[role];
    if (!queue || queue.length === 0) throw new Error(`Không có reply cho role=${role}`);
    const next = queue.length > 1 ? queue.shift()! : queue[0];
    return next();
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

export interface Deferred<T> {
  promise: Promise<T>;
  resolve: (value: T) => void;
}

export function deferred<T>(): Deferred<T> {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => {
    resolve = done;
  });
  return { promise, resolve };
}
