import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import SkillProfilePlaceholder from "@/app/ho-so-ky-nang/page";
import InsightsPage from "@/app/insights/page";
import { fetchNewcomerRoles, type NewcomerRolesEnvelope } from "@/lib/newcomer-roles";

import fixtureJson from "./fixtures/newcomer-roles.json";
import { jsonResponse } from "./helpers/fetch";

// #147 — màn người mới trên Insights, dựng từ response của API giả (#144). Thứ tự dòng do API quyết (AD-22).
const fixture = fixtureJson as unknown as NewcomerRolesEnvelope;
const PATH = "/api/v1/newcomer-roles";

function clone(): NewcomerRolesEnvelope {
  return JSON.parse(JSON.stringify(fixture)) as NewcomerRolesEnvelope;
}

/** Thay `fetch`: mỗi lần gọi lấy reply kế tiếp, reply cuối dùng lại mãi. */
function routeNewcomer(...replies: (() => Response | Promise<Response>)[]) {
  const queue = [...replies];
  const mock = vi.fn(async (input: RequestInfo | URL) => {
    const url = new URL(String(input), "http://localhost");
    if (url.pathname !== PATH) throw new Error(`URL lạ: ${String(input)}`);
    const next = queue.length > 1 ? queue.shift()! : queue[0];
    return next();
  });
  vi.stubGlobal("fetch", mock);
  return mock;
}

async function openList() {
  render(<InsightsPage />);
  return screen.findByRole("list", { name: /Vai trò theo số tin cho người mới/ });
}

function items(list: HTMLElement) {
  return within(list).getAllByRole("listitem");
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fr37 #147 — danh sách vai trò còn tuyển người mới", () => {
  it("fr37: mỗi vai trò một dòng, đúng thứ tự API gửi, nhãn tiếng Việt", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    const list = await openList();
    const rows = items(list);
    expect(rows).toHaveLength(fixture.data.rows.length);
    expect(within(rows[0]).getByText("AI/ML")).toBeTruthy();
    expect(within(rows[2]).getByText("Hạ tầng & IT support")).toBeTruthy();
    expect(within(rows[rows.length - 1]).getByText("Vai trò khác")).toBeTruthy();
  });

  it("fr37: web không sắp xếp lại, kể cả khi API gửi thứ tự khác", async () => {
    const env = clone();
    env.data.rows.reverse();
    routeNewcomer(() => jsonResponse(200, env));
    const rows = items(await openList());
    expect(within(rows[0]).getByText("Vai trò khác")).toBeTruthy();
    expect(within(rows[rows.length - 1]).getByText("AI/ML")).toBeTruthy();
  });

  it("fr37: dòng đủ mẫu có số tin entry-level, tỷ lệ và n của vai trò", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    const row = items(await openList())[0];
    expect(row.textContent).toContain("501 tin cho người mới");
    expect(row.textContent).toContain("57,1%");
    expect(row.textContent).toContain("n = 877");
  });

  it("fr37: vai trò dưới 30 tin ghi chưa đủ dữ liệu (X/30), không có phần trăm", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    const rows = items(await openList());
    const embedded = rows.find((r) => within(r).queryByText("Nhúng"))!;
    expect(embedded.textContent).toContain("chưa đủ dữ liệu (12/30)");
    expect(embedded.textContent).toContain("6 tin cho người mới");
    expect(embedded.textContent).not.toMatch(/%/);
  });

  it("fr37: vai trò không có tin entry-level hiện 0 và vẫn ở trong danh sách", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    const rows = items(await openList());
    const devops = rows.find((r) => within(r).queryByText("DevOps"))!;
    expect(devops.textContent).toContain("0 tin cho người mới");
    expect(devops.textContent).toContain("0,0%");
    const other = rows.find((r) => within(r).queryByText("Vai trò khác"))!;
    expect(other.textContent).toContain("0 tin cho người mới");
    expect(other.textContent).toContain("chưa đủ dữ liệu (0/30)");
  });

  it("fr37: ngưỡng trong ghi chú lấy từ meta.thresholds.min_sample", async () => {
    const env = clone();
    env.meta.thresholds.min_sample = 50;
    routeNewcomer(() => jsonResponse(200, env));
    const rows = items(await openList());
    const embedded = rows.find((r) => within(r).queryByText("Nhúng"))!;
    expect(embedded.textContent).toContain("chưa đủ dữ liệu (12/50)");
  });

  it("fr37: chạm một vai trò mở hồ sơ kỹ năng của vai trò đó ở cấp mới vào nghề", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    const rows = items(await openList());
    const link = within(rows[0]).getByRole("link");
    expect(link.getAttribute("href")).toBe("/ho-so-ky-nang?role=ai_ml&level=entry");
    expect(link.textContent).toMatch(/^AI\/ML/);
  });

  it("fr37: ngày snapshot, nguồn và lưu ý độ phủ nằm ở chú thích riêng", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    await openList();
    const caption = screen.getByRole("region", { name: "Nguồn và lưu ý" });
    expect(caption.textContent).toContain("03/11/2026");
    expect(caption.textContent).toContain("itviec");
    for (const note of fixture.meta.coverage_notes) expect(caption.textContent).toContain(note.text);
  });

  it("fr37: unknown_cell báo lỗi kèm ngày, không có nút thử lại", async () => {
    routeNewcomer(() =>
      jsonResponse(404, {
        error: { code: "unknown_cell", message: "Chưa có snapshot.", snapshot_date: "2026-11-12" },
      }),
    );
    render(<InsightsPage />);
    expect((await screen.findByRole("alert")).textContent).toContain("Chưa có snapshot.");
    expect(screen.getByText("12/11/2026")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Thử lại" })).toBeNull();
    expect(screen.queryByRole("list", { name: /Vai trò theo số tin/ })).toBeNull();
  });

  it("fr37: mạng hỏng thì báo không đọc được và thử lại được", async () => {
    const mock = routeNewcomer(
      () => Promise.reject(new TypeError("mạng hỏng")),
      () => jsonResponse(200, fixture),
    );
    render(<InsightsPage />);
    expect((await screen.findByRole("alert")).textContent).toContain("Không đọc được số liệu");
    await userEvent.click(screen.getByRole("button", { name: "Thử lại" }));
    expect(await screen.findByRole("list", { name: /Vai trò theo số tin/ })).toBeTruthy();
    expect(mock).toHaveBeenCalledTimes(2);
  });
});

describe("fr37 #147 — envelope sai hợp đồng thì không dùng", () => {
  const cases: [string, (env: NewcomerRolesEnvelope) => void][] = [
    ["share không phải level_share", (env) => ((env.data.rows[0].share as { kind: string }).kind = "skill_rate")],
    ["share.cell_id khác total_cell_id", (env) => (env.data.rows[0].share.cell_id = env.data.rows[0].entry_cell_id)],
    ["thiếu ô entry-level", (env) => delete env.meta.cells[env.data.rows[0].entry_cell_id]],
    ["dòng shown mà value null", (env) => (env.data.rows[0].share.value = null)],
    ["dòng null_data mà có value", (env) => (env.data.rows[13].share.value = 0.5)],
    ["vai trò lặp", (env) => (env.data.rows[1].role = env.data.rows[0].role)],
    ["không có dòng nào", (env) => (env.data.rows = [])],
    ["levels rỗng", (env) => (env.data.levels = [])],
  ];

  it.each(cases)("fr37: %s → không đọc được", async (_name, breakIt) => {
    const env = clone();
    breakIt(env);
    routeNewcomer(() => jsonResponse(200, env));
    expect(await fetchNewcomerRoles()).toEqual({ kind: "unreadable" });
  });

  it("fr37: envelope đúng hợp đồng thì đọc được", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    const result = await fetchNewcomerRoles();
    expect(result.kind).toBe("ok");
  });
});

describe("fr37 #147 — trang giữ chỗ hồ sơ kỹ năng (tới khi có #111)", () => {
  async function renderPlaceholder(params: Record<string, string>) {
    render(await SkillProfilePlaceholder({ searchParams: Promise.resolve(params) }));
  }

  it("fr37: gọi tên vai trò, cấp mới vào nghề, và nói hồ sơ kỹ năng có ở sprint sau", async () => {
    await renderPlaceholder({ role: "backend", level: "entry" });
    expect(screen.getByRole("heading", { level: 1 }).textContent).toContain("Backend");
    expect(screen.getByText(/Mới vào nghề/)).toBeTruthy();
    expect(screen.getByText(/sprint sau/)).toBeTruthy();
    expect(screen.getByRole("link", { name: /Quay lại/ }).getAttribute("href")).toBe("/insights");
  });

  it("fr37: mã vai trò lạ thì không bịa tên vai trò", async () => {
    await renderPlaceholder({ role: "khong_co" });
    expect(screen.getByRole("heading", { level: 1 }).textContent).not.toContain("khong_co");
    expect(screen.getByText(/Không có vai trò này/)).toBeTruthy();
  });
});

describe("fr37 DEC-6 (#132) — câu trên màn người mới không chứa chữ số", () => {
  it("fr37: câu giới thiệu và câu trang giữ chỗ không có chữ số", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    await openList();
    const sentences = screen.getAllByTestId("insight-sentence").map((el) => el.textContent ?? "");
    expect(sentences.length).toBeGreaterThan(0);
    for (const s of sentences) expect(s).not.toMatch(/\d/);

    render(await SkillProfilePlaceholder({ searchParams: Promise.resolve({ role: "backend", level: "entry" }) }));
    for (const el of screen.getAllByTestId("insight-sentence")) expect(el.textContent).not.toMatch(/\d/);
  });
});
