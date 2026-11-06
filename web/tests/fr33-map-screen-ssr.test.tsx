// @vitest-environment node
import { renderToString } from "react-dom/server";
import { expect, it } from "vitest";

import { MapScreen } from "@/app/components/map/map-screen";

import { fakeEnvelope } from "./fixtures/envelopes";
import { jsonResponse, routeCityShares } from "./helpers/fetch";

// Chạy trong môi trường node, không có `window`: render phía server mà chạm API trình duyệt
// thì test này đỏ.
it("fr33: render phía server chỉ có trạng thái đang tải, không gọi API", () => {
  const fetchMock = routeCityShares({ all: [() => jsonResponse(200, fakeEnvelope("all"))] });

  const html = renderToString(<MapScreen />);

  expect(typeof window).toBe("undefined");
  expect(html).toContain("Đang tải số liệu…");
  expect(html).not.toContain("%");
  expect(fetchMock).not.toHaveBeenCalled();
});
