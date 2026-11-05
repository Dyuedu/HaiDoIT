import type { Metadata } from "next";
import { Be_Vietnam_Pro } from "next/font/google";
import "./globals.css";
import { AppHeader } from "./components/app-header";

const beVietnamPro = Be_Vietnam_Pro({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin", "vietnamese"],
  display: "swap",
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
    <html lang="vi" className={beVietnamPro.className}>
      <body className="min-h-screen bg-[#070B10] text-[#E6EDF3] antialiased">
        <AppHeader />
        <main className="max-w-[1280px] mx-auto px-6 py-6">
          {children}
        </main>
      </body>
    </html>
  );
}
