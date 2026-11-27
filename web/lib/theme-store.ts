/**
 * Store chế độ Sáng / Tối cho `useSyncExternalStore` (AD-23: không gọi `localStorage` trực tiếp, đi qua `haido-keys.ts`).
 */

import { DEFAULT_THEME, HAIDO_KEYS, THEME_COOKIE_NAME, type ThemeMode, readTheme, writeTheme } from "./haido-keys";

let cached: ThemeMode | null = null;
const listeners = new Set<() => void>();
let cleanupEnvListeners: (() => void) | null = null;

function readCookieTheme(): ThemeMode | null {
  if (typeof document === "undefined") return null;
  try {
    const match = document.cookie.match(new RegExp(`(?:^|; )${THEME_COOKIE_NAME}=(light|dark)`));
    return match ? (match[1] as ThemeMode) : null;
  } catch {
    return null;
  }
}

function resolveInitialTheme(): ThemeMode {
  const saved = readTheme();
  if (saved) return saved;
  const fromCookie = readCookieTheme();
  if (fromCookie) return fromCookie;
  if (typeof window !== "undefined") {
    try {
      if (window.matchMedia?.("(prefers-color-scheme: light)").matches) return "light";
    } catch {
      // Bỏ qua trong môi trường không có matchMedia.
    }
  }
  return DEFAULT_THEME;
}

export function applyThemeToDocument(theme: ThemeMode): void {
  if (typeof document === "undefined") return;
  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme;
}

function attachEnvironmentListeners(): () => void {
  if (typeof window === "undefined") return () => {};

  const onStorage = (event: StorageEvent) => {
    if (event.key !== HAIDO_KEYS.theme && event.key !== null) return;
    cached = resolveInitialTheme();
    applyThemeToDocument(cached);
    for (const listener of listeners) listener();
  };

  window.addEventListener("storage", onStorage);

  let mediaQuery: MediaQueryList | null = null;
  try {
    mediaQuery = window.matchMedia?.("(prefers-color-scheme: light)") ?? null;
  } catch {
    mediaQuery = null;
  }

  const onMediaChange = (event: MediaQueryListEvent) => {
    if (readTheme() !== null) return;
    cached = event.matches ? "light" : "dark";
    applyThemeToDocument(cached);
    for (const listener of listeners) listener();
  };

  mediaQuery?.addEventListener?.("change", onMediaChange);

  return () => {
    window.removeEventListener("storage", onStorage);
    mediaQuery?.removeEventListener?.("change", onMediaChange);
  };
}

export function subscribeTheme(listener: () => void): () => void {
  listeners.add(listener);
  if (listeners.size === 1 && cleanupEnvListeners === null) {
    cleanupEnvListeners = attachEnvironmentListeners();
  }
  return () => {
    listeners.delete(listener);
    if (listeners.size === 0) {
      cached = null;
      cleanupEnvListeners?.();
      cleanupEnvListeners = null;
    }
  };
}

export function getThemeSnapshot(): ThemeMode {
  cached ??= resolveInitialTheme();
  return cached;
}

export function getServerThemeSnapshot(): ThemeMode {
  return DEFAULT_THEME;
}

export function saveTheme(next: ThemeMode): boolean {
  cached = next;
  applyThemeToDocument(next);
  const stored = writeTheme(next);
  for (const listener of listeners) listener();
  return stored;
}
