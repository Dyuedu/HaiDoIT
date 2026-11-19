import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import SkillProfilePage from "@/app/ho-so-ky-nang/page";
import { NOT_ENOUGH_DATA } from "@/lib/city-shares-view";
import { writeProfile } from "@/lib/haido-keys";

import { SKILL_RATES, routeSkillProfile, titleReply } from "./helpers/skill-profile";

// #154 — mỗi AC của story #111 (US-A2) một test, tên test có mã FR mà nó giữ. Test chạy màn thật với response của
// API giả (fixture khóa bằng tests/api/test_ad17_web_fixtures.py). Bảng AC → test ở specs/154-test-ho-so-ky-nang/spec.md.

const PROFILE_LIST = /Kỹ năng theo tỷ lệ tin yêu cầu/;

async function openProfile(params: Record<string, string> = {}) {
  return render(await SkillProfilePage({ searchParams: Promise.resolve(params) }));
}

function rowOf(list: HTMLElement, text: string): HTMLElement {
  const row = within(list)
    .getAllByRole("listitem")
    .find((item) => item.textContent?.includes(text));
  if (!row) throw new Error(`Không có dòng ${text}`);
  return row;
}

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/ho-so-ky-nang");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("US-A2 #111 — hồ sơ kỹ năng của một vai trò ở cấp của mình", () => {
  it("AC1 FR-18: chức danh gõ vào thành một vai trò, màn ghi vai trò đã dùng, và chọn được vai trò khác", async () => {
    const user = userEvent.setup();
    const api = routeSkillProfile({ roleForTitle: () => titleReply("matched", "backend") });
    await openProfile();
    await user.type(screen.getByRole("textbox", { name: /Chức danh bạn muốn ứng tuyển/ }), "Lập trình viên Java");
    await user.click(screen.getByRole("button", { name: "Tìm vai trò" }));
    await screen.findByText(/Hải Đồ dùng vai trò Backend/);
    await screen.findByRole("list", { name: PROFILE_LIST });

    await user.selectOptions(screen.getByRole("combobox", { name: "Vai trò" }), "frontend");
    await waitFor(() => expect(api.calls("/api/v1/skill-rates").at(-1)?.params.role).toBe("frontend"));
  });

  it("AC2 FR-18: chức danh không khớp vai trò IT nào thì nói rõ, đưa danh sách vai trò, không hiện số", async () => {
    const user = userEvent.setup();
    routeSkillProfile({ roleForTitle: () => titleReply("not_it") });
    const view = await openProfile();
    await user.type(screen.getByRole("textbox", { name: /Chức danh bạn muốn ứng tuyển/ }), "Kế toán");
    await user.click(screen.getByRole("button", { name: "Tìm vai trò" }));
    await screen.findByText(/không khớp vai trò IT nào/);
    expect(within(screen.getByRole("list", { name: "Danh sách vai trò" })).getAllByRole("button").length).toBeGreaterThan(1);
    expect(screen.queryByRole("list", { name: PROFILE_LIST })).toBeNull();
    expect(view.container.textContent ?? "").not.toMatch(/\d/);
  });

  it("AC3 FR-18: không chọn cấp thì dùng cấp mặc định của #134, và đổi được cấp", async () => {
    const user = userEvent.setup();
    const api = routeSkillProfile();
    await openProfile({ role: "backend" });
    await screen.findByRole("list", { name: PROFILE_LIST });
    expect((screen.getByRole("combobox", { name: "Cấp bậc" }) as HTMLSelectElement).value).toBe("entry");
    await user.selectOptions(screen.getByRole("combobox", { name: "Cấp bậc" }), "intern");
    await waitFor(() => expect(api.calls("/api/v1/skill-rates").at(-1)?.params.level).toBe("intern"));
  });

  it("AC4 FR-19: từ 30 tin trở lên, mỗi kỹ năng có tỷ lệ và nhóm, theo thứ tự tỷ lệ", async () => {
    routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    const items = within(await screen.findByRole("list", { name: PROFILE_LIST })).getAllByRole("listitem");
    const apiRows = SKILL_RATES["backend|entry"].data.rows;
    expect(items).toHaveLength(apiRows.length);
    expect(items[0].textContent).toMatch(/Java.*65,4%.*Cốt lõi/);
    const shown = items.map((item) => Number((item.textContent?.match(/(\d+),(\d)%/) ?? []).slice(1).join(".")));
    expect(shown).toEqual([...shown].sort((a, b) => b - a));
  });

  it("AC5 FR-19: dưới 30 tin thì gọi tên ô rộng hơn và n của nó; không ô nào đủ thì ghi chưa đủ dữ liệu", async () => {
    routeSkillProfile();
    const wider = await openProfile({ role: "backend", level: "intern" });
    await screen.findByRole("list", { name: PROFILE_LIST });
    expect(screen.getByText(SKILL_RATES["backend|intern"].meta.cells["vn.backend"].fallback_label)).toBeTruthy();
    expect(screen.getByText("Tính trên 157 tin")).toBeTruthy();
    wider.unmount();

    await openProfile({ role: "data_engineer", level: "entry" });
    const items = within(await screen.findByRole("list", { name: PROFILE_LIST })).getAllByRole("listitem");
    expect(items.every((item) => item.textContent?.includes(NOT_ENOUGH_DATA))).toBe(true);
    expect(items.some((item) => item.textContent?.includes("%"))).toBe(false);
  });

  it("AC6 FR-14 AD-22: kỹ năng đã lưu được tick, và dòng đếm ghi số kỹ năng cốt lõi người dùng đã có", async () => {
    writeProfile({ v: 1, role: null, level: null, skills: ["java", "sql", "git"] });
    routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    await screen.findByRole("list", { name: PROFILE_LIST });
    for (const name of ["Java", "SQL", "Git"]) {
      await waitFor(() =>
        expect((screen.getByRole("checkbox", { name: new RegExp(`^Đã có ${name}$`) }) as HTMLInputElement).checked).toBe(true),
      );
    }
    await waitFor(() => expect(screen.getByTestId("core-count").textContent).toContain("3/6"));
  });

  it("AC7 FR-22: chạm một kỹ năng chưa có thì mở lộ trình học ở đúng kỹ năng đó", async () => {
    routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    const list = await screen.findByRole("list", { name: PROFILE_LIST });
    const link = within(rowOf(list, "Spring Boot")).getByRole("link", { name: /Spring Boot/ });
    expect(link.getAttribute("href")).toBe("/co-van?role=backend&level=entry&skill=spring_boot");
  });

  it("FR-18: file này có đúng bảy test AC, mỗi tên có một mã FR", () => {
    const source = readFileSync(fileURLToPath(import.meta.url), "utf8");
    const names = [...source.matchAll(/it\("(AC\d[^"]*)"/g)].map((match) => match[1]);
    expect(names.map((name) => name.slice(0, 3))).toEqual(["AC1", "AC2", "AC3", "AC4", "AC5", "AC6", "AC7"]);
    for (const name of names) expect(name).toMatch(/FR-\d+/);
  });
});
