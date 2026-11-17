/**
 * Hình của `GET /api/v1/skill-roles?skill=` (#166), theo `docs/api/openapi.json` (`Envelope[SkillRolesData]`).
 * Màn "kỹ năng này dùng ở vai trò nào" (#169) đọc qua proxy `/api/*`.
 *
 * - Mỗi vai trò một dòng, đã theo thứ tự hiển thị của máy chủ. Web không sắp xếp, không tự tính (AD-22).
 * - Tỷ lệ: `row.share`; cỡ mẫu của tỷ lệ: `rowN` = `meta.cells[row.share.cell_id].n_by_measure.skill_count` (số tin đã quét
 *   kỹ năng), không phải `n` của ô (số tin của ô, cùng số với màn người mới).
 * - `share.display = null_data`: ghi "not enough data (rowN/min_sample)", `min_sample` ở `meta.thresholds`.
 * - `data.mentioned = false`: ghi rằng chưa tin nào, ở cấp nào, nhắc kỹ năng. Cờ do máy chủ tính, web không suy từ các dòng.
 * - `data.level` (`entry`) là tham số `level` để mở `/ho-so-ky-nang?role=&level=` (#111).
 * - Câu trên màn không có chữ số (DEC-6): số nằm ở ô riêng của nó, kèm n.
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
  readErrorBody,
} from "./city-shares";
import { isSkillCode } from "./haido-keys";

export interface SkillRateStat extends Stat {
  kind: "skill_rate";
}

export interface SkillLabel {
  code: string;
  name_en: string;
  name_vi: string;
}

export interface SkillRoleRow {
  role: string;
  /** `cell_id` là `vn.<role>.entry`. */
  share: SkillRateStat;
}

export interface SkillRolesData {
  skill: SkillLabel;
  /** Mã nhóm cấp bậc của mọi dòng (`entry`): dùng làm `level` khi mở hồ sơ kỹ năng của một vai trò. */
  level: string;
  /** Các cấp bậc tính là entry-level, ví dụ `["intern", "fresher", "junior"]`. */
  levels: string[];
  /** `false`: không tin nào, ở cấp nào, nhắc kỹ năng (kể cả khi mọi ô entry-level bị ẩn). */
  mentioned: boolean;
  rows: SkillRoleRow[];
}

export interface SkillRolesEnvelope {
  data: SkillRolesData;
  meta: Meta;
}

/**
 * Cỡ mẫu của tỷ lệ (số X trong "not enough data (X/30)"), tra từ `meta.cells`: `n_by_measure.skill_count` (số tin đã quét
 * kỹ năng), thiếu thì `n` của ô, đúng như quy tắc của Envelope. Thiếu ô thì ném lỗi.
 */
export function rowN(envelope: SkillRolesEnvelope, row: SkillRoleRow): number {
  const cell = envelope.meta.cells[row.share.cell_id];
  if (!cell) throw new Error(`Thiếu ô trong meta.cells cho vai trò ${row.role}.`);
  return cell.n_by_measure?.skill_count ?? cell.n;
}

export type SkillRolesResult =
  | { kind: "ok"; envelope: SkillRolesEnvelope }
  | {
      kind: "error";
      code: string;
      message: string;
      /** Chỉ có giá trị ở `unknown_cell`. */
      snapshotDate: string | null;
      /** `unknown_skill`, `unknown_cell` và `invalid_query` không có nút "Thử lại": thử lại vẫn ra cùng kết quả. */
      retryable: boolean;
    }
  | { kind: "unreadable" };

const NOT_RETRYABLE: ReadonlySet<string> = new Set(["unknown_cell", "unknown_skill", "invalid_query"]);

/** URL của request, cũng dùng làm khóa so request hiện tại. */
export function skillRolesUrl(skill: string): string {
  return `/api/v1/skill-roles?${new URLSearchParams({ skill }).toString()}`;
}

/**
 * Gọi `GET /api/v1/skill-roles` (#169). Không ném lỗi: trả dữ liệu, lỗi chuẩn của API, hoặc "không đọc được" khi mạng
 * hỏng hay body sai hợp đồng, cùng cách với `fetchSkillRates`.
 */
export async function fetchSkillRoles(options: { skill: string; signal?: AbortSignal }): Promise<SkillRolesResult> {
  let response: Response;
  let body: unknown;
  try {
    response = await fetch(skillRolesUrl(options.skill), {
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
      retryable: !NOT_RETRYABLE.has(error.code),
    };
  }
  return isSkillRolesEnvelope(body) ? { kind: "ok", envelope: body } : { kind: "unreadable" };
}

/** Kiểm phần hợp đồng mà màn đọc. Sai một chỗ là cả envelope không dùng: màn không đoán, không vá số. */
function isSkillRolesEnvelope(body: unknown): body is SkillRolesEnvelope {
  if (!isRecord(body) || !isRecord(body.data) || !isMeta(body.meta)) return false;
  const { data, meta } = body;
  const skill = data.skill;
  if (
    !isRecord(skill) ||
    typeof skill.code !== "string" ||
    !isSkillCode(skill.code) ||
    !isNonEmptyString(skill.name_en) ||
    !isNonEmptyString(skill.name_vi)
  ) {
    return false;
  }
  if (!isNonEmptyString(data.level)) return false;
  if (!isStringArray(data.levels) || data.levels.length === 0) return false;
  if (typeof data.mentioned !== "boolean") return false;
  if (!Array.isArray(data.rows) || data.rows.length === 0) return false;
  const roles = new Set<string>();
  for (const row of data.rows) {
    if (!isRecord(row) || !isNonEmptyString(row.role) || roles.has(row.role)) return false;
    roles.add(row.role);
    const share = row.share;
    if (!isRecord(share) || share.kind !== "skill_rate" || share.cell_id !== `vn.${row.role}.entry`) return false;
    const cellId = share.cell_id as string;
    if (!Object.hasOwn(meta.cells, cellId) || !isRecord(meta.cells[cellId]) || !isCount(meta.cells[cellId].n)) {
      return false;
    }
    if (share.display === "shown") {
      if (typeof share.value !== "number" || !(share.value >= 0 && share.value <= 1)) return false;
    } else if (share.display !== "null_data" || share.value !== null) {
      return false;
    }
  }
  return true;
}
