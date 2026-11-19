import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { buildCitySharesView } from "@/lib/city-shares-view";
import { COLUMN_MAX_HEIGHT, buildColumns } from "@/lib/map-3d-view";
import { ARCHIPELAGOS, CITY_POINTS, OUTLINE, OUTLINE_PATH, STAGE, toStage } from "@/lib/vietnam-geo";

import { allLowSampleEnvelope, fakeEnvelope } from "./fixtures/envelopes";

// #314, #316 — hình học của bản đồ 3D theo prototype màn 01: sân khấu 460×560 px, viền Việt Nam thật (geoBoundaries),
// Hoàng Sa, Trường Sa, và cột cao `share.value × 400` px (như `p × 4` của prototype; FR-33: một chiều cao một nghĩa).

function inStage({ px, py }: { px: number; py: number }) {
  expect(px).toBeGreaterThanOrEqual(0);
  expect(px).toBeLessThanOrEqual(STAGE.width);
  expect(py).toBeGreaterThanOrEqual(0);
  expect(py).toBeLessThanOrEqual(STAGE.height);
}

describe("fr33 #316 — sân khấu", () => {
  it("fr33: sân khấu đúng 460×560 như prototype", () => {
    expect(STAGE).toEqual({ width: 460, height: 560 });
  });

  it("fr33: viền đất liền có nguồn, giấy phép, và mọi điểm nằm trong sân khấu", () => {
    expect(OUTLINE.license).toBe("CC BY 4.0");
    expect(OUTLINE.source).toContain("geoBoundaries");
    for (const ring of OUTLINE.rings) for (const [lon, lat] of ring) inStage(toStage({ lon, lat }));
    expect(OUTLINE_PATH.startsWith("M")).toBe(true);
    expect(OUTLINE_PATH.split("Z").length - 1).toBe(OUTLINE.rings.length);
  });

  it("fr33: Hoàng Sa và Trường Sa luôn có, nhãn như prototype, đảo nằm trong sân khấu", () => {
    const byId = Object.fromEntries(ARCHIPELAGOS.map((a) => [a.id, a]));
    expect(byId.hoang_sa.shortLabel).toBe("QĐ. Hoàng Sa");
    expect(byId.truong_sa.shortLabel).toBe("QĐ. Trường Sa");
    for (const group of ARCHIPELAGOS) {
      expect(group.islands.length).toBeGreaterThanOrEqual(3);
      for (const island of group.islands) inStage(toStage(island));
    }
  });

  it("fr33: hướng giữ đúng: bắc ở trên, Hoàng Sa ở phía đông Đà Nẵng", () => {
    const haNoi = toStage(CITY_POINTS.ha_noi);
    const daNang = toStage(CITY_POINTS.da_nang);
    const hcm = toStage(CITY_POINTS.ho_chi_minh);
    expect(haNoi.py).toBeLessThan(daNang.py);
    expect(daNang.py).toBeLessThan(hcm.py);
    expect(toStage(ARCHIPELAGOS[0].islands[0]).px).toBeGreaterThan(daNang.px);
  });
});

describe("fr33 #316 — cột", () => {
  it("fr33: đúng ba cột theo view.bars, đặt ở vị trí sân khấu của thành phố", () => {
    const view = buildCitySharesView(fakeEnvelope("all"));
    const columns = buildColumns(view);
    expect(columns.map((c) => c.city)).toEqual(["ha_noi", "ho_chi_minh", "da_nang"]);
    expect(columns[0].stage).toEqual(toStage(CITY_POINTS.ha_noi));
  });

  it("fr33 ad22: chiều cao = share.value × 400 px, không chuẩn hóa theo cột cao nhất", () => {
    expect(COLUMN_MAX_HEIGHT).toBe(400);
    const view = buildCitySharesView(fakeEnvelope("all"));
    buildColumns(view).forEach((column, i) => {
      expect(column.height).toBeCloseTo(view.bars[i].value * 400, 10);
    });
  });

  it("fr33: thẻ ghi tỷ trọng và n trên tổng như prototype; tên đọc được có tỷ trọng và n", () => {
    const view = buildCitySharesView(fakeEnvelope("all"));
    const [haNoi] = buildColumns(view);
    expect(haNoi.valueText).toBe(`${view.bars[0].percent} · ${view.bars[0].nText}/${view.table.total.nText} tin`);
    expect(haNoi.info).toBe(view.bars[0].accessibleName);
    expect(haNoi.faded).toBe(false);
    expect(haNoi.smallLabel).toBeNull();
  });

  it("fr33: cột mẫu nhỏ vẫn cao theo tỷ trọng thật, mờ, có câu cỡ mẫu nhỏ", () => {
    const view = buildCitySharesView(allLowSampleEnvelope());
    for (const [i, column] of buildColumns(view).entries()) {
      expect(column.faded).toBe(true);
      expect(column.height).toBeCloseTo(view.bars[i].value * 400, 10);
      expect(column.smallLabel).toMatch(/^Cỡ mẫu nhỏ \(n = [\d.]+ < 30\): số liệu chỉ để tham khảo$/);
    }
  });
});

describe("fr33 #316 — không còn three.js", () => {
  it("fr33: web/package.json không có three, @react-three/fiber, @types/three", () => {
    const pkg = JSON.parse(readFileSync(join(process.cwd(), "package.json"), "utf8"));
    const all = { ...pkg.dependencies, ...pkg.devDependencies };
    for (const name of ["three", "@react-three/fiber", "@types/three"]) expect(all).not.toHaveProperty(name);
  });
});
