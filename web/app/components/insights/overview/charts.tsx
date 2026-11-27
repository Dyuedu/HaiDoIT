import Link from "next/link";

import type { BarRow, ButterflyRow, ColumnRow } from "@/lib/market-overview-view";

import { PLACE_COLORS } from "./palette";

/**
 * Biểu đồ của phần toàn cảnh (#329) vẽ bằng HTML: thanh ngang, cột, hai phía. Độ dài và chiều cao là tỷ lệ vẽ view đã
 * tính sẵn; chữ số in ra đúng như view gửi. Mỗi biểu đồ đi cùng một `DataTable` có đủ số.
 */

interface BarChartProps {
  rows: BarRow[];
  label: string;
  color?: string;
}

/** Thanh ngang, mỗi dòng là liên kết sang hồ sơ kỹ năng của vai trò. Dòng ít tin mờ đi và ghi rõ số tin. */
export function BarChart({ rows, label, color = "var(--color-primary)" }: BarChartProps) {
  return (
    <ol aria-label={label} className="m-0 flex list-none flex-col gap-1 p-0">
      {rows.map((row) => (
        <li key={row.key} className={row.dim ? "opacity-55" : undefined}>
          <Link
            href={row.href}
            className="grid min-h-target grid-cols-[minmax(0,8.5rem)_minmax(0,1fr)_auto] items-center gap-3 rounded-lg px-2 hover:bg-track focus-visible:outline-2 focus-visible:outline-selected sm:grid-cols-[minmax(0,11rem)_minmax(0,1fr)_auto]"
          >
            <span className="truncate text-caption text-text-secondary">{row.label}</span>
            <span aria-hidden="true" className="h-2.5 rounded-sm bg-track">
              <span
                className="block h-full rounded-sm"
                style={{ width: `${(row.length * 100).toFixed(2)}%`, background: color }}
              />
            </span>
            <span className="text-right font-mono text-caption text-text">
              {row.countText}
              <span className="sr-only">
                {" "}
                tin, {row.shareText}
                {row.note ? `. ${row.note}` : ""}
              </span>
            </span>
          </Link>
        </li>
      ))}
    </ol>
  );
}

/** Cột đứng; số tin trên đầu cột, nhãn dưới chân. */
export function ColumnChart({ rows, label, colorOf }: { rows: ColumnRow[]; label: string; colorOf: (key: string) => string }) {
  return (
    <ol aria-label={label} className="m-0 flex h-56 list-none items-end gap-1.5 p-0 sm:gap-3">
      {rows.map((row) => (
        <li key={row.key} className={`flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-1 ${row.dim ? "opacity-55" : ""}`}>
          <span className="font-mono text-footer text-text">{row.countText}</span>
          <span
            aria-hidden="true"
            className="w-3/4 rounded-t ring-1 ring-inset ring-border/40"
            style={{ height: `${Math.max(row.height * 70, row.height > 0 ? 1 : 0).toFixed(2)}%`, background: colorOf(row.key) }}
          />
          <span className="min-h-8 text-center text-footer leading-tight text-text-secondary">
            {row.label}
            <span className="sr-only">: {row.percent}{row.note ? `. ${row.note}` : ""}</span>
          </span>
        </li>
      ))}
    </ol>
  );
}

/** Hai phía: Hà Nội bên trái, TP.HCM bên phải, tên vai trò ở giữa. */
export function ButterflyChart({ rows }: { rows: ButterflyRow[] }) {
  return (
    <div className="flex flex-col gap-1">
      <div aria-hidden="true" className="grid grid-cols-[minmax(0,1fr)_7rem_minmax(0,1fr)] font-mono text-footer text-text-muted sm:grid-cols-[minmax(0,1fr)_10rem_minmax(0,1fr)]">
        <span className="text-right">← HÀ NỘI</span>
        <span />
        <span>TP.HCM →</span>
      </div>
      <ol aria-label="Phần trăm tin của mỗi vai trò ở Hà Nội và TP.HCM" className="m-0 flex list-none flex-col gap-1 p-0">
        {rows.map((row) => (
          <li
            key={row.key}
            className="grid min-h-8 grid-cols-[minmax(0,1fr)_7rem_minmax(0,1fr)] items-center sm:grid-cols-[minmax(0,1fr)_10rem_minmax(0,1fr)]"
          >
            <span className="flex items-center justify-end gap-2">
              <span className="font-mono text-footer text-text">{row.hn.percent}</span>
              <span aria-hidden="true" className={`h-3 rounded-sm ${row.hn.dim ? "opacity-55" : ""}`} style={{ width: `${(row.hn.value * 80).toFixed(2)}%`, background: PLACE_COLORS.hn }} />
            </span>
            <span className="truncate px-2 text-center text-caption text-text-secondary">
              {row.label}
              <span className="sr-only">
                : Hà Nội {row.hn.percent}, TP.HCM {row.hcm.percent}, trên {row.totalText} tin
              </span>
            </span>
            <span className="flex items-center gap-2">
              <span aria-hidden="true" className={`h-3 rounded-sm ${row.hcm.dim ? "opacity-55" : ""}`} style={{ width: `${(row.hcm.value * 80).toFixed(2)}%`, background: PLACE_COLORS.hcm }} />
              <span className="font-mono text-footer text-text">{row.hcm.percent}</span>
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}

/** Bảng số của một biểu đồ, gập lại sẵn. Cột số canh phải. */
export function DataTable({ caption, head, rows, numeric }: { caption: string; head: string[]; rows: string[][]; numeric: number[] }) {
  return (
    <details className="text-caption">
      <summary className="cursor-pointer font-mono text-footer text-text-muted focus-visible:outline-2 focus-visible:outline-selected">
        Xem bảng số
      </summary>
      <div className="mt-2 max-h-80 overflow-auto">
        <table className="w-full border-collapse">
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr>
              {head.map((h, i) => (
                <th key={h} scope="col" className={`border-b border-border px-2 py-1 font-medium text-text-muted ${numeric.includes(i) ? "text-right" : "text-left"}`}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.join("|")}>
                {row.map((cell, i) =>
                  i === 0 ? (
                    <th key={i} scope="row" className="border-b border-border px-2 py-1 text-left font-normal text-text-secondary">
                      {cell}
                    </th>
                  ) : (
                    <td key={i} className={`border-b border-border px-2 py-1 text-text ${numeric.includes(i) ? "text-right font-mono" : ""}`}>
                      {cell}
                    </td>
                  ),
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}
