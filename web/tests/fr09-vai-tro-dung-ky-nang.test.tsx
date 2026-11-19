import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import InsightsPage from "@/app/insights/page";
import type { SkillRolesEnvelope } from "@/lib/skill-roles";

import { jsonResponse } from "./helpers/fetch";
import { SKILL_ROLES, UNKNOWN_SKILL_CELL, routeInsights } from "./helpers/skill-roles";

// #169 — mục "Kỹ năng của bạn dùng ở vai trò nào" trên /insights, dựng từ response của API giả (#166). Thứ tự dòng do
// API quyết, web không tính (AD-22). Số đứng ở ô riêng, câu không có chữ số (DEC-6).

const LIST = /Vai trò theo tỷ lệ tin nhắc tới kỹ năng/;

function openWithSkill(skill: string) {
  window.history.replaceState(null, "", `/insights?skill=${skill}`);
  return render(<InsightsPage />);
}

function clone(skill: keyof typeof SKILL_ROLES): SkillRolesEnvelope {
  return structuredClone(SKILL_ROLES[skill]) as unknown as SkillRolesEnvelope;
}

function rowOf(list: HTMLElement, label: string): HTMLElement {
  const row = within(list)
    .getAllByRole("listitem")
    .find((item) => within(item).queryByText(label, { exact: true }));
  if (!row) throw new Error(`Không có dòng ${label}`);
  return row;
}

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/insights");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fr09 #169 — vai trò nào dùng một kỹ năng", () => {
  it("fr09: mỗi vai trò một dòng, đúng thứ tự API gửi", async () => {
    routeInsights();
    openWithSkill("python");
    const list = await screen.findByRole("list", { name: LIST });
    const items = within(list).getAllByRole("listitem");
    expect(items).toHaveLength(SKILL_ROLES.python.data.rows.length);
    expect(within(items[0]).getByText("AI/ML", { exact: true })).toBeTruthy();
    expect(within(items[1]).getByText("Phân tích dữ liệu", { exact: true })).toBeTruthy();
  });

  it("fr09 ad22: web không sắp lại, kể cả khi API gửi thứ tự khác", async () => {
    const env = clone("python");
    env.data.rows.reverse();
    routeInsights({ skillRoles: () => jsonResponse(200, env) });
    openWithSkill("python");
    const items = within(await screen.findByRole("list", { name: LIST })).getAllByRole("listitem");
    expect(within(items[items.length - 1]).getByText("AI/ML", { exact: true })).toBeTruthy();
  });

  it("fr09: dòng có tỷ lệ ghi tỷ lệ ở ô số, câu thường, và n là cỡ mẫu của phép đo", async () => {
    routeInsights();
    openWithSkill("python");
    const row = rowOf(await screen.findByRole("list", { name: LIST }), "AI/ML");
    expect(row.textContent).toContain("77,6%");
    expect(row.textContent).toContain("tin AI/ML mới vào nghề nhắc tới Python");
    expect(row.textContent).toContain("n = 501");
  });

  it("fr09: vai trò dưới ngưỡng ghi chưa đủ dữ liệu (X/30), X là skill_count, không có %", async () => {
    routeInsights();
    openWithSkill("python");
    const row = rowOf(await screen.findByRole("list", { name: LIST }), "Kỹ sư dữ liệu");
    expect(row.textContent).toContain("chưa đủ dữ liệu (4/30)");
    expect(row.textContent).not.toContain("%");
  });

  it("fr09: ngưỡng lấy từ meta.thresholds.min_sample", async () => {
    const env = clone("python");
    env.meta.thresholds.min_sample = 50;
    routeInsights({ skillRoles: () => jsonResponse(200, env) });
    openWithSkill("python");
    const row = rowOf(await screen.findByRole("list", { name: LIST }), "Kỹ sư dữ liệu");
    expect(row.textContent).toContain("chưa đủ dữ liệu (4/50)");
  });

  it("fr18: chạm một vai trò mở hồ sơ kỹ năng của vai trò đó ở cấp data.level", async () => {
    routeInsights();
    openWithSkill("python");
    const row = rowOf(await screen.findByRole("list", { name: LIST }), "AI/ML");
    expect(within(row).getByRole("link").getAttribute("href")).toBe("/ho-so-ky-nang?role=ai_ml&level=entry");
  });

  it("fr09: khung Nguồn và lưu ý có ngày, nguồn, lưu ý và bộ lọc mới vào nghề", async () => {
    routeInsights();
    openWithSkill("python");
    await screen.findByRole("list", { name: LIST });
    const regions = screen.getAllByRole("region", { name: "Nguồn và lưu ý" });
    const caption = regions[regions.length - 1];
    expect(caption.textContent).toContain("03/11/2026");
    expect(caption.textContent).toContain("Mới vào nghề");
    for (const note of SKILL_ROLES.python.meta.coverage_notes) expect(caption.textContent).toContain(note.text);
  });

  it("fr09: unknown_cell thì có thông báo, không có Thử lại, không có danh sách", async () => {
    routeInsights();
    openWithSkill("java");
    await screen.findByText(UNKNOWN_SKILL_CELL.error.message);
    expect(screen.queryByRole("button", { name: "Thử lại" })).toBeNull();
    expect(screen.queryByRole("list", { name: LIST })).toBeNull();
  });

  it("fr09: mạng hỏng thì báo không đọc được, Thử lại tải lại được", async () => {
    const user = userEvent.setup();
    let broken = true;
    routeInsights({
      skillRoles: () => (broken ? Promise.reject(new TypeError("offline")) : jsonResponse(200, SKILL_ROLES.python)),
    });
    openWithSkill("python");
    const section = await screen.findByRole("region", { name: "Kỹ năng của bạn dùng ở vai trò nào" });
    await within(section).findByText(/Không đọc được số liệu/);
    broken = false;
    await user.click(within(section).getByRole("button", { name: "Thử lại" }));
    await screen.findByRole("list", { name: LIST });
  });

  it("fr09 ad8: câu của mục (tiêu đề, đoạn văn) không có chữ số ngoài ô số", async () => {
    routeInsights();
    openWithSkill("python");
    await screen.findByRole("list", { name: LIST });
    const section = screen.getByRole("region", { name: "Kỹ năng của bạn dùng ở vai trò nào" });
    for (const node of section.querySelectorAll("h2, h3, p")) {
      if (node.closest("ol") || node.closest("[aria-label='Nguồn và lưu ý'], section section")) continue;
      expect(node.textContent ?? "").not.toMatch(/\d/);
    }
  });
});
