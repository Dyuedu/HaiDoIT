/**
 * Chức danh → vai trò (#150): đọc `GET /api/v1/role-for-title?title=` qua proxy `/api/*`.
 *
 * API chạy phép 6 trên chức danh (`haido_core/domain/classify.py`), nên vai trò của màn trùng vai trò của số liệu. Web
 * không so khớp chức danh. Response không có số nên không có Envelope: `{data: {status, role}}`.
 */

import { isRecord } from "./city-shares";
import { ROLE_OPTIONS } from "./labels";

export type TitleStatus = "matched" | "generic" | "not_it";

export type RoleForTitleResult =
  | { kind: "matched"; role: string }
  | { kind: "generic" }
  | { kind: "not_it" }
  | { kind: "unreadable" };

const ROLE_CODES = new Set(ROLE_OPTIONS.filter((option) => option.code !== "all").map((option) => option.code));

/** Gọi API. Không ném lỗi: lỗi mạng, lỗi API hay body sai hợp đồng đều là "không đọc được". */
export async function fetchRoleForTitle(title: string, options: { signal?: AbortSignal } = {}): Promise<RoleForTitleResult> {
  let body: unknown;
  try {
    const response = await fetch(`/api/v1/role-for-title?${new URLSearchParams({ title }).toString()}`, {
      headers: { accept: "application/json" },
      cache: "no-store",
      signal: options.signal,
    });
    if (!response.ok) return { kind: "unreadable" };
    body = await response.json();
  } catch {
    return { kind: "unreadable" };
  }
  if (!isRecord(body) || !isRecord(body.data)) return { kind: "unreadable" };
  const { status, role } = body.data;
  if (status === "matched") {
    return typeof role === "string" && ROLE_CODES.has(role) ? { kind: "matched", role } : { kind: "unreadable" };
  }
  if ((status === "generic" || status === "not_it") && role === null) return { kind: status };
  return { kind: "unreadable" };
}
