import Link from "next/link";

import type { NewcomerLine } from "@/lib/newcomer-roles-view";

/**
 * Danh sách vai trò theo số tin cho người mới (#147), đúng thứ tự API gửi. Mỗi dòng là một liên kết sang hồ sơ kỹ năng
 * của vai trò ở cấp mới vào nghề. Trên điện thoại tên vai trò và ô số xếp chồng; từ `sm` thành hai cột (cách của
 * summary list trong GOV.UK Frontend). Dòng chưa đủ dữ liệu có viền nét đứt hổ phách, không có tỷ lệ.
 */
export function NewcomerList({ lines }: { lines: NewcomerLine[] }) {
  return (
    <ol aria-label="Vai trò theo số tin cho người mới" className="m-0 flex list-none flex-col gap-2 p-0">
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
              <span className="font-mono text-mono text-text">{line.entryText}</span>
              <span className={line.shareShown ? "font-mono text-mono text-text-secondary" : "text-amber"}>
                {line.shareShown ? `${line.shareText} số tin của vai trò` : line.shareText}
              </span>
              <span className="font-mono text-footer text-text-muted">{line.nText}</span>
            </span>
          </Link>
        </li>
      ))}
    </ol>
  );
}
