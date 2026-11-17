import { describe, expect, it } from "vitest";

import { fetchSkillRoles, rowN, skillRolesUrl, type SkillRolesEnvelope } from "@/lib/skill-roles";

import abapJson from "./fixtures/skill-roles-abap.json";
import figmaJson from "./fixtures/skill-roles-figma.json";
import machineLearningJson from "./fixtures/skill-roles-machine_learning.json";
import pythonJson from "./fixtures/skill-roles-python.json";
import sapJson from "./fixtures/skill-roles-sap.json";

// Ba fixture là response của API giả cho `GET /api/v1/skill-roles?skill=` (#166).
// `tests/api/test_ad17_web_fixtures.py` so chúng với API, nên đây chỉ kiểm phía web đọc được.
const python = pythonJson as unknown as SkillRolesEnvelope;
const figma = figmaJson as unknown as SkillRolesEnvelope;
const abap = abapJson as unknown as SkillRolesEnvelope;
const machineLearning = machineLearningJson as unknown as SkillRolesEnvelope;
const sap = sapJson as unknown as SkillRolesEnvelope;

function stubFetch(status: number, body: unknown): void {
  globalThis.fetch = (async () =>
    new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } })) as typeof fetch;
}

describe("FR-9 fixture màn kỹ năng qua các vai trò", () => {
  it("mọi dòng có ô entry-level trong meta.cells và share là skill_rate của ô đó", () => {
    for (const env of [python, figma, abap, sap, machineLearning]) {
      expect(env.data.rows.length).toBeGreaterThan(0);
      for (const row of env.data.rows) {
        expect(env.meta.cells[row.share.cell_id]).toBeDefined();
        expect(row.share.kind).toBe("skill_rate");
        expect(row.share.cell_id).toBe(`vn.${row.role}.entry`);
      }
    }
  });

  it("rowN tra n từ meta, không tính lại", () => {
    const top = python.data.rows[0];
    expect(top.role).toBe("ai_ml");
    expect(rowN(python, top)).toBe(501);
  });

  it("rowN là cỡ mẫu của phép đo (skill_count), không phải n của ô: game có 43 tin, 12 được quét kỹ năng", () => {
    const game = python.data.rows.find((r) => r.role === "game")!;
    expect(python.meta.cells[game.share.cell_id].n).toBe(43);
    expect(rowN(python, game)).toBe(12);
    expect(game.share.display).toBe("null_data");
    expect(rowN(python, game)).toBeLessThan(python.meta.thresholds.min_sample);
  });

  it("rowN dùng n của ô khi ô không có skill_count", () => {
    const row = python.data.rows[0];
    const copy = structuredClone(python);
    copy.meta.cells[row.share.cell_id].n_by_measure = {};
    expect(rowN(copy, row)).toBe(501);
  });

  it("level là mã nhóm cấp entry để mở hồ sơ kỹ năng của #111", () => {
    for (const env of [python, figma, abap, sap, machineLearning]) expect(env.data.level).toBe("entry");
  });

  it("sap: không tin entry-level nào nhắc nhưng có tin ở cấp khác nên mentioned = true", () => {
    expect(sap.data.mentioned).toBe(true);
    expect(sap.data.rows.every((r) => r.share.value === null || r.share.value === 0)).toBe(true);
  });

  it("nhãn song ngữ khác nhau: machine_learning là Machine Learning và Học máy", () => {
    expect(machineLearning.data.skill).toEqual({
      code: "machine_learning",
      name_en: "Machine Learning",
      name_vi: "Học máy",
    });
  });

  it("vai trò dưới ngưỡng có share null_data nhưng vẫn có n để ghi 'chưa đủ dữ liệu (n/ngưỡng)'", () => {
    const small = python.data.rows.find((r) => r.share.display === "null_data" && rowN(python, r) > 0)!;
    expect(small.share.value).toBeNull();
    expect(rowN(python, small)).toBeLessThan(python.meta.thresholds.min_sample);
  });

  it("vai trò đủ mẫu mà không tin nào nhắc hiện 0", () => {
    const zero = python.data.rows.find((r) => r.share.display === "shown" && r.share.value === 0)!;
    expect(rowN(python, zero)).toBeGreaterThanOrEqual(python.meta.thresholds.min_sample);
  });

  it("kỹ năng không tin nào nhắc có mentioned = false, kỹ năng khác có mentioned = true", () => {
    expect(abap.data.mentioned).toBe(false);
    expect(python.data.mentioned).toBe(true);
    expect(figma.data.mentioned).toBe(true);
  });

  it("nhãn kỹ năng là mã cùng tên song ngữ để màn ghi kỹ năng đã dùng", () => {
    expect(python.data.skill).toEqual({ code: "python", name_en: "Python", name_vi: "Python" });
  });

  it("rowN ném lỗi khi thiếu ô, để màn hình không hiện số bịa", () => {
    const broken = structuredClone(python);
    delete broken.meta.cells[broken.data.rows[0].share.cell_id];
    expect(() => rowN(broken, broken.data.rows[0])).toThrow();
  });
});

describe("FR-9 skillRolesUrl và fetchSkillRoles", () => {
  it("URL mang mã kỹ năng", () => {
    expect(skillRolesUrl("python")).toBe("/api/v1/skill-roles?skill=python");
  });

  it("response đúng hợp đồng thì trả ok", async () => {
    stubFetch(200, python);
    const result = await fetchSkillRoles({ skill: "python" });
    expect(result.kind).toBe("ok");
  });

  it("unknown_skill, unknown_cell và invalid_query không cho thử lại, lỗi khác thì có", async () => {
    for (const [code, retryable] of [
      ["unknown_skill", false],
      ["unknown_cell", false],
      ["invalid_query", false],
      ["internal_error", true],
    ] as const) {
      stubFetch(code === "internal_error" ? 500 : code === "invalid_query" ? 422 : 404, { error: { code, message: "x", snapshot_date: null } });
      const result = await fetchSkillRoles({ skill: "python" });
      expect(result).toMatchObject({ kind: "error", code, retryable });
    }
  });

  it("body sai hợp đồng là unreadable: mentioned thiếu, share sai kind, ô thiếu", async () => {
    const noMentioned = structuredClone(python) as unknown as { data: Record<string, unknown> };
    delete noMentioned.data.mentioned;
    const wrongKind = structuredClone(python);
    (wrongKind.data.rows[0].share as { kind: string }).kind = "level_share";
    const noLevel = structuredClone(python) as unknown as { data: Record<string, unknown> };
    delete noLevel.data.level;
    const noCell = structuredClone(python);
    delete noCell.meta.cells[noCell.data.rows[0].share.cell_id];
    for (const bad of [noMentioned, wrongKind, noCell, noLevel]) {
      stubFetch(200, bad);
      expect(await fetchSkillRoles({ skill: "python" })).toEqual({ kind: "unreadable" });
    }
  });

  it("mạng hỏng là unreadable", async () => {
    globalThis.fetch = (async () => {
      throw new TypeError("network");
    }) as typeof fetch;
    expect(await fetchSkillRoles({ skill: "python" })).toEqual({ kind: "unreadable" });
  });
});
