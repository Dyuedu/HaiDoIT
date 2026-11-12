import { describe, expect, it } from "vitest";

import { buildCitySharesView } from "@/lib/city-shares-view";
import { BAR_CITIES, cityLabel, LEGEND_CITIES } from "@/lib/labels";

import { buildEnvelope } from "./fixtures/envelopes";

function envelope() {
  return buildEnvelope({
    role: "all",
    level: "all",
    totalN: 1000,
    rows: [
      { city: "ha_noi", n: 520, value: 0.52, display: "shown" },
      { city: "ho_chi_minh", n: 330, value: 0.33, display: "shown" },
      { city: "da_nang", n: 40, value: 0.04, display: "shown" },
      { city: "bac_ninh", n: 24, value: 0.024, display: "low_sample_shown" },
      { city: "hai_phong", n: 41, value: 0.041, display: "shown" },
      { city: "remote", n: 15, value: 0.015, display: "low_sample_shown" },
      { city: "abroad", n: 20, value: 0.02, display: "low_sample_shown" },
      { city: "unknown", n: 10, value: 0.01, display: "low_sample_shown" },
    ],
  });
}

describe("fr33 #285 — 34 tỉnh, Remote, Nước ngoài", () => {
  it("fr33: thanh là ba thành phố; chú thích là Remote, Nước ngoài, Không xác định", () => {
    expect(BAR_CITIES).toEqual(["ha_noi", "ho_chi_minh", "da_nang"]);
    expect(LEGEND_CITIES).toEqual(["remote", "abroad", "unknown"]);
    const view = buildCitySharesView(envelope());
    expect(view.bars.map((b) => b.city)).toEqual(["ha_noi", "ho_chi_minh", "da_nang"]);
    expect(view.legend.map((l) => l.city)).toEqual(["remote", "abroad", "unknown"]);
  });

  it("fr33: bảng có các tỉnh khác theo số tin giảm dần, giữa ba thành phố và ba dòng chú thích", () => {
    const rows = buildCitySharesView(envelope()).table.rows;
    expect(rows.map((r) => r.city)).toEqual([
      "ha_noi",
      "ho_chi_minh",
      "da_nang",
      "hai_phong",
      "bac_ninh",
      "remote",
      "abroad",
      "unknown",
    ]);
    expect(rows.map((r) => r.label)).toEqual([
      "Hà Nội",
      "TP.HCM",
      "Đà Nẵng",
      "Hải Phòng",
      "Bắc Ninh",
      "Làm từ xa (Remote)",
      "Nước ngoài",
      "Không xác định nơi làm việc",
    ]);
    const bacNinh = rows.find((r) => r.city === "bac_ninh");
    expect(bacNinh?.shareShown).toBe(false);
  });

  it("fr33: mọi mã tỉnh có nhãn tiếng Việt, không trả lại chính mã", () => {
    for (const code of ["hue", "can_tho", "khanh_hoa", "dak_lak", "lam_dong", "ca_mau", "lao_cai"]) {
      expect(cityLabel(code)).not.toBe(code);
    }
  });
});
