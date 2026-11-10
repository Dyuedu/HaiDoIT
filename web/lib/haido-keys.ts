/**
 * Hợp đồng biên trình duyệt (AD-23, #205): danh sách khóa `localStorage` đóng và hồ sơ kỹ năng.
 *
 * Đây là file duy nhất của web được gọi `localStorage` (cổng AD-23 trong `tools/gates` chặn
 * mọi chỗ khác). Thêm khóa mới thì thêm vào `HAIDO_KEYS` ở đây, với tiền tố `haido:`.
 * "Xóa hồ sơ" xóa theo tiền tố, nên nó đúng cả với khóa thêm về sau.
 *
 * Mã kỹ năng cùng định dạng với `haido_core/vocab/skills.py`. Danh sách kỹ năng lấy từ
 * `GET /api/v1/skills`. Web không cộng, chia hay đếm trên mã kỹ năng (AD-22).
 */

export const HAIDO_PREFIX = "haido:";

/** Danh sách khóa đóng. */
export const HAIDO_KEYS = {
  /** Hồ sơ: vai trò, cấp bậc, mã kỹ năng đã tick (FR-13, FR-14, FR-15). */
  profile: "haido:profile",
  /** Mã phiên ẩn danh (FR-17). Xóa hồ sơ cũng xóa khóa này. */
  session: "haido:session",
  /** `"1"` khi vào bằng link thử nghiệm (FR-41, FR-45). */
  eval: "haido:eval",
} as const;

export type HaidoKey = (typeof HAIDO_KEYS)[keyof typeof HAIDO_KEYS];

export const PROFILE_VERSION = 1;
export const MAX_SKILL_CODE_LEN = 40;
/** Trần số mã trong hồ sơ, cùng trần với `have=` của AD-22. */
export const MAX_PROFILE_SKILLS = 200;

const SKILL_CODE_RE = /^[a-z0-9]+(_[a-z0-9]+)*$/;
const CODE_RE = /^[a-z0-9_]{1,64}$/;

export interface Profile {
  v: typeof PROFILE_VERSION;
  /** Mã vai trò trong `config/rules.toml`, hoặc `null` khi chưa chọn. */
  role: string | null;
  /** Mã cấp bậc (`intern`, `fresher`, `junior`, ...), hoặc `null` khi chưa chọn. */
  level: string | null;
  /** Mã kỹ năng đã tick, không trùng, giữ thứ tự tick, tối đa `MAX_PROFILE_SKILLS`. */
  skills: string[];
}

export const EMPTY_PROFILE: Readonly<Profile> = Object.freeze({
  v: PROFILE_VERSION,
  role: null,
  level: null,
  skills: Object.freeze([]) as unknown as string[],
});

export function isSkillCode(value: string): boolean {
  return value.length <= MAX_SKILL_CODE_LEN && SKILL_CODE_RE.test(value);
}

function emptyProfile(): Profile {
  return { v: PROFILE_VERSION, role: null, level: null, skills: [] };
}

function code(value: unknown): string | null {
  return typeof value === "string" && CODE_RE.test(value) ? value : null;
}

/** Chuẩn hóa một hồ sơ: bỏ trường lạ, mã sai định dạng, mã trùng; cắt ở trần. */
function sanitize(value: unknown): Profile {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return emptyProfile();
  }
  const raw = value as Record<string, unknown>;
  if (raw.v !== PROFILE_VERSION) {
    return emptyProfile();
  }
  const seen = new Set<string>();
  const skills: string[] = [];
  if (Array.isArray(raw.skills)) {
    for (const item of raw.skills) {
      if (typeof item === "string" && isSkillCode(item) && !seen.has(item)) {
        seen.add(item);
        skills.push(item);
        if (skills.length === MAX_PROFILE_SKILLS) break;
      }
    }
  }
  return { v: PROFILE_VERSION, role: code(raw.role), level: code(raw.level), skills };
}

// Mọi lời gọi tới bộ nhớ đi qua ba hàm này. Trình duyệt chặn bộ nhớ (Safari tắt cookie,
// chế độ riêng tư) thì `localStorage` ném lỗi ngay khi truy cập; module không ném ra ngoài.
// Giữ tick cho phiên hiện tại khi bộ nhớ bị chặn là việc của #210.
function storage(): Storage | null {
  try {
    return typeof window === "undefined" ? null : window.localStorage;
  } catch {
    return null;
  }
}

function getItem(key: HaidoKey): string | null {
  try {
    return storage()?.getItem(key) ?? null;
  } catch {
    return null;
  }
}

function setItem(key: HaidoKey, value: string): boolean {
  try {
    const store = storage();
    if (!store) return false;
    store.setItem(key, value);
    return true;
  } catch {
    return false;
  }
}

/** Hồ sơ đã lưu. Không có, JSON hỏng hay sai phiên bản thì trả hồ sơ rỗng. */
export function readProfile(): Profile {
  const raw = getItem(HAIDO_KEYS.profile);
  if (raw === null) return emptyProfile();
  try {
    return sanitize(JSON.parse(raw));
  } catch {
    return emptyProfile();
  }
}

/** Lưu hồ sơ đã chuẩn hóa. Trả `false` khi trình duyệt không cho lưu. */
export function writeProfile(profile: Profile): boolean {
  return setItem(HAIDO_KEYS.profile, JSON.stringify(sanitize(profile)));
}

/** Xóa mọi khóa có tiền tố `haido:`, kể cả khóa không còn trong danh sách. Giữ khóa của trang khác. */
export function clearHaidoData(): void {
  try {
    const store = storage();
    if (!store) return;
    const keys: string[] = [];
    for (let i = 0; i < store.length; i += 1) {
      const key = store.key(i);
      if (key?.startsWith(HAIDO_PREFIX)) keys.push(key);
    }
    for (const key of keys) store.removeItem(key);
  } catch {
    // Bộ nhớ bị chặn thì cũng không có gì để xóa.
  }
}
