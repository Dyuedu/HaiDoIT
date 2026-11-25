/**
 * Màn hồ sơ kỹ năng (#152): dựng chữ hiển thị từ envelope của `GET /api/v1/skill-rates`.
 *
 * Không tính số mới, không sắp xếp lại, không đếm trên mã kỹ năng (AD-22): tỷ lệ là `rate` đã qua `suppression_for` ở
 * máy chủ, dòng đếm core là `have_core`/`core_size` của API. Câu trên màn không chứa số; số đứng ở ô riêng (DEC-6).
 */

import {
  ANY_YEARS_TEXT,
  NOT_ENOUGH_DATA,
  type SnapshotCaption,
  filtersText,
  formatCount,
  formatPercent,
  snapshotCaption,
} from "./city-shares-view";
import { levelLabel, roleLabel } from "./labels";
import type { SkillGroup, SkillRatesEnvelope } from "./skill-rates";

/** Đường dẫn Cố vấn: màn lộ trình học (#121, #217). */
export const ADVISOR_PATH = "/co-van";

/** Lộ trình học của vai trò ở cấp, mở tại một kỹ năng nếu có (#153, #217). Nơi duy nhất dựng liên kết này. */
export function learningPathHref(role: string, level: string, skill: string | null = null): string {
  const params = new URLSearchParams({ role, level });
  if (skill !== null) params.set("skill", skill);
  return `${ADVISOR_PATH}?${params.toString()}`;
}

export const GROUP_LABELS: Readonly<Record<SkillGroup, string>> = {
  core: "Cốt lõi",
  common: "Thường gặp",
  company_specific: "Riêng của công ty",
};

/** Chú thích nhóm. Nhóm thường gặp nói theo FR-25; không câu nào khuyên bỏ một kỹ năng. */
export const GROUP_NOTE =
  "Cốt lõi: kỹ năng tin của vai trò này đòi nhiều nhất. Thường gặp: nên học sau khi đã nắm các kỹ năng cốt lõi. Riêng của công ty: chỉ một phần nhỏ tin nhắc tới.";

/** Ô đủ mẫu mà mọi kỹ năng dưới ngưỡng "thường gặp": không có dòng nào. Câu không chứa số (DEC-6). */
export const NO_COMMON_SKILLS = "Không kỹ năng nào được nhắc đủ thường xuyên để xếp vào nhóm cốt lõi hay phổ biến.";

export interface SkillProfileLine {
  skill: string;
  name: string;
  /** "65,4%" khi có tỷ lệ; "chưa đủ dữ liệu" khi `null_data`. */
  shareText: string;
  shareShown: boolean;
  /** "Cốt lõi", ...; `null` khi `null_data`. */
  groupText: string | null;
  /** Lộ trình học ở kỹ năng này (#153). */
  pathHref: string;
}

export interface SkillProfileView {
  lines: SkillProfileLine[];
  /** Câu thay danh sách khi `lines` rỗng (ô đủ mẫu, mọi kỹ năng hiếm); `null` khi có dòng. */
  emptyText: string | null;
  /** Câu quay về của API, nguyên văn; `null` khi chọn thẳng ô. */
  fallbackText: string | null;
  /** "Tính trên 157 tin": số tin của ô đã dùng (#324). */
  nText: string;
  /** "3/6" do API đếm; `null` khi chưa đủ dữ liệu. */
  coreCountText: string | null;
  caption: SnapshotCaption;
}

export function buildSkillProfileView(
  envelope: SkillRatesEnvelope,
  names: (code: string) => string,
): SkillProfileView {
  const { data, meta } = envelope;
  const cell = meta.cells[data.cell_id];
  const lines = data.rows.map((row) => {
    const shareShown = row.rate.display !== "null_data" && row.rate.value !== null;
    return {
      skill: row.skill,
      name: names(row.skill),
      shareText: shareShown ? formatPercent(row.rate.value as number) : NOT_ENOUGH_DATA,
      shareShown,
      groupText: shareShown && row.group ? GROUP_LABELS[row.group] : null,
      pathHref: learningPathHref(data.role, data.level, row.skill),
    };
  });
  return {
    lines,
    emptyText: lines.length === 0 ? NO_COMMON_SKILLS : null,
    fallbackText: cell.fallback_label,
    nText: `Tính trên ${formatCount(cell.n)} tin`,
    coreCountText:
      data.core_size !== null && data.have_core !== null && data.core_size > 0
        ? `${data.have_core}/${data.core_size}`
        : null,
    caption: snapshotCaption(meta, filtersText([roleLabel(data.role), levelLabel(data.level), ANY_YEARS_TEXT])),
  };
}
