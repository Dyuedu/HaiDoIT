/**
 * Danh sách kỹ năng để tìm và tick (#207): đọc `GET /api/v1/skills` (hình của #205) qua proxy `/api/*`.
 *
 * Tìm là lọc trên danh sách, không phải số học trên mã kỹ năng (AD-22 cho phép). Bỏ dấu theo đúng luật `fold` của
 * `haido_core/domain/posting_text.py`: chữ thường, bỏ dấu kết hợp, `đ` → `d`, gộp khoảng trắng. Dùng chung cho #113.
 */

import { isNonEmptyString, isRecord, isStringArray } from "./city-shares";
import { isSkillCode } from "./haido-keys";

export interface SkillRow {
  code: string;
  name_en: string;
  name_vi: string;
  aliases: string[];
}

export type SkillsResult = { kind: "ok"; skills: SkillRow[] } | { kind: "unreadable" };

/** Số kết quả tìm tối đa hiện ra. */
export const MAX_SEARCH_RESULTS = 8;

const MARKS = /\p{M}/gu;
const SPACES = /\s+/g;

/** Chuỗi để so khớp: chữ thường, bỏ dấu tiếng Việt (`đ` → `d`), gộp khoảng trắng. Giữ ký hiệu (`c#`, `c++`). */
export function foldText(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(MARKS, "")
    .replace(/đ/g, "d")
    .replace(SPACES, " ")
    .trim();
}

/** Tên hiện trên màn: "Học máy (Machine Learning)" khi hai tên khác nhau, nếu không thì một tên. */
export function skillDisplayName(skill: SkillRow): string {
  return foldText(skill.name_vi) === foldText(skill.name_en) ? skill.name_en : `${skill.name_vi} (${skill.name_en})`;
}

/**
 * Kỹ năng khớp `query` ở tên tiếng Anh, tên tiếng Việt hoặc bí danh, sau khi bỏ dấu. Khớp đầu tên (hay đầu một từ)
 * đứng trước khớp giữa tên; hòa thì giữ thứ tự danh sách. Tối đa `MAX_SEARCH_RESULTS`.
 */
export function searchSkills(skills: readonly SkillRow[], query: string): SkillRow[] {
  const needle = foldText(query);
  if (!needle) return [];
  const ranked: { skill: SkillRow; rank: number; index: number }[] = [];
  skills.forEach((skill, index) => {
    let best = Number.POSITIVE_INFINITY;
    for (const name of [skill.name_en, skill.name_vi, ...skill.aliases]) {
      const hay = foldText(name);
      const at = hay.indexOf(needle);
      if (at < 0) continue;
      const rank = hay === needle ? 0 : at === 0 ? 1 : hay[at - 1] === " " ? 2 : 3;
      best = Math.min(best, rank);
    }
    if (best !== Number.POSITIVE_INFINITY) ranked.push({ skill, rank: best, index });
  });
  ranked.sort((a, b) => a.rank - b.rank || a.index - b.index);
  return ranked.slice(0, MAX_SEARCH_RESULTS).map((entry) => entry.skill);
}

function isSkillRow(value: unknown): value is SkillRow {
  return (
    isRecord(value) &&
    typeof value.code === "string" &&
    isSkillCode(value.code) &&
    isNonEmptyString(value.name_en) &&
    isNonEmptyString(value.name_vi) &&
    isStringArray(value.aliases)
  );
}

/** Gọi `GET /api/v1/skills`. Không ném lỗi: mạng hỏng hay body sai hợp đồng là "không đọc được". */
export async function fetchSkills(options: { signal?: AbortSignal } = {}): Promise<SkillsResult> {
  try {
    const response = await fetch("/api/v1/skills", {
      headers: { accept: "application/json" },
      signal: options.signal,
    });
    const body: unknown = await response.json();
    if (!response.ok || !isRecord(body) || !isRecord(body.data) || !Array.isArray(body.data.skills)) {
      return { kind: "unreadable" };
    }
    const skills = body.data.skills;
    return skills.every(isSkillRow) ? { kind: "ok", skills } : { kind: "unreadable" };
  } catch {
    return { kind: "unreadable" };
  }
}
