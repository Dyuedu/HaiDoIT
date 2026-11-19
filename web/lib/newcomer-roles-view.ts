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
}

export interface NewcomerView {
  lines: NewcomerLine[];
  caption: SnapshotCaption;
}

export function buildNewcomerView(envelope: NewcomerRolesEnvelope): NewcomerView {
  const { data, meta } = envelope;
  const minSample = meta.thresholds.min_sample;
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
    };
  });
  return {
    lines,
    caption: snapshotCaption(
      meta,
      filtersText(["Mọi vai trò", `${levelLabel(NEWCOMER_LEVEL)} (${data.levels.map(levelLabel).join(", ")})`, ANY_YEARS_TEXT]),
    ),
  };
}
