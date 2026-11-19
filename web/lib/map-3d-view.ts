/**
 * Cột của bản đồ 3D (#314, #316), dựng từ đúng các dòng mà lối Biểu đồ 2D vẽ (`view.bars` của `buildCitySharesView`).
 *
 * Không tính số mới (AD-22): chiều cao là `share.value × 400` px, như `p × 4` của prototype màn 01, không chuẩn hóa theo
 * cột cao nhất, nên một chiều cao chỉ mang một nghĩa (FR-33). Cột mẫu nhỏ vẫn cao theo tỷ trọng thật, chỉ mờ đi. Chữ
 * trên thẻ lấy nguyên các chuỗi đã định dạng của view.
 */

import type { CitySharesView } from "./city-shares-view";
import { CITY_POINTS, toStage } from "./vietnam-geo";

/** Chiều cao (px trên sân khấu) của cột có tỷ trọng 100%. */
export const COLUMN_MAX_HEIGHT = 400;

export interface MapColumn {
  city: string;
  label: string;
  /** Vị trí trên sân khấu 460×560. */
  stage: { px: number; py: number };
  height: number;
  /** `share.display = low_sample_shown`: vẽ mờ, tỷ trọng chỉ hiện khi trỏ, focus hoặc chạm. */
  faded: boolean;
  percent: string;
  /** "41,7% · 848/2.040 tin", như thẻ của prototype. */
  valueText: string;
  /** Câu cỡ mẫu nhỏ; `null` khi đủ mẫu. */
  smallLabel: string | null;
  /** Tên đọc được: tên, tỷ trọng, số tin, và câu mẫu nhỏ nếu có. */
  info: string;
}

export function buildColumns(view: CitySharesView): MapColumn[] {
  const total = view.table.total.nText;
  return view.bars.flatMap((line) => {
    const point = CITY_POINTS[line.city as keyof typeof CITY_POINTS];
    if (!point) return [];
    return [
      {
        city: line.city,
        label: line.label,
        stage: toStage(point),
        height: line.value * COLUMN_MAX_HEIGHT,
        faded: line.lowSample,
        percent: line.percent,
        valueText: `${line.percent} · ${line.nText}/${total} tin`,
        smallLabel: line.lowSampleNote,
        info: line.accessibleName,
      },
    ];
  });
}
