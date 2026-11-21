/**
 * Mục "Kỹ năng của bạn dùng ở vai trò nào" (#169): dựng chữ hiển thị từ envelope của `GET /api/v1/skill-roles`.
 *
 * Không tính số mới, không sắp xếp lại (AD-22): tỷ lệ là `share` đã qua `suppression_for` ở máy chủ; cỡ mẫu là `rowN`
 * (`n_by_measure.skill_count`). Câu "chưa tin nào nhắc" chỉ theo `data.mentioned`. Câu không chứa số; tỷ lệ và n đứng ở
 * ô riêng (DEC-6).
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
  /** "77,6%" khi có tỷ lệ; "Mới có 4 tin, cần ít nhất 30" hoặc "Chưa có tin nào" khi `null_data` (#324). */
  shareText: string;
  /** Vị trí chấm 0–1 trên trục 0–100% (#330): đúng `share.value`; `null` khi `null_data`. */
  dot: number | null;
  /** "tin AI/ML cho người mới có nhắc tới Python" khi có tỷ lệ; `null` khi `null_data`. */
  sentence: string | null;
  /** "tính trên 501 tin": cỡ mẫu của phép đo (#324); rỗng khi không có tin nào. */
  nText: string;
}

export interface SkillRolesView {
  /** "Kỹ năng: Học máy (Machine Learning)". */
  skillText: string;
  /** "Hiện chưa tin tuyển dụng nào nhắc tới ABAP." khi `mentioned = false`; `null` khi có. */
  notMentionedText: string | null;
  /** Nhận định: "nền tảng" (nhiều vai trò) hoặc "chuyên biệt" (ít vai trò); `null` khi không nhắc. */
  insight: string | null;
  lines: SkillRoleLine[];
  caption: SnapshotCaption;
}

const BROAD_THRESHOLD = 0.2;

function skillInsight(skillName: string, lines: SkillRoleLine[]): string | null {
  const shown = lines.filter((l) => l.shareShown);
  if (shown.length === 0) return null;
  const broad = shown.filter((l) => l.dot !== null && l.dot > BROAD_THRESHOLD);
  if (broad.length >= Math.ceil(shown.length * 0.6)) {
    return `${skillName} là kỹ năng nền tảng — được nhiều vai trò yêu cầu ở tin cho người mới.`;
  }
  if (broad.length <= 2 && broad.length > 0) {
    const names = broad.map((l) => l.label);
    const joined = names.length === 1 ? names[0] : `${names[0]} và ${names[1]}`;
    return `${skillName} là kỹ năng chuyên biệt, chủ yếu được nhắc ở ${joined}.`;
  }
  return null;
}

export function buildSkillRolesView(envelope: SkillRolesEnvelope): SkillRolesView {
  const { data, meta } = envelope;
  const minSample = meta.thresholds.min_sample;
  const name = data.skill.name_vi;
  const audience = data.level === "entry" ? "cho người mới" : `cấp ${levelLabel(data.level)}`;
  const lines = data.rows.map((row) => {
    const n = rowN(envelope, row);
    const shareShown = row.share.display !== "null_data" && row.share.value !== null;
    const label = roleLabel(row.role);
    return {
      role: row.role,
      label,
      href: skillProfileHref(row.role, data.level),
      shareShown,
      shareText: shareShown ? formatPercent(row.share.value as number) : notEnoughText(n, minSample),
      dot: shareShown ? (row.share.value as number) : null,
      sentence: shareShown ? `tin ${label} ${audience} có nhắc tới ${name}` : null,
      nText: n > 0 ? `tính trên ${formatCount(n)} tin` : "",
    };
  });
  return {
    skillText: `Kỹ năng: ${skillLabelText(data.skill)}`,
    notMentionedText: data.mentioned ? null : `Hiện chưa tin tuyển dụng nào nhắc tới ${name}.`,
    insight: data.mentioned ? skillInsight(name, lines) : null,
    lines,
    caption: snapshotCaption(
      meta,
      filtersText(["Mọi vai trò", `${levelLabel(data.level)} (${data.levels.map(levelLabel).join(", ")})`, ANY_YEARS_TEXT]),
    ),
  };
}
