import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { MapScreen } from "@/app/components/map/map-screen";

import { fakeEnvelope } from "./fixtures/envelopes";
import { deferred, jsonResponse, routeCityShares } from "./helpers/fetch";
import { levelSelect, optionLabels, pick, roleSelect, selectedLabel, yearsSelect } from "./helpers/filters";

const codes = (select: HTMLSelectElement) => Array.from(select.options).map((option) => option.value);
const tokens = (element: Element | null) => (element?.getAttribute("class") ?? "").split(/\s+/).filter(Boolean);

const ok = (role: "all" | "ai_ml" | "backend") => () => jsonResponse(200, fakeEnvelope(role));

async function openScreen() {
  const user = userEvent.setup();
  render(<MapScreen />);
  await screen.findByRole("button", { name: /^Hà Nội:/ });
  return user;
}

describe("fr33 #293 — ba bộ lọc là <select> có nhãn", () => {
  it("fr33: mỗi bộ lọc là một combobox có <label for> hiện, không còn nhóm chip", async () => {
    routeCityShares({ all: [ok("all")] });
    await openScreen();

    for (const [select, text] of [
      [roleSelect(), "Vai trò"],
      [levelSelect(), "Cấp bậc"],
      [yearsSelect(), "Số năm kinh nghiệm"],
    ] as const) {
      expect(select.tagName).toBe("SELECT");
      const label = document.querySelector(`label[for="${select.id}"]`);
      expect(label?.textContent).toBe(text);
      expect(label?.getAttribute("aria-hidden")).toBeNull();
      // Nhãn hiện thật: không `sr-only`, không `hidden` (kể cả có tiền tố như `sm:hidden`).
      const labelTokens = tokens(label ?? null);
      expect(labelTokens.filter((t) => t === "sr-only" || t.split(":").pop() === "hidden")).toEqual([]);
      expect(select.hasAttribute("aria-pressed")).toBe(false);
      expect(select.className).toContain("min-h-target");
    }
    for (const name of ["Vai trò", "Cấp bậc", "Số năm kinh nghiệm"]) {
      expect(screen.queryByRole("group", { name })).toBeNull();
    }
    // Cụm Lối xem vẫn là nút.
    screen.getByRole("group", { name: "Lối xem" });
  });

  it("fr33: option và thứ tự viết cứng (không đọc labels.ts); vai trò không chia optgroup; mặc định all, entry, any", async () => {
    routeCityShares({ all: [ok("all")] });
    await openScreen();

    // Thứ tự viết cứng: vai trò theo `[roles]` của config/rules.toml với "all" đứng đầu, rồi cấp bậc, rồi số năm.
    expect(codes(roleSelect())).toEqual([
      "all", "embedded", "ai_ml", "data_scientist", "data_engineer", "data_analyst", "qa", "devops", "security",
      "it_infra", "mobile", "frontend", "backend", "fullstack", "ba_po_pm", "ui_ux", "game", "other",
    ]);
    expect(codes(levelSelect())).toEqual([
      "entry", "intern", "fresher", "junior", "mid", "senior", "lead", "unknown", "all",
    ]);
    expect(codes(yearsSelect())).toEqual(["any", "0", "1", "2", "3", "5"]);
    expect(roleSelect().options[0].textContent).toBe("Tất cả");
    expect(roleSelect().querySelector("optgroup")).toBeNull();
    expect(optionLabels(levelSelect())).toEqual([
      "Mới vào nghề", "Intern", "Fresher", "Junior", "Mid", "Senior", "Lead", "Chưa ghi cấp bậc", "Mọi cấp bậc",
    ]);
    expect(optionLabels(yearsSelect())).toEqual([
      "Mọi số năm", "Không cần kinh nghiệm", "Tối đa 1 năm", "Tối đa 2 năm", "Tối đa 3 năm", "Tối đa 5 năm",
    ]);
    expect([roleSelect().value, levelSelect().value, yearsSelect().value]).toEqual(["all", "entry", "any"]);
  });

  it("fr33: ghi chú nối bằng aria-describedby: cấp bậc nói nhóm mới vào nghề, số năm nói số năm tối thiểu", async () => {
    routeCityShares({ all: [ok("all")] });
    await openScreen();

    const levelNote = document.getElementById(levelSelect().getAttribute("aria-describedby") as string);
    expect(levelNote?.textContent).toBe("Mới vào nghề gồm Intern, Fresher và Junior.");
    const yearsNote = document.getElementById(yearsSelect().getAttribute("aria-describedby") as string);
    expect(yearsNote?.textContent).toBe("Tính theo số năm tối thiểu tin yêu cầu.");
  });

  it("fr33: ba ô nằm trong một lưới: một cột ở điện thoại, ba cột từ sm; ô rộng hết cột để nhãn dài không tràn", async () => {
    routeCityShares({ all: [ok("all")] });
    await openScreen();

    const grid = roleSelect().closest(".grid");
    expect(grid?.className).toContain("grid-cols-1");
    expect(grid?.className).toContain("sm:grid-cols-3");
    expect(levelSelect().closest(".grid")).toBe(grid);
    expect(yearsSelect().closest(".grid")).toBe(grid);
    for (const select of [roleSelect(), levelSelect(), yearsSelect()]) {
      expect(select.className).toContain("w-full");
      expect(select.className).toContain("min-w-0");
    }
  });
});

describe("fr33 #293 — đổi bộ lọc như chip cũ", () => {
  it("fr33: chọn lại đúng giá trị đang chọn không gọi lại API, ở cả ba ô", async () => {
    const fetchMock = routeCityShares({ all: [ok("all")] });
    const user = await openScreen();
    const before = fetchMock.mock.calls.length;

    await pick(user, roleSelect(), "Tất cả");
    await pick(user, levelSelect(), "Mới vào nghề");
    await pick(user, yearsSelect(), "Mọi số năm");

    expect(fetchMock.mock.calls.length).toBe(before);
    expect(screen.getByRole("status").textContent).toBe("");
  });

  it("fr33: đổi ô nào cũng gửi đúng một lượt gọi mới, giữ hai ô còn lại", async () => {
    const fetchMock = routeCityShares({ all: [ok("all")], ai_ml: [ok("ai_ml")], backend: [ok("backend")] });
    const user = await openScreen();

    await pick(user, roleSelect(), "Backend");
    await pick(user, levelSelect(), "Senior");
    await pick(user, yearsSelect(), "Tối đa 2 năm");

    const urls = fetchMock.mock.calls.map((call) => String(call[0]));
    expect(urls.slice(1)).toEqual([
      "/api/v1/city-shares?role=backend&level=entry&years=any",
      "/api/v1/city-shares?role=backend&level=senior&years=any",
      "/api/v1/city-shares?role=backend&level=senior&years=2",
    ]);
    expect([selectedLabel(roleSelect()), selectedLabel(levelSelect()), selectedLabel(yearsSelect())]).toEqual([
      "Backend",
      "Senior",
      "Tối đa 2 năm",
    ]);
  });

  it("fr33: response về muộn của lựa chọn cũ bị bỏ khi đổi ô khác", async () => {
    const slow = deferred<Response>();
    routeCityShares({ all: [ok("all")], ai_ml: [() => slow.promise], backend: [ok("backend")] });
    const user = await openScreen();

    await pick(user, roleSelect(), "AI/ML");
    await pick(user, roleSelect(), "Backend");
    const daNang = await screen.findByRole("button", { name: /^Đà Nẵng:/ });
    expect(daNang.textContent).toContain("n = 9 < 30");

    await act(async () => slow.resolve(jsonResponse(200, fakeEnvelope("ai_ml"))));

    expect(screen.getByRole("button", { name: /^Đà Nẵng:/ }).textContent).toContain("n = 9 < 30");
    expect(selectedLabel(roleSelect())).toBe("Backend");
  });

  it("fr33: ba ô vẫn đổi được khi đang tải, và sau lỗi bấm Thử lại giữ nguyên lựa chọn", async () => {
    const pending = deferred<Response>();
    const fetchMock = routeCityShares({
      all: [ok("all")],
      ai_ml: [() => pending.promise],
    });
    const user = await openScreen();

    await pick(user, roleSelect(), "AI/ML");
    expect(screen.getByRole("status").textContent).toBe("Đang tải số liệu…");
    expect(roleSelect().disabled).toBe(false);
    expect(levelSelect().disabled).toBe(false);
    expect(yearsSelect().disabled).toBe(false);
    await act(async () => pending.resolve(jsonResponse(502, { error: { code: "api_unavailable", message: "API tắt.", snapshot_date: null } })));

    await screen.findByRole("alert");
    expect(roleSelect().disabled).toBe(false);
    expect(selectedLabel(roleSelect())).toBe("AI/ML");
    const callsBefore = fetchMock.mock.calls.length;
    await user.click(screen.getByRole("button", { name: "Thử lại" }));
    expect(String(fetchMock.mock.calls[callsBefore][0])).toBe("/api/v1/city-shares?role=ai_ml&level=entry&years=any");
    expect(selectedLabel(roleSelect())).toBe("AI/ML");
  });
});

describe("fr33 #293 — chốt AC 3 bằng class và CSS (jsdom không có layout)", () => {
  const FORBIDDEN = ["outline-none", "focus:outline-none", "focus-visible:outline-none", "transition-colors", "transition-all"];

  it("fr33: ô chọn cao tối thiểu 44px ở mọi khổ, giữ vòng focus chung và không animate outline", async () => {
    routeCityShares({ all: [ok("all")] });
    await openScreen();

    for (const select of [roleSelect(), levelSelect(), yearsSelect()]) {
      const list = tokens(select);
      expect(list).toContain("min-h-target"); // không tiền tố: `sm:min-h-target` chỉ có từ khổ sm trở lên
      expect(list.filter((t) => /^[a-z-]+:min-h-/.test(t))).toEqual([]);
      expect(list.filter((t) => FORBIDDEN.includes(t))).toEqual([]);
    }
  });

  it("fr33: lưới bộ lọc và các lớp bọc không đặt min-w cố định, nên không ép trang tràn ngang ở 360px", async () => {
    routeCityShares({ all: [ok("all")] });
    await openScreen();

    const grid = roleSelect().closest(".grid");
    expect(grid).not.toBeNull();
    for (let el: Element | null = roleSelect(); el && el !== document.body; el = el.parentElement) {
      const bad = tokens(el).filter((t) => /(^|:)min-w-/.test(t) && !t.endsWith("min-w-0"));
      expect(bad, el.tagName + "." + tokens(el).join(".")).toEqual([]);
    }
  });

  it("fr33: globals.css giữ token 44px và vòng :focus-visible 2px màu accent, lệch 2px", () => {
    const css = readFileSync(resolve(process.cwd(), "app/globals.css"), "utf-8");

    expect(css).toMatch(/--spacing-target:\s*44px\s*;/);
    expect(css).toMatch(/--color-primary:\s*#c5f36a\s*;/i);
    const rule = css.match(/:focus-visible\s*\{([^}]*)\}/);
    expect(rule, "không thấy luật :focus-visible toàn cục").not.toBeNull();
    expect(rule?.[1]).toMatch(/outline:\s*2px\s+solid\s+var\(--color-primary\)\s*;/);
    expect(rule?.[1]).toMatch(/outline-offset:\s*2px\s*;/);
  });
});
