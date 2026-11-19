import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Không bật `globals` nên Testing Library không tự dọn DOM sau mỗi test.
afterEach(() => {
  cleanup();
});

// jsdom trả `true` cho `CSS.supports("transform-style", "preserve-3d")` nhưng không tính layout 3D. Coi như không dựng được
// CSS 3D để màn Bản đồ mở lối 2D như trên server (#316); test của lối 3D tự giả lập `@/lib/css3d`.
if (typeof CSS !== "undefined" && typeof CSS.supports === "function") {
  const supports = CSS.supports.bind(CSS);
  CSS.supports = ((property: string, value?: string) =>
    property === "transform-style" && value === "preserve-3d"
      ? false
      : value === undefined
        ? supports(property)
        : supports(property, value)) as typeof CSS.supports;
}
