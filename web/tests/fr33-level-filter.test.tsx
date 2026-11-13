import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { MapScreen } from "@/app/components/map/map-screen";
import { DEFAULT_LEVEL, LEVEL_OPTIONS, levelLabel } from "@/lib/labels";

import { buildEnvelope, fakeEnvelope } from "./fixtures/envelopes";
import { deferred, jsonResponse, routeCityShares } from "./helpers/fetch";
import { levelSelect, optionLabels, pick, roleSelect, selectedLabel } from "./helpers/filters";

const LOADING = "Đang tải số liệu…";
const LEVEL_NAMES = [
  "Mới vào nghề",
  "Intern",
  "Fresher",
  "Junior",
  "Mid",
  "Senior",
  "Lead",
  "Chưa ghi cấp bậc",
  "Mọi cấp bậc",
];

const entry = (role: "all" | "ai_ml" | "backend") => () => jsonResponse(200, fakeEnvelope(role, "entry"));
const every = (role: "all" | "ai_ml" | "backend") => () => jsonResponse(200, fakeEnvelope(role, "all"));

/** Envelope của một cấp khác `entry` và `all` (bản giả chỉ có hai cấp đó), dựng theo hình API. */
function senior() {
  return buildEnvelope({
    role: "all",
    level: "senior",
    totalN: 512,
    rows: [
      { city: "ha_noi", n: 210, value: 210 / 512, display: "shown" },
      { city: "ho_chi_minh", n: 242, value: 242 / 512, display: "shown" },
      { city: "da_nang", n: 11, value: 11 / 512, display: "low_sample_shown" },
      { city: "other", n: 18, value: 18 / 512, display: "low_sample_shown" },
      { city: "unknown", n: 31, value: 31 / 512, display: "shown" },
    ],
  });
}

function lead() {
  return buildEnvelope({
    role: "all",
    level: "lead",
    totalN: 60,
    rows: [
      { city: "ha_noi", n: 30, value: 0.5, display: "shown" },
      { city: "ho_chi_minh", n: 29, value: 29 / 60, display: "low_sample_shown" },
      { city: "da_nang", n: 1, value: 1 / 60, display: "low_sample_shown" },
      { city: "other", n: 0, value: 0, display: "low_sample_shown" },
      { city: "unknown", n: 0, value: 0, display: "low_sample_shown" },
    ],
  });
}

function modeButton(name: string) {
  return within(screen.getByRole("group", { name: "Lối xem" })).getByRole("button", { name });
}

function cityButton(label: string) {
  return screen.getByRole("button", { name: new RegExp(`^${label}:`) });
}

function fill(button: HTMLElement) {
  const element = button.querySelector<HTMLElement>('[data-part="fill"]');
  if (!element) throw new Error("thiếu phần tô của thanh");
  return element;
}

async function openScreen() {
  const user = userEvent.setup();
  render(<MapScreen />);
  await screen.findByRole("button", { name: /^Hà Nội:/ });
  return user;
}

describe("fr33 #163 — bộ lọc cấp bậc mở ở mặc định của #134", () => {
  it("fr33: mặc định là nhóm mới vào nghề (entry) và lượt gọi đầu mang level=entry", async () => {
    const fetchMock = routeCityShares({ "all|entry": [entry("all")] });
    await openScreen();

    expect(DEFAULT_LEVEL).toBe("entry");
    expect(String(fetchMock.mock.calls[0][0])).toBe("/api/v1/city-shares?role=all&level=entry&years=any");
    expect(selectedLabel(levelSelect())).toBe("Mới vào nghề");
    expect(levelSelect().value).toBe("entry");
  });

  it("fr33: lựa chọn đúng danh sách của #134, theo thứ tự, trong một <select>", async () => {
    routeCityShares({ "all|entry": [entry("all")] });
    await openScreen();

    expect(optionLabels(levelSelect())).toEqual(LEVEL_NAMES);
    expect(LEVEL_OPTIONS.map((option) => option.code)).toEqual([
      "entry",
      "intern",
      "fresher",
      "junior",
      "mid",
      "senior",
      "lead",
      "unknown",
      "all",
    ]);
    expect(Array.from(levelSelect().options).map((option) => option.value)).toEqual(
      LEVEL_OPTIONS.map((option) => option.code),
    );
    expect(levelSelect().tagName).toBe("SELECT");
    expect(levelSelect().hasAttribute("aria-pressed")).toBe(false);
  });

  it("fr33: ô đủ 44px, có viền focus chung và nhóm chữ giải thích nhóm mới vào nghề", async () => {
    routeCityShares({ "all|entry": [entry("all")] });
    await openScreen();

    expect(levelSelect().className).toContain("min-h-target");
    screen.getByText("Mới vào nghề gồm Intern, Fresher và Junior.");
    expect(levelLabel("entry")).toBe("Mới vào nghề");
    expect(levelLabel("unknown")).toBe("Chưa ghi cấp bậc");
    expect(levelLabel("khong_co_cap")).toBe("khong_co_cap");
  });

  it("fr33: ô cấp bậc được mô tả bằng dòng chú thích (aria-describedby trỏ đúng dòng đó)", async () => {
    routeCityShares({ "all|entry": [entry("all")] });
    await openScreen();

    const noteId = levelSelect().getAttribute("aria-describedby");
    expect(noteId).toBeTruthy();
    expect(document.getElementById(noteId as string)?.textContent).toBe("Mới vào nghề gồm Intern, Fresher và Junior.");
  });

  it("fr33: <caption> của bảng nêu cấp bậc đang chọn và đổi theo cấp", async () => {
    routeCityShares({ "all|entry": [entry("all")], "all|senior": [() => jsonResponse(200, senior())] });
    const user = await openScreen();
    await user.click(modeButton("Bảng"));
    expect(screen.getByRole("table").querySelector("caption")?.textContent).toContain("· Mới vào nghề");

    await pick(user, levelSelect(), "Senior");
    await screen.findByRole("table");
    expect(screen.getByRole("table").querySelector("caption")?.textContent).toContain("· Senior");
  });

  it("fr33: số mở ra là số của nhóm entry, không phải của mọi cấp", async () => {
    routeCityShares({ "all|entry": [entry("all")] });
    await openScreen();

    const haNoi = cityButton("Hà Nội");
    expect(haNoi.textContent).toContain("41,7%");
    expect(haNoi.textContent).toContain("848 tin");
    expect(screen.getByRole("figure").textContent).toContain("Mới vào nghề");
  });
});

describe("fr33 #163 — đổi cấp bậc thì bảng và biểu đồ đổi cùng nhau", () => {
  it("fr33: bấm Senior gọi lại với level=senior, hiện đang tải, rồi thanh và bảng cùng ra số của Senior", async () => {
    const pending = deferred<Response>();
    const fetchMock = routeCityShares({
      "all|entry": [entry("all")],
      "all|senior": [() => pending.promise],
    });
    const user = await openScreen();

    await pick(user, levelSelect(), "Senior");

    expect(String(fetchMock.mock.calls[1][0])).toBe("/api/v1/city-shares?role=all&level=senior&years=any");
    expect(screen.getByRole("status").textContent).toBe(LOADING);
    expect(screen.queryByRole("button", { name: /^Hà Nội:/ })).toBeNull();
    expect(selectedLabel(levelSelect())).toBe("Senior");

    await act(async () => pending.resolve(jsonResponse(200, senior())));
    const haNoi = await screen.findByRole("button", { name: /^Hà Nội:/ });
    expect(haNoi.textContent).toContain("210 tin");
    expect(fill(haNoi).style.width).toBe(`${(210 / 512) * 100}%`);

    await user.click(modeButton("Bảng"));
    const table = screen.getByRole("table");
    const haNoiRow = within(table).getByRole("row", { name: /Hà Nội/ });
    expect(within(haNoiRow).getAllByRole("cell").map((cell) => cell.textContent).slice(0, 2)).toEqual([
      "41,0%",
      "210",
    ]);
    const total = within(table).getByRole("row", { name: /Tổng/ });
    expect(within(total).getAllByRole("cell")[1].textContent).toBe("512");
  });

  it("fr33: đổi giữa entry và mọi cấp đổi số ở cả thanh lẫn bảng", async () => {
    routeCityShares({ "all|entry": [entry("all")], "all|all": [every("all")] });
    const user = await openScreen();
    expect(cityButton("Hà Nội").textContent).toContain("848 tin");

    await pick(user, levelSelect(), "Mọi cấp bậc");
    await screen.findByText(/1\.490 tin/);
    expect(cityButton("Hà Nội").textContent).toContain("41,6%");

    await user.click(modeButton("Bảng"));
    const table = screen.getByRole("table");
    expect(within(within(table).getByRole("row", { name: /Hà Nội/ })).getAllByRole("cell")[1].textContent).toBe(
      "1.490",
    );
    expect(within(within(table).getByRole("row", { name: /Tổng/ })).getAllByRole("cell")[1].textContent).toBe(
      "3.586",
    );
  });

  it("fr33: đang ở lối Bảng thì đổi cấp vẫn giữ lối Bảng và bảng đổi số", async () => {
    routeCityShares({ "all|entry": [entry("all")], "all|senior": [() => jsonResponse(200, senior())] });
    const user = await openScreen();
    await user.click(modeButton("Bảng"));
    const total = () =>
      within(within(screen.getByRole("table")).getByRole("row", { name: /Tổng/ })).getAllByRole("cell")[1]
        .textContent;
    expect(total()).toBe("2.036");

    await pick(user, levelSelect(), "Senior");
    await screen.findByRole("table");

    expect(modeButton("Bảng").getAttribute("aria-pressed")).toBe("true");
    expect(total()).toBe("512");
  });

  it("fr33: bấm cấp liên tiếp thì bỏ response về muộn của cấp cũ", async () => {
    const slowSenior = deferred<Response>();
    routeCityShares({
      "all|entry": [entry("all")],
      "all|senior": [() => slowSenior.promise],
      "all|lead": [() => jsonResponse(200, lead())],
    });
    const user = await openScreen();

    await pick(user, levelSelect(), "Senior");
    await pick(user, levelSelect(), "Lead");
    const haNoi = await screen.findByRole("button", { name: /^Hà Nội:/ });
    expect(haNoi.textContent).toContain("30 tin");

    await act(async () => slowSenior.resolve(jsonResponse(200, senior())));

    expect(cityButton("Hà Nội").textContent).toContain("30 tin");
    expect(screen.queryByText(/210 tin/)).toBeNull();
    expect(selectedLabel(levelSelect())).toBe("Lead");
  });

  it("fr33: đổi vai trò giữ nguyên cấp bậc đang chọn và lượt gọi mang cả hai", async () => {
    const fetchMock = routeCityShares({
      "all|entry": [entry("all")],
      "all|senior": [() => jsonResponse(200, senior())],
      "ai_ml|senior": [() => jsonResponse(200, { ...senior(), data: { ...senior().data, role: "ai_ml" } })],
    });
    const user = await openScreen();
    await pick(user, levelSelect(), "Senior");
    await screen.findByText(/210 tin/);

    await pick(user, roleSelect(), "AI/ML");
    await screen.findByRole("button", { name: /^Hà Nội:/ });

    const urls = fetchMock.mock.calls.map((call) => String(call[0]));
    expect(urls.at(-1)).toBe("/api/v1/city-shares?role=ai_ml&level=senior&years=any");
    expect(selectedLabel(levelSelect())).toBe("Senior");
  });

  it("fr33: bấm lại cấp đang chọn không gọi API thêm", async () => {
    const fetchMock = routeCityShares({ "all|entry": [entry("all")] });
    const user = await openScreen();

    await pick(user, levelSelect(), "Mới vào nghề");

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("fr33: cấp không có tin hiện thông báo kèm ngày snapshot, bộ chọn cấp vẫn bấm được rồi đổi cấp khác ra số", async () => {
    routeCityShares({
      "all|entry": [entry("all")],
      "all|lead": [
        () =>
          jsonResponse(404, {
            error: {
              code: "unknown_cell",
              message: "Vai trò đã chọn không có tin nào ở cấp bậc này của snapshot này.",
              snapshot_date: "2026-11-03",
            },
          }),
      ],
      "all|all": [every("all")],
    });
    const user = await openScreen();

    await pick(user, levelSelect(), "Lead");
    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toContain("không có tin nào ở cấp bậc này");
    expect(alert.textContent).toContain("03/11/2026");
    expect(screen.queryByRole("button", { name: "Thử lại" })).toBeNull();
    expect(selectedLabel(levelSelect())).toBe("Lead");

    await pick(user, levelSelect(), "Mọi cấp bậc");
    await screen.findByRole("button", { name: /^Hà Nội:/ });
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("fr33: Thử lại sau lỗi mạng giữ cấp đã chọn", async () => {
    const fetchMock = routeCityShares({
      "all|entry": [entry("all")],
      "all|senior": [
        () => jsonResponse(502, { error: { code: "api_unavailable", message: "API tắt.", snapshot_date: null } }),
        () => jsonResponse(200, senior()),
      ],
    });
    const user = await openScreen();
    await pick(user, levelSelect(), "Senior");
    await screen.findByRole("alert");

    await user.click(screen.getByRole("button", { name: "Thử lại" }));
    await screen.findByRole("button", { name: /^Hà Nội:/ });

    expect(String(fetchMock.mock.calls.at(-1)?.[0])).toBe("/api/v1/city-shares?role=all&level=senior&years=any");
  });

  it("fr33: response có data.level khác cấp đã hỏi bị coi là không đọc được, không hiện số của cấp khác", async () => {
    routeCityShares({ "all|entry": [entry("all")], "all|senior": [entry("all")] }, { echoLevel: false });
    const user = userEvent.setup();
    render(<MapScreen />);
    await screen.findByRole("button", { name: /^Hà Nội:/ });

    await pick(user, levelSelect(), "Senior");

    expect((await screen.findByRole("alert")).textContent).toBe("Không đọc được số liệu. Thử lại sau.");
    expect(screen.queryByRole("figure")).toBeNull();
  });
});

describe("fr33 #163 — thành phố dưới 30 tin ở cấp đã chọn bị làm mờ như bản đồ mọi cấp", () => {
  it("fr33: AI/ML ở entry: Đà Nẵng n = 11 mờ có nhãn mẫu nhỏ, Hà Nội n = 241 không mờ", async () => {
    routeCityShares({ "all|entry": [entry("all")], "ai_ml|entry": [entry("ai_ml")] });
    const user = await openScreen();
    await pick(user, roleSelect(), "AI/ML");
    const daNang = await screen.findByRole("button", { name: /^Đà Nẵng:/ });

    expect(fill(daNang).getAttribute("data-low-sample")).toBe("true");
    expect(daNang.textContent).toContain("Cỡ mẫu nhỏ (n = 11 < 30): số liệu chỉ để tham khảo");
    expect(daNang.textContent).not.toContain("2,2%");
    expect(fill(cityButton("Hà Nội")).getAttribute("data-low-sample")).toBe("false");

    await user.hover(daNang);
    expect(daNang.textContent).toContain("2,2%");
  });

  it("fr33: mờ theo n của cấp đã chọn: cùng Đà Nẵng, n = 11 ở entry và n = 21 ở mọi cấp", async () => {
    routeCityShares({
      "all|entry": [entry("all")],
      "ai_ml|entry": [entry("ai_ml")],
      "ai_ml|all": [every("ai_ml")],
    });
    const user = await openScreen();
    await pick(user, roleSelect(), "AI/ML");
    expect((await screen.findByRole("button", { name: /^Đà Nẵng:/ })).textContent).toContain("n = 11 < 30");

    await pick(user, levelSelect(), "Mọi cấp bậc");

    const daNang = await screen.findByText(/n = 21 < 30/);
    expect(daNang.closest("button")).toBe(cityButton("Đà Nẵng"));
    expect(fill(cityButton("Đà Nẵng")).getAttribute("data-low-sample")).toBe("true");
  });

  it("fr33: ở lối Bảng ô của thành phố mẫu nhỏ ghi 'chưa đủ dữ liệu' kèm n của cấp", async () => {
    routeCityShares({ "all|entry": [entry("all")], "backend|entry": [entry("backend")] });
    const user = await openScreen();
    await pick(user, roleSelect(), "Backend");
    await screen.findByRole("button", { name: /^Hà Nội:/ });
    await user.click(modeButton("Bảng"));

    const table = screen.getByRole("table");
    const haNoi = within(within(table).getByRole("row", { name: /Hà Nội/ })).getAllByRole("cell");
    expect(haNoi.map((cell) => cell.textContent)).toEqual(["chưa đủ dữ liệu", "20", "Cỡ mẫu nhỏ (n = 20 < 30)"]);
    const daNang = within(within(table).getByRole("row", { name: /Đà Nẵng/ })).getAllByRole("cell");
    expect(daNang.map((cell) => cell.textContent)).toEqual(["chưa đủ dữ liệu", "3", "Cỡ mẫu nhỏ (n = 3 < 30)"]);
  });

  it("fr33: web chỉ đọc display của API: n = 30 shown không mờ, n = 29 mờ", async () => {
    routeCityShares({ "all|entry": [entry("all")], "all|lead": [() => jsonResponse(200, lead())] });
    const user = await openScreen();

    await pick(user, levelSelect(), "Lead");
    const haNoi = await screen.findByRole("button", { name: /^Hà Nội:/ });

    expect(fill(haNoi).getAttribute("data-low-sample")).toBe("false");
    expect(fill(cityButton("TP.HCM")).getAttribute("data-low-sample")).toBe("true");
    expect(cityButton("TP.HCM").textContent).toContain("Cỡ mẫu nhỏ (n = 29 < 30)");
  });
});

describe("fr33 #163, #293 — bàn phím", () => {
  it("fr33: Tab tới bộ chọn cấp bậc rồi chọn giá trị, gửi level mới", async () => {
    routeCityShares({ "all|entry": [entry("all")], "all|senior": [() => jsonResponse(200, senior())] });
    const user = await openScreen();

    act(() => roleSelect().focus());
    await user.tab();
    expect(document.activeElement).toBe(levelSelect());
    // jsdom và user-event không có phím mũi tên của <select>: chọn giá trị bằng selectOptions (đường con trỏ).
    // Đổi bằng mũi tên được kiểm trong trình duyệt thật (tdd.md của #293).
    await pick(user, levelSelect(), "Senior");

    expect(levelSelect().value).toBe("senior");
    await screen.findByText(/210 tin/);
  });
});
