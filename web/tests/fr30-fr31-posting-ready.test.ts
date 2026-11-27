import { describe, expect, it } from "vitest";

import {
  POSTING_SIGN_CODES,
  fetchPostingCheck,
  isPostingCheckEnvelope,
  type PostingCheckEnvelope,
  type PostingReadData,
} from "@/lib/posting";

import checkNotReady from "./fixtures/posting-check-backend.junior-have.json";
import readBackend from "./fixtures/posting-read-backend.json";
import readyFull from "./fixtures/posting-check-ready-full.json";
import readySparse from "./fixtures/posting-check-ready-sparse.json";

// Hai fixture `ready` là ví dụ viết tay (API giả còn `not_ready` tới #240–#246), được `tests/api/test_fr30_fr31_posting_ready_shapes.py`
// kiểm bằng chính schema của API và `test_ad17_web_fixtures.py` giữ bằng `tests/api/posting_examples.py`. Ở đây kiểm phía web:
// màn không bị trắng khi #240 và #244 nối số thật, và bộ kiểm từ chối hình sai.
const full = readyFull as unknown as PostingCheckEnvelope;
const sparse = readySparse as unknown as PostingCheckEnvelope;
const notReady = checkNotReady as unknown as PostingCheckEnvelope;
const read = (readBackend as unknown as { data: PostingReadData }).data;

type Json = Record<string, any>;

function clone(env: PostingCheckEnvelope): Json {
  return structuredClone(env) as unknown as Json;
}

function accepts(env: Json): boolean {
  return isPostingCheckEnvelope(env);
}

function stubFetch(status: number, body: unknown): void {
  globalThis.fetch = (async () => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } })) as typeof fetch;
}

describe("FR-30/31 hình ready của market và warnings", () => {
  it("hai ví dụ ready và fixture not_ready đều qua bộ kiểm, nên màn không trắng khi API nối số thật", () => {
    expect(isPostingCheckEnvelope(full)).toBe(true);
    expect(isPostingCheckEnvelope(sparse)).toBe(true);
    expect(isPostingCheckEnvelope(notReady)).toBe(true);
    expect(full.data.market.status).toBe("ready");
    expect(full.data.warnings.status).toBe("ready");
  });

  it("bước hai ready đọc được qua fetchPostingCheck, kèm phần match", async () => {
    stubFetch(200, full);
    const result = await fetchPostingCheck({ read, have: ["java"] });
    expect(result.kind).toBe("ok");
    if (result.kind === "ok") expect(result.envelope.data.match.status).toBe("ready");
  });

  it("market full: phân vị là Stat, mẫu số X/30 tra ở ô của market, lương đã quy đổi kèm tỷ giá và đơn vị", () => {
    const { market } = full.data;
    if (market.status !== "ready") throw new Error("ví dụ phải ready");
    expect(market.cell_id).toBe("vn.backend");
    expect(market.years.percentile?.kind).toBe("percentile");
    expect(market.years.ci_low).toBeNull(); // n = 110 từ 100: không có khoảng tin cậy
    expect(market.salary.converted?.fx).toEqual({ rate: 25000, unit: "vnd_per_usd", fx_version: "fx-2026-11-03" });
    expect(full.meta.cells[market.cell_id].n_by_measure.salary).toBe(35);
  });

  it("market sparse: chưa đủ dữ liệu (X/30), khoảng tin cậy 95% khi 30 ≤ n < 100, lương không ghi là câu trung tính", () => {
    const { market } = sparse.data;
    if (market.status !== "ready") throw new Error("ví dụ phải ready");
    expect(market.years.state).toBe("not_enough_data");
    expect(sparse.meta.cells[market.cell_id].n_by_measure.experience_years).toBe(24);
    expect(market.skill_count.ci_low?.value).toBeLessThanOrEqual(market.skill_count.percentile?.value ?? -1);
    expect(market.salary).toMatchObject({ state: "not_stated", note: "salary_not_stated", converted: null });
    expect(sparse.data.warnings.salary_note).toBe("salary_not_stated");
  });

  it("warnings: đủ bảy dấu hiệu D1–D7 theo thứ tự, mỗi dấu hiệu có trạng thái và dữ kiện", () => {
    expect(POSTING_SIGN_CODES).toEqual([
      "d1_wide_skills",
      "d2_specific_heavy",
      "d3_high_req_low_pay",
      "d4_reposted",
      "d5_unusual_contact",
      "d6_fee_first",
      "d7_no_company",
    ]);
    for (const env of [full, sparse]) {
      const { warnings } = env.data;
      expect(warnings.disclaimer).toBe("signs_are_hints");
      expect(warnings.signs.map((s) => s.code)).toEqual([...POSTING_SIGN_CODES]);
    }
    const d1 = full.data.warnings.signs[0];
    expect(d1.status).toBe("triggered");
    expect(d1.fact).toMatchObject({ kind: "d1_wide_skills", skill_count: 14 });
    expect(full.data.warnings.signs[4].source_field).toBe("contacts");
    expect(sparse.data.warnings.signs[3]).toMatchObject({ status: "not_evaluable", reason: "not_in_data", fact: null });
  });

  it("không câu cấm trong bất kỳ giá trị nào của ví dụ", () => {
    const text = JSON.stringify([full, sparse]).toLowerCase();
    for (const word of ["lừa đảo", "tin giả", "tin ma"]) expect(text).not.toContain(word);
  });
});

describe("bộ kiểm từ chối hình ready sai", () => {
  const bad: [string, (env: Json) => void][] = [
    ["market ready thiếu cell_id", (e) => (e.data.market.cell_id = null)],
    ["market ready trỏ ô không có trong meta", (e) => (e.data.market.cell_id = "khong.co")],
    ["market not_ready còn dữ liệu", (e) => Object.assign(e.data, { market: { ...e.data.market, status: "not_ready" } })],
    ["market thiếu mục lương", (e) => delete e.data.market.salary],
    ["market ready thiếu câu ghi chú cố định", (e) => (e.data.market.note = null)],
    ["câu ghi chú của market là chữ tự do", (e) => (e.data.market.note = "So sánh chỉ để tham khảo")],
    ["trạng thái phân vị lạ", (e) => (e.data.market.years.state = "pending")],
    ["compared mà phân vị ẩn", (e) => (e.data.market.years.percentile.display = "null_data")],
    ["phân vị không phải kind percentile", (e) => (e.data.market.years.percentile.kind = "skill_rate")],
    ["khoảng tin cậy chỉ có một đầu", (e) => (e.data.market.skill_count.ci_low = e.data.market.skill_count.percentile)],
    ["khoảng tin cậy không bao phân vị", (e) => (e.data.market.skill_count.ci_high = { ...e.data.market.skill_count.percentile, value: 0.5 })],
    ["lương compared thiếu quy đổi", (e) => (e.data.market.salary.converted = null)],
    ["lương compared thiếu khoảng giữa", (e) => (e.data.market.salary.low = null)],
    ["tỷ giá không dương", (e) => (e.data.market.salary.converted.fx.rate = 0)],
    ["đơn vị tỷ giá lạ", (e) => (e.data.market.salary.converted.fx.unit = "eur_per_vnd")],
    ["trạng thái lương cũ not_comparable", (e) => (e.data.market.salary.state = "not_comparable")],
    ["warnings thiếu một dấu hiệu", (e) => e.data.warnings.signs.pop()],
    ["warnings sai thứ tự dấu hiệu", (e) => e.data.warnings.signs.reverse()],
    ["dấu hiệu mã lạ", (e) => (e.data.warnings.signs[0].code = "d9_la")],
    ["trạng thái dấu hiệu lạ", (e) => (e.data.warnings.signs[0].status = "maybe")],
    ["triggered thiếu dữ kiện", (e) => (e.data.warnings.signs[0].fact = null)],
    ["triggered thiếu gợi ý hành động", (e) => (e.data.warnings.signs[0].action = null)],
    ["dữ kiện lệch mã dấu hiệu", (e) => (e.data.warnings.signs[0].fact.kind = "d2_specific_heavy")],
    ["D1 thiếu P90", (e) => (e.data.warnings.signs[0].fact.p90 = null)],
    ["not_evaluable thiếu lý do", (e) => (e.data.warnings.signs[2].status = "not_evaluable")],
    ["thiếu câu ghi chú cố định", (e) => (e.data.warnings.disclaimer = null)],
    ["câu ghi chú là chữ tự do", (e) => (e.data.warnings.disclaimer = "Dấu hiệu là gợi ý")],
    ["checklist thiếu mục", (e) => e.data.warnings.checklist.pop()],
    ["D2 không đánh giá được vì không có trong dữ liệu", (e) => Object.assign(e.data.warnings.signs[1], { status: "not_evaluable", reason: "not_in_data", fact: null, action: null })],
    ["checklist present không phải bool", (e) => (e.data.warnings.checklist[0].present = "có")],
    ["collected_match lệch dữ kiện D4", (e) => (e.data.warnings.collected_match.repost_count = 9)],
    ["D4 triggered mà không có tin khớp", (e) => (e.data.warnings.collected_match = null)],
  ];
  for (const [why, mutate] of bad) {
    it(why, () => {
      const env = clone(full);
      expect(accepts(env)).toBe(true);
      mutate(env);
      expect(accepts(env)).toBe(false);
    });
  }

  it("lương not_stated mà thiếu câu trung tính bị từ chối", () => {
    const env = clone(sparse);
    expect(accepts(env)).toBe(true);
    env.data.market.salary.note = null;
    expect(accepts(env)).toBe(false);
  });

  it("not_ready còn dữ liệu bị từ chối, và not_ready cũ vẫn được nhận", () => {
    const stale = clone(notReady);
    stale.data.warnings.disclaimer = "signs_are_hints";
    expect(accepts(stale)).toBe(false);
    expect(accepts(clone(notReady))).toBe(true);
  });

  it("market sparse: các trạng thái hợp lệ còn lại", () => {
    const env = clone(sparse);
    env.data.market.years = { state: "not_stated", percentile: null, ci_low: null, ci_high: null };
    env.data.market.salary = { state: "not_numeric", position: null, low: null, high: null, converted: null, note: null };
    expect(accepts(env)).toBe(true);
    env.data.market.salary = { ...env.data.market.salary, state: "not_enough_data", converted: { min_vnd_month: 1, max_vnd_month: 2, fx: null } };
    env.data.market.salary.low = { ...env.data.market.skill_count.percentile, value: null, display: "null_data" };
    env.data.market.salary.high = { ...env.data.market.salary.low };
    expect(accepts(env)).toBe(true);
  });
});

describe("hợp đồng đã chốt ở đợt rà lại 2026-11-27", () => {
  it("D2 không đánh giá được khi ô chưa đủ mẫu (nhóm kỹ năng chỉ có ở n ≥ 30)", () => {
    const env = clone(sparse);
    Object.assign(env.data.warnings.signs[1], { status: "not_evaluable", reason: "not_enough_data", fact: null, action: null });
    expect(accepts(env)).toBe(true);
  });

  it("market not_ready mà còn câu ghi chú bị từ chối, ready mang mã so sánh không phải phán quyết", () => {
    expect((full.data.market as { note: string }).note).toBe("comparisons_not_verdict");
    const stale = clone(notReady);
    stale.data.market.note = "comparisons_not_verdict";
    expect(accepts(stale)).toBe(false);
  });

  it("checklist present null là 'không biết' và được nhận", () => {
    const env = clone(full);
    env.data.warnings.checklist[3].present = null;
    expect(accepts(env)).toBe(true);
  });

  it("D7 với thêm trường lạ vẫn được nhận (tương thích tiến), kind sai thì không", () => {
    const env = clone(full);
    const d7 = env.data.warnings.signs[6];
    expect(d7.status).toBe("triggered");
    d7.fact.later_field = 1;
    expect(accepts(env)).toBe(true);
    d7.fact.kind = "d6_fee_first";
    expect(accepts(env)).toBe(false);
  });
});
