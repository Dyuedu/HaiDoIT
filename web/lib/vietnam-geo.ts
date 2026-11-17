/**
 * Hình học của bản đồ 3D (#314): viền Việt Nam, Hoàng Sa, Trường Sa, vị trí ba thành phố, và phép chiếu sang mặt phẳng
 * của cảnh 3D. Hàm thuần, không phụ thuộc three.js, để test trong jsdom.
 *
 * Viền đất liền lấy từ geoBoundaries (CC BY 4.0), đã rút gọn (`geo/vietnam-outline.json`). Nguồn đó không có Hoàng Sa,
 * Trường Sa, nên hai quần đảo được vẽ riêng ở đây bằng các điểm đảo đại diện, luôn có nhãn. Tọa độ đảo là xấp xỉ, đủ cho
 * bản đồ tỷ lệ nhỏ, không dùng để đo đạc.
 */

import outline from "./geo/vietnam-outline.json";

export interface LonLat {
  lon: number;
  lat: number;
}

export interface Outline {
  source: string;
  license: string;
  attribution: string;
  /** Mỗi vòng là một đường khép kín `[kinh độ, vĩ độ]`; vòng đầu là đất liền. */
  rings: [number, number][][];
}

// JSON chỉ cho kiểu `number[][][]`; mỗi điểm luôn có đúng hai số (script rút gọn ghi `[kinh độ, vĩ độ]`).
export const OUTLINE = outline as unknown as Outline;

export interface Archipelago {
  id: "hoang_sa" | "truong_sa";
  label: string;
  /** Nhãn ngắn trên bản đồ, như prototype màn 01: "QĐ. Hoàng Sa". */
  shortLabel: string;
  /** Điểm đặt nhãn. */
  labelAt: LonLat;
  islands: (LonLat & { name: string })[];
}

/** Hai quần đảo của Việt Nam. Luôn được vẽ, kể cả khi viền đất liền không có chúng. */
export const ARCHIPELAGOS: readonly Archipelago[] = [
  {
    id: "hoang_sa",
    label: "Quần đảo Hoàng Sa",
    shortLabel: "QĐ. Hoàng Sa",
    labelAt: { lon: 112.0, lat: 17.2 },
    islands: [
      { name: "Hoàng Sa", lon: 111.61, lat: 16.53 },
      { name: "Phú Lâm", lon: 112.34, lat: 16.84 },
      { name: "Tri Tôn", lon: 111.2, lat: 15.78 },
      { name: "Linh Côn", lon: 112.73, lat: 16.67 },
      { name: "Quang Ảnh", lon: 111.51, lat: 16.45 },
    ],
  },
  {
    id: "truong_sa",
    label: "Quần đảo Trường Sa",
    shortLabel: "QĐ. Trường Sa",
    labelAt: { lon: 114.3, lat: 11.9 },
    islands: [
      { name: "Trường Sa", lon: 111.92, lat: 8.64 },
      { name: "Song Tử Tây", lon: 114.33, lat: 11.43 },
      { name: "Thị Tứ", lon: 114.28, lat: 11.05 },
      { name: "Ba Bình", lon: 114.36, lat: 10.38 },
      { name: "Nam Yết", lon: 114.36, lat: 10.18 },
      { name: "Sinh Tồn", lon: 114.33, lat: 9.88 },
      { name: "An Bang", lon: 112.92, lat: 7.89 },
    ],
  },
];

/** Vị trí ba thành phố có cột (FR-33). Mã trùng mã thành phố của `config/rules.toml`. */
export const CITY_POINTS: Readonly<Record<"ha_noi" | "ho_chi_minh" | "da_nang", LonLat>> = {
  ha_noi: { lon: 105.85, lat: 21.03 },
  ho_chi_minh: { lon: 106.7, lat: 10.78 },
  da_nang: { lon: 108.21, lat: 16.05 },
};

/** Tâm phép chiếu: giữa đất liền và hai quần đảo, để bản đồ nằm giữa khung. */
export const CENTER: LonLat = { lon: 108.5, lat: 15.8 };
const KX = Math.cos((CENTER.lat * Math.PI) / 180);

/**
 * Chiếu `[kinh độ, vĩ độ]` sang mặt phẳng XZ của cảnh (y là chiều cao): một độ vĩ là một đơn vị, kinh độ nhân cos của
 * vĩ độ tâm. Bắc là z âm, đông là x dương (máy quay nhìn từ phía nam lên).
 */
export function project(point: LonLat): { x: number; z: number } {
  return { x: (point.lon - CENTER.lon) * KX, z: -(point.lat - CENTER.lat) };
}

/** Sân khấu của bản đồ 3D CSS, đúng kích thước của prototype màn 01 (#316). */
export const STAGE = { width: 460, height: 560 } as const;
const STAGE_PAD = 18;

// Khung bao của mọi thứ vẽ trên sân khấu (đất liền và hai quần đảo), trên mặt phẳng của `project`.
const ALL_POINTS = [
  ...OUTLINE.rings.flatMap((ring) => ring.map(([lon, lat]) => project({ lon, lat }))),
  ...ARCHIPELAGOS.flatMap((group) => [...group.islands.map(project), project(group.labelAt)]),
];
const MIN_X = Math.min(...ALL_POINTS.map((p) => p.x));
const MAX_X = Math.max(...ALL_POINTS.map((p) => p.x));
const MIN_Z = Math.min(...ALL_POINTS.map((p) => p.z));
const MAX_Z = Math.max(...ALL_POINTS.map((p) => p.z));
const SCALE = Math.min(
  (STAGE.width - 2 * STAGE_PAD) / (MAX_X - MIN_X),
  (STAGE.height - 2 * STAGE_PAD) / (MAX_Z - MIN_Z),
);
const OFFSET_X = (STAGE.width - SCALE * (MAX_X - MIN_X)) / 2;
const OFFSET_Y = (STAGE.height - SCALE * (MAX_Z - MIN_Z)) / 2;

/** Chiếu `[kinh độ, vĩ độ]` sang pixel của sân khấu 460×560 (bắc ở trên), giữ tỷ lệ và căn giữa (#316). */
export function toStage(point: LonLat): { px: number; py: number } {
  const { x, z } = project(point);
  return { px: OFFSET_X + (x - MIN_X) * SCALE, py: OFFSET_Y + (z - MIN_Z) * SCALE };
}

/** Đường SVG của viền đất liền trên sân khấu: mỗi vòng một đoạn `M … Z`. */
export const OUTLINE_PATH: string = OUTLINE.rings
  .map(
    (ring) =>
      ring
        .map(([lon, lat], i) => {
          const { px, py } = toStage({ lon, lat });
          return `${i === 0 ? "M" : "L"}${px.toFixed(1)},${py.toFixed(1)}`;
        })
        .join(" ") + " Z",
  )
  .join(" ");
