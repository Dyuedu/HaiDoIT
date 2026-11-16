/**
 * Hồ sơ trình duyệt cho `useSyncExternalStore` (#206). Bọc `readProfile`/`writeProfile` của `haido-keys.ts` (AD-23:
 * file này không gọi `localStorage`).
 *
 * - Server render và lần hydrate đầu dùng `EMPTY_PROFILE`, nên HTML không lệch giữa server và trình duyệt.
 * - Trình duyệt đọc hồ sơ một lần rồi giữ bản đọc được; `saveProfile` ghi xuống và báo các màn đang nghe.
 * - Trình duyệt chặn bộ nhớ thì `writeProfile` trả `false` nhưng bản giữ trong bộ nhớ vẫn đổi, nên tick còn trong phiên.
 * - Khi không còn màn nào nghe (rời trang), bản giữ bị bỏ: mở lại trang thì đọc lại từ bộ nhớ.
 */

import { EMPTY_PROFILE, MAX_PROFILE_SKILLS, type Profile, readProfile, writeProfile } from "./haido-keys";

let cached: Profile | null = null;
const listeners = new Set<() => void>();

export function subscribeProfile(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
    if (listeners.size === 0) cached = null;
  };
}

export function getProfileSnapshot(): Profile {
  cached ??= readProfile();
  return cached;
}

export function getServerProfileSnapshot(): Profile {
  return EMPTY_PROFILE;
}

/** Ghi hồ sơ và báo các màn đang nghe. Trả `false` khi trình duyệt không cho lưu (hồ sơ vẫn đổi trong phiên). */
export function saveProfile(next: Profile): boolean {
  cached = { ...next, skills: [...new Set(next.skills)].slice(0, MAX_PROFILE_SKILLS) };
  const stored = writeProfile(cached);
  for (const listener of listeners) listener();
  return stored;
}
