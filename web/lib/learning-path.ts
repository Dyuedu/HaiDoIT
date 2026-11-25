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

import {
  type ErrorEnvelope,
  type Meta,
  type Stat,
  isCount,
  isMeta,
  isNonEmptyString,
  isRecord,
  isStringArray,
} from "./city-shares";
import { isSkillCode, MAX_PROFILE_SKILLS } from "./haido-keys";
import type { SkillGroup } from "./skill-rates";

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
  group: SkillGroup | null;
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
  /** Tên chủ đề của chặng. */
  title: string;
  /** Các kỹ năng là lựa chọn thay nhau: API coi chặng là xong khi đã có một kỹ năng. */
  choose_one: boolean;
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
  /** Chặng đầu chưa xong; `null` khi mọi chặng đã xong hoặc `not_ready`. */
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

const GROUPS: readonly string[] = ["core", "common", "company_specific"];

function isOrdinal(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value > 0;
}

function isPathSkill(value: unknown, cellId: string): value is PathSkill {
  if (!isRecord(value) || !isRecord(value.rate) || !isRecord(value.resource)) return false;
  const { rate, resource } = value;
  if (typeof value.skill !== "string" || !isSkillCode(value.skill)) return false;
  if (typeof value.have !== "boolean" || !isNonEmptyString(value.blurb)) return false;
  if (!isStringArray(value.foundation_for) || !isStringArray(value.prerequisite_for)) return false;
  // Link đi thẳng vào `href`: chỉ nhận https.
  if (!isNonEmptyString(resource.title) || typeof resource.url !== "string" || !/^https:\/\/\S+$/.test(resource.url)) {
    return false;
  }
  if (rate.kind !== "skill_rate" || rate.cell_id !== cellId) return false;
  if (rate.display === "null_data") return rate.value === null && value.group === null;
  return (
    rate.display === "shown" &&
    typeof rate.value === "number" &&
    rate.value >= 0 &&
    rate.value <= 1 &&
    typeof value.group === "string" &&
    GROUPS.includes(value.group)
  );
}

function hasCell(meta: Meta, id: string): boolean {
  const cell: unknown = Object.hasOwn(meta.cells, id) ? meta.cells[id] : undefined;
  return isRecord(cell) && isCount(cell.n) && (cell.fallback_label === null || isNonEmptyString(cell.fallback_label));
}

/**
 * Kiểm phần hợp đồng mà màn đọc. Sai một chỗ là cả envelope không dùng: màn không đoán, không vá số. Không đếm lại
 * `have_on_path`, `current_stage` (AD-22), chỉ kiểm kiểu và miền.
 */
function isEnvelope(body: unknown): body is LearningPathEnvelope {
  if (!isRecord(body) || !isRecord(body.data) || !isMeta(body.meta)) return false;
  const { data, meta } = body;
  if (!isNonEmptyString(data.role) || !isNonEmptyString(data.level)) return false;
  if (!isNonEmptyString(data.entry_cell_id) || !hasCell(meta, data.entry_cell_id)) return false;
  if (!Array.isArray(data.stages) || !isCount(data.have_on_path) || !isCount(data.path_size)) return false;
  if (data.have_on_path > data.path_size || !isStringArray(data.have_ignored)) return false;
  if (data.current_stage !== null && !isOrdinal(data.current_stage)) return false;
  if (data.status === "not_ready") return data.stages.length === 0;
  if (data.status !== "ready" || data.stages.length === 0) return false;
  const cellId = data.cell_id;
  if (!isNonEmptyString(cellId) || !hasCell(meta, cellId)) return false;
  return data.stages.every(
    (stage, index) =>
      isRecord(stage) &&
      stage.stage === index + 1 &&
      Array.isArray(stage.skills) &&
      typeof stage.title === "string" &&
      stage.title.trim() !== "" &&
      typeof stage.choose_one === "boolean" &&
      stage.skills.length >= (stage.choose_one ? 2 : 1) &&
      stage.skills.every((skill) => isPathSkill(skill, cellId)),
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
  // API trả lại đúng vai trò và cấp đã hỏi; lệch thì số không phải của lộ trình đang xem.
  return isEnvelope(body) && body.data.role === role && body.data.level === level
    ? { kind: "ok", envelope: body }
    : { kind: "unreadable" };
}
