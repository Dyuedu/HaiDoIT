/**
 * Màu biểu đồ của phần toàn cảnh (#329). Cấp bậc là một dải xanh lam từ nhạt (Intern) tới đậm (Lead), "chưa ghi cấp"
 * là xám. Hà Nội, TP.HCM, nơi khác là ba màu phân loại đã kiểm trên nền `panel` bằng bộ kiểm bảng màu (dải sáng, độ
 * bão hòa, tách màu với người mù màu, tương phản 3:1). Màu chỉ đi kèm nhãn, không bao giờ là cách duy nhất để phân biệt.
 */

export const LEVEL_COLORS: Readonly<Record<string, string>> = {
  intern: "#c9f2f9",
  fresher: "#96e0ee",
  junior: "#5ec7dc",
  mid: "#2ea6c2",
  senior: "#2386a3",
  lead: "#1c6a84",
  unknown: "#4b5866",
};

export function levelColor(code: string): string {
  return LEVEL_COLORS[code] ?? LEVEL_COLORS.unknown;
}

export const PLACE_COLORS = {
  hn: "#78a32c",
  hcm: "#1d9cc0",
  other: "#cf7434",
} as const;

export const BAR_COLOR = "#c5f36a";
