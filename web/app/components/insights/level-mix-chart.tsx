import type { MixRow } from "@/lib/market-overview-view";

import { levelColor } from "./overview/palette";

/**
 * Cơ cấu cấp bậc từng vai trò (#330): mỗi vai trò một thanh xếp chồng 100%, đoạn dài đúng tỷ lệ cấp API gửi
 * (`market-overview`), cùng thứ tự với danh sách người mới. Màu chỉ là phụ: chú thích ghi tên cấp, bảng có đủ số.
 */
export function LevelMixChart({ rows, levels }: { rows: MixRow[]; levels: { code: string; label: string }[] }) {
  return (
    <div className="flex flex-col gap-3">
      <ul aria-label="Chú thích cấp bậc" className="m-0 flex list-none flex-wrap gap-x-4 gap-y-1 p-0 text-footer text-text-muted">
        {levels.map((lv) => (
          <li key={lv.code} className="flex items-center gap-1.5">
            <span aria-hidden="true" className="h-2.5 w-2.5 rounded-sm" style={{ background: levelColor(lv.code) }} />
            {lv.label}
          </li>
        ))}
      </ul>
      <ol aria-label="Cơ cấu cấp bậc của từng vai trò" className="m-0 flex list-none flex-col gap-1.5 p-0">
        {rows.map((row) => (
          <li key={row.key} className="grid min-h-6 grid-cols-[minmax(0,8.5rem)_minmax(0,1fr)] items-center gap-3 sm:grid-cols-[minmax(0,11rem)_minmax(0,1fr)]">
            <span data-part="label" className="truncate text-caption text-text-secondary">
              {row.label}
            </span>
            {row.note ? (
              <span className="text-caption text-amber">{row.note}</span>
            ) : (
              <span className="flex h-3 w-full overflow-hidden rounded-sm bg-track">
                {row.segments.map((s) => (
                  <span
                    key={s.code}
                    data-part="segment"
                    title={`${s.label}: ${s.percent}`}
                    className="block h-full border-r-2 border-panel last:border-r-0"
                    style={{ width: `${(s.value * 100).toFixed(2)}%`, background: levelColor(s.code) }}
                  >
                    <span className="sr-only">
                      {s.label} {s.percent}
                    </span>
                  </span>
                ))}
              </span>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
