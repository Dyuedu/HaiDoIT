"use client";

import { useEffect, useRef, useState } from "react";

import type { CitySharesView } from "@/lib/city-shares-view";
import { buildColumns } from "@/lib/map-3d-view";
import { ARCHIPELAGOS, OUTLINE, OUTLINE_PATH, STAGE, toStage } from "@/lib/vietnam-geo";

import css from "./map-3d.module.css";

/** Góc nhìn mặc định và giới hạn, như prototype màn 01 (#316). */
const TILT = 56;
const SPIN = -16;
const MAX_TILT = 72;
const STEP = 30;
const DRAG_START = 6;

/** Lớp nền của hình đất: độ sâu, màu nền, màu nét (prototype vẽ năm lớp để có bề dày). */
const LAYERS: { z: number; fill: string; stroke?: string; opacity?: number }[] = [
  { z: -36, fill: "var(--color-map-depth-0)", opacity: 0.85 },
  { z: -12, fill: "var(--color-map-depth-1)", stroke: "var(--color-map-depth-1-edge)" },
  { z: -8, fill: "var(--color-map-depth-2)", stroke: "var(--color-map-depth-2-edge)" },
  { z: -4, fill: "var(--color-map-depth-3)", stroke: "var(--color-map-depth-3-edge)" },
];

interface Drag {
  x: number;
  y: number;
  rx: number;
  rz: number;
  active: boolean;
  id: number;
  el: HTMLElement;
}

function RotateIcon({ dir }: { dir: "left" | "right" }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {dir === "left" ? (
        <>
          <path d="M3 12a9 9 0 1 0 3-6.7" />
          <path d="M3 4v5h5" />
        </>
      ) : (
        <>
          <path d="M21 12a9 9 0 1 1-3-6.7" />
          <path d="M21 4v5h-5" />
        </>
      )}
    </svg>
  );
}

const ICON_BUTTON =
  "inline-flex size-11 items-center justify-center rounded-lg border border-border-strong bg-inset p-0 text-text-secondary transition-colors hover:border-selected hover:text-text";

/**
 * Lối 3D của màn Bản đồ (#316), dựng bằng CSS 3D theo prototype màn 01: sân khấu 460×560 nghiêng `rotateX` và xoay
 * `rotateZ`, tấm lưới, hình Việt Nam (viền geoBoundaries) cùng Hoàng Sa, Trường Sa, ba cột vuông cao `share.value × 400` px,
 * mỗi cột một thẻ nhãn đứng thẳng. Ba nút xoay trái, xoay phải, đặt lại; kéo ngang để xoay, kéo dọc để nghiêng. Mở màn:
 * 250ms sau sân khấu nghiêng lên và cột mọc. Thẻ là nút DOM nên bàn phím và trình đọc màn hình dùng được.
 */
export function Map3D({ view }: { view: CitySharesView }) {
  const columns = buildColumns(view);
  const [rx, setRx] = useState(0);
  const [rz, setRz] = useState(SPIN);
  const [grown, setGrown] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const drag = useRef<Drag | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setRx(TILT);
      setGrown(true);
    }, 250);
    return () => clearTimeout(timer);
  }, []);

  const down = (event: React.PointerEvent<HTMLDivElement>) => {
    if (event.button !== undefined && event.button !== 0) return;
    drag.current = { x: event.clientX, y: event.clientY, rx, rz, active: false, id: event.pointerId, el: event.currentTarget };
  };
  const move = (event: React.PointerEvent<HTMLDivElement>) => {
    const d = drag.current;
    if (!d) return;
    const dx = event.clientX - d.x;
    const dy = event.clientY - d.y;
    if (!d.active) {
      if (Math.abs(dx) + Math.abs(dy) < DRAG_START) return;
      d.active = true;
      try {
        d.el.setPointerCapture(d.id);
      } catch {
        // jsdom và vài trình duyệt cũ không có pointer capture: vẫn kéo được trong khung.
      }
      setDragging(true);
    }
    setRz(d.rz + dx * 0.35);
    setRx(Math.max(0, Math.min(MAX_TILT, d.rx - dy * 0.3)));
  };
  const up = () => {
    const d = drag.current;
    drag.current = null;
    if (d?.active) setDragging(false);
  };

  const deg = (n: number) => `${Number(n.toFixed(1))}deg`;

  return (
    <section aria-label="Bản đồ 3D" className="m-0 flex flex-col gap-3 rounded-xl border border-border bg-panel p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="font-mono text-kicker uppercase text-text-muted">
          {view.title}
        </span>
        <div className="flex items-center gap-1.5">
          <button type="button" aria-label="Xoay trái 30 độ" className={ICON_BUTTON} onClick={() => setRz((z) => z - STEP)}>
            <RotateIcon dir="left" />
          </button>
          <button type="button" aria-label="Xoay phải 30 độ" className={ICON_BUTTON} onClick={() => setRz((z) => z + STEP)}>
            <RotateIcon dir="right" />
          </button>
          <button
            type="button"
            aria-label="Đặt lại góc nhìn"
            className={ICON_BUTTON}
            onClick={() => {
              setRx(TILT);
              setRz(SPIN);
            }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 2v4M12 18v4M2 12h4M18 12h4" />
            </svg>
          </button>
        </div>
      </div>

      <div
        role="group"
        aria-label="Bản đồ 3D. Kéo để xoay, kéo dọc để nghiêng. Chọn nhãn của một nơi để xem tỷ trọng."
        className={`${css.viewport} ${dragging ? css.dragging : ""}`}
        onPointerDown={down}
        onPointerMove={move}
        onPointerUp={up}
        onPointerCancel={up}
        onPointerLeave={up}
      >
        <div className={css.scaler}>
          <div
            data-testid="map-3d-stage"
            className={css.stage}
            style={{ transform: `translateY(40px) rotateX(${deg(rx)}) rotateZ(${deg(rz)})` }}
          >
            <div className={css.plate} />
            {LAYERS.map((layer) => (
              <svg
                key={layer.z}
                className={css.slab}
                viewBox={`0 0 ${STAGE.width} ${STAGE.height}`}
                style={{ transform: `translateZ(${layer.z}px)` }}
                aria-hidden="true"
              >
                <path d={OUTLINE_PATH} fill={layer.fill} stroke={layer.stroke} strokeWidth={1} opacity={layer.opacity} />
              </svg>
            ))}
            <svg data-testid="map-3d-land" className={css.slab} viewBox={`0 0 ${STAGE.width} ${STAGE.height}`} aria-hidden="true">
              <defs>
                <pattern id="bd-dots" width="7" height="7" patternUnits="userSpaceOnUse">
                  <circle cx="2" cy="2" r="1.1" fill="var(--color-selected)" opacity=".5" />
                </pattern>
              </defs>
              <path d={OUTLINE_PATH} fill="var(--color-map-land)" />
              <path d={OUTLINE_PATH} fill="url(#bd-dots)" />
              <path d={OUTLINE_PATH} fill="none" stroke="var(--color-selected)" strokeWidth={1.6} strokeLinejoin="round" />
              {ARCHIPELAGOS.map((group) => {
                const at = toStage(group.labelAt);
                return (
                  <g key={group.id}>
                    <g fill="var(--color-selected)" opacity=".85">
                      {group.islands.map((island) => {
                        const p = toStage(island);
                        return <circle key={island.name} cx={p.px} cy={p.py} r={2.2} />;
                      })}
                    </g>
                    <text x={at.px - 40} y={at.py - 6} fill="var(--color-text-muted)" fontSize={12} fontFamily="JetBrains Mono, monospace">
                      {group.shortLabel}
                    </text>
                  </g>
                );
              })}
            </svg>
            {columns.map((column) => {
              const h = grown ? column.height : 0;
              const opacity = column.faded ? 0.4 : 1;
              const isSelected = selected === column.city;
              return (
                <div
                  key={column.city}
                  data-testid={`map-3d-column-${column.city}`}
                  data-height={column.height}
                  data-faded={column.faded}
                  data-selected={isSelected}
                  className={css.col}
                  style={{ left: column.stage.px, top: column.stage.py }}
                >
                  <span className={css.glow} style={{ opacity }} />
                  <span
                    className={`${css.face} ${css.top}`}
                    style={{
                      transform: `translateZ(${h}px)`,
                      background: isSelected ? "var(--color-text)" : "var(--color-selected)",
                      opacity,
                    }}
                  />
                  <span className={`${css.face} ${css.front}`} style={{ height: h, opacity }} />
                  <span className={`${css.face} ${css.back}`} style={{ height: h, opacity }} />
                  <span className={`${css.face} ${css.left}`} style={{ width: h, opacity }} />
                  <span className={`${css.face} ${css.right}`} style={{ width: h, opacity }} />
                  <button
                    type="button"
                    aria-label={column.info}
                    aria-pressed={isSelected}
                    onClick={() => setSelected((s) => (s === column.city ? null : column.city))}
                    onPointerDown={(event) => event.stopPropagation()}
                    className={`${css.card} ${column.faded ? css.small : ""}`}
                    style={{
                      transform: `translateZ(${h + 12}px) rotateZ(${deg(-rz)}) rotateX(${deg(-rx)}) translate(-50%, -100%)`,
                    }}
                  >
                    <span className="text-[12px] font-semibold">{column.label}</span>
                    {column.faded ? (
                      <>
                        <span data-reveal className={`${css.reveal} font-mono text-[11px] text-selected`}>
                          {column.valueText}
                        </span>
                        <span className="max-w-[200px] whitespace-normal text-center font-mono text-[11px] leading-snug text-amber">
                          {column.smallLabel}
                        </span>
                      </>
                    ) : (
                      <span className="font-mono text-[11px] text-selected">{column.valueText}</span>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <span className="font-mono text-[11px] text-text-muted">
        Kéo để xoay · kéo dọc để nghiêng · cột mờ = cỡ mẫu nhỏ, trỏ hoặc chạm nhãn để xem tỷ trọng
      </span>
      <span className="text-caption text-text-muted">
        Viền đất liền: {OUTLINE.attribution}. Quần đảo Hoàng Sa và Trường Sa vẽ theo các đảo đại diện.
      </span>
    </section>
  );
}
