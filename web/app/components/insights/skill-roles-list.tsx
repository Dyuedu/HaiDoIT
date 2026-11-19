import Link from "next/link";

import type { SkillRoleLine } from "@/lib/skill-roles-view";

/**
 * Danh sách vai trò theo tỷ lệ tin nhắc tới một kỹ năng (#169), đúng thứ tự API gửi. Mỗi dòng là liên kết sang hồ sơ
 * kỹ năng của vai trò (#111). Như danh sách người mới (#147): trên điện thoại tên và ô số xếp chồng, từ `sm` thành hai
 * cột; dòng chưa đủ dữ liệu có viền nét đứt hổ phách, không có tỷ lệ. Tỷ lệ và n đứng ở ô số riêng (DEC-6). Từ #330
 * dòng có tỷ lệ kèm một biểu đồ lollipop trên trục 0–100%, chấm đứng đúng `share.value`, chỉ để nhìn (`aria-hidden`).
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
            <span className="flex flex-col gap-1.5">
              <span className="text-body-md font-semibold text-text">{line.label}</span>
              {line.dot !== null && (
                <span aria-hidden="true" className="relative block h-3 w-full max-w-md">
                  <span className="absolute top-1/2 left-0 h-px w-full bg-border-strong" />
                  <span
                    className="absolute top-1/2 left-0 h-0.5 -translate-y-1/2 bg-selected"
                    style={{ width: `${(line.dot * 100).toFixed(2)}%` }}
                  />
                  <span
                    data-part="share-dot"
                    className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-panel bg-selected"
                    style={{ left: `${(line.dot * 100).toFixed(2)}%` }}
                  />
                </span>
              )}
            </span>
            <span className="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-caption sm:justify-end">
              {line.shareShown ? (
                <span className="text-text-secondary">
                  <span className="font-mono text-mono text-text">{line.shareText}</span> {line.sentence}
                </span>
              ) : (
                <span className="text-amber">{line.shareText}</span>
              )}
              {line.nText && <span className="text-footer text-text-muted">{line.nText}</span>}
            </span>
          </Link>
        </li>
      ))}
    </ol>
  );
}
