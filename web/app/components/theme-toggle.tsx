"use client";

import { useEffect, useSyncExternalStore } from "react";

import {
  applyThemeToDocument,
  getServerThemeSnapshot,
  getThemeSnapshot,
  saveTheme,
  subscribeTheme,
} from "@/lib/theme-store";

function SunIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2" />
      <path d="M12 20v2" />
      <path d="m4.93 4.93 1.41 1.41" />
      <path d="m17.66 17.66 1.41 1.41" />
      <path d="M2 12h2" />
      <path d="M20 12h2" />
      <path d="m6.34 17.66-1.41 1.41" />
      <path d="m19.07 4.93-1.41 1.41" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
    </svg>
  );
}

/**
 * Nút chuyển chế độ Sáng / Tối trên thanh đầu trang (#ui-theme-mode).
 */
export function ThemeToggle() {
  const theme = useSyncExternalStore(subscribeTheme, getThemeSnapshot, getServerThemeSnapshot);

  useEffect(() => {
    applyThemeToDocument(theme);
  }, [theme]);

  const next = theme === "dark" ? "light" : "dark";
  const label = next === "light" ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối";

  return (
    <button
      type="button"
      onClick={() => saveTheme(next)}
      aria-label={label}
      title={label}
      className="inline-flex min-h-target shrink-0 cursor-pointer items-center gap-2 rounded-lg border border-border-chip bg-inset px-3 text-ui text-text-secondary transition-colors hover:border-selected hover:text-text"
    >
      {theme === "dark" ? <SunIcon /> : <MoonIcon />}
      <span className="hidden sm:inline">{theme === "dark" ? "Sáng" : "Tối"}</span>
    </button>
  );
}
