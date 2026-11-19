/**
 * Hàm thuần: envelope `city-shares` → những gì màn Bản đồ hiện (thanh, chú thích, bảng, chú
 * thích snapshot).
 *
 * Không tự tính số nào. Chỉ đọc `share.value`, `share.display`, `meta.cells[cell_id].n`,
 * `meta.thresholds.min_sample` và `n` của `data.total_cell_id`; không cộng, không chia, không so
 * `n` với ngưỡng. Làm tròn đúng một lần, ở `formatPercent`.
 */

import type { CityShareRow, CitySharesEnvelope, CoverageNote, Meta } from "./city-shares";
import { BAR_CITIES, cityLabel, LEGEND_CITIES, levelLabel, roleLabel, yearsLabel } from "./labels";
import { sourcesText } from "./source-labels";

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
  /** Bộ lọc đang dùng (#280, #324): "Mọi vai trò, mới vào nghề, mọi số năm kinh nghiệm". */
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
  /** Tiêu đề khung bản đồ (#324): "521 tin Backend · mọi cấp bậc, mọi số năm kinh nghiệm". */
  title: string;
  unstatedNote: string | null;
  bars: ShareLine[];
  legend: ShareLine[];
  table: { rows: TableRow[]; total: TableTotal; roundingNote: string };
  caption: SnapshotCaption;
}

export const NOT_ENOUGH_DATA = "chưa đủ dữ liệu";
export const ROUNDING_NOTE = "Tổng các dòng có thể lệch 0,1% do làm tròn.";
/** Câu cho nhóm không có tin nào (#324), thay cho "Mới có 0 tin…". */
export const NO_POSTINGS = "Chưa có tin nào";

/** Câu của snapshot `partial` (#324): tên nguồn viết như trang đó viết. */
export function failedSourcesText(codes: readonly string[]): string {
  return `Lần cập nhật này chưa lấy đủ tin từ ${sourcesText(codes)}`;
}

/** Dòng dưới ngưỡng trong danh sách (#324): "Mới có 12 tin, cần ít nhất 30"; 0 tin thì "Chưa có tin nào". */
export function notEnoughText(n: number, minSample: number): string {
  return n === 0 ? NO_POSTINGS : `Mới có ${formatCount(n)} tin, cần ít nhất ${formatCount(minSample)}`;
}

function lowerFirst(text: string): string {
  return text.charAt(0).toLocaleLowerCase("vi") + text.slice(1);
}

/** Các phần của bộ lọc thành một câu (#324): "Mọi vai trò, mới vào nghề, mọi số năm kinh nghiệm". */
export function filtersText(parts: readonly string[]): string {
  return parts.map((part, i) => (i === 0 ? part : lowerFirst(part))).join(", ");
}

/** Vai trò trong câu bộ lọc: "Tất cả" đọc thành "Mọi vai trò". */
export function roleFilterLabel(role: string): string {
  return role === "all" ? "Mọi vai trò" : roleLabel(role);
}

/** Số năm trong câu bộ lọc: "Mọi số năm" của ô chọn đọc đủ thành "Mọi số năm kinh nghiệm". */
export function yearsFilterLabel(years: string): string {
  return years === "any" ? ANY_YEARS_TEXT : yearsLabel(years);
}

export const ANY_YEARS_TEXT = "Mọi số năm kinh nghiệm";

/** Caption chung của mọi màn (#324): nguồn để nguyên mã, khung chú thích đổi ra tên khi in. */
export function snapshotCaption(meta: Meta, filters: string): SnapshotCaption {
  return {
    sources: meta.sources,
    snapshotDate: formatDate(meta.snapshot_date),
    notes: meta.coverage_notes,
    failedSources:
      meta.snapshot_status === "partial" && meta.sources_failed.length > 0
        ? failedSourcesText(meta.sources_failed)
        : null,
    filters,
  };
}

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

/** Ghi chú mẫu nhỏ trong bảng (#324): "Mới có 21 tin, chưa đủ 30"; 0 tin thì "Chưa có tin nào". */
function lowSampleLead(n: number, minSample: number): string {
  return n === 0 ? NO_POSTINGS : `Mới có ${formatCount(n)} tin, chưa đủ ${formatCount(minSample)}`;
}

function toShareLine(row: CityShareRow, envelope: CitySharesEnvelope): ShareLine {
  const label = cityLabel(row.city);
  const value = row.share.value;
  const percent = formatPercent(value);
  const n = envelope.meta.cells[row.share.cell_id].n;
  const nText = formatCount(n);
  const lowSample = row.share.display === "low_sample_shown";
  const lowSampleNote = lowSample
    ? n === 0
      ? NO_POSTINGS
      : `${lowSampleLead(n, envelope.meta.thresholds.min_sample)} để so sánh chắc chắn`
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

  const scope = [roleFilterLabel(data.role), levelLabel(data.level)];
  const unstatedNote =
    data.years_unstated_cell_id === null
      ? null
      : `${formatCount(meta.cells[data.years_unstated_cell_id].n)} tin không ghi số năm kinh nghiệm ` +
        `nên không được tính (${lowerFirst(filtersText(scope))}).`;
  const totalText = formatCount(meta.cells[data.total_cell_id].n);
  const subject = data.role === "all" ? "IT" : roleLabel(data.role);

  return {
    role: data.role,
    roleLabel: roleLabel(data.role),
    level: data.level,
    levelLabel: levelLabel(data.level),
    years: data.years,
    yearsLabel: yearsLabel(data.years),
    title: `${totalText} tin ${subject} · ${lowerFirst(filtersText([levelLabel(data.level), yearsFilterLabel(data.years)]))}`,
    unstatedNote,
    bars,
    legend,
    table: {
      rows: tableRows,
      total: { label: "Tổng", share: "100%", nText: totalText },
      roundingNote: ROUNDING_NOTE,
    },
    caption: snapshotCaption(meta, filtersText([...scope, yearsFilterLabel(data.years)])),
  };
}
