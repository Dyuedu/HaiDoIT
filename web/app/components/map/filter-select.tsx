import { useId } from "react";

interface FilterOption {
  code: string;
  label: string;
}

interface FilterSelectProps {
  label: string;
  value: string;
  options: readonly FilterOption[];
  onChange: (code: string) => void;
  /** Dòng chú thích dưới ô; nối với `<select>` bằng `aria-describedby`. */
  note?: string;
}

/**
 * Bộ lọc của màn Bản đồ (#293): một `<select>` gốc có `<label for>` hiện, thay cho hàng chip. Giữ picker và bàn phím
 * của trình duyệt (`appearance-none` chỉ bỏ mũi tên mặc định, mũi tên vẽ lại nằm ngoài ô và không bắt chuột). Luôn
 * đổi được, kể cả khi đang tải hoặc lỗi. Cao tối thiểu 44px, vòng focus là `:focus-visible` chung của `globals.css`.
 */
export function FilterSelect({ label, value, options, onChange, note }: FilterSelectProps) {
  const id = useId();
  const noteId = `${id}-note`;
  return (
    <div className="flex min-w-0 flex-col gap-1.5">
      <label htmlFor={id} className="font-mono text-kicker uppercase text-text-muted">
        {label}
      </label>
      <div className="relative">
        <select
          id={id}
          value={value}
          aria-describedby={note ? noteId : undefined}
          onChange={(event) => onChange(event.target.value)}
          className="min-h-target w-full min-w-0 cursor-pointer appearance-none truncate rounded-lg border border-border-chip bg-inset py-2 pl-3 pr-10 text-body-md text-text transition-[border-color] [color-scheme:dark] hover:border-selected"
        >
          {options.map((option) => (
            <option key={option.code} value={option.code}>
              {option.label}
            </option>
          ))}
        </select>
        <svg
          aria-hidden="true"
          viewBox="0 0 20 20"
          className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-text-muted forced-colors:text-[CanvasText]"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="m5 8 5 5 5-5" />
        </svg>
      </div>
      {note && (
        <p id={noteId} className="m-0 text-caption text-text-muted">
          {note}
        </p>
      )}
    </div>
  );
}
