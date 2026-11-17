import { useId } from "react";

export type ViewMode = "3d" | "2d" | "table";

/** Câu đi kèm nút 3D khi trình duyệt không chạy được WebGL, hoặc lối 3D đã lỗi (FR-36). */
export const NO_3D_NOTE = "Trình duyệt này không chạy được bản đồ 3D, nên đang hiện biểu đồ 2D.";

interface ViewSwitchProps {
  value: ViewMode;
  onChange: (mode: ViewMode) => void;
  /** `false` khi không có WebGL hoặc lối 3D đã lỗi: nút 3D tắt và nói vì sao. */
  can3d: boolean;
}

const ITEM = "min-h-target rounded-segment px-3 font-mono text-mono-sm font-semibold transition-colors";
const ON = "bg-selected/[0.16] text-text shadow-[inset_0_0_0_1px_var(--color-selected)]";
const OFF = "text-text-quiet hover:text-text";

/**
 * Cụm "3D / Biểu đồ 2D / Bảng", có mặt ở mọi khổ màn hình, cùng một bộ số (UX-DR12). Khi không chạy được 3D (#314,
 * FR-36), nút 3D dùng `aria-disabled` (vẫn focus được để đọc câu giải thích), không dùng `disabled`, và bấm không đổi lối.
 */
export function ViewSwitch({ value, onChange, can3d }: ViewSwitchProps) {
  const noteId = useId();
  const options: { mode: ViewMode; label: string }[] = [
    { mode: "2d", label: "Biểu đồ 2D" },
    { mode: "table", label: "Bảng" },
  ];
  return (
    <div className="flex flex-col items-start gap-1 sm:items-end">
      <div
        role="group"
        aria-label="Lối xem"
        className="inline-flex gap-1 rounded-lg border border-border-strong bg-inset p-1"
      >
        {can3d ? (
          <button
            type="button"
            aria-pressed={value === "3d"}
            onClick={() => onChange("3d")}
            className={`${ITEM} ${value === "3d" ? ON : OFF}`}
          >
            3D
          </button>
        ) : (
          <button
            type="button"
            aria-pressed={false}
            aria-disabled="true"
            aria-describedby={noteId}
            className={`${ITEM} cursor-not-allowed text-text-dim`}
          >
            3D
          </button>
        )}
        {options.map((option) => (
          <button
            key={option.mode}
            type="button"
            aria-pressed={value === option.mode}
            onClick={() => onChange(option.mode)}
            className={`${ITEM} ${value === option.mode ? ON : OFF}`}
          >
            {option.label}
          </button>
        ))}
      </div>
      {!can3d && (
        <p id={noteId} className="m-0 text-caption text-text-muted">
          {NO_3D_NOTE}
        </p>
      )}
    </div>
  );
}
