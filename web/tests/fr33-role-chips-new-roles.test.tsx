import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { MapScreen } from "@/app/components/map/map-screen";

import { buildEnvelope, fakeEnvelope } from "./fixtures/envelopes";
import { jsonResponse, routeCityShares } from "./helpers/fetch";

const ROLE_NAMES = [
  "Tất cả",
  "Nhúng",
  "AI/ML",
  "Khoa học dữ liệu",
  "Kỹ sư dữ liệu",
  "Phân tích dữ liệu",
  "Kiểm thử (QA)",
  "DevOps",
  "Bảo mật",
  "Hạ tầng & IT support",
  "Mobile",
  "Frontend",
  "Backend",
  "Fullstack",
  "BA / PO / PM",
  "UI/UX",
  "Phát triển game",
  "Vai trò khác",
];

function roleGroup() {
  return screen.getByRole("group", { name: "Vai trò" });
}

function fullstack() {
  return buildEnvelope({
    role: "fullstack",
    level: "entry",
    totalN: 34,
    rows: [
      { city: "ha_noi", n: 19, value: 19 / 34, display: "low_sample_shown" },
      { city: "ho_chi_minh", n: 13, value: 13 / 34, display: "low_sample_shown" },
      { city: "da_nang", n: 1, value: 1 / 34, display: "low_sample_shown" },
      { city: "other", n: 0, value: 0, display: "low_sample_shown" },
      { city: "unknown", n: 1, value: 1 / 34, display: "low_sample_shown" },
    ],
  });
}

async function openScreen() {
  const user = userEvent.setup();
  render(<MapScreen />);
  await screen.findByRole("button", { name: /^Hà Nội:/ });
  return user;
}

describe("fr33 #284 — bảy vai trò mới trên bộ chọn vai trò", () => {
  it("fr33: nhóm Vai trò có 18 nút theo thứ tự config, nhãn tiếng Việt, xuống dòng khi hẹp", async () => {
    routeCityShares({ "all|entry": [() => jsonResponse(200, fakeEnvelope("all", "entry"))] });
    await openScreen();
    const buttons = within(roleGroup()).getAllByRole("button");
    expect(buttons.map((b) => b.textContent)).toEqual(ROLE_NAMES);
    for (const button of buttons) {
      expect(button.getAttribute("aria-pressed")).not.toBeNull();
      expect(button.className).toContain("min-h-target");
    }
    expect(roleGroup().className).toContain("flex-wrap");
  });

  it("fr33: Tab đi qua đủ 18 nút vai trò theo thứ tự", async () => {
    routeCityShares({ "all|entry": [() => jsonResponse(200, fakeEnvelope("all", "entry"))] });
    const user = await openScreen();
    const buttons = within(roleGroup()).getAllByRole("button");
    buttons[0].focus();
    for (const button of buttons.slice(1)) {
      await user.tab();
      expect(document.activeElement).toBe(button);
    }
  });

  it("fr33: bấm Fullstack gọi API với role=fullstack và hiện số của Fullstack", async () => {
    const fetchMock = routeCityShares({
      "all|entry": [() => jsonResponse(200, fakeEnvelope("all", "entry"))],
      "fullstack|entry": [() => jsonResponse(200, fullstack())],
    });
    const user = await openScreen();
    await user.click(within(roleGroup()).getByRole("button", { name: "Fullstack" }));
    await screen.findByRole("button", { name: /^Hà Nội: .*19 tin/ });
    const urls = fetchMock.mock.calls.map((call) => String(call[0]));
    expect(urls.at(-1)).toBe("/api/v1/city-shares?role=fullstack&level=entry&years=any");
    expect(within(roleGroup()).getByRole("button", { name: "Fullstack" }).getAttribute("aria-pressed")).toBe("true");
  });
});
