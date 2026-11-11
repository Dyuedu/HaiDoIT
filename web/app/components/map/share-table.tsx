import type { CitySharesView } from "@/lib/city-shares-view";

const HEAD = "px-3 py-2 font-mono text-kicker font-semibold tracking-[0.06em] text-text-muted";
const CELL = "px-3 py-2";

/**
 * Lối Bảng: bản chữ của biểu đồ, cùng bộ số. Dòng không `shown` ghi "chưa đủ dữ liệu" nhưng vẫn
 * ghi `n`. Dòng tổng ghi cố định 100% và `n` của ô toàn quốc, không cộng các dòng.
 */
export function ShareTable({ view }: { view: CitySharesView }) {
  const { rows, total, roundingNote } = view.table;
  return (
    <div className="rounded-xl border border-border bg-panel p-panel">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-ui">
          <caption className="sr-only">Tỷ trọng tin theo thành phố · {view.roleLabel} · {view.levelLabel}</caption>
          <thead>
            <tr className="border-b border-border-row">
              <th scope="col" className={`${HEAD} text-left`}>
                Nơi
              </th>
              <th scope="col" className={`${HEAD} text-right`}>
                Tỷ trọng
              </th>
              <th scope="col" className={`${HEAD} text-right`}>
                Số tin
              </th>
              <th scope="col" className={`${HEAD} text-left`}>
                Ghi chú
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.city} className="border-b border-border-row">
                <th scope="row" className={`${CELL} text-left font-medium`}>
                  {row.label}
                </th>
                <td
                  className={`${CELL} text-right ${
                    row.shareShown ? "font-mono text-mono text-text" : "text-amber"
                  }`}
                >
                  {row.share}
                </td>
                <td className={`${CELL} text-right font-mono text-mono`}>{row.nText}</td>
                <td className={`${CELL} text-caption text-amber`}>{row.note}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <th scope="row" className={`${CELL} text-left font-semibold`}>
                {total.label}
              </th>
              <td className={`${CELL} text-right font-mono text-mono`}>{total.share}</td>
              <td className={`${CELL} text-right font-mono text-mono`}>{total.nText}</td>
              <td className={CELL} />
            </tr>
          </tfoot>
        </table>
      </div>
      <p className="mt-3 text-caption text-text-muted">{roundingNote}</p>
    </div>
  );
}
