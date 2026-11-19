import Link from "next/link";

import type { NewcomerLine } from "@/lib/newcomer-roles-view";

/**
 * Danh sách vai trò theo số tin cho người mới (#147), đúng thứ tự API gửi. Mỗi dòng là một liên kết sang hồ sơ kỹ năng
 * của vai trò ở cấp mới vào nghề. Trên điện thoại tên vai trò và ô số xếp chồng; từ `sm` thành hai cột (cách của
 * summary list trong GOV.UK Frontend). Dòng chưa đủ dữ liệu có viền nét đứt hổ phách, không có tỷ lệ. Tỷ lệ đứng
 * trước, rồi câu "X trên N tin dành cho người mới" (#324). Từ #330 mỗi dòng có tỷ lệ kèm một thanh: dài theo tỷ lệ so
 * với tỷ lệ lớn nhất của danh sách, chỉ để nhìn (`aria-hidden`); số đọc được vẫn là chữ của dòng.
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
            <span className="flex flex-col gap-1.5">
              <span className="text-body-md font-semibold text-text">{line.label}</span>
              {line.barLength !== null && (
                <span aria-hidden="true" className="block h-2 w-full max-w-md rounded-sm bg-track">
                  <span
                    data-part="share-bar"
                    className="block h-full rounded-sm bg-primary"
                    style={{ width: `${(line.barLength * 100).toFixed(2)}%` }}
                  />
                </span>
              )}
            </span>
            <span className="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-caption sm:justify-end">
              <span className={line.shareShown ? "font-mono text-mono text-text" : "text-amber"}>{line.shareText}</span>
              {line.entryText && <span className="text-text-secondary">{line.entryText}</span>}
            </span>
          </Link>
        </li>
      ))}
    </ol>
  );
}
