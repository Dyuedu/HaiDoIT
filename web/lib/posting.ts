/**
 * Hình của tin dán "Soi tin" (#230, US-D1/D2/D3), theo `docs/api/openapi.json`. Hai bước:
 *
 * 1. `POST /api/v1/posting-reads` `{text}`: đọc chữ dán một lần, trả `{data}` (không có `meta`: không có số liệu thị trường).
 *    Chữ dán không được lưu ở đâu cả (AD-11): web không giữ chữ sau khi gửi và không ghi vào `localStorage`.
 * 2. `GET /api/v1/posting-check?role=&level=&have=&skills=&...`: chỉ mã và số (AD-22), trả `{data, meta}` với ba mục:
 *    `match` (có số), `market` (#125, FR-30) và `warnings` (#126, FR-31). Hai mục sau còn `status = not_ready` ở dữ liệu tới #240–#246,
 *    nhưng bộ kiểm ở đây đã nhận cả hình `ready` đã chốt, nên màn không trắng khi API nối số thật.
 *
 * Web không tính mức khớp, không so mã, không sắp xếp lại: máy chủ đã làm (AD-22). Cụm chữ chưa nhận diện (`unrecognised`), trích dẫn
 * phí (`fee_mentions`), trích dẫn liên hệ (`contact_quotes`) và link tin thu thập (`collected.url`) chỉ hiện trên màn, không bao giờ
 * vào URL của bước hai (`postingFactsOf` chỉ lấy mã và số).
 */

import {
  type ErrorEnvelope,
  type Meta,
  type Stat,
  isCount,
  isMeta,
  isNonEmptyString,
  isRecord,
  isStringArray,
  readErrorBody,
} from "./city-shares";
import { isSkillCode } from "./haido-keys";

// ------------------------------------------------------------------------------------------ bước 1

export type PostingReason = "not_posting" | "too_short" | "not_it";
export type ContactChannel = "company_email" | "company_site" | "phone" | "zalo" | "telegram" | "personal_email";
export type SalaryCurrency = "vnd" | "usd";
export type SalaryPeriod = "month" | "year";

export interface PostingSkillMention {
  code: string;
  mentions: number;
}

export interface PostingSalary {
  min: number | null;
  max: number | null;
  currency: SalaryCurrency;
  period: SalaryPeriod;
}

/** Trích dẫn nguyên văn về một kênh liên hệ (#245): chỉ hiện trên màn từ response bước một. */
export interface PostingContactQuote {
  channel: ContactChannel;
  quote: string;
}

/** Tin thu thập khớp (FR-32, #246): bước một đã tra, có link. Bước hai chỉ nhận số lần đăng lại và số snapshot. */
export interface PostingCollected {
  site: string;
  first_seen: string;
  repost_count: number;
  snapshots_seen: number;
  url: string;
}

export interface PostingReadData {
  is_posting: boolean;
  /** `null` khi là tin; khi không: `not_posting`, `too_short` hoặc `not_it` ("Tin này có vẻ không thuộc lĩnh vực IT"). */
  reason: PostingReason | null;
  /** Mã vai trò, nhánh (FR-27) và cấp bậc nhận diện (`null` khi không phải tin). Người dùng đổi vai trò hoặc cấp mà không dán lại. */
  role: string | null;
  branch: string | null;
  level: string | null;
  skills: PostingSkillMention[];
  /** Chữ chưa nhận diện, nguyên văn: chỉ hiện ("không tính vào mức khớp"), không đi vào query. */
  unrecognised: string[];
  years_min: number | null;
  salary: PostingSalary | null;
  /** Tin có nói về lương nhưng không có số ("thỏa thuận"). Không đi cùng `salary`. */
  salary_non_numeric: boolean;
  company_named: boolean;
  duties_described: boolean;
  /** Cấp bậc mà chức danh cho biết (mã, không gồm `unknown`), hoặc `null`. */
  title_level: string | null;
  contacts: ContactChannel[];
  /** Trích dẫn kênh liên hệ (#245): chỉ hiện, không đi vào query. */
  contact_quotes: PostingContactQuote[];
  /** Trích dẫn ngắn về phí hoặc đặt cọc: chỉ hiện, không đi vào query. */
  fee_mentions: string[];
  collected: PostingCollected | null;
  model_id: string;
  prompt_version: string;
  vocab_version: string;
}

export interface PostingReadResponse {
  data: PostingReadData;
}

/** Mã lỗi của đường đọc thật (#231, #232) cùng HTTP của chúng. */
export const POSTING_READ_ERRORS: Readonly<Record<string, number>> = {
  text_too_long: 413,
  rate_limited: 429,
  read_failed: 502,
  read_unavailable: 503,
  read_timeout: 504,
};

/** Lỗi mà thử lại vẫn ra cùng kết quả: chữ quá dài, truy vấn sai hình, hoặc "không có số cho vai trò và cấp này". */
const NOT_RETRYABLE: ReadonlySet<string> = new Set(["text_too_long", "invalid_query", "unknown_cell"]);

const CONTACTS: readonly string[] = ["company_email", "company_site", "phone", "zalo", "telegram", "personal_email"];
const REASONS: readonly string[] = ["not_posting", "too_short", "not_it"];

const MAX_QUOTES = 5;
const MAX_QUOTE_LEN = 120;

export type PostingError = {
  kind: "error";
  code: string;
  message: string;
  snapshotDate: string | null;
  /** `false` với `text_too_long`, `invalid_query`, `unknown_cell`; `check_unavailable` (503, chưa nối số thật) và `read_*` thử lại được. */
  retryable: boolean;
};

export type PostingReadResult = { kind: "ok"; response: PostingReadResponse } | PostingError | { kind: "unreadable" };

function isOptionalCount(value: unknown): boolean {
  return value === null || isCount(value);
}

function isSalary(value: unknown): boolean {
  if (!isRecord(value)) return false;
  const min: unknown = value.min;
  const max: unknown = value.max;
  return (
    isOptionalCount(min) &&
    isOptionalCount(max) &&
    (min !== null || max !== null) &&
    (min === null || max === null || (min as number) <= (max as number)) &&
    (value.currency === "vnd" || value.currency === "usd") &&
    (value.period === "month" || value.period === "year")
  );
}

function isContactQuote(value: unknown, contacts: readonly unknown[]): boolean {
  return (
    isRecord(value) &&
    typeof value.channel === "string" &&
    contacts.includes(value.channel) &&
    typeof value.quote === "string" &&
    value.quote.length > 0 &&
    value.quote.length <= MAX_QUOTE_LEN
  );
}

function isCollected(value: unknown): boolean {
  return (
    isRecord(value) &&
    isNonEmptyString(value.site) &&
    typeof value.first_seen === "string" &&
    /^\d{4}-\d{2}-\d{2}$/.test(value.first_seen) &&
    isCount(value.repost_count) &&
    isCount(value.snapshots_seen) &&
    value.snapshots_seen >= 1 &&
    typeof value.url === "string" &&
    /^https?:\/\/\S+$/.test(value.url) // FR-32: tin khớp thì có link về tin gốc
  );
}

/** Kiểm phần hợp đồng mà màn đọc. Sai một chỗ là cả response không dùng: màn không đoán, không vá. */
export function isPostingReadResponse(body: unknown): body is PostingReadResponse {
  if (!isRecord(body) || !isRecord(body.data) || "meta" in body) return false;
  const d = body.data;
  if (typeof d.is_posting !== "boolean" || typeof d.company_named !== "boolean") return false;
  if (typeof d.duties_described !== "boolean" || typeof d.salary_non_numeric !== "boolean") return false;
  if (!isNonEmptyString(d.model_id) || !isNonEmptyString(d.prompt_version) || !isNonEmptyString(d.vocab_version)) return false;
  if (!Array.isArray(d.skills) || !isStringArray(d.unrecognised) || !isStringArray(d.fee_mentions)) return false;
  if (!Array.isArray(d.contacts) || !d.contacts.every((c) => typeof c === "string" && CONTACTS.includes(c))) return false;
  if (new Set(d.contacts).size !== d.contacts.length) return false;
  if (!Array.isArray(d.contact_quotes) || d.contact_quotes.length > MAX_QUOTES) return false;
  if (!d.contact_quotes.every((q) => isContactQuote(q, d.contacts as unknown[]))) return false;
  if (!isOptionalCount(d.years_min) || (d.salary !== null && !isSalary(d.salary))) return false;
  if (d.branch !== null && !isNonEmptyString(d.branch)) return false;
  if (d.title_level !== null && (!isNonEmptyString(d.title_level) || d.title_level === "unknown")) return false;
  if (d.collected !== null && !isCollected(d.collected)) return false;
  if (d.is_posting !== (d.reason === null)) return false;
  if (!d.is_posting) {
    return (
      typeof d.reason === "string" &&
      REASONS.includes(d.reason) &&
      d.role === null &&
      d.branch === null &&
      d.level === null &&
      d.skills.length === 0 &&
      d.unrecognised.length === 0 &&
      d.years_min === null &&
      d.salary === null &&
      !d.salary_non_numeric &&
      !d.company_named &&
      !d.duties_described &&
      d.title_level === null &&
      d.contacts.length === 0 &&
      d.contact_quotes.length === 0 &&
      d.fee_mentions.length === 0 &&
      d.collected === null
    );
  }
  if (!isNonEmptyString(d.role) || !isNonEmptyString(d.level)) return false;
  if (d.salary_non_numeric && d.salary !== null) return false;
  const codes = new Set<string>();
  for (const skill of d.skills) {
    if (!isRecord(skill) || typeof skill.code !== "string" || !isSkillCode(skill.code) || codes.has(skill.code)) return false;
    if (!isCount(skill.mentions) || skill.mentions < 1) return false;
    codes.add(skill.code);
  }
  return true;
}

export async function fetchPostingRead(options: { text: string; signal?: AbortSignal }): Promise<PostingReadResult> {
  let response: Response;
  let body: unknown;
  try {
    response = await fetch("/api/v1/posting-reads", {
      method: "POST",
      headers: { accept: "application/json", "content-type": "application/json" },
      body: JSON.stringify({ text: options.text }),
      cache: "no-store",
      signal: options.signal,
    });
    body = await response.json();
  } catch {
    return { kind: "unreadable" };
  }
  if (!response.ok) return readError(body);
  return isPostingReadResponse(body) ? { kind: "ok", response: body } : { kind: "unreadable" };
}

function readError(body: unknown): PostingError | { kind: "unreadable" } {
  const error = readErrorBody(body as ErrorEnvelope);
  if (!error) return { kind: "unreadable" };
  return {
    kind: "error",
    code: error.code,
    message: error.message,
    snapshotDate: error.snapshot_date,
    retryable: !NOT_RETRYABLE.has(error.code),
  };
}

// ------------------------------------------------------------------------------------------ bước 2

export type PostingGroup = "core" | "common" | "specific";

export interface PostingSkillLabel {
  code: string;
  name_en: string;
  name_vi: string;
}

export interface PostingMatchedSkill {
  skill: PostingSkillLabel;
  /** `null` khi ô không đủ mẫu để chia nhóm. */
  group: PostingGroup | null;
  /** `skill_rate` của ô đã dùng (`data.cell_id`); `null_data` khi ô không đủ mẫu. */
  rate: Stat;
  /** `null` khi không có hồ sơ. Máy chủ so, web không tự so mã. */
  have: boolean | null;
}

export interface PostingGroupCount {
  group: PostingGroup;
  total: number;
  /** `null` khi không có hồ sơ. */
  had: number | null;
}

export interface PostingMatchLevel {
  points: number;
  max_points: number;
  /** 0 đến 100, làm tròn nửa lên ở máy chủ. */
  percent: number;
}

export interface PostingMatch {
  status: "ready" | "not_enough_data" | "no_skills";
  /** Đã theo thứ tự hiển thị của máy chủ: core, common, specific, rồi tỷ lệ giảm dần. */
  skills: PostingMatchedSkill[];
  /** Đủ ba dòng khi `ready`, rỗng nếu không. */
  groups: PostingGroupCount[];
  /** `null` khi không có hồ sơ hoặc `status` khác `ready`. */
  level: PostingMatchLevel | null;
  /** Mã kỹ năng nên đặt đầu CV (hồ sơ có và tin nêu). */
  cv_first: string[];
  config_version: string;
}

/** Vị trí của tin theo số năm hoặc số kỹ năng so với ô (#125, FR-30). X/30 của "chưa đủ dữ liệu" tra ở `meta.cells[market.cell_id].n_by_measure`. */
export interface PostingPercentile {
  state: "compared" | "not_enough_data" | "not_stated";
  /** `percentile` 0–100; `null_data` khi `not_enough_data`; `null` khi `not_stated`. */
  percentile: Stat | null;
  /** Khoảng tin cậy 95% khi 30 ≤ n < 100 (AD-26); đi cặp. */
  ci_low: Stat | null;
  ci_high: Stat | null;
}

/** Tỷ giá đã dùng để đổi USD sang VND (AD-10): số VND cho một USD, kèm phiên bản của snapshot. */
export interface PostingFxRate {
  rate: number;
  unit: "vnd_per_usd";
  fx_version: string;
}

/** Lương của tin sau khi quy về VND một tháng gross. */
export interface PostingSalaryConversion {
  min_vnd_month: number | null;
  max_vnd_month: number | null;
  /** `null` khi tin đã ghi bằng VND. */
  fx: PostingFxRate | null;
}

export interface PostingSalaryComparison {
  /** `not_stated`: tin không công bố lương (sự thật trung tính, `note`). `not_numeric`: có nói về lương nhưng không có số. */
  state: "compared" | "not_enough_data" | "not_stated" | "not_numeric";
  position: "below" | "within" | "above" | null;
  /** P25 và P75 của lương trong ô, VND một tháng. */
  low: Stat | null;
  high: Stat | null;
  converted: PostingSalaryConversion | null;
  note: "salary_not_stated" | null;
}

/** Mục chưa làm là `not_ready`, không phải số 0. */
export interface PostingMarketNotReady {
  status: "not_ready";
  cell_id: null;
  years: null;
  skill_count: null;
  salary: null;
  note: null;
}

export interface PostingMarketReady {
  status: "ready";
  /** Ô của ba so sánh; có thể khác `data.cell_id` của `match`. */
  cell_id: string;
  years: PostingPercentile;
  skill_count: PostingPercentile;
  salary: PostingSalaryComparison;
  /** Mã câu "so sánh, không phải phán quyết về tin" (#125 AC5, #242); chữ do màn dựng. */
  note: "comparisons_not_verdict";
}

export type PostingMarket = PostingMarketNotReady | PostingMarketReady;

export const POSTING_SIGN_CODES = [
  "d1_wide_skills",
  "d2_specific_heavy",
  "d3_high_req_low_pay",
  "d4_reposted",
  "d5_unusual_contact",
  "d6_fee_first",
  "d7_no_company",
] as const;
export type PostingSignCode = (typeof POSTING_SIGN_CODES)[number];

export const POSTING_CHECKLIST_CODES = ["company_named", "salary_stated", "duties_described", "title_matches_level"] as const;

export type PostingSignFact =
  | { kind: "d1_wide_skills"; skill_count: number; p90: Stat }
  | { kind: "d2_specific_heavy"; recognised_count: number; specific_count: number }
  | { kind: "d3_high_req_low_pay"; skill_count: number; p75_skill_count: Stat; salary_ceiling_vnd_month: number; p25_salary: Stat }
  | { kind: "d4_reposted"; reposts: number; snapshots_seen: number }
  | { kind: "d5_unusual_contact"; channels: ContactChannel[] }
  | { kind: "d6_fee_first"; quote_count: number }
  | { kind: "d7_no_company" };

export interface PostingSign {
  code: PostingSignCode;
  status: "triggered" | "not_triggered" | "not_evaluable";
  /** Chỉ có khi `not_evaluable`: `not_in_data` (D4: tin chưa có trong dữ liệu), `not_enough_data`, `no_numeric_salary`. */
  reason: "not_in_data" | "not_enough_data" | "no_numeric_salary" | null;
  /** Dữ kiện đã kích hoạt, chỉ có khi `triggered`. */
  fact: PostingSignFact | null;
  /** Mã câu gợi ý hành động, chỉ có khi `triggered`. */
  action: string | null;
  /** Trường của bước một mà màn trích nguyên văn: D5 `contacts` (lọc `contact_quotes` theo `fact.channels`), D6 `fee_mentions`. */
  source_field: "fee_mentions" | "contacts" | null;
}

export interface PostingChecklistItem {
  code: (typeof POSTING_CHECKLIST_CODES)[number];
  /** `null` là không biết (ví dụ chức danh không cho biết cấp), khác với `false`. */
  present: boolean | null;
}

/** Vòng đời của tin thu thập khớp; site, ngày thấy đầu và link ở `PostingReadData.collected`. */
export interface PostingCollectedCounts {
  repost_count: number;
  snapshots_seen: number;
}

/**
 * `not_ready`: `checklist` và `signs` rỗng, mọi trường còn lại `null`. `ready`: đủ bốn mục checklist, đủ bảy dấu hiệu D1–D7 theo thứ tự,
 * `disclaimer = "signs_are_hints"` (mã câu cố định của FR-31).
 */
export interface PostingWarnings {
  status: "not_ready" | "ready";
  checklist: PostingChecklistItem[];
  signs: PostingSign[];
  /** `null` là không khớp tin đã thu thập: D4 không đánh giá được. */
  collected_match: PostingCollectedCounts | null;
  /** `salary_not_stated`: dòng trung tính khi tin không ghi lương, không phải cảnh báo. */
  salary_note: "salary_not_stated" | null;
  disclaimer: "signs_are_hints" | null;
}

export interface PostingCheckData {
  role: string;
  /** Nhánh đã gửi lên, lặp lại nguyên mã. */
  branch: string | null;
  level: string;
  /** Ô đã dùng cho `match`, sau khi quay về; nhãn ở `meta.cells[cell_id].fallback_label`. */
  cell_id: string;
  has_profile: boolean;
  match: PostingMatch;
  market: PostingMarket;
  warnings: PostingWarnings;
}

export interface PostingCheckEnvelope {
  data: PostingCheckData;
  meta: Meta;
}

export type PostingCheckResult = { kind: "ok"; envelope: PostingCheckEnvelope } | PostingError | { kind: "unreadable" };

/** Sự kiện đóng của bước một mà bước hai nhận. Chỉ mã và số: không có chữ chưa nhận diện, trích dẫn, link hay tên nguồn. */
export interface PostingFacts {
  branch: string | null;
  yearsMin: number | null;
  salary: PostingSalary | null;
  salaryNonNumeric: boolean;
  companyNamed: boolean;
  contacts: ContactChannel[];
  /** Số trích dẫn phí, không phải chính chữ. */
  fees: number;
  dutiesDescribed: boolean;
  titleLevel: string | null;
  /** Số lần đăng lại và số snapshot của tin thu thập khớp; `null` khi không khớp. */
  collectedReposts: number | null;
  collectedSnapshots: number | null;
}

export function postingFactsOf(read: PostingReadData): PostingFacts {
  return {
    branch: read.branch,
    yearsMin: read.years_min,
    salary: read.salary,
    salaryNonNumeric: read.salary_non_numeric,
    companyNamed: read.company_named,
    contacts: read.contacts,
    fees: read.fee_mentions.length,
    dutiesDescribed: read.duties_described,
    titleLevel: read.title_level,
    collectedReposts: read.collected?.repost_count ?? null,
    collectedSnapshots: read.collected?.snapshots_seen ?? null,
  };
}

export interface PostingCheckOptions {
  /** Kết quả bước một. Dùng lại khi đổi vai trò hoặc cấp: không dán lại. */
  read: PostingReadData;
  /** Hồ sơ (AD-22), rỗng là không có hồ sơ. */
  have: readonly string[];
  /** Ghi đè vai trò hoặc cấp nhận diện được. Đổi vai trò thì bỏ nhánh (nhánh thuộc vai trò); đổi cấp thì giữ. */
  role?: string;
  level?: string;
  signal?: AbortSignal;
}

/**
 * URL của bước hai, hoặc `null` khi chữ dán không phải tin (không có gì để khớp). Chỉ mã kỹ năng, mã vai trò, mã nhánh, mã cấp và số.
 */
export function postingCheckUrl(options: Pick<PostingCheckOptions, "read" | "have" | "role" | "level">): string | null {
  const { read } = options;
  const role = options.role ?? read.role;
  const level = options.level ?? read.level;
  if (!read.is_posting || role === null || level === null) return null;
  const facts = postingFactsOf(read);
  const params = new URLSearchParams({ role, level });
  if (facts.branch !== null && role === read.role) params.set("branch", facts.branch);
  if (options.have.length > 0) params.set("have", options.have.join(","));
  if (read.skills.length > 0) params.set("skills", read.skills.map((s) => s.code).join(","));
  if (facts.yearsMin !== null) params.set("years_min", String(facts.yearsMin));
  if (facts.salary !== null) {
    if (facts.salary.min !== null) params.set("salary_min", String(facts.salary.min));
    if (facts.salary.max !== null) params.set("salary_max", String(facts.salary.max));
    params.set("salary_currency", facts.salary.currency);
    params.set("salary_period", facts.salary.period);
  }
  if (facts.salaryNonNumeric) params.set("salary_non_numeric", "true");
  params.set("company_named", String(facts.companyNamed));
  if (facts.contacts.length > 0) params.set("contacts", facts.contacts.join(","));
  if (facts.fees > 0) params.set("fees", String(facts.fees));
  params.set("duties_described", String(facts.dutiesDescribed));
  if (facts.titleLevel !== null) params.set("title_level", facts.titleLevel);
  if (facts.collectedReposts !== null && facts.collectedSnapshots !== null) {
    params.set("collected_reposts", String(facts.collectedReposts));
    params.set("collected_snapshots", String(facts.collectedSnapshots));
  }
  return `/api/v1/posting-check?${params.toString()}`;
}

/** Gọi bước hai. Không ném lỗi: trả dữ liệu, lỗi chuẩn của API, hoặc "không đọc được". */
export async function fetchPostingCheck(options: PostingCheckOptions): Promise<PostingCheckResult> {
  const url = postingCheckUrl(options);
  if (url === null) return { kind: "unreadable" };
  let response: Response;
  let body: unknown;
  try {
    response = await fetch(url, { headers: { accept: "application/json" }, cache: "no-store", signal: options.signal });
    body = await response.json();
  } catch {
    return { kind: "unreadable" };
  }
  if (!response.ok) return readError(body);
  return isPostingCheckEnvelope(body) ? { kind: "ok", envelope: body } : { kind: "unreadable" };
}

// ------------------------------------------------------------------------------------------ bộ kiểm hợp đồng

function isHiddenOrShownRate(rate: unknown, cellId: string): boolean {
  if (!isRecord(rate) || rate.kind !== "skill_rate" || rate.cell_id !== cellId) return false;
  if (rate.display === "shown") return typeof rate.value === "number" && rate.value >= 0 && rate.value <= 1;
  return rate.display === "null_data" && rate.value === null;
}

/** `Stat` kind `percentile` của ô `cellId`: hiện số (0 đến `upper`, hoặc không trần) hoặc `null_data`. */
function isPercentileStat(stat: unknown, cellId: string, shown: boolean, upper: number | null = null): stat is Stat {
  if (!isRecord(stat) || stat.kind !== "percentile" || stat.cell_id !== cellId) return false;
  if (!shown) return stat.display === "null_data" && stat.value === null;
  return (
    stat.display === "shown" &&
    typeof stat.value === "number" &&
    Number.isFinite(stat.value) &&
    stat.value >= 0 &&
    (upper === null || stat.value <= upper)
  );
}

function isPercentilePart(part: unknown, cellId: string, allowNotStated: boolean): boolean {
  if (!isRecord(part)) return false;
  const { state, percentile, ci_low: low, ci_high: high } = part;
  if (state === "compared") {
    if (!isPercentileStat(percentile, cellId, true, 100)) return false;
    if (low === null && high === null) return true;
    return (
      isPercentileStat(low, cellId, true, 100) &&
      isPercentileStat(high, cellId, true, 100) &&
      (low.value as number) <= (percentile.value as number) &&
      (percentile.value as number) <= (high.value as number)
    );
  }
  if (state === "not_enough_data") return isPercentileStat(percentile, cellId, false) && low === null && high === null;
  return allowNotStated && state === "not_stated" && percentile === null && low === null && high === null;
}

function isConversion(value: unknown): boolean {
  if (!isRecord(value)) return false;
  const { min_vnd_month: min, max_vnd_month: max, fx } = value;
  if (!isOptionalCount(min) || !isOptionalCount(max) || (min === null && max === null)) return false;
  if (min !== null && max !== null && (min as number) > (max as number)) return false;
  if (fx === null) return true;
  return isRecord(fx) && isCount(fx.rate) && fx.rate >= 1 && fx.unit === "vnd_per_usd" && isNonEmptyString(fx.fx_version);
}

function isSalaryPart(salary: unknown, cellId: string): boolean {
  if (!isRecord(salary)) return false;
  const { state, position, low, high, converted, note } = salary;
  if (state === "compared" || state === "not_enough_data") {
    if (!isConversion(converted) || note !== null) return false;
    if (state === "not_enough_data") return position === null && isPercentileStat(low, cellId, false) && isPercentileStat(high, cellId, false);
    return (
      (position === "below" || position === "within" || position === "above") &&
      isPercentileStat(low, cellId, true) &&
      isPercentileStat(high, cellId, true) &&
      (low.value as number) <= (high.value as number)
    );
  }
  if (position !== null || low !== null || high !== null || converted !== null) return false;
  if (state === "not_stated") return note === "salary_not_stated";
  return state === "not_numeric" && note === null;
}

function isNotReadyMarket(market: Record<string, unknown>): boolean {
  return market.cell_id === null && market.years === null && market.skill_count === null && market.salary === null && market.note === null;
}

function isMarket(market: unknown, meta: Meta): boolean {
  if (!isRecord(market)) return false;
  if (market.status === "not_ready") return isNotReadyMarket(market);
  if (market.status !== "ready" || market.note !== "comparisons_not_verdict") return false;
  const cellId = market.cell_id;
  if (!isNonEmptyString(cellId) || !Object.hasOwn(meta.cells, cellId) || !isRecord(meta.cells[cellId])) return false;
  return (
    isPercentilePart(market.years, cellId, true) && isPercentilePart(market.skill_count, cellId, false) && isSalaryPart(market.salary, cellId)
  );
}

const PERSONAL_CHANNELS: readonly string[] = ["zalo", "telegram", "personal_email"];

function isFact(fact: Record<string, unknown>, code: string): boolean {
  if (fact.kind !== code) return false;
  const cell = (stat: unknown): boolean => isRecord(stat) && isNonEmptyString(stat.cell_id) && isPercentileStat(stat, stat.cell_id, true);
  switch (code) {
    case "d1_wide_skills":
      return isCount(fact.skill_count) && cell(fact.p90);
    case "d2_specific_heavy":
      return isCount(fact.recognised_count) && isCount(fact.specific_count) && fact.specific_count <= fact.recognised_count;
    case "d3_high_req_low_pay":
      return isCount(fact.skill_count) && isCount(fact.salary_ceiling_vnd_month) && cell(fact.p75_skill_count) && cell(fact.p25_salary);
    case "d4_reposted":
      return isCount(fact.reposts) && isCount(fact.snapshots_seen);
    case "d5_unusual_contact":
      return (
        Array.isArray(fact.channels) &&
        fact.channels.length > 0 &&
        new Set(fact.channels).size === fact.channels.length &&
        fact.channels.every((c) => typeof c === "string" && PERSONAL_CHANNELS.includes(c))
      );
    case "d6_fee_first":
      return isCount(fact.quote_count) && fact.quote_count >= 1 && fact.quote_count <= MAX_QUOTES;
    default:
      return code === "d7_no_company"; // trường lạ được bỏ qua: tương thích tiến
  }
}

const NOT_EVALUABLE: Readonly<Record<string, readonly string[]>> = {
  d1_wide_skills: ["not_enough_data"],
  d2_specific_heavy: ["not_enough_data"],
  d3_high_req_low_pay: ["not_enough_data", "no_numeric_salary"],
  d4_reposted: ["not_in_data"],
};
const SOURCE_FIELD: Readonly<Record<string, string | null>> = { d5_unusual_contact: "contacts", d6_fee_first: "fee_mentions" };

function isSign(sign: unknown, code: string): boolean {
  if (!isRecord(sign) || sign.code !== code) return false;
  const source = SOURCE_FIELD[code] ?? null;
  if (sign.status === "triggered") {
    return isRecord(sign.fact) && isFact(sign.fact, code) && isNonEmptyString(sign.action) && sign.reason === null && sign.source_field === source;
  }
  if (sign.fact !== null || sign.action !== null || sign.source_field !== null) return false;
  if (sign.status === "not_triggered") return sign.reason === null;
  return sign.status === "not_evaluable" && typeof sign.reason === "string" && (NOT_EVALUABLE[code] ?? []).includes(sign.reason);
}

function isWarnings(warnings: unknown): boolean {
  if (!isRecord(warnings) || !Array.isArray(warnings.checklist) || !Array.isArray(warnings.signs)) return false;
  if (warnings.status === "not_ready") {
    return (
      warnings.checklist.length === 0 &&
      warnings.signs.length === 0 &&
      warnings.collected_match === null &&
      warnings.salary_note === null &&
      warnings.disclaimer === null
    );
  }
  if (warnings.status !== "ready" || warnings.disclaimer !== "signs_are_hints") return false;
  if (warnings.salary_note !== null && warnings.salary_note !== "salary_not_stated") return false;
  if (warnings.checklist.length !== POSTING_CHECKLIST_CODES.length) return false;
  const checklistOk = POSTING_CHECKLIST_CODES.every((code, i) => {
    const item: unknown = (warnings.checklist as unknown[])[i];
    return isRecord(item) && item.code === code && (item.present === null || typeof item.present === "boolean");
  });
  if (!checklistOk || warnings.signs.length !== POSTING_SIGN_CODES.length) return false;
  if (!POSTING_SIGN_CODES.every((code, i) => isSign((warnings.signs as unknown[])[i], code))) return false;
  const d4 = (warnings.signs as Record<string, unknown>[])[3];
  const collected = warnings.collected_match;
  if (collected === null) return d4.status === "not_evaluable";
  if (!isRecord(collected) || !isCount(collected.repost_count) || !isCount(collected.snapshots_seen) || d4.status === "not_evaluable") return false;
  const fact = d4.fact;
  return !isRecord(fact) || (fact.reposts === collected.repost_count && fact.snapshots_seen === collected.snapshots_seen);
}

/**
 * Kiểm phần hợp đồng của bước hai mà màn đọc, gồm cả hình `ready` của `market` và `warnings` đã chốt trong schema: màn không trắng khi
 * #240 và #244 nối số thật. Web chỉ kiểm hình và tính nhất quán của chính response; không tính lại trạng thái từ cỡ mẫu (máy chủ làm).
 */
export function isPostingCheckEnvelope(body: unknown): body is PostingCheckEnvelope {
  if (!isRecord(body) || !isRecord(body.data) || !isMeta(body.meta)) return false;
  const { data, meta } = body;
  if (!isNonEmptyString(data.role) || !isNonEmptyString(data.level) || typeof data.has_profile !== "boolean") return false;
  if (data.branch !== null && !isNonEmptyString(data.branch)) return false;
  const cellId = data.cell_id;
  if (!isNonEmptyString(cellId) || !Object.hasOwn(meta.cells, cellId) || !isRecord(meta.cells[cellId])) return false;
  if (!isCount(meta.cells[cellId].n)) return false;
  if (!isMarket(data.market, meta) || !isWarnings(data.warnings)) return false;
  const match = data.match;
  if (!isRecord(match) || !isNonEmptyString(match.config_version) || !isStringArray(match.cv_first)) return false;
  if (match.status !== "ready" && match.status !== "not_enough_data" && match.status !== "no_skills") return false;
  if (!Array.isArray(match.skills) || !Array.isArray(match.groups)) return false;
  const codes = new Set<string>();
  for (const row of match.skills) {
    if (!isRecord(row) || !isRecord(row.skill) || typeof row.skill.code !== "string" || !isSkillCode(row.skill.code)) return false;
    if (codes.has(row.skill.code) || !isNonEmptyString(row.skill.name_en) || !isNonEmptyString(row.skill.name_vi)) return false;
    codes.add(row.skill.code);
    if (row.group !== null && row.group !== "core" && row.group !== "common" && row.group !== "specific") return false;
    if (row.have !== null && typeof row.have !== "boolean") return false;
    if ((row.have !== null) !== data.has_profile) return false;
    if ((row.group === null) !== (isRecord(row.rate) && row.rate.display === "null_data")) return false;
    if (!isHiddenOrShownRate(row.rate, cellId)) return false;
  }
  if (!match.cv_first.every((code) => codes.has(code))) return false;
  if (match.status === "ready" ? match.groups.length !== 3 : match.groups.length !== 0) return false;
  for (const g of match.groups) {
    if (!isRecord(g) || !isCount(g.total) || !(g.had === null ? !data.has_profile : isCount(g.had) && g.had <= g.total)) return false;
  }
  const level = match.level;
  if (level === null) return match.status !== "ready" || !data.has_profile;
  if (match.status !== "ready" || !data.has_profile || !isRecord(level)) return false;
  return (
    isCount(level.points) &&
    isCount(level.max_points) &&
    isCount(level.percent) &&
    level.max_points >= 1 &&
    level.points <= level.max_points &&
    level.percent <= 100
  );
}
