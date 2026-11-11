import { act, fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { MapScreen } from "@/app/components/map/map-screen";

import { allLowSampleEnvelope, fakeEnvelope, statEnvelope } from "./fixtures/envelopes";
import { deferred, jsonResponse, routeCityShares } from "./helpers/fetch";

const LOADING = "Đang tải số liệu…";
const LOW_SAMPLE_21 = "Cỡ mẫu nhỏ (n = 21 < 30): số liệu chỉ để tham khảo";
const UNREADABLE = "Không đọc được số liệu. Thử lại sau.";

const ok = (role: "all" | "ai_ml" | "backend") => () => jsonResponse(200, fakeEnvelope(role));

function chip(name: string) {
  return within(screen.getByRole("group", { name: "Vai trò" })).getByRole("button", { name });
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
  const view = render(<MapScreen />);
  await screen.findByRole("button", { name: /^Hà Nội:/ });
  return { user, ...view };
}

async function pickRole(user: ReturnType<typeof userEvent.setup>, name: string) {
  await user.click(chip(name));
}

/** Mở màn, chọn AI/ML, trả dòng Đà Nẵng (mẫu nhỏ, n = 21) với phần trăm đang ẩn. */
async function openAiMl() {
  routeCityShares({ all: [ok("all")], ai_ml: [ok("ai_ml")] });
  const { user } = await openScreen();
  await pickRole(user, "AI/ML");
  const daNang = await screen.findByRole("button", { name: /^Đà Nẵng:/ });
  expect(daNang.textContent).not.toContain("2,4%");
  return { user, daNang };
}

describe("fr33 — mở trang", () => {
  it("fr33: mở trang vào lối 2D, chip Tất cả, ba thanh theo share.value", async () => {
    const fetchMock = routeCityShares({ all: [ok("all")] });
    render(<MapScreen />);

    expect(screen.getByRole("status").textContent).toBe(LOADING);
    const haNoi = await screen.findByRole("button", { name: /^Hà Nội:/ });

    // #163: màn luôn gửi cấp bậc, mặc định là nhóm mới vào nghề (entry) của #134.
    expect(String(fetchMock.mock.calls[0][0])).toBe("/api/v1/city-shares?role=all&level=entry");
    expect(chip("Tất cả").getAttribute("aria-pressed")).toBe("true");
    expect(chip("AI/ML").getAttribute("aria-pressed")).toBe("false");
    expect(modeButton("Biểu đồ 2D").getAttribute("aria-pressed")).toBe("true");
    expect(modeButton("Bảng").getAttribute("aria-pressed")).toBe("false");
    expect(screen.getByRole("status").textContent).toBe("");

    expect(fill(haNoi).style.width).toBe(`${0.4155047406581149 * 100}%`);
    expect(fill(cityButton("TP.HCM")).style.width).toBe(`${0.4774121583937535 * 100}%`);
    expect(fill(cityButton("Đà Nẵng")).style.width).toBe(`${0.01784718349135527 * 100}%`);
    expect(haNoi.textContent).toContain("41,6%");
    expect(haNoi.textContent).toContain("1.490 tin");
  });

  it("fr33: chỉ ba thanh nằm trong figure; Khác và không xác định là dòng chú thích", async () => {
    routeCityShares({ all: [ok("all")] });
    await openScreen();
    const figure = screen.getByRole("figure");

    expect(figure.querySelectorAll('[data-part="track"]')).toHaveLength(3);
    const other = cityButton("Khác");
    const unknown = cityButton("Không xác định thành phố");
    expect(other.querySelector('[data-part="track"]')).toBeNull();
    expect(unknown.querySelector('[data-part="track"]')).toBeNull();
    expect(other.textContent).toContain("3,2%");
    expect(other.textContent).toContain("113 tin");
    expect(unknown.textContent).toContain("207 tin");
  });

  it("fr33: màn không thêm thẻ <a> hay <nav>", async () => {
    routeCityShares({ all: [ok("all")] });
    const { container } = await openScreen();

    expect(container.querySelectorAll("a, nav")).toHaveLength(0);
  });
});

describe("fr33 — mẫu nhỏ", () => {
  it("fr33: Đà Nẵng mẫu nhỏ mờ có sọc, nhãn luôn hiện, % chỉ hiện khi trỏ chuột", async () => {
    routeCityShares({ all: [ok("all")], ai_ml: [ok("ai_ml")] });
    const { user } = await openScreen();
    await pickRole(user, "AI/ML");
    const daNang = await screen.findByRole("button", { name: /^Đà Nẵng:/ });

    expect(daNang.getAttribute("aria-label")).toBe(`Đà Nẵng: 2,4%, 21 tin. ${LOW_SAMPLE_21}`);
    expect(fill(daNang).getAttribute("data-low-sample")).toBe("true");
    expect(fill(cityButton("Hà Nội")).getAttribute("data-low-sample")).toBe("false");
    expect(daNang.textContent).toContain(LOW_SAMPLE_21);
    expect(daNang.textContent).not.toContain("2,4%");

    await user.hover(daNang);
    expect(daNang.textContent).toContain("2,4%");

    // Di chuột lên chính phần trăm không làm nó biến mất.
    await user.hover(within(daNang).getByText("2,4%"));
    expect(daNang.textContent).toContain("2,4%");

    await user.unhover(daNang);
    expect(daNang.textContent).not.toContain("2,4%");
  });

  it("fr33: % hiện khi focus và Esc ẩn lại", async () => {
    routeCityShares({ all: [ok("all")], ai_ml: [ok("ai_ml")] });
    const { user } = await openScreen();
    await pickRole(user, "AI/ML");
    const daNang = await screen.findByRole("button", { name: /^Đà Nẵng:/ });

    act(() => daNang.focus());
    expect(daNang.textContent).toContain("2,4%");

    await user.keyboard("{Escape}");
    expect(daNang.textContent).not.toContain("2,4%");
    expect(daNang.textContent).toContain(LOW_SAMPLE_21);
  });

  it("fr33: chạm hiện %, chạm lần nữa ẩn", async () => {
    routeCityShares({ all: [ok("all")], ai_ml: [ok("ai_ml")] });
    const { user } = await openScreen();
    await pickRole(user, "AI/ML");
    const daNang = await screen.findByRole("button", { name: /^Đà Nẵng:/ });

    await user.pointer({ keys: "[TouchA]", target: daNang });
    expect(daNang.textContent).toContain("2,4%");

    await user.pointer({ keys: "[TouchA]", target: daNang });
    expect(daNang.textContent).not.toContain("2,4%");
  });

  it("fr33: trỏ chuột rồi bấm thì phần trăm vẫn hiện; bấm lần nữa thì ẩn", async () => {
    const { user, daNang } = await openAiMl();

    await user.hover(daNang);
    await user.click(daNang);
    expect(daNang.textContent).toContain("2,4%");

    await user.click(daNang);
    expect(daNang.textContent).not.toContain("2,4%");
  });

  it("fr33: focus rồi Enter giữ phần trăm, Enter lần nữa ẩn", async () => {
    const { user, daNang } = await openAiMl();

    act(() => daNang.focus());
    await user.keyboard("{Enter}");
    expect(daNang.textContent).toContain("2,4%");

    await user.keyboard("{Enter}");
    expect(daNang.textContent).not.toContain("2,4%");
  });

  it("fr33: focus rồi Tab sang chỗ khác thì phần trăm ẩn", async () => {
    const { user, daNang } = await openAiMl();

    act(() => daNang.focus());
    expect(daNang.textContent).toContain("2,4%");

    await user.tab();
    expect(document.activeElement).not.toBe(daNang);
    expect(daNang.textContent).not.toContain("2,4%");
  });

  it("fr33: trỏ chuột, focus, rồi rời chuột thì phần trăm vẫn hiện khi còn focus", async () => {
    const { user, daNang } = await openAiMl();

    await user.hover(daNang);
    act(() => daNang.focus());
    await user.unhover(daNang);

    expect(daNang.textContent).toContain("2,4%");
  });

  it("fr33: bút trỏ cũng hiện phần trăm như chuột", async () => {
    const { daNang } = await openAiMl();

    fireEvent.pointerEnter(daNang, { pointerType: "pen" });
    expect(daNang.textContent).toContain("2,4%");

    fireEvent.pointerLeave(daNang, { pointerType: "pen" });
    expect(daNang.textContent).not.toContain("2,4%");
  });

  it("fr33: Khác n = 5 và không xác định n = 8 có nhãn mẫu nhỏ ở chú thích (backend)", async () => {
    routeCityShares({ all: [ok("all")], backend: [ok("backend")] });
    const { user } = await openScreen();
    await pickRole(user, "Backend");
    const other = await screen.findByRole("button", { name: /^Khác:/ });
    const unknown = cityButton("Không xác định thành phố");

    expect(other.textContent).toContain("Cỡ mẫu nhỏ (n = 5 < 30): số liệu chỉ để tham khảo");
    expect(other.textContent).not.toContain("3,2%");
    expect(unknown.textContent).toContain("Cỡ mẫu nhỏ (n = 8 < 30): số liệu chỉ để tham khảo");

    await user.hover(other);
    expect(other.textContent).toContain("3,2%");
  });

  it("fr33: tỷ trọng 0 vẫn có rãnh, button focus được, nhãn n = 0", async () => {
    routeCityShares({ all: [ok("all")], ai_ml: [() => jsonResponse(200, statEnvelope())] });
    const { user } = await openScreen();
    await pickRole(user, "AI/ML");
    const daNang = await screen.findByRole("button", { name: /^Đà Nẵng:/ });

    expect(daNang.querySelector('[data-part="track"]')).not.toBeNull();
    expect(fill(daNang).style.width).toBe("0%");
    expect(daNang.textContent).toContain("Cỡ mẫu nhỏ (n = 0 < 30): số liệu chỉ để tham khảo");
    act(() => daNang.focus());
    expect(document.activeElement).toBe(daNang);
  });

  it("fr33: năm dòng đều mẫu nhỏ thì mọi dòng có nhãn", async () => {
    routeCityShares({ all: [ok("all")], backend: [() => jsonResponse(200, allLowSampleEnvelope())] });
    const { user } = await openScreen();
    await pickRole(user, "Backend");
    await screen.findByRole("button", { name: /^Hà Nội:.*Cỡ mẫu nhỏ/ });

    for (const label of ["Hà Nội", "TP.HCM", "Đà Nẵng", "Khác", "Không xác định thành phố"]) {
      const button = cityButton(label);
      expect(button.textContent).toContain("Cỡ mẫu nhỏ");
      expect(button.textContent).not.toContain("%");
    }
  });
});

describe("fr33 — lối Bảng", () => {
  it("fr33: bảng có cột Nơi, Tỷ trọng, Số tin, Ghi chú; ĐN mẫu nhỏ ghi 'chưa đủ dữ liệu' và 21", async () => {
    routeCityShares({ all: [ok("all")], ai_ml: [ok("ai_ml")] });
    const { user } = await openScreen();
    await pickRole(user, "AI/ML");
    await screen.findByRole("button", { name: /^Đà Nẵng:/ });
    await user.click(modeButton("Bảng"));

    expect(modeButton("Bảng").getAttribute("aria-pressed")).toBe("true");
    expect(modeButton("Biểu đồ 2D").getAttribute("aria-pressed")).toBe("false");
    expect(screen.queryByRole("figure")).toBeNull();
    const table = screen.getByRole("table");
    const headers = within(table).getAllByRole("columnheader").map((cell) => cell.textContent);
    expect(headers).toEqual(["Nơi", "Tỷ trọng", "Số tin", "Ghi chú"]);

    const daNang = within(table).getByRole("row", { name: /Đà Nẵng/ });
    const cells = within(daNang).getAllByRole("cell").map((cell) => cell.textContent);
    expect(cells).toEqual(["chưa đủ dữ liệu", "21", "Cỡ mẫu nhỏ (n = 21 < 30)"]);
    const haNoi = within(table).getByRole("row", { name: /Hà Nội/ });
    expect(within(haNoi).getAllByRole("cell")[0].textContent).toBe("47,0%");
  });

  it("fr33: bảng có dòng Khác và không xác định (backend)", async () => {
    routeCityShares({ all: [ok("all")], backend: [ok("backend")] });
    const { user } = await openScreen();
    await user.click(modeButton("Bảng"));
    await pickRole(user, "Backend");
    const table = await screen.findByRole("table");

    const other = within(table).getByRole("row", { name: /^Khác/ });
    const unknown = within(table).getByRole("row", { name: /Không xác định thành phố/ });
    expect(within(other).getAllByRole("cell").map((cell) => cell.textContent).slice(0, 2)).toEqual([
      "chưa đủ dữ liệu",
      "5",
    ]);
    expect(within(unknown).getAllByRole("cell")[1].textContent).toBe("8");
  });

  it("fr33: dòng tổng ghi 100% và n = 3.586, kèm chú thích lệch do làm tròn", async () => {
    routeCityShares({ all: [ok("all")] });
    const { user } = await openScreen();
    await user.click(modeButton("Bảng"));
    const table = screen.getByRole("table");

    const total = within(table).getByRole("row", { name: /Tổng/ });
    expect(within(total).getAllByRole("cell").map((cell) => cell.textContent).slice(0, 2)).toEqual([
      "100%",
      "3.586",
    ]);
    screen.getByText("Tổng các dòng có thể lệch 0,1% do làm tròn.");
  });
});

describe("fr33 — đổi vai trò", () => {
  it("fr33: đổi vai trò hiện trạng thái đang tải thay cho số cũ, aria-pressed đổi theo", async () => {
    const pending = deferred<Response>();
    routeCityShares({ all: [ok("all")], ai_ml: [() => pending.promise] });
    const { user } = await openScreen();

    await pickRole(user, "AI/ML");

    expect(screen.getByRole("status").textContent).toBe(LOADING);
    expect(screen.queryByRole("button", { name: /^Hà Nội:/ })).toBeNull();
    expect(chip("AI/ML").getAttribute("aria-pressed")).toBe("true");
    expect(chip("Tất cả").getAttribute("aria-pressed")).toBe("false");

    await act(async () => pending.resolve(jsonResponse(200, fakeEnvelope("ai_ml"))));
    expect((await screen.findByRole("button", { name: /^Đà Nẵng:/ })).textContent).toContain(
      LOW_SAMPLE_21,
    );
  });

  it("fr33: đổi vai trò nhanh thì bỏ response về muộn của vai trò cũ", async () => {
    const slowAiMl = deferred<Response>();
    routeCityShares({
      all: [ok("all")],
      ai_ml: [() => slowAiMl.promise],
      backend: [ok("backend")],
    });
    const { user } = await openScreen();

    await pickRole(user, "AI/ML");
    await pickRole(user, "Backend");
    const daNang = await screen.findByRole("button", { name: /^Đà Nẵng:/ });
    expect(daNang.textContent).toContain("n = 9 < 30");

    await act(async () => slowAiMl.resolve(jsonResponse(200, fakeEnvelope("ai_ml"))));

    expect(cityButton("Đà Nẵng").textContent).toContain("n = 9 < 30");
    expect(screen.queryByText(LOW_SAMPLE_21)).toBeNull();
    expect(chip("Backend").getAttribute("aria-pressed")).toBe("true");
  });
});

describe("fr33 — trạng thái tải sau lỗi và khi quay lại vai trò cũ", () => {
  it("fr33: quay lại vai trò đã tải trong lúc lượt khác chưa về thì hiện đang tải, không hiện số cũ", async () => {
    const allAgain = deferred<Response>();
    const aiMl = deferred<Response>();
    routeCityShares({ all: [ok("all"), () => allAgain.promise], ai_ml: [() => aiMl.promise] });
    const { user } = await openScreen();

    await pickRole(user, "AI/ML");
    await pickRole(user, "Tất cả");

    expect(screen.getByRole("status").textContent).toBe(LOADING);
    expect(screen.queryByRole("button", { name: /^Hà Nội:/ })).toBeNull();
  });

  it("fr33: đổi vai trò từ lỗi unknown_cell hiện đang tải, không còn thông báo lỗi", async () => {
    const aiMl = deferred<Response>();
    routeCityShares({
      all: [
        () =>
          jsonResponse(404, {
            error: { code: "unknown_cell", message: "Không có ô.", snapshot_date: "2026-11-03" },
          }),
      ],
      ai_ml: [() => aiMl.promise],
    });
    const user = userEvent.setup();
    render(<MapScreen />);
    await screen.findByRole("alert");

    await pickRole(user, "AI/ML");

    expect(screen.getByRole("status").textContent).toBe(LOADING);
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("fr33: bấm Thử lại sau 502 hiện đang tải, không còn thông báo lỗi, focus về vùng trạng thái", async () => {
    const second = deferred<Response>();
    routeCityShares({
      all: [
        () =>
          jsonResponse(502, {
            error: { code: "api_unavailable", message: "API tắt.", snapshot_date: null },
          }),
        () => second.promise,
      ],
    });
    const user = userEvent.setup();
    render(<MapScreen />);
    await screen.findByRole("alert");

    await user.click(screen.getByRole("button", { name: "Thử lại" }));

    const status = screen.getByRole("status");
    expect(status.textContent).toBe(LOADING);
    expect(screen.queryByRole("alert")).toBeNull();
    expect(document.activeElement).not.toBe(document.body);
    expect(document.activeElement).toBe(status);
  });
});

describe("fr33 — nút 3D", () => {
  it("fr33: nút 3D aria-disabled, không dùng disabled, nối với 'Bản đồ 3D sắp có'", async () => {
    routeCityShares({ all: [ok("all")] });
    await openScreen();
    const button3d = modeButton("3D");

    expect(button3d.getAttribute("aria-disabled")).toBe("true");
    expect(button3d.hasAttribute("disabled")).toBe(false);
    const describedBy = button3d.getAttribute("aria-describedby");
    expect(describedBy).toBeTruthy();
    expect(document.getElementById(describedBy!)?.textContent).toBe("Bản đồ 3D sắp có");
  });

  it("fr33: bấm hoặc Enter trên nút 3D không đổi lối", async () => {
    routeCityShares({ all: [ok("all")] });
    const { user } = await openScreen();
    const button3d = modeButton("3D");

    await user.click(button3d);
    act(() => button3d.focus());
    await user.keyboard("{Enter}");

    expect(button3d.getAttribute("aria-pressed")).toBe("false");
    expect(button3d.getAttribute("aria-disabled")).toBe("true");
    expect(modeButton("Biểu đồ 2D").getAttribute("aria-pressed")).toBe("true");
    screen.getByRole("figure");
  });
});

describe("fr33 — lỗi", () => {
  it("fr33: API tắt (502) hiện error.message và nút Thử lại, không có thanh hay bảng", async () => {
    const message = "Dịch vụ API hiện không phản hồi. Vui lòng thử lại sau.";
    const fetchMock = routeCityShares({
      all: [
        () => jsonResponse(502, { error: { code: "api_unavailable", message, snapshot_date: null } }),
        ok("all"),
      ],
    });
    const user = userEvent.setup();
    render(<MapScreen />);

    expect((await screen.findByRole("alert")).textContent).toContain(message);
    expect(screen.queryByRole("figure")).toBeNull();
    expect(screen.queryByRole("table")).toBeNull();

    await user.click(screen.getByRole("button", { name: "Thử lại" }));
    await screen.findByRole("button", { name: /^Hà Nội:/ });
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("fr33: 404 unknown_cell hiện message kèm ngày snapshot, không có Thử lại, chip vẫn đổi được", async () => {
    const message = "Không có ô thống kê nào cho vai trò đã chọn.";
    routeCityShares({
      all: [
        () =>
          jsonResponse(404, {
            error: { code: "unknown_cell", message, snapshot_date: "2026-11-03" },
          }),
      ],
      ai_ml: [ok("ai_ml")],
    });
    const user = userEvent.setup();
    render(<MapScreen />);

    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toContain(message);
    expect(alert.textContent).toContain("03/11/2026");
    expect(screen.queryByRole("button", { name: "Thử lại" })).toBeNull();
    expect(screen.queryByRole("figure")).toBeNull();

    await pickRole(user, "AI/ML");
    await screen.findByRole("button", { name: /^Đà Nẵng:/ });
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it.each([
    ["thiếu dòng da_nang", () => {
      const envelope = fakeEnvelope("all");
      envelope.data.rows = envelope.data.rows.filter((row) => row.city !== "da_nang");
      return jsonResponse(200, envelope);
    }],
    ["thiếu meta", () => jsonResponse(200, { data: fakeEnvelope("all").data })],
    ["body không phải JSON", () => jsonResponse(200, "<html></html>")],
  ])("fr33: envelope hỏng (%s) hiện câu không đọc được và nút Thử lại", async (_name, reply) => {
    routeCityShares({ all: [reply] });
    render(<MapScreen />);

    expect((await screen.findByRole("alert")).textContent).toBe(UNREADABLE);
    screen.getByRole("button", { name: "Thử lại" });
    expect(screen.queryByRole("figure")).toBeNull();
  });

  it("fr33: fetch bị từ chối hiện câu không đọc được", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("Failed to fetch");
      }),
    );
    render(<MapScreen />);

    expect((await screen.findByRole("alert")).textContent).toBe(UNREADABLE);
  });
});

describe("fr33 — bàn phím", () => {
  it("fr33: Tab đi qua chip vai trò, cụm lối xem, nút cấp bậc, rồi từng dòng thành phố", async () => {
    routeCityShares({ all: [ok("all")] });
    const { user } = await openScreen();
    const stops: string[] = [];

    for (let i = 0; i < 28; i += 1) {
      await user.tab();
      const active = document.activeElement as HTMLElement;
      stops.push(active.getAttribute("aria-label")?.split(":")[0] ?? active.textContent ?? "");
    }

    expect(stops).toEqual([
      "Tất cả",
      "Nhúng",
      "AI/ML",
      "Kỹ sư dữ liệu",
      "Phân tích dữ liệu",
      "Kiểm thử (QA)",
      "DevOps",
      "Mobile",
      "Frontend",
      "Backend",
      "Vai trò khác",
      "3D",
      "Biểu đồ 2D",
      "Bảng",
      "Mới vào nghề",
      "Intern",
      "Fresher",
      "Junior",
      "Mid",
      "Senior",
      "Lead",
      "Chưa ghi cấp bậc",
      "Mọi cấp bậc",
      "Hà Nội",
      "TP.HCM",
      "Đà Nẵng",
      "Khác",
      "Không xác định thành phố",
    ]);
  });

  it("fr33: mỗi dòng thành phố là một <button> trong <li> của một <ul> trong <figure>", async () => {
    routeCityShares({ all: [ok("all")] });
    await openScreen();
    const haNoi = cityButton("Hà Nội");

    expect(haNoi.tagName).toBe("BUTTON");
    expect(haNoi.getAttribute("type")).toBe("button");
    expect(haNoi.closest("li")?.parentElement?.tagName).toBe("UL");
    expect(haNoi.closest("figure")).not.toBeNull();
  });
});
