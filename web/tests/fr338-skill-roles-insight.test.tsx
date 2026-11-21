import { describe, expect, it } from "vitest";

import type { SkillRolesEnvelope } from "@/lib/skill-roles";
import { buildSkillRolesView } from "@/lib/skill-roles-view";

import abapJson from "./fixtures/skill-roles-abap.json";
import figmaJson from "./fixtures/skill-roles-figma.json";
import pythonJson from "./fixtures/skill-roles-python.json";

// #338 — Nhận định ở phần kỹ năng theo vai trò. buildSkillRolesView trả thêm field insight.

const python = pythonJson as unknown as SkillRolesEnvelope;
const figma = figmaJson as unknown as SkillRolesEnvelope;
const abap = abapJson as unknown as SkillRolesEnvelope;

describe("#338 — nhận định ở phần kỹ năng theo vai trò", () => {
  it("insight nói 'nền tảng' hoặc 'nhiều vai trò' khi kỹ năng phổ biến rộng (Python)", () => {
    const view = buildSkillRolesView(python);
    expect(view.insight).not.toBeNull();
    expect(view.insight).toMatch(/nền tảng|nhiều vai trò/i);
  });

  it("insight nói 'chuyên biệt' hoặc tên vai trò cụ thể khi kỹ năng hẹp (Figma)", () => {
    const view = buildSkillRolesView(figma);
    expect(view.insight).not.toBeNull();
    expect(view.insight).toMatch(/chuyên biệt|Frontend|Fullstack/i);
  });

  it("insight là null khi kỹ năng không được nhắc (ABAP)", () => {
    const view = buildSkillRolesView(abap);
    expect(view.insight).toBeNull();
  });

  it("câu không chứa chữ số (DEC-6)", () => {
    for (const env of [python, figma]) {
      const view = buildSkillRolesView(env);
      if (view.insight) expect(view.insight).not.toMatch(/\d/);
    }
  });
});
