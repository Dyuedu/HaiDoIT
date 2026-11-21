import { describe, expect, it } from "vitest";

import { type MarketOverviewEnvelope } from "@/lib/market-overview";
import { buildMarketOverviewView } from "@/lib/market-overview-view";

import fixtureJson from "./fixtures/market-overview.json";

// #338 — Nhận định hành động ở phần toàn cảnh. Mở rộng takeaways với câu hướng dẫn hành động.

const fixture = fixtureJson as unknown as MarketOverviewEnvelope;

function takeaways(patch?: (env: MarketOverviewEnvelope) => void): string[] {
  const env = structuredClone(fixture);
  patch?.(env);
  return buildMarketOverviewView(env).takeaways;
}

describe("#338 — nhận định hành động ở phần toàn cảnh", () => {
  it("có câu gợi ý vai trò cho người chưa chọn hướng, dựa trên roles_by_entry_share", () => {
    const lines = takeaways();
    const text = lines.join(" ");
    // roles_by_entry_share[0] trong fixture là qa
    expect(text).toMatch(/chưa chọn hướng|bắt đầu/i);
  });

  it("có câu khuyến khích khi tỷ trọng '0 năm' + 'không ghi' ≥ 40%", () => {
    const lines = takeaways((env) => {
      const total = env.meta.cells[env.data.total_cell_id].n;
      const y0 = env.data.years.find((y) => y.code === "0")!;
      const yNone = env.data.years.find((y) => y.code === "none")!;
      env.meta.cells[y0.share.cell_id].n = Math.ceil(total * 0.15);
      env.meta.cells[yNone.share.cell_id].n = Math.ceil(total * 0.30);
    });
    const text = lines.join(" ");
    expect(text).toMatch(/không phải rào cản|cơ hội.*mở|không bắt buộc/i);
  });

  it("có câu lưu ý khi tỷ trọng '0 năm' + 'không ghi' < 40%", () => {
    // Fixture mặc định: 0 (2.1%) + none (28.1%) = 30.2% < 40%
    const lines = takeaways();
    const text = lines.join(" ");
    expect(text).toMatch(/yêu cầu kinh nghiệm|chuẩn bị|kinh nghiệm.*cần/i);
  });

  it("có câu gợi ý theo vùng miền khi HN và HCM chênh lệch rõ ở một vai trò", () => {
    const lines = takeaways();
    const text = lines.join(" ");
    expect(text).toMatch(/miền Bắc|miền Nam|sinh viên.*Hà Nội|sinh viên.*TP\.HCM/i);
  });

  it("câu nhận định không chứa chữ số (DEC-6)", () => {
    const lines = takeaways();
    for (const line of lines) expect(line).not.toMatch(/\d/);
  });
});
