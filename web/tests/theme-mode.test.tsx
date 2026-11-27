import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AppHeader } from "@/app/components/app-header";
import { FilterSelect } from "@/app/components/map/filter-select";
import JobScanPage from "@/app/soi-tin/page";
import { clearHaidoData, readTheme, writeTheme } from "@/lib/haido-keys";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

function resetThemeDom() {
  document.documentElement.removeAttribute("data-theme");
  document.documentElement.style.colorScheme = "";
  document.cookie = "haido_theme=; path=/; max-age=0";
  window.localStorage.clear();
}

beforeEach(() => {
  resetThemeDom();
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  resetThemeDom();
});

describe("Chế độ Sáng / Tối toàn hệ thống", () => {
  it("hiển thị nút đổi giao diện trong AppHeader, chuyển đổi light/dark và lưu vào khóa haido:theme", async () => {
    const user = userEvent.setup();
    render(<AppHeader />);

    const toggle = screen.getByRole("button", { name: /chế độ sáng/i });
    expect(toggle.className).toContain("min-h-target");
    expect(document.documentElement.dataset.theme).toBe("dark");

    await user.click(toggle);
    expect(document.documentElement.dataset.theme).toBe("light");
    expect(document.documentElement.style.colorScheme).toBe("light");
    expect(readTheme()).toBe("light");
    expect(screen.getByRole("button", { name: /chế độ tối/i })).toBeTruthy();

    await user.click(screen.getByRole("button", { name: /chế độ tối/i }));
    expect(document.documentElement.dataset.theme).toBe("dark");
    expect(readTheme()).toBe("dark");
  });

  it("khôi phục lựa chọn sáng đã lưu trong haido:theme và xóa sạch khi clearHaidoData()", () => {
    writeTheme("light");
    render(<AppHeader />);

    expect(document.documentElement.dataset.theme).toBe("light");
    expect(screen.getByRole("button", { name: /chế độ tối/i })).toBeTruthy();

    clearHaidoData();
    expect(readTheme()).toBeNull();
  });

  it("áp dụng prefers-color-scheme: light khi người dùng chưa chọn thủ công", () => {
    vi.stubGlobal(
      "matchMedia",
      vi.fn((query: string) => ({
        matches: query.includes("light"),
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })),
    );
    render(<AppHeader />);

    expect(document.documentElement.dataset.theme).toBe("light");
  });

  it("globals.css định nghĩa bảng màu light trên :root[data-theme='light'] và giữ token tối mặc định", () => {
    const css = readFileSync(resolve(process.cwd(), "app/globals.css"), "utf-8");
    expect(css).toMatch(/:root\[data-theme="light"\]\s*\{/);
    expect(css).toMatch(/color-scheme:\s*light\s*;/);
    expect(css).toMatch(/--color-canvas:\s*#[0-9a-f]{6}\s*;/i);
    expect(css).toMatch(/--color-primary:\s*#c5f36a\s*;/i);
  });

  it("các component dùng biến CSS thích ứng thay vì ép color-scheme:dark hay hex nền tối", () => {
    const { container } = render(
      <FilterSelect label="Vai trò" value="backend" options={[{ code: "backend", label: "Backend" }]} onChange={() => {}} />,
    );
    expect(container.querySelector("select")?.className).not.toContain("[color-scheme:dark]");

    const scan = render(<JobScanPage />);
    expect(scan.container.querySelector("h1")?.className).toContain("text-text");
    expect(scan.container.querySelector("h1")?.className).not.toContain("text-[#");
  });
});
