import Link from "next/link";

import type { SkillRoleLine } from "@/lib/skill-roles-view";

/**
 * Danh sách vai trò theo tỷ lệ tin nhắc tới một kỹ năng (#169), đúng thứ tự API gửi. Mỗi dòng là liên kết sang hồ sơ
 * kỹ năng của vai trò (#111). Như danh sách người mới (#147): trên điện thoại tên và ô số xếp chồng, từ `sm` thành hai
 * cột; dòng chưa đủ dữ liệu có viền nét đứt hổ phách, không có tỷ lệ. Tỷ lệ và n đứng ở ô số riêng (DEC-6).
 */
export function SkillRolesList({ lines }: { lines: SkillRoleLine[] }) {
  return (
    <ol aria-label="Vai trò theo tỷ lệ tin nhắc tới kỹ năng" className="m-0 flex list-none flex-col gap-2 p-0">
      {lines.map((line) => (
        <li key={line.role}>
          <Link
            href={line.href}
            className={`grid min-h-target gap-1 rounded-xl border bg-panel px-4 py-3 transition-colors hover:border-selected sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center sm:gap-4 ${
              line.shareShown ? "border-border" : "border-dashed border-amber-deep"
            }`}
          >
            <span className="text-body-md font-semibold text-text">{line.label}</span>
            <span className="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-caption sm:justify-end">
              {line.shareShown ? (
                <span className="text-text-secondary">
                  <span className="font-mono text-mono text-text">{line.shareText}</span> {line.sentence}
                </span>
              ) : (
                <span className="text-amber">{line.shareText}</span>
              )}
              <span className="font-mono text-footer text-text-muted">{line.nText}</span>
            </span>
          </Link>
        </li>
      ))}
    </ol>
  );
}
