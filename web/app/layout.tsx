import type { Metadata } from "next";
import { Be_Vietnam_Pro, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AppHeader } from "./components/app-header";

// Chữ giao diện (DESIGN.md).
const beVietnamPro = Be_Vietnam_Pro({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin", "vietnamese"],
  display: "swap",
  variable: "--font-be-vietnam-pro",
});

// Số, n, ngày, phần trăm, mã (DESIGN.md).
const jetBrainsMono = JetBrains_Mono({
  weight: ["400", "600"],
  subsets: ["latin", "vietnamese"],
  display: "swap",
  variable: "--font-jetbrains-mono",
});

export const metadata: Metadata = {
  // Gốc để Next ghép URL tuyệt đối cho opengraph-image (deploy/compose.proxy.yml).
  metadataBase: new URL("https://haidoit.io.vn"),
  title: "Hải Đồ IT",
  description: "Bản đồ nhu cầu kỹ năng trên tin tuyển dụng IT",
};

const THEME_BOOT_SCRIPT =
  '(function(){try{var d=document.documentElement,c=document.cookie.match(/(?:^|; )haido_theme=(light|dark)/),t=c?c[1]:(window.matchMedia&&window.matchMedia("(prefers-color-scheme: light)").matches?"light":"dark");d.dataset.theme=t;d.style.colorScheme=t;}catch(e){}})();';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className={`${beVietnamPro.variable} ${jetBrainsMono.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_BOOT_SCRIPT }} />
      </head>
      <body className="min-h-screen bg-canvas font-sans text-text antialiased">
        <AppHeader />
        <main className="mx-auto max-w-content px-page py-6">{children}</main>
      </body>
    </html>
  );
}
