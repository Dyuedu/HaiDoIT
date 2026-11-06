"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { label: "Bản đồ", href: "/" },
  { label: "Insights", href: "/insights" },
  { label: "Cố vấn", href: "/co-van" },
  { label: "Soi tin", href: "/soi-tin" },
];

export function AppHeader() {
  const pathname = usePathname();

  return (
    <header className="flex min-h-nav flex-wrap items-center justify-between border-b border-border bg-header px-page">
      <div className="flex flex-wrap items-center gap-6">
        <Link
          href="/"
          className="flex items-center gap-1 text-logo text-text transition-opacity hover:opacity-90"
        >
          <span>HẢI ĐỒ</span>
          <span className="text-primary">•</span>
          <span>IT</span>
        </Link>

        <nav aria-label="Điều hướng chính" className="flex items-center gap-1 overflow-x-auto">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={`flex h-nav items-center border-b-2 px-3 text-ui transition-colors hover:text-text ${
                  isActive ? "border-selected text-text" : "border-transparent text-text-muted"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
