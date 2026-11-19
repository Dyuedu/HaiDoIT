/**
 * Hình của `GET /api/v1/market-overview` (#327), theo `docs/api/openapi.json` (`Envelope[MarketOverviewData]`).
 * Phần toàn cảnh của Insights (#329) đọc qua proxy `/api/*`.
 *
 * Mọi tỷ trọng và mọi thứ hạng đã do máy chủ tính và xếp; web chỉ in, không cộng, không chia, không sắp xếp (AD-22).
 * Số tin của một phần là `meta.cells[share.cell_id].n`.
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

export interface OverviewShare {
  code: string;
  share: Stat;
}

export interface OverviewRole {
  role: string;
  cell_id: string;
  entry_cell_id: string;
  share: Stat;
  entry_share: Stat;
  level_mix: OverviewShare[];
  places: OverviewShare[];
}

export interface OverviewRanking {
  level: string;
  roles: string[];
}

export interface MarketOverviewData {
  total_cell_id: string;
  entry_cell_id: string;
  levels: string[];
  entry_levels: string[];
  level_mix: OverviewShare[];
  entry_share: Stat;
  big_cities_share: Stat;
  roles: OverviewRole[];
  places: OverviewShare[];
  levels_by_size: string[];
  roles_by_level: OverviewRanking[];
  roles_by_entry_share: string[];
  years: OverviewShare[];
}

export interface MarketOverviewEnvelope {
  data: MarketOverviewData;
  meta: Meta;
}

export type MarketOverviewResult =
  | { kind: "ok"; envelope: MarketOverviewEnvelope }
  | { kind: "error"; code: string; message: string; snapshotDate: string | null; retryable: boolean }
  | { kind: "unreadable" };

/** Gọi `GET /api/v1/market-overview`. Không ném lỗi, cùng cách với `fetchNewcomerRoles`. */
export async function fetchMarketOverview(options: { signal?: AbortSignal } = {}): Promise<MarketOverviewResult> {
  let response: Response;
  let body: unknown;
  try {
    response = await fetch("/api/v1/market-overview", {
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
  return isMarketOverviewEnvelope(body) ? { kind: "ok", envelope: body } : { kind: "unreadable" };
}

const DISPLAYS: readonly string[] = ["shown", "low_sample_shown", "null_data"];

/** Kiểm phần hợp đồng mà màn đọc. Sai một chỗ là cả envelope không dùng: màn không đoán, không vá số. */
export function isMarketOverviewEnvelope(body: unknown): body is MarketOverviewEnvelope {
  if (!isRecord(body) || !isRecord(body.data) || !isMeta(body.meta)) return false;
  const { data, meta } = body;
  const hasCell = (cellId: unknown) =>
    isNonEmptyString(cellId) &&
    Object.hasOwn(meta.cells, cellId) &&
    isRecord(meta.cells[cellId]) &&
    isCount(meta.cells[cellId].n);
  const isStat = (stat: unknown, kind: string): boolean => {
    if (!isRecord(stat) || stat.kind !== kind || !DISPLAYS.includes(stat.display as string) || !hasCell(stat.cell_id)) {
      return false;
    }
    if (stat.display === "null_data") return stat.value === null;
    return typeof stat.value === "number" && stat.value >= 0 && stat.value <= 1;
  };
  const isShares = (rows: unknown, kind: string): rows is OverviewShare[] =>
    Array.isArray(rows) && rows.every((row) => isRecord(row) && isNonEmptyString(row.code) && isStat(row.share, kind));

  if (!hasCell(data.total_cell_id) || !hasCell(data.entry_cell_id)) return false;
  if (!isStringArray(data.levels) || data.levels.length === 0 || !isStringArray(data.entry_levels)) return false;
  const levels = data.levels;
  const sameLevels = (rows: OverviewShare[]) => rows.map((r) => r.code).join() === levels.join();
  if (!isShares(data.level_mix, "level_share") || !sameLevels(data.level_mix)) return false;
  if (!isStat(data.entry_share, "level_share") || !isStat(data.big_cities_share, "composition_share")) return false;
  if (!isShares(data.places, "composition_share") || data.places.length === 0) return false;
  if (!isShares(data.years, "composition_share") || data.years.length === 0) return false;
  if (!Array.isArray(data.roles) || data.roles.length === 0) return false;
  const roles = new Set<string>();
  for (const row of data.roles) {
    if (!isRecord(row) || !isNonEmptyString(row.role) || roles.has(row.role)) return false;
    roles.add(row.role);
    if (!hasCell(row.cell_id) || !hasCell(row.entry_cell_id)) return false;
    if (!isStat(row.share, "composition_share") || !isStat(row.entry_share, "level_share")) return false;
    if (!isShares(row.level_mix, "level_share") || !sameLevels(row.level_mix)) return false;
    if (!isShares(row.places, "composition_share")) return false;
  }
  const sameRoles = (list: unknown) => isStringArray(list) && list.length === roles.size && list.every((r) => roles.has(r));
  if (!isStringArray(data.levels_by_size) || !data.levels_by_size.every((lv) => levels.includes(lv))) return false;
  if (!Array.isArray(data.roles_by_level) || data.roles_by_level.length !== levels.length) return false;
  if (!data.roles_by_level.every((r, i) => isRecord(r) && r.level === levels[i] && sameRoles(r.roles))) return false;
  return isStringArray(data.roles_by_entry_share) && data.roles_by_entry_share.every((r) => roles.has(r));
}
