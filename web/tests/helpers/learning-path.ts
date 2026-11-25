import { vi } from "vitest";

import type { LearningPathEnvelope } from "@/lib/learning-path";

import aiMl from "../fixtures/learning-path-ai_ml.json";
import backend from "../fixtures/learning-path-backend.json";
import backendIntern from "../fixtures/learning-path-backend.intern.json";
import dataEngineer from "../fixtures/learning-path-data_engineer.json";
import skills from "../fixtures/skills.json";
import { jsonResponse } from "./fetch";

type Reply = Response | Promise<Response>;

/** Response của API giả (#212), khóa bằng `tests/api/test_ad17_web_fixtures.py`. */
export const PATHS = {
  backend,
  backendIntern,
  data_engineer: dataEngineer,
  ai_ml: aiMl,
} as const;

export const NO_REAL_PATH = {
  error: { code: "unknown_cell", message: "Lộ trình học chưa có số liệu thật.", snapshot_date: null },
};

export function clonePath(key: keyof typeof PATHS): LearningPathEnvelope {
  return structuredClone(PATHS[key]) as unknown as LearningPathEnvelope;
}

/** Cờ `have` và số đếm như API trả (`apply_have`). Chỉ test dựng body; web không đếm (AD-22). */
export function pathWithHave(key: keyof typeof PATHS, have: readonly string[]): LearningPathEnvelope {
  const body = clonePath(key);
  const owned = new Set(have);
  const all = body.data.stages.flatMap((stage) => stage.skills);
  for (const skill of all) skill.have = owned.has(skill.skill);
  body.data.have_on_path = all.filter((skill) => skill.have).length;
  body.data.current_stage = body.data.stages.find(
    (stage) => !(stage.choose_one ? stage.skills.some((s) => s.have) : stage.skills.every((s) => s.have)),
  )?.stage ?? null;
  const onPath = new Set(all.map((skill) => skill.skill));
  body.data.have_ignored = [...owned].filter((code) => !onPath.has(code)).sort();
  return body;
}

export interface PathRouteOptions {
  learningPath?: (params: Record<string, string>) => Reply;
  skills?: () => Reply;
}

function defaultPath(params: Record<string, string>): Response {
  const role = params.role as keyof typeof PATHS;
  if (!(role in PATHS)) return jsonResponse(404, NO_REAL_PATH);
  return jsonResponse(200, pathWithHave(role, (params.have ?? "").split(",").filter(Boolean)));
}

/** Thay `fetch` toàn cục cho màn lộ trình: `/api/v1/skills` và `/api/v1/learning-path`. */
export function routeLearningPath(options: PathRouteOptions = {}) {
  const log: { path: string; params: Record<string, string> }[] = [];
  const fetchMock = vi.fn(async (input: RequestInfo | URL, _init?: RequestInit) => {
    const url = new URL(String(input), "http://localhost");
    const params = Object.fromEntries(url.searchParams.entries());
    log.push({ path: url.pathname, params });
    switch (url.pathname) {
      case "/api/v1/skills":
        return options.skills ? options.skills() : jsonResponse(200, skills);
      case "/api/v1/learning-path":
        return options.learningPath ? options.learningPath(params) : defaultPath(params);
      default:
        throw new Error(`URL lạ: ${String(input)}`);
    }
  });
  vi.stubGlobal("fetch", fetchMock);
  return { fetchMock, calls: () => log.filter((call) => call.path === "/api/v1/learning-path") };
}
