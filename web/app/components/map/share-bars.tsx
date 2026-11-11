import type { CitySharesView } from "@/lib/city-shares-view";

import { ShareLineButton } from "./share-line-button";

/**
 * Lối Biểu đồ 2D: ba thanh Hà Nội, TP.HCM, Đà Nẵng, rộng đúng `share.value × 100%` của rãnh,
 * rồi chú thích Khác và không xác định, mỗi phần một dòng.
 */
export function ShareBars({ view }: { view: CitySharesView }) {
  return (
    <figure className="m-0 rounded-xl border border-border bg-panel p-panel">
      <figcaption className="font-mono text-kicker uppercase text-text-muted">
        Tỷ trọng tin theo thành phố · {view.roleLabel} · {view.levelLabel}
      </figcaption>
      <ul className="mt-4 flex list-none flex-col gap-1 p-0">
        {view.bars.map((line) => (
          <li key={`${view.role}.${line.city}`}>
            <ShareLineButton line={line} withTrack />
          </li>
        ))}
      </ul>
      <ul
        aria-label="Chú thích"
        className="mt-4 flex list-none flex-col gap-1 border-t border-border p-0 pt-3"
      >
        {view.legend.map((line) => (
          <li key={`${view.role}.${line.city}`}>
            <ShareLineButton line={line} />
          </li>
        ))}
      </ul>
    </figure>
  );
}
