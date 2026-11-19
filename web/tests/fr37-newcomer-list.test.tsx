import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import SkillProfilePage from "@/app/ho-so-ky-nang/page";
import InsightsPage from "@/app/insights/page";
import { formatCount, formatPercent, notEnoughText } from "@/lib/city-shares-view";
import { fetchNewcomerRoles, type NewcomerRolesEnvelope } from "@/lib/newcomer-roles";

import fixtureJson from "./fixtures/newcomer-roles.json";
import { deferred, jsonResponse } from "./helpers/fetch";
import { routeSkillProfile } from "./helpers/skill-profile";

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
    // Từ #329 /insights còn gọi toàn cảnh thị trường; giữ nó ở trạng thái đang tải để test chỉ kiểm mục người mới.
    if (url.pathname === "/api/v1/market-overview") return new Promise<Response>(() => {});
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

  it("fr37: #110 AC2 — dòng chưa đủ dữ liệu đứng sau mọi dòng có tỷ lệ, theo thứ tự DOM", async () => {
    const shownRoles = fixture.data.rows.filter((r) => r.share.display === "shown").map((r) => r.role);
    const nullRoles = fixture.data.rows.filter((r) => r.share.display === "null_data").map((r) => r.role);
    // fixture phải trộn cả hai loại, nếu không test này không kiểm được gì
    expect(shownRoles.length).toBeGreaterThan(0);
    expect(nullRoles.length).toBeGreaterThan(0);
    routeNewcomer(() => jsonResponse(200, fixture));
    const rows = items(await openList());
    const kinds = rows.map((r) => (/cần ít nhất|Chưa có tin nào/.test(r.textContent ?? "") ? "null_data" : "shown"));
    expect(kinds.filter((k) => k === "shown")).toHaveLength(shownRoles.length);
    const firstNull = kinds.indexOf("null_data");
    expect(firstNull).toBe(shownRoles.length);
    expect(kinds.slice(firstNull).every((k) => k === "null_data")).toBe(true);
  });

  it("fr37: #110 AC1 — dòng có tỷ lệ theo đúng thứ tự máy chủ, số tin cho người mới giảm dần", async () => {
    const shown = fixture.data.rows.filter((r) => r.share.display === "shown");
    const counts = shown.map((r) => fixture.meta.cells[r.entry_cell_id].n);
    // fixture có các số khác nhau, nên giảm dần là giảm nghiêm ngặt
    expect(new Set(counts).size).toBe(counts.length);
    expect(counts).toEqual([...counts].sort((a, b) => b - a));
    routeNewcomer(() => jsonResponse(200, fixture));
    const rows = items(await openList()).slice(0, shown.length);
    const shownCounts = rows.map((r) => Number(/(\d+) trên [\d.]+ tin dành cho người mới/.exec(r.textContent ?? "")![1]));
    expect(shownCounts).toEqual(counts);
    for (let i = 1; i < shownCounts.length; i++) expect(shownCounts[i]).toBeLessThan(shownCounts[i - 1]);
    rows.forEach((row, i) => expect(within(row).getByRole("link").getAttribute("href")).toContain(`role=${shown[i].role}`));
  });

  it("fr37: dòng đủ mẫu có số tin entry-level, tỷ lệ và n của vai trò", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    const row = items(await openList())[0];
    expect(row.textContent).toContain("501 trên 877 tin dành cho người mới");
    expect(row.textContent).toContain("57,1%");
    expect(row.textContent).not.toContain("n = ");
  });

  it("fr37: #110 AC1 — MỌI dòng ghi đúng số tin entry-level, n của vai trò và tỷ lệ của chính dòng đó", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    const rows = items(await openList());
    expect(rows).toHaveLength(fixture.data.rows.length);
    const minSample = fixture.meta.thresholds.min_sample;
    // các n khác nhau, nếu không một dòng hiện n của dòng khác vẫn xanh
    const ns = fixture.data.rows.map((r) => fixture.meta.cells[r.total_cell_id].n);
    expect(new Set(ns).size).toBeGreaterThan(5);
    fixture.data.rows.forEach((row, i) => {
      const entry = fixture.meta.cells[row.entry_cell_id].n;
      const n = fixture.meta.cells[row.total_cell_id].n;
      const view = within(rows[i]);
      const where = `dòng ${i} (${row.role})`;
      if (n > 0) expect(view.getByText(`${formatCount(entry)} trên ${formatCount(n)} tin dành cho người mới`), where).toBeTruthy();
      if (row.share.display === "shown") {
        expect(view.getByText(formatPercent(row.share.value as number)), where).toBeTruthy();
      } else {
        expect(view.getByText(notEnoughText(n, minSample)), where).toBeTruthy();
        expect(rows[i].textContent, where).not.toMatch(/%/);
      }
    });
    // tỷ lệ khác nhau giữa các dòng shown, nên "hiện tỷ lệ của dòng 0 ở mọi dòng" bị bắt
    const values = fixture.data.rows.filter((r) => r.share.display === "shown").map((r) => r.share.value);
    expect(new Set(values).size).toBeGreaterThan(3);
  });

  it("fr37: vai trò dưới 30 tin ghi chưa đủ dữ liệu (X/30), không có phần trăm", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    const rows = items(await openList());
    const embedded = rows.find((r) => within(r).queryByText("Nhúng"))!;
    expect(embedded.textContent).toContain("Mới có 12 tin, cần ít nhất 30");
    expect(embedded.textContent).toContain("6 trên 12 tin dành cho người mới");
    expect(embedded.textContent).not.toMatch(/%/);
  });

  it("fr37: vai trò không có tin entry-level hiện 0 và vẫn ở trong danh sách", async () => {
    routeNewcomer(() => jsonResponse(200, fixture));
    const rows = items(await openList());
    const devops = rows.find((r) => within(r).queryByText("DevOps"))!;
    expect(devops.textContent).toMatch(/0 trên [\d.]+ tin dành cho người mới/);
    expect(devops.textContent).toContain("0,0%");
    const other = rows.find((r) => within(r).queryByText("Vai trò khác"))!;
    expect(other.textContent).toContain("Chưa có tin nào");
    expect(other.textContent).not.toContain("trên 0 tin");
  });

  it("fr37: ngưỡng trong ghi chú lấy từ meta.thresholds.min_sample", async () => {
    const env = clone();
    env.meta.thresholds.min_sample = 50;
    routeNewcomer(() => jsonResponse(200, env));
    const rows = items(await openList());
    const embedded = rows.find((r) => within(r).queryByText("Nhúng"))!;
    expect(embedded.textContent).toContain("Mới có 12 tin, cần ít nhất 50");
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
    expect(caption.textContent).toContain("ITviec");
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
    // Từ #169 trang còn gọi /api/v1/skills cho mục kỹ năng; chỉ đếm lần gọi của danh sách người mới.
    expect(mock.mock.calls.filter(([input]) => String(input).includes(PATH))).toHaveLength(2);
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

describe("fr37 #147 #152 — trang đích của một dòng: hồ sơ kỹ năng (thay trang giữ chỗ)", () => {
  // #152 thay trang giữ chỗ của #147 bằng hồ sơ kỹ năng thật (FR-005 của #147). Ở đây chỉ giữ điều #147 hứa: dòng mở
  // đúng vai trò ở cấp mới vào nghề, và mã lạ không được in như một tên. Hành vi của hồ sơ test ở fr19-skill-profile.
  async function renderProfile(params: Record<string, string>) {
    routeSkillProfile();
    render(await SkillProfilePage({ searchParams: Promise.resolve(params) }));
  }

  it("fr37: mở đúng vai trò của dòng, ở cấp mới vào nghề", async () => {
    await renderProfile({ role: "backend", level: "entry" });
    expect(screen.getByRole("heading", { level: 1 }).textContent).toContain("Backend");
    expect((screen.getByRole("combobox", { name: "Cấp bậc" }) as HTMLSelectElement).value).toBe("entry");
    await screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
  });

  it("fr37: mã vai trò lạ thì không bịa tên vai trò", async () => {
    await renderProfile({ role: "khong_co" });
    expect(screen.getByRole("heading", { level: 1 }).textContent).not.toContain("khong_co");
    expect(screen.getByText(/Không có vai trò này/)).toBeTruthy();
  });

  it("fr37: role=all không phải một vai trò, hiện 'Không có vai trò này' chứ không phải 'Mọi vai trò'", async () => {
    await renderProfile({ role: "all" });
    expect(screen.getByText(/Không có vai trò này/)).toBeTruthy();
    expect(screen.queryByText(/Mọi vai trò/)).toBeNull();
    expect(screen.getByRole("heading", { level: 1 }).textContent).not.toContain("Mọi vai trò");
  });
});

describe("fr37 ad8 DEC-6 (#132) — câu trên màn người mới không chứa chữ số", () => {
  const CAPTION = "Nguồn và lưu ý";

  /**
   * Mọi chữ trên trang mà người đọc đọc như câu: duyệt MỌI nút chữ dưới `root` (không chỉ h1-h6, p, a) và các thuộc
   * tính `aria-label`, `title`, `alt`. Loại hai chỗ: danh sách số `ol` (ô số là số theo thiết kế) và khung "Nguồn và
   * lưu ý" (region, có số nguồn): chưa rõ có được miễn không, câu hỏi còn mở ở #132 (xem specs/148-test-nguoi-moi/spec.md).
   * Mã được thực thi là AD-8; #132 mở rộng kiểm chữ số sang câu soạn sẵn.
   */
  function narrative(root: HTMLElement): string[] {
    const caption = within(root).queryByRole("region", { name: CAPTION });
    // Từ #330 bảng số (`table`) cũng là ô số theo thiết kế, như danh sách `ol`.
    const outOfScope = (node: Node) =>
      !!caption?.contains(node) || !!(node.parentElement ?? (node as Element)).closest("ol, table");
    const out: string[] = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (!outOfScope(node) && (node.textContent ?? "").trim() !== "") out.push(node.textContent!);
    }
    root.querySelectorAll("*").forEach((el) => {
      if (outOfScope(el)) return;
      for (const attr of ["aria-label", "title", "alt"]) {
        const value = el.getAttribute(attr);
        if (value) out.push(value);
      }
    });
    return out;
  }

  function expectNoDigits(root: HTMLElement, minTexts = 1) {
    const texts = narrative(root);
    expect(texts.length).toBeGreaterThanOrEqual(minTexts);
    for (const t of texts) expect(t).not.toMatch(/\d/);
  }

  it("fr37 ad8: khung 'Nguồn và lưu ý' là region có tên, và narrative() bỏ qua nó nhưng không bỏ qua tiêu đề", () => {
    const { container, unmount } = render(
      <div>
        <h2>Tiêu đề</h2>
        <section aria-labelledby="cap">
          <h2 id="cap">{CAPTION}</h2>
          <p>trên 8 nguồn</p>
        </section>
      </div>,
    );
    expect(screen.getByRole("region", { name: CAPTION })).toBeTruthy();
    expect(narrative(container)).toEqual(["Tiêu đề"]);
    unmount();
    const bad = render(
      <div>
        <h2>Tiêu đề 3</h2>
        <section aria-labelledby="cap">
          <h2 id="cap">{CAPTION}</h2>
          <p>trên 8 nguồn</p>
        </section>
      </div>,
    );
    expect(narrative(bad.container).some((t) => /\d/.test(t))).toBe(true);
    bad.unmount();
    const attr = render(<a href="/x" title="3 tin">Xem</a>);
    expect(narrative(attr.container)).toContain("3 tin");
  });

  it("fr37 ad8: /insights lúc đang tải, báo lỗi, không đọc được, unknown_cell và có số đều không có chữ số", async () => {
    // đang tải
    const pending = deferred<Response>();
    routeNewcomer(() => pending.promise);
    const loading = render(<InsightsPage />);
    // Từ #169 trang có thêm vùng trạng thái của mục kỹ năng; đọc vùng của mục người mới.
    expect(within(screen.getByRole("region", { name: "Cửa vào cho người mới" })).getByRole("status").textContent).toContain("Đang tải");
    expectNoDigits(loading.container, 4);
    loading.unmount();

    // lỗi mạng, có nút thử lại
    routeNewcomer(() => Promise.reject(new TypeError("mạng hỏng")));
    const failed = render(<InsightsPage />);
    await screen.findByRole("button", { name: "Thử lại" });
    expectNoDigits(failed.container, 5);
    failed.unmount();

    // envelope sai hợp đồng
    const broken = clone();
    broken.data.rows = [];
    routeNewcomer(() => jsonResponse(200, broken));
    const unreadable = render(<InsightsPage />);
    await screen.findByText(/Không đọc được số liệu/);
    expectNoDigits(unreadable.container, 5);
    unreadable.unmount();

    // unknown_cell: ngày snapshot là số liệu của máy chủ (như ô số), nên ca này không gửi ngày
    routeNewcomer(() => jsonResponse(404, { error: { code: "unknown_cell", message: "Chưa có snapshot.", snapshot_date: null } }));
    const unknown = render(<InsightsPage />);
    await screen.findByText("Chưa có snapshot.");
    expectNoDigits(unknown.container, 4);
    unknown.unmount();

    // có số
    routeNewcomer(() => jsonResponse(200, fixture));
    const ok = render(<InsightsPage />);
    await screen.findByRole("list", { name: /Vai trò theo số tin cho người mới/ });
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Insights");
    expect(screen.getByRole("heading", { level: 2, name: "Cửa vào cho người mới" })).toBeTruthy();
    expectNoDigits(ok.container, 3);
  });

  it("fr37 ad8: trang hồ sơ kỹ năng lúc chưa có số không có chữ số, cả khi vai trò lạ và role=all", async () => {
    // Từ #152 trang có số khi tải xong (ô số, như danh sách người mới); ở đây kiểm câu của khung trang trước khi có số.
    routeSkillProfile({ skillRates: () => new Promise<Response>(() => {}) });
    for (const params of [{ role: "backend", level: "entry" }, { role: "khong_co" }, { role: "all" }]) {
      const { container, unmount } = render(await SkillProfilePage({ searchParams: Promise.resolve(params) }));
      expect(screen.getByRole("heading", { level: 1 })).toBeTruthy();
      expectNoDigits(container, 3);
      unmount();
    }
  });
});
