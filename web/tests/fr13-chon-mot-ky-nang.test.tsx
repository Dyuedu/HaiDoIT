import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import InsightsPage from "@/app/insights/page";
import { writeProfile } from "@/lib/haido-keys";

import { jsonResponse } from "./helpers/fetch";
import { routeInsights } from "./helpers/skill-roles";

// #167 — chọn đúng một kỹ năng bằng tiếng Việt hoặc tiếng Anh (hàm tìm của #207), màn ghi kỹ năng đã dùng theo API, và
// nói khi không tin nào nhắc kỹ năng (cờ `mentioned` của #166, web không suy từ các dòng: AD-22).

const LIST = /Vai trò theo tỷ lệ tin nhắc tới kỹ năng/;

function section() {
  return screen.findByRole("region", { name: "Kỹ năng của bạn dùng ở vai trò nào" });
}

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/insights");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fr13 #167 — chọn một kỹ năng", () => {
  it("fr13: gõ 'học máy', chọn Học máy thì màn ghi kỹ năng đã dùng, gọi đúng mã và đổi URL", async () => {
    const user = userEvent.setup();
    const api = routeInsights();
    render(<InsightsPage />);
    const area = await section();
    await user.type(within(area).getByRole("searchbox", { name: /Tìm kỹ năng/ }), "học máy");
    const results = await within(area).findByRole("list", { name: "Kết quả tìm kỹ năng" });
    const option = within(results).getByRole("button", { name: "Học máy (Machine Learning)" });
    await user.click(option);

    await within(area).findByText("Kỹ năng: Học máy (Machine Learning)");
    expect(api.calls("/api/v1/skill-roles").at(-1)?.params.skill).toBe("machine_learning");
    expect(window.location.search).toBe("?skill=machine_learning");
    expect(option.getAttribute("aria-pressed")).toBe("true");
    await within(area).findByRole("list", { name: LIST });
  });

  it("fr13: không dấu, tiếng Anh, bí danh cũng ra Học máy", async () => {
    const user = userEvent.setup();
    routeInsights();
    render(<InsightsPage />);
    const area = await section();
    const box = within(area).getByRole("searchbox", { name: /Tìm kỹ năng/ });
    for (const query of ["hoc may", "machine", "ml"]) {
      await user.clear(box);
      await user.type(box, query);
      const results = await within(area).findByRole("list", { name: "Kết quả tìm kỹ năng" });
      expect(within(results).getByRole("button", { name: "Học máy (Machine Learning)" })).toBeTruthy();
    }
  });

  it("fr13 fr14: kỹ năng trong hồ sơ trình duyệt hiện thành nút chọn nhanh", async () => {
    const user = userEvent.setup();
    writeProfile({ v: 1, role: null, level: null, skills: ["python", "figma"] });
    const api = routeInsights();
    render(<InsightsPage />);
    const area = await section();
    const quick = await within(area).findByRole("list", { name: "Kỹ năng trong hồ sơ của bạn" });
    await user.click(within(quick).getByRole("button", { name: "Figma" }));
    await within(area).findByText("Kỹ năng: Figma");
    expect(api.calls("/api/v1/skill-roles").at(-1)?.params.skill).toBe("figma");
  });

  it("fr13: mở với ?skill=python thì Python đã được chọn và danh sách hiện ngay", async () => {
    routeInsights();
    window.history.replaceState(null, "", "/insights?skill=python");
    render(<InsightsPage />);
    const area = await section();
    await within(area).findByText("Kỹ năng: Python");
    await within(area).findByRole("list", { name: LIST });
  });

  it("fr13: mã sai định dạng trong URL thì coi như chưa chọn, không gọi API", async () => {
    const api = routeInsights();
    window.history.replaceState(null, "", "/insights?skill=Khong-Hop-Le");
    render(<InsightsPage />);
    await section();
    await waitFor(() => expect(api.calls("/api/v1/skills").length).toBeGreaterThan(0));
    expect(api.calls("/api/v1/skill-roles")).toHaveLength(0);
    expect(screen.queryByText(/^Kỹ năng:/)).toBeNull();
  });

  it("fr13: chuỗi không khớp thì nói không có kỹ năng nào khớp", async () => {
    const user = userEvent.setup();
    routeInsights();
    render(<InsightsPage />);
    const area = await section();
    await user.type(within(area).getByRole("searchbox", { name: /Tìm kỹ năng/ }), "zzzz");
    const status = await within(area).findByText("Không có kỹ năng nào khớp");
    expect(status.closest("[role=status]")).toBeTruthy();
  });
});

describe("fr09 #167 — kỹ năng không tin nào nhắc", () => {
  it("fr09: mentioned = false thì nói chưa tin nào nhắc, không có danh sách hay 0%", async () => {
    routeInsights();
    window.history.replaceState(null, "", "/insights?skill=abap");
    render(<InsightsPage />);
    const area = await section();
    await within(area).findByText("Hiện chưa tin tuyển dụng nào nhắc tới ABAP.");
    expect(within(area).queryByRole("list", { name: LIST })).toBeNull();
    expect(area.textContent).not.toContain("0,0%");
  });

  it("fr09 ad22: mentioned = true mà mọi dòng bằng 0 thì vẫn hiện danh sách, không nói chưa tin nào nhắc", async () => {
    routeInsights();
    window.history.replaceState(null, "", "/insights?skill=sap");
    render(<InsightsPage />);
    const area = await section();
    await within(area).findByRole("list", { name: LIST });
    expect(within(area).queryByText(/Hiện chưa tin tuyển dụng nào nhắc/)).toBeNull();
  });

  it("fr13: unknown_skill thì hiện thông báo của API, không có Thử lại", async () => {
    routeInsights({
      skillRoles: () =>
        jsonResponse(404, { error: { code: "unknown_skill", message: "Không có kỹ năng này trong bộ từ vựng.", snapshot_date: null } }),
    });
    window.history.replaceState(null, "", "/insights?skill=khong_co");
    render(<InsightsPage />);
    const area = await section();
    await within(area).findByText("Không có kỹ năng này trong bộ từ vựng.");
    expect(within(area).queryByRole("button", { name: "Thử lại" })).toBeNull();
  });

  it("fr13: danh sách kỹ năng không tải được thì ô tìm báo lỗi, ?skill= vẫn dùng được", async () => {
    routeInsights({ skills: () => Promise.reject(new TypeError("offline")) });
    window.history.replaceState(null, "", "/insights?skill=python");
    render(<InsightsPage />);
    const area = await section();
    await within(area).findByText(/Không tải được danh sách kỹ năng/);
    await within(area).findByRole("list", { name: LIST });
  });
});
