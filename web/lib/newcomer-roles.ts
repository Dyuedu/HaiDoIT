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

import type { Meta, Stat } from "./city-shares";

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
