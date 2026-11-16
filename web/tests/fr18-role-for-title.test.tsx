import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import SkillProfilePage from "@/app/ho-so-ky-nang/page";
import { fetchRoleForTitle } from "@/lib/role-for-title";

import { jsonResponse } from "./helpers/fetch";
import { routeSkillProfile, titleReply } from "./helpers/skill-profile";

// #150 — chức danh người dùng gõ thành một vai trò qua phép 6 (`GET /api/v1/role-for-title`), màn ghi vai trò đã dùng.

async function openProfile(params: Record<string, string> = {}) {
  return render(await SkillProfilePage({ searchParams: Promise.resolve(params) }));
}

async function searchTitle(user: ReturnType<typeof userEvent.setup>, title: string) {
  await user.type(screen.getByRole("textbox", { name: /Chức danh bạn muốn ứng tuyển/ }), title);
  await user.click(screen.getByRole("button", { name: "Tìm vai trò" }));
}

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/ho-so-ky-nang");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fr18 #150 — chức danh khớp một vai trò", () => {
  it("fr18: gõ chức danh khớp thì màn ghi vai trò đã dùng, ô Vai trò chọn vai trò đó, và tải số của nó", async () => {
    const user = userEvent.setup();
    const api = routeSkillProfile({ roleForTitle: () => titleReply("matched", "backend") });
    await openProfile();
    await searchTitle(user, "Lập trình viên Java");

    await screen.findByText(/Hải Đồ dùng vai trò Backend/);
    expect(api.calls("/api/v1/role-for-title")[0].params.title).toBe("Lập trình viên Java");
    expect((screen.getByRole("combobox", { name: "Vai trò" }) as HTMLSelectElement).value).toBe("backend");
    await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
    expect(api.calls("/api/v1/skill-rates").at(-1)?.params).toMatchObject({ role: "backend", level: "entry" });
    expect(screen.getByRole("heading", { level: 1 }).textContent).toContain("Backend");
  });

  it("fr18: đổi ô Vai trò thì tải số của vai trò mới", async () => {
    const user = userEvent.setup();
    const api = routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
    await user.selectOptions(screen.getByRole("combobox", { name: "Vai trò" }), "frontend");
    await waitFor(() =>
      expect(api.calls("/api/v1/skill-rates").at(-1)?.params).toMatchObject({ role: "frontend", level: "entry" }),
    );
    const list = await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
    await waitFor(() => expect(within(list).getAllByRole("listitem")[0].textContent).toContain("JavaScript"));
    expect(window.location.search).toBe("?role=frontend&level=entry");
  });

  it("fr18: ô chức danh trống thì bấm tìm không gọi API", async () => {
    const user = userEvent.setup();
    const api = routeSkillProfile({ roleForTitle: () => titleReply("matched", "backend") });
    await openProfile();
    await user.click(screen.getByRole("button", { name: "Tìm vai trò" }));
    expect(api.calls("/api/v1/role-for-title")).toHaveLength(0);
  });
});

describe("fr18 #150 — chức danh không khớp vai trò IT nào", () => {
  for (const status of ["not_it", "generic"] as const) {
    it(`fr18: ${status} thì nói không khớp, hiện danh sách vai trò, không có số nào`, async () => {
      const user = userEvent.setup();
      const api = routeSkillProfile({ roleForTitle: () => titleReply(status) });
      const view = await openProfile({ role: "backend", level: "entry" });
      await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
      await searchTitle(user, status === "not_it" ? "Kế toán" : "Developer");

      await screen.findByText(/không khớp vai trò IT nào/);
      const roles = screen.getByRole("list", { name: "Danh sách vai trò" });
      const buttons = within(roles).getAllByRole("button");
      expect(buttons.map((b) => b.textContent)).toContain("Backend");
      expect(buttons.map((b) => b.textContent)).not.toContain("Tất cả");
      expect(screen.queryByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ })).toBeNull();
      expect(view.container.textContent ?? "").not.toMatch(/\d/);
      // chọn một vai trò trong danh sách thì có số trở lại
      await user.click(within(roles).getByRole("button", { name: "Frontend" }));
      await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
      expect(api.calls("/api/v1/skill-rates").at(-1)?.params.role).toBe("frontend");
    });
  }

  it("fr18: lỗi khi tìm vai trò thì báo, không đoán vai trò", async () => {
    const user = userEvent.setup();
    routeSkillProfile({
      roleForTitle: () => jsonResponse(422, { error: { code: "invalid_query", message: "Sai.", snapshot_date: null } }),
    });
    await openProfile();
    await searchTitle(user, "x");
    await screen.findByText(/Không tìm được vai trò cho chức danh này/);
  });
});

describe("fr18 #150 — đọc response", () => {
  it("fr18: response sai hợp đồng thì không đọc được", async () => {
    for (const body of [
      { data: { status: "matched", role: null } },
      { data: { status: "not_it", role: "backend" } },
      { data: { status: "khac", role: null } },
      { data: { status: "matched", role: "khong_co_trong_danh_sach" } },
      {},
    ]) {
      routeSkillProfile({ roleForTitle: () => jsonResponse(200, body) });
      expect((await fetchRoleForTitle("x")).kind).toBe("unreadable");
    }
  });
});
