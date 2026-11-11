import { useId } from "react";

import { YEARS_OPTIONS } from "@/lib/labels";

interface YearsChipsProps {
  value: string;
  onChange: (years: string) => void;
}

/**
 * Bộ chọn số năm kinh nghiệm (#280): mỗi lựa chọn một `<button aria-pressed>` cao tối thiểu 44px, cùng kiểu với chip
 * cấp bậc, xuống dòng được ở khổ điện thoại. Luôn bấm được, kể cả khi đang lỗi. Dòng chú thích nói mốc "tối đa N năm"
 * so với số năm tối thiểu mà tin yêu cầu.
 */
export function YearsChips({ value, onChange }: YearsChipsProps) {
  const noteId = useId();
  return (
    <div className="flex flex-col gap-1">
      <div className="flex flex-wrap items-center gap-2">
        <span aria-hidden="true" className="font-mono text-kicker uppercase text-text-muted">
          Số năm kinh nghiệm
        </span>
        <div
          role="group"
          aria-label="Số năm kinh nghiệm"
          aria-describedby={noteId}
          className="flex flex-wrap gap-2"
        >
          {YEARS_OPTIONS.map((years) => {
            const selected = years.code === value;
            return (
              <button
                key={years.code}
                type="button"
                aria-pressed={selected}
                onClick={() => onChange(years.code)}
                className={`min-h-target rounded-full border px-4 text-chip transition-colors ${
                  selected
                    ? "border-selected bg-selected/[0.14] text-text"
                    : "border-border-chip bg-inset text-text-secondary hover:border-selected"
                }`}
              >
                {years.label}
              </button>
            );
          })}
        </div>
      </div>
      <p id={noteId} className="m-0 text-caption text-text-muted">
        Tính theo số năm tối thiểu tin yêu cầu.
      </p>
    </div>
  );
}
