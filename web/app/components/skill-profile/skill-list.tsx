import Link from "next/link";

import type { SkillProfileLine } from "@/lib/skill-profile-view";

interface SkillListProps {
  lines: SkillProfileLine[];
  /** Mã kỹ năng có trong hồ sơ (chỉ để hiện tick, không đếm). */
  owned: ReadonlySet<string>;
  onToggle: (skill: string) => void;
}

/**
 * Danh sách kỹ năng của hồ sơ (#152), đúng thứ tự API gửi. Mỗi dòng có một ô tick gốc ("Đã có …", #206) và, khi kỹ năng
 * chưa có, một liên kết tới lộ trình học ở đúng kỹ năng đó (#153). Trên điện thoại tên và ô số xếp chồng; từ `sm` thành
 * hai cột. Dòng chưa đủ dữ liệu có chữ hổ phách, không có tỷ lệ hay nhóm.
 */
export function SkillList({ lines, owned, onToggle }: SkillListProps) {
  return (
    <ol aria-label="Kỹ năng theo tỷ lệ tin yêu cầu" className="m-0 flex list-none flex-col gap-2 p-0">
      {lines.map((line) => {
        const have = owned.has(line.skill);
        return (
          <li
            key={line.skill}
            className="grid gap-2 rounded-xl border border-border bg-panel px-4 py-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center sm:gap-4"
          >
            <div className="flex min-w-0 items-center gap-3">
              <input
                type="checkbox"
                checked={have}
                onChange={() => onToggle(line.skill)}
                aria-label={`Đã có ${line.name}`}
                className="size-6 shrink-0 cursor-pointer accent-selected"
              />
              {have ? (
                <span className="flex min-h-target min-w-0 flex-wrap items-center gap-x-2">
                  <span className="break-words text-body-md font-semibold text-text">{line.name}</span>
                  <span className="text-caption text-text-muted">Đã có</span>
                </span>
              ) : (
                <Link
                  href={line.pathHref}
                  className="flex min-h-target min-w-0 flex-wrap items-center gap-x-2 rounded-md text-text hover:text-selected"
                >
                  <span className="break-words text-body-md font-semibold">{line.name}</span>
                  <span className="text-caption text-text-muted">Xem lộ trình học</span>
                </Link>
              )}
            </div>
            <span className="flex flex-wrap items-baseline gap-x-3 gap-y-1 pl-9 text-caption sm:justify-end sm:pl-0">
              <span className={line.shareShown ? "font-mono text-mono text-text" : "text-amber"}>{line.shareText}</span>
              {line.groupText && <span className="text-text-secondary">{line.groupText}</span>}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
