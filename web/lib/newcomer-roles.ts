/**
 * Hình của `GET /api/v1/newcomer-roles` (#144), theo `docs/api/openapi.json`
 * (`Envelope[NewcomerRolesData]`). Màn người mới (#147) đọc qua proxy `/api/*`.
 *
 * - Số tin entry-level: `meta.cells[row.entry_cell_id].n`.
 * - n của vai trò: `meta.cells[row.total_cell_id].n`.
 * - Tỷ lệ: `row.share`; `display = null_data` thì ghi "not enough data (n/min_sample)".
 *
 * Dòng đã theo thứ tự hiển thị của máy chủ. Web không sắp xếp lại, không tự tính (AD-22).
 */

import {
  type Meta,
  type Stat,
  isCount,
  isMeta,
  isNonEmptyString,
  isRecord,
  isStringArray,
  readErrorBody,
} from "./city-shares";

export interface LevelShareStat extends Stat {
  kind: "level_share";
}

export interface NewcomerRoleRow {
  role: string;
  total_cell_id: string;
  entry_cell_id: string;
  share: LevelShareStat;
}

export interface NewcomerRolesData {
  /** Các cấp bậc tính là entry-level, ví dụ `["intern", "fresher", "junior"]`. */
  levels: string[];
  rows: NewcomerRoleRow[];
}

export interface NewcomerRolesEnvelope {
  data: NewcomerRolesData;
  meta: Meta;
}

/** Số tin entry-level và n của một dòng, tra từ `meta.cells`. Thiếu ô thì ném lỗi. */
export function rowCounts(
  envelope: NewcomerRolesEnvelope,
  row: NewcomerRoleRow
): { entry: number; n: number } {
  const entry = envelope.meta.cells[row.entry_cell_id];
  const total = envelope.meta.cells[row.total_cell_id];
  if (!entry || !total) {
    throw new Error(`Thiếu ô trong meta.cells cho vai trò ${row.role}.`);
  }
  return { entry: entry.n, n: total.n };
}

export type NewcomerRolesResult =
  | { kind: "ok"; envelope: NewcomerRolesEnvelope }
  | {
      kind: "error";
      code: string;
      message: string;
      /** Chỉ có giá trị ở `unknown_cell`. */
      snapshotDate: string | null;
      /** `unknown_cell` thì không có nút "Thử lại": thử lại vẫn ra cùng kết quả. */
      retryable: boolean;
    }
  | { kind: "unreadable" };

/**
 * Gọi `GET /api/v1/newcomer-roles` qua proxy `/api/*` (#147). Không ném lỗi: trả dữ liệu, lỗi chuẩn của API, hoặc
 * "không đọc được" khi mạng hỏng hay body sai hợp đồng, cùng cách với `fetchCityShares`.
 */
export async function fetchNewcomerRoles(options: { signal?: AbortSignal } = {}): Promise<NewcomerRolesResult> {
  let response: Response;
  let body: unknown;
  try {
    response = await fetch("/api/v1/newcomer-roles", {
      headers: { accept: "application/json" },
      cache: "no-store",
      signal: options.signal,
    });
    body = await response.json();
  } catch {
    return { kind: "unreadable" };
  }
  if (!response.ok) {
    const error = readErrorBody(body);
    if (!error) return { kind: "unreadable" };
    return {
      kind: "error",
      code: error.code,
      message: error.message,
      snapshotDate: error.snapshot_date,
      retryable: error.code !== "unknown_cell",
    };
  }
  return isNewcomerRolesEnvelope(body) ? { kind: "ok", envelope: body } : { kind: "unreadable" };
}

/** Kiểm phần hợp đồng mà màn người mới đọc. Sai một chỗ là cả envelope không dùng: màn không đoán, không vá số. */
function isNewcomerRolesEnvelope(body: unknown): body is NewcomerRolesEnvelope {
  if (!isRecord(body) || !isRecord(body.data) || !isMeta(body.meta)) return false;
  const { data, meta } = body;
  const hasCell = (cellId: unknown) =>
    isNonEmptyString(cellId) &&
    Object.hasOwn(meta.cells, cellId) &&
    isRecord(meta.cells[cellId]) &&
    isCount(meta.cells[cellId].n);
  if (!isStringArray(data.levels) || data.levels.length === 0) return false;
  if (!Array.isArray(data.rows) || data.rows.length === 0) return false;
  const roles = new Set<string>();
  for (const row of data.rows) {
    if (!isRecord(row) || !isNonEmptyString(row.role) || roles.has(row.role)) return false;
    roles.add(row.role);
    if (!hasCell(row.total_cell_id) || !hasCell(row.entry_cell_id) || row.total_cell_id === row.entry_cell_id) {
      return false;
    }
    const share = row.share;
    if (!isRecord(share) || share.kind !== "level_share" || share.cell_id !== row.total_cell_id) return false;
    if (share.display === "shown") {
      if (typeof share.value !== "number" || !(share.value >= 0 && share.value <= 1)) return false;
    } else if (share.display !== "null_data" || share.value !== null) {
      return false;
    }
  }
  return true;
}
