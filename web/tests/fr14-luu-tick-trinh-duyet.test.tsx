import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import SkillProfilePage from "@/app/ho-so-ky-nang/page";
import { HAIDO_KEYS, writeProfile, readProfile } from "@/lib/haido-keys";

import { routeSkillProfile } from "./helpers/skill-profile";

// #206 — kỹ năng đã tick nằm trong `haido:profile` (khóa của #205, AD-23); mở lại trang trong cùng trình duyệt vẫn còn.

async function openProfile(params: Record<string, string>) {
  return render(await SkillProfilePage({ searchParams: Promise.resolve(params) }));
}

function saved(): { v: number; role: string | null; level: string | null; skills: string[] } {
  return readProfile();
}

function checkbox(name: string): HTMLInputElement {
  return screen.getByRole("checkbox", { name: new RegExp(`^Đã có ${name}$`) }) as HTMLInputElement;
}

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/ho-so-ky-nang");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fr14 ad23 #206 — lưu tick trong trình duyệt", () => {
  it("fr14: tick Java, mở lại trang thì Java vẫn được tick", async () => {
    const user = userEvent.setup();
    routeSkillProfile();
    const first = await openProfile({ role: "backend", level: "entry" });
    await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
    await user.click(checkbox("Java"));
    first.unmount();

    await openProfile({ role: "backend", level: "entry" });
    await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
    await waitFor(() => expect(checkbox("Java").checked).toBe(true));
  });

  it("ad23: chỉ khóa haido:profile được ghi, đúng hình {v, role, level, skills}, giữ thứ tự tick", async () => {
    const user = userEvent.setup();
    routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
    await user.click(checkbox("SQL"));
    await user.click(checkbox("Java"));
    expect(Object.keys(window.localStorage)).toEqual([HAIDO_KEYS.profile]);
    expect(saved()).toEqual({ v: 1, role: "backend", level: "entry", skills: ["sql", "java"] });
  });

  it("fr14: bỏ tick thì mã ra khỏi hồ sơ đã lưu", async () => {
    const user = userEvent.setup();
    writeProfile({ v: 1, role: null, level: null, skills: ["java", "sql"] });
    routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
    await waitFor(() => expect(checkbox("Java").checked).toBe(true));
    await user.click(checkbox("Java"));
    expect(saved().skills).toEqual(["sql"]);
  });

  it("fr14: đổi vai trò và cấp thì lưu vai trò mục tiêu và cấp, giữ nguyên kỹ năng", async () => {
    const user = userEvent.setup();
    writeProfile({ v: 1, role: null, level: null, skills: ["git"] });
    routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
    await user.selectOptions(screen.getByRole("combobox", { name: "Vai trò" }), "frontend");
    await user.selectOptions(screen.getByRole("combobox", { name: "Cấp bậc" }), "intern");
    expect(saved()).toEqual({ v: 1, role: "frontend", level: "intern", skills: ["git"] });
  });

  it("fr14: mở không có role thì dùng vai trò mục tiêu đã lưu", async () => {
    writeProfile({ v: 1, role: "backend", level: null, skills: [] });
    const api = routeSkillProfile();
    await openProfile({});
    await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
    expect((screen.getByRole("combobox", { name: "Vai trò" }) as HTMLSelectElement).value).toBe("backend");
    expect(api.calls("/api/v1/skill-rates")[0].params.role).toBe("backend");
  });

  it("fr14: trình duyệt chặn bộ nhớ thì màn không vỡ và ô vẫn tick trong phiên", async () => {
    const user = userEvent.setup();
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("blocked", "SecurityError");
    });
    routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    const list = await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
    await user.click(checkbox("Java"));
    expect(checkbox("Java").checked).toBe(true);
    expect(within(list).getAllByRole("listitem").length).toBeGreaterThan(0);
  });
});
