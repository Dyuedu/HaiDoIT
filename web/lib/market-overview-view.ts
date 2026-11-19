/**
 * Phần toàn cảnh của Insights (#329): envelope `market-overview` → chữ và số mà các biểu đồ in.
 *
 * Không tính số mới (AD-22): tỷ trọng, tỷ lệ và thứ hạng lấy nguyên từ API; số tin tra ở `meta.cells`. Độ dài thanh và
 * chiều cao cột là tỷ lệ vẽ so với phần lớn nhất của chính biểu đồ đó, không phải con số in ra. Câu tóm tắt chỉ gọi tên
 * theo thứ hạng máy chủ gửi, không chứa số (DEC-6, #132).
 */

import type { Stat } from "./city-shares";
import {
  type SnapshotCaption,
  NOT_ENOUGH_DATA,
  filtersText,
  formatCount,
  formatDate,
  formatPercent,
  snapshotCaption,
} from "./city-shares-view";
import { cityLabel, levelLabel, roleLabel } from "./labels";
import type { MarketOverviewEnvelope, OverviewRole, OverviewShare } from "./market-overview";
import { skillProfileHref } from "./newcomer-roles-view";

/** Mã giả của biểu đồ vai trò khi chưa chọn cấp nào. */
export const ALL_LEVELS_KEY = "all";
const OTHER_ROLE = "other";
const BIG_CITIES = ["ha_noi", "ho_chi_minh"] as const;

export interface Kpi {
  value: string;
  label: string;
  detail: string;
}

export interface Slice {
  code: string;
  label: string;
  /** `share.value` của cấp, dùng làm góc của miếng; `null` khi API ẩn số. */
  value: number | null;
  countText: string;
  percent: string;
}

export interface BarRow {
  key: string;
  label: string;
  href: string;
  countText: string;
  /** "12,3% tin IT" hay "12,3% tin của vai trò"; câu thiếu mẫu khi API ẩn tỷ lệ. */
  shareText: string;
  /** Độ dài vẽ 0–1 so với thanh dài nhất của biểu đồ. */
  length: number;
  dim: boolean;
  note: string | null;
}

export interface ColumnRow {
  key: string;
  label: string;
  countText: string;
  percent: string;
  /** Chiều cao vẽ 0–1 so với cột cao nhất. */
  height: number;
  dim: boolean;
  note: string | null;
}

export interface ButterflyRow {
  key: string;
  label: string;
  hn: { value: number; percent: string; countText: string; dim: boolean };
  hcm: { value: number; percent: string; countText: string; dim: boolean };
  totalText: string;
}

export interface OverviewView {
  kpis: Kpi[];
  takeaways: string[];
  slices: Slice[];
  totalText: string;
  /** Biểu đồ vai trò theo từng cấp, khóa là mã cấp hoặc `ALL_LEVELS_KEY`. */
  roleBars: Record<string, BarRow[]>;
  years: ColumnRow[];
  places: ColumnRow[];
  butterfly: ButterflyRow[];
  caption: SnapshotCaption;
}

/** Nhãn mốc số năm: `0`, `1`, `4-5`, `over_5`, `none`. */
export function yearsBucketLabel(code: string): string {
  if (code === "0") return "Không cần kinh nghiệm";
  if (code === "none") return "Không ghi";
  const over = /^over_(\d+)$/.exec(code);
  if (over) return `Trên ${over[1]} năm`;
  const range = /^(\d+)-(\d+)$/.exec(code);
  if (range) return `${range[1]}–${range[2]} năm`;
  return `${code} năm`;
}

/** Nhãn nơi làm việc của toàn cảnh; `other_provinces` là các tỉnh còn lại gộp. */
export function placeLabel(code: string): string {
  return code === "other_provinces" ? "Tỉnh khác" : cityLabel(code);
}

function lowSampleNote(n: number, minSample: number): string {
  return n === 0 ? "Chưa có tin nào" : `Mới có ${formatCount(n)} tin, chưa đủ ${formatCount(minSample)}`;
}

function percentOf(stat: Stat): string {
  return stat.value === null ? NOT_ENOUGH_DATA : formatPercent(stat.value);
}

function byLength<T extends { count: number }>(rows: T[]): (T & { length: number })[] {
  const top = rows.reduce((max, row) => (row.count > max ? row.count : max), 0);
  return rows.map((row) => ({ ...row, length: top > 0 ? row.count / top : 0 }));
}

function joinNames(names: string[]): string {
  if (names.length <= 1) return names.join("");
  return `${names.slice(0, -1).join(", ")} và ${names[names.length - 1]}`;
}

export function buildMarketOverviewView(envelope: MarketOverviewEnvelope): OverviewView {
  const { data, meta } = envelope;
  const min = meta.thresholds.min_sample;
  const cellN = (id: string) => meta.cells[id].n;
  const total = cellN(data.total_cell_id);
  const totalText = formatCount(total);
  const date = formatDate(meta.snapshot_date);
  const unstated = data.years.find((y) => y.code === "none");

  const kpis: Kpi[] = [
    { value: totalText, label: "tin IT đang mở", detail: `cập nhật ${date}` },
    {
      value: percentOf(data.entry_share),
      label: "tin dành cho Intern, Fresher, Junior",
      detail: `${formatCount(cellN(data.entry_cell_id))} trên ${totalText} tin`,
    },
    {
      value: percentOf(data.big_cities_share),
      label: "tin ở Hà Nội hoặc TP.HCM",
      detail: `${formatCount(cellN(data.big_cities_share.cell_id))} trên ${totalText} tin`,
    },
    ...(unstated
      ? [
          {
            value: percentOf(unstated.share),
            label: "tin không ghi số năm kinh nghiệm",
            detail: `${formatCount(cellN(unstated.share.cell_id))} trên ${totalText} tin`,
          },
        ]
      : []),
  ];

  const mix = meta.cells[data.total_cell_id].seniority_mix;
  const slices: Slice[] = data.level_mix.map((row) => ({
    code: row.code,
    label: levelLabel(row.code),
    value: row.share.value,
    countText: formatCount(mix[row.code] ?? 0),
    percent: percentOf(row.share),
  }));

  const roleByCode = new Map(data.roles.map((r) => [r.role, r]));
  const roleBars: Record<string, BarRow[]> = {};
  roleBars[ALL_LEVELS_KEY] = byLength(
    data.roles.map((r) => ({ role: r, count: cellN(r.cell_id), stat: r.share, suffix: "tin IT" })),
  ).map((row) => barRow(row, min));
  for (const ranking of data.roles_by_level) {
    const level = ranking.level;
    roleBars[level] = byLength(
      ranking.roles.map((code) => {
        const role = roleByCode.get(code) as OverviewRole;
        const stat = role.level_mix.find((s) => s.code === level)?.share as Stat;
        return { role, count: meta.cells[role.cell_id].seniority_mix[level] ?? 0, stat, suffix: "tin của vai trò" };
      }),
    ).map((row) => barRow(row, min));
  }

  const columns = (rows: OverviewShare[], label: (code: string) => string): ColumnRow[] => {
    const counted = rows.map((row) => ({ row, count: cellN(row.share.cell_id) }));
    const top = counted.reduce((max, c) => (c.count > max ? c.count : max), 0);
    return counted.map(({ row, count }) => ({
      key: row.code,
      label: label(row.code),
      countText: formatCount(count),
      percent: percentOf(row.share),
      height: top > 0 ? count / top : 0,
      dim: row.share.display !== "shown",
      note: row.share.display === "low_sample_shown" ? lowSampleNote(count, min) : null,
    }));
  };

  const butterfly: ButterflyRow[] = data.roles
    .filter((r) => r.role !== OTHER_ROLE && r.share.display === "shown")
    .map((r) => {
      const side = (city: string) => {
        const place = r.places.find((p) => p.code === city);
        const n = place ? cellN(place.share.cell_id) : 0;
        return {
          value: place?.share.value ?? 0,
          percent: place ? percentOf(place.share) : formatPercent(0),
          countText: formatCount(n),
          dim: place?.share.display !== "shown",
        };
      };
      return { key: r.role, label: roleLabel(r.role), hn: side("ha_noi"), hcm: side("ho_chi_minh"), totalText: formatCount(cellN(r.cell_id)) };
    });

  return {
    kpis,
    takeaways: takeaways(envelope),
    slices,
    totalText,
    roleBars,
    years: columns(data.years, yearsBucketLabel),
    places: columns(data.places, placeLabel),
    butterfly,
    caption: snapshotCaption(meta, filtersText(["Mọi vai trò", "mọi cấp bậc", "mọi số năm kinh nghiệm"])),
  };
}

function barRow(
  row: { role: OverviewRole; count: number; stat: Stat; suffix: string; length: number },
  min: number,
): BarRow {
  const { role, count, stat, suffix, length } = row;
  return {
    key: role.role,
    label: roleLabel(role.role),
    href: skillProfileHref(role.role),
    countText: formatCount(count),
    shareText: stat.value === null ? NOT_ENOUGH_DATA : `${formatPercent(stat.value)} ${suffix}`,
    length,
    dim: role.role === OTHER_ROLE || stat.display !== "shown",
    note: stat.display === "shown" ? null : lowSampleNote(count, min),
  };
}

/** Câu tóm tắt: chỉ gọi tên theo thứ hạng máy chủ gửi, không chứa số (DEC-6). */
function takeaways({ data }: MarketOverviewEnvelope): string[] {
  const lines: string[] = [];
  const sizes = data.levels_by_size;
  if (sizes.length >= 3) {
    lines.push(
      `Tin tuyển nhiều nhất ở cấp ${levelLabel(sizes[0])} và ${levelLabel(sizes[1])}; ` +
        `${levelLabel(sizes[sizes.length - 1])} là cấp ít tin nhất.`,
    );
  }
  const top = data.roles.filter((r) => r.role !== OTHER_ROLE).slice(0, 2);
  if (top.length === 2) lines.push(`${roleLabel(top[0].role)} và ${roleLabel(top[1].role)} là hai vai trò có nhiều tin nhất.`);
  const doors = data.roles_by_entry_share;
  if (doors.length >= 3) {
    lines.push(
      `${roleLabel(doors[0])} và ${roleLabel(doors[1])} là hai cửa rộng nhất cho người mới; ` +
        `${roleLabel(doors[doors.length - 1])} hẹp nhất.`,
    );
  }
  const place = (code: string) => data.places.find((p) => p.code === code)?.share.value ?? null;
  const [hn, hcm] = BIG_CITIES.map(place);
  if (hn !== null && hcm !== null && hn !== hcm) {
    const [more, less] = hn > hcm ? ["Hà Nội", "TP.HCM"] : ["TP.HCM", "Hà Nội"];
    const leaning = data.roles
      .filter((r) => r.role !== OTHER_ROLE && r.share.display === "shown")
      .filter((r) => {
        const [a, b] = BIG_CITIES.map((c) => r.places.find((p) => p.code === c)?.share.value ?? 0);
        return hn > hcm ? b > a : a > b;
      })
      .slice(0, 3)
      .map((r) => roleLabel(r.role));
    lines.push(`${more} có nhiều tin IT hơn ${less}${leaning.length ? `, nhưng ${less} dẫn ở ${joinNames(leaning)}` : ""}.`);
  }
  return lines;
}

