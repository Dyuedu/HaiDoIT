import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import AdvisoryPage from "@/app/co-van/page";
import { NOT_ENOUGH_DATA } from "@/lib/city-shares-view";
import { readProfile, writeProfile } from "@/lib/haido-keys";
import { fetchLearningPath, type LearningPathEnvelope } from "@/lib/learning-path";
import { buildLearningPathView, connectorPath } from "@/lib/learning-path-view";

import { deferred, jsonResponse } from "./helpers/fetch";
import { NO_REAL_PATH, PATHS, clonePath, pathWithHave, routeLearningPath } from "./helpers/learning-path";

// #217 — lộ trình học kiểu roadmap.sh: mỗi chặng là một chủ đề ở cột giữa, kỹ năng thành cụm ở một bên, đường nối SVG. Thứ tự, chặng
// đang học và số đếm do API quyết (AD-7, AD-22); web chỉ hiện.

async function open(params: Record<string, string>) {
  return render(await AdvisoryPage({ searchParams: Promise.resolve(params) }));
}

const path = () => screen.findByRole("list", { name: "Các chặng của lộ trình học" });
const stageItems = (list: HTMLElement) => [...list.children] as HTMLElement[];
const node = (name: RegExp | string) => screen.getByRole("button", { name });
const box = (name: string) => screen.getByRole("checkbox", { name }) as HTMLInputElement;
const panel = () => screen.queryByRole("dialog");

/** Mã kỹ năng theo thứ tự DOM. */
function domOrder(root: ParentNode): string[] {
  return [...root.querySelectorAll("[data-skill]")].map((el) => el.getAttribute("data-skill") as string);
}

function seed(skills: string[]) {
  writeProfile({ v: 1, role: null, level: null, skills });
}

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/co-van");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fr22 #217 — các chặng", () => {
  it("fr22: mỗi chặng của API là một mục, đúng số chặng và đúng kỹ năng", async () => {
    routeLearningPath();
    await open({ role: "backend" });
    const items = stageItems(await path());
    const stages = PATHS.backend.data.stages;
    expect(items).toHaveLength(stages.length);
    items.forEach((item, i) => {
      expect(within(item).getByRole("heading", { level: 2 }).textContent).toBe(`Chặng ${stages[i].stage}${stages[i].title}`);
      expect(domOrder(item).sort()).toEqual(stages[i].skills.map((s) => s.skill).sort());
    });
  });

  it("fr22 ad7: trong một chặng giữ đúng thứ tự API, cốt lõi trước thường gặp", async () => {
    routeLearningPath();
    await open({ role: "backend" });
    const items = stageItems(await path());
    items.forEach((item, i) => {
      expect(domOrder(item)).toEqual(PATHS.backend.data.stages[i].skills.map((s) => s.skill));
    });
  });

  it("fr22: mỗi nút có tên, tỷ lệ và nhóm; nút nền tảng ghi cần cho kỹ năng nào (FR-20)", async () => {
    routeLearningPath();
    await open({ role: "backend" });
    const list = await path();
    const java = list.querySelector('[data-skill="java"]') as HTMLElement;
    expect(java.textContent).toContain("Java");
    expect(java.textContent).toContain("65,4%");
    expect(java.textContent).toContain("Cốt lõi");
    const linux = list.querySelector('[data-skill="linux"]') as HTMLElement;
    await waitFor(() => expect(linux.textContent).toMatch(/Kỹ năng nền tảng \(cần cho .*Docker.*\)/));
    expect(linux.textContent).not.toContain("Riêng của công ty");
  });

  it("fr22 #134: luôn hỏi cấp entry, kể cả khi URL có cấp khác", async () => {
    const api = routeLearningPath();
    await open({ role: "backend", level: "senior" });
    await path();
    expect(api.calls()[0].params).toEqual({ role: "backend", level: "entry" });
    expect(screen.getByText("Mới vào nghề")).toBeTruthy();
  });

  it("fr22: chưa đủ dữ liệu thì không có %, không nhóm", async () => {
    routeLearningPath();
    await open({ role: "data_engineer" });
    const list = await path();
    for (const el of list.querySelectorAll("[data-skill]")) {
      expect(el.textContent).toContain(NOT_ENOUGH_DATA);
      expect(el.textContent).not.toMatch(/%|Cốt lõi|Thường gặp/);
    }
    // Không tỷ lệ nào hiện thì không nói "Tính trên … tin".
    expect(screen.queryByText(/^Tính trên/)).toBeNull();
    expect(screen.getByText(PATHS.data_engineer.meta.cells["vn.data_engineer"].fallback_label)).toBeTruthy();
  });

  it("fr22 fr19: ô quay về hiện nguyên văn câu của API và số tin đã dùng", async () => {
    const env = clonePath("backendIntern");
    env.data.level = "entry"; // API trả lại đúng cấp đã hỏi
    routeLearningPath({ learningPath: () => jsonResponse(200, env) });
    await open({ role: "backend" });
    await path();
    expect(screen.getByText(PATHS.backendIntern.meta.cells["vn.backend"].fallback_label)).toBeTruthy();
    expect(screen.getByText("Tính trên 157 tin")).toBeTruthy();
  });

  it("fr22: có khung nguồn và lưu ý", async () => {
    routeLearningPath();
    await open({ role: "backend" });
    await path();
    expect(screen.getByRole("heading", { name: "Nguồn và lưu ý" })).toBeTruthy();
  });

  it("fr22 ad8: câu trên màn không có chữ số (DEC-6)", async () => {
    routeLearningPath();
    const { container } = await open({ role: "backend", skill: "java" });
    await path();
    await screen.findByRole("dialog");
    for (const el of container.querySelectorAll('[data-testid="insight-sentence"]')) {
      expect(el.textContent ?? "").not.toMatch(/\d/);
    }
    expect(container.querySelectorAll('[data-testid="insight-sentence"]').length).toBeGreaterThan(0);
  });
});

describe("fr22 fr14 ad22 #217 — tôi đã có", () => {
  it("fr22: đánh dấu đã có thì nút hiện xong, hồ sơ được lưu, API được hỏi lại với have", async () => {
    const user = userEvent.setup();
    const api = routeLearningPath();
    await open({ role: "backend" });
    const list = await path();
    await user.click(box("Đã có Java"));
    expect(box("Đã có Java").checked).toBe(true);
    expect(list.querySelector('[data-skill="java"]')?.getAttribute("data-have")).toBe("true");
    expect(readProfile().skills).toEqual(["java"]);
    await waitFor(() => expect(api.calls().at(-1)?.params.have).toBe("java"));
    await waitFor(() => expect(screen.getByTestId("path-count").textContent).toContain("1/14"));
  });

  it("fr22: bỏ đánh dấu thì trở lại", async () => {
    const user = userEvent.setup();
    seed(["java"]);
    routeLearningPath();
    await open({ role: "backend" });
    await path();
    await user.click(box("Đã có Java"));
    expect(box("Đã có Java").checked).toBe(false);
    expect(readProfile().skills).toEqual([]);
  });

  it("fr22: xong chặng thì chặng sau thành chặng đang học và kỹ năng của nó lên khung Học tiếp", async () => {
    const user = userEvent.setup();
    seed(["git"]);
    routeLearningPath();
    await open({ role: "backend" });
    const list = await path();
    const next = screen.getByRole("region", { name: "Học tiếp" });
    await waitFor(() => expect(stageItems(list)[0].getAttribute("aria-current")).toBe("step"));
    expect(next.textContent).toContain("Công cụ làm việc");
    expect(within(next).getByRole("button", { name: /Linux/ })).toBeTruthy();
    expect(within(next).queryByRole("button", { name: /Git/ })).toBeNull();
    expect(within(next).queryByRole("button", { name: /Java/ })).toBeNull();

    await user.click(box("Đã có Linux"));
    await waitFor(() => expect(stageItems(list)[1].getAttribute("aria-current")).toBe("step"));
    expect(stageItems(list)[0].getAttribute("aria-current")).toBeNull();
    expect(stageItems(list)[0].textContent).toContain("Đã xong");
    expect(next.textContent).toContain("Ngôn ngữ lập trình");
    expect(within(next).getByRole("button", { name: /Java/ })).toBeTruthy();
    expect(within(next).queryByRole("button", { name: /Linux/ })).toBeNull();
  });

  it("fr22: chặng chọn một ghi rõ, và xong ngay khi có một lựa chọn", async () => {
    const user = userEvent.setup();
    seed(["git", "linux", "java", "sql"]);
    routeLearningPath();
    await open({ role: "backend" });
    const list = await path();
    const db = stageItems(list)[3];
    await waitFor(() => expect(db.getAttribute("aria-current")).toBe("step"));
    expect(within(db).getByText("Chọn một")).toBeTruthy();
    expect(within(stageItems(list)[0]).queryByText("Chọn một")).toBeNull();
    const next = screen.getByRole("region", { name: "Học tiếp" });
    expect(within(next).getByText("Chọn một")).toBeTruthy();

    await user.click(box("Đã có MySQL"));
    await waitFor(() => expect(stageItems(list)[4].getAttribute("aria-current")).toBe("step"));
    expect(db.textContent).toContain("Đã xong");
    expect(box("Đã có PostgreSQL").checked).toBe(false);
  });

  it("fr22: đi hết các chặng dù chưa có mọi lựa chọn thì nói đã đi hết, không nói đã có mọi kỹ năng", async () => {
    const all = PATHS.backend.data.stages.flatMap((s) => (s.choose_one ? s.skills.slice(0, 1) : s.skills).map((k) => k.skill));
    seed(all);
    routeLearningPath();
    await open({ role: "backend" });
    const list = await path();
    await screen.findByText("Bạn đã đi hết các chặng của lộ trình này.");
    expect(list.querySelector("[aria-current]")).toBeNull();
    expect(screen.getByTestId("path-count").textContent).toContain("12/14");
  });

  it("fr22: có hết thì nói đã đi hết, không còn chặng đang học", async () => {
    const all = PATHS.backend.data.stages.flatMap((s) => s.skills.map((k) => k.skill));
    seed(all);
    routeLearningPath();
    await open({ role: "backend" });
    const list = await path();
    await screen.findByText("Bạn đã đi hết các chặng của lộ trình này.");
    expect(list.querySelector("[aria-current]")).toBeNull();
  });

  it("ad22: số đếm và chặng đang học là của API, không phải web tự tính", async () => {
    const env = pathWithHave("backend", []);
    env.data.have_on_path = 7;
    env.data.current_stage = 2;
    routeLearningPath({ learningPath: () => jsonResponse(200, env) });
    await open({ role: "backend" });
    const list = await path();
    expect(screen.getByTestId("path-count").textContent).toContain("7/14");
    expect(stageItems(list)[1].getAttribute("aria-current")).toBe("step");
  });

  it("fr22: đánh dấu không đổi thứ tự và không làm danh sách nhảy trong lúc tải lại", async () => {
    const user = userEvent.setup();
    const slow = deferred<Response>();
    routeLearningPath({
      learningPath: (p) => (p.have ? slow.promise : jsonResponse(200, pathWithHave("backend", []))),
    });
    await open({ role: "backend" });
    const list = await path();
    const before = domOrder(list);
    await user.click(box("Đã có SQL"));
    expect(domOrder(list)).toEqual(before);
    slow.resolve(jsonResponse(200, pathWithHave("backend", ["sql"])));
    await waitFor(() => expect(screen.getByTestId("path-count").textContent).toContain("1/14"));
    expect(domOrder(list)).toEqual(before);
  });

  it("fr14: đánh dấu không làm mất vai trò và cấp đã lưu", async () => {
    const user = userEvent.setup();
    writeProfile({ v: 1, role: "qa", level: "mid", skills: ["go"] });
    routeLearningPath();
    await open({ role: "backend" });
    await path();
    await user.click(box("Đã có Java"));
    expect(readProfile()).toEqual({ v: 1, role: "qa", level: "mid", skills: ["go", "java"] });
  });
});

describe("fr23 #217 — ngăn chi tiết", () => {
  it("fr23: bấm một nút mở ngăn có tỷ lệ, nhóm, lời dẫn, kỹ năng mở ra và tài liệu", async () => {
    const user = userEvent.setup();
    routeLearningPath();
    await open({ role: "backend" });
    await path();
    expect(panel()).toBeNull();
    await user.click(node(/^Spring Boot/));
    const dialog = await screen.findByRole("dialog", { name: "Spring Boot" });
    expect(dialog.textContent).toContain("51,9%");
    expect(dialog.textContent).toContain("Cốt lõi");
    expect(dialog.textContent).toContain("Framework để dựng dịch vụ Java");
    expect(within(within(dialog).getByRole("list", { name: "Cần học trước" })).getByRole("button").textContent).toContain("Java");
    expect(within(dialog).getByRole("list", { name: "Học xong thì học được" }).textContent).toMatch(/microservices/i);
    const link = within(dialog).getByRole("link", { name: /Bắt đầu với Spring Boot/ });
    expect(link.getAttribute("href")).toBe("https://spring.io/guides/gs/spring-boot/");
    expect(link.getAttribute("rel")).toContain("noopener");
  });

  it("fr23: bấm kỹ năng cần học trước thì ngăn chuyển sang kỹ năng đó", async () => {
    const user = userEvent.setup();
    routeLearningPath();
    await open({ role: "backend", skill: "spring_boot" });
    const dialog = await screen.findByRole("dialog", { name: "Spring Boot" });
    await user.click(within(within(dialog).getByRole("list", { name: "Cần học trước" })).getByRole("button"));
    expect(await screen.findByRole("dialog", { name: "Java" })).toBeTruthy();
  });

  it("fr23: Escape đóng ngăn và trả focus về nút", async () => {
    const user = userEvent.setup();
    routeLearningPath();
    await open({ role: "backend" });
    await path();
    await user.click(node(/^Spring Boot/));
    await screen.findByRole("dialog");
    await user.keyboard("{Escape}");
    expect(panel()).toBeNull();
    expect(document.activeElement).toBe(node(/^Spring Boot/));
  });

  it("fr23: nút Đóng cũng đóng ngăn", async () => {
    const user = userEvent.setup();
    routeLearningPath();
    await open({ role: "backend", skill: "java" });
    await screen.findByRole("dialog");
    await user.click(screen.getByRole("button", { name: "Đóng" }));
    expect(panel()).toBeNull();
  });

  it("fr23: đánh dấu đã có ngay trong ngăn", async () => {
    const user = userEvent.setup();
    routeLearningPath();
    await open({ role: "backend", skill: "java" });
    const dialog = await screen.findByRole("dialog", { name: "Java" });
    await user.click(within(dialog).getByRole("checkbox", { name: "Tôi đã có kỹ năng này" }));
    expect(readProfile().skills).toEqual(["java"]);
    expect(box("Đã có Java").checked).toBe(true);
  });

  it("fr23: mở ngăn không gọi thêm API", async () => {
    const user = userEvent.setup();
    const api = routeLearningPath();
    await open({ role: "backend" });
    await path();
    const before = api.fetchMock.mock.calls.length;
    await user.click(node(/^Spring Boot/));
    await screen.findByRole("dialog");
    expect(api.fetchMock.mock.calls.length).toBe(before);
  });

  it("fr22 #153: ?skill= mở đúng kỹ năng; URL giữ kỹ năng đang mở", async () => {
    const user = userEvent.setup();
    routeLearningPath();
    await open({ role: "backend", level: "entry", skill: "spring_boot" });
    await screen.findByRole("dialog", { name: "Spring Boot" });
    expect(window.location.search).toBe("?role=backend&level=entry&skill=spring_boot");
    await user.keyboard("{Escape}");
    await waitFor(() => expect(window.location.search).toBe("?role=backend&level=entry"));
  });

  it("fr22 #153: kỹ năng có tên mà không nằm trên lộ trình thì nói rõ", async () => {
    routeLearningPath();
    await open({ role: "backend", skill: "figma" });
    await path();
    expect(await screen.findByText(/Figma không nằm trên lộ trình của vai trò này/)).toBeTruthy();
    expect(panel()).toBeNull();
  });
});

describe("fr22 #217 — chọn vai trò", () => {
  it("fr22: không có role thì mời chọn vai trò, không gọi API", async () => {
    const api = routeLearningPath();
    await open({});
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Cố vấn");
    expect(screen.getByRole("combobox", { name: "Vai trò" })).toBeTruthy();
    await waitFor(() => expect(api.fetchMock).toHaveBeenCalled());
    expect(api.calls()).toHaveLength(0);
  });

  it("fr14: không có role thì dùng vai trò mục tiêu đã lưu", async () => {
    writeProfile({ v: 1, role: "backend", level: null, skills: [] });
    routeLearningPath();
    await open({});
    await path();
    expect(screen.getByRole("heading", { level: 1 }).textContent).toBe("Lộ trình học: Backend");
  });

  it("fr22: đổi vai trò thì tải lộ trình mới, lưu vai trò, đóng ngăn", async () => {
    const user = userEvent.setup();
    const api = routeLearningPath();
    await open({ role: "backend", skill: "java" });
    await screen.findByRole("dialog");
    await user.selectOptions(screen.getByRole("combobox", { name: "Vai trò" }), "data_engineer");
    await waitFor(() => expect(api.calls().at(-1)?.params.role).toBe("data_engineer"));
    const list = await path();
    expect(list.querySelector('[data-skill="python"]')).toBeTruthy();
    expect(panel()).toBeNull();
    expect(readProfile().role).toBe("data_engineer");
  });

  it("fr22: mã vai trò lạ thì không in mã", async () => {
    routeLearningPath();
    const { container } = await open({ role: "khong_co" });
    expect(container.textContent).not.toContain("khong_co");
    expect(screen.getByText(/Không có vai trò này/)).toBeTruthy();
  });
});

describe("fr22 #217 — chưa có lộ trình và lỗi", () => {
  it("fr22: not_ready nói lộ trình đang biên soạn và đưa tới hồ sơ kỹ năng", async () => {
    routeLearningPath();
    await open({ role: "ai_ml" });
    await screen.findByText("Lộ trình học có thứ tự cho vai trò này đang được biên soạn.");
    expect(screen.queryByRole("list", { name: "Các chặng của lộ trình học" })).toBeNull();
    expect(screen.getByRole("link", { name: /hồ sơ kỹ năng/i }).getAttribute("href")).toBe("/ho-so-ky-nang?role=ai_ml&level=entry");
  });

  it("fr22: API chưa có số thật thì báo lỗi, không Thử lại, vẫn có lối sang hồ sơ kỹ năng", async () => {
    routeLearningPath({ learningPath: () => jsonResponse(404, NO_REAL_PATH) });
    await open({ role: "backend" });
    await screen.findByText(NO_REAL_PATH.error.message);
    expect(screen.queryByRole("button", { name: "Thử lại" })).toBeNull();
    expect(screen.getByRole("link", { name: /hồ sơ kỹ năng/i })).toBeTruthy();
  });

  it("fr22: mạng hỏng thì Thử lại tải lại được", async () => {
    const user = userEvent.setup();
    let broken = true;
    routeLearningPath({
      learningPath: () => (broken ? Promise.reject(new TypeError("offline")) : jsonResponse(200, PATHS.backend)),
    });
    await open({ role: "backend" });
    await screen.findByText(/Không đọc được số liệu/);
    broken = false;
    await user.click(screen.getByRole("button", { name: "Thử lại" }));
    await path();
  });
});

describe("fr22 #217 — điện thoại là danh sách, đường nối chỉ là hình", () => {
  it("fr22: đường nối là SVG ẩn với trình đọc màn hình và chỉ hiện từ lg", async () => {
    routeLearningPath();
    await open({ role: "backend" });
    const list = await path();
    const svgs = [...list.querySelectorAll("svg[data-connector]")];
    expect(svgs.length).toBeGreaterThan(0);
    for (const svg of svgs) {
      expect(svg.getAttribute("aria-hidden")).toBe("true");
      expect(svg.getAttribute("class")).toContain("hidden");
      expect(svg.getAttribute("class")).toContain("lg:block");
    }
  });

  it("fr22: mỗi kỹ năng chỉ có một nút và một ô tick trong DOM", async () => {
    routeLearningPath();
    await open({ role: "backend" });
    const codes = domOrder(await path());
    expect(new Set(codes).size).toBe(codes.length);
    expect(codes).toHaveLength(PATHS.backend.data.path_size);
  });

  it("fr22: connectorPath nối giữa cạnh chặng tới giữa từng hàng đều nhau", () => {
    expect(connectorPath("right", 0, 1)).toBe("M 0 50 C 50 50, 50 50, 100 50");
    expect(connectorPath("right", 0, 2)).toBe("M 0 50 C 50 50, 50 25, 100 25");
    expect(connectorPath("left", 1, 2)).toBe("M 100 50 C 50 50, 50 75, 0 75");
  });

  it("fr22: mỗi chặng một cụm, giữ đúng thứ tự API, so le phải trái", () => {
    for (const key of ["backend", "data_engineer"] as const) {
      const view = buildLearningPathView(clonePath(key), (code) => code);
      view.stages.forEach((stage, i) => {
        const api = PATHS[key].data.stages[i];
        expect(stage.nodes.map((n) => n.skill)).toEqual(api.skills.map((s) => s.skill));
        expect([stage.title, stage.chooseOne]).toEqual([api.title, api.choose_one]);
        expect(stage.side).toBe(i % 2 === 0 ? "right" : "left");
      });
    }
  });

  it("fr22: số đường nối bằng số hàng của cụm; cụm chọn một chỉ có một đường", async () => {
    routeLearningPath();
    await open({ role: "backend" });
    const items = stageItems(await path());
    items.forEach((item, i) => {
      const api = PATHS.backend.data.stages[i];
      const rows = api.choose_one ? 1 : Math.ceil(api.skills.length / 2);
      expect(item.querySelectorAll("svg[data-connector] path")).toHaveLength(rows);
    });
  });

  it("fr22: ô kỹ năng mang loại để tô màu, có chú giải cho từng loại", async () => {
    routeLearningPath();
    await open({ role: "backend" });
    const list = await path();
    const kind = (code: string) => list.querySelector(`[data-skill="${code}"]`)?.getAttribute("data-kind");
    expect(kind("java")).toBe("core");
    expect(kind("redis")).toBe("common");
    expect(kind("linux")).toBe("foundation");
    const legend = screen.getByRole("list", { name: "Chú giải" });
    for (const text of ["Cốt lõi", "Thường gặp", "Nền tảng", "Đã có"]) expect(legend.textContent).toContain(text);
  });

  it("fr22: ô chỉ ghi tên ngắn, ngăn chi tiết ghi tên đầy đủ song ngữ", async () => {
    routeLearningPath();
    await open({ role: "backend", skill: "microservices" });
    const dialog = await screen.findByRole("dialog", { name: "Kiến trúc microservices (Microservices)" });
    expect(dialog).toBeTruthy();
    const cell = (await path()).querySelector('[data-skill="microservices"]') as HTMLElement;
    expect(cell.textContent).toContain("Kiến trúc microservices");
    expect(cell.textContent).not.toContain("(Microservices)");
    expect(box("Đã có Kiến trúc microservices")).toBeTruthy();
  });

  it("fr22: chưa đủ dữ liệu thì ô không mang loại", () => {
    const view = buildLearningPathView(clonePath("data_engineer"), (code) => code);
    expect(view.nodes.every((n) => n.kind === "unknown")).toBe(true);
  });

  it("fr23: ngăn của kỹ năng chọn một liệt kê lựa chọn thay thế", async () => {
    routeLearningPath();
    await open({ role: "backend", skill: "spring_boot" });
    const dialog = await screen.findByRole("dialog", { name: "Spring Boot" });
    expect(within(dialog).getByRole("list", { name: "Lựa chọn thay thế" }).textContent).toContain("Node.js");
  });

  it("fr23: kỹ năng thường không có mục lựa chọn thay thế", async () => {
    routeLearningPath();
    await open({ role: "backend", skill: "java" });
    const dialog = await screen.findByRole("dialog", { name: "Java" });
    expect(within(dialog).queryByRole("list", { name: "Lựa chọn thay thế" })).toBeNull();
  });
});

describe("fr22 ad17 #217 — envelope sai hợp đồng thì không đọc được", () => {
  const broken: [string, (env: LearningPathEnvelope) => void][] = [
    ["have không phải bool", (e) => ((e.data.stages[0].skills[0] as unknown as { have: unknown }).have = "yes")],
    ["tài liệu không phải https", (e) => (e.data.stages[0].skills[0].resource.url = "javascript:alert(1)")],
    ["rate thuộc ô khác", (e) => (e.data.stages[0].skills[0].rate.cell_id = "vn.khac")],
    ["shown mà không có giá trị", (e) => (e.data.stages[0].skills[0].rate.value = null)],
    ["null_data mà có nhóm", (e) => {
      e.data.stages[0].skills[0].rate.display = "null_data";
      e.data.stages[0].skills[0].rate.value = null;
    }],
    ["prerequisite_for không phải mảng chuỗi", (e) => ((e.data.stages[0].skills[0] as unknown as { prerequisite_for: unknown }).prerequisite_for = "x")],
    ["ready mà không có chặng", (e) => (e.data.stages = [])],
    ["chặng không có tên", (e) => (e.data.stages[0].title = " ")],
    ["choose_one không phải bool", (e) => ((e.data.stages[0] as unknown as { choose_one: unknown }).choose_one = "yes")],
    ["chọn một mà chỉ có một kỹ năng", (e) => (e.data.stages[1].choose_one = true)],
    ["chặng rỗng", (e) => (e.data.stages[0].skills = [])],
    ["thiếu ô của tỷ lệ", (e) => delete (e.meta.cells as Record<string, unknown>)[e.data.cell_id as string]],
    ["have_on_path lớn hơn path_size", (e) => (e.data.have_on_path = e.data.path_size + 1)],
    ["trả vai trò khác", (e) => (e.data.role = "qa")],
  ];
  for (const [name, mutate] of broken) {
    it(`fr22: ${name}`, async () => {
      const env = clonePath("backend");
      mutate(env);
      routeLearningPath({ learningPath: () => jsonResponse(200, env) });
      expect((await fetchLearningPath("backend", "entry", [])).kind).toBe("unreadable");
    });
  }

  it("fr22: mọi fixture của API giả đọc được", async () => {
    for (const [role, body] of [["backend", PATHS.backend], ["data_engineer", PATHS.data_engineer], ["ai_ml", PATHS.ai_ml]] as const) {
      routeLearningPath({ learningPath: () => jsonResponse(200, body) });
      expect((await fetchLearningPath(role, "entry", [])).kind).toBe("ok");
    }
  });
});
