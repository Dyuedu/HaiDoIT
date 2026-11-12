import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import MapPage from "@/app/page";

import { fakeEnvelope } from "./fixtures/envelopes";
import { jsonResponse, routeCityShares } from "./helpers/fetch";

describe("fr33 #285 — câu giới thiệu trang Bản đồ", () => {
  it("fr33: câu giới thiệu nói tới mọi tỉnh, thành, làm từ xa và nước ngoài, không chỉ ba thành phố", async () => {
    routeCityShares({ "all|entry": [() => jsonResponse(200, fakeEnvelope("all", "entry"))] });
    render(<MapPage />);
    await screen.findByRole("button", { name: /^Hà Nội:/ });

    const intro = screen.getByText(/tuyển dụng IT của vai trò bạn chọn/);
    expect(intro.textContent).toContain("từng tỉnh, thành");
    expect(intro.textContent).toContain("làm từ xa");
    expect(intro.textContent).toContain("nước ngoài");
    expect(intro.textContent).not.toContain("Hà Nội, TP.HCM và Đà Nẵng chiếm");
  });
});
