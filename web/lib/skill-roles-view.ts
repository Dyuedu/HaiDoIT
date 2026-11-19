/**
 * Mục "Kỹ năng của bạn dùng ở vai trò nào" (#169): dựng chữ hiển thị từ envelope của `GET /api/v1/skill-roles`.
 *
 * Không tính số mới, không sắp xếp lại (AD-22): tỷ lệ là `share` đã qua `suppression_for` ở máy chủ; cỡ mẫu là `rowN`
 * (`n_by_measure.skill_count`). Câu "chưa tin nào nhắc" chỉ theo `data.mentioned`. Câu không chứa số; tỷ lệ và n đứng ở
 * ô riêng (DEC-6).
 */

import { FAILED_SOURCES_PREFIX, NOT_ENOUGH_DATA, type SnapshotCaption, formatCount, formatDate, formatPercent } from "./city-shares-view";
import { levelLabel, roleLabel } from "./labels";
import { skillProfileHref } from "./newcomer-roles-view";
import { type SkillLabel, type SkillRolesEnvelope, rowN } from "./skill-roles";

/** "Học máy (Machine Learning)" khi hai tên khác nhau, nếu không thì một tên. */
export function skillLabelText(skill: SkillLabel): string {
  return skill.name_vi.trim().toLowerCase() === skill.name_en.trim().toLowerCase()
    ? skill.name_en
    : `${skill.name_vi} (${skill.name_en})`;
}

export interface SkillRoleLine {
  role: string;
  label: string;
  /** Hồ sơ kỹ năng của vai trò ở cấp `data.level` (#111). */
  href: string;
  shareShown: boolean;
  /** "77,6%" khi có tỷ lệ; "chưa đủ dữ liệu (4/30)" khi `null_data`. */
  shareText: string;
  /** "tin AI/ML mới vào nghề nhắc tới Python" khi có tỷ lệ; `null` khi `null_data`. */
  sentence: string | null;
  /** "n = 501": cỡ mẫu của phép đo. */
  nText: string;
}

export interface SkillRolesView {
  /** "Kỹ năng: Học máy (Machine Learning)". */
  skillText: string;
  /** "Chưa tin tuyển dụng hiện tại nào nhắc tới ABAP." khi `mentioned = false`; `null` khi có. */
  notMentionedText: string | null;
  lines: SkillRoleLine[];
  caption: SnapshotCaption;
}

export function buildSkillRolesView(envelope: SkillRolesEnvelope): SkillRolesView {
  const { data, meta } = envelope;
  const minSample = meta.thresholds.min_sample;
  const name = data.skill.name_vi;
  const entry = levelLabel(data.level).toLowerCase();
  const lines = data.rows.map((row) => {
    const n = rowN(envelope, row);
    const shareShown = row.share.display !== "null_data" && row.share.value !== null;
    const label = roleLabel(row.role);
    return {
      role: row.role,
      label,
      href: skillProfileHref(row.role, data.level),
      shareShown,
      shareText: shareShown
        ? formatPercent(row.share.value as number)
        : `${NOT_ENOUGH_DATA} (${formatCount(n)}/${formatCount(minSample)})`,
      sentence: shareShown ? `tin ${label} ${entry} nhắc tới ${name}` : null,
      nText: `n = ${formatCount(n)}`,
    };
  });
  return {
    skillText: `Kỹ năng: ${skillLabelText(data.skill)}`,
    notMentionedText: data.mentioned ? null : `Chưa tin tuyển dụng hiện tại nào nhắc tới ${name}.`,
    lines,
    caption: {
      sources: meta.sources,
      snapshotDate: formatDate(meta.snapshot_date),
      notes: meta.coverage_notes,
      failedSources:
        meta.snapshot_status === "partial" && meta.sources_failed.length > 0
          ? FAILED_SOURCES_PREFIX + meta.sources_failed.join(", ")
          : null,
      filters: `Mọi vai trò · ${levelLabel(data.level)} (${data.levels.map(levelLabel).join(", ")}) · Mọi số năm`,
    },
  };
}
