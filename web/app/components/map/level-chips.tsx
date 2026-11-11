import { useId } from "react";

import { LEVEL_OPTIONS } from "@/lib/labels";

interface LevelChipsProps {
  value: string;
  onChange: (level: string) => void;
}

/**
 * Bộ chọn cấp bậc (#163, #134): mỗi lựa chọn một `<button aria-pressed>` cao tối thiểu 44px, cùng kiểu với chip vai
 * trò, xuống dòng được ở khổ điện thoại. Luôn bấm được, kể cả khi đang lỗi. Dòng chú thích nói nhóm "Mới vào nghề" gồm
 * những cấp nào, vì người dùng không thấy danh sách `level_groups` trong config.
 */
export function LevelChips({ value, onChange }: LevelChipsProps) {
  const noteId = useId();
  return (
    <div className="flex flex-col gap-1">
      <div className="flex flex-wrap items-center gap-2">
        <span aria-hidden="true" className="font-mono text-kicker uppercase text-text-muted">
          Cấp bậc
        </span>
        <div role="group" aria-label="Cấp bậc" aria-describedby={noteId} className="flex flex-wrap gap-2">
          {LEVEL_OPTIONS.map((level) => {
            const selected = level.code === value;
            return (
              <button
                key={level.code}
                type="button"
                aria-pressed={selected}
                onClick={() => onChange(level.code)}
                className={`min-h-target rounded-full border px-4 text-chip transition-colors ${
                  selected
                    ? "border-selected bg-selected/[0.14] text-text"
                    : "border-border-chip bg-inset text-text-secondary hover:border-selected"
                }`}
              >
                {level.label}
              </button>
            );
          })}
        </div>
      </div>
      <p id={noteId} className="m-0 text-caption text-text-muted">
        Mới vào nghề gồm Intern, Fresher và Junior.
      </p>
    </div>
  );
}
