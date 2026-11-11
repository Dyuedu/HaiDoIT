/**
 * Đọc `GET /api/v1/city-shares?role=&level=&years=` qua proxy `/api/*` của web.
 *
 * Kiểu của envelope `{data, meta}` theo `docs/api/openapi.json` (`Envelope[CitySharesData]`,
 * `Stat`, `Meta`, `CellMeta`, `ErrorEnvelope`). `fetchCityShares` không ném lỗi: nó trả dữ liệu,
 * lỗi chuẩn của API, hoặc "không đọc được" khi mạng hỏng hay body sai hợp đồng.
 */

import { BAR_CITIES, LEGEND_CITIES } from "./labels";

export type DisplayState = "shown" | "low_sample_shown" | "null_data";
export type MeasureKind = "composition_share" | "skill_rate" | "percentile" | "level_share";
export type SnapshotStatus = "published" | "partial";

/** Một con số kèm trạng thái hiển thị và ô đã sinh ra nó. */
export interface Stat {
  /** Chưa làm tròn, 0–1. `null` khi `display = null_data`. */
  value: number | null;
  kind: MeasureKind;
  display: DisplayState;
  cell_id: string;
}

export interface CellMeta {
  n: number;
  fallback_label: string | null;
  seniority_mix: Record<string, number>;
  n_by_measure: Record<string, number>;
  insufficient_by_measure: Record<string, boolean>;
}

export interface Thresholds {
  min_sample: number;
  theta_core: number;
  theta_common: number;
}

export interface CoverageNote {
  code: string;
  text: string;
}

export interface Meta {
  /** `YYYY-MM-DD` theo `Asia/Ho_Chi_Minh`. */
  snapshot_date: string;
  snapshot_status: SnapshotStatus;
  sources: string[];
  sources_failed: string[];
  thresholds: Thresholds;
  coverage_notes: CoverageNote[];
  cells: Record<string, CellMeta>;
}

/**
 * Tỷ trọng thành phố đã qua `fetchCityShares`: theo hợp đồng luôn có `value`, và chỉ tỷ trọng
 * cấu phần nên `display` không bao giờ là `null_data`.
 */
export interface ShareStat extends Stat {
  value: number;
  kind: "composition_share";
  display: "shown" | "low_sample_shown";
}

export interface CityShareRow {
  city: string;
  share: ShareStat;
}

export interface CitySharesData {
  role: string;
  /** Cấp bậc lọc đã dùng (#163): `all`, `entry`, hoặc một cấp. */
  level: string;
  /** Mốc số năm đã dùng (#280): `any` hoặc `N` (tối đa N năm). */
  years: string;
  /**
   * Ô của các tin không ghi số năm (#280), số tin là `meta.cells[...].n`. `null` khi `years = any`.
   */
  years_unstated_cell_id: string | null;
  total_cell_id: string;
  rows: CityShareRow[];
}

export interface Envelope<T> {
  data: T;
  meta: Meta;
}

export type CitySharesEnvelope = Envelope<CitySharesData>;

export interface ErrorBody {
  code: string;
  message: string;
  snapshot_date: string | null;
}

export interface ErrorEnvelope {
  error: ErrorBody;
}

export type CitySharesResult =
  | { kind: "ok"; envelope: CitySharesEnvelope }
  | {
      kind: "error";
      code: string;
      message: string;
      /** Chỉ có giá trị ở `unknown_cell`. */
      snapshotDate: string | null;
      /** Có nút "Thử lại" hay không. `unknown_cell` thì không: thử lại vẫn ra cùng kết quả. */
      retryable: boolean;
    }
  | { kind: "unreadable" };

/** Năm dòng phải có trong mọi envelope: ba thành phố, Khác, không xác định. */
const REQUIRED_CITIES: readonly string[] = [...BAR_CITIES, ...LEGEND_CITIES];
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;
const SHARE_DISPLAYS: readonly string[] = ["shown", "low_sample_shown"];
const SNAPSHOT_STATUSES: readonly string[] = ["published", "partial"];

/**
 * `level` là cấp bậc lọc (#163), `years` là mốc số năm (#280). Màn Bản đồ luôn gửi cả hai; bỏ trống thì không có tham
 * số và API trả mọi cấp, mọi số năm. Envelope có `data.level` hay `data.years` khác điều đã hỏi là sai hợp đồng: không
 * dùng, như khi `data.role` lệch.
 */
export async function fetchCityShares(
  role: string,
  options: { level?: string; years?: string; signal?: AbortSignal } = {},
): Promise<CitySharesResult> {
  let response: Response;
  let body: unknown;
  const query =
    `role=${encodeURIComponent(role)}` +
    (options.level === undefined ? "" : `&level=${encodeURIComponent(options.level)}`) +
    (options.years === undefined ? "" : `&years=${encodeURIComponent(options.years)}`);
  try {
    response = await fetch(`/api/v1/city-shares?${query}`, {
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

  return isCitySharesEnvelope(body, role, options.level, options.years)
    ? { kind: "ok", envelope: body }
    : { kind: "unreadable" };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function isCount(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}

function readErrorBody(body: unknown): ErrorBody | null {
  if (!isRecord(body) || !isRecord(body.error)) return null;
  const { code, message, snapshot_date: snapshotDate } = body.error;
  if (!isNonEmptyString(code) || !isNonEmptyString(message)) return null;
  return {
    code,
    message,
    snapshot_date: typeof snapshotDate === "string" && ISO_DATE.test(snapshotDate) ? snapshotDate : null,
  };
}

function isMeta(meta: unknown): meta is Meta {
  if (!isRecord(meta)) return false;
  const { thresholds, coverage_notes: notes } = meta;
  return (
    typeof meta.snapshot_date === "string" &&
    ISO_DATE.test(meta.snapshot_date) &&
    SNAPSHOT_STATUSES.includes(meta.snapshot_status as string) &&
    isStringArray(meta.sources) &&
    meta.sources.length > 0 &&
    isStringArray(meta.sources_failed) &&
    isRecord(thresholds) &&
    isCount(thresholds.min_sample) &&
    thresholds.min_sample > 0 &&
    Array.isArray(notes) &&
    notes.length > 0 &&
    notes.every(
      (note) => isRecord(note) && isNonEmptyString(note.code) && isNonEmptyString(note.text),
    ) &&
    isRecord(meta.cells)
  );
}

/**
 * Kiểm phần hợp đồng mà màn Bản đồ đọc. Sai một chỗ là cả envelope không dùng được: màn không
 * đoán, không vá số.
 */
function isCitySharesEnvelope(
  body: unknown,
  role: string,
  level: string | undefined,
  years: string | undefined,
): body is CitySharesEnvelope {
  if (!isRecord(body) || !isRecord(body.data) || !isMeta(body.meta)) return false;
  const { data, meta } = body;
  const hasCell = (cellId: unknown) =>
    isNonEmptyString(cellId) &&
    Object.hasOwn(meta.cells, cellId) &&
    isRecord(meta.cells[cellId]) &&
    isCount(meta.cells[cellId].n);

  if (
    data.role !== role ||
    !isNonEmptyString(data.level) ||
    (level !== undefined && data.level !== level) ||
    !isNonEmptyString(data.years) ||
    (years !== undefined && data.years !== years) ||
    (data.years === "any" ? data.years_unstated_cell_id !== null : !hasCell(data.years_unstated_cell_id)) ||
    !hasCell(data.total_cell_id) ||
    !Array.isArray(data.rows)
  ) {
    return false;
  }
  const cities = new Set<string>();
  for (const row of data.rows) {
    if (!isRecord(row) || !isNonEmptyString(row.city) || cities.has(row.city)) return false;
    cities.add(row.city);
    const share = row.share;
    if (
      !isRecord(share) ||
      share.kind !== "composition_share" ||
      !SHARE_DISPLAYS.includes(share.display as string) ||
      typeof share.value !== "number" ||
      !(share.value >= 0 && share.value <= 1) ||
      !hasCell(share.cell_id)
    ) {
      return false;
    }
  }
  return REQUIRED_CITIES.every((city) => cities.has(city));
}
