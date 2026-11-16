import { vi } from "vitest";

import skills from "../fixtures/skills.json";
import backendEntryHave from "../fixtures/skill-rates-backend.entry-have.json";
import backendEntry from "../fixtures/skill-rates-backend.entry.json";
import backendIntern from "../fixtures/skill-rates-backend.intern.json";
import dataEngineerEntry from "../fixtures/skill-rates-data_engineer.entry.json";
import frontendEntry from "../fixtures/skill-rates-frontend.entry.json";
import { jsonResponse } from "./fetch";

type Reply = Response | Promise<Response>;

/** Response của API giả cho `skill-rates`, theo `role|level`. Có `have` thì lấy bản `-have` (đã sinh với java,sql,git). */
export const SKILL_RATES = {
  "backend|entry": backendEntry,
  "backend|entry|have": backendEntryHave,
  "backend|intern": backendIntern,
  "data_engineer|entry": dataEngineerEntry,
  "frontend|entry": frontendEntry,
} as const;

export const SKILLS = skills;

export const UNKNOWN_CELL = {
  error: {
    code: "unknown_cell",
    message: "Không có ô thống kê nào cho vai trò và cấp bậc đã chọn.",
    snapshot_date: "2026-11-03",
  },
};

export interface ApiCall {
  path: string;
  params: Record<string, string>;
}

export interface RouteOptions {
  /** Thay reply của `skill-rates`. Mặc định: fixture theo `role|level`, có `have` thì bản `-have`; không có thì 404. */
  skillRates?: (params: Record<string, string>) => Reply;
  /** Reply của `role-for-title`. Mặc định: 404. */
  roleForTitle?: (title: string) => Reply;
  /** Reply của `skills`. Mặc định: `fixtures/skills.json`. */
  skills?: () => Reply;
}

/** Envelope `skill-rates` với cờ `have` và số đếm như API sẽ trả cho hồ sơ `have` (dùng cho test tick). */
export function skillRatesWithHave(key: keyof typeof SKILL_RATES, have: readonly string[]): unknown {
  const body = structuredClone(SKILL_RATES[key]) as {
    data: { rows: { skill: string; group: string | null; have: boolean }[]; core_size: number | null; have_core: number | null };
  };
  const owned = new Set(have);
  for (const row of body.data.rows) row.have = owned.has(row.skill);
  if (body.data.core_size !== null) {
    // Như bản giả ở API: đếm dòng core có `have`. Chỉ test dựng body; web không đếm (AD-22).
    body.data.have_core = body.data.rows.filter((row) => row.group === "core" && row.have).length;
  }
  return body;
}

function defaultSkillRates(params: Record<string, string>): Response {
  const have = (params.have ?? "").split(",").filter(Boolean);
  const key = `${params.role}|${params.level}` as keyof typeof SKILL_RATES;
  if (!(key in SKILL_RATES)) return jsonResponse(404, UNKNOWN_CELL);
  return jsonResponse(200, skillRatesWithHave(key, have));
}

/**
 * Thay `fetch` toàn cục cho màn hồ sơ kỹ năng: `/api/v1/skills`, `/api/v1/skill-rates`, `/api/v1/role-for-title`.
 * Trả hàm `calls()` liệt kê các lần gọi theo thứ tự.
 */
export function routeSkillProfile(options: RouteOptions = {}) {
  const log: ApiCall[] = [];
  const fetchMock = vi.fn(async (input: RequestInfo | URL, _init?: RequestInit) => {
    const url = new URL(String(input), "http://localhost");
    const params = Object.fromEntries(url.searchParams.entries());
    log.push({ path: url.pathname, params });
    switch (url.pathname) {
      case "/api/v1/skills":
        return options.skills ? options.skills() : jsonResponse(200, SKILLS);
      case "/api/v1/skill-rates":
        return options.skillRates ? options.skillRates(params) : defaultSkillRates(params);
      case "/api/v1/role-for-title":
        return options.roleForTitle
          ? options.roleForTitle(params.title ?? "")
          : jsonResponse(404, { error: { code: "not_found", message: "Không có đường dẫn này.", snapshot_date: null } });
      default:
        throw new Error(`URL lạ: ${String(input)}`);
    }
  });
  vi.stubGlobal("fetch", fetchMock);
  return {
    fetchMock,
    calls: (path?: string) => (path ? log.filter((call) => call.path === path) : [...log]),
  };
}

/** `{data: {status, role}}` của `role-for-title`. */
export function titleReply(status: "matched" | "generic" | "not_it", role: string | null = null): Response {
  return jsonResponse(200, { data: { status, role } });
}
