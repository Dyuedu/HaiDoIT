import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import AdvisoryPage from "@/app/co-van/page";
import SkillProfilePage from "@/app/ho-so-ky-nang/page";
import { writeProfile } from "@/lib/haido-keys";
import { learningPathHref } from "@/lib/skill-profile-view";

import { routeSkillProfile } from "./helpers/skill-profile";

// #153 — chạm một kỹ năng chưa có mở lộ trình học (#121) ở đúng kỹ năng đó. Màn lộ trình có ở Sprint 4; tới khi đó
// `/co-van` là trang giữ chỗ gọi tên vai trò, cấp và kỹ năng.

async function openProfile(params: Record<string, string>) {
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

describe("fr22 #153 — liên kết từ kỹ năng chưa có", () => {
  it("fr22: learningPathHref dựng đường dẫn có vai trò, cấp, kỹ năng", () => {
    expect(learningPathHref("backend", "entry", "spring_boot")).toBe(
      "/co-van?role=backend&level=entry&skill=spring_boot",
    );
  });

  it("fr22: dòng chưa tick có liên kết tới lộ trình ở kỹ năng đó; dòng đã tick ghi Đã có, không có liên kết", async () => {
    writeProfile({ v: 1, role: null, level: null, skills: ["java"] });
    routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    const list = await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });

    const spring = within(rowOf(list, "Spring Boot")).getByRole("link", { name: /Spring Boot/ });
    expect(spring.getAttribute("href")).toBe("/co-van?role=backend&level=entry&skill=spring_boot");

    const java = rowOf(list, "Java");
    expect(within(java).queryByRole("link")).toBeNull();
    expect(java.textContent).toContain("Đã có");
  });

  it("fr22: tick một kỹ năng thì liên kết lộ trình của nó biến mất, bỏ tick thì trở lại", async () => {
    const user = userEvent.setup();
    routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    const list = await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });

    await user.click(within(rowOf(list, "Spring Boot")).getByRole("checkbox"));
    expect(within(rowOf(list, "Spring Boot")).queryByRole("link")).toBeNull();
    await user.click(within(rowOf(list, "Spring Boot")).getByRole("checkbox"));
    expect(within(rowOf(list, "Spring Boot")).getByRole("link")).toBeTruthy();
  });
});

describe("fr22 #153 — trang giữ chỗ /co-van", () => {
  async function openAdvisory(params: Record<string, string>) {
    return render(await AdvisoryPage({ searchParams: Promise.resolve(params) }));
  }

  it("fr22: gọi tên vai trò, cấp và kỹ năng, nói lộ trình có ở sprint sau, có nút quay lại hồ sơ", async () => {
    routeSkillProfile();
    await openAdvisory({ role: "backend", level: "entry", skill: "spring_boot" });
    expect(screen.getByRole("heading", { level: 1 }).textContent).toContain("Backend");
    await screen.findByText(/Spring Boot/);
    expect(screen.getByText(/Mới vào nghề/)).toBeTruthy();
    expect(screen.getByText(/sprint sau/)).toBeTruthy();
    expect(screen.getByRole("link", { name: /Quay lại hồ sơ kỹ năng/ }).getAttribute("href")).toBe(
      "/ho-so-ky-nang?role=backend&level=entry",
    );
  });

  it("fr22: mã vai trò hay kỹ năng lạ thì không in mã như một tên", async () => {
    routeSkillProfile();
    const { container } = await openAdvisory({ role: "khong_co", level: "entry", skill: "khong_co_ky_nang" });
    await screen.findByRole("heading", { level: 1 });
    expect(container.textContent).not.toContain("khong_co");
  });

  it("fr22 ad8: câu của trang giữ chỗ không có chữ số (DEC-6)", async () => {
    routeSkillProfile();
    const { container } = await openAdvisory({ role: "backend", level: "entry", skill: "spring_boot" });
    await screen.findByText(/Spring Boot/);
    for (const node of container.querySelectorAll("h1, h2, p, a")) {
      expect(node.textContent ?? "").not.toMatch(/\d/);
    }
  });

  it("fr22: không có tham số thì giữ câu giới thiệu chung của Cố vấn", async () => {
    routeSkillProfile();
    await openAdvisory({});
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Cố vấn");
  });
});
