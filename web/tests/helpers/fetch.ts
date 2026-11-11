import { vi } from "vitest";

type Reply = Response | Promise<Response>;

/** Response JSON như proxy `/api/*` chuyển về. */
export function jsonResponse(status: number, body: unknown): Response {
  const text = typeof body === "string" ? body : JSON.stringify(body);
  return new Response(text, { status, headers: { "content-type": "application/json" } });
}

/**
 * Thay `fetch` toàn cục: mỗi lần gọi `/api/v1/city-shares?role=X&level=Y` lấy reply kế tiếp trong hàng của
 * `X|Y`, nếu không có thì hàng của `X`. Hàng chỉ còn một reply thì reply đó dùng lại mãi.
 *
 * Như API thật, bản thay trả lại cấp đã yêu cầu ở `data.level` khi reply là một envelope 200 (`echoLevel`, mặc định
 * bật): test không quan tâm cấp có thể dùng envelope của cấp nào cũng được. Test về cấp lệch tắt `echoLevel`.
 */
export function routeCityShares(
  replies: Record<string, (() => Reply)[]>,
  options: { echoLevel?: boolean } = {},
) {
  const echoLevel = options.echoLevel ?? true;
  const queues = Object.fromEntries(Object.entries(replies).map(([key, list]) => [key, [...list]]));
  const fetchMock = vi.fn(async (input: RequestInfo | URL, _init?: RequestInit) => {
    const url = new URL(String(input), "http://localhost");
    if (url.pathname !== "/api/v1/city-shares") throw new Error(`URL lạ: ${String(input)}`);
    const role = url.searchParams.get("role") ?? "";
    const level = url.searchParams.get("level");
    const key = level !== null && queues[`${role}|${level}`] ? `${role}|${level}` : role;
    const queue = queues[key];
    if (!queue || queue.length === 0) throw new Error(`Không có reply cho role=${role} level=${level}`);
    const next = queue.length > 1 ? queue.shift()! : queue[0];
    const reply = await next();
    return echoLevel && level !== null ? withLevel(reply, level) : reply;
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function withLevel(reply: Response, level: string): Promise<Response> {
  if (reply.status !== 200) return reply;
  const body: unknown = await reply.clone().json().catch(() => null);
  if (typeof body !== "object" || body === null || !("data" in body)) return reply;
  const data = (body as { data: unknown }).data;
  if (typeof data !== "object" || data === null || !("level" in data)) return reply;
  (data as { level: string }).level = level;
  return jsonResponse(200, body);
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
