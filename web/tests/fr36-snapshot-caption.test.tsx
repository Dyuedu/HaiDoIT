import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { MapScreen } from "@/app/components/map/map-screen";

import { fakeEnvelope, STAT_COVERAGE_NOTES, statEnvelope } from "./fixtures/envelopes";
import { jsonResponse, routeCityShares } from "./helpers/fetch";

const FR36_NOTES = {
  posting_not_demand: "Tin tuyển dụng không đồng nghĩa với vị trí đang thực sự cần người.",
  big_city_bias: "Dữ liệu nghiêng về thành phố lớn và công ty lớn.",
  salary_disclosed_only: "Con số lương chỉ phản ánh những tin có công bố lương.",
};

async function openWith(envelope = fakeEnvelope("all")) {
  routeCityShares({ [envelope.data.role]: [() => jsonResponse(200, envelope)] });
  const user = userEvent.setup();
  render(<MapScreen />);
  await screen.findByRole("button", { name: /^Hà Nội:/ });
  return user;
}

function caption() {
  return screen.getByRole("region", { name: "Nguồn và lưu ý" });
}

function noteTexts() {
  return within(caption())
    .getAllByRole("listitem")
    .map((item) => item.textContent);
}

describe("fr36 — chú thích snapshot", () => {
  it("fr36: hiện nguồn đúng như API gửi, ngày snapshot và bốn câu coverage_notes nguyên văn", async () => {
    const envelope = fakeEnvelope("all");
    await openWith(envelope);

    expect(caption().textContent).toContain(envelope.meta.sources.join(", "));
    expect(caption().textContent).toContain("03/11/2026");
    expect(noteTexts()).toEqual(envelope.meta.coverage_notes.map((note) => note.text));
    expect(noteTexts()).toEqual(expect.arrayContaining(Object.values(FR36_NOTES)));
    expect(caption().textContent).not.toContain("Nguồn lỗi ở snapshot này");
  });

  it("fr36: chú thích vẫn hiện ở lối Bảng", async () => {
    const user = await openWith();

    await user.click(screen.getByRole("button", { name: "Bảng" }));

    screen.getByRole("table");
    expect(noteTexts()).toHaveLength(4);
    expect(caption().textContent).toContain("03/11/2026");
  });

  it("fr36: snapshot cũ hiện đúng ngày của snapshot đó", async () => {
    const envelope = fakeEnvelope("all");
    envelope.meta.snapshot_date = "2026-10-28";
    await openWith(envelope);

    expect(caption().textContent).toContain("28/10/2026");
  });

  it("fr36: snapshot partial ghi 'Nguồn lỗi ở snapshot này: …'", async () => {
    const envelope = fakeEnvelope("all");
    envelope.meta.snapshot_status = "partial";
    envelope.meta.sources_failed = ["topdev"];
    await openWith(envelope);

    expect(caption().textContent).toContain("Nguồn lỗi ở snapshot này: topdev");
  });

  it("fr36: envelope hình #69 in nguyên văn bốn câu, kể cả câu số nguồn", async () => {
    await openWith(statEnvelope("all"));

    expect(noteTexts()).toEqual(STAT_COVERAGE_NOTES.map((note) => note.text));
  });

  it("fr36: không có chú thích khi chưa có dữ liệu", async () => {
    routeCityShares({
      all: [
        () =>
          jsonResponse(502, {
            error: { code: "api_unavailable", message: "API tắt.", snapshot_date: null },
          }),
      ],
    });
    render(<MapScreen />);

    await screen.findByRole("alert");
    expect(screen.queryByRole("region", { name: "Nguồn và lưu ý" })).toBeNull();
  });
});
