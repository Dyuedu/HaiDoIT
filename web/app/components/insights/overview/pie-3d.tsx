"use client";

import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";

import type { Slice } from "@/lib/market-overview-view";
import { getServerThemeSnapshot, getThemeSnapshot, subscribeTheme } from "@/lib/theme-store";

import { levelColor } from "./palette";

const TILT = 0.56;
const STEP = Math.PI / 6;

interface Pie3DProps {
  slices: Slice[];
  /** Mã cấp đang chọn, hoặc `null`. */
  selected: string | null;
  onSelect: (code: string | null) => void;
  /** Tên của nhóm nút chú thích, đọc bằng trình đọc màn hình. */
  label: string;
}

interface Arc {
  slice: Slice;
  a0: number;
  a1: number;
  mid: number;
}

function shade(hex: string, factor: number): string {
  const n = Number.parseInt(hex.slice(1), 16);
  const channel = (shift: number) => Math.round(((n >> shift) & 255) * factor);
  return `rgb(${channel(16)},${channel(8)},${channel(0)})`;
}

function isLight(hex: string): boolean {
  const n = Number.parseInt(hex.slice(1), 16);
  return (0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255 > 0.55;
}

/**
 * Biểu đồ tròn 3D vẽ bằng canvas (#329). Góc mỗi miếng là `share.value` API gửi; miếng nào API ẩn số thì không vẽ.
 * Kéo ngang để xoay, hai nút xoay cho bàn phím. Canvas chỉ để nhìn (`aria-hidden`): mỗi miếng có một nút chú thích
 * cùng chọn, và bảng số nằm ngay dưới biểu đồ. Độ nghiêng làm miếng phía trước trông lớn hơn, nên phần trăm ghi trên
 * miếng và trong chú thích.
 */
export function Pie3D({ slices, selected, onSelect, label }: Pie3DProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [rotation, setRotation] = useState(-Math.PI / 2 - 0.35);
  const [hover, setHover] = useState<string | null>(null);
  const drag = useRef<{ x: number; start: number; moved: boolean } | null>(null);
  const [width, setWidth] = useState(320);
  const theme = useSyncExternalStore(subscribeTheme, getThemeSnapshot, getServerThemeSnapshot);

  const drawable = slices.filter((s) => s.value !== null && s.value > 0);
  const sum = drawable.reduce((acc, s) => acc + (s.value as number), 0);

  const arcs = useCallback((): Arc[] => {
    let angle = rotation;
    return drawable.map((slice) => {
      const a0 = angle;
      angle += ((slice.value as number) / (sum || 1)) * Math.PI * 2;
      return { slice, a0, a1: angle, mid: (a0 + angle) / 2 };
    });
  }, [drawable, rotation, sum]);

  const geometry = useCallback(() => {
    const height = Math.round(width * 0.66);
    const rx = Math.min(width * 0.44, (height * 0.78) / (TILT * 2 + 0.2));
    return { height, cx: width / 2, cy: height * 0.42, rx, ry: rx * TILT, depth: rx * 0.17, lift: rx * 0.1 };
  }, [width]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(() => setWidth(canvas.clientWidth || 320));
    observer.observe(canvas);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    let ctx: CanvasRenderingContext2D | null = null;
    try {
      ctx = canvas?.getContext("2d") ?? null;
    } catch {
      ctx = null;
    }
    if (!canvas || !ctx) return;
    const g = geometry();
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(g.height * ratio);
    canvas.style.height = `${g.height}px`;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, g.height);
    const offset = (arc: Arc) => {
      const k = arc.slice.code === selected ? 1 : arc.slice.code === hover ? 0.55 : 0;
      return { x: Math.cos(arc.mid) * g.lift * k, y: Math.sin(arc.mid) * g.lift * TILT * k };
    };
    const sector = (c: CanvasRenderingContext2D, x: number, y: number, a0: number, a1: number) => {
      c.beginPath();
      c.moveTo(x, y);
      c.ellipse(x, y, g.rx, g.ry, 0, a0, a1);
      c.closePath();
    };
    // Miếng phía sau vẽ trước để miếng phía trước che lên đúng chỗ.
    const ordered = arcs().sort((p, q) => Math.sin(p.mid) - Math.sin(q.mid));
    const panelStroke =
      (typeof getComputedStyle === "function"
        ? getComputedStyle(canvas).getPropertyValue("--color-panel").trim()
        : "") || (theme === "light" ? "#ffffff" : "#0d141c");
    for (const arc of ordered) {
      const { x, y } = offset(arc);
      const cx = g.cx + x;
      const cy = g.cy + y;
      const color = levelColor(arc.slice.code);
      ctx.globalAlpha = selected && arc.slice.code !== selected ? 0.42 : 1;
      for (let d = g.depth; d >= 1; d -= 1) {
        ctx.fillStyle = shade(color, 0.42 + 0.18 * (1 - d / g.depth));
        sector(ctx, cx, cy + d, arc.a0, arc.a1);
        ctx.fill();
      }
      ctx.fillStyle = color;
      sector(ctx, cx, cy, arc.a0, arc.a1);
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = panelStroke;
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
    for (const arc of ordered) {
      if ((arc.slice.value as number) / (sum || 1) < 0.07) continue;
      const { x, y } = offset(arc);
      const color = levelColor(arc.slice.code);
      ctx.font = `600 ${Math.max(11, Math.round(g.rx * 0.11))}px var(--font-jetbrains-mono), monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = isLight(color) ? "#08131a" : "#f2f7fa";
      ctx.fillText(arc.slice.percent, g.cx + x + Math.cos(arc.mid) * g.rx * 0.62, g.cy + y + Math.sin(arc.mid) * g.ry * 0.62);
    }
  }, [arcs, geometry, hover, selected, sum, theme, width]);

  const hit = (event: React.PointerEvent<HTMLCanvasElement>): string | null => {
    const rect = event.currentTarget.getBoundingClientRect();
    const g = geometry();
    const px = event.clientX - rect.left;
    const py = event.clientY - rect.top;
    for (const arc of arcs().sort((p, q) => Math.sin(q.mid) - Math.sin(p.mid))) {
      const nx = (px - g.cx) / g.rx;
      const ny = (py - g.cy) / g.ry;
      if (nx * nx + ny * ny > 1) continue;
      let rel = (Math.atan2(ny, nx) - arc.a0) % (Math.PI * 2);
      if (rel < 0) rel += Math.PI * 2;
      if (rel <= arc.a1 - arc.a0) return arc.slice.code;
    }
    return null;
  };

  const choose = (code: string | null) => onSelect(code !== null && code === selected ? null : code);

  return (
    <div className="flex flex-col gap-3">
      <canvas
        ref={canvasRef}
        aria-hidden="true"
        data-testid="pie-3d"
        className="block w-full touch-pan-y cursor-grab"
        onPointerDown={(e) => {
          drag.current = { x: e.clientX, start: rotation, moved: false };
          e.currentTarget.setPointerCapture?.(e.pointerId);
        }}
        onPointerMove={(e) => {
          const d = drag.current;
          if (d) {
            const dx = e.clientX - d.x;
            if (Math.abs(dx) > 4) d.moved = true;
            if (d.moved) {
              setRotation(d.start + dx * 0.012);
              return;
            }
          }
          setHover(hit(e));
        }}
        onPointerUp={(e) => {
          if (drag.current && !drag.current.moved) choose(hit(e));
          drag.current = null;
        }}
        onPointerLeave={() => {
          if (!drag.current) setHover(null);
        }}
      />
      <div className="flex items-center justify-center gap-2">
        <button
          type="button"
          className="min-h-target rounded-lg border border-border-strong px-3 text-caption text-text-secondary hover:border-selected focus-visible:outline-2 focus-visible:outline-selected"
          onClick={() => setRotation((r) => r - STEP)}
        >
          Xoay trái
        </button>
        <button
          type="button"
          className="min-h-target rounded-lg border border-border-strong px-3 text-caption text-text-secondary hover:border-selected focus-visible:outline-2 focus-visible:outline-selected"
          onClick={() => setRotation((r) => r + STEP)}
        >
          Xoay phải
        </button>
      </div>
      <div role="group" aria-label={label} className="grid grid-cols-1 gap-1 sm:grid-cols-2">
        {slices.map((slice) => (
          <button
            key={slice.code}
            type="button"
            aria-pressed={selected === slice.code}
            onClick={() => choose(slice.code)}
            onMouseEnter={() => setHover(slice.code)}
            onMouseLeave={() => setHover(null)}
            onFocus={() => setHover(slice.code)}
            onBlur={() => setHover(null)}
            className="grid min-h-target grid-cols-[12px_minmax(0,1fr)_auto_auto] items-center gap-2 rounded-lg px-2 text-left text-caption text-text-secondary hover:bg-track aria-pressed:bg-track aria-pressed:text-text focus-visible:outline-2 focus-visible:outline-selected"
          >
            <span aria-hidden="true" className="h-3 w-3 rounded-sm" style={{ background: levelColor(slice.code) }} />
            <span>{slice.label}</span>
            <span className="font-mono text-text">{slice.countText}</span>
            <span className="min-w-12 text-right font-mono text-text-muted">{slice.percent}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
