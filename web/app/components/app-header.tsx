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
    <header
      style={{
        backgroundColor: "#0A1017",
        borderBottom: "1px solid #1C2A36",
        padding: "0 24px",
      }}
      className="flex flex-wrap items-center justify-between min-h-[52px]"
    >
      <div className="flex flex-wrap items-center gap-6">
        <Link
          href="/"
          className="text-base font-bold tracking-wider text-[#E6EDF3] flex items-center gap-1 hover:opacity-90 transition-opacity"
        >
          <span>HẢI ĐỒ</span>
          <span style={{ color: "#C5F36A" }}>•</span>
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
                style={{
                  color: isActive ? "#E6EDF3" : "#9FB0C2",
                  borderBottom: isActive ? "2px solid #62D9EE" : "2px solid transparent",
                }}
                className="px-3 h-[52px] flex items-center text-sm font-medium hover:text-[#E6EDF3] transition-colors"
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
