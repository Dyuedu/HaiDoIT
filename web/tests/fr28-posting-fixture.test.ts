import { describe, expect, it } from "vitest";

import {
  fetchPostingCheck,
  fetchPostingRead,
  isPostingCheckEnvelope,
  isPostingReadResponse,
  postingCheckUrl,
  postingFactsOf,
  type PostingCheckEnvelope,
  type PostingReadResponse,
} from "@/lib/posting";

import checkBackendJuniorHave from "./fixtures/posting-check-backend.junior-have.json";
import checkBackendJunior from "./fixtures/posting-check-backend.junior.json";
import checkBackendInternHave from "./fixtures/posting-check-backend.intern-have.json";
import checkBackendUnknownFee from "./fixtures/posting-check-backend.unknown-fee.json";
import checkDataEngineer from "./fixtures/posting-check-data_engineer.entry-have.json";
import readBackend from "./fixtures/posting-read-backend.json";
import readCloud from "./fixtures/posting-read-cloud.json";
import readFee from "./fixtures/posting-read-fee.json";
import readNotIt from "./fixtures/posting-read-not-it.json";
import readNotPosting from "./fixtures/posting-read-not-posting.json";
import readTooShort from "./fixtures/posting-read-too-short.json";

// Các fixture là response của API giả (#230). `tests/api/test_ad17_web_fixtures.py` so chúng với API,
// nên đây chỉ kiểm phía web đọc được, dựng URL chỉ bằng mã và số, và đọc lỗi chuẩn.
const reads = {
  backend: readBackend as unknown as PostingReadResponse,
  fee: readFee as unknown as PostingReadResponse,
  notPosting: readNotPosting as unknown as PostingReadResponse,
  tooShort: readTooShort as unknown as PostingReadResponse,
  notIt: readNotIt as unknown as PostingReadResponse,
  cloud: readCloud as unknown as PostingReadResponse,
};
const checks = {
  juniorHave: checkBackendJuniorHave as unknown as PostingCheckEnvelope,
  junior: checkBackendJunior as unknown as PostingCheckEnvelope,
  internHave: checkBackendInternHave as unknown as PostingCheckEnvelope,
  notEnough: checkDataEngineer as unknown as PostingCheckEnvelope,
  unknownFee: checkBackendUnknownFee as unknown as PostingCheckEnvelope,
};

function stubFetch(status: number, body: unknown, seen: { url?: string; init?: RequestInit } = {}): void {
  globalThis.fetch = (async (url: string, init?: RequestInit) => {
    seen.url = url;
    seen.init = init;
    return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
}

describe("FR-26 hình đọc tin dán", () => {
  it("mọi fixture qua bộ kiểm hợp đồng", () => {
    for (const read of Object.values(reads)) expect(isPostingReadResponse(read)).toBe(true);
  });

  it("tin Backend Junior có mã, đếm lần nhắc, chữ chưa nhận diện và sự kiện đóng", () => {
    const { data } = reads.backend;
    expect(data.is_posting).toBe(true);
    expect(data.role).toBe("backend");
    expect(data.level).toBe("junior");
    expect(data.skills.map((s) => s.code)).toContain("java");
    expect(data.unrecognised.length).toBeGreaterThan(0);
    expect(data.salary).toEqual({ min: 10000000, max: 18000000, currency: "vnd", period: "month" });
    expect(data.model_id).toBeTruthy();
    expect(data.prompt_version).toBeTruthy();
    expect(data.vocab_version).toBeTruthy();
  });

  it("không phải tin, quá ngắn hoặc không thuộc IT: có lý do, không có gì để khớp", () => {
    expect(reads.notPosting.data.reason).toBe("not_posting");
    expect(reads.tooShort.data.reason).toBe("too_short");
    expect(reads.notIt.data.reason).toBe("not_it"); // UX-DR44: "Tin này có vẻ không thuộc lĩnh vực IT"
    for (const { data } of [reads.notPosting, reads.tooShort, reads.notIt]) {
      expect(data.is_posting).toBe(false);
      expect(data.skills).toEqual([]);
      expect(data.role).toBeNull();
      expect(data.branch).toBeNull();
      expect(data.collected).toBeNull();
      expect(data.contact_quotes).toEqual([]);
    }
  });

  it("tin DevOps có nhánh, tin thu thập khớp (đủ link) và lương không có số", () => {
    const { data } = reads.cloud;
    expect(data.branch).toBe("cloud");
    expect(data.salary).toBeNull();
    expect(data.salary_non_numeric).toBe(true);
    expect(data.collected).toMatchObject({ site: expect.any(String), repost_count: expect.any(Number), snapshots_seen: expect.any(Number) });
    expect(data.collected?.url).toMatch(/^https?:\/\//);
  });

  it("tin có phí có trích dẫn liên hệ cho từng kênh, và sự kiện danh sách chi tiết", () => {
    const { data } = reads.fee;
    expect(data.contact_quotes.map((q) => q.channel).sort()).toEqual(["telegram", "zalo"]);
    expect(data.contact_quotes.every((q) => q.quote.length > 0 && q.quote.length <= 120)).toBe(true);
    expect(data.duties_described).toBe(false);
    expect(data.title_level).toBeNull();
    expect(reads.backend.data.title_level).toBe("junior");
  });

  it("bộ kiểm từ chối tin sai hợp đồng", () => {
    const bad = structuredClone(reads.backend) as unknown as { data: Record<string, unknown> };
    bad.data.reason = "not_posting";
    expect(isPostingReadResponse(bad)).toBe(false);
    const dup = structuredClone(reads.backend);
    dup.data.skills.push({ ...dup.data.skills[0] });
    expect(isPostingReadResponse(dup)).toBe(false);
    expect(isPostingReadResponse({ data: reads.backend.data, meta: {} })).toBe(false);
  });

  it("bộ kiểm từ chối các trường mới sai hợp đồng", () => {
    const mutate = (fn: (d: Record<string, any>) => void, base = reads.cloud): boolean => {
      const copy = structuredClone(base) as unknown as { data: Record<string, any> };
      fn(copy.data);
      return isPostingReadResponse(copy);
    };
    expect(mutate(() => undefined)).toBe(true);
    expect(mutate((d) => (d.reason = "khac"), reads.notIt)).toBe(false);
    expect(mutate((d) => (d.branch = ""))).toBe(false);
    expect(mutate((d) => (d.branch = undefined))).toBe(false);
    expect(mutate((d) => (d.title_level = "unknown"))).toBe(false);
    expect(mutate((d) => (d.duties_described = null))).toBe(false);
    expect(mutate((d) => (d.salary_non_numeric = "true"))).toBe(false);
    expect(mutate((d) => (d.salary = { min: 1, max: 2, currency: "vnd", period: "month" }))).toBe(false); // vừa có số vừa "không có số"
    expect(mutate((d) => (d.collected.url = null))).toBe(false); // FR-32: phải có link
    expect(mutate((d) => (d.collected.url = "ftp://x"))).toBe(false);
    expect(mutate((d) => (d.collected.repost_count = -1))).toBe(false);
    expect(mutate((d) => (d.contact_quotes = Array(6).fill({ channel: "zalo", quote: "q" })), reads.fee)).toBe(false);
    expect(mutate((d) => (d.contact_quotes = [{ channel: "company_email", quote: "q" }]), reads.fee)).toBe(false); // kênh không có trong contacts
    expect(mutate((d) => (d.contact_quotes = [{ channel: "zalo", quote: "q".repeat(121) }]), reads.fee)).toBe(false);
    expect(mutate((d) => (d.reason = "not_it"), reads.backend)).toBe(false);
  });
});

describe("AD-22 query của bước 2 chỉ có mã và số", () => {
  it("URL dựng từ tin chỉ chứa mã kỹ năng, cấp và sự kiện đóng", () => {
    const url = postingCheckUrl({
      read: reads.backend.data,
      have: ["java", "sql"],
    });
    expect(url).not.toBeNull();
    const query = new URL(url!, "http://x").searchParams;
    expect(query.get("role")).toBe("backend");
    expect(query.get("level")).toBe("junior");
    expect(query.get("skills")).toBe(reads.backend.data.skills.map((s) => s.code).join(","));
    expect(query.get("have")).toBe("java,sql");
    expect(query.get("years_min")).toBe("1");
    expect(query.get("salary_min")).toBe("10000000");
    expect(query.get("salary_currency")).toBe("vnd");
    expect(query.get("company_named")).toBe("true");
    expect(query.get("duties_described")).toBe("true");
    expect(query.get("title_level")).toBe("junior");
    expect(query.has("branch")).toBe(false);
    expect(query.has("collected_reposts")).toBe(false);
    expect(url).toMatch(/^\/api\/v1\/posting-check\?[a-z0-9_=&.%A-F-]+$/);
    for (const phrase of reads.backend.data.unrecognised) expect(url).not.toContain(encodeURIComponent(phrase));
  });

  it("chữ chưa nhận diện và trích dẫn phí không bao giờ vào query", () => {
    const facts = postingFactsOf(reads.fee.data);
    expect(Object.keys(facts).sort()).toEqual(
      [
        "branch", "collectedReposts", "collectedSnapshots", "companyNamed", "contacts", "dutiesDescribed", "fees", "salary",
        "salaryNonNumeric", "titleLevel", "yearsMin",
      ].sort(),
    );
    expect(facts.fees).toBe(reads.fee.data.fee_mentions.length);
    const url = postingCheckUrl({ read: reads.fee.data, have: [] })!;
    for (const quote of reads.fee.data.fee_mentions) expect(decodeURIComponent(url)).not.toContain(quote);
    for (const { quote } of reads.fee.data.contact_quotes) expect(decodeURIComponent(url)).not.toContain(quote); // #245: chỉ hiện từ POST
    expect(new URL(url, "http://x").searchParams.has("have")).toBe(false);
    expect(new URL(url, "http://x").searchParams.get("duties_described")).toBe("false");
  });

  it("nhánh, số lần đăng lại và số snapshot đi vào query, còn link và tên nguồn của tin thu thập thì không", () => {
    const url = postingCheckUrl({ read: reads.cloud.data, have: [] })!;
    const query = new URL(url, "http://x").searchParams;
    expect(query.get("branch")).toBe("cloud");
    expect(query.get("collected_reposts")).toBe(String(reads.cloud.data.collected?.repost_count));
    expect(query.get("collected_snapshots")).toBe(String(reads.cloud.data.collected?.snapshots_seen));
    expect(query.get("salary_non_numeric")).toBe("true");
    expect(query.has("salary_min")).toBe(false);
    expect(decodeURIComponent(url)).not.toContain(reads.cloud.data.collected?.url as string);
    expect(decodeURIComponent(url)).not.toContain(reads.cloud.data.collected?.site as string);
    for (const name of query.keys()) expect(["role", "level", "branch", "skills", "years_min", "salary_non_numeric", "company_named", "contacts", "duties_described", "title_level", "collected_reposts", "collected_snapshots"]).toContain(name);
  });

  it("đổi vai trò thì bỏ nhánh (nhánh thuộc vai trò), đổi cấp thì giữ", () => {
    const role = new URL(postingCheckUrl({ read: reads.cloud.data, have: [], role: "backend" })!, "http://x").searchParams;
    expect(role.has("branch")).toBe(false);
    const level = new URL(postingCheckUrl({ read: reads.cloud.data, have: [], level: "entry" })!, "http://x").searchParams;
    expect(level.get("branch")).toBe("cloud");
  });

  it("đổi vai trò hoặc cấp dùng lại cùng tin, không cần chữ dán", () => {
    const url = postingCheckUrl({ read: reads.backend.data, have: [], role: "frontend", level: "entry" })!;
    const query = new URL(url, "http://x").searchParams;
    expect(query.get("role")).toBe("frontend");
    expect(query.get("level")).toBe("entry");
  });

  it("không phải tin thì không có URL", () => {
    expect(postingCheckUrl({ read: reads.notPosting.data, have: [] })).toBeNull();
    expect(postingCheckUrl({ read: reads.tooShort.data, have: [] })).toBeNull();
  });
});

describe("FR-28 fixture mục khớp, mục thị trường và cảnh báo chưa xong", () => {
  it("mọi fixture qua bộ kiểm hợp đồng", () => {
    for (const env of Object.values(checks)) expect(isPostingCheckEnvelope(env)).toBe(true);
  });

  it("ví dụ 16 trên 18 là 89%, đếm 4/4, 2/2, 0/2", () => {
    const { match } = checks.juniorHave.data;
    expect(match.level).toEqual({ points: 16, max_points: 18, percent: 89 });
    expect(match.groups.map((g) => [g.group, g.had, g.total])).toEqual([
      ["core", 4, 4],
      ["common", 2, 2],
      ["specific", 0, 2],
    ]);
    expect(match.cv_first).toHaveLength(6);
    expect([...match.cv_first].sort()).toEqual(["docker", "git", "java", "mysql", "spring_boot", "sql"]);
  });

  it("không hồ sơ: không có mức khớp, cờ have là null, nhóm và tỷ lệ vẫn có", () => {
    const { data } = checks.junior;
    expect(data.has_profile).toBe(false);
    expect(data.match.level).toBeNull();
    expect(data.match.skills.every((s) => s.have === null && s.rate.value !== null)).toBe(true);
    expect(data.match.groups.every((g) => g.had === null)).toBe(true);
  });

  it("quay về ô rộng có nhãn ở meta.cells", () => {
    const { data, meta } = checks.internHave;
    expect(data.cell_id).toBe("vn.backend");
    expect(meta.cells[data.cell_id].fallback_label).toBeTruthy();
  });

  it("không ô nào đủ mẫu: not_enough_data, không nhóm, tỷ lệ ẩn", () => {
    const { match } = checks.notEnough.data;
    expect(match.status).toBe("not_enough_data");
    expect(match.groups).toEqual([]);
    expect(match.skills.every((s) => s.group === null && s.rate.display === "null_data")).toBe(true);
  });

  it("market và warnings là not_ready và rỗng ở mọi fixture", () => {
    for (const env of Object.values(checks)) {
      expect(env.data.market).toEqual({ status: "not_ready", cell_id: null, years: null, skill_count: null, salary: null, note: null });
      expect(env.data.warnings).toEqual({
        status: "not_ready",
        checklist: [],
        signs: [],
        collected_match: null,
        salary_note: null,
        disclaimer: null,
      });
    }
  });

  it("tin có phí không ghi cấp quay về ô mọi cấp chứ không 404", () => {
    const { data, meta } = checks.unknownFee;
    expect(data.level).toBe("unknown");
    expect(data.cell_id).toBe("vn.backend");
    expect(meta.cells[data.cell_id].fallback_label).toBeTruthy();
  });

  it("bộ kiểm từ chối mục chưa xong mà có số, và mức khớp vô lý", () => {
    const market = structuredClone(checks.juniorHave) as unknown as { data: { market: Record<string, unknown> } };
    market.data.market.years = { state: "not_stated", percentile: null, ci_low: null, ci_high: null };
    expect(isPostingCheckEnvelope(market)).toBe(false);
    const level = structuredClone(checks.juniorHave);
    level.data.match.level = { points: 19, max_points: 18, percent: 105 };
    expect(isPostingCheckEnvelope(level)).toBe(false);
    const cell = structuredClone(checks.juniorHave);
    delete (cell.meta.cells as Record<string, unknown>)[cell.data.cell_id];
    expect(isPostingCheckEnvelope(cell)).toBe(false);
  });
});

describe("gọi API", () => {
  it("POST posting-reads gửi chỉ {text}, không lưu cache, và đọc kết quả", async () => {
    const seen: { url?: string; init?: RequestInit } = {};
    stubFetch(200, reads.backend, seen);
    const result = await fetchPostingRead({ text: "nội dung tin" });
    expect(result.kind).toBe("ok");
    expect(seen.url).toBe("/api/v1/posting-reads");
    expect(seen.init?.method).toBe("POST");
    expect(JSON.parse(String(seen.init?.body))).toEqual({ text: "nội dung tin" });
    expect(seen.init?.cache).toBe("no-store");
  });

  it("đọc lỗi chuẩn của đường thật và cho biết có nên thử lại không", async () => {
    const codes: Record<string, boolean> = {
      text_too_long: false,
      invalid_query: false,
      rate_limited: true,
      read_unavailable: true,
      read_timeout: true,
      read_failed: true,
    };
    for (const [code, retryable] of Object.entries(codes)) {
      stubFetch(503, { error: { code, message: "m", snapshot_date: null } });
      expect(await fetchPostingRead({ text: "x" })).toMatchObject({ kind: "error", code, retryable });
    }
  });

  it("body sai hợp đồng hoặc mạng hỏng là unreadable", async () => {
    stubFetch(200, { data: { is_posting: "có" } });
    expect(await fetchPostingRead({ text: "x" })).toEqual({ kind: "unreadable" });
    globalThis.fetch = (async () => {
      throw new Error("mạng");
    }) as typeof fetch;
    expect(await fetchPostingRead({ text: "x" })).toEqual({ kind: "unreadable" });
  });

  it("check_unavailable (503) là lỗi tạm thời, thử lại được; khác unknown_cell (404) là không có số", async () => {
    stubFetch(503, { error: { code: "check_unavailable", message: "m", snapshot_date: null } });
    expect(await fetchPostingCheck({ read: reads.backend.data, have: [] })).toMatchObject({
      kind: "error",
      code: "check_unavailable",
      retryable: true,
    });
    stubFetch(404, { error: { code: "unknown_cell", message: "m", snapshot_date: null } });
    expect(await fetchPostingCheck({ read: reads.backend.data, have: [] })).toMatchObject({ code: "unknown_cell", retryable: false });
  });

  it("GET posting-check đọc envelope; 404 unknown_cell không thử lại", async () => {
    const seen: { url?: string; init?: RequestInit } = {};
    stubFetch(200, checks.juniorHave, seen);
    const ok = await fetchPostingCheck({ read: reads.backend.data, have: ["java"] });
    expect(ok.kind).toBe("ok");
    expect(seen.url).toContain("/api/v1/posting-check?");
    expect(seen.init?.method ?? "GET").toBe("GET");
    stubFetch(404, { error: { code: "unknown_cell", message: "m", snapshot_date: "2026-11-03" } });
    expect(await fetchPostingCheck({ read: reads.backend.data, have: [] })).toMatchObject({
      kind: "error",
      code: "unknown_cell",
      snapshotDate: "2026-11-03",
      retryable: false,
    });
  });

  it("không có URL thì không gọi mạng", async () => {
    let called = false;
    globalThis.fetch = (async () => {
      called = true;
      return new Response("{}");
    }) as typeof fetch;
    expect(await fetchPostingCheck({ read: reads.notPosting.data, have: [] })).toEqual({ kind: "unreadable" });
    expect(called).toBe(false);
  });
});
