/**
 * Mã và nhãn tiếng Việt của vai trò và thành phố trên màn Bản đồ.
 *
 * Mã vai trò là `all` cộng các mã trong `roles` của `config/rules.toml`, cùng thứ tự; nhãn là tiếng
 * Việt. `tests/deploy/test_gh162_ban_do_doc_snapshot_that.py` so danh sách này với config mỗi lần chạy
 * pytest. Thêm hay đổi vai trò thì sửa config rồi sửa file này: web không suy nhãn từ mã ở chỗ nào khác.
 *
 * Cấp bậc lọc (#163, #134) theo cùng cách: `LEVEL_OPTIONS` là `level_options` của `config/rules.toml` cộng `all` ở
 * cuối; `tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` so với config.
 */

export interface RoleOption {
  code: string;
  label: string;
}

/** Chip vai trò, theo thứ tự hiện trên màn. */
export const ROLE_OPTIONS: readonly RoleOption[] = [
  { code: "all", label: "Tất cả" },
  { code: "embedded", label: "Nhúng" },
  { code: "ai_ml", label: "AI/ML" },
  { code: "data_engineer", label: "Kỹ sư dữ liệu" },
  { code: "data_analyst", label: "Phân tích dữ liệu" },
  { code: "qa", label: "Kiểm thử (QA)" },
  { code: "devops", label: "DevOps" },
  { code: "mobile", label: "Mobile" },
  { code: "frontend", label: "Frontend" },
  { code: "backend", label: "Backend" },
  { code: "other", label: "Vai trò khác" },
];

/** Vai trò khi mở trang. */
export const DEFAULT_ROLE = "all";

export interface LevelOption {
  code: string;
  label: string;
}

/**
 * Nút cấp bậc, theo thứ tự của #134: nhóm mới vào nghề, từng cấp, chưa ghi cấp bậc, rồi mọi cấp. `entry` là
 * Intern, Fresher, Junior gộp một và không gồm `unknown`.
 */
export const LEVEL_OPTIONS: readonly LevelOption[] = [
  { code: "entry", label: "Mới vào nghề" },
  { code: "intern", label: "Intern" },
  { code: "fresher", label: "Fresher" },
  { code: "junior", label: "Junior" },
  { code: "mid", label: "Mid" },
  { code: "senior", label: "Senior" },
  { code: "lead", label: "Lead" },
  { code: "unknown", label: "Chưa ghi cấp bậc" },
  { code: "all", label: "Mọi cấp bậc" },
];

/** Cấp bậc khi mở trang: nhóm mới vào nghề (#134). Mọi màn nói "mới vào nghề" dùng cùng nhóm này. */
export const DEFAULT_LEVEL = "entry";

/** Ba thành phố thành thanh, theo thứ tự vẽ. Đà Nẵng luôn có mặt. */
export const BAR_CITIES: readonly string[] = ["ha_noi", "ho_chi_minh", "da_nang"];

/** Hai phần không thành thanh, mỗi phần một dòng chú thích: thành phố khác, không xác định. */
export const LEGEND_CITIES: readonly string[] = ["other", "unknown"];

const ROLE_LABELS: Readonly<Record<string, string>> = Object.fromEntries(
  ROLE_OPTIONS.map((role) => [role.code, role.label]),
);

const LEVEL_LABELS: Readonly<Record<string, string>> = Object.fromEntries(
  LEVEL_OPTIONS.map((level) => [level.code, level.label]),
);

const CITY_LABELS: Readonly<Record<string, string>> = {
  ha_noi: "Hà Nội",
  ho_chi_minh: "TP.HCM",
  da_nang: "Đà Nẵng",
  other: "Khác",
  unknown: "Không xác định thành phố",
};

/** Nhãn của vai trò; mã không có trong file này thì trả chính mã đó. */
export function roleLabel(code: string): string {
  return Object.hasOwn(ROLE_LABELS, code) ? ROLE_LABELS[code] : code;
}

/** Nhãn của cấp bậc; mã không có trong file này thì trả chính mã đó. */
export function levelLabel(code: string): string {
  return Object.hasOwn(LEVEL_LABELS, code) ? LEVEL_LABELS[code] : code;
}

/** Nhãn của thành phố; mã không có trong file này thì trả chính mã đó. */
export function cityLabel(code: string): string {
  return Object.hasOwn(CITY_LABELS, code) ? CITY_LABELS[code] : code;
}
