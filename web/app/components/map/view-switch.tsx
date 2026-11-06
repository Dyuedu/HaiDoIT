import { useId } from "react";

export type ViewMode = "2d" | "table";

interface ViewSwitchProps {
  value: ViewMode;
  onChange: (mode: ViewMode) => void;
}

const ITEM = "min-h-target rounded-segment px-3 font-mono text-mono-sm font-semibold transition-colors";
const ON = "bg-selected/[0.16] text-text shadow-[inset_0_0_0_1px_var(--color-selected)]";
const OFF = "text-text-quiet hover:text-text";

/**
 * Cụm "3D / Biểu đồ 2D / Bảng", có mặt ở mọi khổ màn hình. 3D chờ 1.17: dùng `aria-disabled`
 * (vẫn focus được để đọc chú thích), không dùng `disabled`, và bấm vào không đổi lối.
 */
export function ViewSwitch({ value, onChange }: ViewSwitchProps) {
  const noteId = useId();
  return (
    <div className="flex flex-col items-start gap-1 sm:items-end">
      <div
        role="group"
        aria-label="Lối xem"
        className="inline-flex gap-1 rounded-lg border border-border-strong bg-inset p-1"
      >
        <button
          type="button"
          aria-pressed={false}
          aria-disabled="true"
          aria-describedby={noteId}
          className={`${ITEM} cursor-not-allowed text-text-dim`}
        >
          3D
        </button>
        <button
          type="button"
          aria-pressed={value === "2d"}
          onClick={() => onChange("2d")}
          className={`${ITEM} ${value === "2d" ? ON : OFF}`}
        >
          Biểu đồ 2D
        </button>
        <button
          type="button"
          aria-pressed={value === "table"}
          onClick={() => onChange("table")}
          className={`${ITEM} ${value === "table" ? ON : OFF}`}
        >
          Bảng
        </button>
      </div>
      <p id={noteId} className="m-0 text-caption text-text-muted">
        Bản đồ 3D sắp có
      </p>
    </div>
  );
}
