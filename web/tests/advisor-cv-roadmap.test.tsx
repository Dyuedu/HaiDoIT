import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import AdvisoryPage from "@/app/co-van/page";
import {
  ADVISOR_ROADMAP_URL,
  type AdvisorRoadmapEnvelope,
  CV_MAX_BYTES,
} from "@/lib/advisor-roadmap";
import { readProfile, writeProfile } from "@/lib/haido-keys";

import { deferred, jsonResponse } from "./helpers/fetch";
import { PATHS, pathWithHave } from "./helpers/learning-path";

async function open(params: Record<string, string>) {
  return render(await AdvisoryPage({ searchParams: Promise.resolve(params) }));
}

function makeAdvisorEnvelope(overrides: {
  role?: string;
  level?: string;
  have?: string[];
  cvSkills?: string[];
  missingCore?: string[];
  missingCommon?: string[];
  mode?: "llm" | "market_fallback";
} = {}): AdvisorRoadmapEnvelope {
  const role = overrides.role ?? "backend";
  const level = overrides.level ?? "junior";
  const basePath = pathWithHave(role === "data_engineer" ? "data_engineer" : "backend", overrides.have ?? ["sql"]);
  basePath.data.role = role;
  basePath.data.level = level;
  return {
    data: {
      path: basePath.data,
      cv_skills: overrides.cvSkills ?? ["sql", "git"],
      missing_core_skills: overrides.missingCore ?? ["java", "spring_boot"],
      missing_common_skills: overrides.missingCommon ?? ["docker"],
      advisor_summary:
        "CV đã thể hiện SQL và Git. Lộ trình bên dưới ưu tiên bù Java và Spring Boot theo yêu cầu tuyển dụng Backend.",
      generation_mode: overrides.mode ?? "llm",
    },
    meta: basePath.meta,
  };
}

function routeAdvisorApis(options: {
  postHandler?: (form: FormData, url: string) => Response | Promise<Response>;
} = {}) {
  const getCalls: { path: string; params: Record<string, string> }[] = [];
  const postCalls: { url: string; form: FormData }[] = [];

  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(input), "http://localhost");
    if (url.pathname === "/api/v1/skills") {
      return jsonResponse(200, {
        data: {
          skills: [
            { code: "java", name_en: "Java", name_vi: "Java", aliases: [] },
            { code: "sql", name_en: "SQL", name_vi: "SQL", aliases: [] },
            { code: "git", name_en: "Git", name_vi: "Git", aliases: [] },
            { code: "spring_boot", name_en: "Spring Boot", name_vi: "Spring Boot", aliases: [] },
            { code: "docker", name_en: "Docker", name_vi: "Docker", aliases: [] },
          ],
        },
        meta: PATHS.backend.meta,
      });
    }
    if (url.pathname === "/api/v1/learning-path") {
      const role = url.searchParams.get("role") ?? "";
      const level = url.searchParams.get("level") ?? "entry";
      const haveParam = url.searchParams.get("have") ?? "";
      const have = haveParam ? haveParam.split(",").filter(Boolean) : [];
      getCalls.push({
        path: url.pathname,
        params: Object.fromEntries(url.searchParams.entries()),
      });
      const res = pathWithHave(role === "data_engineer" ? "data_engineer" : "backend", have);
      res.data.role = role;
      res.data.level = level;
      return jsonResponse(200, res);
    }
    if (url.pathname === ADVISOR_ROADMAP_URL) {
      const form = init?.body as FormData;
      postCalls.push({ url: url.pathname, form });
      if (options.postHandler) return await options.postHandler(form, url.pathname);
      return jsonResponse(
        200,
        makeAdvisorEnvelope({
          role: String(form.get("role") ?? "backend"),
          level: String(form.get("level") ?? "junior"),
        }),
      );
    }
    throw new Error(`URL lạ: ${url.pathname}`);
  });

  vi.stubGlobal("fetch", fetchMock);
  return { getCalls, postCalls, fetchMock };
}

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/co-van");
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("Hướng B — chọn cấp bậc và tạo lộ trình từ CV + LLM + JD", () => {
  it("chọn cấp bậc đổi request learning-path, URL và lưu vào hồ sơ", async () => {
    const user = userEvent.setup();
    const api = routeAdvisorApis();
    await open({ role: "backend", level: "entry" });
    await screen.findByRole("list", { name: "Các chặng của lộ trình học" });

    const levelSelect = screen.getByRole("combobox", { name: "Cấp bậc" }) as HTMLSelectElement;
    expect(levelSelect.value).toBe("entry");

    await user.selectOptions(levelSelect, "mid");
    await waitFor(() => expect(api.getCalls.at(-1)?.params.level).toBe("mid"));
    expect(window.location.search).toContain("level=mid");
    expect(readProfile().level).toBe("mid");
  });

  it("chặn gửi CV khi chưa đánh dấu đồng ý; khi đồng ý sẽ gửi POST, hiện tiến trình, đồng bộ cv_skills và vẽ PathGraph", async () => {
    const user = userEvent.setup();
    writeProfile({ v: 1, role: "backend", level: "junior", skills: ["git"] });
    const pending = deferred<Response>();
    const api = routeAdvisorApis({
      postHandler: () => pending.promise,
    });

    await open({ role: "backend", level: "junior" });
    await screen.findByRole("list", { name: "Các chặng của lộ trình học" });

    const fileInput = screen.getByLabelText(/Tệp CV/i) as HTMLInputElement;
    const pdfFile = new File(["%PDF-1.4\nCV backend SQL Git"], "ung-vien.pdf", { type: "application/pdf" });
    await user.upload(fileInput, pdfFile);

    const submitBtn = screen.getByRole("button", { name: "Tạo lộ trình từ CV" });
    await user.click(submitBtn);
    expect(api.postCalls).toHaveLength(0);
    expect(screen.getByRole("alert").textContent).toMatch(/đồng ý/i);

    const consentBox = screen.getByRole("checkbox", { name: /Tôi đồng ý gửi nội dung CV/i });
    await user.click(consentBox);
    await user.click(submitBtn);

    expect(api.postCalls).toHaveLength(1);
    const sent = api.postCalls[0].form;
    expect(sent.get("role")).toBe("backend");
    expect(sent.get("level")).toBe("junior");
    expect(sent.get("consent")).toBe("true");
    expect((sent.get("cv") as File).name).toBe("ung-vien.pdf");
    expect(screen.getByRole("status", { name: "Tiến trình phân tích CV" }).textContent).toMatch(
      /Đang phân tích CV|Đang đối chiếu|Đang dựng lộ trình/i,
    );

    pending.resolve(jsonResponse(200, makeAdvisorEnvelope({ role: "backend", level: "junior" })));

    const summaryHeading = await screen.findByRole("heading", { name: "Phân tích CV theo yêu cầu tuyển dụng" });
    const summarySection = summaryHeading.closest("section")!;
    expect(summarySection.textContent).toContain("CV đã thể hiện SQL và Git.");
    expect(summarySection.textContent).toContain("Phân tích bằng AI + dữ liệu JD");
    expect(within(summarySection).getByText("SQL")).toBeTruthy();
    expect(within(summarySection).getByText("Java")).toBeTruthy();

    expect(readProfile().skills).toEqual(["git", "sql"]);

    // Tick kỹ năng trên PathGraph cập nhật ngay mà không bắt upload lại CV
    const postCountBefore = api.postCalls.length;
    const getCountBefore = api.getCalls.length;
    await user.click(screen.getByRole("checkbox", { name: "Đã có Docker" }));
    expect(readProfile().skills).toEqual(["git", "sql", "docker"]);
    expect(api.postCalls).toHaveLength(postCountBefore);
    expect(api.getCalls).toHaveLength(getCountBefore);
    expect(screen.getByTestId("path-count").textContent).toContain("3/");
  });

  it("chặn tệp sai định dạng hoặc vượt quá 5 MB ngay tại trình duyệt và hiện lỗi từ server khi CV là bản scan", async () => {
    const user = userEvent.setup({ applyAccept: false });
    const api = routeAdvisorApis({
      postHandler: () =>
        jsonResponse(422, {
          error: {
            code: "cv_unreadable",
            message: "Không đọc được chữ trong CV — nếu là bản scan ảnh, hãy xuất PDF có lớp chữ từ Word, Canva hoặc Overleaf.",
            snapshot_date: null,
          },
        }),
    });

    await open({ role: "backend", level: "entry" });
    await screen.findByRole("list", { name: "Các chặng của lộ trình học" });

    const fileInput = screen.getByLabelText(/Tệp CV/i) as HTMLInputElement;
    await user.upload(fileInput, new File(["png"], "avatar.png", { type: "image/png" }));
    expect(screen.getByRole("alert").textContent).toMatch(/PDF hoặc DOCX/i);

    const bigBytes = new Uint8Array(CV_MAX_BYTES + 1);
    await user.upload(fileInput, new File([bigBytes], "heavy.pdf", { type: "application/pdf" }));
    expect(screen.getByRole("alert").textContent).toMatch(/5 MB/i);

    await user.upload(fileInput, new File(["%PDF-1.4\nCV"], "scan.pdf", { type: "application/pdf" }));
    await user.click(screen.getByRole("checkbox", { name: /Tôi đồng ý gửi nội dung CV/i }));
    await user.click(screen.getByRole("button", { name: "Tạo lộ trình từ CV" }));

    await waitFor(() => expect(api.postCalls).toHaveLength(1));
    expect((await screen.findByRole("alert")).textContent).toContain("Word, Canva hoặc Overleaf");
  });
});
