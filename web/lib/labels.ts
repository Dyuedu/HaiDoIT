/**
 * Mã và nhãn tiếng Việt của vai trò và thành phố trên màn Bản đồ.
 *
 * Mã vai trò là `all` cộng các mã trong `roles` của `config/rules.toml`, cùng thứ tự; nhãn là tiếng
 * Việt. `tests/deploy/test_gh162_ban_do_doc_snapshot_that.py` so danh sách này với config mỗi lần chạy
 * pytest. Thêm hay đổi vai trò thì sửa config rồi sửa file này: web không suy nhãn từ mã ở chỗ nào khác.
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

/** Ba thành phố thành thanh, theo thứ tự vẽ. Đà Nẵng luôn có mặt. */
export const BAR_CITIES: readonly string[] = ["ha_noi", "ho_chi_minh", "da_nang"];

/** Hai phần không thành thanh, mỗi phần một dòng chú thích: thành phố khác, không xác định. */
export const LEGEND_CITIES: readonly string[] = ["other", "unknown"];

const ROLE_LABELS: Readonly<Record<string, string>> = Object.fromEntries(
  ROLE_OPTIONS.map((role) => [role.code, role.label]),
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

/** Nhãn của thành phố; mã không có trong file này thì trả chính mã đó. */
export function cityLabel(code: string): string {
  return Object.hasOwn(CITY_LABELS, code) ? CITY_LABELS[code] : code;
}
