import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { MapScreen } from "@/app/components/map/map-screen";
import { buildCitySharesView } from "@/lib/city-shares-view";

import { fakeEnvelope } from "./fixtures/envelopes";
import { jsonResponse, routeCityShares } from "./helpers/fetch";

// #314 — lối 3D của màn Bản đồ. jsdom không có WebGL: kết quả dò WebGL và component canvas (`map-3d.tsx`) được thay bằng
// bản giả; phần còn lại (chuyển lối, nút chọn cột, khung thông tin, chú thích, rơi về 2D) là mã thật.

const control = vi.hoisted(() => ({ webgl: true, throwIn3d: false }));

vi.mock("@/lib/webgl", () => ({
  subscribeWebGL: () => () => {},
  getWebGLSnapshot: () => control.webgl,
  getServerWebGLSnapshot: () => false,
}));

vi.mock("@/app/components/map/map-3d", () => ({
  default: function FakeMap3D(props: { columns: { city: string; height: number }[] }) {
    if (control.throwIn3d) throw new Error("WebGL context lost");
    return <div data-testid="map-3d-canvas">{props.columns.map((c) => `${c.city}:${c.height.toFixed(3)}`).join(" ")}</div>;
  },
}));

const NO_WEBGL = "Trình duyệt này không chạy được bản đồ 3D, nên đang hiện biểu đồ 2D.";

function modeButton(name: string) {
  return within(screen.getByRole("group", { name: "Lối xem" })).getByRole("button", { name });
}

async function openScreen() {
  routeCityShares({ all: [() => jsonResponse(200, fakeEnvelope("all"))] });
  const user = userEvent.setup();
  const view = render(<MapScreen />);
  return { user, ...view };
}

beforeEach(() => {
  control.webgl = true;
  control.throwIn3d = false;
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fr33 fr36 #314 — có WebGL", () => {
  it("fr33: mở bản đồ vào lối 3D, có ba cột theo tỷ trọng của lối 2D", async () => {
    await openScreen();
    const canvas = await screen.findByTestId("map-3d-canvas");
    expect(modeButton("3D").getAttribute("aria-pressed")).toBe("true");
    expect(modeButton("3D").getAttribute("aria-disabled")).toBeNull();
    const view = buildCitySharesView(fakeEnvelope("all"));
    for (const bar of view.bars) expect(canvas.textContent).toContain(`${bar.city}:`);
    expect(screen.getByRole("figure", { name: /Bản đồ 3D/ })).toBeTruthy();
  });

  it("fr36: chuyển 2D, Bảng rồi quay lại 3D", async () => {
    const { user } = await openScreen();
    await screen.findByTestId("map-3d-canvas");
    await user.click(modeButton("Biểu đồ 2D"));
    expect(screen.queryByTestId("map-3d-canvas")).toBeNull();
    await screen.findByRole("button", { name: /^Hà Nội:/ });
    await user.click(modeButton("Bảng"));
    await screen.findByRole("table");
    await user.click(modeButton("3D"));
    await screen.findByTestId("map-3d-canvas");
  });

  it("fr33: chọn một cột thì khung thông tin ghi tỷ trọng và số tin", async () => {
    const { user } = await openScreen();
    await screen.findByTestId("map-3d-canvas");
    const figure = screen.getByRole("figure", { name: /Bản đồ 3D/ });
    const view = buildCitySharesView(fakeEnvelope("all"));
    await user.click(within(figure).getByRole("button", { name: "Hà Nội" }));
    expect(within(figure).getByRole("button", { name: "Hà Nội" }).getAttribute("aria-pressed")).toBe("true");
    expect(within(figure).getByRole("status").textContent).toBe(view.bars[0].accessibleName);
  });

  it("fr36: lối 3D vẫn có chú thích các phần không thành cột và khung Nguồn và lưu ý", async () => {
    await openScreen();
    await screen.findByTestId("map-3d-canvas");
    const legend = screen.getByRole("list", { name: "Chú thích" });
    expect(within(legend).getByRole("button", { name: /^Làm từ xa \(Remote\):/ })).toBeTruthy();
    expect(screen.getByRole("region", { name: "Nguồn và lưu ý" })).toBeTruthy();
    expect(screen.getByText(/geoBoundaries/)).toBeTruthy();
  });
});

describe("fr33 #314 — điện thoại (NFR-12, UX-DR39)", () => {
  it("fr33: màn hẹp hơn 640px mở lối 2D dù có WebGL, nút 3D vẫn bấm được", async () => {
    vi.stubGlobal(
      "matchMedia",
      (query: string) =>
        ({ matches: false, media: query, addEventListener: () => {}, removeEventListener: () => {} }) as unknown as MediaQueryList,
    );
    const { user } = await openScreen();
    await screen.findByRole("button", { name: /^Hà Nội:/ });
    expect(modeButton("Biểu đồ 2D").getAttribute("aria-pressed")).toBe("true");
    expect(modeButton("3D").getAttribute("aria-disabled")).toBeNull();
    await user.click(modeButton("3D"));
    await screen.findByTestId("map-3d-canvas");
  });
});

describe("fr36 #314 — không có WebGL", () => {
  it("fr36: không có WebGL thì mở lối 2D, nút 3D aria-disabled kèm câu, không màn hình lỗi", async () => {
    control.webgl = false;
    await openScreen();
    await screen.findByRole("button", { name: /^Hà Nội:/ });
    const button3d = modeButton("3D");
    expect(button3d.getAttribute("aria-disabled")).toBe("true");
    expect(document.getElementById(button3d.getAttribute("aria-describedby")!)?.textContent).toBe(NO_WEBGL);
    expect(modeButton("Biểu đồ 2D").getAttribute("aria-pressed")).toBe("true");
    expect(screen.queryByTestId("map-3d-canvas")).toBeNull();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("fr36: lối 3D lỗi khi dựng thì chuyển 2D, không màn hình lỗi", async () => {
    control.throwIn3d = true;
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    await openScreen();
    await screen.findByRole("button", { name: /^Hà Nội:/ });
    expect(modeButton("Biểu đồ 2D").getAttribute("aria-pressed")).toBe("true");
    expect(modeButton("3D").getAttribute("aria-disabled")).toBe("true");
    expect(screen.getByText(NO_WEBGL)).toBeTruthy();
    expect(screen.queryByRole("alert")).toBeNull();
    spy.mockRestore();
  });
});
