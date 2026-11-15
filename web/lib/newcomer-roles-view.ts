/**
 * Màn người mới (#147): dựng chữ hiển thị từ envelope của `GET /api/v1/newcomer-roles`.
 *
 * Không tính số mới và không sắp xếp lại (AD-22): số tin entry-level và n tra ở `meta.cells`, tỷ lệ là `share` đã qua
 * `suppression_for` ở máy chủ. Dòng `null_data` ghi "chưa đủ dữ liệu (n/ngưỡng)" thay cho tỷ lệ (#110). Câu trên màn
 * không chứa số; số đứng ở ô riêng (DEC-6, #132).
 */

import { FAILED_SOURCES_PREFIX, NOT_ENOUGH_DATA, type SnapshotCaption, formatCount, formatDate, formatPercent } from "./city-shares-view";
import { levelLabel, roleLabel } from "./labels";
import { type NewcomerRolesEnvelope, rowCounts } from "./newcomer-roles";

/** Đường dẫn hồ sơ kỹ năng của một vai trò. Tới khi có #111 thì là trang giữ chỗ. */
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
  /** "132 tin cho người mới". */
  entryText: string;
  /** "27,2%" khi có tỷ lệ; "chưa đủ dữ liệu (12/30)" khi `null_data`. */
  shareText: string;
  shareShown: boolean;
  /** "n = 485": số tin của vai trò. */
  nText: string;
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
      entryText: `${formatCount(entry)} tin cho người mới`,
      shareText: shareShown
        ? formatPercent(row.share.value as number)
        : `${NOT_ENOUGH_DATA} (${formatCount(n)}/${formatCount(minSample)})`,
      shareShown,
      nText: `n = ${formatCount(n)}`,
    };
  });
  return {
    lines,
    caption: {
      sources: meta.sources,
      snapshotDate: formatDate(meta.snapshot_date),
      notes: meta.coverage_notes,
      failedSources:
        meta.snapshot_status === "partial" && meta.sources_failed.length > 0
          ? FAILED_SOURCES_PREFIX + meta.sources_failed.join(", ")
          : null,
      filters: `Mọi vai trò · ${levelLabel(NEWCOMER_LEVEL)} (${data.levels.map(levelLabel).join(", ")}) · Mọi số năm`,
    },
  };
}
