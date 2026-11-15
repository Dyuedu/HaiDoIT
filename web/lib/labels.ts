/**
 * Mã và nhãn tiếng Việt của vai trò và thành phố trên màn Bản đồ.
 *
 * Mã vai trò là `all` cộng các mã trong `roles` của `config/rules.toml`, cùng thứ tự; nhãn là tiếng
 * Việt. `tests/deploy/test_gh162_ban_do_doc_snapshot_that.py` so danh sách này với config mỗi lần chạy
 * pytest. Thêm hay đổi vai trò thì sửa config rồi sửa file này: web không suy nhãn từ mã ở chỗ nào khác.
 *
 * Cấp bậc lọc (#163, #134) theo cùng cách: `LEVEL_OPTIONS` là `level_options` của `config/rules.toml` cộng `all` ở
 * cuối; `tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` so với config.
 *
 * Mốc số năm kinh nghiệm (#280): `YEARS_OPTIONS` là `any` ở đầu cộng `years_options` của `config/rules.toml`;
 * `tests/deploy/test_gh280_bo_loc_so_nam_khop_config.py` so với config.
 */

export interface RoleOption {
  code: string;
  label: string;
}

/** Lựa chọn của ô Vai trò, theo thứ tự hiện trên màn. */
export const ROLE_OPTIONS: readonly RoleOption[] = [
  { code: "all", label: "Tất cả" },
  { code: "embedded", label: "Nhúng" },
  { code: "ai_ml", label: "AI/ML" },
  { code: "data_scientist", label: "Khoa học dữ liệu" },
  { code: "data_engineer", label: "Kỹ sư dữ liệu" },
  { code: "data_analyst", label: "Phân tích dữ liệu" },
  { code: "qa", label: "Kiểm thử (QA)" },
  { code: "devops", label: "DevOps" },
  { code: "security", label: "Bảo mật" },
  { code: "it_infra", label: "Hạ tầng & IT support" },
  { code: "mobile", label: "Mobile" },
  { code: "frontend", label: "Frontend" },
  { code: "backend", label: "Backend" },
  { code: "fullstack", label: "Fullstack" },
  { code: "ba_po_pm", label: "BA / PO / PM" },
  { code: "ui_ux", label: "UI/UX" },
  { code: "game", label: "Phát triển game" },
  { code: "other", label: "Vai trò khác" },
];

/** Vai trò khi mở trang. */
export const DEFAULT_ROLE = "all";

export interface LevelOption {
  code: string;
  label: string;
}

/**
 * Lựa chọn của ô Cấp bậc, theo thứ tự của #134: nhóm mới vào nghề, từng cấp, chưa ghi cấp bậc, rồi mọi cấp. `entry` là
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

/**
 * Dòng chú thích dưới ô Cấp bậc, liệt kê các cấp trong nhóm `entry`.
 * `tests/deploy/test_gh163_bo_loc_cap_bac_khop_config.py` so chữ này với `[level_groups]` của `config/rules.toml`.
 */
export const LEVEL_ENTRY_NOTE = "Mới vào nghề gồm Intern, Fresher và Junior.";

/** Cấp bậc khi mở trang: nhóm mới vào nghề (#134). Mọi màn nói "mới vào nghề" dùng cùng nhóm này. */
export const DEFAULT_LEVEL = "entry";

export interface YearsOption {
  code: string;
  label: string;
}

/**
 * Lựa chọn của ô Số năm kinh nghiệm (#280): mọi số năm, rồi từng mốc "tối đa N năm". Mốc `N` chỉ đếm tin yêu cầu tối thiểu không
 * quá N năm; tin không ghi số năm chỉ nằm trong "Mọi số năm".
 */
export const YEARS_OPTIONS: readonly YearsOption[] = [
  { code: "any", label: "Mọi số năm" },
  { code: "0", label: "Không cần kinh nghiệm" },
  { code: "1", label: "Tối đa 1 năm" },
  { code: "2", label: "Tối đa 2 năm" },
  { code: "3", label: "Tối đa 3 năm" },
  { code: "5", label: "Tối đa 5 năm" },
];

/** Số năm khi mở trang: không lọc. */
export const DEFAULT_YEARS = "any";

/** Ba thành phố thành thanh, theo thứ tự vẽ. Đà Nẵng luôn có mặt. */
export const BAR_CITIES: readonly string[] = ["ha_noi", "ho_chi_minh", "da_nang"];

/**
 * Ba phần không thành thanh, mỗi phần một dòng chú thích (#285): làm từ xa, nước ngoài, không xác định. Các tỉnh còn lại
 * (34 tỉnh, thành sau 1/7/2025) không thành thanh; chúng nằm trong bảng, nơi nhiều tin đứng trước.
 */
export const LEGEND_CITIES: readonly string[] = ["remote", "abroad", "unknown"];

const ROLE_LABELS: Readonly<Record<string, string>> = Object.fromEntries(
  ROLE_OPTIONS.map((role) => [role.code, role.label]),
);

const LEVEL_LABELS: Readonly<Record<string, string>> = Object.fromEntries(
  LEVEL_OPTIONS.map((level) => [level.code, level.label]),
);

const YEARS_LABELS: Readonly<Record<string, string>> = Object.fromEntries(
  YEARS_OPTIONS.map((years) => [years.code, years.label]),
);

/**
 * Nhãn nơi làm việc. Nhãn của 34 tỉnh, thành trùng nhãn trong `[labels.city]` của `config/rules.toml`;
 * `tests/deploy/test_gh285_noi_khop_config.py` so hai nơi. `other` ("Khác") chỉ còn cho snapshot tính trước #285.
 */
const CITY_LABELS: Readonly<Record<string, string>> = {
  ha_noi: "Hà Nội",
  ho_chi_minh: "TP.HCM",
  da_nang: "Đà Nẵng",
  hai_phong: "Hải Phòng",
  quang_ninh: "Quảng Ninh",
  bac_ninh: "Bắc Ninh",
  hung_yen: "Hưng Yên",
  ninh_binh: "Ninh Bình",
  phu_tho: "Phú Thọ",
  thai_nguyen: "Thái Nguyên",
  tuyen_quang: "Tuyên Quang",
  lao_cai: "Lào Cai",
  cao_bang: "Cao Bằng",
  lang_son: "Lạng Sơn",
  lai_chau: "Lai Châu",
  dien_bien: "Điện Biên",
  son_la: "Sơn La",
  thanh_hoa: "Thanh Hóa",
  nghe_an: "Nghệ An",
  ha_tinh: "Hà Tĩnh",
  quang_tri: "Quảng Trị",
  hue: "Huế",
  quang_ngai: "Quảng Ngãi",
  gia_lai: "Gia Lai",
  dak_lak: "Đắk Lắk",
  khanh_hoa: "Khánh Hòa",
  lam_dong: "Lâm Đồng",
  dong_nai: "Đồng Nai",
  tay_ninh: "Tây Ninh",
  can_tho: "Cần Thơ",
  vinh_long: "Vĩnh Long",
  dong_thap: "Đồng Tháp",
  an_giang: "An Giang",
  ca_mau: "Cà Mau",
  remote: "Làm từ xa (Remote)",
  abroad: "Nước ngoài",
  unknown: "Không xác định nơi làm việc",
  other: "Khác",
};

/** Nhãn của vai trò; mã không có trong file này thì trả chính mã đó. */
export function roleLabel(code: string): string {
  return Object.hasOwn(ROLE_LABELS, code) ? ROLE_LABELS[code] : code;
}

/** Nhãn của cấp bậc; mã không có trong file này thì trả chính mã đó. */
export function levelLabel(code: string): string {
  return Object.hasOwn(LEVEL_LABELS, code) ? LEVEL_LABELS[code] : code;
}

/** Nhãn của mốc số năm; mã không có trong file này thì trả chính mã đó. */
export function yearsLabel(code: string): string {
  return Object.hasOwn(YEARS_LABELS, code) ? YEARS_LABELS[code] : code;
}

/** Nhãn của thành phố; mã không có trong file này thì trả chính mã đó. */
export function cityLabel(code: string): string {
  return Object.hasOwn(CITY_LABELS, code) ? CITY_LABELS[code] : code;
}
