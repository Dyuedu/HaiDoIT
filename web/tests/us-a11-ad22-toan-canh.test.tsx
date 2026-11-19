import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { MarketOverviewScreen } from "@/app/components/insights/overview/market-overview-screen";
import { formatCount, formatPercent } from "@/lib/city-shares-view";
import { levelLabel, roleLabel } from "@/lib/labels";
import { type MarketOverviewEnvelope, isMarketOverviewEnvelope } from "@/lib/market-overview";

import fixtureJson from "./fixtures/market-overview.json";
import { jsonResponse } from "./helpers/fetch";

// US-A11 #326, #329 — toàn cảnh thị trường đầu trang Insights. Mọi tỷ trọng và thứ hạng lấy từ API (AD-22).

const fixture = fixtureJson as unknown as MarketOverviewEnvelope;
const PATH = "/api/v1/market-overview";

function route(reply: () => Response) {
  const mock = vi.fn(async (input: RequestInfo | URL) => {
    const url = new URL(String(input), "http://localhost");
    if (url.pathname !== PATH) throw new Error(`URL lạ: ${String(input)}`);
    return reply();
  });
  vi.stubGlobal("fetch", mock);
  return mock;
}

async function open() {
  route(() => jsonResponse(200, fixture));
  const user = userEvent.setup();
  render(<MarketOverviewScreen />);
  await screen.findByRole("list", { name: "Chỉ số chính" });
  return user;
}

function roleNames(list: HTMLElement): string[] {
  return within(list)
    .getAllByRole("listitem")
    .map((item) => within(item).getByRole("link").firstElementChild?.textContent ?? "");
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("US-A11 #326 — toàn cảnh thị trường", () => {
  it("AC1 AD-22: bốn chỉ số, mỗi chỉ số có số tin và ngày cập nhật; tỷ lệ in đúng giá trị API", async () => {
    await open();
    const kpis = within(screen.getByRole("list", { name: "Chỉ số chính" })).getAllByRole("listitem");
    expect(kpis).toHaveLength(4);
    expect(kpis[0].textContent).toContain(formatCount(fixture.meta.cells["vn.all"].n));
    expect(kpis[0].textContent).toContain("cập nhật 03/11/2026");
    expect(kpis[1].textContent).toContain(formatPercent(fixture.data.entry_share.value as number));
    expect(kpis[2].textContent).toContain(formatPercent(fixture.data.big_cities_share.value as number));
    expect(kpis[3].textContent).toContain("không ghi số năm kinh nghiệm");
  });

  it("AC2: biểu đồ tròn có một nút cho mỗi cấp; chọn Senior xếp vai trò theo thứ tự máy chủ gửi cho cấp đó", async () => {
    const user = await open();
    const group = screen.getByRole("group", { name: "Chọn cấp bậc" });
    const buttons = within(group).getAllByRole("button");
    expect(buttons.map((b) => b.textContent)).toEqual(
      fixture.data.levels.map((lv) => expect.stringContaining(levelLabel(lv)) as unknown as string),
    );
    await user.click(within(group).getByRole("button", { name: /^Senior/ }));
    expect(within(group).getByRole("button", { name: /^Senior/ }).getAttribute("aria-pressed")).toBe("true");
    const list = screen.getByRole("list", { name: "Tin cấp Senior theo vai trò" });
    const senior = fixture.data.roles_by_level.find((r) => r.level === "senior")!.roles;
    expect(roleNames(list)).toEqual(senior.map(roleLabel));
    await user.click(screen.getByRole("button", { name: "Bỏ lọc cấp bậc" }));
    expect(roleNames(screen.getByRole("list", { name: "Số tin theo vai trò" }))).toEqual(fixture.data.roles.map((r) => roleLabel(r.role)));
  });

  it("AC2: có nút xoay cho bàn phím; canvas chỉ để nhìn", async () => {
    const user = await open();
    await user.click(screen.getByRole("button", { name: "Xoay trái" }));
    await user.click(screen.getByRole("button", { name: "Xoay phải" }));
    expect(screen.getByTestId("pie-3d").getAttribute("aria-hidden")).toBe("true");
  });

  it("AC3: cột số năm, cột nơi làm việc và biểu đồ hai phía theo thứ tự API", async () => {
    await open();
    const years = within(screen.getByRole("list", { name: "Số tin theo số năm kinh nghiệm" })).getAllByRole("listitem");
    expect(years).toHaveLength(fixture.data.years.length);
    expect(years[0].textContent).toContain("Không cần kinh nghiệm");
    expect(years[years.length - 1].textContent).toContain("Không ghi");
    const places = within(screen.getByRole("list", { name: "Số tin theo nơi làm việc" })).getAllByRole("listitem");
    expect(places.map((p) => p.textContent)).toEqual([
      expect.stringContaining("Hà Nội"),
      expect.stringContaining("TP.HCM"),
      expect.stringContaining("Đà Nẵng"),
      expect.stringContaining("Tỉnh khác"),
      expect.any(String),
      expect.any(String),
      expect.any(String),
    ]);
    const sides = within(screen.getByRole("list", { name: "Phần trăm tin của mỗi vai trò ở Hà Nội và TP.HCM" })).getAllByRole(
      "listitem",
    );
    const shown = fixture.data.roles.filter((r) => r.role !== "other" && r.share.display === "shown");
    expect(sides).toHaveLength(shown.length);
  });

  it("AC4 DEC-6: câu tóm tắt gọi tên theo thứ hạng máy chủ và không có chữ số", async () => {
    await open();
    const lines = within(screen.getByTestId("takeaways")).getAllByRole("listitem").map((li) => li.textContent ?? "");
    expect(lines.length).toBeGreaterThanOrEqual(3);
    for (const line of lines) expect(line).not.toMatch(/\d/);
    const [first, second] = fixture.data.levels_by_size;
    expect(lines[0]).toContain(`${levelLabel(first)} và ${levelLabel(second)}`);
    const [a, b] = fixture.data.roles_by_entry_share;
    expect(lines.join(" ")).toContain(`${roleLabel(a)} và ${roleLabel(b)} là hai cửa rộng nhất cho người mới`);
  });

  it("AC5: vai trò dưới 30 tin mờ đi và nói rõ có bao nhiêu tin", async () => {
    await open();
    const list = screen.getByRole("list", { name: "Số tin theo vai trò" });
    const row = within(list).getAllByRole("listitem").find((li) => li.textContent?.includes("Nhúng"))!;
    expect(row.className).toContain("opacity");
    expect(row.textContent).toContain("Mới có 12 tin, chưa đủ 30");
  });

  it("AC6: mỗi biểu đồ có bảng số", async () => {
    await open();
    expect(screen.getAllByText("Xem bảng số")).toHaveLength(5);
  });

  it("lỗi unknown_cell có câu của API, không có nút thử lại; body sai hợp đồng thì báo không đọc được", async () => {
    route(() =>
      jsonResponse(404, { error: { code: "unknown_cell", message: "Chưa có snapshot nào.", snapshot_date: null } }),
    );
    const { unmount } = render(<MarketOverviewScreen />);
    expect(await screen.findByText("Chưa có snapshot nào.")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Thử lại" })).toBeNull();
    unmount();
    const broken = structuredClone(fixture) as unknown as { data: { roles_by_level: unknown[] } };
    broken.data.roles_by_level = [];
    route(() => jsonResponse(200, broken));
    render(<MarketOverviewScreen />);
    expect(await screen.findByText("Không đọc được số liệu. Thử lại sau.")).toBeTruthy();
  });

  it("AD-22: bộ kiểm hợp đồng nhận fixture và từ chối thứ hạng thiếu vai trò", () => {
    expect(isMarketOverviewEnvelope(fixture)).toBe(true);
    const broken = structuredClone(fixture);
    broken.data.roles_by_level[0].roles = broken.data.roles_by_level[0].roles.slice(1);
    expect(isMarketOverviewEnvelope(broken)).toBe(false);
  });
});
