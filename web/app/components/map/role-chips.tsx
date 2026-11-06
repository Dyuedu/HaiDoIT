import { ROLE_OPTIONS } from "@/lib/labels";

interface RoleChipsProps {
  value: string;
  onChange: (role: string) => void;
}

/** Chip vai trò: mỗi chip một `<button aria-pressed>`. Luôn bấm được, kể cả khi đang lỗi. */
export function RoleChips({ value, onChange }: RoleChipsProps) {
  return (
    <div role="group" aria-label="Vai trò" className="flex flex-wrap gap-2">
      {ROLE_OPTIONS.map((role) => {
        const selected = role.code === value;
        return (
          <button
            key={role.code}
            type="button"
            aria-pressed={selected}
            onClick={() => onChange(role.code)}
            className={`min-h-target rounded-full border px-4 text-chip transition-colors ${
              selected
                ? "border-selected bg-selected/[0.14] text-text"
                : "border-border-chip bg-inset text-text-secondary hover:border-selected"
            }`}
          >
            {role.label}
          </button>
        );
      })}
    </div>
  );
}
