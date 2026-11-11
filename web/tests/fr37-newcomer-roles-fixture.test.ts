import { describe, expect, it } from "vitest";

import { rowCounts, type NewcomerRolesEnvelope } from "@/lib/newcomer-roles";

import fixtureJson from "./fixtures/newcomer-roles.json";

// `newcomer-roles.json` là response của API giả cho `GET /api/v1/newcomer-roles` (#144).
// `tests/api/test_ad17_web_fixtures.py` so nó với API, nên đây chỉ kiểm phía web đọc được.
const fixture = fixtureJson as unknown as NewcomerRolesEnvelope;

describe("FR-37 fixture màn người mới", () => {
  it("mọi dòng có ô entry-level và ô vai trò trong meta.cells", () => {
    expect(fixture.data.rows.length).toBeGreaterThan(0);
    for (const row of fixture.data.rows) {
      expect(fixture.meta.cells[row.entry_cell_id]).toBeDefined();
      expect(fixture.meta.cells[row.total_cell_id]).toBeDefined();
      expect(row.share.kind).toBe("level_share");
      expect(row.share.cell_id).toBe(row.total_cell_id);
    }
  });

  it("rowCounts tra số entry-level và n từ meta, không tính lại", () => {
    const aiMl = fixture.data.rows.find((r) => r.role === "ai_ml")!;
    expect(rowCounts(fixture, aiMl)).toEqual({ entry: 501, n: 877 });
  });

  it("vai trò dưới ngưỡng có share null_data nhưng vẫn có số entry-level và n", () => {
    const small = fixture.data.rows.find((r) => r.share.display === "null_data" && rowCounts(fixture, r).n > 0)!;
    expect(small.share.value).toBeNull();
    const { entry, n } = rowCounts(fixture, small);
    expect(n).toBeLessThan(fixture.meta.thresholds.min_sample);
    expect(entry).toBeGreaterThanOrEqual(0);
  });

  it("vai trò đủ mẫu mà không có tin entry-level hiện 0", () => {
    const zero = fixture.data.rows.find((r) => r.share.display === "shown" && rowCounts(fixture, r).entry === 0)!;
    expect(zero.share.value).toBe(0);
  });

  it("rowCounts ném lỗi khi thiếu ô, để màn hình không hiện số bịa", () => {
    const broken = structuredClone(fixture);
    delete broken.meta.cells[broken.data.rows[0].entry_cell_id];
    expect(() => rowCounts(broken, broken.data.rows[0])).toThrow();
  });
});
