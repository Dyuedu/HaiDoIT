import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { MapScreen } from "@/app/components/map/map-screen";
import { buildCitySharesView } from "@/lib/city-shares-view";

import { allLowSampleEnvelope, fakeEnvelope } from "./fixtures/envelopes";
import { jsonResponse, routeCityShares } from "./helpers/fetch";

// #316 — lối 3D CSS của màn Bản đồ theo prototype màn 01 (DESIGN.md). jsdom không có `CSS.supports`: kết quả dò CSS 3D
// được giả lập; khung, sân khấu, cột, thẻ, nút xoay, kéo và panel bên phải là mã thật.

const control = vi.hoisted(() => ({ css3d: true }));

vi.mock("@/lib/css3d", () => ({
  subscribeCss3d: () => () => {},
  getCss3dSnapshot: () => control.css3d,
  getServerCss3dSnapshot: () => false,
}));

const NO_3D = "Trình duyệt này không chạy được bản đồ 3D, nên đang hiện biểu đồ 2D.";
const VIEWPORT = /^Bản đồ 3D/;

function modeButton(name: string) {
  return within(screen.getByRole("group", { name: "Lối xem" })).getByRole("button", { name });
}

function stageTransform(): string {
  const stage = screen.getByTestId("map-3d-stage");
  return stage.style.transform;
}

async function openScreen(envelope = fakeEnvelope("all")) {
  // Màn mở ở vai trò "Tất cả": envelope phải mang role "all" mới được đọc (fixture mẫu nhỏ là của backend).
  const body = structuredClone(envelope);
  body.data.role = "all";
  routeCityShares({ all: [() => jsonResponse(200, body)] });
  const user = userEvent.setup();
  const view = render(<MapScreen />);
  await screen.findByRole("group", { name: VIEWPORT });
  // Mở màn: 250ms sau sân khấu nghiêng lên 56° và cột mọc (hẹn giờ thật; jsdom không chạy theo đồng hồ giả).
  await waitFor(() => expect(stageTransform()).toContain("rotateX(56deg)"));
  return { user, ...view };
}

beforeEach(() => {
  control.css3d = true;
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("fr33 #316 — khung và sân khấu", () => {
  it("fr33: mở bản đồ vào lối 3D, sân khấu nghiêng 56° và xoay −16° sau mở màn", async () => {
    await openScreen();
    expect(modeButton("3D").getAttribute("aria-pressed")).toBe("true");
    expect(stageTransform()).toContain("rotateX(56deg)");
    expect(stageTransform()).toContain("rotateZ(-16deg)");
    const svg = screen.getByTestId("map-3d-land");
    expect(svg.textContent).toContain("QĐ. Hoàng Sa");
    expect(svg.textContent).toContain("QĐ. Trường Sa");
  });

  it("fr33: ba cột cao theo tỷ trọng, mỗi cột một thẻ nhãn là nút có tên đọc được gồm tỷ trọng và n", async () => {
    await openScreen();
    const view = buildCitySharesView(fakeEnvelope("all"));
    const viewport = screen.getByRole("group", { name: VIEWPORT });
    for (const bar of view.bars) {
      const card = within(viewport).getByRole("button", { name: bar.accessibleName });
      expect(card.textContent).toContain(bar.label);
      expect(card.textContent).toContain(`${bar.percent} · ${bar.nText}/${view.table.total.nText} tin`);
      const column = screen.getByTestId(`map-3d-column-${bar.city}`);
      expect(Number(column.dataset.height)).toBeCloseTo(bar.value * 400, 6);
    }
  });

  it("fr33: cột mẫu nhỏ mờ, thẻ có câu cỡ mẫu nhỏ, tỷ trọng chỉ hiện khi trỏ, focus hoặc chạm", async () => {
    await openScreen(allLowSampleEnvelope());
    const view = buildCitySharesView(allLowSampleEnvelope());
    const bar = view.bars[0];
    const card = within(screen.getByRole("group", { name: VIEWPORT })).getByRole("button", { name: bar.accessibleName });
    expect(card.textContent).toContain(bar.lowSampleNote!);
    expect(card.querySelector("[data-reveal]")?.textContent).toContain(bar.percent);
    expect(screen.getByTestId(`map-3d-column-${bar.city}`).dataset.faded).toBe("true");
  });

  it("fr33: bấm thẻ thì chọn cột: aria-pressed và mặt trên đổi màu", async () => {
    const { user } = await openScreen();
    const view = buildCitySharesView(fakeEnvelope("all"));
    const card = within(screen.getByRole("group", { name: VIEWPORT })).getByRole("button", { name: view.bars[1].accessibleName });
    await user.click(card);
    expect(card.getAttribute("aria-pressed")).toBe("true");
    expect(screen.getByTestId(`map-3d-column-${view.bars[1].city}`).dataset.selected).toBe("true");
  });
});

describe("fr33 #316 — xoay, nghiêng", () => {
  it("fr33: ba nút xoay trái, xoay phải 30° và đặt lại góc nhìn", async () => {
    const { user } = await openScreen();
    await user.click(screen.getByRole("button", { name: "Xoay phải 30 độ" }));
    expect(stageTransform()).toContain("rotateZ(14deg)");
    await user.click(screen.getByRole("button", { name: "Xoay trái 30 độ" }));
    await user.click(screen.getByRole("button", { name: "Xoay trái 30 độ" }));
    expect(stageTransform()).toContain("rotateZ(-46deg)");
    await user.click(screen.getByRole("button", { name: "Đặt lại góc nhìn" }));
    expect(stageTransform()).toContain("rotateX(56deg)");
    expect(stageTransform()).toContain("rotateZ(-16deg)");
  });

  it("fr33: kéo ngang xoay 0,35°/px, kéo dọc nghiêng trong 0–72°, dưới 6px không đổi", async () => {
    await openScreen();
    const viewport = screen.getByRole("group", { name: VIEWPORT });
    fireEvent.pointerDown(viewport, { clientX: 100, clientY: 100, button: 0, pointerId: 1 });
    fireEvent.pointerMove(viewport, { clientX: 103, clientY: 101, pointerId: 1 });
    expect(stageTransform()).toContain("rotateZ(-16deg)");
    fireEvent.pointerMove(viewport, { clientX: 200, clientY: 100, pointerId: 1 });
    expect(stageTransform()).toContain("rotateZ(19deg)");
    fireEvent.pointerMove(viewport, { clientX: 200, clientY: -400, pointerId: 1 });
    expect(stageTransform()).toContain("rotateX(72deg)");
    fireEvent.pointerUp(viewport, { pointerId: 1 });
  });
});

describe("fr33 fr36 #316 — panel bên phải", () => {
  it("fr36: panel liệt kê ba nơi, các phần không thành cột, và Nguồn và lưu ý", async () => {
    await openScreen();
    const view = buildCitySharesView(fakeEnvelope("all"));
    const panel = screen.getByRole("region", { name: `Tin ${view.roleLabel} nằm ở đâu` });
    for (const bar of view.bars) {
      expect(panel.textContent).toContain(bar.label);
      expect(panel.textContent).toContain(`${bar.nText} / ${view.table.total.nText} tin`);
    }
    for (const line of view.legend) expect(panel.textContent).toContain(line.label);
    expect(screen.getByRole("region", { name: "Nguồn và lưu ý" })).toBeTruthy();
  });

  it("fr36: panel có ở cả lối 2D và Bảng", async () => {
    const { user } = await openScreen();
    const name = `Tin ${buildCitySharesView(fakeEnvelope("all")).roleLabel} nằm ở đâu`;
    await user.click(modeButton("Biểu đồ 2D"));
    expect(screen.getByRole("region", { name })).toBeTruthy();
    await user.click(modeButton("Bảng"));
    expect(screen.getByRole("region", { name })).toBeTruthy();
  });
});

describe("fr36 #316 — khi không mở 3D", () => {
  it("fr36: không chạy được CSS 3D thì lối 2D, nút 3D aria-disabled kèm câu, không màn hình lỗi", async () => {
    control.css3d = false;
    routeCityShares({ all: [() => jsonResponse(200, fakeEnvelope("all"))] });
    render(<MapScreen />);
    await screen.findByRole("button", { name: /^Hà Nội:/ });
    const button3d = modeButton("3D");
    expect(button3d.getAttribute("aria-disabled")).toBe("true");
    expect(document.getElementById(button3d.getAttribute("aria-describedby")!)?.textContent).toBe(NO_3D);
    expect(screen.queryByRole("group", { name: VIEWPORT })).toBeNull();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("fr33: màn hẹp hơn 640px mở lối 2D, nút 3D vẫn bấm được (NFR-12)", async () => {
    vi.stubGlobal(
      "matchMedia",
      (query: string) =>
        ({ matches: false, media: query, addEventListener: () => {}, removeEventListener: () => {} }) as unknown as MediaQueryList,
    );
    routeCityShares({ all: [() => jsonResponse(200, fakeEnvelope("all"))] });
    const user = userEvent.setup();
    render(<MapScreen />);
    await screen.findByRole("button", { name: /^Hà Nội:/ });
    expect(modeButton("Biểu đồ 2D").getAttribute("aria-pressed")).toBe("true");
    await user.click(modeButton("3D"));
    await screen.findByRole("group", { name: VIEWPORT });
  });
});
