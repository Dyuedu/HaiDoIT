import { render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import InsightsPage from "@/app/insights/page";
import { roleLabel } from "@/lib/labels";
import type { MarketOverviewEnvelope } from "@/lib/market-overview";
import type { NewcomerRolesEnvelope } from "@/lib/newcomer-roles";

import overviewJson from "./fixtures/market-overview.json";
import newcomerJson from "./fixtures/newcomer-roles.json";
import { jsonResponse } from "./helpers/fetch";
import { SKILL_ROLES, routeInsights } from "./helpers/skill-roles";

// #330 (story #326) — danh sách người mới (#110) và kỹ năng theo vai trò (#113) thành biểu đồ, cùng số, cùng thứ tự,
// cùng luật ẩn số; cơ cấu cấp bậc từng vai trò lấy tỷ lệ từ market-overview (AD-22).

const newcomer = newcomerJson as unknown as NewcomerRolesEnvelope;
const overview = overviewJson as unknown as MarketOverviewEnvelope;
const NEWCOMER = /Vai trò theo số tin cho người mới/;
const SKILL_LIST = /Vai trò theo tỷ lệ tin nhắc tới kỹ năng/;

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.replaceState(null, "", "/");
});

function open(options: Parameters<typeof routeInsights>[0] = {}, skill = "python") {
  routeInsights(options);
  window.history.replaceState(null, "", `/insights?skill=${skill}`);
  return render(<InsightsPage />);
}

function width(el: Element): number {
  return Number.parseFloat((el as HTMLElement).style.width);
}

describe("#330 — người mới thành biểu đồ thanh", () => {
  it("US-A11 fr37: dòng có tỷ lệ có thanh dài theo tỷ lệ API gửi; dòng chưa đủ dữ liệu không có thanh", async () => {
    open();
    const items = within(await screen.findByRole("list", { name: NEWCOMER })).getAllByRole("listitem");
    const top = Math.max(...newcomer.data.rows.map((r) => r.share.value ?? 0));
    newcomer.data.rows.forEach((row, i) => {
      const bar = items[i].querySelector("[data-part='share-bar']");
      if (row.share.display === "shown") {
        expect(width(bar!)).toBeCloseTo(((row.share.value as number) / top) * 100, 1);
      } else {
        expect(bar).toBeNull();
      }
    });
  });

  it("US-A11 fr37: có bảng số với mọi vai trò, và dòng vẫn mở hồ sơ kỹ năng", async () => {
    open();
    const section = screen.getByRole("region", { name: "Cửa vào cho người mới" });
    const list = await within(section).findByRole("list", { name: NEWCOMER });
    expect(within(list).getAllByRole("link")[0].getAttribute("href")).toContain("/ho-so-ky-nang?role=");
    const table = within(section).getByRole("table", { name: "Tỷ lệ tin cho người mới theo vai trò" });
    expect(within(table).getAllByRole("row")).toHaveLength(newcomer.data.rows.length + 1);
  });

  it("US-A11 AD-22: cơ cấu cấp bậc theo thứ tự danh sách người mới, mỗi đoạn dài đúng tỷ lệ cấp của API", async () => {
    open({ marketOverview: () => jsonResponse(200, overview) });
    const mix = await screen.findByRole("list", { name: "Cơ cấu cấp bậc của từng vai trò" });
    const items = within(mix).getAllByRole("listitem");
    expect(items.map((li) => li.querySelector("[data-part='label']")?.textContent)).toEqual(
      newcomer.data.rows.map((r) => roleLabel(r.role)),
    );
    const ai = overview.data.roles.find((r) => r.role === "ai_ml")!;
    const segments = [...items[0].querySelectorAll("[data-part='segment']")];
    const shown = ai.level_mix.filter((s) => (s.share.value ?? 0) > 0);
    expect(segments).toHaveLength(shown.length);
    segments.forEach((seg, i) => expect(width(seg)).toBeCloseTo((shown[i].share.value as number) * 100, 1));
  });

  it("US-A11: vai trò mà API ẩn tỷ lệ cấp thì dòng cơ cấu ghi chưa đủ dữ liệu, không có đoạn nào", async () => {
    open({ marketOverview: () => jsonResponse(200, overview) });
    const items = within(await screen.findByRole("list", { name: "Cơ cấu cấp bậc của từng vai trò" })).getAllByRole("listitem");
    const embedded = items.find((li) => li.textContent?.includes("Nhúng"))!;
    expect(embedded.querySelectorAll("[data-part='segment']")).toHaveLength(0);
    expect(embedded.textContent).toContain("chưa đủ dữ liệu");
  });

  it("US-A11: market-overview lỗi thì danh sách người mới vẫn hiện, chỉ thiếu cơ cấu cấp bậc", async () => {
    open({ marketOverview: () => jsonResponse(500, { error: { code: "internal_error", message: "x", snapshot_date: null } }) });
    expect(await screen.findByRole("list", { name: NEWCOMER })).toBeTruthy();
    expect(screen.queryByRole("list", { name: "Cơ cấu cấp bậc của từng vai trò" })).toBeNull();
  });
});

describe("#330 — kỹ năng theo vai trò thành biểu đồ lollipop", () => {
  it("US-A11 fr09: chấm đứng ở đúng tỷ lệ API gửi trên trục 0–100%; dòng chưa đủ dữ liệu không có chấm", async () => {
    open();
    const items = within(await screen.findByRole("list", { name: SKILL_LIST })).getAllByRole("listitem");
    SKILL_ROLES.python.data.rows.forEach((row, i) => {
      const dot = items[i].querySelector("[data-part='share-dot']") as HTMLElement | null;
      if (row.share.value !== null) {
        expect(Number.parseFloat(dot!.style.left)).toBeCloseTo(row.share.value * 100, 1);
      } else {
        expect(dot).toBeNull();
      }
    });
  });

  it("US-A11 fr09: có bảng số với mọi vai trò", async () => {
    open();
    await screen.findByRole("list", { name: SKILL_LIST });
    const table = screen.getByRole("table", { name: "Tỷ lệ tin cho người mới nhắc tới kỹ năng, theo vai trò" });
    expect(within(table).getAllByRole("row")).toHaveLength(SKILL_ROLES.python.data.rows.length + 1);
  });
});
