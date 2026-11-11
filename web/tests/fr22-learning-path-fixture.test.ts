import { afterEach, describe, expect, it, vi } from "vitest";

import {
  fetchLearningPath,
  learningPathUrl,
  type LearningPathEnvelope,
  type PathSkill,
} from "@/lib/learning-path";
import { MAX_PROFILE_SKILLS } from "@/lib/haido-keys";

import backendJson from "./fixtures/learning-path-backend.json";
import backendHaveJson from "./fixtures/learning-path-backend-have.json";
import aiMlJson from "./fixtures/learning-path-ai_ml.json";
import backendInternJson from "./fixtures/learning-path-backend.intern.json";
import dataEngineerHaveJson from "./fixtures/learning-path-data_engineer-have.json";
import dataEngineerJson from "./fixtures/learning-path-data_engineer.json";
import qaJson from "./fixtures/learning-path-qa.json";
import { jsonResponse } from "./helpers/fetch";

// Các fixture là response của API giả cho `GET /api/v1/learning-path` (#212).
// `tests/api/test_ad17_web_fixtures.py` so chúng với API; đây chỉ kiểm phía web đọc được và không tự đếm (AD-22).
const backend = backendJson as unknown as LearningPathEnvelope;
const backendHave = backendHaveJson as unknown as LearningPathEnvelope;
const dataEngineer = dataEngineerJson as unknown as LearningPathEnvelope;
const qa = qaJson as unknown as LearningPathEnvelope;
const aiMl = aiMlJson as unknown as LearningPathEnvelope;
const backendIntern = backendInternJson as unknown as LearningPathEnvelope;
const dataEngineerHave = dataEngineerHaveJson as unknown as LearningPathEnvelope;

function allSkills(envelope: LearningPathEnvelope): PathSkill[] {
  return envelope.data.stages.flatMap((stage) => stage.skills);
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("FR-22 fixture lộ trình học", () => {
  it("mọi tỷ lệ thuộc ô data.cell_id và ô đó có trong meta.cells", () => {
    expect(backend.data.status).toBe("ready");
    expect(backend.data.cell_id).not.toBeNull();
    for (const skill of allSkills(backend)) {
      expect(skill.rate.kind).toBe("skill_rate");
      expect(skill.rate.cell_id).toBe(backend.data.cell_id);
    }
    expect(backend.meta.cells[backend.data.cell_id!]).toBeDefined();
    expect(backend.meta.cells[backend.data.entry_cell_id]).toBeDefined();
  });

  it("các chặng đã được đánh số liền từ 1, web không sắp xếp lại", () => {
    expect(backend.data.stages.map((s) => s.stage)).toEqual(backend.data.stages.map((_, i) => i + 1));
    expect(backend.data.path_size).toBe(allSkills(backend).length);
  });

  it("have làm các số đếm và current_stage đổi nhưng không đổi thứ tự", () => {
    const order = (e: LearningPathEnvelope) => allSkills(e).map((s) => s.skill);
    expect(order(backendHave)).toEqual(order(backend));
    expect(backendHave.data.have_on_path).toBe(3);
    expect(allSkills(backendHave).filter((s) => s.have).map((s) => s.skill).sort()).toEqual(["git", "java", "sql"]);
    expect(backendHave.data.current_stage).toBe(1);
  });

  it("data_engineer entry: không ô nào trong vai trò đủ 30 tin nên mọi tỷ lệ là null_data, cell_id ở trong vai trò", () => {
    const { cell_id: cellId, entry_cell_id: entryId } = dataEngineer.data;
    const min = dataEngineer.meta.thresholds.min_sample;
    expect(cellId).toBe("vn.data_engineer");
    expect(entryId).toBe("vn.data_engineer.entry");
    expect(dataEngineer.meta.cells[entryId].n).toBeLessThan(min);
    expect(dataEngineer.meta.cells[cellId!].n).toBeLessThan(min);
    expect(dataEngineer.meta.cells[cellId!].fallback_label).toBeTruthy();
    expect(dataEngineer.data.status).toBe("ready");
    for (const skill of allSkills(dataEngineer)) {
      expect(skill.rate.display).toBe("null_data");
      expect(skill.rate.value).toBeNull();
      expect(skill.group).toBeNull();
    }
  });

  it("backend intern: quay về vai trò × mọi cấp, có số, nhãn ghi tỷ lệ Mid trở lên", () => {
    const { cell_id: cellId, entry_cell_id: entryId } = backendIntern.data;
    expect(cellId).toBe("vn.backend");
    expect(entryId).toBe("vn.backend.entry");
    const cell = backendIntern.meta.cells[cellId!];
    expect(cell.n).toBeGreaterThanOrEqual(backendIntern.meta.thresholds.min_sample);
    expect(cell.fallback_label).toMatch(/Mid trở lên/);
    expect(backendIntern.meta.cells[entryId].fallback_label).toBeNull();
    for (const skill of allSkills(backendIntern)) {
      expect(skill.rate.display).toBe("shown");
      expect(skill.rate.value).not.toBeNull();
    }
  });

  it("data_engineer với hồ sơ {java, sql, git}: giao là sql và git, java nằm ở have_ignored (FR-24)", () => {
    expect(dataEngineerHave.data.have_on_path).toBe(2);
    expect(dataEngineerHave.data.path_size).toBe(11);
    expect(dataEngineerHave.data.have_ignored).toEqual(["java"]);
    expect(allSkills(dataEngineerHave).filter((s) => s.have).map((s) => s.skill).sort()).toEqual(["git", "sql"]);
  });

  it("not_ready: không chặng, không đếm, vẫn có ô entry", () => {
    expect(qa.data.status).toBe("not_ready");
    expect(qa.data.stages).toEqual([]);
    expect(qa.data.current_stage).toBeNull();
    expect(qa.data.cell_id).toBeNull();
    expect(qa.data.path_size).toBe(0);
    expect(qa.meta.cells[qa.data.entry_cell_id].n).toBeGreaterThan(0);
  });

  it("not_ready của ai_ml có hồ sơ kỹ năng để mở (#111); qa thì không có", () => {
    expect(aiMl.data.status).toBe("not_ready");
    expect(aiMl.data.role).toBe("ai_ml");
    expect(aiMl.data.stages).toEqual([]);
    expect(aiMl.meta.cells[aiMl.data.entry_cell_id].n).toBeGreaterThan(0);
  });
});

describe("FR-22 learningPathUrl và fetchLearningPath", () => {
  it("dựng query với have gửi nguyên mã, không đếm hay lọc", () => {
    expect(learningPathUrl("backend", "entry", ["java", "sql"])).toBe(
      "/api/v1/learning-path?role=backend&level=entry&have=java%2Csql",
    );
    expect(learningPathUrl("backend", "entry", [])).toBe("/api/v1/learning-path?role=backend&level=entry");
  });

  it("chỉ gửi tối đa 200 mã đầu của hồ sơ (AD-22)", () => {
    const codes = Array.from({ length: MAX_PROFILE_SKILLS + 5 }, (_, i) => `skill_${i}`);
    const have = new URL(learningPathUrl("backend", "entry", codes), "http://x").searchParams.get("have")!;
    expect(have.split(",")).toHaveLength(MAX_PROFILE_SKILLS);
  });

  it("bỏ mã trùng (giữ thứ tự gặp đầu) và mã sai định dạng trước khi cắt 200, không đếm hay sắp xếp", () => {
    const have = (codes: string[]) => new URL(learningPathUrl("backend", "entry", codes), "http://x").searchParams.get("have");
    expect(have(["sql", "java", "sql", "Java", "spring-boot", "", "java", "a".repeat(41), "git"])).toBe("sql,java,git");
    expect(learningPathUrl("backend", "entry", ["Java", "x y"])).toBe("/api/v1/learning-path?role=backend&level=entry");
    const dupes = [
      ...Array.from({ length: MAX_PROFILE_SKILLS }, (_, i) => `skill_${i}`),
      ...Array.from({ length: 60 }, (_, i) => `skill_${i}`),
      "extra_skill",
    ];
    const sent = have(dupes)!.split(",");
    expect(sent).toHaveLength(MAX_PROFILE_SKILLS);
    expect(new Set(sent).size).toBe(MAX_PROFILE_SKILLS);
    expect(sent[0]).toBe("skill_0");
    const invalidFirst = [...Array.from({ length: 30 }, () => "BAD"), ...Array.from({ length: 200 }, (_, i) => `k${i}`)];
    expect(have(invalidFirst)!.split(",")).toHaveLength(MAX_PROFILE_SKILLS);
  });

  it("422 invalid_query cũng không thử lại, lỗi máy chủ thì có", async () => {
    const invalid = { error: { code: "invalid_query", message: "have không hợp lệ." } };
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(422, invalid)));
    expect(await fetchLearningPath("backend", "entry", [])).toMatchObject({ code: "invalid_query", retryable: false });
    const internal = { error: { code: "internal_error", message: "Lỗi." } };
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(500, internal)));
    expect(await fetchLearningPath("backend", "entry", [])).toMatchObject({ code: "internal_error", retryable: true });
  });

  it("trả envelope khi API trả 200", async () => {
    const fetchMock = vi.fn(async (..._args: [RequestInfo | URL, RequestInit?]) => jsonResponse(200, backend));
    vi.stubGlobal("fetch", fetchMock);
    const result = await fetchLearningPath("backend", "entry", []);
    expect(result).toEqual({ kind: "ok", envelope: backend });
    expect(String(fetchMock.mock.calls[0][0])).toBe("/api/v1/learning-path?role=backend&level=entry");
  });

  it("trả lỗi chuẩn của API và không thử lại với unknown_cell", async () => {
    const error = { error: { code: "unknown_cell", message: "Không có ô.", snapshot_date: "2026-11-03" } };
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(404, error)));
    expect(await fetchLearningPath("backend", "senior", [])).toEqual({
      kind: "error",
      code: "unknown_cell",
      message: "Không có ô.",
      snapshotDate: "2026-11-03",
      retryable: false,
    });
  });

  it("body lạ hoặc mạng hỏng là unreadable", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => jsonResponse(200, { data: {} })));
    expect(await fetchLearningPath("backend", "entry", [])).toEqual({ kind: "unreadable" });
    vi.stubGlobal("fetch", vi.fn(async () => Promise.reject(new Error("offline"))));
    expect(await fetchLearningPath("backend", "entry", [])).toEqual({ kind: "unreadable" });
  });
});
