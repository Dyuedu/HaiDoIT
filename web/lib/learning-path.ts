/**
 * Đọc `GET /api/v1/learning-path?role=&level=&have=` (#212) qua proxy `/api/*`.
 *
 * Kiểu theo `docs/api/openapi.json` (`Envelope[LearningPathData]`). Lộ trình đã xếp sẵn: web không sắp xếp, không
 * tính chặng, không đếm "N of M" hay chặng hiện tại (AD-7, AD-22); chỉ gửi mã kỹ năng của hồ sơ qua `have`.
 * Chặng là thuộc tính của từng kỹ năng: đổi `have` không đổi thứ tự.
 *
 * - Tỷ lệ: `skill.rate`; số tin entry-level: `meta.cells[data.entry_cell_id].n` (có cả khi `cell_id` quay về).
 * - `status = not_ready`: không có chặng; gợi ý hồ sơ kỹ năng của vai trò.
 */

import type { ErrorEnvelope, Meta, Stat } from "./city-shares";
import { isSkillCode, MAX_PROFILE_SKILLS } from "./haido-keys";

export interface SkillRateStat extends Stat {
  kind: "skill_rate";
}

export interface PathResource {
  title: string;
  url: string;
}

export interface PathSkill {
  /** Mã snake_case, có trong bộ từ vựng. */
  skill: string;
  rate: SkillRateStat;
  /** `core`, `common`, `company_specific`; `null` khi `rate` là `null_data`. */
  group: string | null;
  /** Không rỗng khi là kỹ năng nền tảng: ghi "Kỹ năng nền tảng (cần cho X)". */
  foundation_for: string[];
  prerequisite_for: string[];
  have: boolean;
  /** Lời dẫn viết sẵn, không có số ngoài tên công nghệ. */
  blurb: string;
  resource: PathResource;
}

export interface PathStage {
  /** Từ 1, liền nhau. */
  stage: number;
  skills: PathSkill[];
}

export type PathStatus = "ready" | "not_ready";

export interface LearningPathData {
  role: string;
  level: string;
  status: PathStatus;
  /** Ô của các tỷ lệ; `null` khi `not_ready`. */
  cell_id: string | null;
  entry_cell_id: string;
  stages: PathStage[];
  /** Chặng đầu còn kỹ năng chưa có; `null` khi đã có hết hoặc `not_ready`. */
  current_stage: number | null;
  have_on_path: number;
  path_size: number;
  have_ignored: string[];
}

export interface LearningPathEnvelope {
  data: LearningPathData;
  meta: Meta;
}

export type LearningPathResult =
  | { kind: "ok"; envelope: LearningPathEnvelope }
  | { kind: "error"; code: string; message: string; snapshotDate: string | null; retryable: boolean }
  | { kind: "unreadable" };

/**
 * URL của lộ trình. `have` gửi mã hồ sơ sau khi chỉ lọc đầu vào: bỏ mã trùng (giữ thứ tự gặp đầu), bỏ mã sai định dạng
 * (`isSkillCode`), rồi lấy tối đa `MAX_PROFILE_SKILLS` mã đầu. Không đếm, không sắp xếp, không tính chặng (AD-22).
 */
export function learningPathUrl(role: string, level: string, have: readonly string[]): string {
  const base = `/api/v1/learning-path?role=${encodeURIComponent(role)}&level=${encodeURIComponent(level)}`;
  const codes = [...new Set(have)].filter(isSkillCode).slice(0, MAX_PROFILE_SKILLS);
  return codes.length === 0 ? base : `${base}&have=${encodeURIComponent(codes.join(","))}`;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isEnvelope(body: unknown): body is LearningPathEnvelope {
  if (!isRecord(body) || !isRecord(body.data) || !isRecord(body.meta)) return false;
  const { data } = body;
  return (
    (data.status === "ready" || data.status === "not_ready") &&
    typeof data.entry_cell_id === "string" &&
    Array.isArray(data.stages) &&
    isRecord(body.meta.cells)
  );
}

export async function fetchLearningPath(
  role: string,
  level: string,
  have: readonly string[],
  options: { signal?: AbortSignal } = {},
): Promise<LearningPathResult> {
  let response: Response;
  let body: unknown;
  try {
    response = await fetch(learningPathUrl(role, level, have), {
      headers: { accept: "application/json" },
      cache: "no-store",
      signal: options.signal,
    });
    body = await response.json();
  } catch {
    return { kind: "unreadable" };
  }
  if (!response.ok) {
    const error = (body as Partial<ErrorEnvelope> | null)?.error;
    if (!error || typeof error.code !== "string" || typeof error.message !== "string") {
      return { kind: "unreadable" };
    }
    return {
      kind: "error",
      code: error.code,
      message: error.message,
      snapshotDate: typeof error.snapshot_date === "string" ? error.snapshot_date : null,
      // Thử lại vẫn ra cùng kết quả với `unknown_cell` và `invalid_query` (422): chỉ lỗi máy chủ mới đáng thử lại.
      retryable: error.code !== "unknown_cell" && error.code !== "invalid_query",
    };
  }
  return isEnvelope(body) ? { kind: "ok", envelope: body } : { kind: "unreadable" };
}
