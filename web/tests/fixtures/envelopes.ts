import type {
  CellMeta,
  CitySharesEnvelope,
  CoverageNote,
  ShareStat,
  SnapshotStatus,
} from "@/lib/city-shares";

import allJson from "./city-shares-all.json";
import allEntryJson from "./city-shares-all.entry.json";
import backendJson from "./city-shares-backend.json";
import backendEntryJson from "./city-shares-backend.entry.json";
import aiMlJson from "./city-shares-ai_ml.json";
import aiMlEntryJson from "./city-shares-ai_ml.entry.json";

// Sáu file JSON là response thật của API giả (#2), sinh từ `haido_api` qua TestClient:
// `GET /api/v1/city-shares?role=all|ai_ml|backend&level=all|entry` (#163). Tên `city-shares-<role>.json` là mọi cấp,
// `city-shares-<role>.entry.json` là nhóm mới vào nghề. `tests/api/test_ad17_web_fixtures.py` so chúng với API mỗi lần
// chạy pytest, nên API đổi mà quên sinh lại thì CI đỏ.
const FAKE = {
  all: { all: allJson, entry: allEntryJson },
  ai_ml: { all: aiMlJson, entry: aiMlEntryJson },
  backend: { all: backendJson, entry: backendEntryJson },
} as const;

export type FakeRole = keyof typeof FAKE;
export type FakeLevel = "all" | "entry";

/** Envelope y như API giả trả cho vai trò và cấp đó. Mỗi lần gọi là một bản sao mới. */
export function fakeEnvelope(role: FakeRole, level: FakeLevel = "all"): CitySharesEnvelope {
  return structuredClone(FAKE[role][level]) as unknown as CitySharesEnvelope;
}

export interface RowSpec {
  city: string;
  n: number;
  value: number;
  display: ShareStat["display"];
}

export interface EnvelopeSpec {
  role: string;
  /** Cấp bậc lọc; mặc định `all`. Khác `all` thì mã ô có đuôi `.<level>` như API. */
  level?: string;
  /** Mốc số năm (#280); mặc định `any`. Khác `any` thì mã ô có thêm đuôi `.y<N>` như API. */
  years?: string;
  /** Số tin không ghi số năm (#280): `n` của ô `vn.<role>[.<level>].ynone`; chỉ dùng khi `years` khác `any`. */
  yearsUnstated?: number;
  totalN: number;
  rows: RowSpec[];
  snapshotDate?: string;
  snapshotStatus?: SnapshotStatus;
  sources?: string[];
  sourcesFailed?: string[];
  minSample?: number;
  coverageNotes?: CoverageNote[];
}

/** Bốn câu `coverage_notes` mà nguồn `stat` (#69) gửi: ba lưu ý FR-36 cộng câu số nguồn. */
export const STAT_COVERAGE_NOTES: CoverageNote[] = [
  { code: "n_sources", text: "Dữ liệu chỉ gồm tin tuyển dụng IT đăng online trên 7 nguồn." },
  {
    code: "posting_not_demand",
    text: "Tin tuyển dụng không đồng nghĩa với vị trí đang thực sự cần người.",
  },
  { code: "big_city_bias", text: "Dữ liệu nghiêng về thành phố lớn và công ty lớn." },
  {
    code: "salary_disclosed_only",
    text: "Con số lương chỉ phản ánh những tin có công bố lương.",
  },
];

const STAT_SOURCES = ["careerlink", "itnavi", "zalo", "vietnamworks", "topdev", "momo", "itviec"];

/** Mục ô có hình như #69 gửi: `n_by_measure = {}`, `insufficient_by_measure = {}`. */
function statCell(n: number): CellMeta {
  return {
    n,
    fallback_label: null,
    seniority_mix: {},
    n_by_measure: {},
    insufficient_by_measure: {},
  };
}

/** Dựng một envelope hợp đồng từ mô tả gọn. `display` lấy nguyên từ mô tả, không suy từ `n`. */
export function buildEnvelope(spec: EnvelopeSpec): CitySharesEnvelope {
  const level = spec.level ?? "all";
  const years = spec.years ?? "any";
  const suffix = (level === "all" ? "" : `.${level}`) + (years === "any" ? "" : `.y${years}`);
  const totalCellId = `vn.${spec.role}${suffix}`;
  const cells: Record<string, CellMeta> = { [totalCellId]: statCell(spec.totalN) };
  const rows = spec.rows.map((row) => {
    const cellId = `${row.city}.${spec.role}${suffix}`;
    cells[cellId] = statCell(row.n);
    return {
      city: row.city,
      share: {
        value: row.value,
        kind: "composition_share" as const,
        display: row.display,
        cell_id: cellId,
      },
    };
  });
  let unstatedCellId: string | null = null;
  if (years !== "any") {
    unstatedCellId = `vn.${spec.role}${level === "all" ? "" : `.${level}`}.ynone`;
    cells[unstatedCellId] = statCell(spec.yearsUnstated ?? 0);
  }
  return {
    data: {
      role: spec.role,
      level,
      years,
      years_unstated_cell_id: unstatedCellId,
      total_cell_id: totalCellId,
      rows,
    },
    meta: {
      snapshot_date: spec.snapshotDate ?? "2026-11-07",
      snapshot_status: spec.snapshotStatus ?? "published",
      sources: spec.sources ?? STAT_SOURCES,
      sources_failed: spec.sourcesFailed ?? [],
      thresholds: { min_sample: spec.minSample ?? 30, theta_core: 0.3, theta_common: 0.1 },
      coverage_notes: spec.coverageNotes ?? STAT_COVERAGE_NOTES,
      cells,
    },
  };
}

/**
 * Envelope có hình như output của #69: `n_by_measure = {}`, Đà Nẵng `n = 0` với `share = 0`,
 * Khác và không xác định dưới ngưỡng, bốn câu `coverage_notes`.
 */
export function statEnvelope(role = "ai_ml"): CitySharesEnvelope {
  return buildEnvelope({
    role,
    totalN: 80,
    rows: [
      { city: "ha_noi", n: 40, value: 0.5, display: "shown" },
      { city: "ho_chi_minh", n: 35, value: 0.4375, display: "shown" },
      { city: "da_nang", n: 0, value: 0, display: "low_sample_shown" },
      { city: "other", n: 3, value: 0.0375, display: "low_sample_shown" },
      { city: "unknown", n: 2, value: 0.025, display: "low_sample_shown" },
    ],
  });
}

/** Năm dòng đều `low_sample_shown`. */
export function allLowSampleEnvelope(): CitySharesEnvelope {
  return buildEnvelope({
    role: "backend",
    totalN: 20,
    rows: [
      { city: "ha_noi", n: 8, value: 0.4, display: "low_sample_shown" },
      { city: "ho_chi_minh", n: 7, value: 0.35, display: "low_sample_shown" },
      { city: "da_nang", n: 2, value: 0.1, display: "low_sample_shown" },
      { city: "other", n: 1, value: 0.05, display: "low_sample_shown" },
      { city: "unknown", n: 2, value: 0.1, display: "low_sample_shown" },
    ],
  });
}
