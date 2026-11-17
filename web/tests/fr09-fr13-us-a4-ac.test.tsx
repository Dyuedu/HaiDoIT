import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import InsightsPage from "@/app/insights/page";

import { SKILL_ROLES, routeInsights } from "./helpers/skill-roles";

// #170 — mỗi AC của story #113 (US-A4) một test, tên test có mã FR. Chạy trang /insights thật với response của API giả
// (fixture của #166, khóa bằng tests/api/test_ad17_web_fixtures.py). Bảng AC → test ở specs/170-test-vai-tro-dung-ky-nang/spec.md.

const LIST = /Vai trò theo tỷ lệ tin nhắc tới kỹ năng/;

async function openSection(search = "") {
  window.history.replaceState(null, "", `/insights${search}`);
  render(<InsightsPage />);
  return screen.findByRole("region", { name: "Kỹ năng của bạn dùng ở vai trò nào" });
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
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("US-A4 #113 — vai trò nào dùng kỹ năng mình đã có", () => {
  it("AC1 FR-13: gõ kỹ năng bằng tiếng Việt hoặc tiếng Anh khớp một kỹ năng, và màn ghi kỹ năng đó", async () => {
    const user = userEvent.setup();
    const api = routeInsights();
    const area = await openSection();
    await user.type(within(area).getByRole("searchbox", { name: /Tìm kỹ năng/ }), "học máy");
    await user.click(
      within(await within(area).findByRole("list", { name: "Kết quả tìm kỹ năng" })).getByRole("button", {
        name: "Học máy (Machine Learning)",
      }),
    );
    await within(area).findByText("Kỹ năng: Học máy (Machine Learning)");
    expect(api.calls("/api/v1/skill-roles").at(-1)?.params.skill).toBe("machine_learning");
  });

  it("AC2 FR-09 AD-22: mỗi vai trò có tỷ lệ tin entry-level nhắc kỹ năng, theo tỷ lệ, bằng một câu thường", async () => {
    routeInsights();
    const area = await openSection("?skill=python");
    const list = await within(area).findByRole("list", { name: LIST });
    expect(rowOf(list, "AI/ML").textContent).toContain("77,6% tin AI/ML mới vào nghề nhắc tới Python");
    const shown = SKILL_ROLES.python.data.rows.filter((row) => row.share.value !== null).length;
    const percents = within(list)
      .getAllByRole("listitem")
      .slice(0, shown)
      .map((item) => Number((item.textContent?.match(/(\d+),(\d)%/) ?? []).slice(1).join(".")));
    expect(percents).toEqual([...percents].sort((a, b) => b - a));
  });

  it("AC3 FR-09: vai trò dưới 30 tin entry-level ghi chưa đủ dữ liệu (X/30)", async () => {
    routeInsights();
    const area = await openSection("?skill=python");
    const list = await within(area).findByRole("list", { name: LIST });
    expect(rowOf(list, "Kỹ sư dữ liệu").textContent).toContain("chưa đủ dữ liệu (4/30)");
  });

  it("AC4 FR-09: kỹ năng không tin hiện tại nào nhắc thì nói như vậy", async () => {
    routeInsights();
    const area = await openSection("?skill=abap");
    await within(area).findByText("Chưa tin tuyển dụng hiện tại nào nhắc tới ABAP.");
    expect(within(area).queryByRole("list", { name: LIST })).toBeNull();
  });

  it("AC5 FR-18: chạm một vai trò mở hồ sơ kỹ năng của vai trò đó (#111)", async () => {
    routeInsights();
    const area = await openSection("?skill=python");
    const list = await within(area).findByRole("list", { name: LIST });
    expect(within(rowOf(list, "AI/ML")).getByRole("link").getAttribute("href")).toBe(
      "/ho-so-ky-nang?role=ai_ml&level=entry",
    );
  });

  it("FR-09: file này có đúng năm test AC, mỗi tên có một mã FR", () => {
    const source = readFileSync(fileURLToPath(import.meta.url), "utf8");
    const names = [...source.matchAll(/it\("(AC\d[^"]*)"/g)].map((match) => match[1]);
    expect(names.map((name) => name.slice(0, 3))).toEqual(["AC1", "AC2", "AC3", "AC4", "AC5"]);
    for (const name of names) expect(name).toMatch(/FR-\d+/);
  });
});
