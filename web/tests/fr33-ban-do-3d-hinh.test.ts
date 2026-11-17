import { describe, expect, it } from "vitest";

import { buildCitySharesView } from "@/lib/city-shares-view";
import { COLUMN_MAX_HEIGHT, buildColumns } from "@/lib/map-3d-view";
import { ARCHIPELAGOS, CITY_POINTS, OUTLINE, project } from "@/lib/vietnam-geo";

import { allLowSampleEnvelope, fakeEnvelope } from "./fixtures/envelopes";

// #314 — hình học của bản đồ 3D (hàm thuần, chạy được trong jsdom): viền Việt Nam, Hoàng Sa, Trường Sa, phép chiếu,
// và cột theo `view.bars` (FR-33: một chiều cao một nghĩa, cột mẫu nhỏ vẫn vẽ theo tỷ trọng thật).

describe("fr33 #314 — viền và quần đảo", () => {
  it("fr33: viền có đất liền, mọi điểm nằm trong khung đất liền Việt Nam, có nguồn và giấy phép", () => {
    expect(OUTLINE.rings.length).toBeGreaterThan(0);
    expect(OUTLINE.rings[0].length).toBeGreaterThan(200);
    for (const ring of OUTLINE.rings) {
      for (const [lon, lat] of ring) {
        expect(lon).toBeGreaterThanOrEqual(102);
        expect(lon).toBeLessThanOrEqual(110);
        expect(lat).toBeGreaterThanOrEqual(8);
        expect(lat).toBeLessThanOrEqual(24);
      }
    }
    expect(OUTLINE.license).toBe("CC BY 4.0");
    expect(OUTLINE.source).toContain("geoBoundaries");
  });

  it("fr33: Hoàng Sa và Trường Sa luôn có, mỗi quần đảo có nhãn và điểm đảo trong vùng tọa độ của nó", () => {
    const byId = Object.fromEntries(ARCHIPELAGOS.map((a) => [a.id, a]));
    expect(byId.hoang_sa.label).toBe("Quần đảo Hoàng Sa");
    expect(byId.truong_sa.label).toBe("Quần đảo Trường Sa");
    expect(byId.hoang_sa.islands.length).toBeGreaterThanOrEqual(3);
    expect(byId.truong_sa.islands.length).toBeGreaterThanOrEqual(3);
    for (const { lon, lat } of byId.hoang_sa.islands) {
      expect(lat).toBeGreaterThanOrEqual(15);
      expect(lat).toBeLessThanOrEqual(17.5);
      expect(lon).toBeGreaterThanOrEqual(110.5);
      expect(lon).toBeLessThanOrEqual(113);
    }
    for (const { lon, lat } of byId.truong_sa.islands) {
      expect(lat).toBeGreaterThanOrEqual(7);
      expect(lat).toBeLessThanOrEqual(12);
      expect(lon).toBeGreaterThanOrEqual(111);
      expect(lon).toBeLessThanOrEqual(117);
    }
  });

  it("fr33: phép chiếu giữ hướng: bắc ở z nhỏ hơn, đông ở x lớn hơn", () => {
    const haNoi = project(CITY_POINTS.ha_noi);
    const hcm = project(CITY_POINTS.ho_chi_minh);
    const daNang = project(CITY_POINTS.da_nang);
    expect(haNoi.z).toBeLessThan(daNang.z);
    expect(daNang.z).toBeLessThan(hcm.z);
    const hoangSa = project(ARCHIPELAGOS.find((a) => a.id === "hoang_sa")!.islands[0]);
    expect(hoangSa.x).toBeGreaterThan(daNang.x);
  });
});

describe("fr33 #314 — cột", () => {
  it("fr33: đúng ba cột Hà Nội, TP.HCM, Đà Nẵng theo view.bars", () => {
    const view = buildCitySharesView(fakeEnvelope("all"));
    const columns = buildColumns(view.bars);
    expect(columns.map((c) => c.city)).toEqual(["ha_noi", "ho_chi_minh", "da_nang"]);
    expect(columns.map((c) => c.label)).toEqual(["Hà Nội", "TP.HCM", "Đà Nẵng"]);
  });

  it("fr33 ad22: chiều cao = share.value nhân hằng số, không chuẩn hóa theo cột cao nhất", () => {
    const view = buildCitySharesView(fakeEnvelope("all"));
    const columns = buildColumns(view.bars);
    columns.forEach((column, i) => {
      expect(column.height).toBeCloseTo(view.bars[i].value * COLUMN_MAX_HEIGHT, 10);
    });
    const [a, b] = columns;
    expect(a.height / b.height).toBeCloseTo(view.bars[0].value / view.bars[1].value, 10);
  });

  it("fr33: cột mẫu nhỏ vẫn cao theo tỷ trọng thật, mờ, nhãn có câu Cỡ mẫu nhỏ", () => {
    const view = buildCitySharesView(allLowSampleEnvelope());
    const columns = buildColumns(view.bars);
    for (const [i, column] of columns.entries()) {
      expect(column.faded).toBe(true);
      expect(column.height).toBeCloseTo(view.bars[i].value * COLUMN_MAX_HEIGHT, 10);
      expect(column.info).toMatch(/Cỡ mẫu nhỏ \(n = [\d.]+ < 30\): số liệu chỉ để tham khảo/);
    }
  });

  it("fr33: cột đặt ở đúng vị trí chiếu của thành phố", () => {
    const view = buildCitySharesView(fakeEnvelope("all"));
    const [haNoi] = buildColumns(view.bars);
    expect(haNoi.position).toEqual(project(CITY_POINTS.ha_noi));
  });
});
