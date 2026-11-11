import { vi } from "vitest";

type Reply = Response | Promise<Response>;

/** Response JSON như proxy `/api/*` chuyển về. */
export function jsonResponse(status: number, body: unknown): Response {
  const text = typeof body === "string" ? body : JSON.stringify(body);
  return new Response(text, { status, headers: { "content-type": "application/json" } });
}

/**
 * Thay `fetch` toàn cục: mỗi lần gọi `/api/v1/city-shares?role=X&level=Y&years=Z` lấy reply kế tiếp trong hàng của
 * `X|Y|Z`, nếu không có thì hàng của `X|Y`, rồi hàng của `X`. Hàng chỉ còn một reply thì reply đó dùng lại mãi.
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
    const years = url.searchParams.get("years");
    const full = `${role}|${level}|${years}`;
    const key =
      years !== null && level !== null && queues[full]
        ? full
        : level !== null && queues[`${role}|${level}`]
          ? `${role}|${level}`
          : role;
    const queue = queues[key];
    if (!queue || queue.length === 0) throw new Error(`Không có reply cho role=${role} level=${level}`);
    const next = queue.length > 1 ? queue.shift()! : queue[0];
    const reply = await next();
    return echoLevel && (level !== null || years !== null) ? withFilters(reply, level, years) : reply;
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

/** Như API thật: trả lại cấp và số năm đã hỏi ở `data.level`, `data.years` (#163, #280). */
async function withFilters(reply: Response, level: string | null, years: string | null): Promise<Response> {
  if (reply.status !== 200) return reply;
  const body: unknown = await reply.clone().json().catch(() => null);
  if (typeof body !== "object" || body === null || !("data" in body)) return reply;
  const { data, meta } = body as { data: unknown; meta?: { cells?: Record<string, unknown> } };
  if (typeof data !== "object" || data === null || !("level" in data)) return reply;
  const record = data as { level: string; years?: string; years_unstated_cell_id?: string | null };
  if (level !== null) record.level = level;
  if (years !== null && record.years !== years) {
    record.years = years;
    if (years === "any") {
      record.years_unstated_cell_id = null;
    } else if (!record.years_unstated_cell_id && meta?.cells) {
      // Envelope dựng cho `any` mà test hỏi một mốc: thêm ô số tin bị bỏ n = 0 cho đúng hợp đồng.
      record.years_unstated_cell_id = "vn.echo.ynone";
      meta.cells["vn.echo.ynone"] = {
        n: 0,
        fallback_label: null,
        seniority_mix: {},
        n_by_measure: {},
        insufficient_by_measure: {},
      };
    }
  }
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
