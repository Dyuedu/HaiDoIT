import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { MapScreen } from "@/app/components/map/map-screen";
import { fetchCityShares } from "@/lib/city-shares";
import { buildCitySharesView } from "@/lib/city-shares-view";
import { DEFAULT_YEARS, YEARS_OPTIONS, yearsLabel } from "@/lib/labels";

import { buildEnvelope, fakeEnvelope } from "./fixtures/envelopes";
import { deferred, jsonResponse, routeCityShares } from "./helpers/fetch";

const LOADING = "Đang tải số liệu…";
const YEARS_NAMES = [
  "Mọi số năm",
  "Không cần kinh nghiệm",
  "Tối đa 1 năm",
  "Tối đa 2 năm",
  "Tối đa 3 năm",
  "Tối đa 5 năm",
];

afterEach(() => {
  vi.unstubAllGlobals();
});

const entry = () => jsonResponse(200, fakeEnvelope("all", "entry"));

/** Envelope của một mốc số năm, dựng theo hình API (#280). */
function upTo(years: string, opts: { level?: string; role?: string; unstated?: number; haNoi?: number } = {}) {
  const haNoi = opts.haNoi ?? 120;
  const total = haNoi + 80 + 20 + 5 + 15;
  return buildEnvelope({
    role: opts.role ?? "all",
    level: opts.level ?? "entry",
    years,
    yearsUnstated: opts.unstated ?? 37,
    totalN: total,
    rows: [
      { city: "ha_noi", n: haNoi, value: haNoi / total, display: "shown" },
      { city: "ho_chi_minh", n: 80, value: 80 / total, display: "shown" },
      { city: "da_nang", n: 20, value: 20 / total, display: "low_sample_shown" },
      { city: "other", n: 5, value: 5 / total, display: "low_sample_shown" },
      { city: "unknown", n: 15, value: 15 / total, display: "low_sample_shown" },
    ],
  });
}

function yearsGroup() {
  return screen.getByRole("group", { name: "Số năm kinh nghiệm" });
}

function yearsButton(name: string) {
  return within(yearsGroup()).getByRole("button", { name });
}

function levelButton(name: string) {
  return within(screen.getByRole("group", { name: "Cấp bậc" })).getByRole("button", { name });
}

async function openScreen() {
  const user = userEvent.setup();
  render(<MapScreen />);
  await screen.findByRole("button", { name: /^Hà Nội:/ });
  return user;
}

function lastUrl(fetchMock: ReturnType<typeof routeCityShares>) {
  return String(fetchMock.mock.calls.at(-1)![0]);
}

describe("fr33 #280 — bộ chọn số năm kinh nghiệm", () => {
  it("fr33: mở ở 'Mọi số năm', lượt gọi đầu mang years=any", async () => {
    const fetchMock = routeCityShares({ "all|entry": [entry] });
    await openScreen();

    expect(DEFAULT_YEARS).toBe("any");
    expect(String(fetchMock.mock.calls[0][0])).toBe("/api/v1/city-shares?role=all&level=entry&years=any");
    expect(yearsButton("Mọi số năm").getAttribute("aria-pressed")).toBe("true");
  });

  it("fr33: đúng sáu lựa chọn theo thứ tự, mỗi lựa chọn một <button aria-pressed> cao 44px", async () => {
    routeCityShares({ "all|entry": [entry] });
    await openScreen();

    const buttons = within(yearsGroup()).getAllByRole("button");
    expect(buttons.map((b) => b.textContent)).toEqual(YEARS_NAMES);
    expect(YEARS_OPTIONS.map((o) => o.code)).toEqual(["any", "0", "1", "2", "3", "5"]);
    for (const button of buttons) {
      expect(button.getAttribute("type")).toBe("button");
      expect(button.hasAttribute("aria-pressed")).toBe(true);
      expect(button.className).toContain("min-h-target");
    }
    expect(yearsLabel("2")).toBe("Tối đa 2 năm");
    expect(yearsLabel("la")).toBe("la");
  });

  it("fr33: bấm 'Tối đa 2 năm' gửi years=2, giữ cấp, rồi hiện số của mốc đó", async () => {
    const fetchMock = routeCityShares({ "all|entry|any": [entry], "all|entry|2": [() => jsonResponse(200, upTo("2"))] });
    const user = await openScreen();

    await user.click(yearsButton("Tối đa 2 năm"));
    expect(lastUrl(fetchMock)).toBe("/api/v1/city-shares?role=all&level=entry&years=2");
    expect(await screen.findByRole("button", { name: /^Hà Nội: .*, 120 tin/ })).toBeTruthy();
    expect(yearsButton("Tối đa 2 năm").getAttribute("aria-pressed")).toBe("true");
  });

  it("fr33: đổi cấp giữ số năm, đổi vai trò giữ cả hai", async () => {
    const fetchMock = routeCityShares({
      "all|entry|any": [entry],
      "all|entry|3": [() => jsonResponse(200, upTo("3"))],
      "all|senior|3": [() => jsonResponse(200, upTo("3", { level: "senior" }))],
      "backend|senior|3": [() => jsonResponse(200, upTo("3", { level: "senior", role: "backend" }))],
    });
    const user = await openScreen();

    await user.click(yearsButton("Tối đa 3 năm"));
    await screen.findByText(/37 tin/);
    await user.click(levelButton("Senior"));
    expect(lastUrl(fetchMock)).toBe("/api/v1/city-shares?role=all&level=senior&years=3");
    await screen.findByText(/37 tin/);
    await user.click(within(screen.getByRole("group", { name: "Vai trò" })).getByRole("button", { name: "Backend" }));
    expect(lastUrl(fetchMock)).toBe("/api/v1/city-shares?role=backend&level=senior&years=3");
  });

  it("fr33: đang lọc số năm thì nói rõ bao nhiêu tin bị bỏ vì không ghi số năm; 'Mọi số năm' thì không", async () => {
    routeCityShares({ "all|entry|any": [entry], "all|entry|1": [() => jsonResponse(200, upTo("1", { unstated: 1234 }))] });
    const user = await openScreen();

    expect(screen.queryByText(/không ghi số năm kinh nghiệm/)).toBeNull();
    await user.click(yearsButton("Tối đa 1 năm"));
    const note = await screen.findByText(/không ghi số năm kinh nghiệm/);
    expect(note.textContent).toBe("1.234 tin của Tất cả · Mới vào nghề không ghi số năm kinh nghiệm nên không được tính.");
  });

  it("fr33: khung chú thích nêu bộ lọc (vai trò · cấp · số năm) cạnh ngày snapshot; tiêu đề biểu đồ nêu số năm", async () => {
    routeCityShares({ "all|entry|any": [entry], "all|entry|2": [() => jsonResponse(200, upTo("2"))] });
    const user = await openScreen();

    await user.click(yearsButton("Tối đa 2 năm"));
    await screen.findByText(/37 tin/);
    const caption = screen.getByRole("region", { name: "Nguồn và lưu ý" });
    expect(within(caption).getByText("Bộ lọc")).toBeTruthy();
    expect(within(caption).getByText("Tất cả · Mới vào nghề · Tối đa 2 năm")).toBeTruthy();
    expect(within(caption).getByText("Ngày snapshot")).toBeTruthy();
    expect(screen.getByText(/Tỷ trọng tin theo thành phố · Tất cả · Mới vào nghề · Tối đa 2 năm/)).toBeTruthy();
  });

  it("fr33: bấm nhanh hai mốc, response về muộn của mốc đầu bị bỏ", async () => {
    const slow = deferred<Response>();
    routeCityShares({
      "all|entry|any": [entry],
      "all|entry|1": [() => slow.promise],
      "all|entry|5": [() => jsonResponse(200, upTo("5", { haNoi: 300 }))],
    });
    const user = await openScreen();

    await user.click(yearsButton("Tối đa 1 năm"));
    expect(screen.getByRole("status").textContent).toBe(LOADING);
    await user.click(yearsButton("Tối đa 5 năm"));
    await screen.findByRole("button", { name: /^Hà Nội: .*, 300 tin/ });
    await act(async () => {
      slow.resolve(jsonResponse(200, upTo("1", { haNoi: 7 })));
    });
    expect(screen.queryByRole("button", { name: /^Hà Nội: .*, 7 tin\b/ })).toBeNull();
    expect(yearsButton("Tối đa 5 năm").getAttribute("aria-pressed")).toBe("true");
  });

  it("fr33: bộ chọn số năm vẫn ở đó trên lối Bảng và lối danh sách", async () => {
    routeCityShares({ "all|entry": [entry] });
    const user = await openScreen();

    expect(yearsGroup()).toBeTruthy();
    await user.click(within(screen.getByRole("group", { name: "Lối xem" })).getByRole("button", { name: "Bảng" }));
    expect(yearsGroup()).toBeTruthy();
    expect(yearsGroup().className).toContain("flex-wrap");
  });
});

describe("fr33 #280 — hợp đồng years của client", () => {
  it("fr33: envelope có data.years khác mốc đã hỏi là không đọc được", async () => {
    routeCityShares({ all: [() => jsonResponse(200, upTo("2"))] }, { echoLevel: false });
    const result = await fetchCityShares("all", { level: "entry", years: "1" });
    expect(result.kind).toBe("unreadable");
  });

  it("fr33: years khác any mà years_unstated_cell_id không trỏ tới một ô của meta.cells là không đọc được", async () => {
    const bad = upTo("2") as unknown as { data: { years_unstated_cell_id: unknown } };
    bad.data.years_unstated_cell_id = "vn.khong_co.ynone";
    routeCityShares({ all: [() => jsonResponse(200, bad)] }, { echoLevel: false });
    expect((await fetchCityShares("all", { level: "entry", years: "2" })).kind).toBe("unreadable");
  });

  it("fr33: view có nhãn số năm và câu tin bị bỏ chỉ khi years khác any", () => {
    const view = buildCitySharesView(upTo("2", { unstated: 5 }));
    expect(view.yearsLabel).toBe("Tối đa 2 năm");
    expect(view.unstatedNote).toBe("5 tin của Tất cả · Mới vào nghề không ghi số năm kinh nghiệm nên không được tính.");
    expect(view.caption.filters).toBe("Tất cả · Mới vào nghề · Tối đa 2 năm");
    const any = buildCitySharesView(upTo("any"));
    expect(any.unstatedNote).toBeNull();
    expect(any.caption.filters).toBe("Tất cả · Mới vào nghề · Mọi số năm");
  });
});
