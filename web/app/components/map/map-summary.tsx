"use client";

import { useId, useState } from "react";

import type { CitySharesView, ShareLine } from "@/lib/city-shares-view";

/**
 * Panel bên phải của màn Bản đồ (#316, prototype màn 01): "Tin <vai trò> nằm ở đâu" với ba nơi có cột (tỷ trọng lớn,
 * "n / tổng tin · ngày"), rồi các phần không thành cột (Làm từ xa, Nước ngoài, Không xác định). Tỷ trọng của nơi mẫu nhỏ
 * nằm sau nút "Trỏ hoặc chạm để xem %" (DESIGN.md `map-column`); tên đọc được của nút luôn có tỷ trọng. Có ở cả ba lối.
 */
export function MapSummary({ view }: { view: CitySharesView }) {
  const headingId = useId();
  const total = view.table.total.nText;
  return (
    <section aria-labelledby={headingId} className="flex flex-col gap-3 rounded-xl border border-border bg-panel p-panel">
      <h2 id={headingId} className="m-0 font-mono text-kicker uppercase text-text-muted">
        Tin {view.roleLabel} nằm ở đâu
      </h2>
      {view.bars.map((line) => (
        <Place key={`${view.role}.${line.city}`} line={line} total={total} date={view.caption.snapshotDate} />
      ))}
      <ul className="m-0 flex list-none flex-col gap-1 p-0">
        {view.legend.map((line) => (
          <li
            key={`${view.role}.${line.city}`}
            className="flex justify-between gap-3 text-caption leading-normal text-text-muted"
          >
            <span>{line.label}</span>
            <span className="whitespace-nowrap font-mono">
              {line.percent} · {line.nText}/{total} tin
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function Place({ line, total, date }: { line: ShareLine; total: string; date: string }) {
  const [shown, setShown] = useState(false);
  return (
    <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-3 gap-y-1 border-b border-border-row py-2">
      <span className="text-[15px] font-semibold text-text">{line.label}</span>
      {line.lowSample ? (
        <button
          type="button"
          // Tên bắt đầu bằng "Tỷ trọng" để không trùng nút của thanh 2D ("Đà Nẵng: …"); vẫn đủ tỷ trọng và n.
          aria-label={`Tỷ trọng ${line.accessibleName}`}
          aria-pressed={shown}
          onClick={() => setShown((s) => !s)}
          className="group inline-flex min-h-target items-center justify-end whitespace-nowrap rounded-lg border border-dashed border-amber-deep px-2.5 font-mono text-[13px] font-semibold text-text hover:border-amber"
        >
          <span className={`${shown ? "inline" : "hidden"} text-[18px] group-hover:inline group-focus-visible:inline`}>
            {line.percent}
          </span>
          <span
            className={`${shown ? "hidden" : "inline"} font-sans text-[11px] font-medium text-text-muted group-hover:hidden group-focus-visible:hidden`}
          >
            Trỏ hoặc chạm để xem %
          </span>
        </button>
      ) : (
        <span className="text-right font-mono text-[18px] font-semibold text-text">{line.percent}</span>
      )}
      <span className="col-span-2 font-mono text-[11px] text-text-muted">
        {line.nText} / {total} tin · {date}
      </span>
      {line.lowSampleNote && (
        <span className="col-span-2 text-caption leading-snug text-amber">{line.lowSampleNote}</span>
      )}
    </div>
  );
}
