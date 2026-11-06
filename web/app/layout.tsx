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
  title: "Hải Đồ IT",
  description: "Bản đồ nhu cầu kỹ năng trên tin tuyển dụng IT",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className={`${beVietnamPro.variable} ${jetBrainsMono.variable}`}>
      <body className="min-h-screen bg-canvas font-sans text-text antialiased">
        <AppHeader />
        <main className="mx-auto max-w-content px-page py-6">{children}</main>
      </body>
    </html>
  );
}
