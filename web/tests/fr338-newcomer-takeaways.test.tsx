import { describe, expect, it } from "vitest";

import { type NewcomerRolesEnvelope } from "@/lib/newcomer-roles";
import { buildNewcomerView } from "@/lib/newcomer-roles-view";

import fixtureJson from "./fixtures/newcomer-roles.json";

// #338 — Nhận định ở phần người mới. buildNewcomerView trả thêm field takeaways.

const fixture = fixtureJson as unknown as NewcomerRolesEnvelope;

function newcomerTakeaways(patch?: (env: NewcomerRolesEnvelope) => void): string[] {
  const env = structuredClone(fixture);
  patch?.(env);
  return buildNewcomerView(env).takeaways;
}

describe("#338 — nhận định ở phần người mới", () => {
  it("có câu nêu tên hai vai trò dẫn đầu khi ≥ 3 vai trò có shareShown", () => {
    const lines = newcomerTakeaways();
    expect(lines.length).toBeGreaterThanOrEqual(1);
    const text = lines.join(" ");
    // Fixture xếp theo thứ tự API (ai_ml, frontend, ... ) nhưng takeaway nên nhắc top entry
    expect(text).toMatch(/AI|Frontend|QA/i);
  });

  it("nhận ra vai trò tỷ lệ entry cao nhưng tổng tin nhỏ", () => {
    // Trong fixture: QA có entry_share 63.1% nhưng chỉ 130 tin tổng (xếp sau ai_ml 877, ba_po_pm 791)
    const lines = newcomerTakeaways();
    const text = lines.join(" ");
    expect(text).toMatch(/đáng chú ý|bất ngờ|cửa vào/i);
  });

  it("câu không chứa chữ số (DEC-6)", () => {
    for (const line of newcomerTakeaways()) expect(line).not.toMatch(/\d/);
  });
});
