import { render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SnapshotCaption } from "@/app/components/map/snapshot-caption";
import InsightsPage from "@/app/insights/page";
import MapPage from "@/app/page";
import { buildCitySharesView, notEnoughText } from "@/lib/city-shares-view";
import { buildNewcomerView } from "@/lib/newcomer-roles-view";
import type { NewcomerRolesEnvelope } from "@/lib/newcomer-roles";
import { buildSkillProfileView } from "@/lib/skill-profile-view";
import type { SkillRatesEnvelope } from "@/lib/skill-rates";
import type { SkillRolesEnvelope } from "@/lib/skill-roles";
import { buildSkillRolesView } from "@/lib/skill-roles-view";
import { sourceLabel } from "@/lib/source-labels";

import { buildEnvelope, fakeEnvelope } from "./fixtures/envelopes";
import newcomerJson from "./fixtures/newcomer-roles.json";
import { jsonResponse, routeCityShares } from "./helpers/fetch";
import { SKILL_RATES } from "./helpers/skill-profile";
import { SKILL_ROLES, routeInsights } from "./helpers/skill-roles";

// #324 — chữ trên màn viết bằng tiếng Việt dễ hiểu: không còn ký hiệu `n`, "snapshot", "entry-level"; số giữ nguyên.

const DEV_WORDS = /n = |snapshot|entry-level/i;
const newcomer = newcomerJson as unknown as NewcomerRolesEnvelope;

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.replaceState(null, "", "/");
});

/** Mọi chuỗi trong view, trừ chữ do API gửi nguyên văn (coverage_notes, fallback_label) và mã. */
function texts(value: unknown, skip = new Set(["notes", "fallbackText", "sources", "href", "pathHref"])): string[] {
  if (typeof value === "string") return [value];
  if (Array.isArray(value)) return value.flatMap((item) => texts(item, skip));
  if (value && typeof value === "object") {
    return Object.entries(value).flatMap(([key, item]) => (skip.has(key) ? [] : texts(item, skip)));
  }
  return [];
}

describe("fr36 #324 — câu thiếu mẫu", () => {
  it("fr36: 0 tin thì 'Chưa có tin nào'; còn lại nói có bao nhiêu và cần bao nhiêu", () => {
    expect(notEnoughText(0, 30)).toBe("Chưa có tin nào");
    expect(notEnoughText(12, 30)).toBe("Mới có 12 tin, cần ít nhất 30");
    expect(notEnoughText(1234, 2000)).toBe("Mới có 1.234 tin, cần ít nhất 2.000");
  });
});

describe("fr36 #324 — tầng view không còn chữ kỹ thuật", () => {
  it("fr36: bản đồ, người mới, kỹ năng theo vai trò, hồ sơ kỹ năng", () => {
    const views = [
      buildCitySharesView(fakeEnvelope("all")),
      buildCitySharesView(fakeEnvelope("ai_ml", "entry")),
      buildNewcomerView(newcomer),
      buildSkillRolesView(SKILL_ROLES.python as unknown as SkillRolesEnvelope),
      buildSkillRolesView(SKILL_ROLES.abap as unknown as SkillRolesEnvelope),
      buildSkillProfileView(SKILL_RATES["backend|intern"] as unknown as SkillRatesEnvelope, (code) => code),
    ];
    for (const view of views) {
      const bad = texts(view).filter((text) => DEV_WORDS.test(text));
      expect(bad).toEqual([]);
    }
  });

  it("fr36: dòng người mới ghi 'X trên N tin dành cho người mới'", () => {
    const view = buildNewcomerView(newcomer);
    const row = newcomer.data.rows[0];
    const entry = newcomer.meta.cells[row.entry_cell_id].n;
    const n = newcomer.meta.cells[row.total_cell_id].n;
    expect(view.lines[0].entryText).toBe(
      `${entry.toLocaleString("vi-VN")} trên ${n.toLocaleString("vi-VN")} tin dành cho người mới`,
    );
  });

  it("fr36: kỹ năng theo vai trò ghi 'cho người mới có nhắc tới' và 'tính trên N tin'", () => {
    const view = buildSkillRolesView(SKILL_ROLES.python as unknown as SkillRolesEnvelope);
    const aiml = view.lines.find((line) => line.role === "ai_ml")!;
    expect(aiml.sentence).toBe("tin AI/ML cho người mới có nhắc tới Python");
    expect(aiml.nText).toBe("tính trên 501 tin");
    const abap = buildSkillRolesView(SKILL_ROLES.abap as unknown as SkillRolesEnvelope);
    expect(abap.notMentionedText).toBe("Hiện chưa tin tuyển dụng nào nhắc tới ABAP.");
  });

  it("fr36: hồ sơ kỹ năng quay về ô rộng ghi 'Tính trên N tin'", () => {
    const view = buildSkillProfileView(SKILL_RATES["backend|intern"] as unknown as SkillRatesEnvelope, (code) => code);
    expect(view.nText).toBe("Tính trên 157 tin");
  });
});

describe("fr36 #324 — khung nguồn và tiêu đề bản đồ", () => {
  it("fr36: 'Đang xem', 'Nguồn', 'Cập nhật', tên nguồn viết như trang đó viết", () => {
    const envelope = buildEnvelope({
      role: "all",
      level: "entry",
      snapshotStatus: "partial",
      sourcesFailed: ["topdev"],
      totalN: 200,
      rows: [{ city: "ha_noi", value: 0.5, n: 100, display: "shown" }],
    });
    const view = buildCitySharesView(envelope);
    render(<SnapshotCaption caption={view.caption} />);
    const box = screen.getByRole("region", { name: "Nguồn và lưu ý" });
    for (const label of ["Đang xem", "Nguồn", "Cập nhật"]) expect(within(box).getByText(label)).toBeTruthy();
    expect(box.textContent).toContain(envelope.meta.sources.map(sourceLabel).join(", "));
    expect(box.textContent).toContain("Lần cập nhật này chưa lấy đủ tin từ TopDev");
    expect(view.caption.filters).toBe("Mọi vai trò, mới vào nghề, mọi số năm kinh nghiệm");
  });

  it("fr36: tên nguồn đúng chữ của từng trang; mã lạ in nguyên", () => {
    expect(["careerlink", "itnavi", "itviec", "momo", "topcv", "topdev", "vietnamworks", "zalo"].map(sourceLabel)).toEqual([
      "CareerLink", "ITnavi", "ITviec", "MoMo Careers", "TopCV", "TopDev", "VietnamWorks", "Zalo Careers",
    ]);
    expect(sourceLabel("newsite")).toBe("newsite");
  });

  it("fr36: tiêu đề bản đồ 'N tin <vai trò> · <cấp>, <số năm>'; mọi vai trò là 'tin IT'", () => {
    const all = buildCitySharesView(fakeEnvelope("all"));
    expect(all.title).toBe(`${all.table.total.nText} tin IT · mọi cấp bậc, mọi số năm kinh nghiệm`);
    const aiml = buildCitySharesView(fakeEnvelope("ai_ml", "entry"));
    expect(aiml.title).toBe(`${aiml.table.total.nText} tin AI/ML · mới vào nghề, mọi số năm kinh nghiệm`);
  });
});

describe("fr36 #324 — chữ trên màn", () => {
  it("fr36: Bản đồ không hiện 'n = ', 'snapshot', 'entry-level'", async () => {
    const envelope = fakeEnvelope("all");
    routeCityShares({ all: [() => jsonResponse(200, envelope)] });
    render(<MapPage />);
    await screen.findByRole("region", { name: "Nguồn và lưu ý" });
    expect(document.body.textContent).not.toMatch(DEV_WORDS);
    expect(document.body.textContent).toContain("kèm số tin, nguồn và ngày cập nhật");
  });

  it("fr36: Insights không hiện 'n = ', 'snapshot', 'entry-level'", async () => {
    routeInsights();
    window.history.replaceState(null, "", "/insights?skill=python");
    render(<InsightsPage />);
    await screen.findByRole("list", { name: /Vai trò theo số tin cho người mới/ });
    await screen.findByRole("list", { name: /Vai trò theo tỷ lệ tin nhắc tới kỹ năng/ });
    expect(document.body.textContent).not.toMatch(DEV_WORDS);
  });
});
