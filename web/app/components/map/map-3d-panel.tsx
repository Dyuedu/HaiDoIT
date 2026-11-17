"use client";

import { Component, type ReactNode, Suspense, lazy, useState } from "react";

import type { CitySharesView } from "@/lib/city-shares-view";
import { buildColumns } from "@/lib/map-3d-view";
import { OUTLINE } from "@/lib/vietnam-geo";

import { ShareLineButton } from "./share-line-button";

// three.js chỉ tải khi mở lối 3D: lối 2D và bảng không nặng thêm.
const Map3D = lazy(() => import("./map-3d"));

/** Chặn lỗi trong canvas (không tạo được context, lỗi tải gói) để màn chuyển 2D thay vì hiện màn hình lỗi (FR-36). */
class Map3DBoundary extends Component<{ onFail: () => void; children: ReactNode }, { failed: boolean }> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch() {
    this.props.onFail();
  }

  render() {
    return this.state.failed ? null : this.props.children;
  }
}

interface Map3DPanelProps {
  view: CitySharesView;
  /** Lối 3D không chạy được: màn chuyển sang 2D. */
  onFail: () => void;
}

/**
 * Lối 3D của màn Bản đồ (#314): khung canvas, nút chọn từng cột (bàn phím và trình đọc màn hình), khung thông tin của cột
 * đang chọn, và chú thích các phần không thành cột như lối 2D. Cột dựng từ `view.bars`, cùng số với lối 2D và bảng.
 */
export function Map3DPanel({ view, onFail }: Map3DPanelProps) {
  const columns = buildColumns(view.bars);
  const [selected, setSelected] = useState<string | null>(null);
  const active = columns.find((column) => column.city === selected) ?? null;

  return (
    <figure aria-label="Bản đồ 3D tỷ trọng tin theo thành phố" className="m-0 rounded-xl border border-border bg-panel p-panel">
      <figcaption className="font-mono text-kicker uppercase text-text-muted">
        Tỷ trọng tin theo thành phố · {view.roleLabel} · {view.levelLabel} · {view.yearsLabel}
      </figcaption>
      <div className="relative mt-3 h-[420px] overflow-hidden rounded-lg bg-inset sm:h-[520px]">
        <Map3DBoundary onFail={onFail}>
          <Suspense
            fallback={<p className="m-0 p-4 text-body-md text-text-muted">Đang tải bản đồ 3D…</p>}
          >
            <Map3D columns={columns} selected={selected} onSelect={setSelected} onContextLost={onFail} />
          </Suspense>
        </Map3DBoundary>
        <p className="pointer-events-none absolute bottom-2 left-3 m-0 text-caption text-text-muted">
          Kéo để xoay và nghiêng bản đồ.
        </p>
      </div>
      <div role="group" aria-label="Chọn cột" className="mt-3 flex flex-wrap gap-2">
        {columns.map((column) => (
          <button
            key={column.city}
            type="button"
            aria-pressed={selected === column.city}
            onClick={() => setSelected(column.city)}
            className={`min-h-target rounded-md border px-3 text-ui transition-colors hover:border-selected hover:text-text aria-pressed:border-selected aria-pressed:text-text ${
              column.faded ? "border-dashed border-amber-deep text-text-secondary" : "border-border-chip text-text-secondary"
            }`}
          >
            {column.label}
          </button>
        ))}
      </div>
      <p role="status" className="mt-2 mb-0 min-h-[1.5em] text-body-md text-text">
        {active ? active.info : ""}
      </p>
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
      <p className="mt-3 mb-0 text-caption text-text-muted">
        Viền đất liền: {OUTLINE.attribution}. Quần đảo Hoàng Sa và Trường Sa vẽ theo các đảo đại diện.
      </p>
    </figure>
  );
}
