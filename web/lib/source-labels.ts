/**
 * Tên hiển thị của nguồn tin (#324): viết như chính trang đó viết tên mình, không theo mã của `meta.sources`.
 * Mã chưa có ở đây thì in nguyên mã, để nguồn mới vẫn hiện ra thay vì biến mất.
 */
const SOURCE_LABELS: Readonly<Record<string, string>> = {
  careerlink: "CareerLink",
  itnavi: "ITnavi",
  itviec: "ITviec",
  momo: "MoMo Careers",
  topcv: "TopCV",
  topdev: "TopDev",
  vietnamworks: "VietnamWorks",
  zalo: "Zalo Careers",
};

export function sourceLabel(code: string): string {
  return SOURCE_LABELS[code] ?? code;
}

/** Danh sách nguồn thành một dòng: "CareerLink, ITnavi, …". */
export function sourcesText(codes: readonly string[]): string {
  return codes.map(sourceLabel).join(", ");
}
