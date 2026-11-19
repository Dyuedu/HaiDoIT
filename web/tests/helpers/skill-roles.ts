import { vi } from "vitest";

import newcomerRoles from "../fixtures/newcomer-roles.json";
import abap from "../fixtures/skill-roles-abap.json";
import figma from "../fixtures/skill-roles-figma.json";
import machineLearning from "../fixtures/skill-roles-machine_learning.json";
import python from "../fixtures/skill-roles-python.json";
import sap from "../fixtures/skill-roles-sap.json";
import skills from "../fixtures/skills.json";
import { jsonResponse } from "./fetch";

type Reply = Response | Promise<Response>;

/** Response của API giả cho `skill-roles?skill=` (#166). */
export const SKILL_ROLES = { python, figma, abap, sap, machine_learning: machineLearning } as const;

export const UNKNOWN_SKILL_CELL = {
  error: { code: "unknown_cell", message: "Không có ô thống kê nào cho kỹ năng đã chọn.", snapshot_date: "2026-11-03" },
};

export interface InsightsRouteOptions {
  /** Thay reply của `market-overview` (#329). Mặc định: không bao giờ trả, phần toàn cảnh đứng ở trạng thái đang tải. */
  marketOverview?: () => Reply;
  /** Thay reply của `skill-roles`. Mặc định: fixture theo `skill`, không có thì 404 `unknown_cell`. */
  skillRoles?: (skill: string) => Reply;
  /** Thay reply của `skills`. Mặc định: `fixtures/skills.json`. */
  skills?: () => Reply;
}

/**
 * Thay `fetch` toàn cục cho trang `/insights`: `/api/v1/newcomer-roles`, `/api/v1/skills`, `/api/v1/skill-roles`.
 * Trả hàm `calls()` liệt kê các lần gọi theo thứ tự.
 */
export function routeInsights(options: InsightsRouteOptions = {}) {
  const log: { path: string; params: Record<string, string> }[] = [];
  const fetchMock = vi.fn(async (input: RequestInfo | URL, _init?: RequestInit) => {
    const url = new URL(String(input), "http://localhost");
    const params = Object.fromEntries(url.searchParams.entries());
    log.push({ path: url.pathname, params });
    switch (url.pathname) {
      case "/api/v1/newcomer-roles":
        return jsonResponse(200, newcomerRoles);
      case "/api/v1/market-overview":
        // Từ #329 /insights mở đầu bằng toàn cảnh; mặc định giữ nó ở trạng thái đang tải.
        return options.marketOverview ? options.marketOverview() : new Promise<Response>(() => {});
      case "/api/v1/skills":
        return options.skills ? options.skills() : jsonResponse(200, skills);
      case "/api/v1/skill-roles": {
        const skill = params.skill ?? "";
        if (options.skillRoles) return options.skillRoles(skill);
        return Object.hasOwn(SKILL_ROLES, skill)
          ? jsonResponse(200, SKILL_ROLES[skill as keyof typeof SKILL_ROLES])
          : jsonResponse(404, UNKNOWN_SKILL_CELL);
      }
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
