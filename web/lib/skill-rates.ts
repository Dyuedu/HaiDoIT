/**
 * Hình của `GET /api/v1/skill-rates?role=&level=&have=` (#149), theo `docs/api/openapi.json`
 * (`Envelope[SkillRatesData]`). Màn hồ sơ kỹ năng (#152) đọc qua proxy `/api/*`.
 *
 * - Thứ tự dòng, cờ `have` từng dòng, `core_size` và `have_core` do API quyết (AD-22). Web không sắp xếp, không đếm.
 * - Ô đã dùng: `data.cell_id`; n và câu quay về ở `meta.cells[data.cell_id]`.
 * - `rate.display = null_data`: không có giá trị, không có nhóm; `core_size`/`have_core` là `null`.
 */

import {
  type ErrorEnvelope,
  type Meta,
  type Stat,
  isCount,
  isMeta,
  isNonEmptyString,
  isRecord,
  readErrorBody,
} from "./city-shares";
import { isSkillCode } from "./haido-keys";

export interface SkillRateStat extends Stat {
  kind: "skill_rate";
}

export type SkillGroup = "core" | "common" | "company_specific";

export interface SkillRateRow {
  skill: string;
  rate: SkillRateStat;
  /** `null` khi `rate.display = null_data`. */
  group: SkillGroup | null;
  /** Mã có trong `have=` của request. */
  have: boolean;
}

export interface SkillRatesData {
  role: string;
  level: string;
  cell_id: string;
  rows: SkillRateRow[];
  /** Số dòng core; `null` khi mọi tỷ lệ là `null_data`. */
  core_size: number | null;
  /** Số dòng core có `have`; `null` cùng lúc với `core_size`. */
  have_core: number | null;
}

export interface SkillRatesEnvelope {
  data: SkillRatesData;
  meta: Meta;
}

export type SkillRatesResult =
  | { kind: "ok"; envelope: SkillRatesEnvelope }
  | { kind: "error"; code: string; message: string; snapshotDate: string | null; retryable: boolean }
  | { kind: "unreadable" };

const GROUPS: readonly string[] = ["core", "common", "company_specific"];

/** URL của request, cũng dùng làm khóa so request hiện tại. Mã kỹ năng giữ nguyên thứ tự hồ sơ. */
export function skillRatesUrl(role: string, level: string, have: readonly string[]): string {
  const params = new URLSearchParams({ role, level });
  if (have.length > 0) params.set("have", have.join(","));
  return `/api/v1/skill-rates?${params.toString().replace(/%2C/g, ",")}`;
}

/**
 * Gọi `GET /api/v1/skill-rates` (#152). Không ném lỗi: trả dữ liệu, lỗi chuẩn của API, hoặc "không đọc được" khi mạng
 * hỏng hay body sai hợp đồng, cùng cách với `fetchNewcomerRoles`.
 */
export async function fetchSkillRates(options: {
  role: string;
  level: string;
  have: readonly string[];
  signal?: AbortSignal;
}): Promise<SkillRatesResult> {
  let response: Response;
  let body: unknown;
  try {
    response = await fetch(skillRatesUrl(options.role, options.level, options.have), {
      headers: { accept: "application/json" },
      cache: "no-store",
      signal: options.signal,
    });
    body = await response.json();
  } catch {
    return { kind: "unreadable" };
  }
  if (!response.ok) {
    const error = readErrorBody(body as ErrorEnvelope);
    if (!error) return { kind: "unreadable" };
    return {
      kind: "error",
      code: error.code,
      message: error.message,
      snapshotDate: error.snapshot_date,
      retryable: error.code !== "unknown_cell",
    };
  }
  return isSkillRatesEnvelope(body) ? { kind: "ok", envelope: body } : { kind: "unreadable" };
}

/** Kiểm phần hợp đồng mà màn đọc. Sai một chỗ là cả envelope không dùng: màn không đoán, không vá số. */
function isSkillRatesEnvelope(body: unknown): body is SkillRatesEnvelope {
  if (!isRecord(body) || !isRecord(body.data) || !isMeta(body.meta)) return false;
  const { data, meta } = body;
  if (!isNonEmptyString(data.role) || !isNonEmptyString(data.level) || !isNonEmptyString(data.cell_id)) return false;
  const cell = meta.cells[data.cell_id];
  if (!Object.hasOwn(meta.cells, data.cell_id) || !isRecord(cell) || !isCount(cell.n)) return false;
  if (cell.fallback_label !== null && !isNonEmptyString(cell.fallback_label)) return false;
  const counts = [data.core_size, data.have_core];
  if (counts.every((c) => c === null)) {
    // chưa đủ dữ liệu: không có số đếm
  } else if (!counts.every(isCount) || (data.have_core as number) > (data.core_size as number)) {
    return false;
  }
  if (!Array.isArray(data.rows) || data.rows.length === 0) return false;
  const seen = new Set<string>();
  for (const row of data.rows) {
    if (!isRecord(row) || typeof row.skill !== "string" || !isSkillCode(row.skill) || seen.has(row.skill)) return false;
    seen.add(row.skill);
    if (typeof row.have !== "boolean") return false;
    const rate = row.rate;
    if (!isRecord(rate) || rate.kind !== "skill_rate" || rate.cell_id !== data.cell_id) return false;
    if (rate.display === "shown") {
      if (typeof rate.value !== "number" || !(rate.value >= 0 && rate.value <= 1)) return false;
      if (typeof row.group !== "string" || !GROUPS.includes(row.group)) return false;
    } else if (rate.display !== "null_data" || rate.value !== null || row.group !== null) {
      return false;
    }
  }
  return true;
}
