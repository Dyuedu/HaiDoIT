/**
 * Hàm thuần: envelope `city-shares` → những gì màn Bản đồ hiện (thanh, chú thích, bảng, chú
 * thích snapshot).
 *
 * Không tự tính số nào. Chỉ đọc `share.value`, `share.display`, `meta.cells[cell_id].n`,
 * `meta.thresholds.min_sample` và `n` của `data.total_cell_id`; không cộng, không chia, không so
 * `n` với ngưỡng. Làm tròn đúng một lần, ở `formatPercent`.
 */

import type { CityShareRow, CitySharesEnvelope, CoverageNote } from "./city-shares";
import { BAR_CITIES, cityLabel, LEGEND_CITIES, levelLabel, roleLabel, yearsLabel } from "./labels";

/** Một dòng có tỷ trọng: thanh ở lối 2D, hoặc dòng chú thích Khác / không xác định. */
export interface ShareLine {
  city: string;
  label: string;
  /** `share.value` nguyên, chưa làm tròn: độ rộng thanh = value × 100% của rãnh. */
  value: number;
  /** Phần trăm đã định dạng, ví dụ "47,0%". */
  percent: string;
  n: number;
  nText: string;
  /** `share.display = low_sample_shown`. */
  lowSample: boolean;
  /** Nhãn luôn hiện khi mẫu nhỏ; `null` khi không. */
  lowSampleNote: string | null;
  /** Tên đọc được của dòng: tên nơi, phần trăm, n, và câu mẫu nhỏ nếu có. */
  accessibleName: string;
}

export interface TableRow {
  city: string;
  label: string;
  /** Phần trăm khi `display = shown`, ngược lại "chưa đủ dữ liệu". */
  share: string;
  shareShown: boolean;
  nText: string;
  note: string;
}

export interface TableTotal {
  label: string;
  share: string;
  nText: string;
}

export interface SnapshotCaption {
  /** `meta.sources` đúng như API gửi. */
  sources: string[];
  snapshotDate: string;
  /** Mọi `meta.coverage_notes`, `text` in nguyên văn, `code` làm khóa. */
  notes: CoverageNote[];
  /** Câu nguồn lỗi khi snapshot `partial` có nguồn lỗi; ngược lại `null`. */
  failedSources: string | null;
  /** Bộ lọc đang dùng (#280): "vai trò · cấp bậc · số năm". */
  filters: string;
}

export interface CitySharesView {
  role: string;
  roleLabel: string;
  /** Cấp bậc lọc của envelope (`data.level`) và nhãn tiếng Việt của nó. */
  level: string;
  levelLabel: string;
  /** Mốc số năm của envelope (`data.years`, #280) và nhãn tiếng Việt của nó. */
  years: string;
  yearsLabel: string;
  /** Câu số tin bị bỏ vì không ghi số năm khi `years` khác `any`; ngược lại `null`. */
  unstatedNote: string | null;
  bars: ShareLine[];
  legend: ShareLine[];
  table: { rows: TableRow[]; total: TableTotal; roundingNote: string };
  caption: SnapshotCaption;
}

export const NOT_ENOUGH_DATA = "chưa đủ dữ liệu";
export const ROUNDING_NOTE = "Tổng các dòng có thể lệch 0,1% do làm tròn.";
export const FAILED_SOURCES_PREFIX = "Nguồn lỗi ở snapshot này: ";

const PERCENT = new Intl.NumberFormat("vi-VN", {
  style: "percent",
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});
const COUNT = new Intl.NumberFormat("vi-VN");

/** Tỷ lệ 0–1 → "47,0%". Lần làm tròn duy nhất của giá trị. */
export function formatPercent(value: number): string {
  return PERCENT.format(value);
}

/** Số tin kiểu Việt Nam: "3.586". */
export function formatCount(n: number): string {
  return COUNT.format(n);
}

/** `YYYY-MM-DD` → `dd/mm/yyyy`. Tách chuỗi, không qua `Date`, nên không lệch múi giờ. */
export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split("-");
  return `${day}/${month}/${year}`;
}

function lowSampleLead(n: number, minSample: number): string {
  return `Cỡ mẫu nhỏ (n = ${formatCount(n)} < ${formatCount(minSample)})`;
}

function toShareLine(row: CityShareRow, envelope: CitySharesEnvelope): ShareLine {
  const label = cityLabel(row.city);
  const value = row.share.value;
  const percent = formatPercent(value);
  const n = envelope.meta.cells[row.share.cell_id].n;
  const nText = formatCount(n);
  const lowSample = row.share.display === "low_sample_shown";
  const lowSampleNote = lowSample
    ? `${lowSampleLead(n, envelope.meta.thresholds.min_sample)}: số liệu chỉ để tham khảo`
    : null;
  const accessibleName =
    `${label}: ${percent}, ${nText} tin` + (lowSampleNote ? `. ${lowSampleNote}` : "");
  return { city: row.city, label, value, percent, n, nText, lowSample, lowSampleNote, accessibleName };
}

function toTableRow(row: CityShareRow, envelope: CitySharesEnvelope): TableRow {
  const line = toShareLine(row, envelope);
  const shareShown = row.share.display === "shown";
  return {
    city: line.city,
    label: line.label,
    share: shareShown ? line.percent : NOT_ENOUGH_DATA,
    shareShown,
    nText: line.nText,
    note: line.lowSample ? lowSampleLead(line.n, envelope.meta.thresholds.min_sample) : "",
  };
}

export function buildCitySharesView(envelope: CitySharesEnvelope): CitySharesView {
  const { data, meta } = envelope;
  const byCity = new Map(data.rows.map((row) => [row.city, row]));
  const pick = (cities: readonly string[]) =>
    cities.flatMap((city) => {
      const row = byCity.get(city);
      return row ? [row] : [];
    });

  const barRows = pick(BAR_CITIES);
  const legendRows = pick(LEGEND_CITIES);
  // Các tỉnh khác (#285) không thành thanh và không thành dòng chú thích: chỉ nằm trong bảng, giữa ba thành phố và ba
  // dòng chú thích, theo `n` của ô giảm dần (không tính gì thêm; hòa thì theo nhãn).
  const provinceRows = data.rows
    .filter((row) => !BAR_CITIES.includes(row.city) && !LEGEND_CITIES.includes(row.city))
    .map((row) => ({ row, n: meta.cells[row.share.cell_id].n, label: cityLabel(row.city) }))
    .sort((a, b) => b.n - a.n || a.label.localeCompare(b.label, "vi"))
    .map((item) => item.row);

  const bars = barRows.map((row) => toShareLine(row, envelope));
  const legend = legendRows.map((row) => toShareLine(row, envelope));
  const tableRows = [...barRows, ...provinceRows, ...legendRows].map((row) => toTableRow(row, envelope));

  const scope = `${roleLabel(data.role)} · ${levelLabel(data.level)}`;
  const unstatedNote =
    data.years_unstated_cell_id === null
      ? null
      : `${formatCount(meta.cells[data.years_unstated_cell_id].n)} tin của ${scope} ` +
        "không ghi số năm kinh nghiệm nên không được tính.";

  return {
    role: data.role,
    roleLabel: roleLabel(data.role),
    level: data.level,
    levelLabel: levelLabel(data.level),
    years: data.years,
    yearsLabel: yearsLabel(data.years),
    unstatedNote,
    bars,
    legend,
    table: {
      rows: tableRows,
      total: { label: "Tổng", share: "100%", nText: formatCount(meta.cells[data.total_cell_id].n) },
      roundingNote: ROUNDING_NOTE,
    },
    caption: {
      sources: meta.sources,
      snapshotDate: formatDate(meta.snapshot_date),
      notes: meta.coverage_notes,
      failedSources:
        meta.snapshot_status === "partial" && meta.sources_failed.length > 0
          ? FAILED_SOURCES_PREFIX + meta.sources_failed.join(", ")
          : null,
      filters: `${scope} · ${yearsLabel(data.years)}`,
    },
  };
}
