import {
  type ErrorBody,
  type Meta,
  isCount,
  isMeta,
  isNonEmptyString,
  isRecord,
  isStringArray,
  readErrorBody,
} from "./city-shares";
import { MAX_PROFILE_SKILLS, isSkillCode } from "./haido-keys";
import type { LearningPathData, LearningPathEnvelope, PathSkill, PathStage } from "./learning-path";

export type AdvisorGenerationMode = "llm" | "market_fallback";

export interface AdvisorRoadmapData {
  path: LearningPathData;
  cv_skills: string[];
  missing_core_skills: string[];
  missing_common_skills: string[];
  advisor_summary: string;
  generation_mode: AdvisorGenerationMode;
}

export interface AdvisorRoadmapEnvelope {
  data: AdvisorRoadmapData;
  meta: Meta;
}

export type AdvisorRoadmapResult =
  | { kind: "ok"; envelope: AdvisorRoadmapEnvelope }
  | { kind: "error"; status: number; code: ErrorBody["code"]; message: string }
  | { kind: "unreadable" };

export const ADVISOR_ROADMAP_URL = "/api/v1/advisor/roadmap";
export const CV_MAX_BYTES = 5 * 1024 * 1024;
export const CV_ACCEPT_ATTR =
  ".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document";

const PDF_MIME = "application/pdf";
const DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document";

export function validateCvFile(file: File): string | null {
  if (file.size === 0) return "Tệp CV đang rỗng. Vui lòng chọn tệp PDF hoặc DOCX hợp lệ.";
  if (file.size > CV_MAX_BYTES) return "Tệp CV vượt quá giới hạn 5 MB.";
  const lowerName = file.name.trim().toLowerCase();
  const byExt = lowerName.endsWith(".pdf") || lowerName.endsWith(".docx");
  const mime = file.type.trim().toLowerCase();
  const byMime = mime === PDF_MIME || mime === DOCX_MIME;
  if (!byMime && !(mime === "" && byExt) && !byExt) {
    return "Chỉ nhận CV định dạng PDF hoặc DOCX (tối đa 5 MB).";
  }
  return null;
}

function isOrdinal(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}

function isPathSkill(value: unknown, cellId: string): value is PathSkill {
  if (!isRecord(value) || !isRecord(value.rate) || !isRecord(value.resource)) return false;
  if (typeof value.skill !== "string" || !isSkillCode(value.skill)) return false;
  if (value.rate.kind !== "skill_rate" || value.rate.cell_id !== cellId) return false;
  if (value.rate.display === "null_data") {
    if (value.rate.value !== null || value.group !== null) return false;
  } else if (
    (value.rate.display !== "shown" && value.rate.display !== "low_sample_shown") ||
    typeof value.rate.value !== "number" ||
    (value.group !== "core" && value.group !== "common" && value.group !== "company_specific")
  ) {
    return false;
  }
  if (!isStringArray(value.foundation_for) || !isStringArray(value.prerequisite_for)) return false;
  if (typeof value.have !== "boolean" || !isNonEmptyString(value.blurb)) return false;
  return (
    isNonEmptyString(value.resource.title) &&
    isNonEmptyString(value.resource.url) &&
    value.resource.url.startsWith("https://")
  );
}

function isCellEntry(cell: unknown): boolean {
  return (
    isRecord(cell) &&
    isCount(cell.n) &&
    (cell.fallback_label === null || isNonEmptyString(cell.fallback_label))
  );
}

function isLearningPathPayload(data: unknown, meta: Meta): data is LearningPathData {
  if (!isRecord(data) || !isNonEmptyString(data.role) || !isNonEmptyString(data.level)) return false;
  if (typeof data.entry_cell_id !== "string" || !isCellEntry(meta.cells[data.entry_cell_id])) return false;
  if (!Array.isArray(data.stages) || !isStringArray(data.have_ignored)) return false;
  if (!isOrdinal(data.have_on_path) || !isOrdinal(data.path_size)) return false;

  if (data.status === "not_ready") {
    return data.cell_id === null && data.stages.length === 0 && data.current_stage === null;
  }
  if (data.status !== "ready" || typeof data.cell_id !== "string" || !isCellEntry(meta.cells[data.cell_id])) {
    return false;
  }
  if (data.stages.length === 0) return false;
  if (data.current_stage !== null && !isOrdinal(data.current_stage)) return false;

  const cid = data.cell_id;
  return data.stages.every(
    (stage) =>
      isRecord(stage) &&
      isOrdinal(stage.stage) &&
      isNonEmptyString(stage.title) &&
      typeof stage.choose_one === "boolean" &&
      Array.isArray(stage.skills) &&
      stage.skills.length > 0 &&
      stage.skills.every((skill) => isPathSkill(skill, cid))
  );
}

export function isAdvisorRoadmapEnvelope(body: unknown): body is AdvisorRoadmapEnvelope {
  if (!isRecord(body) || !isRecord(body.data) || !isMeta(body.meta)) return false;
  const d = body.data;
  if (!isLearningPathPayload(d.path, body.meta)) return false;
  if (!isStringArray(d.cv_skills) || !isStringArray(d.missing_core_skills) || !isStringArray(d.missing_common_skills)) {
    return false;
  }
  if (!isNonEmptyString(d.advisor_summary)) return false;
  return d.generation_mode === "llm" || d.generation_mode === "market_fallback";
}

/**
 * Chuyển đổi `AdvisorRoadmapEnvelope` thành `LearningPathEnvelope` để dùng lại nguyên vẹn `buildLearningPathView`
 * và `PathGraph`.
 */
export function toLearningPathEnvelope(envelope: AdvisorRoadmapEnvelope): LearningPathEnvelope {
  return {
    data: envelope.data.path,
    meta: envelope.meta,
  };
}

/**
 * Cập nhật trạng thái `have`, `have_on_path`, `current_stage`, `have_ignored` khi người dùng tick kỹ năng trên
 * lộ trình đã tạo từ CV mà không cần upload lại CV (giữ nguyên thứ tự và tỷ lệ JD từ API).
 */
export function applyHaveToAdvisorEnvelope(
  envelope: AdvisorRoadmapEnvelope,
  haveSkills: readonly string[]
): AdvisorRoadmapEnvelope {
  const validOwned = Array.from(new Set(haveSkills.filter((c) => isSkillCode(c))));
  const ownedSet = new Set(validOwned);
  const onPath = new Set<string>();

  const nextStages: PathStage[] = envelope.data.path.stages.map((stage) => ({
    ...stage,
    skills: stage.skills.map((skill) => {
      onPath.add(skill.skill);
      return {
        ...skill,
        have: ownedSet.has(skill.skill),
      };
    }),
  }));

  let haveOnPath = 0;
  for (const st of nextStages) {
    for (const s of st.skills) {
      if (s.have) haveOnPath += 1;
    }
  }

  const nextCurrent =
    nextStages.find((st) =>
      st.choose_one ? !st.skills.some((s) => s.have) : !st.skills.every((s) => s.have)
    )?.stage ?? null;

  const haveIgnored = validOwned.filter((c) => !onPath.has(c)).sort();

  return {
    ...envelope,
    data: {
      ...envelope.data,
      path: {
        ...envelope.data.path,
        stages: nextStages,
        current_stage: nextCurrent,
        have_on_path: haveOnPath,
        have_ignored: haveIgnored,
      },
    },
  };
}

export async function postAdvisorRoadmap(options: {
  file: File;
  role: string;
  level: string;
  consent: boolean;
  have?: readonly string[];
  signal?: AbortSignal;
}): Promise<AdvisorRoadmapResult> {
  const form = new FormData();
  form.append("cv", options.file, options.file.name);
  form.append("role", options.role);
  form.append("level", options.level);
  form.append("consent", options.consent ? "true" : "false");
  if (options.have && options.have.length > 0) {
    const clean = Array.from(new Set(options.have.filter((c) => isSkillCode(c)))).slice(0, MAX_PROFILE_SKILLS);
    if (clean.length > 0) form.append("have", clean.join(","));
  }

  try {
    const res = await fetch(ADVISOR_ROADMAP_URL, {
      method: "POST",
      body: form,
      signal: options.signal,
    });
    const body: unknown = await res.json();
    if (!res.ok) {
      const error = readErrorBody(body);
      return error
        ? { kind: "error", status: res.status, code: error.code, message: error.message }
        : { kind: "unreadable" };
    }
    return isAdvisorRoadmapEnvelope(body) ? { kind: "ok", envelope: body } : { kind: "unreadable" };
  } catch {
    return { kind: "unreadable" };
  }
}
