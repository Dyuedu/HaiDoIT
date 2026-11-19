import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import SkillProfilePage from "@/app/ho-so-ky-nang/page";
import { NOT_ENOUGH_DATA } from "@/lib/city-shares-view";
import { writeProfile } from "@/lib/haido-keys";
import { fetchSkillRates, type SkillRatesEnvelope } from "@/lib/skill-rates";

import { jsonResponse } from "./helpers/fetch";
import { SKILL_RATES, UNKNOWN_CELL, routeSkillProfile } from "./helpers/skill-profile";

// #152 — hồ sơ kỹ năng của một vai trò ở một cấp, dựng từ response của API giả (#149). Thứ tự dòng, cờ `have` và số
// đếm core do API quyết (AD-22); web chỉ hiện.

async function openProfile(params: Record<string, string>) {
  const view = render(await SkillProfilePage({ searchParams: Promise.resolve(params) }));
  return view;
}

function skillList() {
  return screen.findByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ });
}

function rows(list: HTMLElement) {
  return within(list).getAllByRole("listitem");
}

function clone(key: keyof typeof SKILL_RATES): SkillRatesEnvelope {
  return structuredClone(SKILL_RATES[key]) as unknown as SkillRatesEnvelope;
}

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/ho-so-ky-nang");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fr19 fr18 #152 — cấp bậc", () => {
  it("fr18: URL không có level thì dùng cấp mặc định Mới vào nghề (#134)", async () => {
    const api = routeSkillProfile();
    await openProfile({ role: "backend" });
    await skillList();
    expect((screen.getByRole("combobox", { name: "Cấp bậc" }) as HTMLSelectElement).value).toBe("entry");
    expect(api.calls("/api/v1/skill-rates")[0].params).toMatchObject({ role: "backend", level: "entry" });
  });

  it("fr18: đổi cấp thì gọi lại với cấp mới và URL đổi theo", async () => {
    const user = userEvent.setup();
    const api = routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    await skillList();
    await user.selectOptions(screen.getByRole("combobox", { name: "Cấp bậc" }), "intern");
    await screen.findByText(/Backend · Intern chỉ có/);
    expect(api.calls("/api/v1/skill-rates").at(-1)?.params).toMatchObject({ role: "backend", level: "intern" });
    expect(window.location.search).toBe("?role=backend&level=intern");
  });
});

describe("fr19 #152 — dòng kỹ năng", () => {
  it("fr19: mỗi dòng có tên, tỷ lệ và nhóm, đúng thứ tự API gửi", async () => {
    routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    const list = await skillList();
    const items = rows(list);
    expect(items).toHaveLength(SKILL_RATES["backend|entry"].data.rows.length);
    expect(items[0].textContent).toContain("Java");
    expect(items[0].textContent).toContain("65,4%");
    expect(items[0].textContent).toContain("Cốt lõi");
    expect(items[1].textContent).toContain("SQL");
    expect(items[6].textContent).toContain("Thường gặp");
  });

  it("fr19: web không sắp lại, kể cả khi API gửi thứ tự khác", async () => {
    const env = clone("backend|entry");
    env.data.rows.reverse();
    routeSkillProfile({ skillRates: () => jsonResponse(200, env) });
    await openProfile({ role: "backend", level: "entry" });
    const items = rows(await skillList());
    expect(items[0].textContent).not.toContain("Java");
    expect(items[items.length - 1].textContent).toContain("Java");
  });

  it("fr19: tên kỹ năng tiếng Việt lấy từ danh sách kỹ năng", async () => {
    routeSkillProfile({ skillRates: () => jsonResponse(200, SKILL_RATES["backend|intern"]) });
    await openProfile({ role: "backend", level: "entry" });
    const list = await skillList();
    await waitFor(() => expect(list.textContent).toContain("Kiến trúc microservices"));
  });
});

describe("fr19 #152 — ô quay về và chưa đủ dữ liệu", () => {
  it("fr19: ô dưới 30 tin hiện nguyên văn câu quay về và n của ô đã dùng", async () => {
    routeSkillProfile();
    await openProfile({ role: "backend", level: "intern" });
    await skillList();
    const label = SKILL_RATES["backend|intern"].meta.cells["vn.backend"].fallback_label;
    expect(screen.getByText(label)).toBeTruthy();
    expect(screen.getByText("Tính trên 157 tin")).toBeTruthy();
  });

  it("fr19: không ô nào đủ 30 thì mỗi dòng ghi chưa đủ dữ liệu, không %, không nhóm, không dòng đếm", async () => {
    routeSkillProfile();
    await openProfile({ role: "data_engineer", level: "entry" });
    const list = await skillList();
    for (const item of rows(list)) {
      expect(item.textContent).toContain(NOT_ENOUGH_DATA);
      expect(item.textContent).not.toContain("%");
      expect(item.textContent).not.toMatch(/Cốt lõi|Thường gặp|Riêng của công ty/);
    }
    expect(screen.queryByTestId("core-count")).toBeNull();
  });
});

describe("fr19 #152 #151 — ô đủ mẫu mà mọi kỹ năng đều hiếm", () => {
  const EMPTY_TEXT = "Không kỹ năng nào được nhắc đủ thường xuyên để xếp vào nhóm cốt lõi hay phổ biến.";

  function allRare(): SkillRatesEnvelope {
    const env = clone("backend|entry");
    env.data.rows = [];
    env.data.core_size = 0;
    env.data.have_core = 0;
    return env;
  }

  it("fr19: rows rỗng với core_size = 0 là response đọc được (API trả đúng thế khi mọi kỹ năng dưới θ_common)", async () => {
    routeSkillProfile({ skillRates: () => jsonResponse(200, allRare()) });
    const result = await fetchSkillRates({ role: "backend", level: "entry", have: [] });
    expect(result.kind).toBe("ok");
  });

  it("fr19: rows rỗng mà core_size null vẫn là response hỏng", async () => {
    const env = allRare();
    env.data.core_size = null;
    env.data.have_core = null;
    routeSkillProfile({ skillRates: () => jsonResponse(200, env) });
    expect((await fetchSkillRates({ role: "backend", level: "entry", have: [] })).kind).toBe("unreadable");
  });

  it("fr19: rows rỗng mà core_size khác 0 vẫn là response hỏng", async () => {
    const env = allRare();
    env.data.core_size = 2;
    env.data.have_core = 0;
    routeSkillProfile({ skillRates: () => jsonResponse(200, env) });
    expect((await fetchSkillRates({ role: "backend", level: "entry", have: [] })).kind).toBe("unreadable");
  });

  it("fr19: màn hiện câu giải thích, không danh sách, không dòng đếm core, không báo lỗi", async () => {
    routeSkillProfile({ skillRates: () => jsonResponse(200, allRare()) });
    await openProfile({ role: "backend", level: "entry" });
    const text = await screen.findByText(EMPTY_TEXT);
    expect(text.textContent).not.toMatch(/\d/);
    expect(screen.queryByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ })).toBeNull();
    expect(screen.queryByTestId("core-count")).toBeNull();
    expect(screen.queryByText(/không đọc được/i)).toBeNull();
  });
});

describe("fr19 fr14 ad22 #152 — kỹ năng đã có", () => {
  it("fr19 ad22: hồ sơ java, sql, git thì ba ô được tick và dòng đếm lấy từ API", async () => {
    writeProfile({ v: 1, role: null, level: null, skills: ["java", "sql", "git"] });
    const api = routeSkillProfile();
    await openProfile({ role: "backend", level: "entry" });
    await skillList();
    await waitFor(() => expect(screen.getByTestId("core-count").textContent).toContain("3/6"));
    expect(screen.getByTestId("core-count").textContent).toContain("kỹ năng cốt lõi bạn đã có");
    expect(api.calls("/api/v1/skill-rates").at(-1)?.params.have).toBe("java,sql,git");
    expect((screen.getByRole("checkbox", { name: /^Đã có Java$/ }) as HTMLInputElement).checked).toBe(true);
    expect((screen.getByRole("checkbox", { name: /^Đã có Spring Boot$/ }) as HTMLInputElement).checked).toBe(false);
  });

  it("ad22: dòng đếm là số API gửi, không phải số web tự đếm", async () => {
    const env = clone("backend|entry");
    env.data.have_core = 5;
    routeSkillProfile({ skillRates: () => jsonResponse(200, env) });
    await openProfile({ role: "backend", level: "entry" });
    await skillList();
    expect(screen.getByTestId("core-count").textContent).toContain("5/6");
  });
});

describe("fr19 #152 — lỗi", () => {
  it("fr19: unknown_cell thì có thông báo, không có Thử lại, không có danh sách", async () => {
    routeSkillProfile();
    await openProfile({ role: "backend", level: "senior" });
    await screen.findByText(UNKNOWN_CELL.error.message);
    expect(screen.queryByRole("button", { name: "Thử lại" })).toBeNull();
    expect(screen.queryByRole("list", { name: /Kỹ năng theo tỷ lệ tin yêu cầu/ })).toBeNull();
  });

  it("fr19: mạng hỏng thì báo không đọc được, Thử lại tải lại được", async () => {
    const user = userEvent.setup();
    let broken = true;
    routeSkillProfile({
      skillRates: () => (broken ? Promise.reject(new TypeError("offline")) : jsonResponse(200, SKILL_RATES["backend|entry"])),
    });
    await openProfile({ role: "backend", level: "entry" });
    await screen.findByText(/Không đọc được số liệu/);
    broken = false;
    await user.click(screen.getByRole("button", { name: "Thử lại" }));
    await skillList();
  });

  it("fr19: mã vai trò lạ trong URL không được in như tên vai trò", async () => {
    routeSkillProfile();
    await openProfile({ role: "khong_co", level: "entry" });
    expect(screen.getByRole("heading", { level: 1 }).textContent).not.toContain("khong_co");
    expect(screen.getByText(/Không có vai trò này/)).toBeTruthy();
  });
});

describe("fr19 ad17 #152 — envelope sai hợp đồng thì không đọc được", () => {
  const broken: [string, (env: SkillRatesEnvelope) => void][] = [
    ["have không phải bool", (env) => ((env.data.rows[0] as unknown as { have: unknown }).have = "yes")],
    ["have_core lớn hơn core_size", (env) => (env.data.have_core = (env.data.core_size ?? 0) + 1)],
    ["chỉ một trong hai số đếm là null", (env) => (env.data.have_core = null)],
    ["rate không phải skill_rate", (env) => ((env.data.rows[0].rate as unknown as { kind: string }).kind = "level_share")],
    ["rate thuộc ô khác", (env) => (env.data.rows[0].rate.cell_id = "vn.khac")],
    ["thiếu ô đã dùng", (env) => delete (env.meta.cells as Record<string, unknown>)[env.data.cell_id]],
    ["shown mà không có giá trị", (env) => (env.data.rows[0].rate.value = null)],
    ["null_data mà có nhóm", (env) => {
      env.data.rows[0].rate.display = "null_data";
      env.data.rows[0].rate.value = null;
    }],
  ];

  for (const [name, mutate] of broken) {
    it(`fr19: ${name}`, async () => {
      const env = clone("backend|entry");
      mutate(env);
      routeSkillProfile({ skillRates: () => jsonResponse(200, env) });
      const result = await fetchSkillRates({ role: "backend", level: "entry", have: [] });
      expect(result.kind).toBe("unreadable");
    });
  }

  it("fr19: envelope đúng hợp đồng thì đọc được, cả khi chưa đủ dữ liệu", async () => {
    routeSkillProfile();
    expect((await fetchSkillRates({ role: "backend", level: "entry", have: [] })).kind).toBe("ok");
    expect((await fetchSkillRates({ role: "data_engineer", level: "entry", have: [] })).kind).toBe("ok");
  });
});
