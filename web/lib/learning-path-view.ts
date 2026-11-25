/**
 * Màn lộ trình học (#217): dựng chữ hiển thị từ envelope của `GET /api/v1/learning-path`.
 *
 * Không tính số mới, không sắp xếp lại, không đếm (AD-7, AD-22): thứ tự kỹ năng, chặng đang học, "N/M" và tỷ lệ đều của
 * API. Mỗi chặng là một chủ đề; việc duy nhất ở đây là đặt cụm kỹ năng của chặng so le phải trái để vẽ. Câu trên màn không
 * chứa số; số đứng ở ô riêng (DEC-6).
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
import type { LearningPathEnvelope, PathSkill } from "./learning-path";
import { GROUP_LABELS } from "./skill-profile-view";

/** Lộ trình luôn tính trên nhóm mới vào nghề; màn không có ô Cấp bậc (#134, #121). */
export const PATH_LEVEL = "entry";

export const NOT_READY_TEXT = "Lộ trình học có thứ tự cho vai trò này đang được biên soạn.";
export const NOT_READY_HINT = "Trong lúc chờ, hồ sơ kỹ năng cho biết tin tuyển dụng của vai trò này yêu cầu những gì.";
export const ALL_DONE_TEXT = "Bạn đã đi hết các chặng của lộ trình này.";

export interface SkillLink {
  skill: string;
  name: string;
}

/** Loại ô để tô màu; `unknown` khi API ẩn nhóm. */
export type NodeKind = "core" | "common" | "foundation" | "unknown";

export interface PathNode {
  skill: string;
  /** Tên đầy đủ, song ngữ khi hai tên khác nhau. */
  name: string;
  /** Tên ngắn ghi trên ô. */
  shortName: string;
  kind: NodeKind;
  /** "65,4%", hoặc "chưa đủ dữ liệu" khi `null_data`. */
  shareText: string;
  shareShown: boolean;
  /** "Kỹ năng nền tảng (cần cho X, Y)" (FR-20), "Cốt lõi", "Thường gặp"; `null` khi `null_data`. */
  groupText: string | null;
  /** Kỹ năng trên lộ trình phải học trước kỹ năng này (cạnh trực tiếp), theo thứ tự lộ trình. */
  needs: SkillLink[];
  /** Kỹ năng trên lộ trình cần kỹ năng này (cạnh trực tiếp). */
  unlocks: SkillLink[];
  /** Các lựa chọn khác của cùng chặng chọn một; rỗng ở chặng thường. */
  alternatives: SkillLink[];
  blurb: string;
  resource: { title: string; url: string };
}

export type PathSide = "left" | "right";

export type StageState = "done" | "current" | "later";

export interface PathStageView {
  stage: number;
  title: string;
  chooseOne: boolean;
  state: StageState;
  side: PathSide;
  nodes: PathNode[];
}

export interface LearningPathView {
  ready: boolean;
  stages: PathStageView[];
  /** Mọi kỹ năng theo thứ tự lộ trình. */
  nodes: PathNode[];
  /** Chặng đang học (gồm cả kỹ năng đã có); `null` khi đã đi hết. */
  current: PathStageView | null;
  allDone: boolean;
  /** "3/14" do API đếm. */
  countText: string;
  /** Câu quay về của API, nguyên văn; `null` khi chọn thẳng ô. */
  fallbackText: string | null;
  /** "Tính trên 157 tin"; `null` khi API ẩn mọi tỷ lệ. */
  nText: string | null;
  caption: SnapshotCaption;
}

function groupText(skill: PathSkill, names: (code: string) => string): string | null {
  if (skill.group === null) return null;
  if (skill.foundation_for.length > 0) return `Kỹ năng nền tảng (cần cho ${skill.foundation_for.map(names).join(", ")})`;
  return GROUP_LABELS[skill.group];
}

function kindOf(skill: PathSkill): NodeKind {
  if (skill.group === null) return "unknown";
  if (skill.foundation_for.length > 0) return "foundation";
  return skill.group === "core" ? "core" : "common";
}

export function buildLearningPathView(
  envelope: LearningPathEnvelope,
  names: (code: string) => string,
  shortNames: (code: string) => string = names,
): LearningPathView {
  const { data, meta } = envelope;
  const link = (code: string): SkillLink => ({ skill: code, name: names(code) });
  const all = data.stages.flatMap((stage) => stage.skills);

  const toNode = (skill: PathSkill, choices: PathSkill[]): PathNode => {
    const shareShown = skill.rate.display === "shown" && skill.rate.value !== null;
    return {
      skill: skill.skill,
      name: names(skill.skill),
      shortName: shortNames(skill.skill),
      kind: kindOf(skill),
      shareText: shareShown ? formatPercent(skill.rate.value as number) : NOT_ENOUGH_DATA,
      shareShown,
      groupText: groupText(skill, names),
      needs: all.filter((other) => other.prerequisite_for.includes(skill.skill)).map((other) => link(other.skill)),
      unlocks: skill.prerequisite_for.map(link),
      alternatives: choices.filter((other) => other.skill !== skill.skill).map((other) => link(other.skill)),
      blurb: skill.blurb,
      resource: skill.resource,
    };
  };

  const state = (stage: number): StageState => {
    if (data.current_stage === null || stage < data.current_stage) return "done";
    return stage === data.current_stage ? "current" : "later";
  };

  const stages = data.stages.map(
    ({ stage, title, choose_one: chooseOne, skills }, index): PathStageView => ({
      stage,
      title,
      chooseOne,
      state: state(stage),
      side: index % 2 === 0 ? "right" : "left",
      nodes: skills.map((skill) => toNode(skill, chooseOne ? skills : [])),
    }),
  );
  const nodes = stages.flatMap((stage) => stage.nodes);
  const cell = data.cell_id === null ? null : meta.cells[data.cell_id];

  return {
    ready: data.status === "ready",
    stages,
    nodes,
    current: stages.find((stage) => stage.state === "current") ?? null,
    allDone: data.status === "ready" && data.current_stage === null,
    countText: `${data.have_on_path}/${data.path_size}`,
    fallbackText: cell?.fallback_label ?? null,
    nText: cell && nodes.some((node) => node.shareShown) ? `Tính trên ${formatCount(cell.n)} tin` : null,
    caption: snapshotCaption(meta, filtersText([roleLabel(data.role), levelLabel(data.level), ANY_YEARS_TEXT])),
  };
}

/**
 * Đường cong nối giữa cạnh ô chặng với giữa hàng thứ `index` trong `count` hàng cao bằng nhau, trong hệ 100×100 được kéo
 * giãn theo khung. Không cần đo DOM: các hàng của một bên luôn cao bằng nhau (`auto-rows-fr`).
 */
export function connectorPath(side: PathSide, index: number, count: number): string {
  const y = ((index + 0.5) / count) * 100;
  const [from, to] = side === "right" ? [0, 100] : [100, 0];
  return `M ${from} 50 C 50 50, 50 ${y}, ${to} ${y}`;
}
