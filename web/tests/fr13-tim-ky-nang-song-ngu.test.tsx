import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import SkillProfilePage from "@/app/ho-so-ky-nang/page";
import { readProfile } from "@/lib/haido-keys";
import { type SkillRow, foldText, searchSkills } from "@/lib/vocab";

import { jsonResponse } from "./helpers/fetch";
import { SKILLS, routeSkillProfile } from "./helpers/skill-profile";

// #207 — tìm kỹ năng bằng tiếng Việt hoặc tiếng Anh trên `GET /api/v1/skills`, tick được kết quả. Dùng chung cho #113.

const ALL = SKILLS.data.skills as SkillRow[];

function codes(query: string): string[] {
  return searchSkills(ALL, query).map((skill) => skill.code);
}

async function openProfile(params: Record<string, string> = {}) {
  return render(await SkillProfilePage({ searchParams: Promise.resolve(params) }));
}

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/ho-so-ky-nang");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fr13 #207 — bỏ dấu và tìm", () => {
  it("fr13: foldText theo luật fold của API: chữ thường, bỏ dấu, đ thành d, gộp khoảng trắng", () => {
    expect(foldText("Học  Máy")).toBe("hoc may");
    expect(foldText("  Đà Nẵng ")).toBe("da nang");
    expect(foldText("C#")).toBe("c#");
  });

  it("fr13: 'học máy' tìm ra Machine Learning", () => {
    expect(codes("học máy")).toContain("machine_learning");
  });

  it("fr13: không dấu, chữ hoa, tiếng Anh cũng tìm ra", () => {
    for (const query of ["hoc may", "HỌC MÁY", "machine", "Machine Learning"]) {
      expect(codes(query)).toContain("machine_learning");
    }
  });

  it("fr13: bí danh tìm ra kỹ năng", () => {
    expect(codes("ml")).toContain("machine_learning");
    expect(codes("reactjs")).toContain("react");
  });

  it("fr13: chuỗi rỗng hay toàn khoảng trắng thì không có kết quả", () => {
    expect(codes("")).toEqual([]);
    expect(codes("   ")).toEqual([]);
  });

  it("fr13: tối đa 8 kết quả, khớp đầu tên đứng trước khớp giữa tên", () => {
    expect(codes("a").length).toBeLessThanOrEqual(8);
    const java = codes("java");
    expect(java[0]).toBe("java");
    expect(java).toContain("javascript");
  });
});

describe("fr13 #207 — ô tìm kỹ năng trên màn", () => {
  it("fr13: gõ 'học máy', tick Machine Learning thì nó vào hồ sơ", async () => {
    const user = userEvent.setup();
    routeSkillProfile();
    await openProfile();
    await user.type(screen.getByRole("searchbox", { name: /Tìm kỹ năng/ }), "học máy");
    const results = await screen.findByRole("list", { name: "Kết quả tìm kỹ năng" });
    const option = within(results).getByRole("checkbox", { name: /Học máy \(Machine Learning\)/ }) as HTMLInputElement;
    expect(option.checked).toBe(false);
    await user.click(option);
    expect(option.checked).toBe(true);
    expect(readProfile().skills).toEqual(["machine_learning"]);
  });

  it("fr13: không có kết quả thì nói thành chữ trong vùng trạng thái", async () => {
    const user = userEvent.setup();
    routeSkillProfile();
    await openProfile();
    await user.type(screen.getByRole("searchbox", { name: /Tìm kỹ năng/ }), "zzzz");
    const status = await screen.findByText("Không có kỹ năng nào khớp");
    expect(status.closest("[role=status]")).toBeTruthy();
    expect(screen.queryByRole("list", { name: "Kết quả tìm kỹ năng" })).toBeNull();
  });

  it("fr13: ô trống thì không hiện danh sách kết quả", async () => {
    routeSkillProfile();
    await openProfile();
    await screen.findByRole("searchbox", { name: /Tìm kỹ năng/ });
    expect(screen.queryByRole("list", { name: "Kết quả tìm kỹ năng" })).toBeNull();
  });

  it("fr13: danh sách kỹ năng không tải được thì ô tìm báo lỗi, phần còn lại vẫn dùng được", async () => {
    routeSkillProfile({ skills: () => Promise.reject(new TypeError("offline")) });
    await openProfile({ role: "backend", level: "entry" });
    await screen.findByText(/Không tải được danh sách kỹ năng/);
    await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
  });

  it("fr13: danh sách kỹ năng sai hợp đồng thì coi như không tải được", async () => {
    routeSkillProfile({ skills: () => jsonResponse(200, { data: { skills: [{ code: 1 }] } }) });
    await openProfile();
    await screen.findByText(/Không tải được danh sách kỹ năng/);
  });
});
