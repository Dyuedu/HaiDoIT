/**
 * Màn người mới (#147): dựng chữ hiển thị từ envelope của `GET /api/v1/newcomer-roles`.
 *
 * Không tính số mới và không sắp xếp lại (AD-22): số tin entry-level và n tra ở `meta.cells`, tỷ lệ là `share` đã qua
 * `suppression_for` ở máy chủ. Dòng `null_data` ghi "Mới có n tin, cần ít nhất ngưỡng" thay cho tỷ lệ (#110, #324). Câu trên màn
 * không chứa số; số đứng ở ô riêng (DEC-6, #132).
 */

import {
  ANY_YEARS_TEXT,
  type SnapshotCaption,
  filtersText,
  formatCount,
  formatPercent,
  notEnoughText,
  snapshotCaption,
} from "./city-shares-view";
import { levelLabel, roleLabel } from "./labels";
import { type NewcomerRolesEnvelope, rowCounts } from "./newcomer-roles";

/** Đường dẫn hồ sơ kỹ năng của một vai trò (#152; trước đó là trang giữ chỗ của #147). */
export const SKILL_PROFILE_PATH = "/ho-so-ky-nang";
/** Cấp mở sẵn khi chạm một vai trò trên màn người mới. */
export const NEWCOMER_LEVEL = "entry";

export function skillProfileHref(role: string, level: string = NEWCOMER_LEVEL): string {
  return `${SKILL_PROFILE_PATH}?role=${encodeURIComponent(role)}&level=${encodeURIComponent(level)}`;
}

export interface NewcomerLine {
  role: string;
  label: string;
  href: string;
  /** "132 trên 485 tin dành cho người mới" (#324); `null` khi vai trò không có tin nào. */
  entryText: string | null;
  /** "27,2%" khi có tỷ lệ; "Mới có 12 tin, cần ít nhất 30" hoặc "Chưa có tin nào" khi `null_data`. */
  shareText: string;
  shareShown: boolean;
  /** Độ dài thanh 0–1 (#330): tỷ lệ của dòng so với tỷ lệ lớn nhất của danh sách, chỉ để vẽ; `null` khi API ẩn tỷ lệ. */
  barLength: number | null;
}

export interface NewcomerView {
  lines: NewcomerLine[];
  takeaways: string[];
  caption: SnapshotCaption;
}

function newcomerTakeaways(lines: NewcomerLine[]): string[] {
  const shown = lines.filter((l) => l.shareShown);
  const result: string[] = [];
  if (shown.length >= 3) {
    result.push(`${shown[0].label} và ${shown[1].label} chiếm phần lớn cơ hội cho người mới vào nghề.`);
  }
  if (shown.length >= 3) {
    const byTotalDesc = [...lines].filter((l) => l.shareShown);
    const topByTotal = byTotalDesc.slice(0, 3).map((l) => l.role);
    const surprise = shown.find((l) => !topByTotal.includes(l.role));
    if (surprise) {
      result.push(`Đáng chú ý, ${surprise.label} cũng là cửa vào rộng dù tổng tin không nằm trong nhóm đầu.`);
    }
  }
  return result;
}

export function buildNewcomerView(envelope: NewcomerRolesEnvelope): NewcomerView {
  const { data, meta } = envelope;
  const minSample = meta.thresholds.min_sample;
  // Tỷ lệ lớn nhất chỉ dùng để vẽ thanh dài nhất kín rãnh (#330); số in ra vẫn là `share.value` (AD-22).
  const top = data.rows.reduce((max, row) => (row.share.value !== null && row.share.value > max ? row.share.value : max), 0);
  const lines = data.rows.map((row) => {
    const { entry, n } = rowCounts(envelope, row);
    const shareShown = row.share.display === "shown" && row.share.value !== null;
    return {
      role: row.role,
      label: roleLabel(row.role),
      href: skillProfileHref(row.role),
      entryText: n > 0 ? `${formatCount(entry)} trên ${formatCount(n)} tin dành cho người mới` : null,
      shareText: shareShown ? formatPercent(row.share.value as number) : notEnoughText(n, minSample),
      shareShown,
      barLength: shareShown && top > 0 ? (row.share.value as number) / top : null,
    };
  });
  return {
    lines,
    takeaways: newcomerTakeaways(lines),
    caption: snapshotCaption(
      meta,
      filtersText(["Mọi vai trò", `${levelLabel(NEWCOMER_LEVEL)} (${data.levels.map(levelLabel).join(", ")})`, ANY_YEARS_TEXT]),
    ),
  };
}
