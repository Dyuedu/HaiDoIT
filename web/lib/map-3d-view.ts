/**
 * Cột của bản đồ 3D (#314), dựng từ đúng các dòng mà lối Biểu đồ 2D vẽ (`view.bars` của `buildCitySharesView`).
 *
 * Không tính số mới (AD-22): chiều cao là `share.value` nhân một hằng số, không chuẩn hóa theo cột cao nhất, nên một chiều
 * cao chỉ mang một nghĩa (FR-33) và hai lối không thể lệch nhau. Cột mẫu nhỏ vẫn cao theo tỷ trọng thật, chỉ mờ đi.
 */

import type { ShareLine } from "./city-shares-view";
import { CITY_POINTS, project } from "./vietnam-geo";

/** Chiều cao (đơn vị cảnh, một đơn vị là một độ vĩ) của cột có tỷ trọng 100%. */
export const COLUMN_MAX_HEIGHT = 10;

export interface MapColumn {
  city: string;
  label: string;
  position: { x: number; z: number };
  height: number;
  /** `share.display = low_sample_shown`: vẽ mờ, vẫn chọn được. */
  faded: boolean;
  /** Chữ của khung thông tin: tên, tỷ trọng, số tin, và câu mẫu nhỏ nếu có. */
  info: string;
}

export function buildColumns(bars: readonly ShareLine[]): MapColumn[] {
  return bars.flatMap((line) => {
    const point = CITY_POINTS[line.city as keyof typeof CITY_POINTS];
    if (!point) return [];
    return [
      {
        city: line.city,
        label: line.label,
        position: project(point),
        height: line.value * COLUMN_MAX_HEIGHT,
        faded: line.lowSample,
        info: line.accessibleName,
      },
    ];
  });
}
