import { describe, expect, it } from "vitest";

import {
  buildCitySharesView,
  formatCount,
  formatDate,
  formatPercent,
} from "@/lib/city-shares-view";
import { cityLabel, DEFAULT_ROLE, ROLE_OPTIONS, roleLabel } from "@/lib/labels";

import {
  allLowSampleEnvelope,
  buildEnvelope,
  fakeEnvelope,
  statEnvelope,
} from "./fixtures/envelopes";

const LOW_SAMPLE_21 = "Cỡ mẫu nhỏ (n = 21 < 30): số liệu chỉ để tham khảo";

describe("fr33 — ba thanh thành phố", () => {
  it("fr33: role=all dựng đúng ba thanh Hà Nội, TP.HCM, Đà Nẵng theo share.value", () => {
    const envelope = fakeEnvelope("all");
    const view = buildCitySharesView(envelope);

    expect(view.bars.map((bar) => bar.city)).toEqual(["ha_noi", "ho_chi_minh", "da_nang"]);
    expect(view.bars.map((bar) => bar.label)).toEqual(["Hà Nội", "TP.HCM", "Đà Nẵng"]);
    // Độ rộng lấy nguyên share.value, không co theo giá trị lớn nhất.
    expect(view.bars.map((bar) => bar.value)).toEqual([
      0.4155047406581149, 0.4774121583937535, 0.01784718349135527,
    ]);
    expect(view.bars.map((bar) => bar.percent)).toEqual(["41,6%", "47,7%", "1,8%"]);
    expect(view.bars.map((bar) => bar.nText)).toEqual(["1.490", "1.712", "64"]);
    expect(view.bars.every((bar) => !bar.lowSample && bar.lowSampleNote === null)).toBe(true);
  });

  it("fr33: Remote, Nước ngoài, không xác định không thành thanh mà là ba dòng chú thích; tỉnh khác chỉ ở bảng (#285)", () => {
    const view = buildCitySharesView(fakeEnvelope("ai_ml"));

    expect(view.bars.map((bar) => bar.city)).toEqual(["ha_noi", "ho_chi_minh", "da_nang"]);
    expect(view.legend.map((line) => [line.city, line.label, line.percent, line.nText])).toEqual([
      ["remote", "Làm từ xa (Remote)", "0,0%", "0"],
      ["abroad", "Nước ngoài", "0,0%", "0"],
      ["unknown", "Không xác định nơi làm việc", "7,4%", "65"],
    ]);
    expect(view.legend.map((line) => line.city)).not.toContain("hai_phong");
  });

  it("fr33: Đà Nẵng mẫu nhỏ vẫn có thanh, kèm nhãn mẫu nhỏ đọc n và min_sample từ envelope", () => {
    const view = buildCitySharesView(fakeEnvelope("ai_ml"));
    const daNang = view.bars[2];

    expect(daNang.city).toBe("da_nang");
    expect(daNang.value).toBe(0.02394526795895097);
    expect(daNang.lowSample).toBe(true);
    expect(daNang.lowSampleNote).toBe(LOW_SAMPLE_21);
    expect(daNang.percent).toBe("2,4%");
    expect(view.bars[0].lowSample).toBe(false);
  });

  it("fr33: tên đọc được của mỗi dòng gồm tên nơi, phần trăm, n và câu mẫu nhỏ nếu có", () => {
    const view = buildCitySharesView(fakeEnvelope("ai_ml"));

    expect(view.bars[0].accessibleName).toBe("Hà Nội: 47,0%, 412 tin");
    expect(view.bars[2].accessibleName).toBe(`Đà Nẵng: 2,4%, 21 tin. ${LOW_SAMPLE_21}`);
  });

  it("fr33: backend: Remote, Nước ngoài n = 0 và không xác định n = 8, mỗi dòng chú thích có nhãn mẫu nhỏ", () => {
    const view = buildCitySharesView(fakeEnvelope("backend"));

    expect(view.legend.map((line) => [line.city, line.lowSample, line.lowSampleNote])).toEqual([
      ["remote", true, "Cỡ mẫu nhỏ (n = 0 < 30): số liệu chỉ để tham khảo"],
      ["abroad", true, "Cỡ mẫu nhỏ (n = 0 < 30): số liệu chỉ để tham khảo"],
      ["unknown", true, "Cỡ mẫu nhỏ (n = 8 < 30): số liệu chỉ để tham khảo"],
    ]);
    expect(view.bars[2].lowSampleNote).toBe("Cỡ mẫu nhỏ (n = 9 < 30): số liệu chỉ để tham khảo");
  });

  it("fr33: tỷ trọng 0 với n = 0 vẫn là một thanh, kèm nhãn n = 0 (envelope hình #69)", () => {
    const view = buildCitySharesView(statEnvelope());
    const daNang = view.bars[2];

    expect(daNang.city).toBe("da_nang");
    expect(daNang.value).toBe(0);
    expect(daNang.percent).toBe("0,0%");
    expect(daNang.lowSample).toBe(true);
    expect(daNang.lowSampleNote).toBe("Cỡ mẫu nhỏ (n = 0 < 30): số liệu chỉ để tham khảo");
  });

  it("fr33: năm dòng đều mẫu nhỏ thì mọi thanh và dòng chú thích đều có nhãn, chú thích đủ", () => {
    const view = buildCitySharesView(allLowSampleEnvelope());

    expect([...view.bars, ...view.legend].every((line) => line.lowSample)).toBe(true);
    expect([...view.bars, ...view.legend].every((line) => line.lowSampleNote !== null)).toBe(true);
    expect(view.bars).toHaveLength(3);
    // Envelope hình cũ (trước #285): có `other`, không có Remote/Nước ngoài; chú thích chỉ còn không xác định.
    expect(view.legend.map((line) => line.city)).toEqual(["unknown"]);
    expect(view.caption.notes).toHaveLength(4);
    expect(view.caption.snapshotDate).toBe("07/11/2026");
  });

  it("fr33: trạng thái chỉ đọc từ display, không so n với ngưỡng", () => {
    const envelope = buildEnvelope({
      role: "ai_ml",
      totalN: 200,
      rows: [
        // n nhỏ nhưng máy chủ nói shown; n lớn nhưng máy chủ nói low_sample_shown.
        { city: "ha_noi", n: 10, value: 0.05, display: "shown" },
        { city: "ho_chi_minh", n: 150, value: 0.75, display: "low_sample_shown" },
        { city: "da_nang", n: 20, value: 0.1, display: "low_sample_shown" },
        { city: "other", n: 10, value: 0.05, display: "shown" },
        { city: "unknown", n: 10, value: 0.05, display: "shown" },
      ],
    });
    const view = buildCitySharesView(envelope);

    expect(view.bars.map((bar) => bar.lowSample)).toEqual([false, true, true]);
  });

  it("fr33: nhãn mẫu nhỏ đọc min_sample của envelope, không viết cứng 30", () => {
    const envelope = buildEnvelope({
      role: "ai_ml",
      totalN: 100,
      minSample: 50,
      rows: [
        { city: "ha_noi", n: 60, value: 0.6, display: "shown" },
        { city: "ho_chi_minh", n: 20, value: 0.2, display: "low_sample_shown" },
        { city: "da_nang", n: 10, value: 0.1, display: "low_sample_shown" },
        { city: "other", n: 5, value: 0.05, display: "low_sample_shown" },
        { city: "unknown", n: 5, value: 0.05, display: "low_sample_shown" },
      ],
    });
    const view = buildCitySharesView(envelope);

    expect(view.bars[1].lowSampleNote).toBe("Cỡ mẫu nhỏ (n = 20 < 50): số liệu chỉ để tham khảo");
  });
});

describe("fr33 — bảng", () => {
  it("fr33: bảng có ba thành phố, tỉnh khác, rồi ba dòng chú thích; dòng mẫu nhỏ ghi 'chưa đủ dữ liệu' nhưng vẫn ghi n", () => {
    const view = buildCitySharesView(fakeEnvelope("ai_ml"));

    expect(view.table.rows.map((row) => [row.label, row.share, row.nText])).toEqual([
      ["Hà Nội", "47,0%", "412"],
      ["TP.HCM", "38,0%", "333"],
      ["Đà Nẵng", "chưa đủ dữ liệu", "21"],
      ["Hải Phòng", "5,2%", "46"],
      ["Làm từ xa (Remote)", "chưa đủ dữ liệu", "0"],
      ["Nước ngoài", "chưa đủ dữ liệu", "0"],
      ["Không xác định nơi làm việc", "7,4%", "65"],
    ]);
    expect(view.table.rows.map((row) => row.shareShown)).toEqual([true, true, false, true, false, false, true]);
    expect(view.table.rows[2].note).toBe("Cỡ mẫu nhỏ (n = 21 < 30)");
    expect(view.table.rows[0].note).toBe("");
  });

  it("fr33: backend có Hải Phòng và ba dòng chú thích, đều 'chưa đủ dữ liệu'", () => {
    const view = buildCitySharesView(fakeEnvelope("backend"));

    expect(view.table.rows.slice(3).map((row) => [row.city, row.share, row.nText])).toEqual([
      ["hai_phong", "chưa đủ dữ liệu", "5"],
      ["remote", "chưa đủ dữ liệu", "0"],
      ["abroad", "chưa đủ dữ liệu", "0"],
      ["unknown", "chưa đủ dữ liệu", "8"],
    ]);
  });

  it("fr33: dòng tổng ghi cố định 100% và n của total_cell_id, không cộng các dòng", () => {
    const view = buildCitySharesView(fakeEnvelope("all"));

    // Các dòng làm tròn riêng cộng ra 100,1%; dòng tổng vẫn là 100%.
    expect(view.table.rows.map((row) => row.share)).toEqual([
      "41,6%",
      "47,7%",
      "1,8%",
      "3,2%",
      "chưa đủ dữ liệu",
      "chưa đủ dữ liệu",
      "5,8%",
    ]);
    expect(view.table.total).toEqual({ label: "Tổng", share: "100%", nText: "3.586" });
    expect(view.table.roundingNote).toBe("Tổng các dòng có thể lệch 0,1% do làm tròn.");
  });

  it("fr33: dòng tổng lấy n của total_cell_id kể cả khi các dòng không cộng ra n đó", () => {
    const envelope = fakeEnvelope("ai_ml");
    envelope.meta.cells[envelope.data.total_cell_id].n = 999;

    expect(buildCitySharesView(envelope).table.total.nText).toBe("999");
  });
});

describe("fr33 — định dạng vi-VN", () => {
  it("fr33: phần trăm một chữ số thập phân với dấu phẩy", () => {
    expect(formatPercent(0.4697833523375142)).toBe("47,0%");
    expect(formatPercent(0)).toBe("0,0%");
    expect(formatPercent(1)).toBe("100,0%");
  });

  it("fr33: làm tròn đúng một lần từ giá trị thô", () => {
    // 4,449% làm tròn một lần ra 4,4%; làm tròn hai lần (4,45 rồi 4,5) sẽ sai.
    expect(formatPercent(0.04449)).toBe("4,4%");
  });

  it("fr33: số tin có dấu chấm ngăn nghìn, ngày dd/mm/yyyy", () => {
    expect(formatCount(3586)).toBe("3.586");
    expect(formatCount(0)).toBe("0");
    expect(formatDate("2026-11-03")).toBe("03/11/2026");
    expect(formatDate("2026-01-09")).toBe("09/01/2026");
  });
});

describe("fr33 — chú thích snapshot", () => {
  it("fr33: nguồn in đúng như API gửi, ngày snapshot, bốn câu coverage_notes nguyên văn", () => {
    const envelope = fakeEnvelope("all");
    const view = buildCitySharesView(envelope);

    expect(view.caption.sources).toEqual(envelope.meta.sources);
    expect(view.caption.snapshotDate).toBe("03/11/2026");
    expect(view.caption.notes).toEqual(envelope.meta.coverage_notes);
    expect(view.caption.failedSources).toBeNull();
  });

  it("fr33: snapshot cũ hiện đúng ngày của snapshot đó", () => {
    const envelope = fakeEnvelope("all");
    envelope.meta.snapshot_date = "2026-10-28";

    expect(buildCitySharesView(envelope).caption.snapshotDate).toBe("28/10/2026");
  });

  it("fr33: snapshot partial ghi 'Nguồn lỗi ở snapshot này: …' với sources_failed", () => {
    const envelope = fakeEnvelope("all");
    envelope.meta.snapshot_status = "partial";
    envelope.meta.sources_failed = ["topdev", "itviec"];

    expect(buildCitySharesView(envelope).caption.failedSources).toBe(
      "Nguồn lỗi ở snapshot này: topdev, itviec",
    );
  });

  it("fr33: snapshot partial mà sources_failed rỗng thì không ghi câu nguồn lỗi", () => {
    const envelope = fakeEnvelope("all");
    envelope.meta.snapshot_status = "partial";
    envelope.meta.sources_failed = [];

    expect(buildCitySharesView(envelope).caption.failedSources).toBeNull();
  });
});

describe("fr33 — nhãn từ labels.ts", () => {
  it("fr33: chip vai trò là all cộng các vai trò trong config/rules.toml, mặc định là all", () => {
    expect(ROLE_OPTIONS).toEqual([
      { code: "all", label: "Tất cả" },
      { code: "embedded", label: "Nhúng" },
      { code: "ai_ml", label: "AI/ML" },
      { code: "data_scientist", label: "Khoa học dữ liệu" },
      { code: "data_engineer", label: "Kỹ sư dữ liệu" },
      { code: "data_analyst", label: "Phân tích dữ liệu" },
      { code: "qa", label: "Kiểm thử (QA)" },
      { code: "devops", label: "DevOps" },
      { code: "security", label: "Bảo mật" },
      { code: "it_infra", label: "Hạ tầng & IT support" },
      { code: "mobile", label: "Mobile" },
      { code: "frontend", label: "Frontend" },
      { code: "backend", label: "Backend" },
      { code: "fullstack", label: "Fullstack" },
      { code: "ba_po_pm", label: "BA / PO / PM" },
      { code: "ui_ux", label: "UI/UX" },
      { code: "game", label: "Phát triển game" },
      { code: "other", label: "Vai trò khác" },
    ]);
    expect(DEFAULT_ROLE).toBe("all");
    expect(roleLabel("ai_ml")).toBe("AI/ML");
    expect(roleLabel("other")).toBe("Vai trò khác");
    expect(cityLabel("ho_chi_minh")).toBe("TP.HCM");
  });

  it("fr33: mã không có trong labels.ts thì hiện chính mã đó", () => {
    expect(roleLabel("khong_co_vai_tro")).toBe("khong_co_vai_tro");
    expect(cityLabel("khong_co_noi")).toBe("khong_co_noi");  // #285: hai_phong nay có nhãn

    const envelope = buildEnvelope({
      role: "khong_co_vai_tro",
      totalN: 100,
      rows: [
        { city: "ha_noi", n: 40, value: 0.4, display: "shown" },
        { city: "ho_chi_minh", n: 30, value: 0.3, display: "shown" },
        { city: "da_nang", n: 10, value: 0.1, display: "low_sample_shown" },
        { city: "khong_co_noi", n: 10, value: 0.1, display: "low_sample_shown" },
        { city: "other", n: 5, value: 0.05, display: "low_sample_shown" },
        { city: "unknown", n: 5, value: 0.05, display: "low_sample_shown" },
      ],
    });
    const view = buildCitySharesView(envelope);

    expect(view.roleLabel).toBe("khong_co_vai_tro");
    expect(view.bars.map((bar) => bar.city)).toEqual(["ha_noi", "ho_chi_minh", "da_nang"]);
    // #285: mã lạ và `other` của snapshot cũ không thành thanh hay chú thích; chúng ở bảng, nhãn là chính mã hoặc "Khác".
    expect(view.legend.map((line) => line.label)).toEqual(["Không xác định nơi làm việc"]);
    const labels = view.table.rows.map((row) => row.label);
    expect(labels).toContain("khong_co_noi");
    expect(labels).toContain("Khác");
  });
});

describe("fr33 #163 — nhãn cấp bậc trên view", () => {
  it("fr33: view mang cấp bậc và nhãn tiếng Việt của envelope", () => {
    const entryView = buildCitySharesView(fakeEnvelope("ai_ml", "entry"));
    expect([entryView.level, entryView.levelLabel]).toEqual(["entry", "Mới vào nghề"]);

    const allView = buildCitySharesView(fakeEnvelope("ai_ml"));
    expect([allView.level, allView.levelLabel]).toEqual(["all", "Mọi cấp bậc"]);
  });

  it("fr33: n của từng thành phố là n của ô ở cấp đã chọn, thanh nhỏ ở entry khác ở mọi cấp", () => {
    const entryView = buildCitySharesView(fakeEnvelope("ai_ml", "entry"));
    const allView = buildCitySharesView(fakeEnvelope("ai_ml"));

    expect(entryView.bars.map((bar) => bar.nText)).toEqual(["241", "188", "11"]);
    expect(allView.bars.map((bar) => bar.nText)).toEqual(["412", "333", "21"]);
    expect(entryView.table.total.nText).toBe("501");
    expect(entryView.bars[2].lowSampleNote).toBe("Cỡ mẫu nhỏ (n = 11 < 30): số liệu chỉ để tham khảo");
  });
});
