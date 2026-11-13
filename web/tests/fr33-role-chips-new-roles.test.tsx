import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { MapScreen } from "@/app/components/map/map-screen";

import { buildEnvelope, fakeEnvelope } from "./fixtures/envelopes";
import { jsonResponse, routeCityShares } from "./helpers/fetch";
import { levelSelect, optionLabels, pick, roleSelect, selectedLabel, yearsSelect } from "./helpers/filters";

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

describe("fr33 #284, #293 — bảy vai trò mới trên ô chọn vai trò", () => {
  it("fr33: ô Vai trò có 18 option theo thứ tự config, nhãn tiếng Việt, không optgroup, cao tối thiểu 44px", async () => {
    routeCityShares({ "all|entry": [() => jsonResponse(200, fakeEnvelope("all", "entry"))] });
    await openScreen();
    expect(optionLabels(roleSelect())).toEqual(ROLE_NAMES);
    expect(roleSelect().querySelector("optgroup")).toBeNull();
    expect(roleSelect().hasAttribute("aria-pressed")).toBe(false);
    expect(roleSelect().className).toContain("min-h-target");
  });

  it("fr33: Tab từ ô Vai trò tới ô Cấp bậc rồi ô Số năm kinh nghiệm", async () => {
    routeCityShares({ "all|entry": [() => jsonResponse(200, fakeEnvelope("all", "entry"))] });
    const user = await openScreen();
    act(() => roleSelect().focus());
    await user.tab();
    expect(document.activeElement).toBe(levelSelect());
    await user.tab();
    expect(document.activeElement).toBe(yearsSelect());
  });

  it("fr33: chọn Fullstack gọi API với role=fullstack và hiện số của Fullstack", async () => {
    const fetchMock = routeCityShares({
      "all|entry": [() => jsonResponse(200, fakeEnvelope("all", "entry"))],
      "fullstack|entry": [() => jsonResponse(200, fullstack())],
    });
    const user = await openScreen();
    await pick(user, roleSelect(), "Fullstack");
    await screen.findByRole("button", { name: /^Hà Nội: .*19 tin/ });
    const urls = fetchMock.mock.calls.map((call) => String(call[0]));
    expect(urls.at(-1)).toBe("/api/v1/city-shares?role=fullstack&level=entry&years=any");
    expect(selectedLabel(roleSelect())).toBe("Fullstack");
  });
});
