import { describe, expect, it, vi } from "vitest";

import {
  type CellMeta,
  type CitySharesEnvelope,
  type CoverageNote,
  fetchCityShares,
} from "@/lib/city-shares";

import { fakeEnvelope, statEnvelope } from "./fixtures/envelopes";
import { jsonResponse } from "./helpers/fetch";

type FetchArgs = [input: RequestInfo | URL, init?: RequestInit];

function stubFetch(status: number, body: unknown) {
  const fetchMock = vi.fn(async (..._args: FetchArgs) => jsonResponse(status, body));
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

/** Như `stubFetch`, nhưng `json()` trả thẳng `body`: để thử giá trị JSON không chở được (NaN). */
function stubFetchParsed(body: unknown) {
  const response = jsonResponse(200, {});
  response.json = async () => body;
  vi.stubGlobal("fetch", vi.fn(async (..._args: FetchArgs) => response));
}

function errorBody(code: string, message: string, snapshotDate: string | null = null) {
  return { error: { code, message, snapshot_date: snapshotDate } };
}

describe("ad17 — đọc city-shares qua proxy", () => {
  it("ad17: gọi /api/v1/city-shares?role= qua proxy và trả envelope", async () => {
    const envelope = fakeEnvelope("data_ai");
    const fetchMock = stubFetch(200, envelope);

    const result = await fetchCityShares("data_ai");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(String(fetchMock.mock.calls[0][0])).toBe("/api/v1/city-shares?role=data_ai");
    expect(result).toEqual({ kind: "ok", envelope });
  });

  it("ad17: mã vai trò được mã hóa trong query", async () => {
    const fetchMock = stubFetch(404, errorBody("unknown_cell", "Không có ô."));

    await fetchCityShares("a&b c");

    expect(String(fetchMock.mock.calls[0][0])).toBe("/api/v1/city-shares?role=a%26b%20c");
  });

  it("ad17: chuyển AbortSignal cho fetch", async () => {
    const fetchMock = stubFetch(200, fakeEnvelope("all"));
    const controller = new AbortController();

    await fetchCityShares("all", { signal: controller.signal });

    expect(fetchMock.mock.calls[0][1]?.signal).toBe(controller.signal);
  });

  it("ad17: nhận envelope hình #69 (n_by_measure rỗng, một dòng n = 0)", async () => {
    const envelope = statEnvelope();
    stubFetch(200, envelope);

    expect(await fetchCityShares("data_ai")).toEqual({ kind: "ok", envelope });
  });
});

describe("ad17 — bảng lỗi", () => {
  it("ad17: 502 api_unavailable trả message, cho thử lại", async () => {
    stubFetch(502, errorBody("api_unavailable", "Dịch vụ API hiện không phản hồi. Vui lòng thử lại sau."));

    expect(await fetchCityShares("all")).toEqual({
      kind: "error",
      code: "api_unavailable",
      message: "Dịch vụ API hiện không phản hồi. Vui lòng thử lại sau.",
      snapshotDate: null,
      retryable: true,
    });
  });

  it("ad17: 404 unknown_cell trả message kèm snapshot_date, không cho thử lại", async () => {
    stubFetch(404, errorBody("unknown_cell", "Không có ô thống kê nào cho vai trò đã chọn.", "2026-11-03"));

    expect(await fetchCityShares("khong_ton_tai")).toEqual({
      kind: "error",
      code: "unknown_cell",
      message: "Không có ô thống kê nào cho vai trò đã chọn.",
      snapshotDate: "2026-11-03",
      retryable: false,
    });
  });

  it.each([
    [500, "invalid_response"],
    [500, "internal_error"],
    [422, "invalid_query"],
    [400, "http_error"],
    [404, "not_found"],
  ])("ad17: %i %s trả message, cho thử lại", async (status, code) => {
    stubFetch(status, errorBody(code, `Lỗi ${code}.`));

    expect(await fetchCityShares("all")).toEqual({
      kind: "error",
      code,
      message: `Lỗi ${code}.`,
      snapshotDate: null,
      retryable: true,
    });
  });

  it("ad17: fetch bị từ chối thì không đọc được", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("Failed to fetch");
      }),
    );

    expect(await fetchCityShares("all")).toEqual({ kind: "unreadable" });
  });

  it("ad17: body 200 không phải JSON thì không đọc được", async () => {
    stubFetch(200, "<html>not json</html>");

    expect(await fetchCityShares("all")).toEqual({ kind: "unreadable" });
  });

  it("ad17: body lỗi không phải JSON thì không đọc được", async () => {
    stubFetch(502, "<html>Bad Gateway</html>");

    expect(await fetchCityShares("all")).toEqual({ kind: "unreadable" });
  });

  it("ad17: snapshot_date của lỗi không phải YYYY-MM-DD thì trả null", async () => {
    stubFetch(404, errorBody("unknown_cell", "Không có ô.", "03/11/2026"));

    expect(await fetchCityShares("all")).toMatchObject({ kind: "error", snapshotDate: null });
  });

  it("ad17: body lỗi thiếu message thì không đọc được", async () => {
    stubFetch(500, { error: { code: "internal_error" } });

    expect(await fetchCityShares("all")).toEqual({ kind: "unreadable" });
  });
});

describe("ad17 — envelope hỏng thì không đọc được", () => {
  const broken: [string, (envelope: CitySharesEnvelope) => unknown][] = [
    ["thiếu meta", ({ data }) => ({ data })],
    ["thiếu data", ({ meta }) => ({ meta })],
    [
      "thiếu dòng da_nang",
      (envelope) => {
        envelope.data.rows = envelope.data.rows.filter((row) => row.city !== "da_nang");
        return envelope;
      },
    ],
    [
      "thiếu dòng unknown",
      (envelope) => {
        envelope.data.rows = envelope.data.rows.filter((row) => row.city !== "unknown");
        return envelope;
      },
    ],
    [
      "trùng dòng ha_noi",
      (envelope) => {
        envelope.data.rows.push(structuredClone(envelope.data.rows[0]));
        return envelope;
      },
    ],
    [
      "ô của một dòng không có trong meta.cells",
      (envelope) => {
        delete envelope.meta.cells[envelope.data.rows[2].share.cell_id];
        return envelope;
      },
    ],
    [
      "ô toàn quốc không có trong meta.cells",
      (envelope) => {
        delete envelope.meta.cells[envelope.data.total_cell_id];
        return envelope;
      },
    ],
    [
      "share.value null",
      (envelope) => {
        (envelope.data.rows[0].share as { value: number | null }).value = null;
        return envelope;
      },
    ],
    [
      "display lạ",
      (envelope) => {
        (envelope.data.rows[0].share as { display: string }).display = "hidden";
        return envelope;
      },
    ],
    [
      "thiếu thresholds.min_sample",
      (envelope) => {
        delete (envelope.meta.thresholds as Partial<typeof envelope.meta.thresholds>).min_sample;
        return envelope;
      },
    ],
    [
      "coverage_notes rỗng",
      (envelope) => {
        envelope.meta.coverage_notes = [];
        return envelope;
      },
    ],
    [
      "thiếu sources",
      (envelope) => {
        delete (envelope.meta as Partial<typeof envelope.meta>).sources;
        return envelope;
      },
    ],
    [
      "snapshot_date sai định dạng",
      (envelope) => {
        envelope.meta.snapshot_date = "03/11/2026";
        return envelope;
      },
    ],
    [
      "snapshot_status lạ",
      (envelope) => {
        (envelope.meta as { snapshot_status: string }).snapshot_status = "draft";
        return envelope;
      },
    ],
    [
      "thiếu sources_failed",
      (envelope) => {
        delete (envelope.meta as Partial<typeof envelope.meta>).sources_failed;
        return envelope;
      },
    ],
    [
      "sources_failed không phải mảng",
      (envelope) => {
        (envelope.meta as { sources_failed: unknown }).sources_failed = "topdev";
        return envelope;
      },
    ],
    [
      "sources rỗng",
      (envelope) => {
        envelope.meta.sources = [];
        return envelope;
      },
    ],
    [
      "min_sample bằng 0",
      (envelope) => {
        envelope.meta.thresholds.min_sample = 0;
        return envelope;
      },
    ],
    [
      "min_sample không nguyên",
      (envelope) => {
        envelope.meta.thresholds.min_sample = 2.5;
        return envelope;
      },
    ],
    [
      "coverage note thiếu text",
      (envelope) => {
        delete (envelope.meta.coverage_notes[1] as Partial<CoverageNote>).text;
        return envelope;
      },
    ],
    [
      "n của ô âm",
      (envelope) => {
        envelope.meta.cells[envelope.data.rows[1].share.cell_id].n = -1;
        return envelope;
      },
    ],
    [
      "n của ô không nguyên",
      (envelope) => {
        envelope.meta.cells[envelope.data.rows[1].share.cell_id].n = 2.5;
        return envelope;
      },
    ],
    [
      "ô thiếu n",
      (envelope) => {
        delete (envelope.meta.cells[envelope.data.rows[1].share.cell_id] as Partial<CellMeta>).n;
        return envelope;
      },
    ],
    [
      "kind khác composition_share",
      (envelope) => {
        (envelope.data.rows[0].share as { kind: string }).kind = "skill_rate";
        return envelope;
      },
    ],
    [
      "value dưới 0",
      (envelope) => {
        envelope.data.rows[0].share.value = -0.1;
        return envelope;
      },
    ],
    [
      "value trên 1",
      (envelope) => {
        envelope.data.rows[0].share.value = 1.2;
        return envelope;
      },
    ],
    [
      "một dòng không phải object",
      (envelope) => {
        (envelope.data.rows as unknown[])[3] = "other";
        return envelope;
      },
    ],
    [
      "data.role khác vai trò đã hỏi",
      (envelope) => {
        envelope.data.role = "backend";
        return envelope;
      },
    ],
  ];

  it.each(broken)("ad17: %s", async (_name, breakIt) => {
    stubFetch(200, breakIt(fakeEnvelope("data_ai")));

    expect(await fetchCityShares("data_ai")).toEqual({ kind: "unreadable" });
  });

  it("ad17: value NaN", async () => {
    const envelope = fakeEnvelope("data_ai");
    envelope.data.rows[0].share.value = Number.NaN;
    stubFetchParsed(envelope);

    expect(await fetchCityShares("data_ai")).toEqual({ kind: "unreadable" });
  });
});
